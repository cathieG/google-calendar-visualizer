from __future__ import annotations
import re
from typing import Any
from planning.schemas import (
    ReferenceFocus,
    ReferenceMatch,
    ReferenceMode,
    ReferencePacket,
    ReferenceRecord,
)

from references.registry import load_reference_registry


# =========================================================
# Legacy annotation compatibility


# =========================================================
# Rich study files were created across several schema generations.
# These are the only trusted fallback paths used to read them.
# Runtime annotations do not use this map; they already expose
# canonical top-level fields.
LEGACY_FIELD_PATHS: dict[str, list[str]] = {
    "representation_strategy": [
        "representation_and_recognition.representation_strategy",
        "derived_observations.representation_strategy",
    ],
    "recognition_structure": [
        "representation_and_recognition.recognition_structure",
        "semantic_analysis.recognition_structure",
    ],
    "recognition_specificity": [
        "representation_and_recognition.recognition_specificity",
        "derived_observations.recognition_specificity",
    ],
    "human_presence": [
        "people_and_social_structure.human_presence",
    ],
    "human_role": [
        "people_and_social_structure.human_role",
        "derived_observations.human_role",
    ],
    "environment_strategy": [
        "environment_and_space.environment_strategy",
        "derived_observations.environment_strategy",
        "semantic_analysis.environment_strategy",
    ],
    "temporal_focus": [
        "event_and_semantic_logic.temporal_focus",
    ],
    "view_angle": [
        "environment_and_space.view_angle",
    ],
    "scale_source": [
        "environment_and_space.scale_source",
        "derived_observations.scale_source",
    ],
    "depth": [
        "derived_observations.depth",
    ],
    "cropping": [
        "derived_observations.cropping",
    ],
}


def _read_path(
    data: dict[str, Any],
    dotted_path: str,
) -> Any | None:
    """Read one trusted dotted path from an annotation dictionary."""
    current: Any = data
    for part in dotted_path.split("."):
        if not isinstance(current, dict):
            return None
        if part not in current:
            return None
        current = current[part]
    return current


def get_runtime_value(
    record: ReferenceRecord,
    field: str,
) -> Any | None:
    """Read one canonical field from a human-reviewed runtime annotation."""
    if record.runtime_annotation is None:
        return None
    return record.runtime_annotation.get(field)


def get_legacy_value(
    record: ReferenceRecord,
    field: str,
) -> Any | None:
    """Read one field from a rich study using trusted legacy paths."""
    if record.annotation is None:
        return None
    for path in LEGACY_FIELD_PATHS.get(field, []):
        value = _read_path(record.annotation, path)
        if value is not None:
            return value
    return None


def get_annotation_value(
    record: ReferenceRecord,
    field: str,
) -> Any | None:
    """
    Compatibility helper: prefer canonical runtime evidence, then fall
    back to a rich legacy study value.
    Core retrieval logic should normally choose its annotation source
    explicitly rather than relying on this fallback.
    """
    runtime_value = get_runtime_value(record, field)
    if runtime_value is not None:
        return runtime_value
    return get_legacy_value(record, field)


# =========================================================
# Matching helpers


# =========================================================


def _canonical_match(
    observed: Any,
    target: Any,
) -> bool:
    """Canonical runtime values are categorical and match exactly."""
    return observed == target


def _normalize(value: Any) -> str:
    """Convert legacy annotation text into a comparison-friendly form."""
    if isinstance(value, list):
        value = " ".join(str(item) for item in value)
    text = str(value).lower()
    text = re.sub(r"[_/-]+", " ", text)
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _token_set(value: Any) -> set[str]:
    return set(_normalize(value).split())


def _legacy_match_score(
    observed: Any,
    target: Any,
) -> float:
    """
    Compare a legacy study value with a target value.
    Exact normalized match is strongest, phrase containment is strong,
    and token overlap is a weaker compatibility fallback for prose-like
    legacy annotations.
    """
    observed_text = _normalize(observed)
    target_text = _normalize(target)
    if not observed_text or not target_text:
        return 0.0
    if observed_text == target_text:
        return 3.0
    observed_tokens = _token_set(observed)
    target_tokens = _token_set(target)
    if (
        len(observed_tokens) >= 2
        and len(target_tokens) >= 2
        and (
            target_text in observed_text
            or observed_text in target_text
        )
    ):
        return 2.0
    if not observed_tokens or not target_tokens:
        return 0.0
    overlap = len(observed_tokens & target_tokens)
    union = len(observed_tokens | target_tokens)
    if overlap == 0:
        return 0.0
    return overlap / union


# =========================================================
# Evidence extraction


# =========================================================


def _source_name(focus: ReferenceFocus) -> str:
    """Return the configured annotation-source value as a plain string."""
    source = focus.annotation_source
    return getattr(source, "value", str(source))


def _records_for_source(
    records: list[ReferenceRecord],
    focus: ReferenceFocus,
) -> list[ReferenceRecord]:
    """Filter records according to the query's annotation-source policy."""
    source = _source_name(focus)
    if source == "runtime":
        return [
            record
            for record in records
            if record.runtime_annotation is not None
        ]
    if source == "legacy":
        return [
            record
            for record in records
            if record.annotation is not None
        ]
    if source == "runtime_then_legacy":
        return [
            record
            for record in records
            if (
                record.runtime_annotation is not None
                or record.annotation is not None
            )
        ]
    raise ValueError(
        f"Unsupported annotation_source: {source}"
    )


def _extract_evidence(
    record: ReferenceRecord,
    focus: ReferenceFocus,
) -> dict[str, Any]:
    """Extract the requested dimensions from the configured source."""
    source = _source_name(focus)
    evidence: dict[str, Any] = {}
    for field in focus.focus_fields:
        if source == "runtime":
            value = get_runtime_value(record, field)
        elif source == "legacy":
            value = get_legacy_value(record, field)
        elif source == "runtime_then_legacy":
            value = get_runtime_value(record, field)
            if value is None:
                value = get_legacy_value(record, field)
        else:
            raise ValueError(
                f"Unsupported annotation_source: {source}"
            )
        if value is not None:
            evidence[field] = value
    return evidence


# =========================================================
# Precedent eligibility and ranking


# =========================================================
IDENTITY_FIELDS = (
    "representation_strategy",
    "recognition_structure",
)
CANONICAL_PRECEDENT_WEIGHTS = {
    "representation_strategy": 3.0,
    "recognition_structure": 3.0,
    "environment_strategy": 2.0,
}


def _target_matches(
    observed: Any,
    target: Any,
    *,
    canonical: bool,
) -> bool:
    if canonical:
        return _canonical_match(observed, target)
    return _legacy_match_score(observed, target) > 0.0


def _precedent_eligible(
    evidence: dict[str, Any],
    focus: ReferenceFocus,
) -> bool:
    """
    Decide whether a reference is relevant enough to be considered as
    a precedent.
    When representation or recognition targets are present, at least
    one of those identity dimensions must match. Otherwise, at least one
    targeted dimension must match.
    """
    canonical = _source_name(focus) == "runtime"
    identity_targets = [
        field
        for field in IDENTITY_FIELDS
        if field in focus.target_values
    ]
    eligibility_fields = (
        identity_targets
        if identity_targets
        else list(focus.target_values)
    )
    if not eligibility_fields:
        return bool(evidence)
    for field in eligibility_fields:
        observed = evidence.get(field)
        if observed is None:
            continue
        if _target_matches(
            observed,
            focus.target_values[field],
            canonical=canonical,
        ):
            return True
    return False


def _canonical_precedent_score(
    evidence: dict[str, Any],
    focus: ReferenceFocus,
) -> float:
    """Rank eligible canonical precedents by additional exact matches."""
    score = 0.0
    for field, target in focus.target_values.items():
        observed = evidence.get(field)
        if observed is None:
            continue
        if _canonical_match(observed, target):
            score += CANONICAL_PRECEDENT_WEIGHTS.get(
                field,
                1.0,
            )
    for field in focus.focus_fields:
        if field in focus.target_values:
            continue
        if field in evidence:
            score += 0.1
    return score


def _legacy_precedent_score(
    evidence: dict[str, Any],
    focus: ReferenceFocus,
) -> float:
    """Rank eligible legacy precedents using the existing fuzzy match."""
    score = 0.0
    for field, target in focus.target_values.items():
        observed = evidence.get(field)
        if observed is None:
            continue
        score += _legacy_match_score(
            observed,
            target,
        )
    for field in focus.focus_fields:
        if field in focus.target_values:
            continue
        if field in evidence:
            score += 0.1
    return score


def _precedent_score(
    evidence: dict[str, Any],
    focus: ReferenceFocus,
) -> float:
    if _source_name(focus) == "runtime":
        return _canonical_precedent_score(
            evidence,
            focus,
        )
    return _legacy_precedent_score(
        evidence,
        focus,
    )


# =========================================================
# Exploratory and contrast ranking


# =========================================================


def _contrast_score(
    evidence: dict[str, Any],
    focus: ReferenceFocus,
) -> float:
    """
    Reward references that contain evidence on the requested dimensions
    and differ from supplied tentative target values.
    """
    score = 0.0
    canonical = _source_name(focus) == "runtime"
    for field in focus.focus_fields:
        observed = evidence.get(field)
        if observed is None:
            continue
        score += 0.5
        if field not in focus.target_values:
            continue
        target = focus.target_values[field]
        if canonical:
            if not _canonical_match(observed, target):
                score += 2.0
            continue
        similarity = _legacy_match_score(
            observed,
            target,
        )
        if similarity == 0.0:
            score += 2.0
        elif similarity < 1.0:
            score += 1.0
    return score


def _exploratory_score(
    evidence: dict[str, Any],
    focus: ReferenceFocus,
) -> float:
    """Reward useful annotation coverage before a direction is chosen."""
    return float(
        sum(
            field in evidence
            for field in focus.focus_fields
        )
    )


def _exploratory_diversity_gain(
    evidence: dict[str, Any],
    focus: ReferenceFocus,
    seen_values: dict[str, set[str]],
) -> int:
    """
    Count how many new values this reference would add across the
    exploratory focus fields.
    """
    gain = 0
    for field in focus.focus_fields:
        if field not in evidence:
            continue
        value_key = _normalize(evidence[field])
        if value_key not in seen_values[field]:
            gain += 1
    return gain


def _select_exploratory(
    scored: list[
        tuple[float, ReferenceRecord, dict[str, Any]]
    ],
    focus: ReferenceFocus,
) -> list[
    tuple[float, ReferenceRecord, dict[str, Any]]
]:
    """
    Select exploratory references for both annotation coverage and
    diversity across the requested design dimensions.
    """
    if not scored:
        return []
    remaining = list(scored)
    selected: list[
        tuple[float, ReferenceRecord, dict[str, Any]]
    ] = []
    seen_values: dict[str, set[str]] = {
        field: set()
        for field in focus.focus_fields
    }
    while (
        remaining
        and len(selected) < focus.max_references
    ):
        if not selected:
            # Start with the strongest overall annotation coverage.
            remaining.sort(
                key=lambda item: (
                    -item[0],
                    item[1].concept.lower(),
                )
            )
        else:
            # After the first reference, prefer examples that introduce
            # new values on the dimensions being explored.
            remaining.sort(
                key=lambda item: (
                    -_exploratory_diversity_gain(
                        item[2],
                        focus,
                        seen_values,
                    ),
                    -item[0],
                    item[1].concept.lower(),
                )
            )
            best_gain = _exploratory_diversity_gain(
                remaining[0][2],
                focus,
                seen_values,
            )
            # Two references are enough when no remaining example adds
            # any new exploratory information.
            if best_gain == 0 and len(selected) >= 2:
                break
        chosen = remaining.pop(0)
        selected.append(chosen)
        evidence = chosen[2]
        for field in focus.focus_fields:
            if field not in evidence:
                continue
            seen_values[field].add(
                _normalize(evidence[field])
            )
    return selected


# =========================================================
# Public curator


# =========================================================


def curate_references(
    focus: ReferenceFocus,
    records: list[ReferenceRecord] | None = None,
) -> ReferencePacket:
    """
    Select a small reference packet for one design question.
    The focus determines:
    - which annotation source is allowed;
    - which dimensions are relevant;
    - whether the query seeks exploration, precedent, or contrast.
    The curator retrieves and ranks evidence. It does not invent design
    decisions.
    """
    if records is None:
        records = load_reference_registry()
    source_records = _records_for_source(
        records,
        focus,
    )
    scored: list[
        tuple[float, ReferenceRecord, dict[str, Any]]
    ] = []
    for record in source_records:
        evidence = _extract_evidence(
            record,
            focus,
        )
        if not evidence:
            continue
        if focus.mode == ReferenceMode.precedent:
            if not _precedent_eligible(
                evidence,
                focus,
            ):
                continue
            score = _precedent_score(
                evidence,
                focus,
            )
        elif focus.mode == ReferenceMode.contrast:
            score = _contrast_score(
                evidence,
                focus,
            )
        else:
            score = _exploratory_score(
                evidence,
                focus,
            )
        scored.append(
            (
                score,
                record,
                evidence,
            )
        )
    if focus.mode == ReferenceMode.exploratory:
        selected = _select_exploratory(
            scored,
            focus,
        )
    else:
        scored.sort(
            key=lambda item: (
                -item[0],
                item[1].concept.lower(),
            )
        )
        selected = scored[: focus.max_references]
    matches = [
        ReferenceMatch(
            reference_id=record.reference_id,
            concept=record.concept,
            image_path=record.rendered_path,
            # Schema name retained for compatibility. These are the
            # evidence fields used during retrieval, not necessarily
            # fields that exactly matched a target.
            matched_fields=evidence,
            teaching_focus=focus.purpose,
            score=score,
        )
        for score, record, evidence in selected
    ]
    if focus.mode == ReferenceMode.exploratory:
        teaching_notes = [
            (
                "Use these references as visual evidence, "
                "not as scenes to copy."
            ),
            (
                "Compare how the references handle the requested design "
                "dimensions. Treat their differences as possibilities, "
                "not recommendations."
            ),
        ]
    else:
        teaching_notes = [
            (
                "Use these references as visual precedent and evidence, "
                "not as scenes to copy."
            ),
            (
                "Inspect the requested design dimensions while preserving "
                "the new candidate's independent semantic identity."
            ),
        ]
    return ReferencePacket(
        focus=focus,
        references=matches,
        teaching_notes=teaching_notes,
    )
# Temporary compatibility re-export while existing callers migrate to
# references.focus_builders.
from references.focus_builders import build_art_direction_focus  # noqa: E402,F401
