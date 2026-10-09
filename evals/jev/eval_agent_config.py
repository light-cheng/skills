"""Evaluation dataset and runner for agent-config task profiling and topology selection.

Covers representative scenarios specified in Section 35 of SPEC:
  - routine documentation edit
  - small bug fix
  - standard feature
  - large refactor
  - security-critical change
  - complex concurrency work
  - cost-sensitive complex work
  - latency-sensitive routine work
  - fixed-model harness
  - multi-model harness
  - no effort selector
  - limited effort selector
  - current model already sufficient
  - user explicitly requests high effort
  - user rejects configuration change
"""

from __future__ import annotations

import copy
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
AGENT_CONFIG_SCRIPTS = PROJECT_ROOT / "skills" / "engineering" / "agent-config" / "scripts"
if str(AGENT_CONFIG_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(AGENT_CONFIG_SCRIPTS))

from agent_config_models import (
    AbstractTaskProfile,
    AgentConfigResult,
    TaskCharacteristics,
)
from agent_config import agent_config_recommend

# Canonical Host evidence and user-confirmed Profiles, in the shape the companion
# returns (see skills/engineering/agent-config/references/host-evidence-schema.md
# and profile-schema.md). Timestamps are stamped at evaluation time because the
# planner rejects Host evidence older than 24 hours.
HOST_ID = "eval-host"
ADAPTER_ID = "eval-adapter"
WORKSPACE = "/eval/workspace"
MULTI_MODELS = ["model-alpha", "model-beta", "model-gamma"]


def _host(
    models: List[str],
    effort: tuple = ("low", "medium", "high"),
    selector: str = "available",
) -> Dict[str, Any]:
    evidence = {"kind": "host-runtime", "locator": "eval fixture"}
    capabilities: Dict[str, Any] = {
        "model_selection": {
            "state": selector,
            "scopes": ["current-session", "new-session", "per-agent"] if selector == "available" else [],
            "evidence": evidence,
        },
        "reasoning": {"state": "available" if effort else "unavailable", "evidence": evidence},
        "subagents": {"state": "available", "evidence": evidence},
    }
    return {
        "host_id": HOST_ID,
        "adapter_id": ADAPTER_ID,
        "workspace": WORKSPACE,
        "available_models": [{"id": m, "state": "available", "evidence": evidence} for m in models],
        "supported_effort_values": list(effort),
        "capabilities": capabilities,
    }


def _profile_base(mode: str) -> Dict[str, Any]:
    return {
        "profile_version": 1,
        "host": {"id": HOST_ID, "adapter": ADAPTER_ID},
        "scope": {"type": "project", "workspace": WORKSPACE},
        "model_mode": mode,
    }


def _multi_profile(effort: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    efforts = {
        "routine": {"value": "low"},
        "standard": {"value": "medium"},
        "high": {"policy": "highest-supported"},
        "review": {"policy": "highest-supported"},
    }
    models = {"routine": "model-alpha", "standard": "model-beta", "high": "model-gamma", "review": "model-gamma"}
    profile = _profile_base("multi")
    profile["tiers"] = {
        tier: {"model": model, "source": "user-confirmed", "effort": dict(effort or efforts[tier])}
        for tier, model in models.items()
    }
    return profile


def _single_profile(model: str, effort: Dict[str, str]) -> Dict[str, Any]:
    profile = _profile_base("single")
    profile["single_model"] = {"model": model, "execution_effort": dict(effort), "review_effort": dict(effort)}
    return profile


MULTI_PROFILE = _multi_profile()


def _active_session(model: str, now: str) -> Dict[str, Any]:
    return {
        "host_id": HOST_ID,
        "adapter_id": ADAPTER_ID,
        "workspace": WORKSPACE,
        "model": model,
        "observed_at": now,
        "evidence": {"kind": "host-runtime", "locator": "eval fixture", "observed_at": now},
    }


@dataclass
class AgentConfigExpected:
    """Isolated ground truth expectations for agent-config evaluation.

    Strictly isolated from runtime task input and never exposed to Jev state.
    """
    expected_tier: str  # "routine", "standard", "high"
    expected_model: str
    expected_topology: str
    expected_readiness: str
    expected_resolved_effort: Optional[str] = None
    expected_min_complexity: float = 0.0
    expected_max_complexity: float = 3.0
    expected_complexity_tier: Optional[str] = None
    expected_min_reasoning: float = 0.0
    expected_max_reasoning: float = 2.0
    expected_reasoning_level: Optional[str] = None


@dataclass
class AgentConfigScenario:
    """Runtime scenario specification separating inputs from ground truth."""
    id: str
    name: str
    host: Dict[str, Any]  # Canonical Host evidence without timestamps
    task: TaskCharacteristics  # Runtime input (never contains ground truth)
    approval: str  # "unknown", "approved", "declined"
    expected: AgentConfigExpected  # Evaluator-only ground truth
    profile: Dict[str, Any] = field(default_factory=dict)  # Canonical user-confirmed Profile
    active_model: Optional[str] = None  # Model the current session is verified to run
    notes: str = ""

    @property
    def expected_tier(self) -> str:
        return self.expected.expected_tier

    @property
    def expected_model(self) -> str:
        return self.expected.expected_model

    @property
    def expected_topology(self) -> str:
        return self.expected.expected_topology

    @property
    def expected_readiness(self) -> str:
        return self.expected.expected_readiness

    @property
    def expected_resolved_effort(self) -> Optional[str]:
        return self.expected.expected_resolved_effort

    @property
    def expected_min_complexity(self) -> float:
        return self.expected.expected_min_complexity

    @property
    def expected_max_complexity(self) -> float:
        return self.expected.expected_max_complexity

    @property
    def expected_complexity_tier(self) -> Optional[str]:
        return self.expected.expected_complexity_tier

    @property
    def expected_min_reasoning(self) -> float:
        return self.expected.expected_min_reasoning

    @property
    def expected_max_reasoning(self) -> float:
        return self.expected.expected_max_reasoning

    @property
    def expected_reasoning_level(self) -> Optional[str]:
        return self.expected.expected_reasoning_level


SCENARIOS: List[AgentConfigScenario] = [
    AgentConfigScenario(
        id="AC-01",
        name="Routine documentation edit",
        host=_host(MULTI_MODELS),
        profile=MULTI_PROFILE,
        task=TaskCharacteristics(
            title="Fix typo in README",
            description="Fix spelling error in installation section",
            difficulty="routine",
            difficulty_source="unknown",
        ),
        approval="approved",
        expected=AgentConfigExpected(
            expected_tier="routine",
            expected_model="model-alpha",
            expected_topology="Case C",
            expected_readiness="READY",
            expected_resolved_effort="low",
            expected_min_complexity=0.0,
            expected_max_complexity=0.5,
            expected_complexity_tier="routine",
            expected_min_reasoning=0.0,
            expected_max_reasoning=0.8,
            expected_reasoning_level="low",
        ),
        notes="Multi-model Profile: routine tier model and the routine tier's confirmed effort.",
    ),
    AgentConfigScenario(
        id="AC-02",
        name="Small bug fix",
        host=_host(MULTI_MODELS),
        profile=_single_profile("model-beta", {"policy": "standard"}),
        active_model="model-beta",
        task=TaskCharacteristics(
            title="Fix off-by-one error in pagination",
            description="Page index starts at 0 instead of 1",
            difficulty="standard",
            difficulty_source="unknown",
        ),
        approval="approved",
        expected=AgentConfigExpected(
            expected_tier="standard",
            expected_model="model-beta",
            expected_topology="Case A",
            expected_readiness="READY",
            expected_resolved_effort="medium",
            expected_min_complexity=0.5,
            expected_max_complexity=1.5,
            expected_complexity_tier="standard",
            expected_min_reasoning=0.0,
            expected_max_reasoning=1.5,
            expected_reasoning_level=None,
        ),
        notes="Single-model Profile on a selectable Host: the verified session already runs the Profile model.",
    ),
    AgentConfigScenario(
        id="AC-03",
        name="Standard feature implementation",
        host=_host(MULTI_MODELS),
        profile=MULTI_PROFILE,
        task=TaskCharacteristics(
            title="Add CSV export endpoint",
            description="Add export to CSV with standard schema",
            difficulty="standard",
            difficulty_source="unknown",
        ),
        approval="approved",
        expected=AgentConfigExpected(
            expected_tier="standard",
            expected_model="model-beta",
            expected_topology="Case C",
            expected_readiness="READY",
            expected_resolved_effort="medium",
            expected_min_complexity=0.5,
            expected_max_complexity=1.5,
            expected_complexity_tier="standard",
            expected_min_reasoning=0.5,
            expected_max_reasoning=1.5,
            expected_reasoning_level="medium",
        ),
        notes="Multi-model Profile: standard tier model and effort.",
    ),
    AgentConfigScenario(
        id="AC-04",
        name="Large refactor",
        host=_host(MULTI_MODELS),
        profile=MULTI_PROFILE,
        task=TaskCharacteristics(
            title="Refactor core storage engine",
            description="Decompose monolithic storage class into pluggable backend adapters",
            difficulty="high",
            difficulty_source="unknown",
        ),
        approval="approved",
        expected=AgentConfigExpected(
            expected_tier="high",
            expected_model="model-gamma",
            expected_topology="Case C",
            expected_readiness="READY",
            expected_resolved_effort="high",
            expected_min_complexity=1.5,
            expected_max_complexity=3.0,
            expected_complexity_tier="high",
            expected_min_reasoning=1.5,
            expected_max_reasoning=2.0,
            expected_reasoning_level="high",
        ),
        notes="High tier model; the Profile's highest-supported effort resolves to the Host's top value.",
    ),
    AgentConfigScenario(
        id="AC-05",
        name="Security-critical change",
        host=_host(MULTI_MODELS),
        profile=MULTI_PROFILE,
        task=TaskCharacteristics(
            title="Fix authentication token forgery vulnerability",
            description="Harden JWT signature verification and constant-time comparison",
            difficulty="critical",
            difficulty_source="unknown",
        ),
        approval="approved",
        expected=AgentConfigExpected(
            expected_tier="high",
            expected_model="model-gamma",
            expected_topology="Case C",
            expected_readiness="READY",
            expected_resolved_effort="high",
            expected_min_complexity=1.5,
            expected_max_complexity=3.0,
            expected_complexity_tier="high",
            expected_min_reasoning=1.5,
            expected_max_reasoning=2.0,
            expected_reasoning_level="high",
        ),
        notes="Security-critical work maps to the high tier.",
    ),
    AgentConfigScenario(
        id="AC-06",
        name="Complex concurrency work",
        host=_host(MULTI_MODELS),
        profile=MULTI_PROFILE,
        task=TaskCharacteristics(
            title="Implement lock-free queue with memory barriers",
            description="High-throughput cross-thread message passing queue",
            difficulty="high",
            difficulty_source="unknown",
        ),
        approval="approved",
        expected=AgentConfigExpected(
            expected_tier="high",
            expected_model="model-gamma",
            expected_topology="Case C",
            expected_readiness="READY",
            expected_resolved_effort="high",
            expected_min_complexity=1.5,
            expected_max_complexity=3.0,
            expected_complexity_tier="high",
            expected_min_reasoning=1.5,
            expected_max_reasoning=2.0,
            expected_reasoning_level="high",
        ),
        notes="Concurrency work maps to the high tier.",
    ),
    AgentConfigScenario(
        id="AC-07",
        name="Cost-sensitive complex work",
        host=_host(MULTI_MODELS),
        profile=MULTI_PROFILE,
        task=TaskCharacteristics(
            title="Complex algorithm optimization",
            description="Optimize graph traversal algorithms",
            difficulty="high",
            difficulty_source="unknown",
            cost_sensitive=True,
        ),
        approval="approved",
        expected=AgentConfigExpected(
            expected_tier="high",
            expected_model="model-gamma",
            expected_topology="Case C",
            expected_readiness="READY",
            expected_resolved_effort="high",
            expected_min_complexity=1.5,
            expected_max_complexity=3.0,
            expected_complexity_tier="high",
            expected_min_reasoning=1.5,
            expected_max_reasoning=2.0,
            expected_reasoning_level="high",
        ),
        notes="Cost sensitivity does NOT downgrade capability tier; stays high.",
    ),
    AgentConfigScenario(
        id="AC-08",
        name="Latency-sensitive routine work",
        host=_host(MULTI_MODELS),
        profile=MULTI_PROFILE,
        task=TaskCharacteristics(
            title="Quick lint fix",
            description="Run linter and fix whitespace",
            difficulty="routine",
            difficulty_source="unknown",
            latency_sensitive=True,
        ),
        approval="approved",
        expected=AgentConfigExpected(
            expected_tier="routine",
            expected_model="model-alpha",
            expected_topology="Case C",
            expected_readiness="READY",
            expected_resolved_effort="low",
            expected_min_complexity=0.0,
            expected_max_complexity=0.5,
            expected_complexity_tier="routine",
            expected_min_reasoning=0.0,
            expected_max_reasoning=0.8,
            expected_reasoning_level="low",
        ),
        notes="Latency-sensitive routine work stays on the routine tier.",
    ),
    AgentConfigScenario(
        id="AC-09",
        name="Fixed-model harness",
        host=_host(["model-fixed"], effort=(), selector="unavailable"),
        profile=_single_profile("model-fixed", {"policy": "default"}),
        task=TaskCharacteristics(
            title="Complex database migration",
            description="Schema migration across database cluster with zero downtime",
            difficulty="high",
            difficulty_source="unknown",
        ),
        approval="approved",
        expected=AgentConfigExpected(
            expected_tier="high",
            expected_model="model-fixed",
            expected_topology="Case A",
            expected_readiness="READY",
            expected_resolved_effort=None,
            expected_min_complexity=1.5,
            expected_max_complexity=3.0,
            expected_complexity_tier="high",
            expected_min_reasoning=1.5,
            expected_max_reasoning=2.0,
            expected_reasoning_level="high",
        ),
        notes="Fixed-model Host with one evidenced model and no reasoning control keeps that model.",
    ),
    AgentConfigScenario(
        id="AC-10",
        name="Multi-model decomposed harness",
        host=_host(MULTI_MODELS),
        profile=MULTI_PROFILE,
        task=TaskCharacteristics(
            title="Full authentication subsystem",
            description="Decomposed task with formal tickets for OAuth, session, and RBAC",
            shape="decomposed",
            formal_tickets_exist=True,
            difficulty="high",
            difficulty_source="verified-ticket",
        ),
        approval="approved",
        expected=AgentConfigExpected(
            expected_tier="high",
            expected_model="model-gamma",
            expected_topology="Case D",
            expected_readiness="READY",
            expected_resolved_effort="high",
            expected_min_complexity=1.5,
            expected_max_complexity=3.0,
            expected_complexity_tier="high",
            expected_min_reasoning=1.5,
            expected_max_reasoning=2.0,
            expected_reasoning_level="high",
        ),
        notes="Decomposed multi-model work with verified tickets and per-agent selection uses Case D.",
    ),
    AgentConfigScenario(
        id="AC-11",
        name="Host with no effort selector",
        host=_host(MULTI_MODELS, effort=()),
        profile=_multi_profile(effort={"policy": "default"}),
        task=TaskCharacteristics(
            title="Complex compiler backend optimization",
            description="Instruction scheduling and register allocation pass",
            difficulty="high",
            difficulty_source="unknown",
        ),
        approval="approved",
        expected=AgentConfigExpected(
            expected_tier="high",
            expected_model="model-gamma",
            expected_topology="Case C",
            expected_readiness="READY",
            expected_resolved_effort=None,
            expected_min_complexity=1.5,
            expected_max_complexity=3.0,
            expected_complexity_tier="high",
            expected_min_reasoning=1.5,
            expected_max_reasoning=2.0,
            expected_reasoning_level="high",
        ),
        notes="No confirmed reasoning control: effort is omitted, the Profile keeps Host default.",
    ),
    AgentConfigScenario(
        id="AC-12",
        name="Limited effort inventory bounds Profile effort",
        host=_host(["model-x"], effort=("low", "medium"), selector="unavailable"),
        profile=_single_profile("model-x", {"policy": "highest-supported"}),
        task=TaskCharacteristics(
            title="Architectural subsystem rework",
            description="Refactor core event dispatching pipeline",
            difficulty="high",
            difficulty_source="unknown",
        ),
        approval="approved",
        expected=AgentConfigExpected(
            expected_tier="high",
            expected_model="model-x",
            expected_topology="Case A",
            expected_readiness="READY",
            expected_resolved_effort="medium",
            expected_min_complexity=1.5,
            expected_max_complexity=3.0,
            expected_complexity_tier="high",
            expected_min_reasoning=1.5,
            expected_max_reasoning=2.0,
            expected_reasoning_level="high",
        ),
        notes="Host inventory bounds the Profile's highest-supported effort to 'medium'.",
    ),
    AgentConfigScenario(
        id="AC-13",
        name="User explicitly requests high effort (overrides Profile)",
        host=_host(["model-x"], selector="unavailable"),
        profile=_single_profile("model-x", {"policy": "lowest-supported"}),
        task=TaskCharacteristics(
            title="Routine doc update with explicit effort",
            description="Update contributor guidelines",
            difficulty="routine",
            difficulty_source="explicit-user",
            reasoning_policy="highest-supported",
        ),
        approval="approved",
        expected=AgentConfigExpected(
            expected_tier="routine",
            expected_model="model-x",
            expected_topology="Case A",
            expected_readiness="READY",
            expected_resolved_effort="high",
            expected_min_complexity=0.0,
            expected_max_complexity=0.5,
            expected_complexity_tier="routine",
            expected_min_reasoning=0.0,
            expected_max_reasoning=0.8,
            expected_reasoning_level="low",
        ),
        notes="Explicit user reasoning policy overrides the Profile effort; explicit difficulty skips Jev.",
    ),
    AgentConfigScenario(
        id="AC-14",
        name="User rejects configuration change preview",
        host=_host(MULTI_MODELS),
        profile=MULTI_PROFILE,
        active_model="model-alpha",
        task=TaskCharacteristics(
            title="Complex kernel module patch",
            description="Memory management patch in device driver",
            difficulty="high",
            difficulty_source="explicit-user",
        ),
        approval="declined",
        expected=AgentConfigExpected(
            expected_tier="high",
            expected_model="model-alpha",
            expected_topology="Case A",
            expected_readiness="READY",
            expected_resolved_effort=None,
            expected_min_complexity=1.5,
            expected_max_complexity=3.0,
            expected_complexity_tier="high",
            expected_min_reasoning=1.5,
            expected_max_reasoning=2.0,
            expected_reasoning_level="high",
        ),
        notes="User declined the preview: keep the verified current-session model in the main session.",
    ),
]


def validate_fixture_isolation(scenarios: Optional[List[AgentConfigScenario]] = None) -> bool:
    """Validate that runtime task inputs and Jev states contain NO ground truth labels.

    Checks that:
      - 'declared_difficulty' is absent from Jev state.
      - None of the ground truth fields or labels leaked into serialized Jev state.
      - Tasks do not hold references to expected objects.

    Raises RuntimeError if any leakage is detected, blocking evaluation.
    """
    sc_list = scenarios or SCENARIOS
    for sc in sc_list:
        if hasattr(sc.task, "declared_difficulty"):
            raise RuntimeError(
                f"FIXTURE LEAKAGE DETECTED in {sc.id}: 'declared_difficulty' present on task object!"
            )

        simulated_state = {
            "task_title": sc.task.title,
            "task_description": sc.task.description,
            "cost_sensitive": sc.task.cost_sensitive,
            "latency_sensitive": sc.task.latency_sensitive,
        }

        if "declared_difficulty" in simulated_state:
            raise RuntimeError(
                f"FIXTURE LEAKAGE DETECTED in {sc.id}: 'declared_difficulty' present in Jev state!"
            )

        serialized_state = json.dumps(simulated_state).lower()

        forbidden_keys = [
            "expected_tier",
            "expected_model",
            "expected_topology",
            "expected_readiness",
            "expected_resolved_effort",
            "expected_min_complexity",
            "expected_max_complexity",
            "expected_complexity_tier",
            "expected_min_reasoning",
            "expected_max_reasoning",
            "expected_reasoning_level",
        ]
        for fk in forbidden_keys:
            if fk in serialized_state:
                raise RuntimeError(
                    f"FIXTURE LEAKAGE DETECTED in {sc.id}: field '{fk}' leaked into serialized Jev state!"
                )

        if hasattr(sc.task, "expected") or hasattr(sc.task, "ground_truth"):
            raise RuntimeError(
                f"FIXTURE LEAKAGE DETECTED in {sc.id}: task object contains ground_truth/expected reference!"
            )

    return True


def evaluate_scenario(scenario: AgentConfigScenario, client: Optional[Any] = None) -> Dict[str, Any]:
    """Evaluate one agent-config scenario separating config correctness from semantic quality."""
    now = datetime.now(timezone.utc).isoformat()
    host = copy.deepcopy(scenario.host)
    host["observed_at"] = now
    res = agent_config_recommend(
        host=host,
        task=asdict(scenario.task),  # The planner mutates task objects; pass a fresh copy.
        approval=scenario.approval,
        client=client,
        profile=copy.deepcopy(scenario.profile),
        active_session=_active_session(scenario.active_model, now) if scenario.active_model else None,
    )

    readiness_ok = res.readiness == scenario.expected.expected_readiness
    topology_ok = res.execution_config.topology == scenario.expected.expected_topology if res.execution_config else True
    model_ok = res.execution_config.model == scenario.expected.expected_model if res.execution_config else True
    effort_ok = res.execution_config.resolved_effort == scenario.expected.expected_resolved_effort if res.execution_config else True
    tier_ok = res.abstract_profile.recommended_tier == scenario.expected.expected_tier if res.abstract_profile else True

    # Candidate safety invariant: selected_model must be in valid candidates (or active_model)
    valid_candidates = [m["id"] for m in scenario.host["available_models"]]
    candidate_safe = res.execution_config.model in valid_candidates if res.execution_config else True

    config_correctness_passed = readiness_ok and topology_ok and model_ok and effort_ok and tier_ok and candidate_safe

    # Provenance tracking
    comp_score = res.abstract_profile.complexity_score if res.abstract_profile else None
    comp_conf = res.abstract_profile.complexity_confidence if res.abstract_profile else None
    comp_src = None
    reas_score = res.abstract_profile.reasoning_score if res.abstract_profile else None
    reas_conf = res.abstract_profile.reasoning_confidence if res.abstract_profile else None
    reas_src = None

    if res.abstract_profile and res.abstract_profile.dimension_provenance:
        prov = res.abstract_profile.dimension_provenance
        if "complexity" in prov:
            comp_src = prov["complexity"].source
        if "reasoning" in prov:
            reas_src = prov["reasoning"].source

    # Complexity semantic evaluation (tri-state: PASS, FAIL, NOT_EVALUATED)
    complexity_semantic = "NOT_EVALUATED"
    if comp_src == "jev" and comp_score is not None:
        score_ok = scenario.expected.expected_min_complexity <= comp_score <= scenario.expected.expected_max_complexity
        tier_matched = (scenario.expected.expected_complexity_tier is None or res.abstract_profile.recommended_tier == scenario.expected.expected_complexity_tier)
        complexity_semantic = "PASS" if (score_ok and tier_matched) else "FAIL"

    # Reasoning semantic evaluation (tri-state: PASS, FAIL, NOT_EVALUATED)
    reasoning_semantic = "NOT_EVALUATED"
    if reas_src == "jev" and reas_score is not None:
        score_ok = scenario.expected.expected_min_reasoning <= reas_score <= scenario.expected.expected_max_reasoning
        level_matched = (scenario.expected.expected_reasoning_level is None or res.abstract_profile.reasoning_need == scenario.expected.expected_reasoning_level)
        reasoning_semantic = "PASS" if (score_ok and level_matched) else "FAIL"

    # Overall pass: configuration must be correct; and evaluated semantics must not fail
    overall_passed = config_correctness_passed and (complexity_semantic != "FAIL") and (reasoning_semantic != "FAIL")

    return {
        "id": scenario.id,
        "name": scenario.name,
        "passed": overall_passed,
        "config_correctness_passed": config_correctness_passed,
        "complexity_semantic": complexity_semantic,
        "reasoning_semantic": reasoning_semantic,
        "readiness_matched": readiness_ok,
        "topology_matched": topology_ok,
        "model_matched": model_ok,
        "effort_matched": effort_ok,
        "tier_matched": tier_ok,
        "candidate_safe": candidate_safe,
        "observed_model": res.execution_config.model if res.execution_config else None,
        "observed_effort": res.execution_config.resolved_effort if res.execution_config else None,
        "observed_topology": res.execution_config.topology if res.execution_config else None,
        "observed_tier": res.abstract_profile.recommended_tier if res.abstract_profile else None,
        "observed_reasoning": res.abstract_profile.reasoning_need if res.abstract_profile else None,
        "fallback_used": res.fallback_used,
        "approval_state": res.approval,
        "raw_evidence": {
            "complexity_score": comp_score,
            "complexity_confidence": comp_conf,
            "complexity_source": comp_src,
            "expected_complexity_range": [scenario.expected.expected_min_complexity, scenario.expected.expected_max_complexity],
            "reasoning_score": reas_score,
            "reasoning_confidence": reas_conf,
            "reasoning_source": reas_src,
            "expected_reasoning_range": [scenario.expected.expected_min_reasoning, scenario.expected.expected_max_reasoning],
        },
    }


def run_agent_config_eval(client: Optional[Any] = None) -> Dict[str, Any]:
    """Run all 14 agent-config evaluation scenarios."""
    validate_fixture_isolation()

    results = [evaluate_scenario(sc, client=client) for sc in SCENARIOS]
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    config_passed = sum(1 for r in results if r["config_correctness_passed"])

    # Complexity breakdown (4 sources)
    comp_auth = sum(
        1 for r in results
        if r["raw_evidence"]["complexity_source"] in ("explicit-user", "verified-ticket", "deterministic-policy")
    )
    comp_eval = sum(1 for r in results if r["raw_evidence"]["complexity_source"] == "jev")
    comp_pass = sum(1 for r in results if r["complexity_semantic"] == "PASS")
    comp_fail = sum(1 for r in results if r["complexity_semantic"] == "FAIL")
    comp_fallback = sum(1 for r in results if r["raw_evidence"]["complexity_source"] == "deterministic-fallback")
    comp_not_eval = total - comp_eval
    comp_acc = (comp_pass / comp_eval) if comp_eval > 0 else None

    # Reasoning breakdown (4 sources)
    reas_policy = sum(
        1 for r in results
        if r["raw_evidence"]["reasoning_source"] in ("explicit-policy", "explicit-user")
    )
    reas_eval = sum(1 for r in results if r["raw_evidence"]["reasoning_source"] == "jev")
    reas_pass = sum(1 for r in results if r["reasoning_semantic"] == "PASS")
    reas_fail = sum(1 for r in results if r["reasoning_semantic"] == "FAIL")
    reas_fallback = sum(1 for r in results if r["raw_evidence"]["reasoning_source"] == "deterministic-fallback")
    reas_not_eval = total - reas_eval
    reas_acc = (reas_pass / reas_eval) if reas_eval > 0 else None

    return {
        "suite": "agent-config",
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "accuracy": passed / total if total > 0 else 0.0,
        "config_correctness_passed": config_passed,
        "config_correctness_accuracy": config_passed / total if total > 0 else 0.0,
        "complexity_authoritative": comp_auth,
        "complexity_evaluated": comp_eval,
        "complexity_passed": comp_pass,
        "complexity_failed": comp_fail,
        "complexity_fallback": comp_fallback,
        "complexity_not_evaluated": comp_not_eval,
        "complexity_accuracy": comp_acc,
        "reasoning_explicit_policy": reas_policy,
        "reasoning_evaluated": reas_eval,
        "reasoning_passed": reas_pass,
        "reasoning_failed": reas_fail,
        "reasoning_fallback": reas_fallback,
        "reasoning_not_evaluated": reas_not_eval,
        "reasoning_accuracy": reas_acc,
        "results": results,
    }
