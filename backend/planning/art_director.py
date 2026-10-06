from __future__ import annotations
import base64
import json
import re
from pathlib import Path
from config import TEXT_MODEL
from openai_client import get_openai_client
from planning.schemas import (
    CandidateScene,
    FinalScenePlan,
    ReferencePacket,
)
from references.multimodal import build_reference_content
from styles import StyleProfile
REFERENCE_IMAGE_DIR = (
    Path(__file__).resolve().parents[1]
    / "references"
    / "google_calendar"
    / "rendered"
)
TEACHING_IMAGES = {
    "vote": REFERENCE_IMAGE_DIR / "img_vote.png",
    "babyshower": REFERENCE_IMAGE_DIR / "img_babyshower.png",
    "doctor": REFERENCE_IMAGE_DIR / "img_doctor.png",
    "bowling": REFERENCE_IMAGE_DIR / "img_bowling.png",
    "cinema": REFERENCE_IMAGE_DIR / "img_cinema.png",
}
TEACHING_IMAGE_PATTERN = re.compile(
    r"\[\[TEACHING IMAGE:\s*([a-z0-9_-]+)\]\]"
)
ART_DIRECTOR_SYSTEM_PROMPT = """
You are the Art Director for a customized calendar illustration pipeline.
Follow the Art Director instructions, authority rules, teaching examples,
and output requirements supplied in the following multimodal message.
Return the requested structured FinalScenePlan.
""".strip()
ART_DIRECTOR_PROMPT = """
You are the Art Director for a customized illustration pipeline for calendar events.
A Creative Planner has already invented what the scene should depict:
its subject, setting, action, human presence, and overall semantic idea.
Your task is to transform that planned scene content into a complete,
visually coherent, and aesthetically effective illustration plan without
turning it into a different idea.
You may resolve staging, composition, depth, scale, cropping, color,
shape, detail, and rendering treatment.

==================================================
SOURCES OF TRUTH
==================================================

Use the inputs according to these roles:

1. CANDIDATE
   The candidate is the current plan for what the illustration depicts
   and for the semantic identity of the scene.
   Use it to determine:
   - the visual thesis,
   - subject,
   - setting,
   - action,
   - human presence,
   - representation strategy,
   - recognition structure,
   - environment strategy,
   - and the intended scene content described in scene_description.
   The Art Director may simplify or reorganize how this content is
   presented, but must stay faithful to the scene's ability to communicate
   the intended concept.

2. STYLE PROFILE
   The StyleProfile is the authority for stable visual grammar of the illustration,
   in order to enable the pipeline's ability to generate images in a selection of
   art styles.
   Use it to guide:
    - composition tendencies,
    - scale and cropping behavior,
    - spatial and perspective behavior,
    - environment treatment,
    - depiction of people,
    - motion treatment,
    - scene density,
    - color behavior,
    - shape language,
    - decorative and nonliteral treatment,
    - and rendering treatment.

3. REFERENCES
   References are existing illustrations of some concept.
   Use them to study how related illustrations solve problems such as:
   - spatial organization,
   - depth,
   - cropping,
   - hierarchy,
   - scale,
   - simplification,
   - and distribution of detail.

   They are also visual references for what the style profile tries to
   communicate textually, so please also use them to study art decisions
   like:
   - composition tendencies,
   - color behavior,
   - shape language,
   - depiction of people,
   - scene density,
   - decorative/artistic elements,
   - and rendering treatment.

If style_profile and candidate conflict, preserve the candidate's
semantic identity and hard constraints first.

==================================================
ART-DIRECTION PROCEDURE
==================================================

Transform the candidate into one coherent visual presentation.
The procedure has two modes of reasoning:
- First, reason holistically about what makes the scene recognizable
  and what overall visual presentation would communicate it best.
- Then, resolve that chosen presentation into explicit structured
  art-direction decisions.
Do not treat composition, viewpoint, crop, depth, scale, environment,
or other visual properties as independent choices. They should support
the same presentation concept and work together as one picture.
The candidate remains the authority for the semantic identity of the
scene. Art direction may simplify, emphasize, crop, reorganize, or
stylize the candidate, but it must not turn it into a different idea.

--------------------------------------------------
1. DIAGNOSE THE VISUAL CORE
--------------------------------------------------

Before designing the image, determine what actually needs to be seen
for the candidate to be recognized quickly and correctly.

recognition_plan
================
Describe which visible elements, actions, interactions, or
relationships carry recognition of the intended concept, and explain
how recognition is distributed among them.
Recognition may be:
- concentrated in one diagnostic element or interaction,
- shared by several mutually supporting elements,
- distributed across a collection of symbolic or contextual cues,
- carried primarily by a person or action,
- carried primarily by objects,
- carried jointly by a subject and its environment,
- or organized in another way appropriate to the candidate.

Do not assume that every scene has one dominant recognition object.
The candidate's recognition_structure is useful guidance about the
general organization of recognition. recognition_plan should make that
logic concrete for this particular scene.

TEACHING EXAMPLE — CONCENTRATED RECOGNITION

Vote:
Recognition is concentrated in the interaction between the hand,
ballot, and slot. The rest of the person and a complete polling
environment are unnecessary for recognizing the action.
[[TEACHING IMAGE: vote]]

TEACHING EXAMPLE — DISTRIBUTED RECOGNITION
Baby Shower:
Recognition is distributed across several complementary symbolic cues,
including the stork-and-bundle, teddy bear, blocks, and toy-train
structure. No single object needs to carry the entire concept.
[[TEACHING IMAGE: babyshower]]

These examples demonstrate different recognition strategies.
Do not copy their subjects, compositions, or object sets unless they
are independently appropriate for the current candidate.

--------------------------------------------------
2. EXPLORE INTEGRATED PRESENTATION CONCEPTS
--------------------------------------------------

Before committing to detailed composition, briefly consider multiple
substantially different ways of presenting the same candidate.
Usually consider 2 or 3 possibilities internally.

A presentation concept is not a list of isolated settings such as:
- strong crop,
- shallow depth,
- side viewpoint.

Instead, it is an integrated visual idea explaining how the image
should present its recognition plan.

A presentation concept may use:
- diagnostic cropping,
- unusual or highly purposeful viewpoint,
- semantic or perspective-driven scale,
- concentrated interaction,
- repeated visual units,
- distributed symbolic organization,
- selective environmental context,
- deliberate omission,
- foreground framing,
- strong negative space,
- nonliteral spatial organization,
- or another visual strategy that serves the candidate.

Cropping, viewpoint, scale, composition, depth, environment, and
spatial simplification may themselves be central parts of the
presentation concept.

The strategies above are examples, not an exhaustive library.
You may combine them, adapt them, or use another strategy when it
better serves the candidate.

TEACHING EXAMPLE — DIAGNOSTIC CROP
Doctor:
Concentrate the illustration on the part of the person containing the
strongest occupational cues: the medical coat, stethoscope, and badge.
The crop removes the face, full body, and unnecessary clinical
environment so that the diagnostic region carries the concept.
[[TEACHING IMAGE: doctor]]

TEACHING EXAMPLE — PERSPECTIVE AS PRESENTATION
Bowling:
Place the viewer near the pins. Large foreground pins, a tapered lane,
a small distant bowler, strong cropping, and near/far scale work
together to make the impact moment the organizing idea of the image.
[[TEACHING IMAGE: bowling]]

TEACHING EXAMPLE — NONLITERAL SEMANTIC COLLAGE
Cinema:
Instead of constructing a literal theater, combine several
cinema-related objects in a shallow conceptual field. Camera, film
strip, popcorn, scale variation, overlap, and abstract light forms
collectively create the visual world.
[[TEACHING IMAGE: cinema]]

These are lessons in visual problem solving, not templates.
Do not reproduce their exact composition, crop boundary, pose,
palette, scale relationship, or object arrangement.

--------------------------------------------------
3. SELECT THE PRESENTATION CONCEPT AND CONTENT
--------------------------------------------------

Choose the strongest presentation concept for the current candidate.
Prefer the concept that best balances:

- semantic clarity,
- rapid recognizability,
- visual economy,
- visual interest,
- coherence with the candidate,
- compatibility with the StyleProfile,
- and useful lessons from the supplied references.

The strongest concept is not necessarily the most literal one.
Do not return the rejected alternatives.

presentation_concept
====================
Describe the chosen integrated visual idea in concise free text.
Explain the organizing idea of the picture and the main visual
strategy through which the recognition_plan will be communicated.
The presentation_concept should be specific enough that later
structured decisions can clearly be understood as consequences of it.

content_selection.visible_elements
==================================
List the semantically meaningful people, objects, environmental cues,
graphic elements, and other content that should actually appear in
the final illustration.
Prefer content already supported by the candidate.
You may make a structural component explicit when it is naturally
implied by an approved object or action and is necessary for coherent
depiction.
A new supporting element may be introduced only when it effectively
improves the chosen presentation while remaining faithful to the
candidate's semantic identity.

content_selection.intentional_omissions
=======================================
List plausible scene elements that are deliberately excluded because
they are unnecessary for recognition, compete with the chosen
presentation concept, create clutter, or encourage an overly literal
scene.
Omission is an active design decision.
Do not remove an element required by the candidate or by the
recognition_plan.

--------------------------------------------------
4. RESOLVE THE SELECTED CONCEPT
--------------------------------------------------
Now resolve the chosen presentation concept into explicit visual
decisions.
These fields are structured for clarity and downstream use, but they
must not be designed independently.
Resolve them together so that composition, viewpoint, framing, depth,
scale, environment, human staging, and relationships reinforce the
same presentation concept.

COMPOSITION
===========

composition.structure
---------------------
Describe the major spatial organization of the image.
Explain the important anchors, clusters, repeated units, major zones,
framing elements, or other large-scale compositional structures.
Do not merely enumerate every object.

composition.hierarchy_and_balance
---------------------------------
Describe what should receive the greatest visual emphasis, what should
support it, and how major visual masses should balance or deliberately
counterbalance one another.
Hierarchy should follow the recognition_plan and
presentation_concept.

composition.negative_space
--------------------------
Describe where relatively quiet or open space should be preserved and
what visual purpose it serves.

Negative space may support:
- hierarchy,
- movement,
- balance,
- isolation,
- breathing room,
- directionality,
- or another compositional purpose.
Do not add empty space mechanically when the scene benefits from a
dense composition.

composition.directional_flow
----------------------------
Describe the intended visual path through the image or the dominant
directional energy of the composition.
Directional flow may come from:
- body pose,
- object orientation,
- diagonals,
- repeated elements,
- gaze or gesture,
- environmental lines,
- perspective,
- negative space,
- or relationships among forms.
Static scenes may have weak or minimal directional flow.

FRAMING AND VIEW
================
framing_and_view.viewpoint
--------------------------
Describe where and how the viewer observes the scene.
Include relevant horizontal or vertical orientation, angle, elevation,
or other viewpoint information when it materially affects the image.
Use free description rather than forcing the scene into a predefined
camera category.

The viewpoint should serve the presentation concept rather than simply
defaulting to an eye-level full-scene view.

framing_and_view.framing
------------------------
Describe how tightly or broadly the scene is framed and which parts of
the scene dominate the visible image area.
Framing should reflect what the viewer actually needs to see.

framing_and_view.cropping_strength
----------------------------------
Choose one:
none
    Important forms are substantially contained within the frame.
light
    Minor edge intersections occur, but major subjects remain mostly
    contained.
moderate
    Cropping is clearly present and contributes to composition or
    continuity, while most primary recognition information remains
    visible.
strong
    Major people, objects, or environmental forms intentionally cross
    the frame and cropping materially shapes the composition.
very_strong
    Cropping deliberately isolates only part of a subject, action, or
    interaction and is itself an important recognition or presentation
    device.
Choose cropping according to the presentation concept.
Do not preserve complete objects or full human bodies merely for the
sake of completeness when a stronger crop communicates the concept
better.
Do not crop away information required by the recognition_plan.

framing_and_view.edge_continuation
----------------------------------
Describe which people, objects, environmental forms, or graphic
elements plausibly continue beyond the image boundaries, if any.
Also explain the purpose when useful, such as:
- implying a larger environment,
- increasing energy,
- creating foreground framing,
- or preventing the composition from feeling artificially contained.

SPATIAL PLAN
============
spatial_plan.depth_strategy
---------------------------
Choose the primary depth strategy:
near_flat
    Almost no meaningful spatial recession. The picture behaves mainly
    as a flat graphic, display, procession, diagram, or symbolic field.
shallow_overlap
    Spatial depth is limited and comes mainly from overlap, occlusion,
    and simple foreground/background ordering.
layered
    Several distinguishable spatial zones create meaningful depth,
    while the scene remains visually simplified rather than fully
    realistic.
perspective_driven
    Perspective, near/far scale difference, or directional recession
    plays a major role in constructing the image.
mixed
    More than one depth mechanism is equally important and no single
    strategy adequately describes the image.
custom
    Use when the selected presentation requires a spatial logic not
    represented above. Explain it clearly in spatial_relationships.
Examples from the teaching references:
- Baby Shower demonstrates near-flat organization.
- Doctor and Vote demonstrate very shallow overlap-based space.
- BBQ and Basketball demonstrate more layered organization.
- Bowling demonstrates perspective-driven depth.

spatial_plan.perspective_strategy
---------------------------------
Choose one:

absent
    Perspective is not meaningfully used.
minimal
    Small spatial cues suggest orientation, but perspective does not
    organize the picture.
limited_functional
    Simplified perspective contributes to readability or spatial logic
    without approaching realistic construction.
strong_simplified
    Perspective is a major organizing device but remains deliberately
    stylized or simplified.
custom
    Use when another perspective treatment better describes the chosen
    presentation. Explain it in spatial_relationships.

spatial_plan.spatial_relationships
----------------------------------
Describe the important spatial relationships that make the scene work.
Include only relationships that matter, such as:
- foreground versus background ordering,
- overlap and occlusion,
- near/far scale separation,
- one element framing another,
- subject embedded within environment,
- objects sharing a baseline,
- objects floating in a conceptual field,
- or other meaningful spatial organization.
Do not force the scene into a predetermined number of numbered layers.

SCALE PLAN
==========
scale_plan.strategy
-------------------

Choose the main scale logic:
naturalistic
    Relative sizes remain broadly plausible within the depicted world.
semantic_exaggeration
    Important elements are intentionally enlarged or reduced because
    semantic importance matters more than physical realism.
framing_driven
    Perceived size is controlled mainly by how closely the scene is
    framed.
perspective_driven
    Near/far placement and viewpoint primarily determine relative scale.
visual_equivalence
    Normally unequal elements are given roughly comparable prominence
    to support rhythm, recognition, or distributed importance.
compositional_variation
    Scale varies mainly to create rhythm, balance, or hierarchy within
    the composition rather than to represent literal physical size.
mixed
    Multiple scale logics are important.
custom
    Use when another scale logic better serves the presentation.

Examples:
- Art demonstrates semantic exaggeration.
- Bowling demonstrates perspective-driven scale.
- Doctor demonstrates framing-driven scale.
- Baby Shower demonstrates visual equivalence among symbolic units.

scale_plan.description
----------------------
Explain how scale should work specifically in this image.
Identify which elements, if any, should be enlarged, reduced, visually
equated, or allowed to dominate because of framing or perspective.
Do not introduce dramatic scale distortion merely for novelty.

ENVIRONMENT
===========
environment_plan
----------------
Describe how the candidate's environment_strategy should be realized
in the finished image.

Explain:
- how much environmental context should remain visible,
- which contextual cues are actually useful,
- how literal or abstract that context should become,
- how strongly it participates in recognition,
- and how the background supports the composition.

Do not independently replace the candidate's environment_strategy.
The environment may be:
- nearly omitted,
- represented through a small contextual fragment,
- simplified into a few diagnostic cues,
- transformed into an abstract or symbolic field,
- or made into an important part of the scene,
when that treatment is consistent with the candidate.

RELATIONSHIPS AND MOTION
========================
relationships_and_motion.key_relationships
------------------------------------------
List the important relationships among people, objects, and
environmental elements.
Describe relationships that materially contribute to recognition,
action, composition, or spatial understanding.
Examples include:
- hand contacting an object,
- person using or holding a tool,
- one figure framing another,
- repeated objects sharing a baseline,
- subject embedded in environment,
- foreground object overlapping a background element,
- one action causing another visual state.
Do not list relationships that have no visual or semantic importance.

relationships_and_motion.motion_plan
------------------------------------
If motion matters, describe how it should be communicated.
Motion may be conveyed through:
- pose,
- gesture,
- body lean,
- object orientation,
- interaction,
- repeated directional forms,
- environmental lines,
- perspective,
- scatter,
- hair or clothing movement,
- or selective graphic cues.
Do not assume that motion lines or blur are necessary.
Use null when the scene is genuinely static.

HUMAN STAGING
=============
If no people are present, human_staging may be null.
Human staging describes what portion of the person is shown and how
the person participates in the visual composition.
It is distinct from human_rendering_direction, which describes how the
person is stylistically rendered.

human_staging.body_visibility
-----------------------------
Choose one:

full_body
    The complete or essentially complete figure is visible.
mostly_full_body
    Most of the figure is visible, with minor cropping or occlusion.
upper_body
    The upper portion of the person is emphasized while much of the
    lower body is excluded.
torso_only
    The composition concentrates primarily on the torso or occupational
    body region rather than the complete person.
limb_only
    Only a diagnostic limb or partial-body interaction is required.
mixed
    Multiple people use meaningfully different levels of body
    visibility.
custom
    Use when another visibility structure better fits the presentation.

Examples:
- Shopping demonstrates full-body action staging.
- The central Basketball player is mostly full-body.
- Doctor demonstrates torso-only staging.
- Vote demonstrates limb-only staging.
- Basketball as a whole demonstrates mixed body visibility.

human_staging.orientation_and_pose
----------------------------------
Describe the figure orientation, pose, gesture, and action-relevant
body configuration.
When multiple people are present, describe the distinctions that
matter for the scene.
Pose should serve recognition and composition rather than merely make
the figures appear active.

human_staging.role_in_composition
---------------------------------
Explain how the person or people function visually within the image.
Possible roles include, but are not limited to:
- dominant recognition anchor,
- primary action carrier,
- supporting action cue,
- occupational carrier,
- framing element,
- distributed group,
- scale reference,
- or environmental participant.
Use free description rather than selecting mechanically from this list.

--------------------------------------------------
5. REALIZE THE DESIGN IN THE STYLE
--------------------------------------------------
Once the presentation and structured visual design are resolved,
translate that design through the supplied StyleProfile.
The StyleProfile remains the authority for stable visual grammar.
Do not reinvent a second style grammar inside the FinalScenePlan.
The supplied visual references may demonstrate how related
illustrations realize style principles, but do not copy their exact
palette, shapes, figures, or composition.

color_direction
===============
Describe the functional use of color in this particular scene.
Explain how color should support:
- hierarchy,
- separation,
- grouping,
- recognition,
- atmosphere,
- or compositional coherence.
Do not simply restate generic StyleProfile rules.
Do not copy a reference palette.

shape_direction
===============
Describe how important subjects and objects should be simplified,
constructed, or differentiated through shape while retaining the
diagnostic structure required for recognition.
Different semantic elements may use different degrees or kinds of
simplification when useful.

detail_direction
================
Describe where visual specificity should be concentrated and where
forms should remain quieter or simpler.
Allocate detail according to semantic importance.
Recognition-critical structures may receive more specificity than
tertiary context.

human_rendering_direction
=========================
If people are present, describe how they should be visually simplified
and rendered within the StyleProfile.
This concerns rendering rather than staging.

It may address:
- anatomical versus geometric simplification,
- facial detail,
- silhouette treatment,
- clothing construction,
- hand detail,
- or other stylistic properties when relevant.

Do not infer unsupported identity-specific characteristics.
Anonymous figures may still appear visually concrete and naturally
varied.
If no people are present, use null.

decorative_direction
====================
Describe whether decorative, symbolic, or nonliteral visual elements
should appear and what purpose they serve.
They may support:
- rhythm,
- balance,
- atmosphere,
- semantic association,
- motion,
- or empty-space activation.

Do not add decoration merely to fill space.
Do not allow decorative elements to compete with the recognition_plan.
If none are useful, say that no additional decorative treatment is
needed.

Important: Rendering treatment that is already stable across the StyleProfile
should follow that profile rather than being reinvented here.

--------------------------------------------------
6. REFINE AND VALIDATE
--------------------------------------------------
Review the complete design as one image.
Simplify only after the presentation concept and structured design have
been resolved.

Remove or quiet elements that:
- do not contribute to recognition,
- compete unnecessarily with the primary visual logic,
- create clutter,
- make the scene more literal than necessary,
- or weaken the chosen presentation concept.

Then verify all of the following:

- The final image still communicates the candidate's intended concept.
- recognition_plan clearly explains why the scene is recognizable.
- presentation_concept is a coherent integrated visual idea.
- visible_elements are sufficient for recognition.
- intentional_omissions do not remove required semantic information.
- composition, viewpoint, cropping, depth, scale, environment, and
  human staging all support the same presentation concept.
- key relationships remain visually clear.
- motion is communicated only when relevant.
- no unsupported semantically important person, relationship, object,
  setting, occasion, profession, or storyline has been introduced.
- the candidate's human presence and semantic identity are respected.
- the StyleProfile governs the final visual grammar.
- supplied references have been used as precedent rather than copied.

The final plan should be visually specific and internally coherent.
Return only the selected FinalScenePlan.
Do not return discarded presentation concepts or analysis.

==================================================
REFERENCE USE
==================================================

Two kinds of visual references may appear in this prompt:

1. TEACHING EXAMPLES
   Teaching examples appear inside the Art-Direction Procedure.
   Their purpose is to demonstrate transferable visual reasoning, such
   as:
   - concentrated versus distributed recognition,
   - diagnostic cropping,
   - perspective-driven presentation,
   - semantic scale,
   - selective omission,
   - or nonliteral visual organization.
   Learn the design principle demonstrated by the example.
   Do not treat its subject, composition, crop boundary, viewpoint,
   object arrangement, palette, pose, or scale relationship as a
   template for the current candidate.

2. SUPPLIED CANDIDATE REFERENCES
   The supplied references are precedents selected because they are
   structurally relevant to the current candidate.
   Study them for useful evidence about how related illustrations solve
   visual problems such as:
   - composition and hierarchy,
   - spatial organization,
   - depth and perspective,
   - framing and cropping,
   - scale relationships,
   - environment treatment,
   - human staging,
   - object and human relationships,
   - simplification,
   - distribution of detail,
   - color behavior,
   - shape language,
   - decorative treatment,
   - and rendering treatment.
   Use them to inform judgment, not to determine the scene.
   A reference may provide a useful lesson even when only one part of
   its solution is relevant.

For all references:
- The candidate remains the authority for what the new scene means and
  depicts.
- The StyleProfile remains the authority for stable visual grammar.
- References may support or clarify art-direction decisions, but they
  must not override either one.
- Do not force the current candidate to resemble a reference merely
  because that reference was supplied.

Do not copy:
- the exact scene,
- object set,
- pose,
- composition,
- crop boundary,
- viewpoint,
- spatial arrangement,
- palette,
- character appearance,
- or narrative.

Transfer the underlying visual lesson rather than the specific design.
""".strip()

def _image_to_data_url(path: Path) -> str:
    """Convert a local PNG image into a base64 data URL for the API."""
    image_bytes = path.read_bytes()
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/png;base64,{encoded}"

def _build_art_director_instruction_content(
    prompt: str,
) -> list[dict[str, str]]:
    """
    Replace teaching-image placeholders with input_image blocks while
    preserving their exact positions among the surrounding text blocks.
    """
    content: list[dict[str, str]] = []
    cursor = 0
    for match in TEACHING_IMAGE_PATTERN.finditer(prompt):
        text_before = prompt[cursor:match.start()]
        if text_before.strip():
            content.append({
                "type": "input_text",
                "text": text_before,
            })
        reference_id = match.group(1)
        try:
            image_path = TEACHING_IMAGES[reference_id]
        except KeyError as exc:
            raise ValueError(
                f"Unknown teaching image: {reference_id}"
            ) from exc
        if not image_path.exists():
            raise FileNotFoundError(
                f"Teaching image not found: {image_path}"
            )
        content.append({
            "type": "input_image",
            "image_url": _image_to_data_url(image_path),
        })
        cursor = match.end()
    remaining_text = prompt[cursor:]
    if remaining_text.strip():
        content.append({
            "type": "input_text",
            "text": remaining_text,
        })
    return content

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
) -> FinalScenePlan:
    """
    Convert one already-viable CandidateScene into a complete
    style-specific FinalScenePlan.

    The candidate supplies the scene identity.
    The StyleProfile supplies stable style grammar.
    References supply optional precedent.

    The Art Director resolves the scene's presentation and
    renderable art direction without turning it into a different idea.
    """
    client = get_openai_client()
    candidate_json = json.dumps(
        candidate.model_dump(mode="json"),
        indent=2,
        ensure_ascii=False,
    )
    
    reference_content = build_reference_content(
        reference_packet
    )

    instruction_content = _build_art_director_instruction_content(
        ART_DIRECTOR_PROMPT
    )
    response = client.responses.parse(
        model=TEXT_MODEL,
        input=[
            {
                "role": "system",
                "content": ART_DIRECTOR_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": [
                    *instruction_content,
                    {
                        "type": "input_text",
                        "text": f"""ART-DIRECT THIS EXISTING CANDIDATE.
CANDIDATE
=========
{candidate_json}

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

Spatial principles:
{_format_principles(style_profile.spatial_principles)}

Perspective principles:
{_format_principles(style_profile.perspective_principles)}

Environment principles:
{_format_principles(style_profile.environment_principles)}

Human principles:
{_format_principles(style_profile.human_principles)}

Motion principles:
{_format_principles(style_profile.motion_principles)}

Scene-density principles:
{_format_principles(style_profile.scene_density_principles)}

Color principles:
{_format_principles(style_profile.color_principles)}

Shape principles:
{_format_principles(style_profile.shape_principles)}

Decorative principles:
{_format_principles(style_profile.decorative_principles)}

Rendering principles:
{_format_principles(style_profile.rendering_principles)}

TASK
====
Resolve this candidate into one complete FinalScenePlan using the
candidate, StyleProfile, and any supplied visual precedents according
to the roles defined above.

SUPPLIED CANDIDATE REFERENCES
=============================
The following references are the Stage-B precedents selected for this
candidate. Treat them according to the SUPPLIED CANDIDATE REFERENCES
rules above.

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
        }
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
