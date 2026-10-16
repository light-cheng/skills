"""Contract checks for the model-invoked agent-config package.

These are deterministic package checks validating the behavioral contracts,
schema specifications, and invariants of agent-config.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
METADATA = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
HOST_SCHEMA = (ROOT / "references" / "host-evidence-schema.md").read_text(encoding="utf-8")
PLAN_SCHEMA = (ROOT / "references" / "plan-schema.md").read_text(encoding="utf-8")
TASK_ASSESSMENT = (ROOT / "references" / "task-assessment.md").read_text(encoding="utf-8")
ADAPTER_CONTRACT = (ROOT / "references" / "provider-adapter-contract.md").read_text(encoding="utf-8")
COMPANION_CONTRACT = (ROOT / "references" / "companion-contract.md").read_text(encoding="utf-8")
PROFILE_SCHEMA = (ROOT / "references" / "profile-schema.md").read_text(encoding="utf-8")
SETUP = (ROOT / "references" / "setup.md").read_text(encoding="utf-8")
ROUTING = (ROOT / "references" / "routing.md").read_text(encoding="utf-8")
HARNESS_SUPPORT = (ROOT / "references" / "harness-support.md").read_text(encoding="utf-8")


class AgentConfigContractTest(unittest.TestCase):
    def test_package_shape_and_supporting_files_exist(self) -> None:
        self.assertTrue((ROOT / "SKILL.md").is_file())
        self.assertTrue((ROOT / "agents" / "openai.yaml").is_file())
        self.assertTrue((ROOT / "references" / "host-evidence-schema.md").is_file())
        self.assertTrue((ROOT / "references" / "plan-schema.md").is_file())
        self.assertTrue((ROOT / "references" / "task-assessment.md").is_file())
        self.assertTrue((ROOT / "references" / "provider-adapter-contract.md").is_file())
        self.assertTrue((ROOT / "references" / "setup.md").is_file())
        self.assertTrue((ROOT / "references" / "routing.md").is_file())
        self.assertTrue((ROOT / "references" / "companion-contract.md").is_file())
        self.assertTrue((ROOT / "references" / "profile-schema.md").is_file())
        self.assertTrue((ROOT / "references" / "harness-support.md").is_file())
        self.assertLess(len(SKILL.splitlines()), 100)
        self.assertGreaterEqual(len(SKILL.splitlines()), 40)
        self.assertRegex(SKILL, r"(?m)^name:\s*agent-config\s*$")
        self.assertRegex(SKILL, r"(?m)^description:\s*.+")
        self.assertNotRegex(SKILL, r"(?m)^disable-model-invocation:")
        self.assertRegex(METADATA, r"(?m)^\s*allow_implicit_invocation:\s*true\s*$")

    def test_host_evidence_schema_v2_and_backward_compatibility(self) -> None:
        for marker in (
            "host_id",
            "adapter_id",
            "available_models",
            "supported_effort_values",
            "capabilities",
            "subagents",
            "threads",
            "parallelism",
            "model_selection",
            "available",
            "unavailable",
            "unknown",
            "host-runtime",
            "fallback-default",
            "routing_rank",
        ):
            self.assertIn(marker, HOST_SCHEMA)

    def test_task_assessment_criteria_and_anti_wordcount_invariant(self) -> None:
        for marker in (
            "single-pass",
            "decomposed",
            "routine",
            "moderate",
            "demanding",
            "critical",
            "Anti-wordcount rule",
            "never use word count",
            "Monotonicity invariant",
        ):
            self.assertIn(marker.lower(), TASK_ASSESSMENT.lower())

    def test_adaptive_plan_schema_defines_headers_and_conditional_layouts(self) -> None:
        for marker in (
            "Readiness: READY | NEED_INPUT | NEED_PROJECT_TICKETS | BLOCKED | UNSUPPORTED",
            "Provider mode: tiered-multi-model | fixed-single-model",
            "Task shape: single-pass | decomposed",
            "Execution status: executable | waiting-on-dependencies | blocked-gate",
            "Apply mode: plan-only | adapter-available-awaiting-approval | applied",
            "## Host summary",
            "## Task assessment",
            "## Execution config",
            "## Review strategy",
            "## Limitations / unknowns",
            "Controller Review",
            "Self-check",
            "Independent Review",
        ):
            self.assertIn(marker, PLAN_SCHEMA)

    def test_core_skill_defines_four_execution_modes_and_setup_gate(self) -> None:
        for marker in (
            "Setup Gate",
            "references/setup.md",
            "single-pass",
            "decomposed",
            "Case A (Fixed Single-model + Single-pass)",
            "Case B (Fixed Single-model + Decomposed",
            "Case C (Tiered Multi-model + Single-pass)",
            "Case D (Tiered Multi-model + Decomposed",
            "highest-supported",
            "NEED_PROJECT_TICKETS",
        ):
            self.assertIn(marker, SKILL)

    def test_provider_adapter_contract_boundaries(self) -> None:
        for marker in (
            "Read-only by default",
            "Explicit user approval required",
            "Graceful adapter absence",
            "Non-blocking adapter failure",
            "Apply request contract",
        ):
            self.assertIn(marker, ADAPTER_CONTRACT)

    def test_companion_contract_tools_and_invariants(self) -> None:
        self.assertIn("protocol_version: 1", COMPANION_CONTRACT)
        self.assertIn("profile_version: 1", COMPANION_CONTRACT)
        for tool_name in (
            "get_setup_status",
            "inspect_host",
            "get_profile",
            "save_profile",
            "preview_configuration",
            "apply_configuration",
            "validate_configuration",
            "reset_profile",
        ):
            self.assertIn(f"`{tool_name}`", COMPANION_CONTRACT)

    def test_profile_schema_specifications_and_invariants(self) -> None:
        for marker in (
            "profile_version",
            "host.id",
            "host.adapter",
            "scope.workspace",
            "model_mode",
            "single_model",
            "tiers",
            "routine",
            "standard",
            "high",
            "review",
            "capabilities",
            "subagents",
            "threads",
            "parallelism",
            "concurrency",
            "highest-supported",
        ):
            self.assertIn(marker.lower(), PROFILE_SCHEMA.lower())

    def test_setup_gate_and_routing_specifications(self) -> None:
        for marker in (
            "agent-config setup",
            "setup gate",
            "inspect_host",
            "Single model",
            "Multiple selectable models",
            "Tier binding",
        ):
            self.assertIn(marker.lower(), SETUP.lower())

        for marker in (
            "Case A: Single-model + Single-pass",
            "Case B: Single-model + Decomposed (P0)",
            "Case C: Multi-model + Single-pass",
            "Case D: Multi-model + Decomposed (P0)",
            "need_project_tickets",
        ):
            self.assertIn(marker.lower(), ROUTING.lower())

    def test_harness_support_and_companion_matrix(self) -> None:
        for harness in (
            "Codex CLI",
            "Claude Code",
            "Antigravity",
            "DeepSeek Harness (DSH)",
            "OpenCode",
            "ZCode",
            "Cursor",
            "Grok Build",
            "Hermes",
        ):
            self.assertIn(harness, HARNESS_SUPPORT)

        for marker in (
            "Pi",
            "Generic/manual",
            "Frozen Mutation Preview",
            "Registration Detection",
            "preview_configuration",
            "User Approval Required",
            "apply_configuration",
            "validate_configuration",
            "Generic Fallback Adapter",
            "Plan-Only Mode",
        ):
            self.assertIn(marker.lower(), HARNESS_SUPPORT.lower())

    def test_live_package_is_self_contained_and_provider_neutral(self) -> None:
        package_text = "\n".join((
            SKILL,
            METADATA,
            HOST_SCHEMA,
            PLAN_SCHEMA,
            TASK_ASSESSMENT,
            ADAPTER_CONTRACT,
            COMPANION_CONTRACT,
            PROFILE_SCHEMA,
            SETUP,
            ROUTING,
            HARNESS_SUPPORT,
        ))
        self.assertNotRegex(
            package_text,
            r"(?i)sol-advisor|\bsol\b|\bterra\b|\bluna\b|mattpocock|github\.com",
        )
        self.assertNotRegex(package_text, r"https?://|/Users/|\.codex")


if __name__ == "__main__":
    unittest.main(verbosity=2)
