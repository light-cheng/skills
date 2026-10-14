"""Port of skills/review/review-loop/tests/manuscript-profile-contract-tests.ps1."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tests"))

from check_helpers import Checks  # noqa: E402


def run_checks(root: Path = ROOT) -> tuple[int, list[str]]:
    c = Checks()
    skill_path = root / "SKILL.md"
    metadata_path = root / "agents" / "openai.yaml"
    profile_path = root / "references" / "profiles" / "manuscript.md"
    generic_path = root / "references" / "profiles" / "generic.md"
    finding_path = root / "references" / "finding-schema.md"
    evidence_path = root / "references" / "evidence-protocol.md"
    stopping_path = root / "references" / "stopping-rules.md"
    roles_path = root / "references" / "subagent-protocol.md"

    for label, path in (
        ("Skill", skill_path),
        ("Agent metadata", metadata_path),
        ("Manuscript Profile", profile_path),
        ("Generic Profile", generic_path),
        ("Finding Schema", finding_path),
        ("Evidence Protocol", evidence_path),
        ("Stopping Rules", stopping_path),
        ("Role Protocol", roles_path),
    ):
        c.require_file(root, path.relative_to(root).as_posix(), label)

    skill = skill_path.read_text(encoding="utf-8", errors="replace")
    metadata = metadata_path.read_text(encoding="utf-8", errors="replace")
    profile = profile_path.read_text(encoding="utf-8", errors="replace")
    generic = generic_path.read_text(encoding="utf-8", errors="replace")
    finding = finding_path.read_text(encoding="utf-8", errors="replace")
    stopping = stopping_path.read_text(encoding="utf-8", errors="replace")

    c.require_match("TC-MS-001 profile link", skill, r"(?im)\[manuscript\.md\]\(references/profiles/manuscript\.md\)")
    c.require_match("TC-MS-001 profile heading", profile, r"(?im)^# Manuscript Profile$")
    c.require_match("TC-MS-001 implicit invocation", metadata, r"(?im)^\s*allow_implicit_invocation:\s*true\s*$")
    c.require_match("TC-MS-001 generic preserved", generic, r"(?im)^# Generic Profile$")

    c.require_match("TC-MS-002 review axes", profile, r"(?im)^## Review axes$")
    for axis in ("Reader task", "Source authority", "Terminology", "Reader fit", "Safety", "Format structure", "Images and figures", "Lifecycle", "Generation reproducibility", "Compatibility"):
        c.require_match(f"TC-MS-002 axis {axis}", profile, rf"(?i)\*\*{axis}")

    c.require_match("TC-MS-003 evidence requirements", profile, r"(?im)^## Evidence requirements$")
    for term in ("ManuscriptBrief", "Acceptance Charter", "SHA-256", "source map/register", "lifecycle state", "semantic batch", "human-gate", "locked-source", "structural", "generation", "render", "visual", "semantic", "round-trip", "fresh independent Evaluator"):
        c.require_match(f"TC-MS-003 evidence {term}", profile, rf"(?i){term}")
    c.require_no_match("TC-MS-003 unsupported primary labels absent", profile, r"(?im)(?:Evidence label|Label):\s*(?:render|visual)\b")

    c.require_match("TC-MS-004 specialist reviewers", profile, r"(?im)^## Specialist reviewers$")
    c.require_match("TC-MS-004 severity guidance", profile, r"(?im)^## Severity guidance$")
    c.require_match("TC-MS-004 severity values", profile, r"(?is)\*\*Critical\*\*.*\*\*High\*\*.*\*\*Medium\*\*.*\*\*Low\*\*")
    c.require_match("TC-MS-004 acceptance conditions", profile, r"(?im)^## Acceptance conditions$")
    c.require_match("TC-MS-004 failure cases", profile, r"(?im)^## Artifact-specific failure cases$")

    c.require_match("TC-MS-005 Core stopping rules", profile, r"(?i)Core.*generic.*`FAIL`.*`BLOCKED`|generic Core.*owns")
    c.require_no_match("TC-MS-005 no duplicate state section", profile, r"(?im)^## (State|Repair rounds|Finding Registry|Stopping Rules)$")

    return c.assertions, c.failures


class ManuscriptProfileContractTest(unittest.TestCase):
    def test_manuscript_profile_contract(self) -> None:
        assertions, failures = run_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"manuscript-profile contract failed: {failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
