"""Behavioral tests for harness adapter, candidate selector, and agent_config CLI."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PACKAGE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def test_effort_resolution_bounds_and_anti_literal_max() -> None:
    from agent_config_models import HostCapabilities
    from harness_adapter import resolve_reasoning_effort

    host_standard = HostCapabilities(supported_effort=["low", "medium", "high"], default_effort="medium")
    host_with_max = HostCapabilities(supported_effort=["low", "medium", "high", "xhigh", "max"])
    host_limited = HostCapabilities(supported_effort=["low", "medium"])
    host_none = HostCapabilities(supported_effort=[])

    assert resolve_reasoning_effort(host_standard, "highest-supported") == "high"
    assert resolve_reasoning_effort(host_with_max, "highest-supported") == "max"
    assert resolve_reasoning_effort(host_standard, "lowest-supported") == "low"
    assert resolve_reasoning_effort(host_standard, "minimal") == "low"
    assert resolve_reasoning_effort(host_standard, "standard") == "medium"
    assert resolve_reasoning_effort(host_standard, "default") == "medium"

    # Never emit unverified literal 'max' when absent from host inventory
    assert resolve_reasoning_effort(host_standard, "max") is None
    assert resolve_reasoning_effort(host_none, "highest-supported") is None

    # Explicit user policy beats typed reasoning_need; host bounds typed reasoning_need
    assert resolve_reasoning_effort(host_standard, "minimal", "high") == "low"
    assert resolve_reasoning_effort(host_limited, None, "high") == "medium"


def test_candidate_discovery_and_peer_topologies_with_updated_handoffs() -> None:
    from agent_config_models import AbstractTaskProfile, HostCapabilities, TaskCharacteristics
    from candidate_selector import select_configuration
    from harness_adapter import discover_valid_candidates

    profile_high = AbstractTaskProfile(recommended_tier="high", reasoning_need="high")

    # Setup gate
    res_setup = select_configuration(
        HostCapabilities(), TaskCharacteristics(), profile_high, setup_intent=True
    )
    assert res_setup.readiness == "NEED_INPUT"
    assert res_setup.handoff == "setup"
    assert res_setup.execution_config is None

    # Decomposition gate -> /to-tickets
    res_tickets = select_configuration(
        HostCapabilities(),
        TaskCharacteristics(shape="decomposed", formal_tickets_exist=False),
        profile_high,
    )
    assert res_tickets.readiness == "NEED_PROJECT_TICKETS"
    assert res_tickets.handoff == "/to-tickets"
    assert res_tickets.execution_config is None

    # Case A: Single-model + single-pass -> /implement
    fixed_host = HostCapabilities(
        has_model_selector=False,
        active_model="model-alpha",
        available_models=["model-alpha"],
        supported_effort=["low", "high"],
    )
    assert discover_valid_candidates(fixed_host) == ["model-alpha"]
    res_a = select_configuration(fixed_host, TaskCharacteristics(shape="single-pass"), profile_high)
    assert res_a.readiness == "READY"
    assert res_a.handoff == "/implement"
    assert res_a.execution_config is not None
    assert res_a.execution_config.topology == "Case A"
    assert res_a.execution_config.model == "model-alpha"
    assert res_a.execution_config.resolved_effort == "high"

    # Case B: Single-model + decomposed -> /implement-spec
    res_b = select_configuration(
        fixed_host,
        TaskCharacteristics(shape="decomposed", formal_tickets_exist=True),
        profile_high,
    )
    assert res_b.readiness == "READY"
    assert res_b.handoff == "/implement-spec"
    assert res_b.execution_config is not None
    assert res_b.execution_config.topology == "Case B"

    # Case C: Multi-model + single-pass -> /implement
    multi_host = HostCapabilities(
        has_model_selector=True,
        per_agent_config=True,
        selector_scopes=["current-session", "per-agent"],
        active_model="model-beta",
        available_models=["model-alpha", "model-beta", "model-gamma", "unprofiled-extra"],
        supported_effort=["low", "medium", "high"],
        profile_tiers={"routine": "model-alpha", "standard": "model-beta", "high": "model-gamma"},
        profile_mode="multi",
    )
    candidates = discover_valid_candidates(multi_host)
    assert candidates == ["model-alpha", "model-beta", "model-gamma"]
    assert "unprofiled-extra" not in candidates

    res_c = select_configuration(multi_host, TaskCharacteristics(shape="single-pass"), profile_high)
    assert res_c.readiness == "READY"
    assert res_c.handoff == "/implement"
    assert res_c.execution_config is not None
    assert res_c.execution_config.topology == "Case C"
    assert res_c.execution_config.model == "model-gamma"

    # Case D: Multi-model + decomposed -> /implement-spec
    res_d = select_configuration(
        multi_host,
        TaskCharacteristics(shape="decomposed", formal_tickets_exist=True),
        profile_high,
    )
    assert res_d.readiness == "READY"
    assert res_d.handoff == "/implement-spec"
    assert res_d.execution_config is not None
    assert res_d.execution_config.topology == "Case D"
    assert res_d.execution_config.model == "model-gamma"

    # Preview declined falls back safely to active model when evidenced
    res_declined = select_configuration(
        multi_host, TaskCharacteristics(shape="single-pass"), profile_high, approval="declined"
    )
    assert res_declined.readiness == "READY"
    assert res_declined.fallback_used is True
    assert res_declined.execution_config is not None
    assert res_declined.execution_config.model == "model-beta"


def _fresh_fixture_host(fixture_name: str, workspace: str) -> dict:
    import json
    from datetime import datetime, timezone

    host = json.loads((PACKAGE_ROOT / "tests" / "fixtures" / fixture_name).read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc).isoformat()
    host["observed_at"] = now
    host["workspace"] = workspace
    for model in host.get("available_models", []):
        if model.get("evidence"):
            model["evidence"]["observed_at"] = now
    for capability in host.get("capabilities", {}).values():
        if capability.get("evidence"):
            capability["evidence"]["observed_at"] = now
    return host


def test_agent_config_recommend_validates_evidence_and_integrates_decide_scores() -> None:
    import json

    from agent_config import agent_config_recommend
    from agent_config_models import TaskCharacteristics

    multi_profile = json.loads(
        (PACKAGE_ROOT / "tests" / "fixtures" / "profile-multi-model.json").read_text(encoding="utf-8")
    )
    single_profile = json.loads(
        (PACKAGE_ROOT / "tests" / "fixtures" / "profile-single-model.json").read_text(encoding="utf-8")
    )
    workspace = multi_profile["scope"]["workspace"]
    tiered_host = _fresh_fixture_host("tiered-host.json", workspace)
    fixed_host = _fresh_fixture_host("fixed-host.json", workspace)

    # Empty or missing profile -> NEED_INPUT
    assert agent_config_recommend({}, {}).readiness == "NEED_INPUT"
    assert agent_config_recommend(tiered_host, {}, profile=None).readiness == "NEED_INPUT"

    # Stale timestamp in raw fixture -> NEED_INPUT
    stale_host = json.loads(
        (PACKAGE_ROOT / "tests" / "fixtures" / "tiered-host.json").read_text(encoding="utf-8")
    )
    stale_host["workspace"] = workspace
    assert agent_config_recommend(stale_host, {}, profile=multi_profile).readiness == "NEED_INPUT"

    # Adapter mismatch -> NEED_INPUT
    mismatched_host = json.loads(json.dumps(tiered_host))
    mismatched_host["adapter_id"] = "wrong-adapter"
    assert agent_config_recommend(mismatched_host, {}, profile=multi_profile).readiness == "NEED_INPUT"

    # Fixed single-model host routes cleanly without active_session override
    fixed_res = agent_config_recommend(
        fixed_host,
        {"shape": "single-pass", "difficulty": "routine"},
        profile=single_profile,
        use_typed_decisions=False,
    )
    assert fixed_res.readiness == "READY"
    assert fixed_res.handoff == "/implement"
    assert fixed_res.execution_config is not None
    assert fixed_res.execution_config.model == "model-alpha"
    assert fixed_res.execution_config.topology == "Case A"

    # Caller task object is not mutated by profile effort resolution
    caller_task = TaskCharacteristics(
        title="Minor tweak", difficulty="routine", difficulty_source="explicit-user"
    )
    first = agent_config_recommend(
        tiered_host, caller_task, profile=multi_profile, use_typed_decisions=False
    )
    assert caller_task.reasoning_policy is None
    assert first.execution_config is not None
    assert first.execution_config.model == "model-alpha"
    assert first.execution_config.resolved_effort == "low"

    # Normalized decide score upgrades routine baseline -> high tier -> model-gamma
    decide_payload = {
        "backend": "magpie",
        "model": "google/gemini-decision-1",
        "data_destination": "on-device",
        "fallback_used": False,
        "answers": {
            "agent-config/task-complexity": {
                "level": 2,
                "label": "high",
                "expected_level": 2.0,
                "score": 2.0,
                "probabilities": {"routine": 0.0, "standard": 0.1, "high": 0.8, "critical": 0.1},
                "confidence": 0.8,
                "provider_confidence": 0.88,
            },
            "agent-config/reasoning-need": {
                "level": 2,
                "label": "high",
                "expected_level": 1.85,
                "score": 1.85,
                "probabilities": {"low": 0.02, "medium": 0.11, "high": 0.87},
                "confidence": 0.87,
                "provider_confidence": 0.91,
            },
        },
    }
    upgraded = agent_config_recommend(
        tiered_host,
        {"title": "Consensus protocol", "difficulty": "routine", "difficulty_source": "unknown"},
        profile=multi_profile,
        decide_scores=decide_payload,
        calibration_thresholds={
            "agent-config/task-complexity": 0.6,
            "agent-config/reasoning-need": 0.6,
        },
    )
    assert upgraded.readiness == "READY"
    assert upgraded.fallback_used is False
    assert upgraded.execution_config is not None
    assert upgraded.execution_config.model == "model-gamma"
    assert upgraded.execution_config.resolved_effort == "high"


def test_cli_entrypoints_accept_decide_scores_file_and_json(tmp_path: Path) -> None:
    import json
    import subprocess

    multi_profile = json.loads(
        (PACKAGE_ROOT / "tests" / "fixtures" / "profile-multi-model.json").read_text(encoding="utf-8")
    )
    tiered_host = _fresh_fixture_host("tiered-host.json", multi_profile["scope"]["workspace"])

    scores_file = tmp_path / "decide-scores.json"
    scores_file.write_text(
        json.dumps(
            {
                "agent-config/task-complexity": {
                    "backend": "local-opendecider",
                    "model": "opendecider-small",
                    "data_destination": "on-device",
                    "expected_level": 2.0,
                    "score": 2.0,
                    "probabilities": {"routine": 0.0, "standard": 0.1, "high": 0.8, "critical": 0.1},
                    "confidence": 0.8,
                },
                "agent-config/reasoning-need": {
                    "backend": "local-opendecider",
                    "model": "opendecider-small",
                    "data_destination": "on-device",
                    "expected_level": 1.8,
                    "score": 1.8,
                    "probabilities": {"low": 0.0, "medium": 0.2, "high": 0.8},
                    "confidence": 0.8,
                },
            }
        ),
        encoding="utf-8",
    )
    thresholds_json = json.dumps(
        {
            "agent-config/task-complexity": 0.6,
            "agent-config/reasoning-need": 0.6,
        }
    )

    # 1. abstract_profiler.py CLI
    prof_proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "abstract_profiler.py"),
            "--task-json",
            json.dumps({"difficulty": "routine", "difficulty_source": "unknown"}),
            "--decide-scores-file",
            str(scores_file),
            "--calibration-thresholds-json",
            thresholds_json,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert prof_proc.returncode == 0, prof_proc.stderr
    prof_out = json.loads(prof_proc.stdout)
    assert prof_out["fallback_used"] is False
    assert prof_out["profile"]["recommended_tier"] == "high"

    # 2. agent_config.py CLI
    cfg_proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "agent_config.py"),
            "--host-json",
            json.dumps(tiered_host),
            "--profile-json",
            json.dumps(multi_profile),
            "--task-json",
            json.dumps({"shape": "decomposed", "formal_tickets_exist": True, "difficulty": "routine"}),
            "--decide-scores-file",
            str(scores_file),
            "--calibration-thresholds-json",
            thresholds_json,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert cfg_proc.returncode == 0, cfg_proc.stderr
    cfg_out = json.loads(cfg_proc.stdout)
    assert cfg_out["readiness"] == "READY"
    assert cfg_out["handoff"] == "/implement-spec"
    assert cfg_out["execution_config"]["model"] == "model-gamma"
    assert cfg_out["execution_config"]["topology"] == "Case D"

