from pathlib import Path
import json
import re


REFERENCE_DIR = Path(__file__).parent / "references"
RENDERED_DIR = REFERENCE_DIR / "rendered"
CATALOG_PATH = REFERENCE_DIR / "references.json"


def filename_to_concept(filename: str) -> str:
    """
    Convert a filename such as:

        img_babyshower.png

    into a first-pass human-readable concept name.

    This is only a fallback. Some compound names may need
    manual correction in references.json afterward.
    """

    stem = Path(filename).stem

    # Remove our standard img_ prefix.
    if stem.startswith("img_"):
        stem = stem[4:]

    # Convert underscores and hyphens to spaces.
    stem = re.sub(r"[_-]+", " ", stem)

    return stem.title()


def build_catalog():
    png_files = sorted(RENDERED_DIR.glob("*.png"))

    if not png_files:
        print("No rendered PNG references found.")
        return

    catalog = []

    for png_path in png_files:
        catalog.append(
            {
                "concept": filename_to_concept(png_path.name),
                "file": png_path.name,
            }
        )

    CATALOG_PATH.write_text(
        json.dumps(
            catalog,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"Created catalog with {len(catalog)} references:"
    )
    print(CATALOG_PATH)


if __name__ == "__main__":
    build_catalog()