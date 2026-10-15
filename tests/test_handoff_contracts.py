"""Handoff contracts between Light packages.

A handoff is an artifact one package writes and another reads. These tests
check that both sides of each handoff name the same artifact, so a rename on
one side cannot silently break the other. They check composition, not
wording: each artifact is a path or a record field, not a sentence.
"""

from __future__ import annotations

import importlib.util
import re
import unittest
from pathlib import Path

from check_helpers import package_dir

ROOT = Path(__file__).resolve().parents[1]
TRACKER = ROOT / "docs" / "agents" / "issue-tracker.md"

# (artifact, writers, readers). The artifact is a literal token that every
# writer and reader must name in its SKILL.md or references.
HANDOFFS = (
    (".scratch/<feature>/clarify-handoff.md", ("project-clarify", "clarify"), ("project-spec",)),
    ("Project clarification handoff", ("project-clarify",), ("project-spec",)),
    (".scratch/<feature>/spec.md", ("project-spec",), ("project-tickets",)),
    ("Approval:", ("project-spec",), ("project-review",)),
    ("Tickets approved", ("project-tickets",), ("project-review",)),
    ("US-", ("project-spec",), ("project-tickets", "project-review")),
    ("Implementation report", ("light-implement",), ("project-review", "light-html-plan")),
    ("Plan gap:", ("light-implement",), ("project-review", "light-html-plan")),
    ("Cause:", ("project-review",), ("light-html-plan",)),
    (".scratch/<feature>/changes/", ("light-redirect",), ("project-spec", "project-tickets")),
    ("changes/", ("light-redirect",), ("light-html-plan",)),
    (".scratch/<feature>/decisions.md", ("light-decide",), ()),
    ("decisions.md", ("light-decide",), ("light-html-plan",)),
    (".scratch/<feature>/plan.html", ("light-html-plan",), ("project-spec", "project-tickets", "light-implement", "project-review")),
)

# Artifacts the local tracker convention must list, so a project that never
# read the writing package still knows where to look.
TRACKER_ARTIFACTS = ("clarify-handoff.md", "spec.md", "Approval:", "Tickets approved", "plan.html", "plan-history/")

TRIAGE = ROOT / "docs" / "agents" / "triage-labels.md"
TICKET_STATUSES = ("ready-for-agent", "open", "claimed", "resolved")
PROPOSAL = "references/PROPOSAL.md"  # inside light-redirect
# A write instruction: a write verb, then a Status field and its value in the same sentence.
WRITE_VERB = re.compile(r"(?i)\b(?:set|sets|mark|marks|update|updates|change|changes|rewrite|rewrites)\b")
STATUS_VALUE = re.compile(r"(?i)\**Status:?\**`?\s*(?:to\s+)?`?(?:\*\*)?\s*([a-z][\w-]*)`?")


def package_text(name: str) -> str:
    package = package_dir(ROOT, name)
    files = [package / "SKILL.md", *sorted((package / "references").rglob("*.md"))]
    return "\n".join(path.read_text(encoding="utf-8") for path in files if path.is_file())


def names(text: str, artifact: str) -> bool:
    return re.search(rf"(?<![\w-]){re.escape(artifact)}", text) is not None


def all_packages() -> set[str]:
    return {path.parent.name for path in (ROOT / "skills").glob("*/*/SKILL.md")}


def status_setters(text: str, own: str, known: set[str]) -> set[tuple[str, str]]:
    """(actor, status) for each instruction in ``text`` that writes a Status value.

    A sentence counts when a write verb ("set", "mark", "update", ...) comes
    before a `Status` field and its value. The actor is the package named in
    backticks as the sentence's subject (before the verb, not after "Unlike");
    otherwise the package whose text this is.
    """
    found = set()
    for unit in re.split(r"\n\s*\n|\n(?=\|)|\n(?=\s*- )|\n(?=\d+\. )", text):
        flat = " ".join(unit.split())
        for sentence in re.split(r"(?<=[.;|])\s+", flat):
            verb = WRITE_VERB.search(sentence)
            if not verb:
                continue
            value = STATUS_VALUE.search(sentence, verb.end())
            if not value:
                continue
            subject = sentence[: verb.start()]
            named = [m.group(1) for m in re.finditer(r"`([\w-]+)`", subject)
                     if m.group(1) in known and not re.search(r"(?i)\bunlike\s*$", subject[: m.start()])]
            found.add((named[-1] if named else own, value.group(1).lower()))
    return found


def table_rows(text: str, heading: str) -> dict[str, list[str]]:
    """First-column value → cells, for the Markdown table under ``heading``."""
    section = re.search(rf"(?ms)^#+ {re.escape(heading)}\n(.*?)(?=^#|\Z)", text)
    rows = {}
    for line in section.group(1).splitlines() if section else ():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) > 1 and cells[0].startswith("`"):
            rows[cells[0].strip("`")] = cells[1:]
    return rows


def owners(cell: str, known: set[str]) -> set[str]:
    return {name for name in re.findall(r"`([\w-]+)`", cell) if name in known}


class HandoffContractTests(unittest.TestCase):
    def test_every_writer_and_reader_names_the_same_artifact(self) -> None:
        for artifact, writers, readers in HANDOFFS:
            for side, packages in (("writer", writers), ("reader", readers)):
                for name in packages:
                    with self.subTest(artifact=artifact, side=side, package=name):
                        self.assertTrue(names(package_text(name), artifact), f"{name} ({side}) never names {artifact}")

    def test_tracker_convention_lists_each_shared_artifact(self) -> None:
        tracker = TRACKER.read_text(encoding="utf-8")
        for artifact in TRACKER_ARTIFACTS:
            with self.subTest(artifact=artifact):
                self.assertIn(artifact, tracker)

    def test_only_the_listed_owner_sets_each_ticket_status(self) -> None:
        # docs/agents/triage-labels.md is the ownership record: claim belongs to
        # light-implement, resolve to project-review (decision-map owns its own questions).
        known = all_packages()
        table = table_rows(TRIAGE.read_text(encoding="utf-8"), "Ticket status")
        self.assertEqual(set(table), set(TICKET_STATUSES))
        allowed = {status: owners(cells[0], known) for status, cells in table.items()}
        self.assertEqual(allowed["claimed"], {"light-implement", "decision-map"})
        self.assertEqual(allowed["resolved"], {"project-review", "decision-map"})
        seen = set()
        for name in sorted(known):
            for actor, status in status_setters(package_text(name), name, known):
                if status in TICKET_STATUSES:
                    if actor == name:  # an owner must give the step in its own Skill
                        seen.add((actor, status))
                    with self.subTest(package=name, actor=actor, status=status):
                        self.assertIn(actor, allowed[status], f"{name} has {actor} set ticket status {status}")
        for status in ("claimed", "resolved"):
            for owner in allowed[status]:
                with self.subTest(owner=owner, status=status):
                    self.assertIn((owner, status), seen, f"{owner} owns {status} but never sets it")

    def test_only_the_user_approves_a_change_proposal(self) -> None:
        known = all_packages()
        proposal = (package_dir(ROOT, "light-redirect") / PROPOSAL).read_text(encoding="utf-8")
        table = table_rows(proposal, "Status")
        for status in ("approved", "rejected"):
            with self.subTest(status=status):
                self.assertEqual(owners(table[status][0], known), {"light-redirect"})
        self.assertTrue({"project-spec", "project-tickets"} <= owners(table["applied"][0], known))
        for name in sorted(known):
            for actor, status in status_setters(package_text(name), name, known):
                if status in ("approved", "rejected"):
                    with self.subTest(package=name, status=status):
                        self.assertEqual(actor, "light-redirect", f"{name} lets {actor} set a proposal {status}")
        for applier in ("project-spec", "project-tickets"):
            with self.subTest(applier=applier):
                # an applier reads the approved status and writes the applied one
                text = package_text(applier)
                self.assertTrue(names(text, "`approved`"))
                self.assertIn((applier, "applied"), status_setters(text, applier, known))

    def test_ticket_status_vocabulary_is_shared(self) -> None:
        # project-init writes the tracker block a new project reads; light-implement
        # writes the ticket header. Both must use the statuses triage-labels.md lists.
        spec = importlib.util.spec_from_file_location(
            "light_bootstrap", package_dir(ROOT, "project-init") / "scripts" / "bootstrap.py")
        bootstrap = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bootstrap)
        block = bootstrap.render_tracker({"issueTracker": {"kind": "local-markdown", "path": ".scratch/<effort>/issues"}})
        line = re.search(r"(?m)^- Statuses:\s*(.+)$", block).group(1)
        self.assertEqual({s.strip() for s in line.split("|")}, set(TICKET_STATUSES))
        header = re.search(r"(?m)^\*\*Status:\*\*\s*(.+)$",
                           (package_dir(ROOT, "light-implement") / "references" / "WORKFLOW.md").read_text(encoding="utf-8"))
        self.assertLessEqual({s.strip() for s in header.group(1).split("|")}, set(TICKET_STATUSES))

    def test_status_parser_catches_reworded_drift(self) -> None:
        # The ownership tests are only as good as this parser: each drift below,
        # written into light-implement, must be read as light-implement setting resolved.
        known = {"light-implement", "project-review"}
        drift = ("light-implement", "resolved")
        for sentence in (
            "Then set `Status: resolved`.",
            "Set `**Status:**` to `resolved` when done.",
            "Mark the ticket `Status: resolved`.",
            "Update `Status: resolved` after tests pass.",
            "Set Status: resolved.",
            "Unlike `project-review`, this Skill sets `Status: resolved`.",
        ):
            with self.subTest(sentence=sentence):
                self.assertIn(drift, status_setters(sentence, "light-implement", known))
        # A sentence naming the real owner as subject is attributed to it, and reading is not writing.
        self.assertEqual(status_setters("- After a PASS, `project-review` sets `**Status:** resolved`.", "x", known),
                         {("project-review", "resolved")})
        self.assertEqual(status_setters("A ticket is unblocked when every file is `Status: resolved`.", "x", known), set())

    def test_an_owner_that_drops_its_step_fails(self) -> None:
        known = all_packages()
        review = package_text("project-review")
        self.assertIn(("project-review", "resolved"), status_setters(review, "project-review", known))
        dropped = re.sub(r"(?i)\bsets?\b", "keeps", review)
        self.assertNotIn(("project-review", "resolved"), status_setters(dropped, "project-review", known))

    def test_the_check_fails_when_a_side_drops_the_artifact(self) -> None:
        # Negative control: a package that never mentions the artifact must fail.
        self.assertFalse(names(package_text("recap"), ".scratch/<feature>/clarify-handoff.md"))
        self.assertFalse(names("see clarify-handoff.md.bak", ".scratch/<feature>/clarify-handoff.md"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
