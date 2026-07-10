#!/usr/bin/env python3
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "apartmancvikov" / "static"
OUTPUT_DIR = STATIC_DIR / "responsive"
MANIFEST_PATH = OUTPUT_DIR / "manifest.json"

sys.path.insert(0, str(BASE_DIR))

from apartmancvikov.image_config import available_widths, variant_path  # noqa: E402

JPEG_QUALITY = 86
WEBP_QUALITY = 82
GM_BINARY = shutil.which("gm")


def digest(path):
    """Return a stable SHA-256 digest for a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sources():
    """Yield every source photograph used by the website."""
    yield STATIC_DIR / "bg.jpg"
    yield from sorted((STATIC_DIR / "foto").glob("*.jpg"))
    yield from sorted((STATIC_DIR / "vylety").glob("*.jpg"))


def dimensions(path):
    """Read source dimensions through GraphicsMagick."""
    result = subprocess.run(  # noqa: S603
        [GM_BINARY, "identify", "-format", "%w %h", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    width, height = result.stdout.split()
    return int(width), int(height)


def output_path(source, width, extension):
    """Resolve an output variant path for a source photograph."""
    relative = source.relative_to(STATIC_DIR).as_posix()
    return STATIC_DIR / variant_path(relative, width, extension)


def convert(source, destination, width, extension):
    """Create one stripped, resized derivative without changing its aspect ratio."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    quality = WEBP_QUALITY if extension == "webp" else JPEG_QUALITY

    def run(target, interlace=None):
        command = [
            GM_BINARY,
            "convert",
            str(source),
            "-auto-orient",
            "-resize",
            f"{width}x>",
            "+profile",
            "*",
            "-quality",
            str(quality),
        ]
        if interlace:
            command.extend(["-interlace", interlace])
        command.append(str(target))
        subprocess.run(command, check=True)  # noqa: S603

    if extension != "jpg":
        run(destination)
        return

    progressive = destination.with_suffix(f".progressive{destination.suffix}")
    run(destination, "Plane")
    try:
        run(progressive, "Line")
        if progressive.stat().st_size < destination.stat().st_size:
            progressive.replace(destination)
    finally:
        progressive.unlink(missing_ok=True)


def expected_output_paths():
    """Return all outputs described by the current source files and settings."""
    result = []
    for source in sources():
        width, _height = dimensions(source)
        result.extend(
            output_path(source, variant_width, extension)
            for variant_width in available_widths(width)
            for extension in ("jpg", "webp")
        )
    return result


def build_manifest(outputs):
    """Describe sources, outputs and encoding settings for CI verification."""
    return {
        "settings": {
            "jpeg_quality": JPEG_QUALITY,
            "webp_quality": WEBP_QUALITY,
            "widths": list(available_widths(10_000)),
        },
        "sources": {
            path.relative_to(STATIC_DIR).as_posix(): digest(path) for path in sources()
        },
        "outputs": {
            path.relative_to(STATIC_DIR).as_posix(): digest(path) for path in outputs
        },
    }


def generate():
    """Regenerate all responsive assets and their manifest."""
    if GM_BINARY is None:
        raise SystemExit("GraphicsMagick (gm) is required to generate images.")

    expected = expected_output_paths()
    expected_set = set(expected)
    if OUTPUT_DIR.exists():
        for existing in OUTPUT_DIR.rglob("*"):
            if (
                existing.is_file()
                and existing != MANIFEST_PATH
                and existing not in expected_set
            ):
                existing.unlink()

    for source in sources():
        width, _height = dimensions(source)
        for variant_width in available_widths(width):
            for extension in ("jpg", "webp"):
                convert(
                    source,
                    output_path(source, variant_width, extension),
                    variant_width,
                    extension,
                )

    manifest = build_manifest(expected)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def check():
    """Verify source and output hashes without requiring image conversion."""
    if not MANIFEST_PATH.exists():
        raise SystemExit("Responsive image manifest is missing; regenerate images.")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    current_sources = {
        path.relative_to(STATIC_DIR).as_posix(): digest(path) for path in sources()
    }
    if manifest.get("sources") != current_sources:
        raise SystemExit("Source images changed; regenerate responsive images.")

    recorded_outputs = manifest.get("outputs", {})
    for relative, expected_digest in recorded_outputs.items():
        path = STATIC_DIR / relative
        if not path.exists() or digest(path) != expected_digest:
            message = f"Responsive image is missing or stale: {relative}"
            raise SystemExit(message)


def main():
    """Generate image derivatives or verify their committed manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify committed variants instead of regenerating them",
    )
    args = parser.parse_args()
    check() if args.check else generate()


if __name__ == "__main__":
    main()
