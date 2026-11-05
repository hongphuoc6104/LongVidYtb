"""Visual clutter gate: score negative space and detect visual clutter in generated images.

Measures the proportion of quiet, flat canvas (negative space) in an image using
low-variance tile analysis. Modern 2D minimalist explainers (Kurzgesagt, Vox, Primer)
maintain high negative space (>= 60-80%), whereas cluttered AI generations filled with
grids, cross-hatching, and multiple schematics have low negative space (< 40%).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from PIL import Image

DEFAULT_NEGATIVE_SPACE_THRESHOLD = 0.60
DEFAULT_TILE_SIZE = 32
DEFAULT_VARIANCE_THRESHOLD = 25.0


def score_negative_space(
    image: Union[str, Path, Image.Image],
    tile_size: int = DEFAULT_TILE_SIZE,
    var_threshold: float = DEFAULT_VARIANCE_THRESHOLD,
) -> float:
    """Calculate the fraction of quiet, flat canvas (negative space) in an image.

    Divides the image into non-overlapping tiles of size `tile_size x tile_size`
    and measures luminance variance within each tile. Tiles with variance
    <= `var_threshold` are counted as quiet canvas.

    Returns:
        float between 0.0 and 1.0 (e.g. 0.85 means 85% quiet negative space).
    """
    if isinstance(image, (str, Path)):
        img = Image.open(str(image)).convert("L")
    elif isinstance(image, Image.Image):
        img = image.convert("L")
    else:
        raise TypeError(f"Expected file path or PIL.Image, got {type(image)}")

    arr = np.array(img, dtype=np.float32)
    h, w = arr.shape
    h_tiles = h // tile_size
    w_tiles = w // tile_size
    if h_tiles == 0 or w_tiles == 0:
        return 1.0 if float(arr.var()) <= var_threshold else 0.0

    trimmed = arr[: h_tiles * tile_size, : w_tiles * tile_size]
    tiles = trimmed.reshape(h_tiles, tile_size, w_tiles, tile_size).transpose(0, 2, 1, 3)
    variances = tiles.var(axis=(2, 3))
    quiet_tiles = int(np.sum(variances <= var_threshold))
    total_tiles = int(h_tiles * w_tiles)
    return float(quiet_tiles / total_tiles)


def evaluate_image(
    image: Union[str, Path, Image.Image],
    threshold: float = DEFAULT_NEGATIVE_SPACE_THRESHOLD,
    tile_size: int = DEFAULT_TILE_SIZE,
    var_threshold: float = DEFAULT_VARIANCE_THRESHOLD,
) -> Tuple[bool, float]:
    """Check whether an image passes the negative space threshold."""
    score = score_negative_space(image, tile_size=tile_size, var_threshold=var_threshold)
    return score >= threshold, score


def scan_run_directory(
    run_dir: Union[str, Path],
    threshold: float = DEFAULT_NEGATIVE_SPACE_THRESHOLD,
    report_filename: str = "clutter_report.json",
    tile_size: int = DEFAULT_TILE_SIZE,
    var_threshold: float = DEFAULT_VARIANCE_THRESHOLD,
) -> Dict[str, Any]:
    """Scan all images in a run directory and write clutter_report.json."""
    rdir = Path(run_dir)
    if not rdir.is_dir():
        raise FileNotFoundError(f"Run directory not found: {rdir}")

    candidate_paths: List[Path] = []

    # Check revisions/images
    rev_img_dir = rdir / "revisions" / "images"
    if rev_img_dir.is_dir():
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
            candidate_paths.extend(rev_img_dir.rglob(ext))

    # Check images dir
    img_dir = rdir / "images"
    if img_dir.is_dir():
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
            candidate_paths.extend(img_dir.rglob(ext))

    # Check top-level run dir for thumbnails / standalone images
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
        candidate_paths.extend(rdir.glob(ext))

    # De-duplicate paths while preserving order
    seen = set()
    unique_paths: List[Path] = []
    for p in candidate_paths:
        resolved = p.resolve()
        if "cache/colab-render" in str(p) or "revisions/render" in str(p) or "_cluttered_old" in str(p):
            continue
        if resolved not in seen:
            seen.add(resolved)
            unique_paths.append(p)

    results: List[Dict[str, Any]] = []
    failing_images: List[Dict[str, Any]] = []

    for p in sorted(unique_paths):
        try:
            score = score_negative_space(p, tile_size=tile_size, var_threshold=var_threshold)
            passed = bool(score >= threshold)
            entry = {
                "path": str(p),
                "filename": p.name,
                "negative_space_score": round(score, 4),
                "passed": passed,
            }
            results.append(entry)
            if not passed:
                failing_images.append(entry)
        except Exception as exc:
            entry = {
                "path": str(p),
                "filename": p.name,
                "error": str(exc),
                "passed": False,
            }
            results.append(entry)
            failing_images.append(entry)

    report = {
        "run_dir": str(rdir.resolve()),
        "threshold": threshold,
        "total_images": len(results),
        "passing_count": len(results) - len(failing_images),
        "failing_count": len(failing_images),
        "passed": len(failing_images) == 0,
        "failing_images": failing_images,
        "results": results,
    }

    out_path = rdir / report_filename
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point for visual clutter gate."""
    parser = argparse.ArgumentParser(description="Visual Clutter Gate: verify negative space and quiet canvas.")
    parser.add_argument("target", help="Run directory to scan or single image file to evaluate.")
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_NEGATIVE_SPACE_THRESHOLD,
        help=f"Negative space ratio threshold (default: {DEFAULT_NEGATIVE_SPACE_THRESHOLD})",
    )
    parser.add_argument(
        "--report",
        default="clutter_report.json",
        help="Output report filename inside run dir (default: clutter_report.json)",
    )
    parser.add_argument(
        "--tile-size",
        type=int,
        default=DEFAULT_TILE_SIZE,
        help=f"Tile size for variance analysis (default: {DEFAULT_TILE_SIZE})",
    )
    parser.add_argument(
        "--var-threshold",
        type=float,
        default=DEFAULT_VARIANCE_THRESHOLD,
        help=f"Tile variance threshold (default: {DEFAULT_VARIANCE_THRESHOLD})",
    )
    args = parser.parse_args(argv)

    target = Path(args.target)
    if target.is_file():
        passed, score = evaluate_image(
            target,
            threshold=args.threshold,
            tile_size=args.tile_size,
            var_threshold=args.var_threshold,
        )
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {target.name}: negative space = {score:.4f} (threshold = {args.threshold})")
        return 0 if passed else 1
    elif target.is_dir():
        report = scan_run_directory(
            target,
            threshold=args.threshold,
            report_filename=args.report,
            tile_size=args.tile_size,
            var_threshold=args.var_threshold,
        )
        print(
            f"Scan complete for {target}: {report['passing_count']}/{report['total_images']} passed "
            f"(threshold = {args.threshold})."
        )
        if report["failing_count"] > 0:
            print(f"FAILED: {report['failing_count']} images failed negative space gate:")
            for f in report["failing_images"]:
                print(f"  - {f.get('filename')}: score {f.get('negative_space_score', 'error')}")
            return 1
        return 0
    else:
        print(f"Error: target not found: {target}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
