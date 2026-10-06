from __future__ import annotations

from planning.schemas import (
    FinalScenePlan,
    RenderPrompt,
)
from references.render_selector import (
    RendererReferencePacket,
)
from styles import StyleProfile


def _bullets(items: list[str]) -> str:
    return "\n".join(
        f"- {item}"
        for item in items
    )


def _optional_text(
    value: str | None,
    fallback: str = "Not applicable.",
) -> str:
    if value is None:
        return fallback

    value = value.strip()

    return value if value else fallback


def _compile_style_contract(
    plan: FinalScenePlan,
    style_profile: StyleProfile,
) -> str:
    """
    Compile stable visual-language rules that the renderer should obey.

    Scene-specific composition, framing, depth, scale, environment,
    motion, and other art-direction decisions have already been made in
    FinalScenePlan and must not be reopened here.

    Only style principles that directly constrain realization are
    included.
    """

    sections: list[str] = []

    def add_section(
        title: str,
        principles: list[str],
    ) -> None:
        if not principles:
            return

        sections.append(
            f"""
{title}

{_bullets(principles)}
""".strip()
        )

    add_section(
        "Rendering",
        style_profile.rendering_principles,
    )

    add_section(
        "Color",
        style_profile.color_principles,
    )

    add_section(
        "Shape",
        style_profile.shape_principles,
    )

    add_section(
        "Scene density",
        style_profile.scene_density_principles,
    )

    if plan.human_staging is not None:
        add_section(
            "Human depiction",
            style_profile.human_principles,
        )

    if plan.relationships_and_motion.motion_plan is not None:
        add_section(
            "Motion language",
            style_profile.motion_principles,
        )

    add_section(
        "Decorative and nonliteral treatment",
        style_profile.decorative_principles,
    )

    return "\n\n".join(sections)


def _compile_reference_guidance(
    packet: RendererReferencePacket | None,
) -> str:
    """
    Translate Stage-C selections into renderer-facing instructions.

    Stage C has already decided which references are useful and exactly
    what each reference demonstrates.

    This function does not reinterpret or rank them.
    """

    if (
        packet is None
        or not packet.references
    ):
        return ""

    sections: list[str] = []

    for index, reference in enumerate(
        packet.references,
        start=1,
    ):
        evidence = _bullets(
            [
                item.demonstrates
                for item in reference.evidence
            ]
        )

        sections.append(
            f"""
REFERENCE {index}: {reference.concept}

Study this image for:
{evidence}

Transfer the visual lesson, not the reference's specific design.
""".strip()
        )

    reference_sections = "\n\n".join(
        sections
    )

    return f"""
VISUAL REFERENCE GUIDANCE
=========================

The supplied images are execution precedents for specific decisions
that already exist in the FinalScenePlan.

Use each reference for the properties listed below.

Do not use a reference to redesign the scene.

Do not copy its components precisely such as:
- subject matter,
- object set,
- exact pose,
- exact composition,
- exact crop boundary,
- exact viewpoint,
- exact spatial arrangement,
- palette,
- character appearance,
- or narrative.

{reference_sections}
""".strip()


def _compile_human_staging(
    plan: FinalScenePlan,
) -> str:
    if plan.human_staging is None:
        return "No people are present in the planned scene."

    return f"""
Body visibility:
{plan.human_staging.body_visibility.value}

Orientation and pose:
{_optional_text(
    plan.human_staging.orientation_and_pose
)}

Role in composition:
{_optional_text(
    plan.human_staging.role_in_composition
)}
""".strip()


def compile_render_prompt(
    plan: FinalScenePlan,
    style_profile: StyleProfile,
    reference_packet: RendererReferencePacket | None = None,
) -> RenderPrompt:
    """
    Deterministically translate a completed FinalScenePlan, StyleProfile,
    and optional Stage-C renderer references into a renderer-ready prompt.

    This function makes no new creative decisions.

    FinalScenePlan defines the finished scene and its art direction.

    StyleProfile supplies stable visual-language constraints.

    Stage-C references provide execution precedents for decisions
    already present in the plan, and they are also visual examples of the
    style profile.
    """

    visible_elements = (
        _bullets(
            plan.content_selection.visible_elements
        )
        if plan.content_selection.visible_elements
        else "- No additional visible elements specified."
    )

    intentional_omissions = (
        _bullets(
            plan.content_selection.intentional_omissions
        )
        if plan.content_selection.intentional_omissions
        else "- No additional intentional omissions."
    )

    key_relationships = (
        _bullets(
            plan.relationships_and_motion.key_relationships
        )
        if plan.relationships_and_motion.key_relationships
        else "- No additional key relationships specified."
    )

    style_contract = _compile_style_contract(
        plan=plan,
        style_profile=style_profile,
    )

    human_staging = _compile_human_staging(
        plan
    )

    reference_guidance = (
        _compile_reference_guidance(
            reference_packet
        )
    )

    reference_section = (
        f"\n\n{reference_guidance}"
        if reference_guidance
        else ""
    )

    prompt = f"""
RENDERING LANGUAGE
==================

Render the entire illustration according to this stable visual language.

{style_contract}

These principles govern HOW the completed design is rendered.

They do not override or reopen any scene-specific decision below.

If you are provided with reference images, the reference images are a subset of
the sources from which style contract is derived. Therefore, your rendering
should be in a style where people can effectively recognize them to be in
the same general style.


CORE VISUAL IDEA
================

Recognition plan:
{plan.recognition_plan}

Presentation concept:
{plan.presentation_concept}

Representation strategy:
{plan.representation_strategy.value}

Recognition structure:
{plan.recognition_structure.value}


CONTENT
=======

Visible elements:
{visible_elements}

Intentionally omitted:
{intentional_omissions}

Render the listed visible elements as required by the completed plan.

Do not reintroduce intentionally omitted content merely because it would
normally appear in a literal real-world version of the scene.


COMPOSITION
===========

Structure:
{plan.composition.structure}

Hierarchy and balance:
{plan.composition.hierarchy_and_balance}

Negative space:
{plan.composition.negative_space}

Directional flow:
{plan.composition.directional_flow}


FRAMING AND VIEW
================

Viewpoint:
{plan.framing_and_view.viewpoint}

Framing:
{plan.framing_and_view.framing}

Cropping strength:
{plan.framing_and_view.cropping_strength.value}

Edge continuation:
{plan.framing_and_view.edge_continuation}


SPATIAL PLAN
============

Depth strategy:
{plan.spatial_plan.depth_strategy.value}

Perspective strategy:
{plan.spatial_plan.perspective_strategy.value}

Spatial relationships:
{plan.spatial_plan.spatial_relationships}


SCALE
=====

Scale strategy:
{plan.scale_plan.strategy.value}

Scale realization:
{plan.scale_plan.description}


ENVIRONMENT
===========

{plan.environment_plan}


RELATIONSHIPS AND MOTION
========================

Key relationships:
{key_relationships}

Motion:
{_optional_text(
    plan.relationships_and_motion.motion_plan,
    fallback="The scene is static; do not add artificial motion cues.",
)}


HUMAN STAGING
=============

{human_staging}


SCENE-SPECIFIC STYLE REALIZATION
================================

Color:
{plan.color_direction}

Shape:
{plan.shape_direction}

Detail:
{plan.detail_direction}

Human rendering:
{_optional_text(
    plan.human_rendering_direction
)}

Decorative / nonliteral treatment:
{plan.decorative_direction}
{reference_section}


EXECUTION RULES
===============

Render this completed visual plan directly.

Do not redesign the scene.

Do not:
- change the presentation concept,
- choose a different composition,
- change the viewpoint,
- change the framing or crop,
- change the depth or perspective strategy,
- change the scale logic,
- introduce a different environment treatment,
- add semantically important people or objects,
- remove recognition-critical content,
- invent a new relationship or storyline,
- or replace the scene-specific art direction with a reference image's
  solution.

Preserve the recognition_plan and presentation_concept as the organizing
logic of the image.

Preserve the specified relationships among important people, objects,
and environmental elements.

The goal is faithful execution of the completed FinalScenePlan, not a
new interpretation of it, and such execution's visual realization belongs
convincingly to thesame illustration family as the references.
""".strip()

    reference_image_paths = (
        [
            reference.image_path
            for reference
            in reference_packet.references
        ]
        if reference_packet is not None
        else []
    )

    return RenderPrompt(
        prompt=prompt,
        reference_image_paths=reference_image_paths,
    )