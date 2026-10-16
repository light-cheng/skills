"""Contract checks for light-redirect: invocation, links and the proposal format."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
METADATA = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
PROPOSAL = (ROOT / "references" / "PROPOSAL.md").read_text(encoding="utf-8")
EXAMPLES = (ROOT / "references" / "EXAMPLES.md").read_text(encoding="utf-8")


def fenced_markdown(text: str) -> list[str]:
    return re.findall(r"```markdown\n(.*?)```", text, flags=re.DOTALL)


def declared_statuses(text: str = PROPOSAL) -> dict[str, str]:
    """Status -> who sets it, read from the status table."""
    return dict(re.findall(r"(?m)^\| `([a-z]+)` \| ([^|]+) \|", text))


def headings(block: str) -> list[str]:
    return re.findall(r"(?m)^## (.+)$", block)


def proposal_errors(block: str, template: str) -> list[str]:
    errors = []
    if headings(block) != headings(template):
        errors.append(f"headings {headings(block)} != {headings(template)}")
    status = re.search(r"(?m)^\*\*Status:\*\* (\S+)$", block)
    if not status or status.group(1) not in declared_statuses():
        errors.append("missing or undeclared status")
    for field in ("Raised by", "Trigger"):
        if not re.search(rf"(?m)^\*\*{field}:\*\* \S", block):
            errors.append(f"missing {field}")
    for line in ("- SPEC:", "- Tickets:", "- Charter:", "- Accept again:"):
        if line not in block:
            errors.append(f"missing change line {line}")
    if not re.match(r"# \d\d — \S", block):
        errors.append("title is not '# NN — sentence'")
    return errors


class LightRedirectContractTest(unittest.TestCase):
    def test_model_invoked_on_both_metadata_surfaces(self) -> None:
        front = re.match(r"\A---\n(.*?)\n---\n", SKILL, flags=re.DOTALL).group(1)
        self.assertRegex(front, r"(?m)^name: light-redirect$")
        self.assertNotIn("disable-model-invocation", front)
        self.assertRegex(METADATA, r"(?m)^\s*allow_implicit_invocation:\s*true\s*$")

    def test_every_relative_link_resolves(self) -> None:
        for target in re.findall(r"\]\(([^)#:]+)\)", SKILL):
            with self.subTest(target=target):
                self.assertTrue((ROOT / target).is_file())

    def test_applied_is_set_by_the_appliers_not_light_redirect(self) -> None:
        statuses = declared_statuses()
        self.assertEqual(set(statuses), {"proposed", "approved", "rejected", "applied"})
        self.assertIn("user", statuses["approved"])
        self.assertIn("user", statuses["rejected"])
        self.assertNotIn("light-redirect", statuses["applied"])

    def test_template_is_complete(self) -> None:
        template = fenced_markdown(PROPOSAL)[0]
        self.assertEqual(headings(template), ["Why", "Change", "Open decisions", "Not changed", "Comments"])

    def test_example_proposal_follows_the_template(self) -> None:
        template = fenced_markdown(PROPOSAL)[0]
        example = fenced_markdown(EXAMPLES)[0]
        self.assertEqual(proposal_errors(example, template), [])
        path = re.search(r"changes/(\d\d-[a-z0-9-]+)\.md", EXAMPLES)
        self.assertIsNotNone(path)

    def test_checks_catch_drift(self) -> None:
        template = fenced_markdown(PROPOSAL)[0]
        example = fenced_markdown(EXAMPLES)[0]
        self.assertTrue(proposal_errors(example.replace("## Not changed", "## Unchanged"), template))
        self.assertTrue(proposal_errors(example.replace("**Status:** proposed", "**Status:** accepted"), template))
        self.assertTrue(proposal_errors(example.replace("- Accept again: none\n", ""), template))
        self.assertTrue(proposal_errors(example.replace("- Charter: none\n", ""), template))
        self.assertTrue(proposal_errors(example.replace("## Open decisions", "## Questions"), template))
        self.assertNotIn("applied", declared_statuses(PROPOSAL.replace("| `applied` |", "| applied |")))


if __name__ == "__main__":
    unittest.main()
