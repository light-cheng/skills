"""Assert source identity and lineage at the Source Register validation seam."""

from __future__ import annotations

import csv
import hashlib
import json
import runpy
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "skills/writing/manuscript-ops"
sys.path.insert(0, str(PACKAGE / "scripts"))
VALIDATOR = runpy.run_path(str(PACKAGE / "scripts/validate_state.py"))
REGISTRY = json.loads((PACKAGE / "assets/format-registry.json").read_text())
COLUMNS = (PACKAGE / "assets/templates/source-register.tsv").read_text().strip().split("\t")


def source_row(root: Path, source_id: str, adapter: str, filename: str, contents: bytes) -> dict:
    (root / filename).write_bytes(contents)
    return {
        "source_id": source_id, "class": "authoritative", "adapter_id": adapter,
        "path_or_url": filename, "publisher_or_owner": "fixture owner",
        "retrieved_at": "2026-10-09T00:00:00Z",
        "sha256": hashlib.sha256(contents).hexdigest(), "privacy_class": "internal",
        "permitted_use": "factual,context", "exclusions": "style,incoming",
        "metadata_json": "{}", "derived_artifacts_json": "[]",
    }


def validate_rows(root: Path, rows: list[dict]) -> tuple[dict, object]:
    path = root / "sources.tsv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    report = VALIDATOR["Report"](root)
    result = VALIDATOR["validate_source_register"]("sources.tsv", REGISTRY, report)
    return result, report


class ManuscriptSourceTests(unittest.TestCase):
    def test_registered_document_formats_are_valid_hash_bound_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = [
                source_row(root, "S1", "markdown", "memo.md", b"# Supplied memo\n"),
                source_row(root, "S2", "pdf", "manual.pdf", b"%PDF-1.4\n%%EOF\n"),
                source_row(root, "S3", "txt", "notes.txt", b"confirmed meaning\n"),
            ]
            result, report = validate_rows(root, rows)
            self.assertEqual(report.errors, [])
            self.assertEqual(set(result["sources"]), {"S1", "S2", "S3"})
            self.assertEqual(result["sources"]["S2"]["adapter_id"], "pdf")

    def test_document_identity_cannot_be_relabelled_to_bypass_source_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            row = source_row(root, "S1", "pdf", "memo.md", b"# not a PDF\n")
            _, report = validate_rows(root, [row])
            self.assertIn("SOURCE_FORMAT", {item["code"] for item in report.errors})

    def test_legacy_doc_keeps_its_identity_and_conversion_lineage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = source_row(root, "S1", "legacy-doc", "original.doc", bytes.fromhex("d0cf11e0a1b11ae1") + b"fixture")
            text = source_row(root, "S2", "txt", "converted.txt", b"faithful extracted text")
            original["derived_artifacts_json"] = json.dumps([{
                "kind": "extracted_text", "path": "converted.txt", "sha256": text["sha256"],
                "parent_source_ids": ["S1"], "created_at": "2026-10-09T00:00:00Z",
            }])
            result, report = validate_rows(root, [original, text])
            self.assertEqual(report.errors, [])
            self.assertEqual(result["sources"]["S1"]["adapter_id"], "legacy-doc")

    def test_json_extraction_requires_a_registered_hash_bound_parent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parent = source_row(root, "S1", "pdf", "manual.pdf", b"%PDF-1.4\n%%EOF\n")
            child = source_row(root, "S2", "json-text-extract", "pages.json", b'{"pages": ["source text"]}')
            child["class"] = "reference-only"
            parent["derived_artifacts_json"] = json.dumps([{
                "kind": "page_text_extract", "path": "pages.json", "sha256": child["sha256"],
                "parent_source_ids": ["S1"], "created_at": "2026-10-09T00:00:00Z",
            }])
            _, report = validate_rows(root, [parent, child])
            self.assertEqual(report.errors, [])
            _, orphan_report = validate_rows(root, [child])
            self.assertIn("SOURCE_LINEAGE", {e["code"] for e in orphan_report.errors})

    def test_renamed_ole_file_is_not_a_docx_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            row = source_row(root, "S1", "docx", "renamed.docx", bytes.fromhex("d0cf11e0a1b11ae1") + b"original")
            _, report = validate_rows(root, [row])
            self.assertIn("SOURCE_FORMAT", {e["code"] for e in report.errors})

    def test_malformed_extraction_parent_is_reported_without_crashing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            row = source_row(root, "S1", "pdf", "manual.pdf", b"%PDF-1.4\n%%EOF\n")
            row["derived_artifacts_json"] = json.dumps([{
                "kind": "page_text_extract", "path": "pages.json", "sha256": "a" * 64,
                "parent_source_ids": None, "created_at": "2026-10-09T00:00:00Z",
            }])
            _, report = validate_rows(root, [row])
            self.assertIn("SOURCE_LINEAGE", {e["code"] for e in report.errors})

    def test_registered_sources_cannot_weaken_the_canonical_format_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            altered = json.loads(json.dumps(REGISTRY))
            next(a for a in altered["adapters"] if a["id"] == "pdf")["blocking_qa_gaps"] = False
            report = VALIDATOR["Report"](Path(directory))
            VALIDATOR["validate_format_registry"](altered, {"formats": ["pdf"]}, report)
            self.assertIn("FORMAT_BASELINE", {item["code"] for item in report.errors})

    def test_derivatives_cannot_promote_parent_authority_or_permissions(self):
        for adapter, filename, contents, kind in (
            ("txt", "extract.txt", b"source text", "extracted_text"),
            ("markdown", "extract.md", b"# source text", "converted_document"),
            ("json-text-extract", "extract.json", b'{"text":"source text"}', "page_text_extract"),
        ):
            with self.subTest(adapter=adapter), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                parent = source_row(root, "P", "pdf", "manual.pdf", b"%PDF-1.4\n%%EOF\n")
                parent.update({"class": "reference-only", "permitted_use": "context",
                               "exclusions": "factual,style,incoming"})
                child = source_row(root, "T", adapter, filename, contents)
                parent["derived_artifacts_json"] = json.dumps([{
                    "kind": kind, "path": "./" + filename, "sha256": child["sha256"],
                    "parent_source_ids": ["P"], "created_at": "2026-10-09T00:00:00Z",
                }])
                _, report = validate_rows(root, [parent, child])
                self.assertTrue({"SOURCE_CLASS", "SOURCE_POLICY"}.issubset({e["code"] for e in report.errors}))
                child.update({"class": "reference-only", "permitted_use": "context",
                              "exclusions": "factual,style,incoming"})
                _, allowed = validate_rows(root, [parent, child])
                self.assertEqual(allowed.errors, [])

    def test_parent_source_id_is_normalized_before_derivative_policy_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parent = source_row(root, " P ", "pdf", "manual.pdf", b"%PDF-1.4\n%%EOF\n")
            parent.update({"class": "reference-only", "permitted_use": "context",
                           "exclusions": "factual,style,incoming"})
            child = source_row(root, "T", "txt", "extract.txt", b"faithful source text")
            parent["derived_artifacts_json"] = json.dumps([{
                "kind": "extracted_text", "path": "extract.txt", "sha256": child["sha256"],
                "parent_source_ids": ["P"], "created_at": "2026-10-09T00:00:00Z",
            }])
            _, report = validate_rows(root, [parent, child])
            self.assertTrue({"SOURCE_CLASS", "SOURCE_POLICY"}.issubset({e["code"] for e in report.errors}))
            child.update({"class": "reference-only", "permitted_use": "context",
                          "exclusions": "factual,style,incoming"})
            _, allowed = validate_rows(root, [parent, child])
            self.assertEqual(allowed.errors, [])


if __name__ == "__main__":
    unittest.main()
