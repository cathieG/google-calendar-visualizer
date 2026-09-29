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


def _compile_style_contract(
    style_profile: StyleProfile,
) -> str:
    """
    Compile only the stable rendering-language invariants that the
    image model must obey directly.

    Composition, scale, cropping, perspective, people, and scene
    density have already been resolved into the FinalScenePlan and
    are therefore not reopened here.
    """

    principles = (
        style_profile.rendering_principles
        + style_profile.color_principles
        + style_profile.shape_principles
    )

    return _bullets(principles)


def _compile_layers(
    plan: FinalScenePlan,
) -> str:
    treatments = {
        treatment.layer_index: treatment
        for treatment in plan.layer_treatments
    }

    sections: list[str] = []

    for layer in plan.scene_structure.layers:
        treatment = treatments[layer.index]

        contents = (
            _bullets(layer.contents)
            if layer.contents
            else "- No additional contents specified."
        )

        sections.append(
            f"""
LAYER {layer.index}: {layer.role}

Contents:
{contents}

Semantic priority:
{layer.semantic_priority}

Detail priority:
{treatment.detail_priority}

Contrast priority:
{treatment.contrast_priority}

Color role:
{treatment.color_role}

Shape specificity:
{treatment.shape_specificity}

Layer guidance:
{layer.notes or "No additional layer guidance."}

Treatment guidance:
{treatment.notes or "No additional treatment guidance."}
""".strip()
        )

    return "\n\n".join(sections)


def _compile_reference_guidance(
    packet: RendererReferencePacket | None,
) -> str:
    """
    Translate Stage-C selections into renderer-facing instructions.

    The selector has already decided which references are useful.
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

Study this reference only for:
{evidence}

Do not copy unrelated properties of this reference.
""".strip()
        )

    reference_sections = "\n\n".join(
        sections
    )

    return f"""
VISUAL REFERENCE GUIDANCE
=========================

The supplied reference images are evidence for specific visual
properties of the completed scene plan.

Use each reference only for the explicitly listed properties.

Do not inherit unrelated properties from a reference.

In particular, do not copy a reference's:
- subject matter,
- object set,
- narrative,
- exact pose,
- exact composition,
- exact spatial layout,
- palette,
- or other visual properties not explicitly identified below.

{reference_sections}
""".strip()


def compile_render_prompt(
    plan: FinalScenePlan,
    style_profile: StyleProfile,
    reference_packet: RendererReferencePacket | None = None,
) -> RenderPrompt:
    """
    Deterministically translate a FinalScenePlan, stable style
    invariants, and optional Stage-C renderer references into a
    renderer-ready prompt.

    This function makes no new creative decisions.

    The FinalScenePlan defines what this particular illustration
    depicts and how it is composed.

    The StyleProfile contributes only stable rendering-language
    constraints that should remain true across illustrations in the
    same visual system.

    Stage-C references provide visual evidence only for specific
    already-decided properties.
    """

    selected_objects = (
        _bullets(plan.selected_objects)
        if plan.selected_objects
        else "- No additional objects beyond the described scene."
    )

    must_preserve = (
        _bullets(plan.must_preserve)
        if plan.must_preserve
        else "- Preserve the scene and recognition logic described above."
    )

    constraints = (
        _bullets(plan.content_constraints)
        if plan.content_constraints
        else "- No additional content constraints."
    )

    accent = (
        plan.accent_detail
        if plan.accent_detail is not None
        else "None."
    )

    style_contract = _compile_style_contract(
        style_profile
    )

    layers = _compile_layers(
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
RENDERING LANGUAGE — NON-NEGOTIABLE
===================================

Render the illustration in the following visual language throughout
the entire image.

{style_contract}

These are global rendering constraints, not optional local suggestions.
They apply to every visible form in the image.


SCENE
=====

Visual thesis:
{plan.visual_thesis}

Subject:
{plan.subject}

Setting:
{plan.setting}

Action:
{plan.action}

Visible objects:
{selected_objects}

Accent detail:
{accent}


VIEW AND COMPOSITION
====================

View angle:
{plan.view_angle}

Framing:
{plan.framing_scale}

Composition:
{plan.composition_structure}

Visual weight:
{plan.visual_weight_distribution}

Salience:
{plan.salience_structure}

Negative space:
{plan.negative_space_strategy}

Directional flow:
{plan.directional_flow}


SCALE AND FRAME
===============

Scale logic:
{plan.scale_source}

Cropping:
{plan.cropping_strength}

Edge continuation:
{plan.edge_continuation}


SPATIAL STRUCTURE
=================

Depth strategy:
{plan.scene_structure.depth_strategy}

Depth span:
{plan.scene_structure.depth_span}

Perspective:
{plan.scene_structure.perspective_strategy}

Spatial coherence:
{plan.scene_structure.spatial_coherence}

{layers}


SCENE-SPECIFIC STYLE TREATMENT
==============================

People:
{plan.human_direction}

Color:
{plan.color_direction}

Shape:
{plan.shape_direction}

Detail:
{plan.detail_direction}

Nonliteral treatment:
{plan.nonliteral_direction}
{reference_section}


MUST PRESERVE
=============

{must_preserve}


CONTENT CONSTRAINTS
===================

{constraints}


EXECUTION
=========

Render this completed plan directly.

Do not redesign the scene, introduce a new storyline, add semantically
important content, or reinterpret the visual concept.

Preserve the specified composition, recognition cues, spatial
relationships, and scene-specific treatment while obeying the global
rendering language above.

When reference images are supplied, use them only for the specific
properties identified in VISUAL REFERENCE GUIDANCE.
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
