from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from config import (
    REFERENCE_RENDERED_DIR,
    RENDER_REFERENCE_ANNOTATIONS_PATH,
)


INDEX_SECTIONS = (
    "scene_features",
    "rendering_features",
    "human_features",
    "object_features",
    "relationship_features",
)


DEPTH_FAMILY = {
    "shallow_layered": "shallow",
    "very_shallow_layered": "very_shallow",
    "near_flat_diagrammatic": "near_flat",
    "moderate_layered": "moderate",
    "perspective_driven_deep": "deep",
    "near_flat": "near_flat",
    "shallow_collage": "shallow",
    "shallow_faceted": "shallow",
    "shallow_stage_layered": "shallow",
    "layered_scale_based": "moderate",
    "extremely_shallow": "very_shallow",
    "shallow_side_view": "shallow",
    "extremely_shallow_overlap": "very_shallow",
}


VIEW_HORIZONTAL_FAMILY = {
    "frontal_orthographic_scene": "frontal",
    "frontal_close_crop": "frontal",
    "frontal_collage_still_life": "frontal",
    "frontal_down_lane_from_pin_end": "frontal",
    "frontal_flat_display": "frontal",
    "frontal_stage_view": "frontal",
    "frontal_wall_view": "frontal",
    "frontal_or_slight_oblique_court_view": "frontal_or_oblique",

    "side_on_environmental_view": "side",
    "side_on_narrative_view": "side",
    "side_profile_action_view": "side",
    "side_profile_orthographic_scene": "side",

    "close_up_oblique": "oblique",

    "not_applicable_flat_collage": "not_applicable",
}


BACKGROUND_FAMILY = {
    "flat_field_with_sparse_abstract_support": "flat_field",
    "abstract_banded_field": "abstract_layered_field",
    "minimal_symbolic_baseline_field": "flat_field",

    "simplified_literal_sports_environment": "simplified_environment",
    "simplified_literal_outdoor_environment": "simplified_environment",
    "simplified_narrative_environment": "simplified_environment",

    "minimal_directional_lane_environment": "partial_environment",
    "simplified_stage_backdrop": "partial_environment",
    "flat_field_with_partial_retail_context": "partial_environment",

    "decorative_flat_field": "flat_field",
    "nonliteral_flat_collage_field": "flat_field",
    "flat_field_with_abstract_support_panels": "flat_field",
    "flat_graphic_field_with_sparse_geometric_support": "flat_field",

    "environment_as_full_frame_faceted_field": "semantic_environment",
}


@dataclass(frozen=True)
class RenderReferenceRecord:
    reference_id: str
    concept: str

    image_path: Path

    annotation: dict[str, Any]

    features: dict[str, frozenset[str]]


def _derive_scene_features(
    annotation: dict[str, Any],
) -> set[str]:
    """
    Derive broad reusable capabilities from the detailed observations.

    These are deterministic mappings, not keyword search.
    """

    whole_scene = annotation["whole_scene"]

    derived: set[str] = set()

    environment = (
        whole_scene
        .get("environment", {})
        .get("normalized_treatment")
    )

    if environment:
        derived.add(
            f"environment:{environment}"
        )

    background = (
        whole_scene
        .get("background", {})
        .get("normalized_treatment")
    )

    if background in BACKGROUND_FAMILY:
        derived.add(
            "background_family:"
            + BACKGROUND_FAMILY[background]
        )

    depth = (
        whole_scene
        .get("depth", {})
        .get("category")
    )

    if depth in DEPTH_FAMILY:
        derived.add(
            "depth_family:"
            + DEPTH_FAMILY[depth]
        )

    horizontal = (
        whole_scene
        .get("viewpoint", {})
        .get("horizontal")
    )

    if horizontal in VIEW_HORIZONTAL_FAMILY:
        derived.add(
            "view_horizontal_family:"
            + VIEW_HORIZONTAL_FAMILY[horizontal]
        )

    vertical = (
        whole_scene
        .get("viewpoint", {})
        .get("vertical")
    )

    if vertical:
        derived.add(
            f"view_vertical_family:{vertical}"
        )

    human_presence = (
        annotation
        .get("humans", {})
        .get("presence")
    )

    if human_presence:
        derived.add(
            f"human_presence:{human_presence}"
        )

    return derived


def load_render_reference_registry(
) -> list[RenderReferenceRecord]:
    """
    Load the deeply annotated Stage-C renderer-reference bank.

    The source JSONL contains detailed observations for a deliberately
    small subset of Google Calendar references.

    No fuzzy matching or semantic inference happens here.
    """

    if not RENDER_REFERENCE_ANNOTATIONS_PATH.exists():
        raise FileNotFoundError(
            "Renderer reference annotations not found: "
            f"{RENDER_REFERENCE_ANNOTATIONS_PATH}"
        )

    records: list[RenderReferenceRecord] = []
    seen_ids: set[str] = set()

    with RENDER_REFERENCE_ANNOTATIONS_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line_number, line in enumerate(
            file,
            start=1,
        ):
            if not line.strip():
                continue

            annotation = json.loads(line)

            reference_id = annotation["reference_id"]
            concept = annotation["concept"]

            if reference_id in seen_ids:
                raise ValueError(
                    "Duplicate renderer reference ID "
                    f"'{reference_id}' on line {line_number}."
                )

            seen_ids.add(reference_id)

            image_source = annotation["image_source"]

            image_path = (
                REFERENCE_RENDERED_DIR
                / image_source
            )

            if not image_path.exists():
                raise FileNotFoundError(
                    f"Renderer reference '{reference_id}' "
                    f"points to missing image: {image_path}"
                )

            raw_index = annotation.get(
                "retrieval_index",
                {},
            )

            features: dict[str, set[str]] = {
                section: set(
                    raw_index.get(section, [])
                )
                for section in INDEX_SECTIONS
            }

            # Add broad reusable scene capabilities alongside the
            # detailed observed features.
            features["scene_features"].update(
                _derive_scene_features(
                    annotation
                )
            )

            records.append(
                RenderReferenceRecord(
                    reference_id=reference_id,
                    concept=concept,
                    image_path=image_path,
                    annotation=annotation,
                    features={
                        section: frozenset(values)
                        for section, values
                        in features.items()
                    },
                )
            )

    return records
