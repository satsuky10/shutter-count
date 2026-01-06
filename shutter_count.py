#!/usr/bin/env python3
"""
shutter_count.py - Extract shutter count from camera image files.

Usage:
    python shutter_count.py image.arw
    python shutter_count.py image.jpg
    python shutter_count.py *.arw

Requires exiftool to be installed.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

__version__ = "0.1.0"


@dataclass
class ShutterCountResult:
    """Result of shutter count extraction."""
    file_path: str
    shutter_count: int | None
    camera_make: str | None
    camera_model: str | None
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.shutter_count is not None and self.error is None


# Shutter count EXIF tags by manufacturer
SHUTTER_COUNT_TAGS = {
    "sony": ["ImageCount", "ShutterCount"],
    "canon": ["ShutterCount", "ImageCount"],
    "nikon": ["ShutterCount", "ImageCount"],
    "fujifilm": ["ImageCount", "ShutterCount"],
}

ALL_SHUTTER_TAGS = ["ImageCount", "ShutterCount", "ShutterCount2", "ImageNumber"]


def find_exiftool() -> str | None:
    """Find exiftool executable in PATH."""
    return shutil.which("exiftool")


def run_exiftool(file_path: Path, tags: list[str]) -> dict:
    """Run exiftool and return parsed JSON output."""
    exiftool_path = find_exiftool()
    if not exiftool_path:
        raise RuntimeError(
            "exiftool not found. Please install exiftool:\n"
            "  macOS: brew install exiftool\n"
            "  Ubuntu/Debian: sudo apt install libimage-exiftool-perl\n"
            "  Windows: https://exiftool.org/"
        )

    tag_args = [f"-{tag}" for tag in tags]
    cmd = [exiftool_path, "-json", "-Make", "-Model", *tag_args, str(file_path)]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(f"exiftool failed: {result.stderr}")

    data = json.loads(result.stdout)
    if not data:
        raise RuntimeError("No EXIF data found")

    return data[0]


def extract_shutter_count(exif_data: dict, camera_make: str | None) -> int | None:
    """Extract shutter count from EXIF data based on camera make."""
    priority_tags = ALL_SHUTTER_TAGS
    if camera_make:
        make_lower = camera_make.lower()
        for manufacturer, tags in SHUTTER_COUNT_TAGS.items():
            if manufacturer in make_lower:
                priority_tags = tags
                break

    for tag in priority_tags:
        value = exif_data.get(tag)
        if value is not None:
            try:
                return int(value)
            except (ValueError, TypeError):
                continue
    return None


def get_shutter_count(file_path: str | Path) -> ShutterCountResult:
    """Extract shutter count from a camera image file."""
    path = Path(file_path)

    if not path.exists():
        return ShutterCountResult(
            file_path=str(path), shutter_count=None,
            camera_make=None, camera_model=None,
            error=f"File not found: {path}"
        )

    if not path.is_file():
        return ShutterCountResult(
            file_path=str(path), shutter_count=None,
            camera_make=None, camera_model=None,
            error=f"Not a file: {path}"
        )

    try:
        exif_data = run_exiftool(path, ALL_SHUTTER_TAGS)
        camera_make = exif_data.get("Make")
        camera_model = exif_data.get("Model")
        shutter_count = extract_shutter_count(exif_data, camera_make)

        if shutter_count is None:
            return ShutterCountResult(
                file_path=str(path), shutter_count=None,
                camera_make=camera_make, camera_model=camera_model,
                error="Shutter count not found in EXIF data."
            )

        return ShutterCountResult(
            file_path=str(path), shutter_count=shutter_count,
            camera_make=camera_make, camera_model=camera_model
        )

    except (RuntimeError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
        return ShutterCountResult(
            file_path=str(path), shutter_count=None,
            camera_make=None, camera_model=None,
            error=str(e)
        )


def main():
    parser = argparse.ArgumentParser(
        description="Extract shutter count from camera image files."
    )
    parser.add_argument("files", nargs="+", type=Path, metavar="FILE",
                        help="Image file(s) to process")
    parser.add_argument("-v", "--version", action="version",
                        version=f"%(prog)s {__version__}")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Output shutter count number only")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")

    args = parser.parse_args()
    results = [get_shutter_count(f) for f in args.files]

    if args.json:
        data = [{
            "file": r.file_path,
            "shutter_count": r.shutter_count,
            "camera_make": r.camera_make,
            "camera_model": r.camera_model,
            "error": r.error
        } for r in results]
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        for i, r in enumerate(results):
            if i > 0:
                print()
            if r.error:
                print(f"Error: {r.error}")
            elif args.quiet and len(results) == 1:
                print(r.shutter_count)
            else:
                print(f"File: {r.file_path}")
                if r.camera_make or r.camera_model:
                    print(f"Camera: {' '.join(filter(None, [r.camera_make, r.camera_model]))}")
                print(f"Shutter Count: {r.shutter_count:,}")

    return 1 if any(r.error for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
