"""Port of skills/review/review-loop/tests/specification-profile-contract-tests.ps1."""

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
    profile_path = root / "references" / "profiles" / "specification.md"
    generic_path = root / "references" / "profiles" / "generic.md"
    finding_path = root / "references" / "finding-schema.md"
    evidence_path = root / "references" / "evidence-protocol.md"
    stopping_path = root / "references" / "stopping-rules.md"
    roles_path = root / "references" / "subagent-protocol.md"

    for label, path in (
        ("Skill", skill_path),
        ("Agent metadata", metadata_path),
        ("Specification Profile", profile_path),
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

    c.require_match("TC-SP-001 profile link", skill, r"(?im)\[specification\.md\]\(references/profiles/specification\.md\)")
    c.require_match("TC-SP-001 profile heading", profile, r"(?im)^# Specification Profile$")
    c.require_match("TC-SP-001 implicit invocation", metadata, r"(?im)^\s*allow_implicit_invocation:\s*true\s*$")
    c.require_match("TC-SP-001 generic preserved", generic, r"(?im)^# Generic Profile$")

    c.require_match("TC-SP-002 review axes", profile, r"(?im)^## Review axes$")
    for axis in ("Authority and baseline", "Scope and target", "Criteria and acceptance", "Terminology and ambiguity", "Contradiction and decision", "Testability and evidence", "Version, change, and hand-off"):
        c.require_match(f"TC-SP-002 axis {axis}", profile, rf"(?i)\*\*{axis}")
    c.require_match("TC-SP-002 severity guidance", profile, r"(?im)^## Severity guidance$")
    c.require_match("TC-SP-002 acceptance conditions", profile, r"(?im)^## Acceptance conditions$")
    c.require_match("TC-SP-002 failure cases", profile, r"(?im)^## Artifact-specific failure cases$")
    c.require_match("TC-SP-002 severity values", profile, r"(?is)\*\*Critical\*\*.*\*\*High\*\*.*\*\*Medium\*\*.*\*\*Low\*\*")

    c.require_no_match("TC-SP-003 unsupported primary labels absent", profile, r"(?im)(?:Evidence label|Label):\s*(?:render|visual)\b")

    c.require_match("TC-SP-004 Core verdict ownership", profile, r"(?is)generic Core.*final.*verdict|Core.*owns.*final.*`PASS`.*`FAIL`.*`BLOCKED`")
    c.require_match("TC-SP-004 dispositions", profile, r"(?is)`confirmed`.*`rejected`.*`duplicate`.*`out-of-scope`")

    c.require_no_match("TC-SP-005 no duplicate state section", profile, r"(?im)^## (State|Repair rounds|Finding Registry|Stopping Rules)$")
    c.require_match("TC-SP-005 canonical finding schema unchanged", finding, r"(?im)^# Finding Registry$")
    c.require_match("TC-SP-005 canonical stop outcomes unchanged", stopping, r"(?i)`PASS`.*`FAIL`.*`BLOCKED`")

    return c.assertions, c.failures


class SpecificationProfileContractTest(unittest.TestCase):
    def test_specification_profile_contract(self) -> None:
        assertions, failures = run_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"specification-profile contract failed: {failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
