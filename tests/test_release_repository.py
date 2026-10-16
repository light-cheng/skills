"""Release scripts take the repository from the checkout and keep main on the verified tree."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import repo_identity  # noqa: E402
from check_merged_candidate import check  # noqa: E402


def completed(argv, code=0, out=""):
    return subprocess.CompletedProcess(argv, code, out, "")


@pytest.mark.parametrize("url", [
    "https://github.com/light-cheng/skills.git",
    "https://github.com/light-cheng/skills",
    "https://github.com/light-cheng/skills/",
    "https://x-access-token@github.com/light-cheng/skills.git",
    "git@github.com:light-cheng/skills.git",
    "ssh://git@github.com/light-cheng/skills.git",
])
def test_remote_url_forms_resolve_to_owner_and_name(url):
    assert repo_identity.parse_remote_url(url + "\n") == "light-cheng/skills"


@pytest.mark.parametrize("url", [
    "https://gitlab.com/light-cheng/skills.git",
    "https://github.com/light-cheng",
    "https://github.com/light-cheng/skills/tree/main",
    "/srv/git/skills.git",
    "",
])
def test_non_github_or_partial_remotes_are_rejected(url):
    with pytest.raises(ValueError):
        repo_identity.parse_remote_url(url)


@pytest.mark.parametrize("value", ["skills", "a/b/c", "owner/..", "-owner/skills", "owner/skills.git", "owner/sk ills"])
def test_explicit_repository_must_be_owner_and_name(value):
    with pytest.raises(ValueError):
        repo_identity.resolve_repository(value, env={})


def test_resolution_order_is_explicit_then_actions_then_gh_then_origin():
    calls = []

    def runner(argv, **kwargs):
        calls.append(argv[0])
        if argv[0] == "gh":
            return completed(argv, 0, "light-cheng/skills\n")
        return completed(argv, 0, "https://github.com/LightDevCoder/skills.git\n")

    assert repo_identity.resolve_repository("me/fork", env={"GITHUB_REPOSITORY": "ci/skills"}, runner=runner) == "me/fork"
    assert repo_identity.resolve_repository(None, env={"GITHUB_REPOSITORY": "ci/skills"}, runner=runner) == "ci/skills"
    assert calls == []
    # gh follows the rename; the stale origin name is only a fallback.
    assert repo_identity.resolve_repository(None, Path("."), env={}, runner=runner) == "light-cheng/skills"
    assert calls == ["gh"]


def test_origin_is_used_when_gh_is_missing_or_fails():
    def missing_gh(argv, **kwargs):
        if argv[0] == "gh":
            raise FileNotFoundError("gh")
        return completed(argv, 0, "git@github.com:light-cheng/skills.git\n")

    def failing_gh(argv, **kwargs):
        if argv[0] == "gh":
            return completed(argv, 1, "")
        return completed(argv, 0, "https://github.com/light-cheng/skills.git\n")

    for runner in (missing_gh, failing_gh):
        assert repo_identity.resolve_repository(None, Path("."), env={}, runner=runner) == "light-cheng/skills"


def test_unresolvable_repository_fails_instead_of_guessing():
    def runner(argv, **kwargs):
        return completed(argv, 1 if argv[0] == "gh" else 0, "/srv/git/skills.git\n")

    with pytest.raises(ValueError, match="--repo"):
        repo_identity.resolve_repository(None, Path("."), env={}, runner=runner)


def test_release_url_matching_is_exact_when_the_repository_is_known():
    url = "https://github.com/light-cheng/skills/releases/tag/v1.2.3"
    assert repo_identity.is_release_url(url, "v1.2.3", "light-cheng/skills")
    assert repo_identity.is_release_url(url, "v1.2.3")
    assert not repo_identity.is_release_url(url, "v1.2.3", "LightDevCoder/skills")
    assert not repo_identity.is_release_url(url, "v1.2.30")
    assert not repo_identity.is_release_url(url + "0", "v1.2.3")
    assert not repo_identity.is_release_url("https://evil.example/light-cheng/skills/releases/tag/v1.2.3", "v1.2.3")
    assert not repo_identity.is_release_url(None, "v1.2.3")


def test_release_scripts_do_not_hard_code_an_owner():
    for path in (ROOT / "scripts").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"(?i)LightDevCoder|light-cheng", text), path.name


def test_published_observation_rejects_another_repository():
    from release_context import validate_publication_observation
    record = {"tagName": "v1.2.3", "isDraft": False, "isPrerelease": False,
              "publishedAt": "2026-10-16T00:00:00Z",
              "url": "https://github.com/someone-else/skills/releases/tag/v1.2.3"}
    assert validate_publication_observation(record, "v1.2.3", "obs") == []
    assert validate_publication_observation(record, "v1.2.3", "obs", "light-cheng/skills")


# --- pull-request path: the merged main commit must carry the candidate tree ---

def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "user.email", "bot@example.com")
    git(tmp_path, "config", "user.name", "Bot")
    (tmp_path / "a.txt").write_text("base\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-qm", "base")
    git(tmp_path, "switch", "-qc", "release/v1.2.3")
    (tmp_path / "a.txt").write_text("candidate\n")
    git(tmp_path, "commit", "-qam", "release: prepare v1.2.3")
    git(tmp_path, "switch", "-q", "main")
    return tmp_path


def test_merge_commit_with_the_candidate_tree_passes(repo: Path):
    candidate = git(repo, "rev-parse", "release/v1.2.3")
    git(repo, "merge", "-q", "--no-ff", "-m", "Merge release", "release/v1.2.3")
    assert check(repo, candidate, git(repo, "rev-parse", "HEAD"), "main") == []


def test_squash_merge_with_the_candidate_tree_passes(repo: Path):
    candidate = git(repo, "rev-parse", "release/v1.2.3")
    git(repo, "merge", "-q", "--squash", "release/v1.2.3")
    git(repo, "commit", "-qm", "release: prepare v1.2.3 (#9)")
    assert check(repo, candidate, "HEAD", "main") == []


def test_merge_onto_a_moved_main_is_blocked(repo: Path):
    candidate = git(repo, "rev-parse", "release/v1.2.3")
    (repo / "b.txt").write_text("landed after the candidate CI\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "unrelated")
    git(repo, "merge", "-q", "--no-ff", "-m", "Merge release", "release/v1.2.3")
    problems = check(repo, candidate, "HEAD", "main")
    assert len(problems) == 1 and "differs from candidate tree" in problems[0]


def test_merged_commit_must_be_on_the_branch(repo: Path):
    candidate = git(repo, "rev-parse", "release/v1.2.3")
    problems = check(repo, candidate, candidate, "main")
    assert len(problems) == 1 and "is not on main" in problems[0]


def test_unknown_commits_and_branch_are_blocked(repo: Path):
    assert len(check(repo, "0" * 40, "f" * 40, "main")) == 2
    candidate = git(repo, "rev-parse", "release/v1.2.3")
    assert "fetch it first" in check(repo, candidate, candidate, "origin/main")[0]


def test_cli_reports_blocked_and_exit_code(repo: Path):
    candidate = git(repo, "rev-parse", "release/v1.2.3")
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/check_merged_candidate.py"),
                           "--candidate", candidate, "--merged", "main", "--branch", "main", "--root", str(repo)],
                          capture_output=True, text=True)
    assert proc.returncode == 1 and "RESULT: BLOCKED" in proc.stdout


def test_known_repository_matches_without_case_but_tag_exactly():
    url = "https://github.com/Light-Cheng/Skills/releases/tag/v1.2.3"
    assert repo_identity.is_release_url(url, "v1.2.3", "light-cheng/skills")
    assert not repo_identity.is_release_url(url.replace("v1.2.3", "V1.2.3"), "v1.2.3", "light-cheng/skills")


def test_missing_git_counts_as_no_remote():
    def runner(argv, **kwargs):
        raise FileNotFoundError(argv[0])

    assert repo_identity.remote_repository(Path("."), runner=runner) is None
    with pytest.raises(ValueError):
        repo_identity.resolve_repository(None, Path("."), env={}, runner=runner)


def test_installation_verifier_reports_an_unresolvable_repository(monkeypatch, capsys):
    import importlib.util
    spec = importlib.util.spec_from_file_location("release_installation_cli", ROOT / "scripts/verify_release_installation.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "resolve_repository", lambda *a, **k: (_ for _ in ()).throw(ValueError("cannot find the GitHub repository")))
    monkeypatch.setattr(sys, "argv", ["verify_release_installation.py", "--tag", "v1.2.3",
                                      "--expected-commit", "a" * 40, "--output", "unused"])
    with pytest.raises(SystemExit) as exit_info:
        module.main()
    assert exit_info.value.code == 2
    assert "cannot find the GitHub repository" in capsys.readouterr().err


def test_documented_commands_brace_variables_before_a_colon():
    """In zsh, "$SHA:refs/..." applies the :r modifier and pushes a wrong refspec; use ${SHA}."""
    for path in (ROOT / "skills/project/release-workflow").rglob("*.md"):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            assert not re.search(r"\$[A-Za-z_][A-Za-z0-9_]*:", line), f"{path.name}:{number}: {line.strip()}"
