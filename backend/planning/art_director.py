from __future__ import annotations

import json

from config import TEXT_MODEL
from openai_client import get_openai_client
from planning.schemas import (
    CandidateScene,
    FinalScenePlan,
    ReferencePacket,
)
from references.multimodal import build_reference_content
from styles import StyleProfile


def _format_principles(
    principles: list[str],
) -> str:
    if not principles:
        return "- No additional principles specified."

    return "\n".join(
        f"- {principle}"
        for principle in principles
    )


def art_direct_scene(
    candidate: CandidateScene,
    style_profile: StyleProfile,
    reference_packet: ReferencePacket | None = None,
    refinement_requests: list[str] | None = None,
) -> FinalScenePlan:
    """
    Convert one already-viable CandidateScene into a complete
    style-specific FinalScenePlan.

    The candidate supplies the scene identity.
    The StyleProfile supplies stable style grammar.
    References supply optional precedent.

    The Art Director resolves scene structure and renderable staging
    without changing the candidate into a different idea.
    """

    client = get_openai_client()

    candidate_json = json.dumps(
        candidate.model_dump(mode="json"),
        indent=2,
        ensure_ascii=False,
    )

    refinement_requests = (
        refinement_requests
        or []
    )

    refinement_text = (
        "\n".join(
            f"- {item}"
            for item in refinement_requests
        )
        if refinement_requests
        else "- No additional curator refinements."
    )

    reference_content = build_reference_content(
        reference_packet
    )

    response = client.responses.parse(
        model=TEXT_MODEL,
        input=[
            {
                "role": "system",
                "content": """
You are the Art Director for a calendar illustration pipeline.

A Creative Planner has already invented the scene, and a Candidate
Curator has already determined that this visual direction is viable.

Your task is to turn that existing candidate into a complete,
style-specific FinalScenePlan.

You may resolve staging, composition, depth, scale, cropping, color,
shape, detail, and rendering treatment.

You must not replace the candidate with a different visual idea.


==================================================
SOURCES OF TRUTH
==================================================

Use the inputs according to these roles:

1. CANDIDATE

   The candidate is the source of scene identity and semantic content.

   Preserve:
   - visual thesis,
   - representation strategy,
   - recognition structure,
   - content constraints,
   - must_preserve properties.

   may_adjust identifies genuine flexibility, not permission to change
   the candidate into another representation.


2. CURATOR REFINEMENTS

   These identify local weaknesses to solve while keeping the same
   candidate.


3. STYLE PROFILE

   The StyleProfile is the authority for stable visual grammar such as
   composition tendencies, color behavior, shape language, human
   treatment, density, and rendering treatment.


4. REFERENCES

   References are visual precedents. They may inform how a design
   problem is handled, but they do not define the scene and must not be
   copied.


If guidance conflicts, preserve the candidate's semantic identity and
hard constraints first.

References never override the candidate or the StyleProfile.


==================================================
ART-DIRECTION PROCEDURE
==================================================

Work from the already-planned picture outward.


------------------------------------------
1. PRESERVE AND SIMPLIFY THE SCENE
------------------------------------------

Start from the candidate's subject, action, setting, viewpoint,
recognition anchor, rough layout, kept scene elements, and deliberate
omissions.

Retain the elements necessary for recognition and candidate identity.

You may omit secondary elements when doing so improves clarity.

selected_objects should describe the objects actually visible in the
final plan. Prefer elements already marked keep=true.

Do not add a new semantically important person, object, setting,
relationship, occasion, profession, recipe, or storyline merely
because it is associated with the event.

A structural part that is already implied by an approved object or
action may be made explicit when necessary to depict that object or
action coherently.


------------------------------------------
2. INFER SCENE STRUCTURE
------------------------------------------

Analyze the spatial organization already implied by the candidate.

Scene structure is descriptive before it is prescriptive.

Identify the minimum set of meaningful visual planes needed to describe
the scene.

A plane is a coherent spatial or semantic field with a distinct role in
the picture. Several objects may belong to one plane.

Do not:
- begin with a preferred layer count,
- add content to manufacture depth,
- count every object as a layer,
- count a plain base background as a separate layer merely because it
  has a color,
- split parts of one object into separate layers unless they function as
  meaningfully distinct spatial planes.

A background or context field may count as a layer when it carries
actual spatial or semantic information.

Use:
- one layer for an essentially flat scene,
- multiple layers only when the existing scene genuinely contains
  distinct spatial or semantic planes.

For SceneStructure:
- depth_strategy describes how space is organized;
- depth_layer_count must equal the number of SceneLayer entries;
- depth_span describes the amount of spatial separation;
- perspective_strategy describes only the spatial logic actually used;
- spatial_coherence briefly explains why the planes form one scene.

SceneLayer indices must begin at 1 and increase consecutively.

After the layers are identified, create exactly one LayerTreatment for
each SceneLayer.

Layer treatment should follow semantic priority:
- primary content may receive the strongest diagnostic detail and
  separation;
- supporting content should generally compete less strongly;
- tertiary context should generally be quieter still.

These are priorities, not a required foreground-middle-background
formula.


------------------------------------------
3. RESOLVE COMPOSITION AND FRAMING
------------------------------------------

Complete the graphic organization of the existing scene.

composition_structure:
Describe the major spatial arrangement.

visual_weight_distribution:
Describe how major visual mass is distributed and balanced.

salience_structure:
Describe what should be noticed first and what supports it.

negative_space_strategy:
Describe where breathing room is preserved and what purpose it serves.

directional_flow:
Describe the eye path or the implied movement through the scene.

framing_scale:
Describe how close or broad the framing should feel.

cropping_strength:
Describe the intended amount of frame intersection.

edge_continuation:
Describe which forms, if any, plausibly continue beyond the frame.

Cropping may be strong when useful, but preserve the diagnostic parts
required for recognition.


------------------------------------------
4. RESOLVE SCALE AND SPACE
------------------------------------------

Naturalistic scale is not mandatory.

Use scale according to the candidate and StyleProfile.

Scale changes should serve recognition, hierarchy, framing, or
narrative clarity rather than exist for stylistic novelty.

scale_source should identify the main logic controlling perceived
scale, such as:
- naturalistic object relationships,
- semantic exaggeration,
- perspective,
- framing,
- visual equivalence,
- mixed.

Do not introduce dramatic scale changes when the candidate works better
without them.


------------------------------------------
5. TRANSLATE THE SCENE INTO THE STYLE
------------------------------------------

Apply the supplied StyleProfile to the already-resolved scene.

Use the StyleProfile rather than inventing a second style grammar inside
this prompt.

color_direction:
Describe the functional use of color for separation, hierarchy, and
coherence. Do not copy a reference palette.

shape_direction:
Describe how forms should be simplified while retaining diagnostic
structure.

detail_direction:
Allocate specificity according to semantic importance. Supporting
elements may be simpler than primary recognition cues.

human_direction:
If people are present, preserve their semantic role and depict only the
amount of person needed by the scene.

Do not infer unsupported identity-specific traits.

If the candidate contains no people, do not add them merely for
liveliness.

nonliteral_direction:
Use nonliteral devices only when they strengthen the candidate's
existing recognition logic.

Examples may include:
- semantic scale,
- simplified spatial relationships,
- visual equivalence,
- decorative abstraction.

If none is useful, say so.

Rendering treatment should follow the StyleProfile.

When the profile is sparse, use restrained, internally coherent
illustration judgment without inventing a named external style.


==================================================
REFERENCE USE
==================================================

Study supplied references only for abstract precedent such as:
- spatial organization,
- depth strategy,
- cropping,
- semantic scale,
- hierarchy,
- simplification,
- distribution of detail.

Do not copy:
- the exact scene,
- object set,
- pose,
- composition,
- palette,
- or narrative.

The candidate remains the source of the new scene.


==================================================
CURATOR REFINEMENTS
==================================================

Treat curator refinement requests as local design problems.

Solve them within the existing candidate.

Do not use them as permission to change the representation strategy,
recognition structure, temporal moment, or semantic identity.


==================================================
OUTPUT
==================================================

Return one FinalScenePlan.

Be specific enough that a deterministic prompt compiler can translate
the result into a renderer prompt without making new creative
decisions.

Be concise.

Do not explain alternatives.

Do not rank this candidate against other candidates.
""".strip(),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"""
ART-DIRECT THIS EXISTING CANDIDATE.


CANDIDATE
=========

{candidate_json}


CURATOR REFINEMENT REQUESTS
===========================

{refinement_text}


STYLE PROFILE
=============

Style ID:
{style_profile.id}

Style name:
{style_profile.name}

Description:
{style_profile.description}

Composition principles:
{_format_principles(style_profile.composition_principles)}

Scale principles:
{_format_principles(style_profile.scale_principles)}

Cropping principles:
{_format_principles(style_profile.cropping_principles)}

Perspective principles:
{_format_principles(style_profile.perspective_principles)}

Human principles:
{_format_principles(style_profile.human_principles)}

Scene-density principles:
{_format_principles(style_profile.scene_density_principles)}

Color principles:
{_format_principles(style_profile.color_principles)}

Shape principles:
{_format_principles(style_profile.shape_principles)}

Rendering principles:
{_format_principles(style_profile.rendering_principles)}


TASK
====

Resolve this candidate into one complete FinalScenePlan using the
candidate, curator refinements, StyleProfile, and any supplied visual
precedents according to the roles defined above.
""".strip(),
                    },
                    *reference_content,
                ],
            },
        ],
        text_format=FinalScenePlan,
    )

    plan = response.output_parsed

    # -----------------------------------------------------
    # Restore hard invariants from the candidate/style.
    # -----------------------------------------------------

    plan = plan.model_copy(
        update={
            "candidate_id": candidate.id,
            "style_id": style_profile.id,
            "visual_thesis": candidate.visual_thesis,
            "representation_strategy": candidate.representation_strategy,
            "recognition_structure": candidate.recognition_structure,
            "subject": candidate.subject,
            "setting": candidate.setting,
            "action": candidate.action,
            "content_constraints": candidate.content_constraints,
            "must_preserve": candidate.simulation.must_preserve,
            "may_adjust": candidate.simulation.may_adjust,
        }
    )

    # The Art Director may omit an existing accent detail, but it must
    # not invent one when the candidate had none.
    if candidate.accent_detail is None:
        plan = plan.model_copy(
            update={
                "accent_detail": None,
            }
        )

    # -----------------------------------------------------
    # Structural validation.
    # -----------------------------------------------------

    layers = plan.scene_structure.layers

    if (
        plan.scene_structure.depth_layer_count
        != len(layers)
    ):
        raise ValueError(
            "depth_layer_count does not match the number "
            "of SceneLayer entries."
        )

    expected_indices = list(
        range(
            1,
            len(layers) + 1,
        )
    )

    actual_indices = [
        layer.index
        for layer in layers
    ]

    if actual_indices != expected_indices:
        raise ValueError(
            "SceneLayer indices must begin at 1 and increase "
            f"consecutively. Got {actual_indices}."
        )

    treatment_indices = [
        treatment.layer_index
        for treatment in plan.layer_treatments
    ]

    if treatment_indices != expected_indices:
        raise ValueError(
            "LayerTreatment entries must correspond exactly to "
            f"SceneLayer indices {expected_indices}. "
            f"Got {treatment_indices}."
        )

    print(
        f"Generated {style_profile.id} FinalScenePlan "
        f"for {candidate.id}:"
    )

    print(
        plan.model_dump_json(
            indent=2
        )
    )

    return plan