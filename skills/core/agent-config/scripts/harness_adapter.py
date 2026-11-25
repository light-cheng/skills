"""Deterministic harness capability adapter for agent-config.

Enforces deterministic capability discovery and effort resolution:
  - Never emit unverified literal 'max'.
  - Support hosts without model selector gracefully (single-model peer mode).
  - Four peer topologies: Case A, Case B, Case C, Case D.
"""

from __future__ import annotations

from typing import List, Optional

try:
    from .agent_config_models import HostCapabilities, TaskCharacteristics
except ImportError:
    from agent_config_models import HostCapabilities, TaskCharacteristics


def resolve_reasoning_effort(
    host: HostCapabilities,
    policy: Optional[str] = None,
    profile_reasoning_need: Optional[str] = None,
) -> Optional[str]:
    """Resolve reasoning effort strictly to verified host-supported strings.

    Precedence:
      1. Host capability constraints: if host does not support reasoning controls, returns None.
      2. Explicit user reasoning policy / profile policy: authoritative; a typed decision cannot lower or override.
      3. Typed reasoning judgment (profile_reasoning_need): maps to nearest verified supported value.
      4. Deterministic fallback: None.
    """
    if not host.supported_effort:
        return None

    efforts = [e.lower() for e in host.supported_effort]

    def exact_host_value(value: str) -> str:
        return host.supported_effort[efforts.index(value)]

    if policy:
        if policy == "highest-supported":
            return host.supported_effort[-1]
        if policy in ("lowest-supported", "minimal"):
            return host.supported_effort[0]
        if policy == "default":
            return host.default_effort if host.default_effort in host.supported_effort else None
        if policy == "standard":
            if "medium" in efforts:
                return exact_host_value("medium")
            if "standard" in efforts:
                return exact_host_value("standard")
            return host.supported_effort[0]
        if policy.lower() in efforts:
            return exact_host_value(policy.lower())
        return None

    if profile_reasoning_need:
        need = profile_reasoning_need.lower()
        if need == "high":
            if "high" in efforts:
                return exact_host_value("high")
            if "medium" in efforts:
                return exact_host_value("medium")
            return host.supported_effort[-1]
        if need == "medium":
            if "medium" in efforts:
                return exact_host_value("medium")
            if "standard" in efforts:
                return exact_host_value("standard")
            if "low" in efforts:
                return exact_host_value("low")
            return host.supported_effort[0]
        if need == "low":
            if "low" in efforts:
                return exact_host_value("low")
            if "minimal" in efforts:
                return exact_host_value("minimal")
            return host.supported_effort[0]

    return None


def discover_valid_candidates(host: HostCapabilities) -> List[str]:
    """Return strictly legal candidate models supported by this harness and confirmed in profile."""
    if not host.has_model_selector:
        return [host.active_model] if host.active_model in host.available_models else []

    valid: List[str] = []
    for model in host.profile_tiers.values():
        if model in host.available_models and model not in valid:
            valid.append(model)

    if not valid and host.active_model in host.available_models:
        valid.append(host.active_model)

    return valid


def determine_topology(
    host: HostCapabilities,
    task: TaskCharacteristics,
    valid_candidates: Optional[List[str]] = None,
    target_model: Optional[str] = None,
) -> str:
    """Determine one of the 4 peer execution modes (Cases A, B, C, D)."""
    candidates = valid_candidates if valid_candidates is not None else discover_valid_candidates(host)
    if task.shape == "decomposed":
        if host.profile_mode == "single" or not host.has_model_selector:
            return "Case B"
        if host.per_agent_config and len(candidates) > 1:
            return "Case D"
        return "Case B"

    if host.profile_mode == "single" or not host.has_model_selector:
        return "Case A"
    if host.profile_mode == "multi" or (
        target_model is not None and target_model != host.active_model and host.has_model_selector
    ):
        return "Case C"
    return "Case A"
