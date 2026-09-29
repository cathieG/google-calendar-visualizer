from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field

from config import TEXT_MODEL
from openai_client import get_openai_client
from planning.schemas import PreliminaryCritique
from references.render_registry import (
    RenderReferenceRecord,
    load_render_reference_registry,
)
from references.render_selector import (
    _compact_annotation,
    _is_empty_evidence,
    _resolve_path,
)


# =========================================================
# Retrieval trigger
# =========================================================

REFERENCE_RELEVANT_CATEGORIES = {
    "artistic_interest",
    "google_calendar_style",
    "composition",
    "complexity",
    "unintended_implication",
}

REFERENCE_RELEVANT_ORIGINS = {
    "art_direction",
    "scene_concept",
}


def should_retrieve_critique_references(
    critique: PreliminaryCritique,
) -> bool:
    """
    Decide deterministically whether visual precedent would materially
    help the critique.

    The model does not get to opt out of references when the diagnosis
    itself concerns artistic quality, representation, or art direction.
    """

    if critique.reference_focus:
        return True

    for issue in critique.issues:
        if issue.category in REFERENCE_RELEVANT_CATEGORIES:
            return True

        if issue.origin in REFERENCE_RELEVANT_ORIGINS:
            return True

    return False


# =========================================================
# Selector output
# =========================================================

class CritiqueEvidenceMatch(BaseModel):
    """
    Why one reference is useful for judging a diagnosed weakness.

    critique_fields and annotation_fields form the deterministic
    grounding trail.
    """

    helps_judge: str

    critique_fields: list[str] = Field(
        default_factory=list
    )

    annotation_fields: list[str] = Field(
        default_factory=list
    )


class CritiqueReferenceChoice(BaseModel):
    reference_id: str

    evidence: list[CritiqueEvidenceMatch] = Field(
        default_factory=list
    )


class CritiqueReferenceSelection(BaseModel):
    references: list[CritiqueReferenceChoice] = Field(
        default_factory=list
    )


# =========================================================
# Validated downstream packet
# =========================================================

class ValidatedCritiqueEvidence(BaseModel):
    helps_judge: str

    critique_evidence: dict[str, Any]

    annotation_evidence: dict[str, Any]


class CritiqueReferenceUse(BaseModel):
    reference_id: str
    concept: str
    image_path: str

    evidence: list[ValidatedCritiqueEvidence]


class CritiqueReferencePacket(BaseModel):
    references: list[CritiqueReferenceUse] = Field(
        default_factory=list
    )


# =========================================================
# Selector
# =========================================================

def select_critique_references(
    critique: PreliminaryCritique,
    records: list[RenderReferenceRecord] | None = None,
    max_references: int = 3,
) -> CritiqueReferencePacket:
    """
    Retrieve Google Calendar precedents for contrastive critique.

    Unlike Stage C, these references do NOT support decisions already
    present in a FinalScenePlan.

    They provide visual evidence for judging diagnosed weaknesses such
    as under-design, excessive literalness, weak negative-space use,
    awkward human treatment, or insufficient abstraction.
    """

    if max_references < 1:
        raise ValueError(
            "max_references must be at least 1."
        )

    if not should_retrieve_critique_references(
        critique
    ):
        print(
            "\nCRITIQUE REFERENCES"
        )
        print(
            "==================="
        )
        print(
            "No critique references needed: "
            "diagnosis is execution-only."
        )

        return CritiqueReferencePacket()

    if records is None:
        records = (
            load_render_reference_registry()
        )

    if not records:
        return CritiqueReferencePacket()

    critique_data = critique.model_dump(
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
You are the critique-reference selector for a Google Calendar
illustration pipeline.

A critic has already inspected a newly rendered illustration and
produced a PreliminaryCritique.

You will receive:

1. that PreliminaryCritique;
2. a small bank of verified annotations describing real Google
   Calendar reference illustrations.

Your job is to select references that provide useful CONTRASTIVE
EVIDENCE for judging the critic's diagnosed design questions.

==================================================
PURPOSE
==================================================

This is not Stage-C renderer reference selection.

Do NOT ask:

"Which reference most closely matches the current scene?"

Instead ask:

"Which existing Google Calendar illustration demonstrates a visual
strategy that helps us evaluate, explain, or challenge the diagnosed
weakness?"

References may therefore differ substantially in subject matter.

The goal is visual precedent, not semantic similarity.

==================================================
GOOD USES OF CRITIQUE REFERENCES
==================================================

References can help judge questions such as:

- whether a sparse composition is designed minimalism or merely empty;
- whether negative space is active;
- whether a human-action scene has a memorable graphic device;
- whether semantic scale is being used inventively;
- whether cropping creates stronger graphic structure;
- whether an environment could be more abstract;
- whether a scene is excessively literal;
- whether incidental detail creates artistic interest without clutter;
- whether human representation can avoid unnecessary bodily emphasis;
- whether motion is expressed graphically;
- whether spatial relationships are deliberately nonliteral;
- whether objects or figures interact with the frame in an interesting
  way;
- whether a scene relies too heavily on generic stock-vector
  composition.

==================================================
DO NOT RETRIEVE BY CONCEPT NAME
==================================================

Do not choose a reference merely because its event or activity resembles
the new illustration.

For example:

A Yoga critique does not automatically need another exercise image.

A Spa critique does not require a health or body-care image.

A reference is useful because of an OBSERVED VISUAL PROPERTY in its
annotation.

Concept names are identifiers only.

==================================================
ANNOTATION GROUNDING
==================================================

Every evidence claim must cite BOTH:

1. exact fields from the PreliminaryCritique;
2. exact fields from the supplied reference annotation.

Use exact dotted/list-indexed paths.

Examples:

issues[0].category

issues[0].observation

issues[0].origin

visual_hook

artistic_question

reference_focus[0]

whole_scene.composition

whole_scene.cropping.strength

whole_scene.background

humans.fine_inventory[0].body_visibility

relationships.primary_motion_cue

objects.image_verified_inventory[0].view

Do not cite fields that are absent, null, empty, or unrelated.

Do not infer visual evidence from the reference's concept name.

==================================================
CONTRASTIVE REASONING
==================================================

A useful reference may demonstrate something the current image LACKS.

For example:

Preliminary critique:
"The scene is readable but visually generic."

Useful reference:
A scene whose annotation verifies strong cropping, semantic scale,
graphic movement, or an unusual interaction with negative space.

The evidence description should explain what comparison the later
critic should make.

Good:

"Compare how this reference turns a sparse human-action composition
into an active graphic structure through directional movement and
asymmetric negative space."

Bad:

"Copy the jumping composition."

==================================================
REFERENCE BOUNDARY
==================================================

References are evidence, not replacement designs.

Do not prescribe copying:

- the reference subject;
- exact objects;
- exact pose;
- exact layout;
- exact palette;
- narrative content.

Do not redesign the new illustration here.

==================================================
SELECTION SIZE
==================================================

Select the smallest useful set.

Return between zero and the supplied maximum.

Do not pad.

Each later reference must contribute a meaningfully different piece of
evidence.

Normally 1-3 references are sufficient.

Return only the structured selection.
""".strip(),
            },
            {
                "role": "user",
                "content": f"""
PRELIMINARY CRITIQUE
====================

{json.dumps(
    critique_data,
    indent=2,
    ensure_ascii=False,
)}


VERIFIED GOOGLE CALENDAR REFERENCE BANK
=======================================

{json.dumps(
    reference_bank,
    indent=2,
    ensure_ascii=False,
)}


MAXIMUM REFERENCES
==================

{max_references}


Select only annotation-grounded references that materially help judge
the diagnosed artistic, representational, or stylistic questions.
""".strip(),
            },
        ],
        text_format=CritiqueReferenceSelection,
    )

    selection = response.output_parsed

    # -----------------------------------------------------
    # Validate selection
    # -----------------------------------------------------

    if len(selection.references) > max_references:
        raise ValueError(
            "Critique selector returned "
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
        CritiqueReferenceUse
    ] = []

    for choice in selection.references:
        reference_id = choice.reference_id

        if reference_id in seen_reference_ids:
            raise ValueError(
                "Critique selector returned duplicate "
                f"reference '{reference_id}'."
            )

        seen_reference_ids.add(
            reference_id
        )

        if reference_id not in record_by_id:
            raise ValueError(
                "Critique selector returned unknown "
                f"reference '{reference_id}'."
            )

        if not choice.evidence:
            raise ValueError(
                f"Selected critique reference "
                f"'{reference_id}' contains no evidence."
            )

        annotation_data = compact_by_id[
            reference_id
        ]

        validated_evidence: list[
            ValidatedCritiqueEvidence
        ] = []

        for evidence in choice.evidence:

            if not evidence.helps_judge.strip():
                raise ValueError(
                    f"Reference '{reference_id}' has an "
                    "empty contrastive evidence description."
                )

            if not evidence.critique_fields:
                raise ValueError(
                    f"Evidence '{evidence.helps_judge}' "
                    "does not cite a PreliminaryCritique field."
                )

            if not evidence.annotation_fields:
                raise ValueError(
                    f"Evidence '{evidence.helps_judge}' "
                    "does not cite an annotation field."
                )

            critique_evidence: dict[
                str,
                Any,
            ] = {}

            for path in evidence.critique_fields:
                value = _resolve_path(
                    critique_data,
                    path,
                )

                if _is_empty_evidence(value):
                    raise ValueError(
                        "Critique selector cited empty "
                        f"PreliminaryCritique field '{path}'."
                    )

                critique_evidence[
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
                        "Critique selector cited empty "
                        "annotation field "
                        f"'{reference_id}:{path}'."
                    )

                annotation_evidence[
                    path
                ] = value

            validated_evidence.append(
                ValidatedCritiqueEvidence(
                    helps_judge=(
                        evidence.helps_judge
                    ),
                    critique_evidence=(
                        critique_evidence
                    ),
                    annotation_evidence=(
                        annotation_evidence
                    ),
                )
            )

        record = record_by_id[
            reference_id
        ]

        validated_uses.append(
            CritiqueReferenceUse(
                reference_id=(
                    record.reference_id
                ),
                concept=record.concept,
                image_path=str(
                    record.image_path
                ),
                evidence=validated_evidence,
            )
        )

    packet = CritiqueReferencePacket(
        references=validated_uses
    )

    # -----------------------------------------------------
    # Debug trace
    # -----------------------------------------------------

    print(
        "\nCRITIQUE REFERENCES"
    )
    print(
        "==================="
    )

    if not packet.references:
        print(
            "No useful contrastive references selected."
        )

    for reference in packet.references:
        print(
            f"\n{reference.reference_id} | "
            f"{reference.concept}"
        )

        for evidence in reference.evidence:
            print(
                f"  - {evidence.helps_judge}"
            )

            print(
                "    Critique basis:"
            )

            for (
                path,
                value,
            ) in evidence.critique_evidence.items():
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
