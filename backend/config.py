from pathlib import Path


# =========================================================
# Paths
# =========================================================

BACKEND_DIR = Path(__file__).resolve().parent

REFERENCE_ROOT = (
    BACKEND_DIR
    / "references"
    / "google_calendar"
)

REFERENCE_CATALOG_PATH = (
    REFERENCE_ROOT
    / "references.json"
)


REFERENCE_ANNOTATIONS_PATH = (
    REFERENCE_ROOT
    / "annotations.jsonl"
)

RENDER_REFERENCE_ANNOTATIONS_PATH = (
    REFERENCE_ROOT
    / "render_annotations.jsonl"
)

REFERENCE_RENDERED_DIR = (
    REFERENCE_ROOT
    / "rendered"
)

REFERENCE_RAW_DIR = (
    REFERENCE_ROOT
    / "raw"
)

REFERENCE_STUDY_DIR = (
    REFERENCE_ROOT
    / "study"
)

GENERATED_DIR = (
    BACKEND_DIR
    / "generated"
)


# =========================================================
# Models
# =========================================================

TEXT_MODEL = "gpt-5.6-luna"

IMAGE_MODEL = "gpt-image-2"
IMAGE_SIZE = "1472x512"
IMAGE_QUALITY = "medium"


# =========================================================
# Pipeline budgets
# =========================================================

DEFAULT_REFERENCE_COUNT = 3
MAX_REFERENCE_COUNT = 4

STANDARD_RENDER_COUNT = 1
EXPLORE_RENDER_COUNT = 3

ENABLE_AUTO_CRITIQUE = False
