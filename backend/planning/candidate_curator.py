from __future__ import annotations

import json

from config import TEXT_MODEL
from openai_client import get_openai_client
from planning.schemas import (
    CandidateCuration,
    CandidateScenePool,
    ConceptBrief,
    RepresentationOptionality,
    ViabilityStatus,
)


def retention_range(
    optionality: RepresentationOptionality,
) -> tuple[int, int]:
    """
    Preferred size of the curated pool.

    These are budgets, not instructions to preserve weak or redundant
    candidates merely to fill a quota.
    """

    if optionality == RepresentationOptionality.low:
        return (1, 1)

    if optionality == RepresentationOptionality.high:
        return (2, 3)

    return (1, 2)


def curate_candidate_scenes(
    concept_brief: ConceptBrief,
    candidate_pool: CandidateScenePool,
) -> CandidateCuration:
    """
    Apply viability gates first, then diversity curation.

    This stage does not redesign candidates and does not perform
    full art direction.
    """

    client = get_openai_client()

    preferred_min, preferred_max = retention_range(
        concept_brief.representation_optionality
    )

    concept_json = json.dumps(
        concept_brief.model_dump(mode="json"),
        indent=2,
        ensure_ascii=False,
    )

    candidates_json = json.dumps(
        candidate_pool.model_dump(mode="json"),
        indent=2,
        ensure_ascii=False,
    )

    response = client.responses.parse(
        model=TEXT_MODEL,
        input=[
            {
                "role": "system",
                "content": """
You are the Candidate Curator for a calendar illustration pipeline.

A Creative Planner has already generated several independently imagined
candidate scenes.

Your job has TWO ordered phases:

1. VIABILITY FILTERING
2. DIVERSITY CURATION

Do not redesign the scenes.

Do not perform full art direction.

Do not choose colors, final composition, layer structure, rendering
technique, or detailed graphic treatment.

==================================================
PHASE 1: VIABILITY FILTERING
==================================================

Evaluate EVERY candidate independently using these six gates.

For each gate return:

- pass
- pass_with_manageable_risk
- fail

A candidate should fail only when the underlying scene itself has a
serious problem.

Do not fail a concept merely because an image model may find it
technically difficult to render.

------------------------------------------
1. SEMANTIC LEGITIMACY
------------------------------------------

Ask:

Does this scene legitimately represent the requested event?

Does it preserve meaningful specificity?

Does it avoid turning associations into unsupported facts?

Does it respect protected unknowns about named people, relationships,
identity, occasion, setting, or other unspecified facts?

FAIL when the scene depends on an unsupported semantic claim or has
drifted into a neighboring concept.

------------------------------------------
2. RECOGNITION SUFFICIENCY
------------------------------------------

Ask:

Could a viewer plausibly understand the intended concept without
reading the calendar title or an explanation?

Consider the complete recognition structure:

- dominant anchor,
- supporting cues,
- relationships,
- environment,
- action,
- object state.

A candidate may use several distributed cues.

Do not require one iconic object when the scene intentionally uses
distributed or relational recognition.

FAIL when the concept would remain fundamentally ambiguous even if
rendered well.

------------------------------------------
3. SCENE COHERENCE
------------------------------------------

Ask:

Does the imagined picture make spatial and visual sense?

Do the selected viewpoint, objects, actions, and relationships belong
in one coherent scene?

Did the shallow simulation expose unresolved contradictions?

Are the kept elements compatible with the chosen viewpoint?

FAIL when the scene cannot be coherently pictured without redesigning
its basic idea.

------------------------------------------
4. CALENDAR-FORMAT FEASIBILITY
------------------------------------------

Ask:

Can this scene plausibly work as a wide, shallow calendar illustration?

It may later use:

- cropping,
- edge continuation,
- simplified context,
- asymmetric composition,
- partial figures.

Do not perform those decisions now.

FAIL only when the scene fundamentally depends on a spatial structure
that cannot reasonably survive the calendar format.

------------------------------------------
5. STYLE-GRAMMAR COMPATIBILITY
------------------------------------------

Ask:

Could this scene be translated into a simplified Google
Calendar-like illustration language without losing the concept?

Do NOT art-direct it yet.

Do not require it to resemble an existing Google Calendar image.

Consider only whether the semantic idea remains workable under a
simplified, low-realism graphic treatment.

FAIL when the candidate fundamentally depends on:

- fine realistic texture,
- subtle photorealistic lighting,
- detailed readable text,
- tiny realistic distinctions,
- or other information unlikely to survive simplification.

------------------------------------------
6. INDEPENDENCE FROM EXPLANATION
------------------------------------------

Ask:

Does the image communicate on its own?

A clever concept must not require the viewer to be told:

"this object symbolizes..."

or

"this half represents before and this half represents after..."

PASS WITH MANAGEABLE RISK is appropriate when the idea could work but
requires especially clear execution.

FAIL when explanation is essential to understanding the concept.

==================================================
OVERALL STATUS
==================================================

overall_status should reflect the candidate as a whole.

Use:

pass
    The underlying scene is sound.

pass_with_manageable_risk
    The scene is fundamentally sound, but one or more issues require
    careful later art direction.

fail
    The basic visual idea is not viable without substantial redesign.

Renderer difficulty alone is not sufficient reason to fail a candidate.

==================================================
REFINEMENT REQUESTS
==================================================

For viable candidates, refinement_requests may identify things the
later Art Director should solve.

Examples:

- strengthen the baking-specific cue,
- preserve the distinction between two object states,
- simplify supporting context,
- make the key interaction unmistakable.

These should refine the existing candidate.

They must NOT replace its representation strategy or invent a new
scene.

==================================================
PHASE 2: DIVERSITY CURATION
==================================================

Only after viability filtering, examine the surviving candidates
together.

The goal is NOT to rank them from best to worst.

The goal is to preserve meaningfully different viable visual
directions while removing redundant ones.

Two candidates may be substantially redundant when they share most of
the following:

- the same recognition mechanism,
- the same central action,
- the same temporal moment,
- essentially the same human/object relationship,
- the same environmental logic,
- the same recognition anchor,
- and only minor object or layout differences.

Do NOT treat candidates as redundant merely because they depict the
same event.

For example:

- active mixing,
- putting a tray into an oven,
- an object-centered transformation,
- and an unoccupied prepared environment

may all be genuinely different visual directions for the same concept.

==================================================
CANDIDATE IDENTITY
==================================================

Respect each candidate's must_preserve fields.

Do not merge two candidates.

Do not mutate one candidate into another.

If a candidate's may_adjust list accidentally contains a change that
would destroy its representation strategy or recognition structure,
treat the candidate's actual stated strategy and visual thesis as the
stronger definition of its identity.

==================================================
RETENTION BUDGET
==================================================

You will be given a preferred retention range.

Try to stay within it.

However:

- never retain a failed candidate merely to fill the minimum;
- never describe the retained candidates as ranked;
- retain candidates because together they form a compact set of
  distinct viable directions.

If fewer candidates survive than the preferred minimum, return the
viable survivors.

==================================================
OUTPUT DISCIPLINE
==================================================

Produce one CandidateAssessment for EVERY input candidate.

retained_candidate_ids:
    IDs of viable candidates retained for later art direction.

removed_as_redundant:
    IDs of otherwise viable candidates removed because another retained
    candidate already covers substantially the same visual direction.

Do not put failed candidates in removed_as_redundant.

failure_reasons:
    Explain only genuine viability failures.

diversity_notes:
    Briefly explain the major distinctions among the retained set and
    any important redundancy decisions.

Do not declare a winner.
""".strip(),
            },
            {
                "role": "user",
                "content": f"""
CURATE THIS CANDIDATE POOL.

Preferred retained-candidate range:
{preferred_min} to {preferred_max}

CONCEPT INTERPRETATION
======================

{concept_json}


CANDIDATE SCENES
================

{candidates_json}


TASK
====

First assess every candidate independently against all six viability
gates.

Then perform diversity curation among the viable candidates.

Do not redesign the scenes.

Do not rank the retained candidates.

Return a compact set of meaningfully distinct viable directions.
""".strip(),
            },
        ],
        text_format=CandidateCuration,
    )

    result = response.output_parsed

    candidate_ids = [
        candidate.id
        for candidate in candidate_pool.candidates
    ]

    candidate_id_set = set(candidate_ids)

    assessment_ids = [
        assessment.candidate_id
        for assessment in result.assessments
    ]

    if (
        len(assessment_ids) != len(candidate_ids)
        or set(assessment_ids) != candidate_id_set
    ):
        raise ValueError(
            "Candidate Curator must assess every candidate exactly once. "
            f"Expected {candidate_ids}, got {assessment_ids}."
        )

    if len(set(result.retained_candidate_ids)) != len(
        result.retained_candidate_ids
    ):
        raise ValueError(
            "retained_candidate_ids contains duplicates."
        )

    if not set(result.retained_candidate_ids).issubset(
        candidate_id_set
    ):
        raise ValueError(
            "Candidate Curator returned an unknown retained candidate ID."
        )

    if not set(result.removed_as_redundant).issubset(
        candidate_id_set
    ):
        raise ValueError(
            "Candidate Curator returned an unknown redundant candidate ID."
        )

    if set(result.retained_candidate_ids) & set(
        result.removed_as_redundant
    ):
        raise ValueError(
            "A candidate cannot be both retained and removed as redundant."
        )

    failed_ids = {
        assessment.candidate_id
        for assessment in result.assessments
        if assessment.overall_status == ViabilityStatus.fail
    }

    if failed_ids & set(result.retained_candidate_ids):
        raise ValueError(
            "A failed candidate cannot be retained."
        )

    if failed_ids & set(result.removed_as_redundant):
        raise ValueError(
            "Failed candidates should not be labeled redundant."
        )

    viable_count = len(candidate_ids) - len(failed_ids)

    if viable_count > 0:
        effective_min = min(
            preferred_min,
            viable_count,
        )
        effective_max = min(
            preferred_max,
            viable_count,
        )

        retained_count = len(
            result.retained_candidate_ids
        )

        if not (
            effective_min
            <= retained_count
            <= effective_max
        ):
            raise ValueError(
                "Candidate Curator retained an unexpected number "
                f"of candidates: {retained_count}. "
                f"Expected {effective_min}-{effective_max} "
                "given the viable pool."
            )

    print("Candidate curation:")
    print(result.model_dump_json(indent=2))

    return result
