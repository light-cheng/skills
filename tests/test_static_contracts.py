"""Seam 1 static contract tests for frontmatter, plugin version sync, and skill linking."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_FRONTMATTER = REPO_ROOT / "scripts" / "check-frontmatter.mjs"
SYNC_PLUGIN_VERSION = REPO_ROOT / "scripts" / "sync-plugin-version.mjs"
LINK_SKILLS = REPO_ROOT / "scripts" / "link-skills.sh"


def _write_skill(
    skill_dir: Path,
    *,
    frontmatter: str,
    body: str = "Body text.\n",
    openai_yaml: str | None = None,
) -> Path:
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(f"---\n{frontmatter.strip()}\n---\n\n{body}", encoding="utf-8")
    if openai_yaml is not None:
        agents_dir = skill_dir / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        (agents_dir / "openai.yaml").write_text(openai_yaml.strip() + "\n", encoding="utf-8")
    return skill_dir


def _run_node(script: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(
        ["node", str(script), *args],
        cwd=str(REPO_ROOT),
        env=merged_env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_check_frontmatter_accepts_valid_model_and_user_invoked_skills(tmp_path: Path) -> None:
    model_skill = _write_skill(
        tmp_path / "skills" / "core" / "alpha",
        frontmatter="""
name: alpha
description: Route alpha decisions when conditions shift.
""",
        body="See [guide](references/guide.md) for details.\n",
        openai_yaml="""
interface:
  display_name: "Alpha"
  short_description: "Route alpha decisions"
policy:
  allow_implicit_invocation: true
""",
    )
    (model_skill / "references").mkdir()
    (model_skill / "references" / "guide.md").write_text("# Guide\n", encoding="utf-8")

    _write_skill(
        tmp_path / "skills" / "core" / "beta-setup",
        frontmatter="""
name: beta-setup
description: Initialize beta configuration in a repository.
disable-model-invocation: true
argument-hint: "[mode]"
""",
        openai_yaml="""
interface:
  display_name: "Beta Setup"
  short_description: "Initialize beta configuration"
policy:
  allow_implicit_invocation: false
""",
    )

    res = _run_node(CHECK_FRONTMATTER, "--repo", str(tmp_path), "--require-skills")
    assert res.returncode == 0, res.stderr


def test_check_frontmatter_rejects_duplicate_keys_and_name_mismatch(tmp_path: Path) -> None:
    dup_skill = _write_skill(
        tmp_path / "skills" / "core" / "dup-skill",
        frontmatter="""
name: dup-skill
name: dup-skill
description: Duplicate key test.
""",
        openai_yaml="""
interface:
  display_name: "Dup"
  short_description: "Dup"
policy:
  allow_implicit_invocation: true
""",
    )
    res_dup = _run_node(CHECK_FRONTMATTER, str(dup_skill))
    assert res_dup.returncode != 0
    assert "Map keys must be unique" in res_dup.stderr or "unique" in res_dup.stderr.lower()

    mismatch_skill = _write_skill(
        tmp_path / "skills" / "core" / "folder-name",
        frontmatter="""
name: wrong-name
description: Mismatched skill name.
""",
        openai_yaml="""
interface:
  display_name: "Wrong"
  short_description: "Wrong"
policy:
  allow_implicit_invocation: true
""",
    )
    res_mismatch = _run_node(CHECK_FRONTMATTER, str(mismatch_skill))
    assert res_mismatch.returncode != 0
    assert "folder-name" in res_mismatch.stderr


def test_check_frontmatter_rejects_invocation_policy_desync(tmp_path: Path) -> None:
    desync_user = _write_skill(
        tmp_path / "skills" / "core" / "user-skill",
        frontmatter="""
name: user-skill
description: User-only skill with desynced openai.yaml.
disable-model-invocation: true
""",
        openai_yaml="""
interface:
  display_name: "User Skill"
  short_description: "User only"
policy:
  allow_implicit_invocation: true
""",
    )
    res_user = _run_node(CHECK_FRONTMATTER, str(desync_user))
    assert res_user.returncode != 0
    assert "allow_implicit_invocation" in res_user.stderr

    desync_model = _write_skill(
        tmp_path / "skills" / "core" / "model-skill",
        frontmatter="""
name: model-skill
description: Model skill with desynced openai.yaml.
""",
        openai_yaml="""
interface:
  display_name: "Model Skill"
  short_description: "Model skill"
policy:
  allow_implicit_invocation: false
""",
    )
    res_model = _run_node(CHECK_FRONTMATTER, str(desync_model))
    assert res_model.returncode != 0
    assert "allow_implicit_invocation" in res_model.stderr

    explicit_false_skill = _write_skill(
        tmp_path / "skills" / "core" / "explicit-false",
        frontmatter="""
name: explicit-false
description: Model skill should omit disable-model-invocation instead of setting false.
disable-model-invocation: false
""",
        openai_yaml="""
interface:
  display_name: "Explicit False"
  short_description: "Explicit false check"
policy:
  allow_implicit_invocation: true
""",
    )
    res_explicit_false = _run_node(CHECK_FRONTMATTER, str(explicit_false_skill))
    assert res_explicit_false.returncode != 0
    assert "omit 'disable-model-invocation'" in res_explicit_false.stderr


def test_check_frontmatter_checks_internal_links_and_ignores_fenced_code(tmp_path: Path) -> None:
    good_code_fence = _write_skill(
        tmp_path / "skills" / "core" / "fence-ok",
        frontmatter="""
name: fence-ok
description: Links inside code blocks are examples, not live file pointers.
""",
        body="```markdown\nSee [example](nonexistent/example.md)\n```\nInline `[skip](missing.md)` and https://example.com.\n",
        openai_yaml="""
interface:
  display_name: "Fence OK"
  short_description: "Fence test"
policy:
  allow_implicit_invocation: true
""",
    )
    assert _run_node(CHECK_FRONTMATTER, str(good_code_fence)).returncode == 0

    broken_link = _write_skill(
        tmp_path / "skills" / "core" / "broken-link",
        frontmatter="""
name: broken-link
description: Contains a broken relative markdown link.
""",
        body="Read [missing](references/does-not-exist.md#section) before running.\n",
        openai_yaml="""
interface:
  display_name: "Broken Link"
  short_description: "Broken link test"
policy:
  allow_implicit_invocation: true
""",
    )
    res_broken = _run_node(CHECK_FRONTMATTER, str(broken_link))
    assert res_broken.returncode != 0
    assert "does-not-exist.md" in res_broken.stderr


def _resolve_repo_node_modules() -> Path:
    direct = REPO_ROOT / "node_modules"
    if direct.is_dir():
        return direct
    git_common = subprocess.run(
        ["git", "rev-parse", "--git-common-dir"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if git_common.returncode == 0 and git_common.stdout.strip():
        common_dir = (REPO_ROOT / git_common.stdout.strip()).resolve()
        candidate = common_dir.parent / "node_modules"
        if candidate.is_dir():
            return candidate
    if os.environ.get("NODE_PATH"):
        for entry in os.environ["NODE_PATH"].split(os.pathsep):
            if entry and Path(entry).is_dir():
                return Path(entry)
    return direct


def test_check_frontmatter_resolves_yaml_via_node_path_outside_repo(tmp_path: Path) -> None:
    copied_script = tmp_path / "isolated-worktree" / "scripts" / "check-frontmatter.mjs"
    copied_script.parent.mkdir(parents=True)
    copied_script.write_text(CHECK_FRONTMATTER.read_text(encoding="utf-8"), encoding="utf-8")

    skill = _write_skill(
        tmp_path / "isolated-worktree" / "skills" / "core" / "solo",
        frontmatter="""
name: solo
description: Validated from an isolated worktree without local node_modules.
""",
        openai_yaml="""
interface:
  display_name: "Solo"
  short_description: "Solo skill"
policy:
  allow_implicit_invocation: true
""",
    )
    res = subprocess.run(
        ["node", str(copied_script), str(skill)],
        cwd=str(tmp_path / "isolated-worktree"),
        env={**os.environ, "NODE_PATH": str(_resolve_repo_node_modules())},
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0, res.stderr


def test_check_frontmatter_enforces_root_readme_word_floor(tmp_path: Path) -> None:
    _write_skill(
        tmp_path / "skills" / "core" / "sample",
        frontmatter="name: sample\ndescription: Sample skill.\n",
        openai_yaml="""
interface:
  display_name: "Sample"
  short_description: "Sample skill"
policy:
  allow_implicit_invocation: true
""",
    )
    (tmp_path / "README.md").write_text("# Too short\nOnly a few words.\n", encoding="utf-8")
    res_short = _run_node(CHECK_FRONTMATTER, "--repo", str(tmp_path))
    assert res_short.returncode != 0
    assert "README.md" in res_short.stderr
    assert "40" in res_short.stderr


def test_sync_plugin_version_syncs_dual_manifests_and_forbids_mcp_servers(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(json.dumps({"name": "light-skills", "version": "1.2.0"}), encoding="utf-8")
    root_manifest = tmp_path / ".claude-plugin" / "plugin.json"
    sub_manifest = tmp_path / "plugins" / "light-manuscript" / ".claude-plugin" / "plugin.json"
    marketplace = tmp_path / ".claude-plugin" / "marketplace.json"
    root_manifest.parent.mkdir(parents=True)
    sub_manifest.parent.mkdir(parents=True)

    # Missing manifests fail when --require-manifests is set, pass without it.
    assert _run_node(SYNC_PLUGIN_VERSION, "--repo", str(tmp_path), "--check").returncode == 0
    assert _run_node(SYNC_PLUGIN_VERSION, "--repo", str(tmp_path), "--check", "--require-manifests").returncode != 0

    root_manifest.write_text(json.dumps({"name": "light", "version": "1.0.0"}, indent=2) + "\n", encoding="utf-8")
    sub_manifest.write_text(json.dumps({"name": "light-manuscript", "version": "1.0.0"}, indent=2) + "\n", encoding="utf-8")
    marketplace.write_text(json.dumps({"name": "light-cheng", "plugins": []}, indent=2) + "\n", encoding="utf-8")

    # Version drift fails --check, then sync fixes both manifests.
    assert _run_node(SYNC_PLUGIN_VERSION, "--repo", str(tmp_path), "--check", "--require-manifests").returncode != 0
    assert _run_node(SYNC_PLUGIN_VERSION, "--repo", str(tmp_path), "--require-manifests").returncode == 0
    assert json.loads(root_manifest.read_text(encoding="utf-8"))["version"] == "1.2.0"
    assert json.loads(sub_manifest.read_text(encoding="utf-8"))["version"] == "1.2.0"
    assert _run_node(SYNC_PLUGIN_VERSION, "--repo", str(tmp_path), "--check", "--require-manifests").returncode == 0

    # Any mcpServers entry is rejected per authoring invariant.
    root_manifest.write_text(
        json.dumps({"name": "light", "version": "1.2.0", "mcpServers": {"bad": {}}}, indent=2) + "\n",
        encoding="utf-8",
    )
    res_mcp = _run_node(SYNC_PLUGIN_VERSION, "--repo", str(tmp_path), "--check")
    assert res_mcp.returncode != 0
    assert "mcpServers" in res_mcp.stderr


def test_link_skills_links_core_by_default_and_optional_with_flag(tmp_path: Path) -> None:
    fake_repo = tmp_path / "repo"
    (fake_repo / "scripts").mkdir(parents=True)
    script_copy = fake_repo / "scripts" / "link-skills.sh"
    script_copy.write_text(LINK_SKILLS.read_text(encoding="utf-8"), encoding="utf-8")
    script_copy.chmod(0o755)

    _write_skill(
        fake_repo / "skills" / "core" / "decide",
        frontmatter="name: decide\ndescription: Core skill.\n",
    )
    _write_skill(
        fake_repo / "plugins" / "light-manuscript" / "skills" / "manuscript-ops",
        frontmatter="name: manuscript-ops\ndescription: Optional manuscript skill.\n",
    )

    dest_claude = tmp_path / "dest-claude"
    dest_agents = tmp_path / "dest-agents"
    env = {**os.environ, "LINK_SKILLS_DESTS": f"{dest_claude}:{dest_agents}"}

    res_default = subprocess.run([str(script_copy)], env=env, capture_output=True, text=True, check=False)
    assert res_default.returncode == 0, res_default.stderr
    assert (dest_claude / "decide").is_symlink()
    assert not (dest_claude / "manuscript-ops").exists()

    res_opt = subprocess.run([str(script_copy), "--with-optional"], env=env, capture_output=True, text=True, check=False)
    assert res_opt.returncode == 0, res_opt.stderr
    assert (dest_claude / "manuscript-ops").is_symlink()
    assert (dest_agents / "manuscript-ops").is_symlink()


def test_live_repository_contracts_and_minimal_root_docs() -> None:
    res_fm = _run_node(CHECK_FRONTMATTER, "--require-skills")
    assert res_fm.returncode == 0, res_fm.stderr
    assert "validated 9 skill package(s)" in res_fm.stdout

    res_ver = _run_node(SYNC_PLUGIN_VERSION, "--check", "--require-manifests")
    assert res_ver.returncode == 0, res_ver.stderr

    for manifest_rel, base_dir in (
        (".claude-plugin/plugin.json", REPO_ROOT),
        ("plugins/light-manuscript/.claude-plugin/plugin.json", REPO_ROOT / "plugins" / "light-manuscript"),
    ):
        manifest = json.loads((REPO_ROOT / manifest_rel).read_text(encoding="utf-8"))
        for rel_skill in manifest["skills"]:
            assert (base_dir / rel_skill / "SKILL.md").is_file(), f"Missing {rel_skill} in {manifest_rel}"

    root_md = {p.name for p in REPO_ROOT.glob("*.md")}
    forbidden_docs = {
        "CATALOG.md",
        "INSTALLATION.md",
        "MAINTENANCE.md",
        "REVIEW_POLICY.md",
        "SKILL_ADMISSION.md",
    }
    assert root_md.isdisjoint(forbidden_docs)
    assert {"README.md", "README.zh-CN.md", "CLAUDE.md", "AGENTS.md", "GLOSSARY.md"}.issubset(root_md)
    assert (REPO_ROOT / "LICENSE").is_file()
