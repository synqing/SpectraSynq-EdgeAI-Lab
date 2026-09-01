#!/usr/bin/env python3
"""Measure text ink against each element crop's dominant background colour."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
CROPS = ROOT / "crops"
ANNOTATED = ROOT / "annotated"
ANNOTATED.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def measure(path: Path) -> dict[str, object]:
    image = Image.open(path).convert("RGB")
    pixels = list(image.getdata())
    background, _ = Counter(pixels).most_common(1)[0]
    coordinates: list[tuple[int, int]] = []
    for y in range(image.height):
        for x in range(image.width):
            pixel = image.getpixel((x, y))
            if max(abs(pixel[index] - background[index]) for index in range(3)) >= 24:
                coordinates.append((x, y))
    if not coordinates:
        raise RuntimeError(f"no ink detected in {path}")
    left = min(item[0] for item in coordinates)
    top = min(item[1] for item in coordinates)
    right = max(item[0] for item in coordinates)
    bottom = max(item[1] for item in coordinates)
    annotated = image.copy()
    ImageDraw.Draw(annotated).rectangle(
        (left, top, right, bottom), outline=(255, 184, 77), width=1
    )
    annotated_path = ANNOTATED / path.name
    annotated.save(annotated_path)
    return {
        "role": path.stem,
        "crop_png": str(path.resolve()),
        "crop_sha256": sha256(path),
        "annotated_crop_png": str(annotated_path.resolve()),
        "annotated_crop_sha256": sha256(annotated_path),
        "crop_width_px": image.width,
        "crop_height_px": image.height,
        "dominant_background_rgb": list(background),
        "ink_bbox": {"left": left, "top": top, "right": right, "bottom": bottom},
        "ink_width_px": right - left + 1,
        "ink_height_px": bottom - top + 1,
        "measure_method": "dominant_background_delta_24_bbox",
    }


def main() -> int:
    results = [measure(path) for path in sorted(CROPS.glob("*.png"))]
    output = ROOT / "ink-measurements.json"
    output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
