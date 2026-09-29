from __future__ import annotations

import json

from config import TEXT_MODEL
from openai_client import get_openai_client
from planning.schemas import (
    CandidateScenePool,
    ConceptBrief,
    ConceptRequest,
    ReferencePacket,
    RepresentationOptionality,
)
from references.multimodal import build_reference_content


def candidate_count_for_optionality(
    optionality: RepresentationOptionality,
) -> int:
    """
    Use more divergent exploration when the concept admits more
    substantially different visual representations.
    """

    if optionality == RepresentationOptionality.low:
        return 2

    if optionality == RepresentationOptionality.high:
        return 6

    return 4


def plan_candidate_scenes(
    request: ConceptRequest,
    concept_brief: ConceptBrief,
    reference_packet: ReferencePacket | None = None,
) -> CandidateScenePool:
    """
    Generate several genuinely different visual directions and perform
    a shallow mental simulation of each one.

    This stage decides a plausible picture, but it does NOT perform
    full style-specific art direction.

    In particular, it must not design visual layers yet.
    """

    client = get_openai_client()

    candidate_count = candidate_count_for_optionality(
        concept_brief.representation_optionality
    )

    reference_content = build_reference_content(
        reference_packet
    )

    concept_json = json.dumps(
        concept_brief.model_dump(mode="json"),
        indent=2,
        ensure_ascii=False,
    )

    response = client.responses.parse(
        model=TEXT_MODEL,
        input=[
            {
                "role": "system",
                "content": """
You are the Creative Planner for a calendar illustration system.

A previous Concept Interpreter has already established the semantic
meaning of the event.

Your job is now to invent MULTIPLE coherent visual scene directions.

You are not the final art director and not the renderer.

==================================================
CORE PRINCIPLE
==================================================

Do not ask only:

"What objects are associated with this event?"

Instead ask:

"What genuinely different pictures could communicate this event
clearly, economically, and visually?"

Generate alternative SCENES, not minor variations of the same scene.

For example, different candidates may differ in:

- whether recognition comes from a human action,
- an object state,
- a relationship between objects,
- a prepared environment,
- a symbolic composition,
- or a short implied narrative;

- whether people are necessary at all;

- whether the scene captures preparation, action, result, or aftermath;

- whether context is omitted, abstracted, or semantically useful.

Do not produce several candidates that merely rearrange the same
objects.

==================================================
SEMANTIC DISCIPLINE
==================================================

Preserve what makes the requested event specific.

Known details may be relied upon.

General associations are possibilities, not requirements.

Open choices are legitimate areas of creative freedom.

Protected unknowns are hard boundaries.

Do not invent unsupported identity-specific facts about named or
otherwise identified people.

A name alone does not establish:

- gender,
- age,
- race or ethnicity,
- skin tone,
- hairstyle,
- appearance,
- body type,
- clothing style,
- occupation,
- or relationship to another participant.

Anonymous people may have ordinary human variation.

If a relationship between identified participants is unknown, do not
invent physical contact, romantic behavior, family behavior,
caretaking, mentorship, or other relationship-specific interaction.

A participant can be semantically part of an event without needing to
appear visually.

==================================================
CONTENT ECONOMY
==================================================

Do not reconstruct the entire real-world event.

Prefer the smallest coherent scene that still preserves the event's
recognizability and meaningful specificity.

Every retained visible element should earn its place.

Redundant objects should be removed.

A scene may contain one subtle accent detail if it adds charm,
specificity, or observation without becoming a second storyline.

Do not force an accent detail.

Do not rely on written text, signage, labels, or event titles to make
the scene understandable.

==================================================
REPRESENTATION STRATEGY
==================================================

Choose the most accurate strategy for each candidate from:

- human_action_scene
- human_object_interaction
- multi_person_interaction
- occupational_figure
- object_centered_scene
- symbolic_object_composition
- iconic_object_collage
- prepared_environment
- environment_led_scene
- decorative_atmosphere_scene

Different candidates should use genuinely different strategies when
the concept supports them.

Do not force diversity when the concept has low representation
optionality.

==================================================
RECOGNITION STRUCTURE
==================================================

Describe how the viewer recognizes the concept using one of:

- concentrated
- dominant_anchor_with_support
- distributed_symbolic
- distributed_functional
- distributed_iconic
- distributed_narrative
- relational
- contextual
- mixed

This field should describe the scene you actually imagined.

Do not mechanically choose a recognition structure first and then
construct a scene merely to satisfy it.

==================================================
ENVIRONMENT STRATEGY
==================================================

For environment_strategy, use exactly one of:

- omitted
- abstract
- partial_context
- semantic_environment
- simplified_literal
- narrative_environment

This describes how environmental context functions in the already
imagined scene.

Do not place representation-strategy values such as
"prepared_environment" or "environment_led_scene" in this field.

==================================================
SEMANTIC SCOPE
==================================================

For semantic_scope, use exactly one of:

- matched_scope
- narrowed_instance
- broader_neighboring_domain
- mixed_breadth
- uncertain

Do not write a sentence in this field.

The visual_thesis, subject, action, and simulation fields already
describe the particular interpretation.

==================================================
CANDIDATE IDENTITY CONSISTENCY
==================================================

The representation_strategy and recognition_structure are part of the
candidate's identity.

A property listed under may_adjust must NOT be allowed to transform the
candidate into a different representation strategy or recognition
structure.

For example:

- a multi_person_interaction candidate cannot say that reducing the
  scene to one person is freely adjustable if the interaction between
  multiple people is what defines that candidate;

- an object_centered_scene cannot permit later addition of a dominant
  human action if that would replace its object-centered identity.

When such a change would alter the candidate's fundamental strategy,
put the defining property in must_preserve instead.

==================================================
SHALLOW SCENE SIMULATION
==================================================

For EVERY candidate, mentally picture the scene before accepting it.

You must simulate enough of the image to test whether it really works.

1. VISUAL THESIS

State the picture in one concise sentence.

The thesis should describe an image, not merely an event category.

2. VIEW ANGLE

Choose a plausible view angle for this candidate.

This is allowed here because viewpoint may determine whether the scene
is visually coherent.

Examples include:

- strict overhead,
- frontal,
- side view,
- three-quarter view,
- slightly elevated,
- simplified perspective view.

Do not choose a viewpoint because a reference used it.
Choose it because this candidate's objects and actions read well from
that viewpoint.

3. ELEMENT-BY-ELEMENT READABILITY

Imagine every proposed visible element from the chosen viewpoint.

For each SceneElement, ask:

- Is the silhouette understandable?
- Is the action understandable?
- Does the object still look like itself from this angle?
- Does it duplicate information already supplied by another element?
- Is it necessary?

Set keep=false when an element is visually weak, redundant, or
unnecessary.

Do not preserve an element merely because it is strongly associated
with the real-world activity.

4. RECOGNITION ANCHOR

Identify what the viewer will notice or understand first.

A candidate may use:

- one dominant recognition anchor,
- several distributed cues,
- a relational interaction,
- or environmental context.

The anchor must actually be sufficient to carry the intended concept.

5. ROUGH LAYOUT

Imagine a simple verbal thumbnail.

Specify enough spatial organization to prove the scene can exist as a
picture.

For example:

"tray right-center; cropped bowl upper-left; diagonal whisk lower-left"

or:

"worker and cart center-right; vehicle enters from right edge;
small residential forms extend across background"

This is a shallow compositional simulation, NOT final art direction.

Do not yet optimize visual weight, color, detailed framing, or graphic
style.

6. DELIBERATE OMISSIONS

Explicitly state meaningful things that you chose NOT to depict.

Examples:

- person,
- literal kitchen,
- redundant flour,
- audience,
- complete room,
- extra decorative objects.

Omission is a design decision.

7. RISKS

Separate:

DESIGN RISKS:
The scene itself may be unclear or semantically weak.

RENDERER RISKS:
The scene is sound in principle but may be difficult for an image
model to draw reliably.

Do not reject a strong scene merely because rendering may require care.

==================================================
CANDIDATE IDENTITY
==================================================

For each candidate, define:

must_preserve:
The properties that make this visual direction fundamentally itself.

may_adjust:
Properties that later art direction may refine without changing the
candidate's identity.

This protects genuinely different candidates from converging into the
same image later.

==================================================
REFERENCE USE
==================================================

You may receive a small set of Google Calendar visual references.

They are DESIGN EVIDENCE.

Use them to learn abstract patterns such as:

- how recognition can be distributed,
- whether people are necessary,
- how much context can be omitted,
- how a viewpoint supports recognition,
- how semantic scale may work,
- how simplified scenes communicate an event.

Do NOT:

- reproduce a reference scene,
- copy its exact object set,
- copy its exact pose,
- copy its layout,
- copy its palette,
- transform one reference into the new concept.

The new scene must arise from the current concept.

References support reasoning.
They do not make the creative decision.

==================================================
IMPORTANT: DO NOT DESIGN LAYERS YET
==================================================

Do not decide:

- foreground/middle/background layer counts,
- visual plane hierarchy,
- layer-specific detail levels,
- layer-specific color hierarchy.

First invent a coherent picture.

Layer analysis happens only AFTER candidates survive curation.

==================================================
STYLE BOUNDARY
==================================================

You may make only the spatial decisions necessary to prove that the
candidate scene works.

Do not yet perform full art direction.

Do not finalize:

- color palette,
- shape language,
- rendering technique,
- lighting,
- texture,
- final cropping treatment,
- final scale exaggeration,
- final visual-weight hierarchy,
- layer hierarchy,
- decorative treatment.

Those decisions belong to the later Art Director.

==================================================
DIVERGENCE REQUIREMENT
==================================================

Return exactly the requested number of candidates.

The candidates are alternatives, not a ranked list.

Do not label one as best.

When representation optionality is high, explore substantially
different recognition strategies.

When representation optionality is low, prioritize coherence over
artificial diversity.

Each candidate must be independently understandable without explaining
why the other candidates exist.
""".strip(),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"""
Create exactly {candidate_count} candidate visual scenes.

EVENT
=====

Name:
{request.name}

Type:
{request.type}

Additional description:
{request.description or "None provided"}


CONCEPT INTERPRETATION
======================

{concept_json}


TASK
====

Generate {candidate_count} genuinely different candidate scenes.

For each candidate:

1. preserve the event's semantic specificity;
2. respect protected unknowns;
3. choose a coherent representation strategy;
4. imagine the actual picture;
5. choose a viewpoint that makes its elements readable;
6. simulate each important visible element;
7. identify the recognition anchor;
8. describe a rough layout;
9. state deliberate omissions;
10. separate design risk from renderer risk;
11. define must_preserve and may_adjust.


Do not perform layer analysis yet.

The candidate IDs must be:

candidate_1
candidate_2
candidate_3
...

in order.
""".strip(),
                    },
                    *reference_content,
                ],
            },
        ],
        text_format=CandidateScenePool,
    )

    pool = response.output_parsed

    if len(pool.candidates) != candidate_count:
        raise ValueError(
            "Creative planner returned "
            f"{len(pool.candidates)} candidates; "
            f"expected {candidate_count}."
        )

    expected_ids = [
        f"candidate_{i}"
        for i in range(1, candidate_count + 1)
    ]

    actual_ids = [
        candidate.id
        for candidate in pool.candidates
    ]

    if actual_ids != expected_ids:
        raise ValueError(
            "Creative planner returned unexpected candidate IDs. "
            f"Expected {expected_ids}, got {actual_ids}."
        )

    print(
        f"Generated {candidate_count} candidate scenes "
        f"for {request.name}:"
    )
    print(
        pool.model_dump_json(indent=2)
    )

    return pool
