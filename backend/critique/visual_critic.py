from __future__ import annotations

from pathlib import Path

from config import TEXT_MODEL
from openai_client import get_openai_client
from planning.schemas import (
    ConceptBrief,
    ConceptRequest,
    FinalScenePlan,
    PreliminaryCritique,
    VisualInspection,
)
from references.multimodal import (
    image_path_to_data_url,
)
from styles import get_style_profile


def _format_principles(
    principles: list[str],
) -> str:
    if not principles:
        return "- None specified."

    return "\n".join(
        f"- {item}"
        for item in principles
    )


def inspect_rendered_image(
    image_path: str | Path,
) -> VisualInspection:
    """
    Pass 1.

    Inspect rendered evidence before revealing the concept or scene
    plan.

    The critic understands Google Calendar visual language, so it does
    not confuse deliberate abstraction with rendering mistakes.
    """

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Rendered image not found: {path}"
        )

    style = get_style_profile(
        "google_calendar"
    )

    client = get_openai_client()

    response = client.responses.parse(
        model=TEXT_MODEL,
        input=[
            {
                "role": "system",
                "content": f"""
This project's goal is to generate customized images for Google Calendar events.
Right now, certain keywords such as "lunch" or "bbq" triggers default illustrations,
and our goal is to generate Google Calendar style illustrations for more user-defined events.

Your role:
You are the perceptual reviewer for this illustration
pipeline.

You see the rendered image BEFORE being told its intended concept,
scene, or FinalScenePlan.

Please note that, because our goal is to generate images that imitate the style of
Google Calendar's default images, as a reviewer, you need to be familiar with some
characteristics of Google Calendar's style and review the images while taking these
principles into consideration.

==================================================
CORE Google Calendar Illustration Characteristics
==================================================

Google Calendar illustrations may deliberately use:

- tiny people beside giant objects (not physical realism);
- semantic exaggeration of scale;
- reduced facial features;
- simplified anatomy;
- strongly cropped people and objects;
- shallow or compressed space;
- simplified perspective;
- abstract environmental planes;
- decorative shapes;
- nonliteral spatial relationships;
- graphic motion
- artistic but unrealistic color themes.

Do not treat those as mistakes merely because they are unrealistic.

Instead distinguish:

DELIBERATE ABSTRACTION
from
ACCIDENTAL VISUAL BREAKAGE.

==================================================
RENDERED EVIDENCE IS PRIMARY
==================================================

Describe what the IMAGE ACTUALLY SHOWS.

Later stages may reveal what the plan intended.

Your observations must remain valid even if later textual instructions
claim something different.

If body coverage is visually ambiguous, record it as ambiguous.

If a face appears omitted, record it as omitted.

If two forms appear fused, record that visual relationship.

Do not infer that something is present simply because it would make
sense for the scene.

==================================================
HUMAN OBSERVATION
==================================================

For every clearly visible human figure, explicitly record:

- face treatment;
- body coverage;
- whether visible exposure could become awkward;
- anatomical coherence.

Important:

A simplified or omitted face is NOT automatically a problem.

Partially exposed skin is NOT automatically a problem.

These fields are perceptual observations first.

But do not sanitize what you see.

If a torso is substantially exposed, say so.

If clothing versus skin is unclear, use "unclear".

If a simplified figure nevertheless feels coherent, say
"stylized_but_coherent".

==================================================
OTHER THINGS TO NOTICE
==================================================

Inspect:

- hand-object contact;
- disconnected objects;
- accidental intersections;
- duplicated or malformed forms;
- broken spatial relationships;
- perspective that looks accidental rather than stylized;
- unclear grounding;
- visual hierarchy;
- cropping;
- clutter;
- accidental emptiness;
- generic stock-vector appearance;
- rendering that feels overly dimensional;
- useful abstraction;
- expressive graphic gestures;
- active negative space;
- memorable visual relationships.

Do not redesign the scene.

Do not invent missing props.

Do not assume something is wrong merely because you are the critic.

==================================================
STYLE PROFILE
==================================================

Composition:
{_format_principles(style.composition_principles)}

Scale:
{_format_principles(style.scale_principles)}

Cropping:
{_format_principles(style.cropping_principles)}

Perspective:
{_format_principles(style.perspective_principles)}

Humans:
{_format_principles(style.human_principles)}

Density:
{_format_principles(style.scene_density_principles)}

Color:
{_format_principles(style.color_principles)}

Shape:
{_format_principles(style.shape_principles)}

Rendering:
{_format_principles(style.rendering_principles)}

Return one VisualInspection.
""".strip(),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Inspect this rendered illustration. "
                            "Describe what is visibly present before "
                            "knowing what it was intended to depict."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": (
                            image_path_to_data_url(
                                str(path)
                            )
                        ),
                        "detail": "high",
                    },
                ],
            },
        ],
        text_format=VisualInspection,
    )

    inspection = response.output_parsed

    print("\nSTYLE-AWARE VISUAL INSPECTION")
    print("=============================")

    print(
        inspection.model_dump_json(
            indent=2
        )
    )

    return inspection


def critique_rendered_image(
    image_path: str | Path,
    request: ConceptRequest,
    concept_brief: ConceptBrief,
    plan: FinalScenePlan,
    inspection: VisualInspection,
) -> PreliminaryCritique:
    """
    Pass 2.

    Interpret perceptual evidence using the intended concept and
    FinalScenePlan.

    The scene plan explains intent but may not override visible image
    evidence.
    """

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Rendered image not found: {path}"
        )

    style = get_style_profile(
        "google_calendar"
    )

    client = get_openai_client()

    response = client.responses.parse(
        model=TEXT_MODEL,
        input=[
            {
                "role": "system",
                "content": f"""
You are the senior critique reasoner for a Google Calendar
illustration pipeline.

A perceptual reviewer has already inspected the image without knowing
its intended concept.

You now know:

- the intended concept;
- its semantic interpretation;
- the FinalScenePlan;
- the perceptual inspection.

==================================================
NON-NEGOTIABLE EVIDENCE RULE
==================================================

RENDERED IMAGE EVIDENCE OUTRANKS PLANNED INTENT.

The FinalScenePlan tells you what SHOULD have happened.

It is not proof of what DID happen.

For example:

If the plan says a person is covered but the perceptual inspection
shows substantial or ambiguous body exposure, you may NOT simply
declare that the person is fully covered.

Instead discuss the discrepancy.

If the plan calls for flat rendering but the image contains gradients,
the image evidence wins.

Use the plan to interpret intention, never to erase visible evidence.

==================================================
RESPONSIBILITY 1 — COHERENCE
==================================================

Evaluate:

- visual coherence;
- real-world action logic;
- semantic readability;
- human-object relationships;
- object use;
- unintended implications;
- unnecessary body exposure;
- awkward human treatment;
- missing information genuinely required for the action.

Do not demand every object commonly associated with an activity.

A fishing scene does not automatically need bait.

A yoga scene does not automatically need plants or candles.

Differentiate:

required correction,
clarity improvement,
style improvement,
optional enrichment.

==================================================
RESPONSIBILITY 2 — ARTISTIC SUCCESS
==================================================

Do NOT equate simplicity with good design.

Explicitly distinguish:

DESIGNED MINIMALISM
from
UNDER-DESIGN.

Ask:

What is the visual hook?

What makes this scene more than a competent stock illustration of the
activity?

Is the negative space actively participating in the composition, or is
it merely unused background?

Is simplification revealing a strong visual idea, or merely removing
detail?

Does the image contain a memorable scene-specific device such as:

- semantic scale;
- unusual cropping;
- expressive directional movement;
- an interesting object relationship;
- decorative abstraction;
- repetition;
- playful spatial compression;
- meaningful incidental detail;
- active negative space;
- a strong silhouette or shape interaction;
- another concept-specific visual idea?

A scene does NOT need several such devices.

One strong idea may be enough.

Fishing, for example, might already be artistically complete if the
casting line itself creates a memorable graphic gesture.

Do not add decoration just to make the illustration busier.

==================================================
FAILURE ORIGIN
==================================================

For each issue identify the earliest likely level that needs to change.

render_execution:
The existing design is sound but the image generator executed it
poorly.

Examples:
- malformed hand;
- weak contrast;
- unwanted gradient;
- accidental intersection.

art_direction:
The underlying scene can remain, but composition, abstraction,
cropping, decorative treatment, hierarchy, scale, or visual interest
needs redesign.

scene_concept:
The chosen representation itself creates the problem.

Examples:
- a massage representation creates avoidable awkward exposure;
- a scene choice is semantically weak;
- another representation strategy would communicate the same concept
  more appropriately.

Do not escalate unnecessarily.

==================================================
REFERENCE FOCUS
==================================================

You are NOT yet being shown critique references.

If there is an artistic, compositional, abstraction, Google-style, or
representation question, describe what evidence would be useful in
reference_focus.

Focus on DESIGN DIMENSIONS, not matching concept names.

Good examples:

- sparse human-action scenes with strong graphic interest
- decorative abstraction around an anonymous figure
- active negative space in wide compositions
- human interaction without bodily emphasis
- partial-body representations
- semantic enlargement of diagnostic objects
- simplified environments with incidental artistic details
- nonliteral spatial organization

If all issues are straightforward execution defects,
reference_focus may be empty.

==================================================
STYLE PROFILE
==================================================

Composition:
{_format_principles(style.composition_principles)}

Scale:
{_format_principles(style.scale_principles)}

Cropping:
{_format_principles(style.cropping_principles)}

Perspective:
{_format_principles(style.perspective_principles)}

Humans:
{_format_principles(style.human_principles)}

Density:
{_format_principles(style.scene_density_principles)}

Color:
{_format_principles(style.color_principles)}

Shape:
{_format_principles(style.shape_principles)}

Rendering:
{_format_principles(style.rendering_principles)}

Return one PreliminaryCritique.
""".strip(),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"""
REQUEST
=======

{request.model_dump_json(indent=2)}


CONCEPT BRIEF
=============

{concept_brief.model_dump_json(indent=2)}


FINAL SCENE PLAN
================

{plan.model_dump_json(indent=2)}


PLAN-BLIND PERCEPTUAL INSPECTION
================================

{inspection.model_dump_json(indent=2)}


TASK
====

Reconcile intention with rendered evidence.

Remember:

IMAGE EVIDENCE > PLAN INTENT.

Evaluate logical coherence, semantic success, human treatment,
artistic interest, Google Calendar language, and the likely pipeline
origin of each issue.

Explicitly identify the scene's visual hook.

If no meaningful visual hook exists, say so rather than interpreting
mere sparseness as elegant minimalism.

Describe any design evidence that should be retrieved before making a
final style/art-direction judgment.
""".strip(),
                    },
                    {
                        "type": "input_image",
                        "image_url": (
                            image_path_to_data_url(
                                str(path)
                            )
                        ),
                        "detail": "high",
                    },
                ],
            },
        ],
        text_format=PreliminaryCritique,
    )

    critique = response.output_parsed

    print("\nPRELIMINARY CONTEXTUAL CRITIQUE")
    print("===============================")

    print(
        critique.model_dump_json(
            indent=2
        )
    )

    return critique
