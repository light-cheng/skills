"""Release context regressions through the same CLI used before publication."""

from __future__ import annotations

import subprocess
import sys
import json
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
TAG = "v9.8.7"
# Fixture repository: release scripts must not depend on the collection's real name.
REPO = "example-owner/skills"


@pytest.fixture(autouse=True)
def _fixture_repository(monkeypatch):
    monkeypatch.setenv("GITHUB_REPOSITORY", REPO)


def git(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=True)
    return proc.stdout.strip()


def write(root: Path, path: str, text: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def make_candidate(root: Path, tag: str = TAG) -> None:
    git(root, "init", "--initial-branch=main")
    git(root, "config", "user.name", "Release fixture")
    git(root, "config", "user.email", "release-fixture@example.invalid")
    write(root, "skills/project/fixture-skill/SKILL.md", "---\nname: fixture-skill\ndescription: Test fixture.\n---\n# Fixture\n")
    for suffix in ("", ".zh-CN"):
        write(root, f"skills/project/README{suffix}.md", "# Project\n\n[Fixture](fixture-skill/SKILL.md)\n")
    evidence = f"docs/evidence/releases/{tag}"
    for path in ("README.md", "README.zh-CN.md", "CATALOG.md", "CATALOG.zh-CN.md", "docs/INSTALLATION.md", "docs/INSTALLATION.zh-CN.md", "docs/MAINTENANCE.md", "docs/MAINTENANCE.zh-CN.md"):
        prefix = "evidence/releases" if path.startswith("docs/") else "docs/evidence/releases"
        content = (
            f"# Skills\n\n**Release snapshot:** `{tag}`\n\n"
            "This tree contains one Skill. It describes its own release content.\n"
            f"[Release Manifest]({prefix}/{tag}/RELEASE_MANIFEST.md) records preparation facts.\n"
            "Observed publication and installation facts belong in the receipt on main.\n"
        )
        if path.startswith("CATALOG"):
            if "zh-CN" in path:
                content += "\n### fixture-skill\n\n- **作用：** Fixture.\n- **什么时候用：** Fixture.\n- **调用方式：** Model-invoked.\n- **包位置：** skills/project/fixture-skill/\n- **状态：** 第一方已准入。\n"
            else:
                content += "\n### fixture-skill\n\n- **Purpose:** Fixture.\n- **When to use:** Fixture.\n- **Invocation:** Model-invoked.\n- **Package:** skills/project/fixture-skill/\n- **Status:** Admitted first-party.\n"
        write(root, path, content)
    for suffix in ("", ".zh-CN"):
        other = ".zh-CN" if not suffix else ""
        write(root, f"{evidence}/RELEASE_MANIFEST{suffix}.md", (
            f"# Release Manifest {tag}\n\n**Preparation snapshot:** PREPARED.\n"
            f"Release: `{tag}`\nRelease identity: `refs/tags/{tag}^{{commit}}`\n"
            "Previous stable at preparation: v9.8.6; installation and publication pending at preparation.\n"
            "Collection package count: 1 admitted packages\nPolicy status: `PROVISIONAL`\n"
            f"[Other language](RELEASE_MANIFEST{other}.md)\n"
        ))
        write(root, f"{evidence}/RELEASE_NOTES{suffix}.md", (
            f"# {tag} — Fixture Skill\n\n**Release snapshot:** `{tag}`\n\n"
            "One fixture Skill and its migration instructions.\n"
            f"[Other language](RELEASE_NOTES{other}.md) · [Release Manifest](RELEASE_MANIFEST.md)\n"
            "Verification: preparation facts are in the Manifest; observed facts are in the receipt on main.\n"
        ))


def commit(root: Path, message: str = "release: fixture preparation") -> str:
    git(root, "add", ".")
    git(root, "commit", "-m", message)
    return git(root, "rev-parse", "HEAD")


def integrity(root: Path, stage: str = "prepared", *extra: str, repo: str | None = REPO,
              env: dict | None = None) -> subprocess.CompletedProcess[str]:
    repo_args = ["--repo", repo] if repo and ("--observations" in extra or stage == "attested") else []
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts/verify_release_integrity.py"),
         "--root", str(root), "--tag", TAG, "--stage", stage, *extra, *repo_args],
        cwd=root, capture_output=True, text=True, timeout=30, env=env,
    )


def test_prepared_rejects_stale_current_status_before_tag_creation(tmp_path: Path) -> None:
    make_candidate(tmp_path)
    write(tmp_path, "README.md", (
        f"# Skills\n\nv9.8.6 is the current stable release; {TAG} is not yet published.\n"
    ))
    commit(tmp_path)
    result = integrity(tmp_path)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "README.md" in result.stdout
    assert "SNAPSHOT" in result.stdout
    assert git(tmp_path, "tag", "--list") == ""


def test_tagged_checks_notes_meaning_in_the_tag_tree(tmp_path: Path) -> None:
    make_candidate(tmp_path)
    path = f"docs/evidence/releases/{TAG}/RELEASE_NOTES.zh-CN.md"
    write(tmp_path, path, f"# {TAG} — Fixture\n\n发布状态：尚未发布。\n")
    commit(tmp_path)
    git(tmp_path, "tag", "-a", TAG, "-m", "Fixture annotated tag")
    result = integrity(tmp_path, "tagged")
    assert result.returncode == 1, result.stdout + result.stderr
    assert "RELEASE_NOTES.zh-CN.md" in result.stdout
    assert "SNAPSHOT_CANDIDATE_STATE" in result.stdout


def make_attested(root: Path) -> tuple[str, str]:
    from test_release_integrity import make_valid_receipt_en, make_valid_receipt_zh
    make_candidate(root)
    candidate = commit(root)
    git(root, "tag", "-a", TAG, "-m", "Fixture annotated tag")
    tag_object = git(root, "rev-parse", f"refs/tags/{TAG}")
    for suffix, factory in (("", make_valid_receipt_en), (".zh-CN", make_valid_receipt_zh)):
        write(root, f"docs/evidence/releases/{TAG}/RELEASE_RECEIPT{suffix}.md",
              factory(tag=TAG, tag_obj=tag_object, tag_target=candidate,
                      release_url=f"https://github.com/{REPO}/releases/tag/{TAG}"))
    for path in ("README.md", "README.zh-CN.md", "CATALOG.md", "CATALOG.zh-CN.md", "docs/INSTALLATION.md", "docs/INSTALLATION.zh-CN.md", "docs/MAINTENANCE.md", "docs/MAINTENANCE.zh-CN.md"):
        doc = root / path
        doc.write_text(doc.read_text(encoding="utf-8") + f"\nCurrent stable release: `{TAG}`.\n", encoding="utf-8")
    return candidate, commit(root, "docs(release): attest fixture")


@pytest.mark.parametrize("public_path", ["README.md", "README.zh-CN.md", "CATALOG.md", "CATALOG.zh-CN.md",
                                        "docs/INSTALLATION.md", "docs/INSTALLATION.zh-CN.md", "docs/MAINTENANCE.md", "docs/MAINTENANCE.zh-CN.md"])
def test_current_attested_gate_rejects_old_installation_stable_field(tmp_path: Path, public_path: str) -> None:
    candidate, _ = make_attested(tmp_path)
    path = tmp_path / public_path
    path.write_text(path.read_text(encoding="utf-8").replace(f"Current stable release: `{TAG}`", "Current stable release: `v9.8.6`"), encoding="utf-8")
    commit(tmp_path, "fixture: stale installation authority")
    result = integrity(tmp_path, "attested", "--release-commit", candidate)
    assert result.returncode == 1, result.stdout + result.stderr
    assert public_path in result.stdout
    assert "CURRENT_STABLE" in result.stdout


def test_prepared_cannot_use_an_ignored_link_target_from_the_worktree(tmp_path: Path) -> None:
    make_candidate(tmp_path)
    readme = tmp_path / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + "\n[Migration](docs/migration-only-local.md)\n", encoding="utf-8")
    commit(tmp_path)
    write(tmp_path, "docs/migration-only-local.md", "# Local only\n")
    (tmp_path / ".git/info/exclude").write_text("docs/migration-only-local.md\n", encoding="utf-8")
    assert git(tmp_path, "status", "--porcelain") == ""
    result = integrity(tmp_path)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "DOCUMENT_LINK" in result.stdout
    assert "docs/migration-only-local.md" in result.stdout


def test_public_export_cannot_use_its_temporary_archive_as_a_link_target(tmp_path: Path) -> None:
    make_candidate(tmp_path)
    readme = tmp_path / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + "\n[Archive](tree.tar)\n", encoding="utf-8")
    commit(tmp_path)
    result = integrity(tmp_path)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "DOCUMENT_LINK" in result.stdout


def test_public_document_cli_uses_confirmed_receipt_current_version(tmp_path: Path) -> None:
    make_attested(tmp_path)
    path = tmp_path / "CATALOG.zh-CN.md"
    path.write_text(path.read_text(encoding="utf-8").replace(f"Current stable release: `{TAG}`", "Current stable release: `v9.8.6`"), encoding="utf-8")
    result = subprocess.run([sys.executable, str(ROOT / "scripts/check_public_docs.py"), "--root", str(tmp_path)], capture_output=True, text=True, timeout=30)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "CURRENT_STABLE" in result.stdout
    assert "CATALOG.zh-CN.md" in result.stdout


def add_previous_release_history(root: Path) -> None:
    """Synthetic complete prior release retained while preparing the next snapshot."""
    from test_release_integrity import make_valid_receipt_en, make_valid_receipt_zh
    previous = "v9.8.6"
    prefix = f"docs/evidence/releases/{previous}"
    for suffix, factory in (("", make_valid_receipt_en), (".zh-CN", make_valid_receipt_zh)):
        for artifact in ("RELEASE_MANIFEST", "RELEASE_NOTES"):
            existing = (root / f"docs/evidence/releases/{TAG}/{artifact}{suffix}.md").read_text(encoding="utf-8")
            write(root, f"{prefix}/{artifact}{suffix}.md", existing.replace(TAG, previous))
        write(root, f"{prefix}/RELEASE_RECEIPT{suffix}.md", factory(tag=previous))


def public_docs_cli(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(ROOT / "scripts/check_public_docs.py"), "--root", str(root)],
                          text=True, capture_output=True, timeout=30)


def test_default_quality_entry_accepts_snapshot_with_previous_release_history(tmp_path: Path) -> None:
    make_candidate(tmp_path)
    add_previous_release_history(tmp_path)
    commit(tmp_path)
    before = (tmp_path / "docs/evidence/releases/v9.8.6/RELEASE_RECEIPT.md").read_bytes()
    result = public_docs_cli(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "docs/evidence/releases/v9.8.6/RELEASE_RECEIPT.md").read_bytes() == before


@pytest.mark.parametrize("claim", ["Current stable release: v9.8.6.", "Publication status: PASS"])
def test_default_snapshot_gate_still_rejects_stale_or_premature_claims(tmp_path: Path, claim: str) -> None:
    make_candidate(tmp_path)
    add_previous_release_history(tmp_path)
    readme = tmp_path / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + "\n" + claim + "\n", encoding="utf-8")
    result = public_docs_cli(tmp_path)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "SNAPSHOT_CURRENT_STATE" in result.stdout or "UNOBSERVED_PUBLICATION" in result.stdout


def test_prepared_procedure_and_ci_command_check_the_same_snapshot(tmp_path: Path) -> None:
    import re
    import shlex
    make_candidate(tmp_path)
    add_previous_release_history(tmp_path)
    stages = (ROOT / "skills/project/release-workflow/references/RELEASE-STAGES.md").read_text()
    match = re.search(r"^\s*python3 (scripts/check_public_docs.py[^\n]*)", stages, re.M)
    assert match
    args = shlex.split(match.group(1).replace("vX.Y.Z", TAG))
    args[0] = str(ROOT / args[0])
    prepared = subprocess.run([sys.executable, *args, "--root", str(tmp_path)], capture_output=True, text=True, timeout=30)
    assert prepared.returncode == 0, prepared.stdout + prepared.stderr
    assert "python scripts/check_public_docs.py" in (ROOT / ".github/workflows/quality.yml").read_text()
    ci = public_docs_cli(tmp_path)
    assert ci.returncode == 0, ci.stdout + ci.stderr


def test_prepared_requires_chinese_installation_authority(tmp_path: Path) -> None:
    make_candidate(tmp_path)
    (tmp_path / "docs/INSTALLATION.zh-CN.md").unlink()
    commit(tmp_path)
    result = integrity(tmp_path)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "docs/INSTALLATION.zh-CN.md" in result.stdout


def test_manifest_must_name_its_preparation_time_context(tmp_path: Path) -> None:
    make_candidate(tmp_path)
    path = tmp_path / f"docs/evidence/releases/{TAG}/RELEASE_MANIFEST.md"
    path.write_text(path.read_text(encoding="utf-8").replace("**Preparation snapshot:** PREPARED.\n", ""), encoding="utf-8")
    commit(tmp_path)
    result = integrity(tmp_path)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "MANIFEST_TIME_CONTEXT" in result.stdout


def test_preparation_history_and_generic_candidate_guidance_are_accepted(tmp_path: Path) -> None:
    make_candidate(tmp_path)
    path = tmp_path / "docs/MAINTENANCE.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nIf a release candidate fails verification, stop promotion and repair it.\n", encoding="utf-8")
    commit(tmp_path)
    result = integrity(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr


def test_current_gate_cannot_silently_switch_to_another_release_target(tmp_path: Path) -> None:
    from test_release_integrity import make_valid_receipt_en, make_valid_receipt_zh
    from release_context import PUBLIC_RELEASE_DOCS
    candidate, _ = make_attested(tmp_path)
    higher = "v9.9.0"
    tag_object = git(tmp_path, "rev-parse", f"refs/tags/{TAG}")
    for suffix, factory in (("", make_valid_receipt_en), (".zh-CN", make_valid_receipt_zh)):
        write(tmp_path, f"docs/evidence/releases/{higher}/RELEASE_RECEIPT{suffix}.md",
              factory(tag=higher, tag_obj=tag_object, tag_target=candidate))
    for path in PUBLIC_RELEASE_DOCS:
        target = tmp_path / path
        target.write_text(target.read_text(encoding="utf-8").replace(f"Current stable release: `{TAG}`", f"Current stable release: `{higher}`"), encoding="utf-8")
    commit(tmp_path, "fixture: another release is now current")
    result = integrity(tmp_path, "attested", "--release-commit", candidate)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "CURRENT_RELEASE_TARGET" in result.stdout
    history = integrity(tmp_path, "attested", "--release-commit", candidate, "--mode", "historical")
    assert history.returncode == 0, history.stdout + history.stderr


def test_prepared_rejects_unobserved_installation_success(tmp_path: Path) -> None:
    make_candidate(tmp_path)
    path = tmp_path / f"docs/evidence/releases/{TAG}/RELEASE_NOTES.md"
    path.write_text(path.read_text(encoding="utf-8") + f"\nActual released-source installation for {TAG} passed.\n", encoding="utf-8")
    commit(tmp_path)
    result = integrity(tmp_path)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "UNOBSERVED_INSTALLATION" in result.stdout


def body_cli(root: Path, body: str, *extra: str) -> subprocess.CompletedProcess[str]:
    input_path = root / "input-body.md"
    input_path.write_text(body, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts/prepare_release_body.py"), "--tag", TAG,
         "--input", str(input_path), "--output", str(root / "release-body.md"), "--repo", REPO, *extra],
        cwd=root, capture_output=True, text=True, timeout=30,
    )


def test_body_preparation_rejects_unpublished_status_even_with_safe_links(tmp_path: Path) -> None:
    result = body_cli(tmp_path, (
        f"# {TAG} — Release\n\nRelease status: not yet published.\n\n"
        "[Manifest](https://github.com/LightDevCoder/skills/blob/main/"
        f"docs/evidence/releases/{TAG}/RELEASE_MANIFEST.md)\n"
    ))
    assert result.returncode == 1, result.stdout + result.stderr
    assert "RELEASE_BODY_CANDIDATE_STATE" in result.stderr
    assert not (tmp_path / "release-body.md").exists()


def observation_file(root: Path, candidate: str, **updates) -> Path:
    data = {
        "kind": "test-double", "tag": TAG, "candidate": candidate,
        "ci": {"databaseId": 1234, "headSha": candidate, "status": "completed", "conclusion": "success"},
    }
    data.update(updates)
    path = root.parent / f"{root.name}-observations.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_ci_verified_gate_uses_exact_completed_success_observation(tmp_path: Path) -> None:
    make_candidate(tmp_path)
    candidate = commit(tmp_path)
    observations = observation_file(tmp_path, candidate)
    result = integrity(tmp_path, "ci_verified", "--observations", str(observations), "--simulate")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "SIMULATED_PASS" in result.stdout
    data = json.loads(observations.read_text(encoding="utf-8"))
    data["ci"]["headSha"] = "f" * 40
    observations.write_text(json.dumps(data), encoding="utf-8")
    wrong_sha = integrity(tmp_path, "ci_verified", "--observations", str(observations), "--simulate")
    assert wrong_sha.returncode == 1, wrong_sha.stdout + wrong_sha.stderr
    assert "CI_IDENTITY" in wrong_sha.stdout


def test_install_verified_requires_actual_source_and_destination_observations(tmp_path: Path) -> None:
    make_candidate(tmp_path)
    candidate = commit(tmp_path)
    git(tmp_path, "tag", "-a", TAG, "-m", "Fixture annotated tag")
    observations = observation_file(tmp_path, candidate)
    result = integrity(tmp_path, "install_verified", "--observations", str(observations), "--simulate")
    assert result.returncode == 1, result.stdout + result.stderr
    assert "INSTALLATION_UNOBSERVED" in result.stdout


def installation_observation(candidate: str) -> dict:
    manifest = {"fixture-skill": {"SKILL.md": "a" * 64}}
    destination = {"packages": 1, "files": 1, "exact": True, "actual_package_manifest": manifest}
    return {
        "status": "VERIFIED", "tag": TAG, "pinned_commit": candidate, "default_commit": candidate,
        "pinned_package_manifest": manifest, "default_package_manifest": manifest,
        "observations": [{"case": case, "destinations": [destination]} for case in ("pinned-whole", "default-whole")],
    }


def test_published_requires_an_observed_release_result(tmp_path: Path) -> None:
    make_candidate(tmp_path)
    candidate = commit(tmp_path)
    git(tmp_path, "tag", "-a", TAG, "-m", "Fixture annotated tag")
    observations = observation_file(tmp_path, candidate, installation=installation_observation(candidate))
    result = integrity(tmp_path, "published", "--observations", str(observations), "--simulate")
    assert result.returncode == 1, result.stdout + result.stderr
    assert "PUBLICATION_UNOBSERVED" in result.stdout


def test_body_installation_claim_requires_bound_observations(tmp_path: Path) -> None:
    make_candidate(tmp_path)
    candidate = commit(tmp_path)
    git(tmp_path, "tag", "-a", TAG, "-m", "Fixture annotated tag")
    notes = (tmp_path / f"docs/evidence/releases/{TAG}/RELEASE_NOTES.md").read_text(encoding="utf-8")
    body = notes + f"\nActual released-source installation for {TAG} passed.\n"
    denied = body_cli(tmp_path, body)
    assert denied.returncode == 1, denied.stdout + denied.stderr
    assert "UNOBSERVED_INSTALLATION" in denied.stderr
    observations = observation_file(tmp_path, candidate, installation=installation_observation(candidate))
    allowed = body_cli(tmp_path, body, "--root", str(tmp_path), "--release-commit", candidate,
                       "--observations", str(observations), "--simulate")
    assert allowed.returncode == 0, allowed.stdout + allowed.stderr
    assert "SIMULATED" in allowed.stderr
    transformed = (tmp_path / "release-body.md").read_text(encoding="utf-8")
    assert f"blob/{TAG}/docs/evidence/releases/{TAG}/RELEASE_MANIFEST.md" in transformed


def test_body_preparation_checks_version_navigation_and_keeps_parent_paths(tmp_path: Path) -> None:
    make_candidate(tmp_path)
    write(tmp_path, "docs/evidence/source-proof.md", "# Source proof\n")
    candidate = commit(tmp_path)
    git(tmp_path, "tag", "-a", TAG, "-m", "Fixture annotated tag")
    notes = (tmp_path / f"docs/evidence/releases/{TAG}/RELEASE_NOTES.md").read_text(encoding="utf-8")
    notes += "\n[Source proof](../../source-proof.md)\n"
    result = body_cli(tmp_path, notes, "--root", str(tmp_path))
    assert result.returncode == 0, result.stdout + result.stderr
    assert f"blob/{TAG}/docs/evidence/source-proof.md" in (tmp_path / "release-body.md").read_text(encoding="utf-8")
    wrong = body_cli(tmp_path, notes + "\n[v9.8.6](https://github.com/LightDevCoder/skills/releases/tag/v9.8.7)\n",
                     "--root", str(tmp_path), "--release-commit", candidate)
    assert wrong.returncode == 1, wrong.stdout + wrong.stderr
    assert "RELEASE_LINK_VERSION" in wrong.stderr


def test_snapshot_target_install_commands_remain_templates(tmp_path: Path) -> None:
    make_candidate(tmp_path)
    path = tmp_path / "docs/INSTALLATION.md"
    original = path.read_text(encoding="utf-8")
    command = f"\n```bash\nnpx skills add LightDevCoder/skills#{TAG}\n```\n"
    path.write_text(original + command, encoding="utf-8")
    commit(tmp_path)
    denied = integrity(tmp_path)
    assert denied.returncode == 1, denied.stdout + denied.stderr
    assert "FUTURE_INSTALL_TEMPLATE" in denied.stdout
    path.write_text(original + "\n## Installation command templates\n" + command, encoding="utf-8")
    commit(tmp_path, "fixture: explicitly scoped future command template")
    allowed = integrity(tmp_path)
    assert allowed.returncode == 0, allowed.stdout + allowed.stderr


def test_verified_titles_do_not_establish_another_current_release(tmp_path: Path) -> None:
    make_attested(tmp_path)
    for suffix in ("", ".zh-CN"):
        write(tmp_path, f"docs/evidence/releases/v9.9.0/RELEASE_RECEIPT{suffix}.md",
              "# v9.9.0\n\nStatus: VERIFIED\n状态：VERIFIED\n")
    result = subprocess.run([sys.executable, str(ROOT / "scripts/check_public_docs.py"), "--root", str(tmp_path)], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr


def test_final_main_ci_is_checked_without_writing_it_into_the_receipt(tmp_path: Path) -> None:
    candidate, attestation = make_attested(tmp_path)
    receipt = tmp_path / f"docs/evidence/releases/{TAG}/RELEASE_RECEIPT.md"
    receipt_before = receipt.read_bytes()
    ci_path = tmp_path.parent / f"{tmp_path.name}-final-ci.json"
    data = {"kind": "test-double", "databaseId": 5678, "headSha": attestation,
            "status": "completed", "conclusion": "success"}
    ci_path.write_text(json.dumps(data), encoding="utf-8")
    allowed = integrity(tmp_path, "attested", "--release-commit", candidate,
                        "--final-ci", str(ci_path), "--simulate")
    assert allowed.returncode == 0, allowed.stdout + allowed.stderr
    assert "SIMULATED_PASS" in allowed.stdout
    data["headSha"] = candidate
    ci_path.write_text(json.dumps(data), encoding="utf-8")
    denied = integrity(tmp_path, "attested", "--release-commit", candidate,
                       "--final-ci", str(ci_path), "--simulate")
    assert denied.returncode == 1, denied.stdout + denied.stderr
    assert "CI_IDENTITY" in denied.stdout
    assert receipt.read_bytes() == receipt_before
    assert attestation.encode() not in receipt_before
    assert git(tmp_path, "status", "--porcelain") == ""


@pytest.mark.parametrize("kind", [None, "unknown", {}, "test-double"])
def test_final_ci_requires_an_explicit_observation_kind(tmp_path: Path, kind) -> None:
    candidate, attestation = make_attested(tmp_path)
    ci = {"databaseId": 5678, "headSha": attestation, "status": "completed", "conclusion": "success"}
    if kind is not None:
        ci["kind"] = kind
    path = tmp_path.parent / f"{tmp_path.name}-ci-kind.json"
    path.write_text(json.dumps(ci), encoding="utf-8")
    result = integrity(tmp_path, "attested", "--release-commit", candidate, "--final-ci", str(path))
    assert result.returncode == 1, result.stdout + result.stderr
    expected = "SIMULATION_FLAG_REQUIRED" if kind == "test-double" else "OBSERVATION_KIND"
    assert expected in result.stdout


@pytest.mark.parametrize("claim", ["| **GitHub Release Publication** | `PASS` |",
                                 "| GitHub Release 发布 | SUCCESS |", "Publication: VERIFIED",
                                 "Publication status: PASS", "Publication result: SUCCESS"])
def test_prepared_rejects_unobserved_publication_table_claims(tmp_path: Path, claim: str) -> None:
    make_candidate(tmp_path)
    path = tmp_path / f"docs/evidence/releases/{TAG}/RELEASE_NOTES.md"
    path.write_text(path.read_text(encoding="utf-8") + "\n" + claim + "\n", encoding="utf-8")
    commit(tmp_path)
    result = integrity(tmp_path)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "UNOBSERVED_PUBLICATION" in result.stdout


@pytest.mark.parametrize("stage", ["prepared", "attested"])
def test_public_tree_export_remains_usable_on_python39(tmp_path: Path, stage: str) -> None:
    runtime = Path("/usr/bin/python3")
    if not runtime.is_file():
        pytest.skip("System Python is unavailable")
    if stage == "prepared":
        make_candidate(tmp_path)
        commit(tmp_path)
    else:
        make_attested(tmp_path)
    result = subprocess.run([str(runtime), str(ROOT / "scripts/verify_release_integrity.py"),
                             "--root", str(tmp_path), "--tag", TAG, "--stage", stage],
                            text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr


def test_compat_archive_export_rejects_symlink_escape(tmp_path: Path) -> None:
    import io
    import tarfile
    from verify_release_integrity import extract_git_archive
    archive = tmp_path / "unsafe.tar"
    with tarfile.open(archive, "w") as writer:
        link = tarfile.TarInfo("linked")
        link.type = tarfile.SYMTYPE
        link.linkname = ".."
        writer.addfile(link)
        member = tarfile.TarInfo("linked/outside.md")
        content = b"must not escape"
        member.size = len(content)
        writer.addfile(member, io.BytesIO(content))
    destination = tmp_path / "exported"
    destination.mkdir()
    with tarfile.open(archive) as reader, pytest.raises(ValueError, match="outside"):
        extract_git_archive(reader, destination)
    assert not (tmp_path / "outside.md").exists()


@pytest.mark.parametrize("fault", ["wrong-title", "unpublished", "wrong-link", "draft"])
def test_attested_remote_body_uses_the_same_semantic_gate(tmp_path: Path, monkeypatch, capsys, fault: str) -> None:
    import verify_release_integrity as verifier
    make_attested(tmp_path)
    body = (tmp_path / f"docs/evidence/releases/{TAG}/RELEASE_NOTES.md").read_text(encoding="utf-8")
    prefix = f"https://github.com/{REPO}/blob/{TAG}/docs/evidence/releases/{TAG}/"
    body = body.replace("(RELEASE_NOTES.zh-CN.md)", f"({prefix}RELEASE_NOTES.zh-CN.md)")
    body = body.replace("(RELEASE_MANIFEST.md)", f"({prefix}RELEASE_MANIFEST.md)")
    if fault == "wrong-title":
        body = body.replace(TAG, "v9.8.6", 1)
    elif fault == "unpublished":
        body += "\nRelease status: not yet published.\n"
    elif fault == "wrong-link":
        body += f"\n[v9.8.6](https://github.com/{REPO}/releases/tag/{TAG})\n"
    release = {"body": body, "tagName": TAG, "isDraft": fault == "draft", "isPrerelease": False,
               "publishedAt": "2026-10-09T00:00:00Z", "url": f"https://github.com/{REPO}/releases/tag/{TAG}"}
    original_run = subprocess.run
    def run(command, *args, **kwargs):
        if command[:3] == ["gh", "release", "view"]:
            return subprocess.CompletedProcess(command, 0, json.dumps(release), "")
        return original_run(command, *args, **kwargs)
    monkeypatch.setattr(verifier.subprocess, "run", run)
    original_tag_check = verifier.check_tag_immutability
    def check_tag(*args, **kwargs):
        kwargs["check_remote"] = False
        return original_tag_check(*args, **kwargs)
    monkeypatch.setattr(verifier, "check_tag_immutability", check_tag)
    monkeypatch.setattr(sys, "argv", ["verify_release_integrity.py", "--root", str(tmp_path),
                                     "--tag", TAG, "--stage", "attested", "--check-remote", "--repo", REPO])
    assert verifier.main() == 1
    output = capsys.readouterr().out
    assert "GitHub Release" in output
    assert "RELEASE_BODY_INCONSISTENT" in output or "PUBLICATION_IDENTITY" in output


def test_six_stage_rehearsal_uses_two_committed_trees_and_external_test_facts(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    from release_context import PUBLIC_RELEASE_DOCS
    from test_release_integrity import make_valid_receipt_en, make_valid_receipt_zh
    make_candidate(tmp_path)
    git(tmp_path, "add", ".")
    candidate_tree = git(tmp_path, "write-tree")
    candidate = commit(tmp_path)
    assert git(tmp_path, "rev-parse", "HEAD^{tree}") == candidate_tree
    prepared = integrity(tmp_path)
    assert prepared.returncode == 0, prepared.stdout + prepared.stderr
    observations = observation_file(tmp_path, candidate)
    ci = integrity(tmp_path, "ci_verified", "--observations", str(observations), "--simulate")
    assert ci.returncode == 0 and "SIMULATED_PASS" in ci.stdout, ci.stdout + ci.stderr
    git(tmp_path, "tag", "-a", TAG, "-m", "Fixture annotated tag")
    tag_object = git(tmp_path, "rev-parse", f"refs/tags/{TAG}")
    tagged = integrity(tmp_path, "tagged", "--observations", str(observations), "--simulate")
    assert tagged.returncode == 0 and "SIMULATED_PASS" in tagged.stdout, tagged.stdout + tagged.stderr
    data = json.loads(observations.read_text(encoding="utf-8"))
    data["installation"] = installation_observation(candidate)
    observations.write_text(json.dumps(data), encoding="utf-8")
    installed = integrity(tmp_path, "install_verified", "--observations", str(observations), "--simulate")
    assert installed.returncode == 0 and "SIMULATED_PASS" in installed.stdout, installed.stdout + installed.stderr
    body_path = tmp_path.parent / f"{tmp_path.name}-body.md"
    body = subprocess.run(
        [sys.executable, str(ROOT / "scripts/prepare_release_body.py"), "--root", str(tmp_path),
         "--tag", TAG, "--repo", REPO, "--observations", str(observations), "--simulate", "--output", str(body_path)],
        capture_output=True, text=True, timeout=30,
    )
    assert body.returncode == 0 and "SIMULATED" in body.stderr, body.stdout + body.stderr
    data["release"] = {
        "tagName": TAG, "isDraft": False, "isPrerelease": False, "publishedAt": "2026-10-09T00:00:00Z",
        "url": f"https://github.com/{REPO}/releases/tag/{TAG}",
        "body": body_path.read_text(encoding="utf-8"),
    }
    observations.write_text(json.dumps(data), encoding="utf-8")
    published = integrity(tmp_path, "published", "--observations", str(observations), "--simulate")
    assert published.returncode == 0 and "SIMULATED_PASS" in published.stdout, published.stdout + published.stderr
    for suffix, factory in (("", make_valid_receipt_en), (".zh-CN", make_valid_receipt_zh)):
        write(tmp_path, f"docs/evidence/releases/{TAG}/RELEASE_RECEIPT{suffix}.md",
              factory(tag=TAG, tag_obj=tag_object, tag_target=candidate, timestamp=data["release"]["publishedAt"],
                          release_url=f"https://github.com/{REPO}/releases/tag/{TAG}") +
              "\nEvidence class: local rehearsal; external results are test doubles.\n")
    for path in PUBLIC_RELEASE_DOCS:
        destination = tmp_path / path
        destination.write_text(destination.read_text(encoding="utf-8") + f"\nCurrent stable release: `{TAG}`.\n", encoding="utf-8")
    git(tmp_path, "add", ".")
    attestation_tree = git(tmp_path, "write-tree")
    attestation = commit(tmp_path, "docs(release): simulated attestation")
    assert candidate != attestation and candidate_tree != attestation_tree
    assert git(tmp_path, "rev-parse", "HEAD^{tree}") == attestation_tree
    assert git(tmp_path, "rev-parse", f"refs/tags/{TAG}") == tag_object
    assert git(tmp_path, "rev-parse", f"refs/tags/{TAG}^{{tree}}") == candidate_tree
    missing = subprocess.run(["git", "cat-file", "-e", f"{candidate}:docs/evidence/releases/{TAG}/RELEASE_RECEIPT.md"], cwd=tmp_path, capture_output=True)
    assert missing.returncode != 0
    attested = integrity(tmp_path, "attested", "--release-commit", candidate,
                         "--observations", str(observations), "--simulate")
    assert attested.returncode == 0 and "SIMULATED_PASS" in attested.stdout, attested.stdout + attested.stderr
    assert len(git(tmp_path, "log", "--format=%H").splitlines()) == 2
    assert git(tmp_path, "status", "--porcelain") == ""


@pytest.mark.parametrize("stage", ["prepared", "ci_verified"])
def test_historical_mode_cannot_promote_candidates(tmp_path: Path, stage: str) -> None:
    make_candidate(tmp_path)
    commit(tmp_path)
    result = integrity(tmp_path, stage, "--mode", "historical")
    assert result.returncode == 2, result.stdout + result.stderr
    assert "cannot prepare or promote" in result.stderr


def test_existing_v027_tag_is_audited_without_rewriting_main_or_tag() -> None:
    before = git(ROOT, "rev-parse", "refs/tags/v0.2.7")
    main_readme_before = (ROOT / "README.md").read_bytes()
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/verify_release_integrity.py"), "--root", str(ROOT),
         "--tag", "v0.2.7", "--stage", "tagged", "--mode", "historical", "--allow-dirty"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0 and "HISTORICAL_SNAPSHOT" in result.stdout, result.stdout + result.stderr
    assert git(ROOT, "rev-parse", "refs/tags/v0.2.7") == before
    assert (ROOT / "README.md").read_bytes() == main_readme_before


def test_known_defect_notice_keeps_a_published_body_valid(tmp_path: Path, monkeypatch, capsys) -> None:
    """BROKEN-RELEASE.md marks a bad release by prefixing its body; the attested gate must still pass."""
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    import verify_release_integrity as verifier
    make_attested(tmp_path)
    body = (tmp_path / f"docs/evidence/releases/{TAG}/RELEASE_NOTES.md").read_text(encoding="utf-8")
    prefix = f"https://github.com/{REPO}/blob/{TAG}/docs/evidence/releases/{TAG}/"
    body = body.replace("(RELEASE_NOTES.zh-CN.md)", f"({prefix}RELEASE_NOTES.zh-CN.md)")
    body = body.replace("(RELEASE_MANIFEST.md)", f"({prefix}RELEASE_MANIFEST.md)")
    body = "> **Known defect:** one script crashes on empty input. Use v9.8.8 instead.\n\n" + body
    release = {"body": body, "tagName": TAG, "isDraft": False, "isPrerelease": False,
               "publishedAt": "2026-10-09T00:00:00Z", "url": f"https://github.com/{REPO}/releases/tag/{TAG}"}
    seen = []
    original_run = subprocess.run
    def run(command, *args, **kwargs):
        if command[:3] == ["gh", "release", "view"]:
            seen.append(command)
            return subprocess.CompletedProcess(command, 0, json.dumps(release), "")
        return original_run(command, *args, **kwargs)
    monkeypatch.setattr(verifier.subprocess, "run", run)
    result = verifier.check_github_release_navigation(TAG, repo=REPO, cwd=tmp_path)
    assert result.passed, result.message
    assert seen and seen[0][seen[0].index("--repo") + 1] == REPO
    wrong_repo = verifier.check_github_release_navigation(TAG, repo="someone-else/skills", cwd=tmp_path)
    assert not wrong_repo.passed and "PUBLICATION_IDENTITY" in wrong_repo.message


def test_publication_observation_is_pinned_to_the_resolved_repository(tmp_path: Path) -> None:
    """Without --repo the gate resolves the repository (here GITHUB_REPOSITORY) and rejects another owner's release."""
    import os
    make_candidate(tmp_path)
    candidate = commit(tmp_path)
    git(tmp_path, "tag", "-a", TAG, "-m", "Fixture annotated tag")
    observations = observation_file(tmp_path, candidate)
    data = json.loads(observations.read_text(encoding="utf-8"))
    data["installation"] = installation_observation(candidate)
    data["release"] = {"tagName": TAG, "isDraft": False, "isPrerelease": False,
                       "publishedAt": "2026-10-09T00:00:00Z",
                       "url": f"https://github.com/someone-else/skills/releases/tag/{TAG}", "body": "x"}
    observations.write_text(json.dumps(data), encoding="utf-8")
    env = {**os.environ, "GITHUB_REPOSITORY": REPO}
    result = integrity(tmp_path, "published", "--observations", str(observations), "--simulate", repo=None, env=env)
    assert result.returncode == 1, result.stdout + result.stderr
    assert f"GitHub Repo:    {REPO}" in result.stdout
    assert "PUBLICATION_IDENTITY" in result.stdout + result.stderr


def test_publication_gate_fails_when_no_repository_can_be_found(tmp_path: Path) -> None:
    import os
    make_candidate(tmp_path)
    candidate = commit(tmp_path)
    observations = observation_file(tmp_path, candidate)
    env = {k: v for k, v in os.environ.items() if k != "GITHUB_REPOSITORY"}
    env["PATH"] = str(tmp_path / "no-gh") + os.pathsep + "/usr/bin:/bin"  # no gh; the fixture has no origin
    result = integrity(tmp_path, "ci_verified", "--observations", str(observations), "--simulate", repo=None, env=env)
    assert result.returncode == 1 and "REPOSITORY_UNRESOLVED" in result.stdout, result.stdout + result.stderr


@pytest.mark.parametrize("url, accepted", [
    (f"https://github.com/LightDevCoder/skills/releases/tag/{TAG}", False),  # old owner: redirects, never live
    (f"https://github.com/light-cheng/skills/releases/tag/{TAG}", True),
    (f"https://github.com/Light-Cheng/Skills/releases/tag/{TAG}", True),
    (f"https://github.com/someone-else/skills/releases/tag/{TAG}", False),
    (f"https://github.com/light-cheng/other/releases/tag/{TAG}", False),
    ("https://github.com/light-cheng/skills/releases/tag/v9.8.6", False),
])
def test_live_publication_accepts_only_the_resolved_repository(url: str, accepted: bool) -> None:
    from release_context import validate_publication_observation
    record = {"tagName": TAG, "isDraft": False, "isPrerelease": False,
              "publishedAt": "2026-10-16T07:22:12Z", "url": url}
    assert (validate_publication_observation(record, TAG, "fixture", "light-cheng/skills") == []) is accepted


def test_current_attested_receipt_must_name_the_resolved_repository(tmp_path: Path) -> None:
    """Without --repo or --check-remote, a current attested run resolves the repo; an old-owner receipt fails."""
    import os
    from test_release_integrity import make_valid_receipt_en, make_valid_receipt_zh
    candidate, _ = make_attested(tmp_path)
    tag_object = git(tmp_path, "rev-parse", f"refs/tags/{TAG}")
    old = f"https://github.com/LightDevCoder/skills/releases/tag/{TAG}"
    for suffix, factory in (("", make_valid_receipt_en), (".zh-CN", make_valid_receipt_zh)):
        write(tmp_path, f"docs/evidence/releases/{TAG}/RELEASE_RECEIPT{suffix}.md",
              factory(tag=TAG, tag_obj=tag_object, tag_target=candidate, release_url=old))
    commit(tmp_path, "receipt names the pre-rename owner")
    env = {**os.environ, "GITHUB_REPOSITORY": REPO}
    current = integrity(tmp_path, "attested", "--release-commit", candidate, repo=None, env=env)
    assert current.returncode == 1 and "RECEIPT_URL_MISMATCH" in current.stdout, current.stdout + current.stderr
    assert f"GitHub Repo:    {REPO}" in current.stdout
    history = integrity(tmp_path, "attested", "--release-commit", candidate, "--mode", "historical", repo=None, env=env)
    assert "RECEIPT_URL_MISMATCH" not in history.stdout, history.stdout
    assert "[PASS] Receipt Consistency" in history.stdout, history.stdout
