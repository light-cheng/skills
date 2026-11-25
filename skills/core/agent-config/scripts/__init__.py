"""Agent Config execution configurator package."""

from __future__ import annotations

from .abstract_profiler import (
    COMPLEXITY_LEVELS,
    COMPLEXITY_QUESTION,
    DOWNGRADE_MARGIN,
    REASONING_LEVELS,
    REASONING_QUESTION,
    build_deterministic_profile,
    extract_abstract_task_profile,
)
from .agent_config import agent_config_recommend
from .agent_config_models import (
    AbstractTaskProfile,
    AgentConfigResult,
    DimensionProvenance,
    ExecutionConfig,
    HostCapabilities,
    TaskCharacteristics,
)
from .candidate_selector import select_configuration
from .harness_adapter import (
    determine_topology,
    discover_valid_candidates,
    resolve_reasoning_effort,
)

__all__ = [
    "COMPLEXITY_LEVELS",
    "COMPLEXITY_QUESTION",
    "DOWNGRADE_MARGIN",
    "REASONING_LEVELS",
    "REASONING_QUESTION",
    "AbstractTaskProfile",
    "AgentConfigResult",
    "DimensionProvenance",
    "ExecutionConfig",
    "HostCapabilities",
    "TaskCharacteristics",
    "agent_config_recommend",
    "build_deterministic_profile",
    "determine_topology",
    "discover_valid_candidates",
    "extract_abstract_task_profile",
    "resolve_reasoning_effort",
    "select_configuration",
]
