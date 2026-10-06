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
2. a small bank of verified visual annotations describing existing
   reference illustrations.

Your task is to select only the reference images that provide useful
visual evidence for EXECUTING decisions that already exist in the
FinalScenePlan.


==================================================
NON-NEGOTIABLE BOUNDARY
==================================================

The FinalScenePlan is authoritative.

Do not redesign, reinterpret, improve, or replace its decisions.

Do not introduce a new:

- subject,
- object,
- person,
- action,
- presentation concept,
- composition,
- hierarchy,
- viewpoint,
- framing,
- crop,
- depth strategy,
- perspective strategy,
- scale strategy,
- environment treatment,
- human staging,
- relationship,
- motion strategy,
- decorative strategy,
- color strategy,
- or narrative.

References support already-made decisions only.

If a reference suggests a visually interesting solution that conflicts
with the FinalScenePlan, ignore that solution.


==================================================
HOW TO READ THE FINAL SCENE PLAN
==================================================

The FinalScenePlan contains both holistic decisions and structured
execution decisions.

Holistic fields may include:

- recognition_plan
- presentation_concept
- content_selection.visible_elements
- content_selection.intentional_omissions

These fields explain the overall visual logic of the finished design.
Use them as context for understanding why a particular execution
precedent may matter.

Structured execution fields may include:

- composition.structure
- composition.hierarchy_and_balance
- composition.negative_space
- composition.directional_flow

- framing_and_view.viewpoint
- framing_and_view.framing
- framing_and_view.cropping_strength
- framing_and_view.edge_continuation

- spatial_plan.depth_strategy
- spatial_plan.perspective_strategy
- spatial_plan.spatial_relationships

- scale_plan.strategy
- scale_plan.description

- environment_plan

- relationships_and_motion.key_relationships
- relationships_and_motion.motion_plan

- human_staging.body_visibility
- human_staging.orientation_and_pose
- human_staging.role_in_composition

- color_direction
- shape_direction
- detail_direction
- human_rendering_direction
- decorative_direction

Not every field will be relevant to every reference.

Do not try to find a precedent for every field.


==================================================
WHAT MAKES A REFERENCE USEFUL
==================================================

A reference is useful when one or more directly observed properties in
its annotation provide concrete execution guidance for a visual decision
that already exists in the FinalScenePlan.

A useful reference may support either:

1. STRUCTURAL EXECUTION

Examples include:
- viewpoint,
- camera elevation,
- framing,
- cropping,
- edge continuation,
- perspective,
- depth construction,
- spatial overlap or ordering,
- scale relationships,
- negative-space organization,
- background treatment,
- environment treatment,
- body visibility,
- body orientation,
- pose,
- visible hands,
- person-object interaction,
- object-object interaction,
- object view or simplification.

2. ARTISTIC / DECORATIVE EXECUTION

Examples include:
- decorative rhythm,
- repeated graphic motifs,
- abstract balancing forms,
- purposeful activation of negative space,
- nonliteral atmospheric forms,
- symbolic or decorative elements,
- scene-specific color organization,
- use of accent color for hierarchy or recognition,
- concentration of visual detail in semantically important areas,
- deliberate quieting of tertiary regions,
- contrast between geometric and organic shape families,
- expressive use of line, silhouette, or repeated forms,
- artistic treatment that reinforces motion, atmosphere, balance,
  recognition, or compositional flow.

These artistic precedents must still correspond to decisions already
present in the FinalScenePlan.

For example, if decorative_direction calls for sparse abstract forms
that activate quiet background space, a reference demonstrating such a
treatment may be useful.

If color_direction calls for one diagnostic element to receive stronger
color emphasis than the surrounding scene, a reference demonstrating
that hierarchy may be useful.

If detail_direction concentrates specificity in recognition-critical
objects while simplifying tertiary context, a reference demonstrating
that distribution of detail may be useful.

The new scene does not need to depict the same activity, object set, or
concept as the reference.

A reference may be useful for only one small visual property.


==================================================
ANNOTATION GROUNDING
==================================================

Every evidence claim must be supported on BOTH sides:

1. by one or more exact fields in the FinalScenePlan;
2. by one or more exact, non-null fields in that reference's supplied
   annotation.

For plan_fields:

- cite exact field paths from the supplied FinalScenePlan JSON.

For annotation_fields:

- cite exact field paths from that reference's supplied annotation JSON.

Use dot notation and list indices when needed.

Examples of valid FinalScenePlan paths:

framing_and_view.cropping_strength
framing_and_view.viewpoint
spatial_plan.depth_strategy
spatial_plan.perspective_strategy
scale_plan.strategy
composition.negative_space
relationships_and_motion.key_relationships[0]
human_staging.body_visibility

Examples of valid annotation paths:

whole_scene.viewpoint.vertical
whole_scene.depth.category
whole_scene.cropping.strength
rendering.shape_language_source.environment
rendering.color_source.functional_role
humans.fine_inventory[0].hands_visible
objects.image_verified_inventory[1].view
relationships.image_verified_relations[0]

The renderer annotations have been normalized so that legitimate
dictionary fields use a consistent structure across references.

A field may therefore exist in the annotation structure while having
the value null for a particular reference.

IMPORTANT:

- A non-null value may be used as annotation evidence when it directly
  supports the claim.
- A null value means that this reference provides no evidence for that
  property.
- Do NOT cite a field whose value is null.
- Do NOT cite a field whose value is empty or unrelated to the claim.

Lists are NOT padded or normalized to a common length.

Therefore, when citing a list element such as:

humans.fine_inventory[1].body_visibility
objects.image_verified_inventory[2].view
relationships.image_verified_relations[3]

the cited index must actually exist in that reference.

A free-text FinalScenePlan field may support a match when its actual text
contains the relevant decision. Do not infer a decision that the field
does not state.

Do not infer a visual property merely from:

- the reference's concept name,
- what normally occurs in that activity,
- or what you assume the image probably contains.

Only the supplied verified annotation may establish what the reference
demonstrates.


==================================================
STRICT ANNOTATION PATH GRAMMAR
==================================================

Every annotation_evidence field path MUST correspond exactly to the
supplied VERIFIED RENDERER REFERENCE BANK.

For renderer evidence, use only these top-level annotation sections:

- whole_scene
- rendering
- humans
- objects
- relationships

These sections are siblings.

They are NOT nested inside one another.

Therefore:

VALID EXAMPLES

whole_scene.environment.normalized_treatment
whole_scene.depth.category
whole_scene.cropping.strength
whole_scene.viewpoint.horizontal

rendering.shape_language_source.overall
rendering.shape_language_source.environment
rendering.color_source.functional_role

humans.fine_inventory[0].body_visibility
humans.fine_inventory[0].hands_visible

objects.image_verified_inventory[0].shape_treatment
objects.image_verified_inventory[0].view

relationships.image_verified_relations[0]

INVALID EXAMPLES

environment.normalized_treatment
whole_scene.objects.image_verified_inventory[0].view
whole_scene.humans.fine_inventory[0].pose
whole_scene.rendering.color_source.functional_role
whole_scene.relationships.image_verified_relations[0]

Do NOT place rendering, humans, objects, or relationships underneath
whole_scene.

Because the renderer annotations are normalized, some legitimate fields
may be present with a null value.

A path with a null value is structurally valid but is NOT valid evidence.

For example:

rendering.shape_language_source.environment = null

means that the path is valid, but this reference does not provide
environment shape-language evidence.

Do not cite it.

For list-valued sections, use only indices that actually exist in the
supplied annotation. Do not invent or assume additional people, objects,
or relationships merely because another reference contains more list
items.

Before returning the final selection, verify every annotation_evidence
path against the supplied annotation:

1. the complete path is structurally valid;
2. every required list index exists;
3. the resolved value is not null;
4. the resolved value is not empty;
5. the resolved value directly supports the visual lesson.

Do not infer, reconstruct, abbreviate, rename, or invent a field path.

If no exact, non-null annotation field supports a claim, omit that
annotation evidence rather than guessing.


==================================================
STYLE-WIDE PROPERTIES VS. SCENE-SPECIFIC ARTISTIC MOVES
==================================================

Do not select a reference solely because it demonstrates stable
StyleProfile properties that apply broadly across the illustration
system, such as:

- flat-color-dominant rendering,
- high shape simplification,
- low material realism,
- minimal gradients,
- minimal realistic shading,
- little texture,
- borderless or selectively outlined forms.

Those properties belong to the StyleProfile and do not by themselves
justify selecting a renderer reference.

However, a reference MAY be useful when it demonstrates a
scene-specific artistic solution that applies those broader style rules
in a way that directly supports the FinalScenePlan.

Examples:

Useful:
- sparse abstract forms activating intentionally quiet negative space;
- a concentrated saturated accent supporting one recognition-critical
  object;
- repeated decorative units creating rhythm across a distributed
  composition;
- simplified geometric context being kept visually quiet while a
  recognition-critical interaction receives more detail;
- abstract light or graphic forms reinforcing directional flow.

Not useful by itself:
- the reference uses flat color;
- the reference has simplified shapes;
- the reference has little shading.

The question is not merely:
"Does this look like the same style?"

The question is:
"Does this reference demonstrate a specific artistic execution strategy
that helps realize an already-decided part of this FinalScenePlan?"

==================================================
HOLISTIC VERSUS PROPERTY-LEVEL MATCHES
==================================================

A reference does not need to match the entire FinalScenePlan.

Sometimes one reference may demonstrate an integrated solution involving
several mutually reinforcing properties, such as:

- viewpoint + crop + perspective + scale,
- human staging + interaction + framing,
- environment + composition + depth,
- distributed objects + visual equivalence + shallow space.

When such an integrated precedent closely supports the existing
presentation_concept, describe that relationship clearly.

However, do not force several weak similarities together merely to make
a reference appear more relevant.

A precise precedent for one important property is preferable to a vague
precedent for many properties.


==================================================
SELECTION SIZE AND REDUNDANCY
==================================================

Build a compact but sufficiently rich visual reference set
covering the major execution demands of the FinalScenePlan.

Return between two and the supplied maximum number of references.

Do not pad the result merely because additional references are
available.

Every selected reference must contribute at least one genuinely useful
piece of execution evidence.

If two references demonstrate essentially the same useful property,
prefer the one whose verified annotation provides the clearer or more
directly applicable precedent.

A later reference should add useful evidence that is not already
adequately supplied by the earlier references.

Do not invent approximate support when the reference bank lacks a useful
precedent.


==================================================
EVIDENCE DESCRIPTION
==================================================

For each selected reference, describe what it demonstrates in concise,
renderer-facing language.

The description should answer:

"What specific visual property or integrated execution solution should
the renderer study from this reference?"

Describe the transferable visual lesson.

Do not tell the renderer to copy the reference's:

- subject,
- object set,
- exact pose,
- exact composition,
- exact crop boundary,
- exact viewpoint,
- exact spatial arrangement,
- palette,
- character appearance,
- or narrative.

Do not ask the renderer to modify any decision already established by
the FinalScenePlan.

Return only the structured selection.


==================================================
FINAL EVIDENCE CHECK
==================================================

Before producing the response, inspect every key placed inside
annotation_evidence.

For each key, confirm that:

1. the complete path exists verbatim in the supplied reference data;
2. the value at that path supports the stated visual lesson;
3. the path begins with exactly one valid root section:
   whole_scene, rendering, humans, objects, or relationships.

If any check fails, remove that evidence entry.
Never repair a path by guessing.


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
            print(
                f"Stage-C skipping reference '{reference_id}' "
                "because it contains no evidence claims."
            )
            continue

        annotation_data = compact_by_id[
            reference_id
        ]

        validated_evidence: list[
            ValidatedRenderEvidence
        ] = []

        for evidence in choice.evidence:
            if not evidence.demonstrates.strip():
                print(
                    f"Stage-C skipping empty evidence claim "
                    f"for reference '{reference_id}'."
                )
                continue

            if not evidence.plan_fields:
                print(
                    f"Stage-C skipping evidence claim with no "
                    f"FinalScenePlan fields for reference "
                    f"'{reference_id}': "
                    f"{evidence.demonstrates}"
                )
                continue

            if not evidence.annotation_fields:
                print(
                    f"Stage-C skipping evidence claim with no "
                    f"annotation fields for reference "
                    f"'{reference_id}': "
                    f"{evidence.demonstrates}"
                )
                continue

            # -------------------------------------------------
            # Validate FinalScenePlan evidence.
            # -------------------------------------------------

            plan_evidence: dict[
                str,
                Any,
            ] = {}

            for path in evidence.plan_fields:
                try:
                    value = _resolve_path(
                        plan_data,
                        path,
                    )

                except (KeyError, ValueError) as exc:
                    print(
                        "Stage-C skipping invalid "
                        "FinalScenePlan path "
                        f"'{path}': {exc}"
                    )
                    continue

                if _is_empty_evidence(value):
                    print(
                        "Stage-C skipping empty "
                        "FinalScenePlan field "
                        f"'{path}'."
                    )
                    continue

                plan_evidence[path] = value

            # An evidence claim must have at least one real
            # FinalScenePlan field supporting it.
            if not plan_evidence:
                print(
                    f"Stage-C skipping evidence claim because "
                    f"no valid FinalScenePlan evidence remained: "
                    f"{evidence.demonstrates}"
                )
                continue

            # -------------------------------------------------
            # Validate renderer-annotation evidence.
            # -------------------------------------------------

            annotation_evidence: dict[
                str,
                Any,
            ] = {}

            for path in evidence.annotation_fields:
                try:
                    value = _resolve_path(
                        annotation_data,
                        path,
                    )

                except (KeyError, ValueError) as exc:
                    print(
                        "Stage-C skipping invalid annotation path "
                        f"'{reference_id}:{path}': {exc}"
                    )
                    continue

                if _is_empty_evidence(value):
                    print(
                        "Stage-C skipping empty annotation field "
                        f"'{reference_id}:{path}'."
                    )
                    continue

                annotation_evidence[path] = value

            # A claim must have at least one actual annotation
            # value. A normalized null field is not evidence.
            if not annotation_evidence:
                print(
                    f"Stage-C skipping evidence claim because "
                    f"no valid annotation evidence remained: "
                    f"{evidence.demonstrates}"
                )
                continue

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

        # If every proposed evidence claim for this reference
        # failed validation, omit the reference rather than
        # sending an unsupported reference downstream.
        if not validated_evidence:
            print(
                f"Stage-C skipping reference '{reference_id}' "
                "because no fully grounded evidence survived "
                "validation."
            )
            continue

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
