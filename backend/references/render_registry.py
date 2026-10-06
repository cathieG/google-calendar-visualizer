from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from config import (
    REFERENCE_RENDERED_DIR,
    RENDER_REFERENCE_ANNOTATIONS_PATH,
)


@dataclass(frozen=True)
class RenderReferenceRecord:
    """
    One deeply annotated reference available to Stage C.

    The registry is intentionally simple:
    - reference_id identifies the reference,
    - concept provides a human-readable label,
    - image_path points to the actual rendered reference image,
    - annotation contains the verified visual observations.

    Stage-C selection logic belongs in render_selector.py.
    """

    reference_id: str
    concept: str
    image_path: Path
    annotation: dict[str, Any]


def load_render_reference_registry(
) -> list[RenderReferenceRecord]:
    """
    Load and validate the deeply annotated Stage-C reference bank.

    This function does not rank, filter, normalize, or semantically
    interpret references. It only:

    1. reads the renderer-reference annotations;
    2. verifies that reference IDs are unique;
    3. resolves each annotation to its rendered image;
    4. verifies that the image exists;
    5. returns structured RenderReferenceRecord objects.

    Stage-C reasoning about which references are useful happens later in
    render_selector.py.
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
            line = line.strip()

            if not line:
                continue

            annotation = json.loads(line)

            reference_id = annotation.get("reference_id")
            concept = annotation.get("concept")
            image_source = annotation.get("image_source")

            if not reference_id:
                raise ValueError(
                    "Renderer reference annotation is missing "
                    f"'reference_id' on line {line_number}."
                )

            if not concept:
                raise ValueError(
                    f"Renderer reference '{reference_id}' is missing "
                    f"'concept' on line {line_number}."
                )

            if not image_source:
                raise ValueError(
                    f"Renderer reference '{reference_id}' is missing "
                    f"'image_source' on line {line_number}."
                )

            if reference_id in seen_ids:
                raise ValueError(
                    "Duplicate renderer reference ID "
                    f"'{reference_id}' on line {line_number}."
                )

            seen_ids.add(reference_id)

            image_path = (
                REFERENCE_RENDERED_DIR
                / image_source
            )

            if not image_path.exists():
                raise FileNotFoundError(
                    f"Renderer reference '{reference_id}' "
                    f"points to missing image: {image_path}"
                )

            records.append(
                RenderReferenceRecord(
                    reference_id=reference_id,
                    concept=concept,
                    image_path=image_path,
                    annotation=annotation,
                )
            )

    return records