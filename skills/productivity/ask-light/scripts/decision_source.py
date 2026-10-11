"""Decision source resolution and policy for the script path of light-decide.

The script asks a typed decision client (the `typesafe_sdk` client) only when
the project's data limit allows the endpoint's destination. Thresholds come
from the user's policy file; an answer is applied only when its question is
calibrated there. Results use the light-decide normalized format.
"""

from __future__ import annotations

import ipaddress
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

DESTINATIONS = ("on-device", "private-network", "third-party")
LIMITS = DESTINATIONS + ("off",)
DEFAULT_LIMIT = "on-device"
POLICY_PATH = Path("~/.config/light/decision-policy.json")
PROJECT_FILE = Path("docs/agents/light-project.md")
HOSTED_ENDPOINT = "typesafe-hosted"
LOCAL_PLACEHOLDER_KEY = "local-no-key"

# The setting is a label: "Decision data:" or a table row "| Decision data | value |",
# after optional list markers or emphasis. A mention inside other text is not the setting.
_DECISION_LABEL = re.compile(r"^\s*(?:[-*+]\s+)?\|?\s*[*_`]*decision data[*_`]*\s*(?::|\|)", re.IGNORECASE)
_FENCE = re.compile(r"^\s*(```|~~~)")


def find_project_file(start: Optional[Path]) -> Optional[Path]:
    """The nearest docs/agents/light-project.md from `start` (or cwd) upward, stopping at a git root."""
    here = (start or Path.cwd()).resolve()
    for folder in (here, *here.parents):
        candidate = folder / PROJECT_FILE
        if candidate.is_file():
            return candidate
        if (folder / ".git").exists():
            return None
    return None


def read_decision_limit(project_root: Optional[Path]) -> tuple[str, bool]:
    """Return (limit, recognized). No line means on-device; any other value means off.

    The line may carry list markers, emphasis, code ticks or table bars. Lines
    inside code fences are examples, not the setting.
    """
    path = find_project_file(project_root)
    if path is None:
        return DEFAULT_LIMIT, True
    in_fence = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if _FENCE.match(line):
            in_fence = not in_fence
            continue
        match = _DECISION_LABEL.match(line)
        if in_fence or not match:
            continue
        value = re.sub(r"[*_`|:]", " ", line[match.end():]).strip().lower()
        if value in LIMITS:
            return value, True
        return "off", False
    return DEFAULT_LIMIT, True


def within_limit(destination: str, limit: str) -> bool:
    if limit == "off" or destination not in DESTINATIONS:
        return False
    return DESTINATIONS.index(destination) <= DESTINATIONS.index(limit)


def load_policy(path: Optional[Path] = None) -> Dict[str, Any]:
    """Read the user's policy file. Missing or unreadable means every source is uncalibrated."""
    target = (path or POLICY_PATH).expanduser()
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _endpoint_name(base_url: Optional[str]) -> str:
    """`host:port` of the endpoint, never its credentials or path."""
    if not base_url:
        return HOSTED_ENDPOINT
    parsed = urlparse(base_url)
    host = parsed.hostname or "unknown-endpoint"
    return f"{host}:{parsed.port}" if parsed.port else host


def _host_destination(base_url: Optional[str]) -> str:
    if not base_url:
        return "third-party"
    host = urlparse(base_url).hostname or ""
    if host == "localhost":
        return "on-device"
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        return "third-party"
    if addr.is_loopback:
        return "on-device"
    if addr.is_private:
        return "private-network"
    return "third-party"


def _farther(a: str, b: str) -> str:
    return a if DESTINATIONS.index(a) >= DESTINATIONS.index(b) else b


def _find_backend(policy: Dict[str, Any], reported: str) -> tuple[Optional[str], Dict[str, Any]]:
    backends = policy.get("backends")
    if not isinstance(backends, dict):
        return None, {}
    for key, entry in backends.items():
        if not isinstance(entry, dict):
            continue
        names = entry.get("names")
        if reported == key or (isinstance(names, list) and reported in names):
            return key, entry
    return None, {}


def _read_env_key(project_root: Optional[Path]) -> Optional[str]:
    env_key = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if env_key:
        return env_key
    if project_root is None:
        return None
    env_path = project_root / ".env"
    if not env_path.is_file():
        return None
    for line in env_path.read_text(encoding="utf-8").splitlines():
        key, sep, value = line.strip().partition("=")
        if sep and key.strip() == "TYPESAFE_API_KEY":
            return value.strip().strip("'\"") or None
    return None


@dataclass
class DecisionSource:
    limit: str
    limit_recognized: bool
    backend: str
    data: str
    base_url: Optional[str]
    api_key: Optional[str]
    policy_entry: Dict[str, Any]
    usable: bool
    reason: str  # "none" when usable, otherwise a light-decide fallback_reason

    def min_confidence(self, question_id: str) -> Optional[float]:
        """Threshold for a calibrated question, or None when it is uncalibrated."""
        questions = self.policy_entry.get("questions")
        entry = questions.get(question_id) if isinstance(questions, dict) else None
        if not isinstance(entry, dict):
            return None
        threshold = entry.get("min_confidence")
        calibration = entry.get("calibration")
        if (isinstance(threshold, (int, float)) and not isinstance(threshold, bool) and 0 <= threshold <= 1
                and isinstance(calibration, str) and calibration.strip()):
            return float(threshold)
        return None


def resolve_source(
    project_root: Optional[Path],
    sdk_available: bool,
    policy: Optional[Dict[str, Any]] = None,
) -> DecisionSource:
    """Decide whether the script may ask the typed decision client in this run."""
    limit, recognized = read_decision_limit(project_root)
    base_url = os.environ.get("TYPESAFE_BASE_URL", "").strip() or None
    reported = _endpoint_name(base_url)
    backend, entry = _find_backend(policy if policy is not None else load_policy(), reported)
    data = _host_destination(base_url)
    declared = entry.get("data")
    if declared in DESTINATIONS:
        data = _farther(data, declared)
    # A private address counts as the user's own network only when the policy says so.
    if data == "private-network" and declared != "private-network":
        data = "third-party"
    api_key = _read_env_key(project_root)
    if api_key is None and data == "on-device":
        api_key = LOCAL_PLACEHOLDER_KEY

    source = DecisionSource(
        limit=limit,
        limit_recognized=recognized,
        backend=backend or reported,
        data=data,
        base_url=base_url,
        api_key=api_key,
        policy_entry=entry,
        usable=False,
        reason="none",
    )
    if limit == "off":
        source.reason = "off"
    elif not within_limit(data, limit) or not sdk_available or not api_key:
        source.reason = "unavailable"
    else:
        source.usable = True
    return source


def make_client(client_cls: Any, source: DecisionSource) -> Any:
    """One attempt per judgment: a timeout or error falls back, never retries.

    The client reads TYPESAFE_BASE_URL itself; swapping backends changes only that variable.
    """
    from typesafe_sdk import RetryPolicy

    return client_cls(api_key=source.api_key, retry=RetryPolicy(max_retries=0))


def yes_no_probabilities(p_yes: float) -> Dict[str, float]:
    p_yes = min(max(float(p_yes), 0.0), 1.0)
    return {"yes": round(p_yes, 4), "no": round(1.0 - p_yes, 4)}


def typed_result(
    source: DecisionSource,
    question_id: str,
    question: str,
    kind: str,
    options: List[str],
    answer: str,
    probabilities: Dict[str, float],
    own_answer: str,
    provider_confidence: Optional[float] = None,
    score: Optional[float] = None,
    confidence: Optional[float] = None,
) -> Dict[str, Any]:
    """Normalize a typed answer and apply the policy: use it only when calibrated and confident."""
    if confidence is None:
        confidence = float(probabilities.get(answer, 0.0))
    threshold = source.min_confidence(question_id)
    calibrated = threshold is not None
    if answer not in options:
        applied, reason = False, "malformed"
    elif not calibrated:
        applied, reason = False, "uncalibrated"
    elif confidence < threshold:
        applied, reason = False, "low-confidence"
    else:
        applied, reason = True, "none"
    return {
        "question_id": question_id,
        "question": question,
        "kind": kind,
        "options": list(options),
        "answer": answer,
        "score": score,
        "probabilities": dict(probabilities),
        "confidence": round(confidence, 4),
        "provider_confidence": provider_confidence,
        "method": "typed-decision",
        "data": source.data,
        "backend": source.backend,
        "calibrated": calibrated,
        "applied": applied,
        "fallback_reason": reason,
        "final": answer if applied else own_answer,
    }


def own_result(
    question_id: str,
    question: str,
    kind: str,
    options: List[str],
    final: str,
    reason: str,
) -> Dict[str, Any]:
    """A self-judgment result: the script's deterministic answer stands in for the agent's own."""
    return {
        "question_id": question_id,
        "question": question,
        "kind": kind,
        "options": list(options),
        "answer": final,
        "score": None,
        "probabilities": {},
        "confidence": None,
        "provider_confidence": None,
        "method": "self-judgment",
        "data": "in-session",
        "backend": "agent",
        "calibrated": False,
        "applied": True,
        "fallback_reason": reason,
        "final": final,
    }
