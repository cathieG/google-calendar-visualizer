from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any
from pydantic import BaseModel
from config import TEXT_MODEL
from openai_client import get_openai_client
from planning.schemas import (
    ConceptBrief,
    ReferenceFocus,
    ReferenceMatch,
    ReferenceMode,
    ReferencePacket,
    ReferenceRecord,
)
from references.registry import load_reference_registry

# =========================================================
# Stage A: semantic reference selection
# =========================================================

REFERENCE_CONCEPT_BRIEFS_PATH = (
    Path(__file__).parent
    / "google_calendar"
    / "stageA_reference.json"
)

class SemanticReferenceChoice(BaseModel):
    reference_id: str
    reason: str

class SemanticReferenceSelection(BaseModel):
    references: list[SemanticReferenceChoice]

def _semantic_brief_view(
    brief: ConceptBrief,
) -> dict[str, Any]:
    """Keep only ConceptBrief fields useful for semantic comparison."""
    return {
        "core_concept": brief.core_concept,
        "known_details": brief.known_details,
        "general_associations": brief.general_associations,
        "open_choices": brief.open_choices,
        "protected_unknowns": brief.protected_unknowns,
        "promising_semantic_cues": brief.promising_semantic_cues,
    }

def _load_reference_concept_briefs(
    path: Path = REFERENCE_CONCEPT_BRIEFS_PATH,
) -> list[dict[str, Any]]:
    """Load ConceptBriefs for the small deeply studied reference corpus."""
    if not path.exists():
        raise FileNotFoundError(
            f"Reference ConceptBrief catalog not found: {path}"
        )
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(
            "reference_concept_briefs.json must contain a JSON list."
        )
    results: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, entry in enumerate(data, start=1):
        if not isinstance(entry, dict):
            raise ValueError(
                f"Reference ConceptBrief entry {index} must be a JSON object."
            )
        reference_id = entry.get("reference_id")
        concept = entry.get("concept")
        brief_data = entry.get("concept_brief")
        if not reference_id or not concept or not brief_data:
            raise ValueError(
                f"Reference ConceptBrief entry {index} must contain "
                "reference_id, concept, and concept_brief."
            )
        if reference_id in seen_ids:
            raise ValueError(
                "Duplicate reference_id in ConceptBrief catalog: "
                f"{reference_id!r}"
            )
        seen_ids.add(reference_id)
        brief = ConceptBrief.model_validate(brief_data)
        results.append(
            {
                "reference_id": reference_id,
                "concept": concept,
                "concept_brief": _semantic_brief_view(brief),
            }
        )
    return results

def curate_semantic_references(
    concept_brief: ConceptBrief,
    records: list[ReferenceRecord] | None = None,
) -> ReferencePacket:
    """
    Stage A.
    Select deeply studied references because their underlying concepts
    are semantically related to the current concept. Selection is based
    on ConceptBrief-to-ConceptBrief comparison, not visual annotations.
    After selection, attach each reference's full rich annotation and
    rendered image path for the Creative Planner to study.
    """
    if records is None:
        records = load_reference_registry()
    reference_briefs = _load_reference_concept_briefs()
    studied_records = {
        record.reference_id: record
        for record in records
        if record.annotation is not None
    }
    available_briefs = [
        entry
        for entry in reference_briefs
        if entry["reference_id"] in studied_records
    ]
    if len(available_briefs) < 3:
        raise ValueError(
            "Stage A requires at least 3 deeply studied references "
            "with ConceptBriefs."
        )
    current_brief_json = json.dumps(
        _semantic_brief_view(concept_brief),
        indent=2,
        ensure_ascii=False,
    )
    reference_briefs_json = json.dumps(
        available_briefs,
        indent=2,
        ensure_ascii=False,
    )
    client = get_openai_client()
    response = client.responses.parse(
        model=TEXT_MODEL,
        input=[
            {
                "role": "system",
                "content": """
You select semantic reference examples for the Creative Planner of a
calendar illustration system.

The Creative Planner has not yet chosen a visual scene.

Your ONLY job is to identify the existing deeply studied reference
concepts that are most semantically relevant to the current concept.
Compare ConceptBrief to ConceptBrief.

Judge semantic relatedness primarily from:
- core_concept,
- known_details,
- general_associations.

You may use:
- open_choices,
- promising_semantic_cues
as supporting semantic evidence， and no other fields.

Semantic relatedness may arise from shared:
- activity,
- purpose,
- real-world setting,
- participants,
- interactions,
- objects,
- experience,
- occasion,
- or situation.

Do NOT choose references because of:
- composition,
- representation strategy,
- human presence,
- viewpoint,
- cropping,
- depth,
- scale,
- color,
- rendering style,
- annotation completeness,
- or annotation diversity.

Do NOT decide how the new concept should be illustrated.
Simply select the strongest semantic precedents. Their detailed visual
annotations and images will be studied only AFTER selection.
Return exactly three references in descending order of
semantic usefulness.
""".strip(),
            },
            {
                "role": "user",
                "content": f"""
CURRENT CONCEPT
===============
{current_brief_json}
AVAILABLE DEEPLY STUDIED REFERENCES
===================================
{reference_briefs_json}
TASK
====
Select exactly 3 references whose ConceptBriefs are
most semantically useful for understanding the current concept.
Give a brief reason for each selection.
""".strip(),
            },
        ],
        text_format=SemanticReferenceSelection,
    )
    selection = response.output_parsed
    selected_ids = [
        choice.reference_id
        for choice in selection.references
    ]
    if len(selected_ids) != 3:
        raise ValueError(
            "Stage-A selector must return exactly 3 references."
        )
    if len(set(selected_ids)) != len(selected_ids):
        raise ValueError(
            "Stage-A selector returned duplicate reference IDs."
        )
    valid_ids = {
        entry["reference_id"]
        for entry in available_briefs
    }
    unknown_ids = set(selected_ids) - valid_ids
    if unknown_ids:
        raise ValueError(
            "Stage-A selector returned unknown reference IDs: "
            f"{sorted(unknown_ids)}"
        )
    focus = ReferenceFocus(
        stage="creative_planning",
        mode=ReferenceMode.exploratory,
        focus_fields=[],
        purpose=(
            "Study semantically related Google Calendar concepts to "
            "understand how related meanings have been translated into "
            "visual illustrations."
        ),
        max_references=3,
    )
    matches: list[ReferenceMatch] = []
    for choice in selection.references:
        record = studied_records[choice.reference_id]
        matches.append(
            ReferenceMatch(
                reference_id=record.reference_id,
                concept=record.concept,
                image_path=record.rendered_path,
                # Schema name retained for compatibility. Stage A now
                # carries the complete rich study annotation here.
                matched_fields=record.annotation or {},
                teaching_focus=choice.reason,
            )
        )
    return ReferencePacket(
        focus=focus,
        references=matches,
        teaching_notes=[
            (
                "These references were selected for semantic relevance "
                "to the current concept."
            ),
            (
                "Study their images and detailed annotations for useful "
                "design evidence, but do not copy their scenes."
            ),
            (
                "The references illustrate how related concepts were "
                "solved; they do not prescribe the representation of "
                "the current concept."
            ),
        ],
    )

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
# Contrast ranking
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

# =========================================================
# Public Stage-B curator
# =========================================================

def curate_references(
    focus: ReferenceFocus,
    records: list[ReferenceRecord] | None = None,
) -> ReferencePacket:
    """
    Stage B.
    Retrieve annotation-based precedents or contrasts for an already
    planned candidate. Stage-A semantic retrieval is handled separately
    by curate_semantic_references().
    """
    if focus.mode == ReferenceMode.exploratory:
        raise ValueError(
            "Exploratory Stage-A retrieval is semantic now. "
            "Use curate_semantic_references(concept_brief) instead."
        )
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
            raise ValueError(
                f"Unsupported Reference-B mode: {focus.mode}"
            )
        scored.append(
            (
                score,
                record,
                evidence,
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
            # Schema name retained for compatibility. These are the
            # evidence fields used during retrieval, not necessarily
            # fields that exactly matched a target.
            matched_fields=evidence,
            teaching_focus=focus.purpose,
            score=score,
        )
        for score, record, evidence in selected
    ]
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
