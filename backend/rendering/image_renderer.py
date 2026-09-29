from __future__ import annotations

import base64
from contextlib import ExitStack
from datetime import datetime
from pathlib import Path

from config import (
    GENERATED_DIR,
    IMAGE_MODEL,
    IMAGE_QUALITY,
    IMAGE_SIZE,
)
from openai_client import get_openai_client
from planning.schemas import RenderPrompt


def _validate_reference_paths(
    reference_image_paths: list[str],
) -> list[Path]:
    """
    Validate renderer-stage reference images before making an API call.
    """

    paths: list[Path] = []

    for raw_path in reference_image_paths:
        path = Path(raw_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Renderer reference image not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Renderer reference path is not a file: {path}"
            )

        paths.append(path)

    return paths


def render_image(
    render_prompt: RenderPrompt,
    filename_prefix: str = "concept",
) -> Path:
    """
    Render one image from a completed RenderPrompt and save it locally.

    This stage performs no creative planning.

    When Stage-C reference images are supplied, they are passed to the
    image model as visual references. Their intended use is already
    described explicitly in the compiled prompt.

    When no references are supplied, ordinary text-to-image generation
    is used.
    """

    if not render_prompt.prompt.strip():
        raise ValueError(
            "Render prompt cannot be empty."
        )

    reference_paths = _validate_reference_paths(
        render_prompt.reference_image_paths
    )

    GENERATED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    client = get_openai_client()

    # -----------------------------------------------------
    # Render with or without Stage-C visual references.
    # -----------------------------------------------------

    if reference_paths:
        with ExitStack() as stack:
            reference_files = [
                stack.enter_context(
                    path.open("rb")
                )
                for path in reference_paths
            ]

            result = client.images.edit(
                model=IMAGE_MODEL,
                image=reference_files,
                prompt=render_prompt.prompt,
                size=IMAGE_SIZE,
                quality=IMAGE_QUALITY,
            )

    else:
        result = client.images.generate(
            model=IMAGE_MODEL,
            prompt=render_prompt.prompt,
            size=IMAGE_SIZE,
            quality=IMAGE_QUALITY,
        )

    # -----------------------------------------------------
    # Validate and save result.
    # -----------------------------------------------------

    if not result.data:
        raise ValueError(
            "Image generation returned no image data."
        )

    image_base64 = result.data[0].b64_json

    if not image_base64:
        raise ValueError(
            "Image generation returned no base64 image."
        )

    image_bytes = base64.b64decode(
        image_base64
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    filename = (
        f"{filename_prefix}_{timestamp}.png"
    )

    output_path = (
        GENERATED_DIR
        / filename
    )

    output_path.write_bytes(
        image_bytes
    )

    return output_path
