"""Contract, invocation, and boundary assertions for generic-review."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
METADATA = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
SCHEMA = (ROOT / "references" / "output-schema.md").read_text(encoding="utf-8")


def frontmatter(text: str) -> str:
    match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.DOTALL)
    return match.group(1) if match else ""


def model_invoked(skill: str, metadata: str) -> bool:
    return (
        bool(re.search(r"(?m)^name:\s*generic-review\s*$", frontmatter(skill)))
        and "disable-model-invocation" not in frontmatter(skill)
        and bool(re.search(r"(?m)^\s*allow_implicit_invocation:\s*true\s*$", metadata))
    )


class GenericReviewContractTest(unittest.TestCase):
    def test_package_shape_and_model_invocation(self) -> None:
        self.assertTrue((ROOT / "SKILL.md").is_file())
        self.assertTrue((ROOT / "agents" / "openai.yaml").is_file())
        self.assertTrue((ROOT / "references" / "output-schema.md").is_file())
        self.assertTrue(model_invoked(SKILL, METADATA))
        self.assertIn("model-invoked", SKILL)

    def test_required_input_and_generic_scope_are_explicit(self) -> None:
        for marker in ("Target:", "Requirements:", "Relevant context:", "Previous findings:"):
            self.assertIn(marker, SKILL)

    def test_normalized_schema_requires_the_finding_fields_and_states(self) -> None:
        for marker in ("id:", "severity:", "location:", "problem:", "reason:", "suggestion:", "new", "persists", "fixed", "duplicate"):
            self.assertIn(marker, SCHEMA)
        self.assertIn("Findings: []", SCHEMA)

    def test_invocation_mutation_is_rejected(self) -> None:
        self.assertTrue(model_invoked(SKILL, METADATA))
        disabled = SKILL.replace("name: generic-review\n", "name: generic-review\ndisable-model-invocation: true\n", 1)
        implicit_off = METADATA.replace("allow_implicit_invocation: true", "allow_implicit_invocation: false")
        self.assertFalse(model_invoked(disabled, METADATA))
        self.assertFalse(model_invoked(SKILL, implicit_off))

    def test_external_runtime_and_authority_mutations_are_rejected(self) -> None:
        live = "\n".join((SKILL, METADATA, SCHEMA))
        self.assertNotRegex(live, r"(?i)github\.com|curl |npm install|subprocess|write_text\(")
        self.assertNotRegex(SKILL, r"(?i)issue a project.*verdict")


if __name__ == "__main__":
    unittest.main(verbosity=2)