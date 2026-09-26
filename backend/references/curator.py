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
# Annotation field map
# =========================================================

# Preferred path first, older-schema fallbacks afterward.
#
# Important:
# We deliberately do NOT search arbitrary nested JSON keys.
# A field with the same name can mean something different
# depending on where it appears.
FIELD_PATHS: dict[str, list[str]] = {
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


# =========================================================
# Annotation extraction
# =========================================================

def _read_path(
    data: dict[str, Any],
    dotted_path: str,
) -> Any | None:
    """
    Read a trusted dotted path from an annotation dictionary.
    """

    current: Any = data

    for part in dotted_path.split("."):
        if not isinstance(current, dict):
            return None

        if part not in current:
            return None

        current = current[part]

    return current


def get_annotation_value(
    record: ReferenceRecord,
    field: str,
) -> Any | None:
    """
    Retrieve one design dimension from a reference annotation.

    Newer codebook paths are preferred, with explicit legacy
    fallbacks where appropriate.
    """

    if record.annotation is None:
        return None

    paths = FIELD_PATHS.get(field, [])

    for path in paths:
        value = _read_path(record.annotation, path)

        if value is not None:
            return value

    return None


# =========================================================
# Deterministic matching
# =========================================================

def _normalize(value: Any) -> str:
    """
    Convert annotation text into a comparison-friendly form.

    This is deliberately lightweight. We are not trying to turn
    prose annotations into a new ontology automatically.
    """

    if isinstance(value, list):
        value = " ".join(str(item) for item in value)

    text = str(value).lower()
    text = re.sub(r"[_/-]+", " ", text)
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def _token_set(value: Any) -> set[str]:
    return set(_normalize(value).split())


def _match_score(
    observed: Any,
    target: Any,
) -> float:
    """
    Compare a requested annotation value with an observed value.

    Exact normalized match:
        strongest

    One phrase containing the other:
        strong

    Token overlap:
        weaker fallback for legacy prose values such as
        "distributed narrative recognition" versus
        "distributed_narrative".
    """

    observed_text = _normalize(observed)
    target_text = _normalize(target)

    if not observed_text or not target_text:
        return 0.0

    if observed_text == target_text:
        return 3.0

    observed_tokens = _token_set(observed)
    target_tokens = _token_set(target)

    # Phrase containment is strong evidence only when both sides
    # contain enough information to be meaningfully specific.
    #
    # For example:
    #   "distributed narrative recognition"
    #   versus
    #   "distributed narrative"
    # is a strong match.
    #
    # But:
    #   "distributed"
    #   versus
    #   "distributed narrative"
    # should not receive the same score.
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


def _matched_fields(
    record: ReferenceRecord,
    focus: ReferenceFocus,
) -> dict[str, Any]:
    """
    Return the requested dimensions that are actually available
    for this reference.
    """

    result: dict[str, Any] = {}

    for field in focus.focus_fields:
        value = get_annotation_value(record, field)

        if value is not None:
            result[field] = value

    return result


def _precedent_score(
    record: ReferenceRecord,
    focus: ReferenceFocus,
) -> float:
    """
    Score how well an annotated reference supports an already
    hypothesized design direction.
    """

    score = 0.0

    for field in focus.focus_fields:
        observed = get_annotation_value(record, field)

        if observed is None:
            continue

        # Small reward for simply having evidence on this dimension.
        score += 0.25

        if field in focus.target_values:
            score += _match_score(
                observed,
                focus.target_values[field],
            )

    return score


def _contrast_score(
    record: ReferenceRecord,
    focus: ReferenceFocus,
) -> float:
    """
    Prefer references that contain evidence on the requested
    dimensions but differ from the current tentative values.
    """

    score = 0.0

    for field in focus.focus_fields:
        observed = get_annotation_value(record, field)

        if observed is None:
            continue

        score += 0.5

        if field in focus.target_values:
            similarity = _match_score(
                observed,
                focus.target_values[field],
            )

            if similarity == 0.0:
                score += 2.0
            elif similarity < 1.0:
                score += 1.0

    return score


def _exploratory_score(
    record: ReferenceRecord,
    focus: ReferenceFocus,
) -> float:
    """
    Exploratory retrieval rewards annotation coverage rather than
    similarity to a choice that has not yet been made.
    """

    return float(
        sum(
            get_annotation_value(record, field) is not None
            for field in focus.focus_fields
        )
    )


# =========================================================
# Public curator
# =========================================================

def curate_references(
    focus: ReferenceFocus,
    records: list[ReferenceRecord] | None = None,
) -> ReferencePacket:
    """
    Select a small reference packet for one design question.

    Modes:
    - exploratory:
        show well-annotated examples relevant to the dimensions
        currently under consideration;

    - precedent:
        retrieve examples supporting tentative design choices;

    - contrast:
        retrieve examples that differ along those same dimensions.

    The curator does not invent a design decision.
    """

    if records is None:
        records = load_reference_registry()

    annotated = [
        record
        for record in records
        if record.annotation is not None
    ]

    scored: list[
        tuple[float, ReferenceRecord, dict[str, Any]]
    ] = []

    for record in annotated:
        matched = _matched_fields(record, focus)

        if not matched:
            continue

        if focus.mode == ReferenceMode.precedent:
            score = _precedent_score(record, focus)

        elif focus.mode == ReferenceMode.contrast:
            score = _contrast_score(record, focus)

        else:
            score = _exploratory_score(record, focus)

        scored.append(
            (
                score,
                record,
                matched,
            )
        )

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
            matched_fields=matched,
            teaching_focus=focus.purpose,
            score=score,
        )
        for score, record, matched in selected
    ]

    return ReferencePacket(
        focus=focus,
        references=matches,
        teaching_notes=[
            (
                "Use these references as visual precedent and evidence, "
                "not as scenes to copy."
            ),
            (
                "Inspect the requested design dimensions while preserving "
                "the new candidate's independent semantic identity."
            ),
        ],
    )
