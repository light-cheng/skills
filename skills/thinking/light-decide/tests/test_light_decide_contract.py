"""Contract checks for light-decide: invocation, links and the shared formats."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
METADATA = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
FORMATS = (ROOT / "references" / "formats.md").read_text(encoding="utf-8")
SELECTION = (ROOT / "references" / "selection.md").read_text(encoding="utf-8")


def fenced(text: str, language: str) -> list[str]:
    return re.findall(rf"```{language}\n(.*?)```", text, flags=re.DOTALL)


def declared_reasons(text: str = FORMATS) -> set[str]:
    """Fallback reasons as declared in the formats table, not a copy kept here."""
    return set(re.findall(r"(?m)^\| `([a-z-]+)` \|", text))


def declared_destinations(text: str = SELECTION) -> list[str]:
    line = re.search(r"`Decision data: ([a-z| -]+)`", text).group(1)
    return [value.strip() for value in line.split("|") if value.strip() != "off"]


def result_fields(text: str = FORMATS) -> dict[str, str]:
    block = fenced(text, "yaml")[0]
    return dict(line.split(": ", 1) for line in block.strip().splitlines())


def probabilities(fields: dict[str, str]) -> dict[str, float]:
    pairs = re.findall(r"([\w-]+): ([0-9.]+)", fields["probabilities"])
    return {key: float(value) for key, value in pairs}


def confidence_errors(fields: dict[str, str]) -> list[str]:
    """The one computable rule: confidence is the probability of the answer."""
    if fields["kind"] == "score":
        return []  # Score confidence sums the levels in the caller's bin; see formats.md "Score".
    probs = probabilities(fields)
    if not probs:
        return [] if fields["confidence"] == "null" else ["confidence without probabilities"]
    errors = []
    expected = probs[fields["answer"]]
    if abs(float(fields["confidence"]) - expected) > 1e-9:
        errors.append(f"confidence {fields['confidence']} != p(answer) {expected}")
    if fields["kind"] == "yes_no" and abs(expected - max(probs["yes"], 1 - probs["yes"])) > 1e-9:
        errors.append("yes_no answer is not the more likely side")
    return errors


def vocabulary_errors(fields: dict[str, str]) -> list[str]:
    errors = []
    if fields["fallback_reason"] not in declared_reasons():
        errors.append(f"undeclared reason {fields['fallback_reason']}")
    if fields["data"] not in declared_destinations() + ["in-session"]:
        errors.append(f"undeclared destination {fields['data']}")
    if fields["method"] not in {"typed-decision", "self-judgment"}:
        errors.append(f"undeclared method {fields['method']}")
    if fields["kind"] not in {"choice", "score", "yes_no"}:
        errors.append(f"undeclared kind {fields['kind']}")
    return errors


def log_rows(text: str = FORMATS) -> list[list[str]]:
    block = fenced(text, "markdown")[0]
    rows = [line for line in block.strip().splitlines() if line.startswith("|")]
    return [[cell.strip() for cell in re.split(r"(?<!\\)\|", row)[1:-1]] for row in rows]


def mismatched_columns(text: str) -> list[str]:
    header, _, row = log_rows(text)
    entry, fields = dict(zip(header, row)), result_fields(text)
    fields["reason"] = fields["fallback_reason"]
    return [column for column in header if column != "time" and entry.get(column) != fields.get(column)]


class LightDecideContractTest(unittest.TestCase):
    def test_model_invoked_on_both_metadata_surfaces(self) -> None:
        front = re.match(r"\A---\n(.*?)\n---\n", SKILL, flags=re.DOTALL).group(1)
        self.assertRegex(front, r"(?m)^name: light-decide$")
        self.assertNotIn("disable-model-invocation", front)
        self.assertRegex(METADATA, r"(?m)^\s*allow_implicit_invocation:\s*true\s*$")

    def test_every_relative_link_resolves(self) -> None:
        for source, text in (("SKILL.md", SKILL), ("references/selection.md", SELECTION), ("references/formats.md", FORMATS)):
            for target in re.findall(r"\]\(([^)#:]+)\)", text):
                with self.subTest(source=source, target=target):
                    self.assertTrue(((ROOT / source).parent / target).is_file())

    def test_declared_vocabularies_are_complete(self) -> None:
        self.assertEqual(
            declared_reasons(),
            {"none", "off", "unavailable", "timeout", "malformed", "low-confidence", "uncalibrated"},
        )
        self.assertEqual(declared_destinations(), ["on-device", "private-network", "third-party"])

    def test_result_example_follows_the_declared_rules(self) -> None:
        fields = result_fields()
        self.assertEqual(vocabulary_errors(fields), [])
        self.assertEqual(confidence_errors(fields), [])

    def test_log_row_mirrors_the_result_fields(self) -> None:
        header, _, row = log_rows()
        self.assertEqual(len(header), len(row))
        self.assertEqual(mismatched_columns(FORMATS), [])
        self.assertRegex(dict(zip(header, row))["time"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")

    def test_policy_example_uses_declared_names_and_calibration(self) -> None:
        policy = json.loads(fenced(FORMATS, "json")[0])
        self.assertEqual(policy["version"], 1)
        self.assertIn(result_fields()["backend"], policy["backends"])
        for key, backend in policy["backends"].items():
            self.assertIn(key, backend["names"])
            self.assertIn(backend["data"], declared_destinations())
            for question_id, entry in backend["questions"].items():
                self.assertRegex(question_id, r"^[a-z0-9-]+/[a-z0-9-]+$")
                self.assertGreater(entry["min_confidence"], 0)
                self.assertTrue(entry["calibration"])

    def test_checks_catch_drift(self) -> None:
        # A log row that disagrees with the result.
        drifted = FORMATS.replace("| uncalibrated | no |", "| uncalibrated | yes |", 1)
        self.assertEqual(mismatched_columns(drifted), ["final"])
        # A confidence that is not the probability of the answer.
        wrong = dict(result_fields(), confidence="0.66")
        self.assertTrue(confidence_errors(wrong))
        # A reason the table does not declare.
        self.assertTrue(vocabulary_errors(dict(result_fields(), fallback_reason="skipped")))
        # A reason dropped from the table is no longer declared.
        self.assertNotIn("timeout", declared_reasons(FORMATS.replace("| `timeout` |", "| timeout |")))


if __name__ == "__main__":
    unittest.main()
