from pathlib import Path
import subprocess
import re


REFERENCE_DIR = Path("references").resolve()
RAW_DIR = REFERENCE_DIR / "raw"
OUTPUT_DIR = REFERENCE_DIR / "rendered"

CHROME_PATH = Path(
    r"C:\Program Files\Google\Chrome\Application\chrome.exe"
)

OUTPUT_DIR.mkdir(exist_ok=True)


def get_svg_dimensions(svg_path):
    text = svg_path.read_text(encoding="utf-8")

    width_match = re.search(r'<svg[^>]*\bwidth="(\d+)', text)
    height_match = re.search(r'<svg[^>]*\bheight="(\d+)', text)

    if not width_match or not height_match:
        raise ValueError(
            f"Could not find width and height in {svg_path.name}"
        )

    width = int(width_match.group(1))
    height = int(height_match.group(1))

    return width, height


def render_references():
    svg_files = sorted(RAW_DIR.glob("*.svg"))

    if not svg_files:
        print("No SVG reference files found.")
        return

    for svg_path in svg_files:
        output_path = OUTPUT_DIR / f"{svg_path.stem}.png"

        if output_path.exists():
            print(f"Skipping {svg_path.name} (already rendered)")
            continue

        width, height = get_svg_dimensions(svg_path)

        print(
            f"Rendering {svg_path.name} "
            f"at {width}x{height}..."
        )

        subprocess.run(
            [
                str(CHROME_PATH),
                "--headless",
                "--disable-gpu",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                f"--window-size={width},{height}",
                f"--screenshot={output_path}",
                svg_path.as_uri(),
            ],
            check=True,
        )

        print(f"  -> {output_path}")

    print(f"\nRendered {len(svg_files)} reference images.")


if __name__ == "__main__":
    render_references()
    