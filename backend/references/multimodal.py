from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

from planning.schemas import ReferencePacket


MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


def image_path_to_data_url(image_path: str) -> str:
    """
    Convert a local reference image into a base64 data URL suitable
    for an OpenAI Responses API image input.
    """

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Reference image not found: {path}"
        )

    suffix = path.suffix.lower()

    if suffix not in MIME_TYPES:
        raise ValueError(
            f"Unsupported reference image type: {suffix}"
        )

    encoded = base64.b64encode(
        path.read_bytes()
    ).decode("utf-8")

    return (
        f"data:{MIME_TYPES[suffix]};"
        f"base64,{encoded}"
    )


def build_reference_content(
    packet: ReferencePacket | None,
) -> list[dict[str, Any]]:
    """
    Convert a curated ReferencePacket into multimodal message content.

    Each image is paired with:
    - its concept,
    - the annotation evidence that caused it to be selected,
    - the design question it is meant to illuminate.

    References are presented as precedents, never as templates to copy.
    """

    if packet is None:
        return []

    content: list[dict[str, Any]] = []

    for index, reference in enumerate(
        packet.references,
        start=1,
    ):
        evidence = json.dumps(
            reference.matched_fields,
            indent=2,
            ensure_ascii=False,
        )

        content.append(
            {
                "type": "input_text",
                "text": (
                    f"REFERENCE {index}: {reference.concept}\n\n"
                    f"Why this reference was selected:\n"
                    f"{reference.teaching_focus}\n\n"
                    f"Relevant annotation evidence:\n"
                    f"{evidence}\n\n"
                    "Study this image as visual precedent. "
                    "Extract abstract design knowledge from the "
                    "requested dimensions. Do not copy its exact "
                    "scene, object combination, pose, layout, "
                    "palette, or composition."
                ),
            }
        )

        content.append(
            {
                "type": "input_image",
                "image_url": image_path_to_data_url(
                    reference.image_path
                ),
                "detail": "auto",
            }
        )

    return content
