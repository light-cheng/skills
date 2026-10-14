"""Composition tests for the Light collection.

These tests protect the composition graph, not SKILL.md wording:

- every declared composition edge points at a real package that the source
  package actually links or names;
- a Skill only *calls* model-invoked capabilities (AGENTS.md invocation
  direction); a user-invoked target may only be *recommended*;
- the ask-light routing map names only real packages;
- public workflow examples never use a retired package name.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from check_helpers import HISTORICAL_NAMES, package_dir

ROOT = Path(__file__).resolve().parents[1]

# (source, target, relation). "calls": the source may start the target itself,
# so the target must be model-invoked. "recommends": the source only names the
# target as a next step for the user, so any invocation type is allowed.
EDGES = (
    ("clarify", "socratic", "calls"),
    ("project-clarify", "socratic", "calls"),
    ("decision-map", "socratic", "calls"),
    ("decision-map", "light-research", "calls"),
    ("decision-map", "light-prototype", "calls"),
    ("decision-map", "light-to-questionnaire", "recommends"),
    ("decision-map", "project-spec", "recommends"),
    ("project-spec", "project-tickets", "recommends"),
    ("light-implement", "agent-config", "calls"),
    ("light-implement", "light-tdd", "calls"),
    ("light-implement", "review-loop", "calls"),
    ("agent-config", "project-tickets", "recommends"),
    ("review-loop", "generic-review", "calls"),
    ("review-loop", "light-code-review", "calls"),
    ("project-review", "review-loop", "calls"),
    ("project-review", "generic-review", "calls"),
    ("project-review", "light-code-review", "calls"),
    # Optional capabilities: the caller keeps its own behaviour when they are missing.
    ("light-implement", "light-decide", "calls-optional"),
    ("light-implement", "light-redirect", "calls-optional"),
    ("light-implement", "light-html-plan", "calls-optional"),
    ("project-review", "light-redirect", "calls-optional"),
    ("project-review", "light-html-plan", "calls-optional"),
    ("project-spec", "light-html-plan", "calls-optional"),
    ("project-tickets", "light-html-plan", "calls-optional"),
    ("light-redirect", "light-decide", "calls-optional"),
    ("ask-light", "light-decide", "calls-optional"),
    ("agent-config", "light-decide", "calls-optional"),
    ("manuscript-ops", "light-decide", "calls-optional"),
)


def package_text(name: str) -> str:
    """SKILL.md plus its references: where a package declares what it composes."""
    package = package_dir(ROOT, name)
    files = [package / "SKILL.md", *sorted((package / "references").glob("*.md"))]
    return "\n".join(path.read_text(encoding="utf-8") for path in files if path.is_file())


def is_model_invoked(name: str) -> bool:
    package = package_dir(ROOT, name)
    metadata = package / "agents" / "openai.yaml"
    if metadata.is_file():
        match = re.search(r"allow_implicit_invocation:\s*(true|false)", metadata.read_text(encoding="utf-8"))
        if match:
            return match.group(1) == "true"
    skill = (package / "SKILL.md").read_text(encoding="utf-8")
    return re.search(r"(?m)^disable-model-invocation:\s*true\s*$", skill) is None


class CompositionGraphTests(unittest.TestCase):
    def test_every_edge_targets_a_real_package_named_by_its_source(self) -> None:
        for source, target, _ in EDGES:
            with self.subTest(edge=f"{source}->{target}"):
                package_dir(ROOT, target)  # raises if the target package is missing
                self.assertRegex(
                    package_text(source),
                    rf"(?<![\w-]){re.escape(target)}(?![\w-])",
                    f"{source} declares no composition with {target}",
                )

    def test_a_skill_only_calls_model_invoked_capabilities(self) -> None:
        for source, target, relation in EDGES:
            if relation.startswith("calls"):
                with self.subTest(edge=f"{source}->{target}"):
                    self.assertTrue(
                        is_model_invoked(target),
                        f"{source} calls {target}, but {target} is user-invoked; recommend it instead",
                    )

    def test_optional_calls_match_declarations_and_each_has_a_fallback(self) -> None:
        declared = set()
        for skill_file in (ROOT / "skills").glob("*/*/SKILL.md"):
            section = re.search(r"(?ms)^## Optional capabilities\n(.*?)(?=^## |\Z)", skill_file.read_text(encoding="utf-8"))
            if not section:
                continue
            for item in re.split(r"(?m)^- ", section.group(1))[1:]:
                targets = re.findall(r"call\s+`([\w-]+)`", item)
                with self.subTest(skill=skill_file.parent.name, item=item[:60]):
                    self.assertTrue(targets, "an optional capability names no call target")
                    # trigger → call, then fallback → behaviour: two arrows
                    self.assertGreaterEqual(item.count("→"), 2, "an optional capability gives no fallback")
                declared |= {(skill_file.parent.name, target) for target in targets}
        edges = {(source, target) for source, target, relation in EDGES if relation == "calls-optional"}
        self.assertEqual(declared, edges)

    def test_script_decision_source_copies_stay_identical(self) -> None:
        # ask-light and agent-config each ship the light-decide script path; the copies must not drift.
        copies = [package_dir(ROOT, name) / "scripts" / "decision_source.py" for name in ("ask-light", "agent-config")]
        self.assertEqual(copies[0].read_bytes(), copies[1].read_bytes())

    def test_invocation_check_rejects_a_user_invoked_target(self) -> None:
        # Negative control: the check above must be able to fail.
        self.assertFalse(is_model_invoked("project-tickets"))
        self.assertTrue(is_model_invoked("socratic"))

    def test_routing_map_names_only_real_packages(self) -> None:
        data = json.loads((package_dir(ROOT, "ask-light") / "references" / "light-skill-map.json").read_text(encoding="utf-8"))
        actual = {path.parent.name for path in (ROOT / "skills").glob("*/*/SKILL.md")}
        referenced = {entry["name"] for entry in data["skills"]}
        referenced |= set(data["taskKindRoutes"].values())
        referenced |= set(data["skillFamilies"])
        for recipe in data["workflows"]:
            referenced |= {step["skill"] for step in recipe["steps"]}
        self.assertEqual(referenced - actual, set())

    def test_public_workflow_examples_use_current_names(self) -> None:
        docs = [ROOT / "README.md", ROOT / "README.zh-CN.md", *sorted((ROOT / "docs" / "workflows").glob("*.md")),
                *sorted((ROOT / "docs" / "zh-CN" / "workflows").glob("*.md"))]
        for doc in docs:
            text = doc.read_text(encoding="utf-8")
            for block in re.findall(r"```text\n(.*?)```", text, re.S):
                for line in block.splitlines():
                    command = line.split("#", 1)[0]
                    for token in re.findall(r"(?<![\w-])\$?([a-z][a-z0-9-]*)(?![\w-])", command):
                        with self.subTest(doc=doc.name, token=token):
                            self.assertNotIn(token, HISTORICAL_NAMES, f"{doc.name}: retired name `{token}` in `{line.strip()}`")


if __name__ == "__main__":
    unittest.main(verbosity=2)
