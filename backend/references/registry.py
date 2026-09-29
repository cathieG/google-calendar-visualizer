import json
from pathlib import Path

from config import (
    REFERENCE_ANNOTATIONS_PATH,
    REFERENCE_CATALOG_PATH,
    REFERENCE_RAW_DIR,
    REFERENCE_RENDERED_DIR,
    REFERENCE_STUDY_DIR,
)
from planning.schemas import ReferenceRecord


def _reference_id_from_filename(filename: str) -> str:
    """
    Convert:
        img_delivery.png
    into:
        delivery
    """

    stem = Path(filename).stem

    if stem.startswith("img_"):
        stem = stem[4:]

    return stem.lower()


def _load_study_annotations() -> dict[str, tuple[Path, dict]]:
    """
    Load all detailed study JSON files currently available.

    The study corpus is intentionally allowed to be incomplete:
    an image can still be used as a reference even when it has not
    yet received a detailed annotation.
    """

    annotations: dict[str, tuple[Path, dict]] = {}

    if not REFERENCE_STUDY_DIR.exists():
        return annotations

    for path in REFERENCE_STUDY_DIR.glob("*.json"):
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        reference_id = data.get("reference_id")

        if not reference_id:
            raise ValueError(
                f"Study annotation has no reference_id: {path}"
            )

        if reference_id in annotations:
            raise ValueError(
                f"Duplicate study annotation for reference_id "
                f"{reference_id!r}"
            )

        annotations[reference_id] = (path, data)

    return annotations


def _load_runtime_annotations() -> dict[str, dict]:
    """
    Load compact canonical annotations used by runtime retrieval.

    The file is intentionally allowed to be incomplete while the
    reference library is being normalized incrementally.
    """

    annotations: dict[str, dict] = {}

    if not REFERENCE_ANNOTATIONS_PATH.exists():
        return annotations

    with REFERENCE_ANNOTATIONS_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            data = json.loads(line)

            reference_id = data.get("reference_id")

            if not reference_id:
                raise ValueError(
                    "Runtime annotation is missing reference_id "
                    f"on line {line_number}."
                )

            if reference_id in annotations:
                raise ValueError(
                    "Duplicate runtime annotation for "
                    f"reference_id {reference_id!r}."
                )

            annotations[reference_id] = data

    return annotations


def load_reference_registry() -> list[ReferenceRecord]:
    """
    Load the Google Calendar reference library.

    references.json is the authoritative list of available images.

    Detailed study annotations are attached when they exist, but they
    are not required. This allows the full 51-image corpus to remain
    usable while annotation work continues incrementally.
    """

    with REFERENCE_CATALOG_PATH.open("r", encoding="utf-8") as file:
        catalog = json.load(file)

    if not isinstance(catalog, list):
        raise ValueError(
            "references.json must contain a JSON list."
        )

    study_annotations = _load_study_annotations()
    runtime_annotations = _load_runtime_annotations()

    records: list[ReferenceRecord] = []
    seen_ids: set[str] = set()

    for entry in catalog:
        concept = entry.get("concept")
        filename = entry.get("file")

        if not concept or not filename:
            raise ValueError(
                "Each references.json entry must contain "
                "'concept' and 'file'."
            )

        reference_id = _reference_id_from_filename(filename)

        if reference_id in seen_ids:
            raise ValueError(
                f"Duplicate reference_id in catalog: {reference_id!r}"
            )

        seen_ids.add(reference_id)

        rendered_path = REFERENCE_RENDERED_DIR / filename

        if not rendered_path.exists():
            raise FileNotFoundError(
                f"Rendered reference not found: {rendered_path}"
            )

        raw_candidate = (
            REFERENCE_RAW_DIR
            / f"{Path(filename).stem}.svg"
        )

        raw_path = (
            str(raw_candidate)
            if raw_candidate.exists()
            else None
        )

        annotation_path = None
        annotation = None

        study_entry = study_annotations.get(reference_id)

        if study_entry is not None:
            study_path, study_data = study_entry

            annotation_path = str(study_path)
            annotation = study_data

        records.append(
            ReferenceRecord(
                reference_id=reference_id,
                concept=concept,
                rendered_path=str(rendered_path),
                raw_path=raw_path,
                annotation_path=annotation_path,
                annotation=annotation,
                runtime_annotation=runtime_annotations.get(reference_id),
            )
        )

    return records


def get_reference(
    reference_id: str,
) -> ReferenceRecord:
    """
    Retrieve one reference by its stable reference ID.
    """

    for record in load_reference_registry():
        if record.reference_id == reference_id:
            return record

    raise KeyError(
        f"Unknown reference_id: {reference_id!r}"
    )
