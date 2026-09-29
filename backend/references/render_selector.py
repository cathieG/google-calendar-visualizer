from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, Field

from config import TEXT_MODEL
from openai_client import get_openai_client
from planning.schemas import FinalScenePlan
from references.render_registry import (
    RenderReferenceRecord,
    load_render_reference_registry,
)


# =========================================================
# Selector output schemas
# =========================================================

class RenderEvidenceMatch(BaseModel):
    """
    One visual property shared by the finished FinalScenePlan and a
    verified renderer reference.

    plan_fields and annotation_fields are an audit trail. They must
    point to real fields in the supplied plan and annotation.
    """

    demonstrates: str

    plan_fields: list[str] = Field(
        default_factory=list
    )

    annotation_fields: list[str] = Field(
        default_factory=list
    )


class RenderReferenceChoice(BaseModel):
    """
    One reference selected by the Stage-C reasoning call.
    """

    reference_id: str

    evidence: list[RenderEvidenceMatch] = Field(
        default_factory=list
    )


class RenderReferenceSelection(BaseModel):
    """
    Raw structured output from the Stage-C selector.
    """

    references: list[RenderReferenceChoice] = Field(
        default_factory=list
    )


# =========================================================
# Validated downstream packet
# =========================================================

class ValidatedRenderEvidence(BaseModel):
    """
    Evidence match after Python verifies every cited field.

    The resolved values are retained for debugging and inspection.
    """

    demonstrates: str

    plan_evidence: dict[str, Any]

    annotation_evidence: dict[str, Any]


class RendererReferenceUse(BaseModel):
    """
    One selected image plus exactly what it should demonstrate.
    """

    reference_id: str
    concept: str
    image_path: str

    evidence: list[ValidatedRenderEvidence]


class RendererReferencePacket(BaseModel):
    """
    Final Stage-C packet.

    It may contain zero references. References are never added merely
    to satisfy a target count.
    """

    references: list[RendererReferenceUse] = Field(
        default_factory=list
    )


# =========================================================
# Annotation projection
# =========================================================

def _compact_annotation(
    record: RenderReferenceRecord,
) -> dict[str, Any]:
    """
    Keep the visually useful, human-verified portion of a rich
    annotation while preserving its original field paths.

    The selector does not need source-study prose or transport metadata.
    """

    annotation = record.annotation

    whole_scene = annotation.get(
        "whole_scene",
        {},
    )

    humans = annotation.get(
        "humans",
        {},
    )

    objects = annotation.get(
        "objects",
        {},
    )

    relationships = annotation.get(
        "relationships",
        {},
    )

    return {
        "reference_id": record.reference_id,
        "concept": record.concept,

        "whole_scene": {
            "composition": whole_scene.get(
                "composition"
            ),
            "background": whole_scene.get(
                "background"
            ),
            "environment": whole_scene.get(
                "environment"
            ),
            "viewpoint": whole_scene.get(
                "viewpoint"
            ),
            "perspective": whole_scene.get(
                "perspective"
            ),
            "depth": whole_scene.get(
                "depth"
            ),
            "cropping": whole_scene.get(
                "cropping"
            ),
            "scale": whole_scene.get(
                "scale"
            ),
        },

        "rendering": annotation.get(
            "rendering"
        ),

        "humans": {
            "presence": humans.get(
                "presence"
            ),
            "represented_person_count": humans.get(
                "represented_person_count"
            ),
            "fine_inventory": humans.get(
                "fine_inventory"
            ),
            "group_observations": humans.get(
                "group_observations"
            ),
        },

        "objects": {
            "primary_recognition_cues": objects.get(
                "primary_recognition_cues"
            ),
            "secondary_recognition_cues": objects.get(
                "secondary_recognition_cues"
            ),
            "symbolic_or_informational_cues": objects.get(
                "symbolic_or_informational_cues"
            ),
            "notable_omissions": objects.get(
                "notable_omissions"
            ),
            "image_verified_inventory": objects.get(
                "image_verified_inventory"
            ),
        },

        "relationships": {
            "human_semantic_role": relationships.get(
                "human_semantic_role"
            ),
            "motion_present": relationships.get(
                "motion_present"
            ),
            "primary_motion_cue": relationships.get(
                "primary_motion_cue"
            ),
            "secondary_motion_cues": relationships.get(
                "secondary_motion_cues"
            ),
            "image_verified_relations": relationships.get(
                "image_verified_relations"
            ),
        },
    }


# =========================================================
# Path validation
# =========================================================

_PATH_PART_RE = re.compile(
    r"([^\[\]]+)|\[(\d+)\]"
)


def _path_tokens(
    path: str,
) -> list[str | int]:
    """
    Convert:

        humans.fine_inventory[0].hands_visible

    into:

        ["humans", "fine_inventory", 0, "hands_visible"]
    """

    if not path.strip():
        raise ValueError(
            "Evidence path cannot be empty."
        )

    tokens: list[str | int] = []

    for segment in path.split("."):
        matches = list(
            _PATH_PART_RE.finditer(
                segment
            )
        )

        if not matches:
            raise ValueError(
                f"Invalid evidence path segment: {segment}"
            )

        reconstructed = "".join(
            match.group(0)
            for match in matches
        )

        if reconstructed != segment:
            raise ValueError(
                f"Invalid evidence path syntax: {path}"
            )

        for match in matches:
            key = match.group(1)
            index = match.group(2)

            if key is not None:
                tokens.append(
                    key
                )
            else:
                tokens.append(
                    int(index)
                )

    return tokens


def _resolve_path(
    data: Any,
    path: str,
) -> Any:
    """
    Resolve an exact dotted/list-indexed path.

    Raises if the selector cites a field that does not actually exist.
    """

    current = data

    for token in _path_tokens(path):
        if isinstance(
            token,
            str,
        ):
            if not isinstance(
                current,
                dict,
            ):
                raise KeyError(
                    f"Cannot access key '{token}' "
                    f"while resolving '{path}'."
                )

            if token not in current:
                raise KeyError(
                    f"Field '{path}' does not exist."
                )

            current = current[token]

        else:
            if not isinstance(
                current,
                list,
            ):
                raise KeyError(
                    f"Cannot access list index [{token}] "
                    f"while resolving '{path}'."
                )

            if (
                token < 0
                or token >= len(current)
            ):
                raise KeyError(
                    f"List index out of range in '{path}'."
                )

            current = current[token]

    return current


def _is_empty_evidence(
    value: Any,
) -> bool:
    """
    Null/empty annotation fields cannot substantiate a claim.
    """

    return (
        value is None
        or value == ""
        or value == []
        or value == {}
    )


# =========================================================
# Selection
# =========================================================

def select_renderer_references(
    plan: FinalScenePlan,
    records: list[RenderReferenceRecord] | None = None,
    max_references: int = 4,
) -> RendererReferencePacket:
    """
    Select a small renderer-reference packet after art direction is
    complete.

    The reasoning model finds intersections between:
        1. decisions already present in FinalScenePlan, and
        2. directly observed properties in verified annotations.

    Python then validates every claimed field path.

    Stage C does not redesign the scene.
    """

    if max_references < 1:
        raise ValueError(
            "max_references must be at least 1."
        )

    if records is None:
        records = (
            load_render_reference_registry()
        )

    if not records:
        return RendererReferencePacket()

    plan_data = plan.model_dump(
        mode="json"
    )

    reference_bank = [
        _compact_annotation(
            record
        )
        for record in records
    ]

    client = get_openai_client()

    response = client.responses.parse(
        model=TEXT_MODEL,
        input=[
            {
                "role": "system",
                "content": """
You are the Stage-C renderer-reference selector for a calendar
illustration pipeline.

The visual design is already finished.

You will receive:

1. one complete FinalScenePlan;
2. a small bank of verified annotations describing existing reference
   illustrations.

Your only job is to determine whether any reference images provide
useful visual evidence for executing decisions that ALREADY EXIST in
the FinalScenePlan.


==================================================
NON-NEGOTIABLE BOUNDARY
==================================================

Do not redesign the scene.

Do not introduce a new:
- subject,
- object,
- person,
- action,
- viewpoint,
- crop,
- environment,
- composition,
- relationship,
- color strategy,
- or narrative.

The FinalScenePlan is authoritative.

References support already-made decisions only.


==================================================
WHAT MAKES A REFERENCE USEFUL
==================================================

A reference is useful when one or more directly observed properties in
its annotation overlap with a concrete visual decision already present
in the FinalScenePlan.

Examples of potentially useful overlap include:
- viewpoint,
- camera elevation,
- perspective strength,
- depth construction,
- cropping,
- edge continuation,
- negative-space organization,
- background treatment,
- environment treatment,
- body visibility,
- body orientation,
- sleeve or arm treatment,
- visible hands,
- pose,
- object view or simplification,
- person-object interaction,
- object-object interaction,
- spatial overlap or ordering.

The new scene does NOT need to depict the same activity or concept as
the reference.

A reference may be useful for only one small visual property.


==================================================
ANNOTATION GROUNDING
==================================================

Every evidence claim must be supported on BOTH sides:

1. by one or more exact fields in the FinalScenePlan;
2. by one or more exact fields in that reference's supplied annotation.

For plan_fields:
- cite exact field paths from the supplied FinalScenePlan JSON.

For annotation_fields:
- cite exact field paths from that reference's supplied annotation JSON.

Use dot notation and list indices when needed.

Examples of valid path syntax:

scene_structure.perspective_strategy

whole_scene.viewpoint.vertical

humans.fine_inventory[0].hands_visible

objects.image_verified_inventory[1].view

relationships.image_verified_relations[0]

Do not cite a field that is absent, null, or unrelated to the claim.

Do not infer a property merely from the reference's concept name.


==================================================
STYLE-WIDE PROPERTIES
==================================================

Do not select a reference solely because it demonstrates universal
style properties that already apply to the entire style system, such
as:

- flat color,
- low material realism,
- minimal gradients,
- simplified shapes,
- minimal realistic shadows.

A selected reference should normally provide more specific execution
evidence than those universal properties.

A universal style property may be mentioned only when it accompanies a
more specific useful precedent.


==================================================
SELECTION SIZE AND REDUNDANCY
==================================================

Select the SMALLEST useful set.

Return between zero and the supplied maximum number of references.

Zero is valid.

Do not pad the result.

Every selected reference must contribute at least one genuinely useful
piece of evidence.

If two references demonstrate essentially the same useful properties,
prefer the one whose annotation provides the clearer or more directly
applicable precedent.

A later reference should add useful evidence not already adequately
supplied by the others.

Do not invent approximate support when the bank lacks a useful
precedent.


==================================================
EVIDENCE DESCRIPTION
==================================================

For each selected reference, describe what it demonstrates in concise
renderer-facing language.

The description should answer:

"What specific visual property should the renderer study from this
reference?"

Do not tell the renderer to copy the reference's:
- subject,
- object set,
- exact pose,
- exact layout,
- palette,
- or narrative.

Return only the structured selection.
""".strip(),
            },
            {
                "role": "user",
                "content": f"""
FINAL SCENE PLAN
================

{json.dumps(
    plan_data,
    indent=2,
    ensure_ascii=False,
)}


VERIFIED RENDERER REFERENCE BANK
================================

{json.dumps(
    reference_bank,
    indent=2,
    ensure_ascii=False,
)}


MAXIMUM REFERENCES
==================

{max_references}

Find only annotation-grounded visual precedents for decisions already
present in the FinalScenePlan.
""".strip(),
            },
        ],
        text_format=RenderReferenceSelection,
    )

    selection = response.output_parsed

    # -----------------------------------------------------
    # Validate reference selection.
    # -----------------------------------------------------

    if len(selection.references) > max_references:
        raise ValueError(
            "Stage-C selector returned "
            f"{len(selection.references)} references, "
            f"but the maximum is {max_references}."
        )

    record_by_id = {
        record.reference_id: record
        for record in records
    }

    compact_by_id = {
        item["reference_id"]: item
        for item in reference_bank
    }

    seen_reference_ids: set[str] = set()

    validated_uses: list[
        RendererReferenceUse
    ] = []

    for choice in selection.references:
        reference_id = choice.reference_id

        if reference_id in seen_reference_ids:
            raise ValueError(
                "Stage-C selector returned duplicate "
                f"reference '{reference_id}'."
            )

        seen_reference_ids.add(
            reference_id
        )

        if reference_id not in record_by_id:
            raise ValueError(
                "Stage-C selector returned unknown "
                f"reference '{reference_id}'."
            )

        if not choice.evidence:
            raise ValueError(
                f"Selected reference '{reference_id}' "
                "contains no evidence claims."
            )

        annotation_data = compact_by_id[
            reference_id
        ]

        validated_evidence: list[
            ValidatedRenderEvidence
        ] = []

        for evidence in choice.evidence:
            if not evidence.demonstrates.strip():
                raise ValueError(
                    f"Reference '{reference_id}' contains "
                    "an empty evidence description."
                )

            if not evidence.plan_fields:
                raise ValueError(
                    f"Evidence '{evidence.demonstrates}' "
                    "does not cite a FinalScenePlan field."
                )

            if not evidence.annotation_fields:
                raise ValueError(
                    f"Evidence '{evidence.demonstrates}' "
                    "does not cite an annotation field."
                )

            plan_evidence: dict[
                str,
                Any,
            ] = {}

            for path in evidence.plan_fields:
                value = _resolve_path(
                    plan_data,
                    path,
                )

                if _is_empty_evidence(value):
                    raise ValueError(
                        "Stage-C cited empty FinalScenePlan "
                        f"field '{path}'."
                    )

                plan_evidence[
                    path
                ] = value

            annotation_evidence: dict[
                str,
                Any,
            ] = {}

            for path in evidence.annotation_fields:
                value = _resolve_path(
                    annotation_data,
                    path,
                )

                if _is_empty_evidence(value):
                    raise ValueError(
                        "Stage-C cited empty annotation field "
                        f"'{reference_id}:{path}'."
                    )

                annotation_evidence[
                    path
                ] = value

            validated_evidence.append(
                ValidatedRenderEvidence(
                    demonstrates=(
                        evidence.demonstrates
                    ),
                    plan_evidence=plan_evidence,
                    annotation_evidence=(
                        annotation_evidence
                    ),
                )
            )

        record = record_by_id[
            reference_id
        ]

        validated_uses.append(
            RendererReferenceUse(
                reference_id=record.reference_id,
                concept=record.concept,
                image_path=str(
                    record.image_path
                ),
                evidence=validated_evidence,
            )
        )

    packet = RendererReferencePacket(
        references=validated_uses
    )

    # -----------------------------------------------------
    # Human-readable debug trace.
    # -----------------------------------------------------

    print(
        "\nSTAGE-C RENDERER REFERENCES"
    )
    print(
        "==========================="
    )

    if not packet.references:
        print(
            "No useful renderer references selected."
        )

    for reference in packet.references:
        print(
            f"\n{reference.reference_id} | "
            f"{reference.concept}"
        )

        for evidence in reference.evidence:
            print(
                f"  - {evidence.demonstrates}"
            )

            print(
                "    Plan basis:"
            )

            for (
                path,
                value,
            ) in evidence.plan_evidence.items():
                print(
                    f"      {path} = {value}"
                )

            print(
                "    Annotation basis:"
            )

            for (
                path,
                value,
            ) in evidence.annotation_evidence.items():
                print(
                    f"      {path} = {value}"
                )

    return packet
