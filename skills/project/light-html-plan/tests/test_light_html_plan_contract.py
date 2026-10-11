"""Contract checks for light-html-plan: invocation, links, the five parts and the records it reads."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
METADATA = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
CSS = (ROOT / "assets" / "plan.css").read_text(encoding="utf-8")
SKELETON = (ROOT / "assets" / "skeleton.html").read_text(encoding="utf-8")
REFS = {path.name: path.read_text(encoding="utf-8") for path in (ROOT / "references").glob("*.md")}

PARTS = ["这个项目是什么", "做到哪一步", "等你决定的事", "跟当初相比哪里变了", "系统替你做了哪些判断"]


def skill_parts(text: str = SKILL) -> list[str]:
    """Part names, in order, from the numbered list under the five-parts heading."""
    section = text.split("## The page has five parts", 1)[1].split("\n## ", 1)[0]
    return re.findall(r"(?m)^\d\. \*\*(.+?)\*\*", section)


def exhibit_parts(text: str) -> list[str]:
    """Part names, in order, from the first column of the exhibit table."""
    section = text.split("## Build from the skeleton", 1)[1].split("\n## ", 1)[0]
    return [row for row in re.findall(r"(?m)^\| ([^|]+?) \|", section) if row not in ("Part", "---", "Top")]


def undefined_classes(html: str, css: str) -> set[str]:
    used = {name for attr in re.findall(r'class="([^"]+)"', html) for name in attr.split()}
    defined = set(re.findall(r"\.([a-zA-Z][\w-]*)", re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)))
    return used - defined


def record_rows(text: str) -> dict[str, str]:
    """Record path -> part column, from the Light project records table."""
    section = text.split("## Light project records", 1)[1].split("\n## ", 1)[0]
    rows = re.findall(r"(?m)^\| (.+?) \| .+? \| (.+?) \|$", section)
    return {record: part for record, part in rows if record not in ("Record", "---")}


class LightHtmlPlanContractTest(unittest.TestCase):
    def test_model_invoked_on_both_metadata_surfaces(self) -> None:
        front = re.match(r"\A---\n(.*?)\n---\n", SKILL, flags=re.DOTALL).group(1)
        self.assertRegex(front, r"(?m)^name: light-html-plan$")
        self.assertNotIn("disable-model-invocation", front)
        self.assertIn(".scratch/<feature>/plan.html", front)
        self.assertRegex(METADATA, r"(?m)^\s*allow_implicit_invocation:\s*true\s*$")

    def test_every_relative_link_resolves(self) -> None:
        sources = {ROOT / "SKILL.md": SKILL, **{ROOT / "references" / name: text for name, text in REFS.items()}}
        for source, text in sources.items():
            for target in re.findall(r"\]\(([^)#:]+)(?:#[^)]*)?\)", text):
                with self.subTest(source=source.name, target=target):
                    self.assertTrue((source.parent / target).is_file())

    def test_five_parts_in_fixed_order_everywhere(self) -> None:
        self.assertEqual(skill_parts(), PARTS)
        self.assertEqual(exhibit_parts(REFS["design-and-verification.md"]), PARTS)
        writing = REFS["writing.md"]
        positions = [writing.index(f"**{part}.**") for part in PARTS]
        self.assertEqual(positions, sorted(positions))

    def test_reads_what_the_sibling_capabilities_write(self) -> None:
        rows = record_rows(REFS["source-protocol.md"])
        joined = " ".join(rows)
        for path in ("spec.md", "issues/NN-", "changes/NN-", "decisions.md", ".project-review/verdict.md"):
            with self.subTest(path=path):
                self.assertIn(path, joined)
        for record, part in rows.items():
            with self.subTest(record=record):
                self.assertTrue(set(re.findall(r"\d", part)) <= set("12345"))
        for status in ("proposed", "approved", "rejected", "applied"):
            self.assertIn(f"`{status}`", REFS["source-protocol.md"])

    def test_three_completion_states_stay_separate(self) -> None:
        progress = REFS["progress-and-refresh.md"]
        for state in ("写完", "验收", "发布"):
            self.assertRegex(progress, rf"(?m)^\| {state} ")
        self.assertIn("plan-history/", progress)

    def test_skeleton_uses_only_the_shipped_visual_system(self) -> None:
        self.assertEqual(undefined_classes(SKELETON, CSS), set())
        ids = re.findall(r'<section id="([a-z]+)"', SKELETON)
        self.assertEqual(ids, ["what", "progress", "decide", "changed", "judged", "sources"])
        self.assertNotRegex(CSS, r"url\(|@import")
        self.assertIn("prefers-color-scheme", CSS)
        self.assertIn('[data-theme="dark"]', CSS)

    def test_checks_catch_drift(self) -> None:
        self.assertEqual(undefined_classes('<div class="card fancy-glow">', CSS), {"fancy-glow"})
        self.assertNotEqual(skill_parts(SKILL.replace("**做到哪一步**", "**进度**")), PARTS)
        design = REFS["design-and-verification.md"]
        swapped = design.replace("| 等你决定的事 |", "| TMP |").replace("| 跟当初相比哪里变了 |", "| 等你决定的事 |").replace("| TMP |", "| 跟当初相比哪里变了 |")
        self.assertNotEqual(exhibit_parts(swapped), PARTS)
        protocol = REFS["source-protocol.md"]
        self.assertNotIn("decisions.md", " ".join(record_rows(protocol.replace("| `decisions.md`", "| `judgments.md`"))))


if __name__ == "__main__":
    unittest.main()
