"""Recreate selected historical shots with the new registry through genuine Flow CDP.

Preview assets live in a separate run. Existing jobs/revisions are read-only.
Repeat calls collect existing downloaded artifacts and refuse unknown submissions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

SYS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SYS))

from flow_prompts import compile_pinned, create_pin, validate_pin
from visual_style import STYLE_VERSION

SAMPLES = [
    ("night-study", "collectors-fallacy-16x9", 6, "SC11_I1", "16:9", "full_scene",
     "A stick-figure student studies an external drive beside a laptop at night, curious about the unread material. A simple desk and a window suggesting night establish the room. Keep the device, face and hands clear. Suggest other furniture with a few quiet shapes; use soft ambient fill rather than making the room nearly black."),
    ("daylight-reading", "collectors-fallacy-16x9", 6, "SC16_I1", "16:9", "full_scene",
     "A stick-figure student calmly reads two selected articles at a small desk in a naturally lit study room. Suggest the room with a light wall and a simple window. Focus on the reading gesture and papers; simplify secondary furniture and omit individual rows of decorative books."),
    ("research-committee", "adversarial-ai-16x9", 6, "SC02_I1", "16:9", "full_scene",
     "Three stick-figure professors sit behind a table in a research defense room, listening with thoughtful, serious expressions. A simple wall and door suggest the room. The three faces and gestures form the focal group. Keep the tabletop simple, with only the papers needed for the discussion; omit decorative shelves and tiny background charts."),
    ("prediction-concept", "adversarial-ai-16x9", 6, "SC03_I1", "16:9", "full_scene",
     "Two stick figures examine a branching prediction diagram in a conceptual computer-science space. One follows a branch while the other points to an alternative. Show only a few clear branches to communicate a choice. Suggest the surrounding space with quiet light shapes instead of racks, cables and repeated screens. No glowing hologram is needed."),
    ("forest-observation", "feynman-jargon-trap-16x9", 3, "SC10_I1", "16:9", "full_scene",
     "A young stick-figure boy walks beside his stick-figure father on a sunlit woodland path, looking curiously toward a bird on a branch. A few simplified trunks and broad leaf shapes suggest the forest. Keep the two figures and bird clear; suggest the remaining foliage with light color areas rather than drawing every leaf or tree."),
    ("saved-posts", "collectors-fallacy-9x16", 8, "SC02_I1", "9:16", "macro_prop",
     "Close view of a simplified white cartoon hand holding a phone with old saved study posts. Use three spacious post cards and a single small clock symbol to suggest material left unread for a long time. Focus on the hand and phone; suggest the surrounding room with a few quiet light color shapes. No repeated tiny icons or readable lettering."),
]


def write_json(path: Path, value: Any) -> None:
    """Persist preview evidence atomically, outside production job state."""
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def prepare(source: Path, output: Path) -> dict[str, Any]:
    """Freeze exact prompts and historical source hashes before provider sends."""
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = output / "preview.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        validate_pin(manifest["pin"])
        return manifest
    pin = create_pin("NanoBanana2Lite", STYLE_VERSION)
    samples = []
    for name, job, revision, image_id, ratio, shot, description in SAMPLES:
        gallery = source / "sys/runs" / job / f"revisions/images/{revision}/gallery.json"
        old = next(item for item in json.loads(gallery.read_text())["items"] if item["image_id"] == image_id)
        old_file = source / "sys/runs" / job / old["path"]
        data = {"description": description, "aspect_ratio": ratio, "shot_type": shot, "allowed_text": []}
        compiled = compile_pinned(pin, "scene", data)
        samples.append({"name": name, "source_job": job, "source_revision": revision,
                        "source_image": str(old_file), "source_sha256": hashlib.sha256(old_file.read_bytes()).hexdigest(),
                        "original_description": old["prompt"], "data": data, "compilation": compiled, "status": "prepared"})
    manifest = {"kind": "authorized-style-preview", "pin": pin, "samples": samples}
    write_json(manifest_path, manifest)
    return manifest


def generate(manifest: dict[str, Any], output: Path, transport_root: Path) -> None:
    """Use the installed bridge/leases; never regenerate an ambiguous request."""
    sys.path.insert(0, str(transport_root / "sys"))
    from flow_cdp.bridge import generate_cdp_image
    from PIL import Image

    for sample in manifest["samples"]:
        folder = output / sample["name"]
        folder.mkdir(exist_ok=True)
        if sample["status"] == "downloaded":
            path = Path(sample["result"]["path"])
            if hashlib.sha256(path.read_bytes()).hexdigest() != sample["result"]["sha256"]:
                raise RuntimeError("Downloaded preview bytes changed; inspect instead of resubmitting")
            continue
        if sample["status"] != "prepared":
            raise RuntimeError("Preview submission is unresolved; reconcile the original request before another send")
        expected = compile_pinned(manifest["pin"], "scene", sample["data"])
        if expected != sample["compilation"]:
            raise RuntimeError("Preview compilation changed after freeze")
        sample["status"] = "submitted"
        write_json(output / "preview.json", manifest)
        print("Generating " + sample["name"], flush=True)
        try:
            result = generate_cdp_image(prompt=expected["prompt"], ratio=sample["data"]["aspect_ratio"],
                                        out_dir=folder, test_case=sample["name"], timeout=240.0,
                                        model=manifest["pin"]["model"], use_character_ref=False,
                                        job_id=output.name)
            path = Path(result["path"])
            with Image.open(path) as image:
                width, height = image.size
                image.verify()
            ratio = 16 / 9 if sample["data"]["aspect_ratio"] == "16:9" else 9 / 16
            if abs(width / height - ratio) > 0.04 or not result.get("forge_id"):
                raise RuntimeError("Provider result lacks required aspect ratio or media identity")
            sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
            if result.get("sha256") != sha256:
                raise RuntimeError("Provider result hash differs from collected bytes")
            metadata = {"jobId": output.name, "prompt": expected["prompt"], "ratio": sample["data"]["aspect_ratio"],
                        "characters": [], "source": "google-flow", "status": "downloaded", "forgeId": result["forge_id"],
                        "sha256": sha256, "width": width, "height": height,
                        "prompt_template": {key: value for key, value in expected.items() if key != "prompt"}}
            write_json(path.with_suffix(".json"), metadata)
            sample.update(status="downloaded", result={**result, "width": width, "height": height})
            print("Downloaded " + sample["name"] + f" ({width}x{height})", flush=True)
        except Exception as error:
            sample.update(status="not_submitted" if getattr(error, "generation_submitted", None) is False else "unknown",
                          error=str(error))
            write_json(output / "preview.json", manifest)
            raise
        write_json(output / "preview.json", manifest)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=SYS.parent)
    parser.add_argument("--transport-root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--generate", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    manifest = prepare(args.source_root.resolve(), output)
    if args.generate:
        generate(manifest, output, (args.transport_root or args.source_root).resolve())
    print(json.dumps({"output": str(output), "states": {sample["name"]: sample["status"] for sample in manifest["samples"]}}, indent=2))


if __name__ == "__main__":
    main()
