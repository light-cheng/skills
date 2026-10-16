"""Stage-aware release document semantics shared by the release CLI gates.

The context is an input to a check, never a second release-state ledger.
Manifest/Receipt content and observed external facts remain authoritative.
"""

from __future__ import annotations

import re
import posixpath
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Mapping
from urllib.parse import unquote, urlparse

from repo_identity import REPO_PATTERN, RELEASE_URL_PATTERN, is_release_url

PUBLIC_RELEASE_DOCS = (
    "README.md", "README.zh-CN.md", "CATALOG.md", "CATALOG.zh-CN.md",
    "docs/INSTALLATION.md", "docs/INSTALLATION.zh-CN.md",
    "docs/MAINTENANCE.md", "docs/MAINTENANCE.zh-CN.md",
)
STAGES = ("prepared", "ci_verified", "tagged", "install_verified", "published", "attested")
VERSION = r"v\d+\.\d+\.\d+"


@dataclass(frozen=True)
class ReleaseContext:
    target: str
    stage: str
    revision: str | None = None
    mode: str = "current"
    current_stable: str | None = None
    evidence_source: str | None = None
    install_verified: bool = False
    published: bool = False
    simulated: bool = False
    repository: str | None = None  # owner/name when known; None accepts any GitHub repository

    def __post_init__(self) -> None:
        if not re.fullmatch(VERSION, self.target):
            raise ValueError("target must be a vX.Y.Z release identifier")
        if self.stage not in STAGES:
            raise ValueError(f"unsupported release stage: {self.stage}")
        if self.mode not in ("current", "historical"):
            raise ValueError("mode must be current or historical")
        if self.mode == "historical" and self.stage in ("prepared", "ci_verified"):
            raise ValueError("historical mode cannot prepare or promote a candidate")


def version_key(version: str) -> tuple[int, int, int]:
    return tuple(int(part) for part in version.lstrip("v").split("."))


def legacy_snapshot(context: ReleaseContext) -> bool:
    """Preserve already frozen documents from before the semantic gate existed."""
    return context.mode == "historical" and version_key(context.target) <= (0, 2, 7)


def apply_observations(context: ReleaseContext, data: Mapping, candidate: str,
                       source: str, *, simulate: bool = False,
                       package_count: int | None = None) -> tuple[ReleaseContext, list[str]]:
    """Validate recorded external observations; test facts require explicit simulation."""
    kind = data.get("kind")
    errors = validate_observation_kind(data, source, simulate=simulate)
    if data.get("tag") != context.target or data.get("candidate") != candidate:
        errors.append(f"[OBSERVATION_IDENTITY] {source}: observations must identify {context.target} at {candidate}")
    errors.extend(validate_ci_observation(data.get("ci"), candidate, source))
    install_verified = False
    if context.stage in ("install_verified", "published", "attested") or "installation" in data:
        install_errors = validate_installation_observation(data.get("installation"), context.target, candidate, source, package_count)
        errors.extend(install_errors)
        install_verified = not install_errors
    published = False
    if context.stage in ("published", "attested") or "release" in data:
        publication_errors = validate_publication_observation(data.get("release"), context.target, source, context.repository)
        errors.extend(publication_errors)
        published = not publication_errors
        if published:
            body_context = replace(context, install_verified=install_verified, published=True, evidence_source=source)
            body = data["release"].get("body")
            if not isinstance(body, str) or not body.strip():
                errors.append(f"[RELEASE_BODY_MISSING] {source}: include the observed GitHub Release body")
            else:
                errors.extend(validate_document(body, f"{source}:GitHub Release body", "release-body", body_context))
                errors.extend(document_links(body, f"{source}:GitHub Release body", body_context, set()))
    return replace(context, evidence_source=source, simulated=kind == "test-double",
                   install_verified=install_verified, published=published), errors


def validate_observation_kind(record: Mapping, source: str, *, simulate: bool = False) -> list[str]:
    kind = record.get("kind")
    if kind not in ("observed", "test-double"):
        return [f"[OBSERVATION_KIND] {source}: kind must be observed or test-double"]
    if kind == "test-double" and not simulate:
        return [f"[SIMULATION_FLAG_REQUIRED] {source}: test-double facts require --simulate"]
    return []


def validate_ci_observation(record, commit: str, source: str) -> list[str]:
    errors: list[str] = []
    record = record if isinstance(record, dict) else {}
    if not re.fullmatch(r"[1-9]\d*", str(record.get("databaseId", ""))) or record.get("headSha") != commit:
        errors.append(f"[CI_IDENTITY] {source}: CI requires a run ID and exact headSha {commit}")
    if record.get("status") != "completed" or record.get("conclusion") != "success":
        errors.append(f"[CI_NOT_SUCCESSFUL] {source}: CI requires status=completed and conclusion=success")
    return errors


def validate_installation_observation(record, tag: str, candidate: str,
                                     source: str, package_count: int | None) -> list[str]:
    """Consume the existing verify_release_installation.py result shape."""
    if not isinstance(record, dict):
        return [f"[INSTALLATION_UNOBSERVED] {source}: include the actual-source installation result"]
    errors: list[str] = []
    if record.get("status") != "VERIFIED" or record.get("tag") != tag or record.get("pinned_commit") != candidate:
        errors.append(f"[INSTALLATION_IDENTITY] {source}: installation must verify {tag} at pinned commit {candidate}")
    if not re.fullmatch(r"[0-9a-f]{40}", str(record.get("default_commit", ""))):
        errors.append(f"[INSTALLATION_IDENTITY] {source}: record the observed default-branch commit")
    observations = record.get("observations", [])
    observations = observations if isinstance(observations, list) else []
    cases = {item.get("case"): item for item in observations if isinstance(item, dict)}
    for case, field in (("pinned-whole", "pinned_package_manifest"), ("default-whole", "default_package_manifest")):
        expected = record.get(field)
        destinations = cases.get(case, {}).get("destinations")
        if not isinstance(expected, dict) or not expected or not isinstance(destinations, list) or not destinations:
            errors.append(f"[INSTALLATION_PAYLOAD] {source}: {case} requires a source manifest and observed destinations")
            continue
        if any(not isinstance(files, dict) or not files or any(not re.fullmatch(r"[0-9a-f]{64}", str(digest)) for digest in files.values())
               for files in expected.values()):
            errors.append(f"[INSTALLATION_PAYLOAD] {source}: {case} requires complete nonempty package hashes")
            continue
        if case == "pinned-whole" and package_count is not None and len(expected) != package_count:
            errors.append(f"[INSTALLATION_PAYLOAD] {source}: pinned manifest count differs from release tree ({package_count})")
        for destination in destinations:
            if (not isinstance(destination, dict) or destination.get("exact") is not True
                    or destination.get("packages") != len(expected)
                    or destination.get("files") != sum(len(files) for files in expected.values())
                    or destination.get("actual_package_manifest") != expected):
                errors.append(f"[INSTALLATION_PAYLOAD] {source}: {case} destination does not match its actual source bytes")
    return errors


def valid_publication_time(value) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is not None
    except ValueError:
        return False


def validate_publication_observation(record, tag: str, source: str, repo: str | None = None) -> list[str]:
    if not isinstance(record, dict):
        return [f"[PUBLICATION_UNOBSERVED] {source}: include the observed GitHub Release result"]
    if (record.get("tagName") != tag or record.get("isDraft") is not False
            or record.get("isPrerelease") is not False or not valid_publication_time(record.get("publishedAt"))
            or not is_release_url(record.get("url"), tag, repo)):
        return [f"[PUBLICATION_IDENTITY] {source}: require the matching non-draft stable release URL and observed publication time"]
    return []


def active_lines(text: str, *, include_code: bool = False):
    """Yield current statements; a named historical section keeps its own time context."""
    historical_level: int | None = None
    in_code = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code and not include_code:
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)", line) if not in_code else None
        if heading:
            level, title = len(heading.group(1)), heading.group(2)
            if historical_level is not None and level <= historical_level:
                historical_level = None
            if re.search(r"histor(?:y|ical)|previous releases?|rollback|recovery|历史|回退|恢复", title, re.I):
                historical_level = level
        if historical_level is None:
            yield number, line


def plain(line: str) -> str:
    return re.sub(r"[`*\[\]]", "", line)


def stable_claims(line: str) -> set[str]:
    value = plain(line)
    if not re.search(r"current stable|当前稳定", value, re.I) and re.search(r"stable release snapshot|historical stable|历史稳定|稳定(?:发布|版本)?快照", value, re.I):
        return set()
    value = re.split(r"previous stable|prior stable|stable at preparation|上一稳定|准备时", value, maxsplit=1, flags=re.I)[0]
    patterns = (
        rf"(?:current stable(?: release)?|stable release|当前稳定(?:版本)?|稳定版本)[^\n\|;；]{{0,100}}?({VERSION})",
        rf"({VERSION})[^\n\|;；]{{0,80}}?(?:current stable|当前稳定)",
        rf"(?:Stable release|稳定版本)\s*\|\s*({VERSION})",
    )
    return {match.group(1) for pattern in patterns for match in re.finditer(pattern, value, re.I)}


def confirmed_stable(documents: Mapping[str, str]) -> tuple[str | None, str | None]:
    """Derive current stable identity from bilingual VERIFIED receipts, not public prose."""
    confirmed: list[tuple[str, str]] = []
    for path, text in documents.items():
        match = re.fullmatch(rf"docs/evidence/releases/({VERSION})/RELEASE_RECEIPT\.md", path)
        if not match:
            continue
        other = documents.get(path.replace(".md", ".zh-CN.md"), "")
        if not re.search(r"^Status:\s*`?VERIFIED\b", text, re.M):
            continue
        if not re.search(r"^(?:Status|状态)[：:]\s*`?VERIFIED\b", other, re.M):
            continue
        version = match.group(1)
        identity_en = re.search(r"\|\s*\*\*Release\*\*\s*\|\s*`?([^`|\s]+)", text)
        identity_zh = re.search(r"\|\s*\*\*发布版本\*\*\s*\|\s*`?([^`|\s]+)", other)
        if not identity_en or not identity_zh or identity_en.group(1) != version or identity_zh.group(1) != version:
            continue
        url = re.compile(RELEASE_URL_PATTERN + re.escape(version) + r"(?![\w.-])")
        if not url.search(text) or not url.search(other):
            continue
        if not re.search(r"\|\s*\*\*GitHub Release Publication\*\*\s*\|\s*`?(?:PASS|SUCCESS)`?\s*\|", text, re.I):
            continue
        if not re.search(r"\|\s*\*\*GitHub Release 发布\*\*\s*\|\s*`?(?:PASS|SUCCESS)`?\s*\|", other, re.I):
            continue
        confirmed.append((version, path))
    return max(confirmed, key=lambda pair: version_key(pair[0])) if confirmed else (None, None)


def infer_document_context(documents: Mapping[str, str]) -> ReleaseContext | None:
    """Select the branch's document view from Manifest/Receipt authority, not public prose."""
    stable, source = confirmed_stable(documents)
    manifests = []
    for path in documents:
        match = re.fullmatch(rf"docs/evidence/releases/({VERSION})/RELEASE_MANIFEST(?:\.zh-CN)?\.md", path)
        if match:
            manifests.append((match.group(1), path))
    candidate = max(manifests, key=lambda pair: version_key(pair[0])) if manifests else None
    if candidate and (stable is None or version_key(candidate[0]) > version_key(stable)):
        return ReleaseContext(candidate[0], "prepared", current_stable=stable, evidence_source=candidate[1])
    if stable:
        return ReleaseContext(stable, "attested", current_stable=stable, evidence_source=source,
                              install_verified=True, published=True)
    return None


def validate_document(text: str, path: str, kind: str, context: ReleaseContext) -> list[str]:
    """Validate one release object; findings name the object and its statement."""
    if kind in ("snapshot", "notes", "manifest") and legacy_snapshot(context):
        return []
    errors: list[str] = []
    active = list(active_lines(text))
    frozen = kind in ("snapshot", "notes", "manifest")
    errors.extend(installation_command_errors(text, path, context, frozen=frozen))
    for number, line in active:
        for statement in re.split(r"[;；。]|\.\s+(?!\d)", plain(line)):
            if installation_claim(statement) and (frozen or not context.install_verified):
                errors.append(f"[UNOBSERVED_INSTALLATION] {path}:{number}: released-source installation success requires observed installation facts")
            if publication_claim(statement) and (frozen or not context.published):
                errors.append(f"[UNOBSERVED_PUBLICATION] {path}:{number}: publication success requires observed publication facts")
    if kind == "manifest":
        if not re.search(r"(?:Preparation (?:snapshot|status)|准备(?:时快照|状态|快照))[：:]", plain(text), re.I):
            errors.append(f"[MANIFEST_TIME_CONTEXT] {path}: label the document as a preparation-time snapshot")
        identity_lines = [plain(line) for _, line in active
                          if re.search(r"^#\s|Release(?: Version)?\s*[:|]|发布版本\s*[：:|]", plain(line), re.I)]
        identities = {version for line in identity_lines for version in re.findall(VERSION, line)}
        if identities != {context.target} or f"refs/tags/{context.target}" not in text:
            errors.append(f"[MANIFEST_IDENTITY] {path}: expected {context.target} and its exact refs/tags identity")
    if kind == "current":
        claims = {version for _, line in active for version in stable_claims(line)}
        if context.current_stable is None or claims != {context.current_stable}:
            errors.append(f"[CURRENT_STABLE] {path}: expected confirmed stable {context.current_stable}, found {sorted(claims)}; source={context.evidence_source}")
        for number, line in active:
            if candidate_statement(line, context):
                errors.append(f"[CURRENT_CANDIDATE_STATE] {path}:{number}: current publication authority retains candidate status")
    if kind in ("snapshot", "notes", "current-notes", "release-body"):
        identity_lines = [plain(line) for _, line in active if re.search(r"release snapshot|版本快照", plain(line), re.I)]
        if kind != "snapshot":
            identity_lines.extend(plain(line) for _, line in active if re.match(r"^#\s", line))
        identities = {version for line in identity_lines for version in re.findall(VERSION, line)}
        if identities != {context.target}:
            errors.append(f"[SNAPSHOT_IDENTITY] {path}: expected release snapshot {context.target}, found {sorted(identities)}")
        if not re.search(r"RELEASE_MANIFEST", text) or not re.search(r"(?:receipt|收据).*main|main.*(?:receipt|收据)", text, re.I):
            errors.append(f"[SNAPSHOT_EVIDENCE] {path}: name the Manifest and the observed-facts receipt on main")
        for number, line in active:
            if kind in ("snapshot", "notes") and stable_claims(line):
                errors.append(f"[SNAPSHOT_CURRENT_STATE] {path}:{number}: a frozen snapshot cannot assert a current stable release")
            if candidate_statement(line, context):
                code = "RELEASE_BODY_CANDIDATE_STATE" if kind == "release-body" else "SNAPSHOT_CANDIDATE_STATE"
                errors.append(f"[{code}] {path}:{number}: candidate status would become stale in the release object")
        if kind in ("release-body", "current-notes") and not re.search(r"(?:^|\n)(?:#{1,6}\s*|\*\*)?(?:Verification|Release status|验证|发布状态)", text, re.I):
            errors.append(f"[RELEASE_VERIFICATION_CONTEXT] {path}: retain the verification/status section and its evidence source")
    return errors


def candidate_statement(line: str, context: ReleaseContext) -> bool:
    value = plain(line)
    if not re.search(r"not yet (?:published|released)|unpublished|unreleased|release candidate|尚未发布|未发布|候选(?:版本|发布)", value, re.I):
        return False
    # Maintenance instructions describe any candidate; they do not assert this
    # version's state. Explicit status fields and target statements still fail.
    if context.target in value or re.search(r"(?:release|publication|current) status|(?:发布|当前)状态|this (?:version|release)|本(?:版|版本)|目标(?:版本)?", value, re.I):
        return True
    return not bool(re.search(r"\b(?:if|when|prepare|create|update|template|must|should)\b|若|如果|准备|创建|更新|先写|验证失败时|必须|模板", value, re.I))


def installation_claim(statement: str) -> bool:
    return bool(re.search(r"\binstall(?:ation)?s?\b|安装", statement, re.I)
                and re.search(r"\b(?:pass(?:ed)?|verified|success(?:ful(?:ly)?)?)\b|通过|已验证|成功", statement, re.I)
                and not re.search(r"not (?:verified|passed)|not installation evidence|不是安装证据|未验证|未通过", statement, re.I))


def installation_command_errors(text: str, path: str, context: ReleaseContext, *, frozen: bool) -> list[str]:
    errors: list[str] = []
    heading = ""
    preceding: list[str] = []
    for number, line in active_lines(text, include_code=True):
        if re.match(r"^#{1,6}\s", line):
            heading = line
            preceding = []
        source = re.search(rf"\bskills\s+add\s+{REPO_PATTERN}(?:#([^\s`]+))?", line)
        if source and (source.group(1) is None or source.group(1) == context.target):
            if (frozen or not context.install_verified) and not re.search(r"template|模板", heading + "\n" + "\n".join(preceding[-4:]), re.I):
                errors.append(f"[FUTURE_INSTALL_TEMPLATE] {path}:{number}: mark the target/default installation command as a template until its released source is verified")
        preceding.append(line)
    return errors


def publication_claim(statement: str) -> bool:
    return bool(re.search(r"(?:is|was|has been|formally|already) published|published and attested|"
                          r"(?:publication[^:：|\n]*|(?:GitHub Release\s*)?发布(?:结果|状态)?)\s*[:：|]\s*(?:PASS|SUCCESS|VERIFIED|通过|成功)|"
                          r"已(?:正式|公开)?发布|已公开", statement, re.I))


def document_links(text: str, path: str, context: ReleaseContext, files: set[str] | None) -> list[str]:
    errors: list[str] = []
    for number, line in active_lines(text):
        for label, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", line):
            target = target.strip().strip("<>")
            parsed = urlparse(target)
            labels = set(re.findall(VERSION, label))
            linked_release = re.search(rf"(?:/releases/tag/|/releases/|/blob/)({VERSION})(?:/|$)", parsed.path)
            if linked_release and labels and labels != {linked_release.group(1)}:
                errors.append(f"[RELEASE_LINK_VERSION] {path}:{number}: label {sorted(labels)} differs from {target}")
            if linked_release and re.search(r"RELEASE_(?:NOTES|MANIFEST|RECEIPT)", target) and linked_release.group(1) != context.target:
                prose = re.sub(r"\[[^\]]+\]\([^)]+\)", "", line)
                named_version = linked_release.group(1) in re.findall(VERSION, prose)
                if not named_version and not re.search(r"previous|earlier|historical|history|rollback|上(?:一|个)|此前|历史|回退", label + " " + line, re.I):
                    errors.append(f"[RELEASE_LINK_VERSION] {path}:{number}: release artifact points to {linked_release.group(1)}, expected {context.target}")
            if parsed.scheme or target.startswith("#"):
                continue
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(path), unquote(parsed.path)))
            if files is not None and resolved not in files:
                errors.append(f"[DOCUMENT_LINK] {path}:{number}: {target} resolves to {resolved}, absent from {context.revision or 'checked tree'}")
    return errors


def check_release_documents(documents: Mapping[str, str], context: ReleaseContext, files: set[str] | None = None) -> list[str]:
    """Check the complete public snapshot and its bilingual release Notes/Manifest."""
    errors: list[str] = []
    files = files if files is not None else set(documents)
    current = context.stage == "attested" and context.mode == "current"
    if current and context.current_stable != context.target:
        errors.append(f"[CURRENT_RELEASE_TARGET] current release target {context.target} differs from confirmed stable {context.current_stable}; use historical mode to audit an older release")
    for path in PUBLIC_RELEASE_DOCS:
        if path not in documents:
            errors.append(f"[SNAPSHOT_MISSING] {path}: missing from {context.revision or 'checked tree'}")
        else:
            errors.extend(validate_document(documents[path], path, "current" if current else "snapshot", context))
            errors.extend(document_links(documents[path], path, context, files))
    prefix = f"docs/evidence/releases/{context.target}"
    for artifact, kind in (("RELEASE_NOTES", "notes"), ("RELEASE_MANIFEST", "manifest")):
        for suffix in ("", ".zh-CN"):
            path = f"{prefix}/{artifact}{suffix}.md"
            if path not in documents:
                errors.append(f"[RELEASE_DOCUMENT_MISSING] {path}: missing from {context.revision or 'checked tree'}")
            else:
                if current and kind == "notes":
                    errors.extend(validate_document(documents[path], path, "current-notes", context))
                elif not current:
                    errors.extend(validate_document(documents[path], path, kind, context))
                errors.extend(document_links(documents[path], path, context, files))
    return errors
