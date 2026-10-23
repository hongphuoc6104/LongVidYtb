"""Remote worker: verifies bounded inputs; builds timeline/captions and MP4 on Colab."""

import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path


def _occurrence(text, anchor):
    start = 0
    for _ in range(anchor["occurrence"]):
        pos = text.find(anchor["quote"], start)
        if pos < 0:
            raise ValueError("Anchor quote/occurrence not in narration")
        start = pos + len(anchor["quote"])
    return pos


def _word_anchor_time(segment, offset):
    tokens = list(re.finditer(r"\S+", segment.get("text", "")))
    stamps = segment.get("word_timestamps")
    if not isinstance(stamps, list) or len(stamps) != len(tokens):
        return None
    duration = float(segment.get("content_end", segment["end"])) - float(segment["start"])
    previous_end = 0.0
    previous_start = 0.0
    for token, stamp in zip(tokens, stamps, strict=True):
        if not isinstance(stamp, dict) or stamp.get("word") != token.group():
            return None
        try:
            left, right = float(stamp["start"]), float(stamp["end"])
        except (KeyError, TypeError, ValueError):
            return None
        if (
            not all(math.isfinite(value) for value in (left, right))
            or not 0 <= previous_start <= left < right <= duration + 0.002
            or left + 0.02 < previous_end
        ):
            return None
        previous_start = left
        previous_end = right
    for index, token in enumerate(tokens):
        if token.start() <= offset < token.end():
            return float(segment["start"]) + float(stamps[index]["start"])
    return None


def _build_timeline(c, images, audio, language, ratio, load):
    by_id = {(im.get("image_id", im["scene_id"]), im.get("ratio", ratio)): im for im in images["items"]}
    output = []
    camera_module = load("vp_camera_motion", "scripts/camera_motion.py")
    scene_camera_motions = camera_module.scene_camera_motions
    pacing_module = load("vp_visual_pacing", "visual_pacing.py")
    smooth_interpolated_beats = pacing_module.smooth_interpolated_beats

    for sc in c["scenes"]:
        track = audio.get("tracks", {}).get(language)
        track_segments = (
            track["segments"]
            if track
            else (audio["segments"] if audio.get("language", "vi") == language else audio["en"]["scenes"])
        )
        spans = [x for x in track_segments if x["scene_id"] == sc["id"]]
        start = spans[0]["start"]
        end = spans[-1]["end"]
        if c.get("schema_version") != "3.0":
            im = by_id[(sc["id"], ratio)]
            output.append({"id": sc["id"], "title": sc["title"], "image": im["path"], "start": start, "end": end})
            continue
        text = sc["narration_en" if language == "en" else "narration"]
        beats = []
        for bt, motion in zip(sc["beats"], scene_camera_motions(sc), strict=True):
            offset = _occurrence(text, bt["anchor"][language])
            at = start + offset / max(1, len(text)) * (spans[-1].get("content_end", end) - start)
            timing_method = "narration_anchor_interpolated"
            if all("text" in seg for seg in spans):
                cursor = 0
                for seg in spans:
                    pos = text.find(seg["text"], cursor)
                    if pos < 0:
                        continue
                    if pos <= offset < pos + len(seg["text"]):
                        measured = _word_anchor_time(seg, offset - pos)
                        if measured is not None:
                            at = measured
                            timing_method = "acoustic_word_timestamps"
                        else:
                            at = seg["start"] + (offset - pos) / max(1, len(seg["text"])) * (
                                seg.get("content_end", seg["end"]) - seg["start"]
                            )
                        break
                    cursor = pos + len(seg["text"])
            im = by_id.get((bt["image_id"], ratio))
            if im is None and images.get("reframe_mode"):
                im = by_id[(bt["image_id"], "16:9")]
            if im is None:
                raise ValueError("Missing requested image aspect: " + bt["image_id"])
            beats.append(
                {
                    "id": bt["id"],
                    "src": im["path"],
                    "at": round(at - start, 4),
                    "effect": motion,
                    "camera_motion": motion,
                    "transition": "cut",
                    "focus": bt["focus"],
                    "timing_method": timing_method,
                    "shot_type": next(
                        (
                            image.get("shot_type", "full_scene")
                            for image in sc.get("images", [])
                            if image["id"] == bt["image_id"]
                        ),
                        "full_scene",
                    ),
                }
            )
        smooth_interpolated_beats(beats, start, end)
        beats[0]["at"] = 0
        if any(round(a["at"] * 30) >= round(z["at"] * 30) for a, z in zip(beats, beats[1:], strict=False)):
            raise ValueError("Visual beats collide at 30 fps; revise content anchors")
        methods = {beat["timing_method"] for beat in beats}
        scene_out = {
            "id": sc["id"],
            "title": sc["title"],
            "start": start,
            "end": end,
            "image": beats[0]["src"],
            "images": beats,
            "timing_method": next(iter(methods)) if len(methods) == 1 else "mixed_word_timestamps_and_interpolation",
        }
        output.append(scene_out)
    return output


def run(bundle_path, output_dir, expected_id, expected_worker):
    from pathlib import PurePosixPath

    if hashlib.sha256(Path(__file__).read_bytes()).hexdigest() != expected_worker:
        raise ValueError("Remote worker checksum mismatch")
    device = subprocess.check_output(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True).strip()
    if "T4" not in device:
        raise RuntimeError("COLAB_GPU_REQUIRED: expected an actual NVIDIA T4 runtime")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    inputs = output.parent / "inputs"
    inputs.mkdir(exist_ok=True)
    with zipfile.ZipFile(bundle_path) as archive:
        entries = archive.infolist()
        if (
            len(entries) > 513
            or len({e.filename for e in entries}) != len(entries)
            or sum(e.file_size for e in entries) > 1_001_000_000
        ):
            raise ValueError("Invalid job bundle bounds")
        for entry in entries:
            name = PurePosixPath(entry.filename)
            if (
                name.is_absolute()
                or ".." in name.parts
                or "\\" in entry.filename
                or entry.is_dir()
                or str(name) != entry.filename
                or (entry.external_attr >> 16) & 0o170000 == 0o120000
            ):
                raise ValueError("Unsafe job bundle path")
        archive.extractall(inputs)
    request = json.loads((inputs / "request.json").read_text())
    if (
        request.get("operation") != "render"
        or request.get("request_id") != expected_id
        or request.get("worker_sha256") != expected_worker
    ):
        raise ValueError("Remote job identity mismatch")
    identity = {key: value for key, value in request.items() if key != "request_id"}
    digest = hashlib.sha256(json.dumps(identity, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    if digest != expected_id:
        raise ValueError("Job contract checksum mismatch")
    if any(
        scene.get("layers") or any(image.get("kind", "scene") != "scene" for image in scene.get("images", []))
        for scene in request.get("content", {}).get("scenes", [])
    ):
        raise ValueError("LAYERING_DISABLED: worker accepts full-frame scene images and beats only")
    expected_names = {"request.json", *(entry["name"] for entry in request["files"])}
    if expected_names != {entry.filename for entry in entries}:
        raise ValueError("Job bundle contains unlisted input")
    for entry in request["files"]:
        source = inputs / entry["name"]
        if source.stat().st_size != entry["size"] or hashlib.sha256(source.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError("Job bundle hash mismatch")
    source = inputs / "source"
    sys.path.insert(0, str(source))
    # Load from this immutable bundle, not modules retained by another job kernel.
    import importlib.util

    def load(name, relative):
        spec = importlib.util.spec_from_file_location(name, source / relative)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    contract = load("vp_output_contract", "output_contract.py")
    sys.modules["output_contract"] = contract
    captions = load("vp_subtitles", "scripts/subtitles.py")
    public = output / "public"
    public.mkdir(exist_ok=True)
    tracks = {}
    audits = {}
    brief, audio = request["brief"], request["audio"]
    cue_aspect = brief.get("aspect_ratio") if brief.get("aspect_ratio") in ("9:16", "16:9") else None
    for language in contract.languages(brief):
        track = audio["tracks"][language]
        wav = language + ".wav"
        shutil.copy2(inputs / track["wav"], public / wav)
        cues = track["cues"] if "cues" in track else captions.subtitle_cues(track["segments"], aspect_ratio=cue_aspect)
        audit = captions.audit_cues(cues, aspect_ratio=cue_aspect)
        audits[language] = audit
        if audit["errors"]:
            raise ValueError("Subtitle technical defects: " + json.dumps(audit["errors"]))

        def timestamp(seconds):
            ms = round(seconds * 1000)
            return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"

        (output / ("subtitles_" + language + ".srt")).write_text(
            "\n".join(
                f"{i}\n{timestamp(c['start'])} --> {timestamp(c['end'])}\n{c['text']}\n" for i, c in enumerate(cues, 1)
            )
        )
        by_aspect = {}
        for plan in brief["outputs"]:
            if plan["language"] != language:
                continue
            scenes = _build_timeline(request["content"], request["images"], audio, language, plan["aspect_ratio"], load)
            if brief.get("visual_pacing_profile") == "full_frame_v1" and brief.get("format_profile") != "short_9x16":
                pacing = load("vp_visual_pacing", "visual_pacing.py")
                errors = pacing.check_see_say_beat_density(scenes)
                (output / f"pacing-{language}-{plan['aspect_ratio'].replace(':', 'x')}.json").write_text(
                    json.dumps(
                        {"profile": "full_frame_v1", "errors": errors, "timeline": scenes}, ensure_ascii=False, indent=2
                    )
                )
                if errors:
                    raise ValueError("VISUAL_PACING_FAILED: " + "; ".join(errors))
            for scene in scenes:
                for beat in scene.get("images", []):
                    name = Path(beat["src"]).name
                    shutil.copy2(inputs / beat["src"], public / name)
                    beat["src"] = name
                name = Path(scene["image"]).name
                shutil.copy2(inputs / scene["image"], public / name)
                scene["image"] = name
            by_aspect[plan["aspect_ratio"]] = scenes
        tracks[language] = {
            "audioSrc": wav,
            "duration": track["duration"],
            "cues": cues,
            "scenesByAspect": by_aspect,
            "words": [
                dict(word=word["word"], start=segment["start"] + word["start"], end=segment["start"] + word["end"])
                for segment in track["segments"]
                for word in segment.get("word_timestamps", [])
            ],
        }
    props = {
        "aspect_ratio": brief["aspect_ratio"],
        "outputs": brief["outputs"],
        "primary_language": contract.primary_language(brief),
        "tracks": tracks,
        "render_concurrency": 4,
        "modern_style": True,
        "reframe_mode": brief.get("reframe_mode", False),
        "omni_platform": brief.get("omni_platform", False),
        "hook_title": brief.get("youtube_title", brief.get("topic", "")),
        "thumbnail_spec": brief.get("thumbnail_spec", {}),
    }
    if request.get("visual_style_profile"):
        props["visual_style_profile"] = request["visual_style_profile"]
    if brief.get("omni_platform"):
        omni = load("vp_omni_render", "omni_render.py")
        props["short_deliveries"] = omni.prepare_shorts(
            brief,
            request["content"],
            audio,
            request["images"],
            inputs,
            public,
            captions,
            tracks["vi"]["scenesByAspect"]["16:9"],
        )
        for delivery in props["short_deliveries"]:
            if request.get("visual_style_profile"):
                delivery["props"]["visual_style_profile"] = request["visual_style_profile"]
    wants_sound_design = bool(
        brief.get("omni_platform")
        or brief.get("visual_pacing_profile") == "full_frame_v1"
        or brief.get("enable_sound_design")
    )
    if wants_sound_design and (source / "assets/sfx/ambient_focus_loop.wav").is_file():
        for sound in (source / "assets/sfx").glob("*.wav"):
            shutil.copy2(sound, public / sound.name)
        props["bgmSrc"] = "ambient_focus_loop.wav"
        props["bgmDuckedVolume"] = 10 ** (-28 / 20)
        props["bgmSwellVolume"] = 10 ** (-22 / 20)
        props["sfx_events"] = [{"at": 0, "src": "pop_clean.wav"}]
        cue_map = {
            "pop": "pop_clean",
            "whoosh": "whoosh_soft",
            "page_turn": "page_flip",
            "pen_scratch": "pen_highlight",
            "clock_tick": "clock_tick",
            "ding": "ding_insight",
        }
        master = tracks[contract.primary_language(brief)]
        scene_times = next(iter(master["scenesByAspect"].values()), [])
        for scene, timed in zip(request["content"].get("scenes", []), scene_times, strict=False):
            for beat, timing in zip(scene.get("beats", []), timed.get("images", []), strict=False):
                cue = (
                    beat.get("foley_cue") or scene.get("foley_cue") or beat.get("purpose") or scene.get("action") or ""
                )
                if not beat.get("foley_cue") and timing["at"] != 0:
                    continue
                key = (
                    cue
                    if cue in cue_map
                    else next(
                        (
                            key
                            for phrase, key in [
                                ("lật", "page_turn"),
                                ("sách", "page_turn"),
                                ("giấy", "page_turn"),
                                ("bút", "pen_scratch"),
                                ("gạch", "pen_scratch"),
                                ("viết", "pen_scratch"),
                                ("đồng hồ", "clock_tick"),
                                ("tích tắc", "clock_tick"),
                                ("whoosh", "whoosh"),
                                ("click", "pop"),
                                ("hoàn tất", "ding"),
                            ]
                            if phrase in cue.lower()
                        ),
                        None,
                    )
                )
                if key:
                    props["sfx_events"].append(
                        {"at": round(timed["start"] + timing["at"], 3), "src": cue_map[key] + ".wav"}
                    )
    (output / "editorial-audit.json").write_text(
        json.dumps(
            {"tracks": audits, "processing_location": "colab", "quality_approval": False}, ensure_ascii=False, indent=2
        )
    )
    (output / "props.json").write_text(json.dumps(props, ensure_ascii=False, indent=2))
    # Remote dependencies are cached by the pinned source package lock.
    runtime = output.parent.parent / (
        "render-runtime-" + hashlib.sha256((source / "package-lock.json").read_bytes()).hexdigest()[:16]
    )
    runtime.mkdir(exist_ok=True)
    for name in ("package.json", "package-lock.json"):
        shutil.copy2(source / name, runtime / name)
    if not (runtime / "node_modules/@remotion/renderer").is_dir():
        subprocess.run(["npm", "ci", "--no-audit", "--no-fund"], cwd=runtime, check=True, timeout=900)
    shutil.copytree(source / "renderer", runtime / "renderer", dirs_exist_ok=True)
    chrome = subprocess.check_output(
        [
            "node",
            "--input-type=module",
            "-e",
            "import {chromium} from 'playwright'; console.log(chromium.executablePath())",
        ],
        cwd=runtime,
        text=True,
    ).strip()
    if not Path(chrome).is_file():
        subprocess.run(
            ["npx", "--no-install", "playwright", "install", "--with-deps", "chromium"],
            cwd=runtime,
            check=True,
            timeout=900,
        )
    if Path("/usr/lib64-nvidia/libEGL_nvidia.so.0").is_file():
        vendor_dir = Path("/usr/share/glvnd/egl_vendor.d")
        vendor_dir.mkdir(parents=True, exist_ok=True)
        (vendor_dir / "10_nvidia.json").write_text(
            json.dumps(
                {"file_format_version": "1.0.0", "ICD": {"library_path": "/usr/lib64-nvidia/libEGL_nvidia.so.0"}},
                indent=2,
            )
        )
    wrapper = runtime / "chrome-wrapper.sh"
    wrapper.write_text(f"""#!/usr/bin/env bash
if [ -f "/usr/lib64-nvidia/libEGL_nvidia.so.0" ]; then
  export LD_LIBRARY_PATH="/usr/lib64-nvidia:${{LD_LIBRARY_PATH}}"
  exec "{chrome}" \\
    --no-sandbox \\
    --disable-dev-shm-usage \\
    --use-gl=angle \\
    --use-angle=gl-egl \\
    --enable-gpu \\
    --enable-gpu-rasterization \\
    --enable-zero-copy \\
    --ignore-gpu-blocklist \\
    --run-all-compositor-stages-before-draw \\
    --disable-checker-imaging \\
    --disable-new-content-rendering-timeout \\
    "$@"
else
  exec "{chrome}" \\
    --no-sandbox \\
    --disable-dev-shm-usage \\
    --run-all-compositor-stages-before-draw \\
    --disable-checker-imaging \\
    --disable-new-content-rendering-timeout \\
    --disable-gpu-rasterization \\
    --enable-gpu \\
    --ignore-gpu-blocklist \\
    "$@"
fi
""")
    wrapper.chmod(0o755)
    env = dict(os.environ, VP_CHROME_PATH=str(wrapper), DISABLE_FROM_SURFACE="true")
    env.pop("DISPLAY", None)
    started = time.monotonic()
    render_cmd = ["node", str(runtime / "renderer/render.mjs"), str(output.resolve())]
    subprocess.run(render_cmd, cwd=runtime, env=env, check=True, timeout=3600)
    deliveries = []
    for plan in brief["outputs"]:
        file = (
            "video.mp4"
            if len(brief["outputs"]) == 1
            else ("video_9x16.mp4" if plan["aspect_ratio"] == "9:16" else "video_16x9.mp4")
        )
        probe = json.loads(
            subprocess.check_output(
                ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(output / file)],
                text=True,
            )
        )
        video = [s for s in probe["streams"] if s["codec_type"] == "video"]
        sound = [s for s in probe["streams"] if s["codec_type"] == "audio"]
        if len(video) != 1 or len(sound) != 1:
            raise ValueError("MP4 must have one video and one audio stream")
        wanted_size = (1080, 1920) if plan["aspect_ratio"] == "9:16" else (1920, 1080)
        if (
            (video[0]["width"], video[0]["height"]) != wanted_size
            or video[0]["codec_name"] != "h264"
            or sound[0]["codec_name"] != "aac"
        ):
            raise ValueError("Encoded MP4 stream/size mismatch")
        if abs(float(probe["format"]["duration"]) - audio["tracks"][plan["language"]]["duration"]) > 0.25:
            raise ValueError("Encoded MP4 duration mismatch")
        deliveries.append(
            dict(
                plan,
                file=file,
                width=video[0]["width"],
                height=video[0]["height"],
                duration=float(probe["format"]["duration"]),
                video_codec=video[0]["codec_name"],
                audio_codec=sound[0]["codec_name"],
            )
        )
    supplemental = []
    if brief.get("omni_platform"):
        main = next(plan for plan in deliveries if plan["aspect_ratio"] == "16:9")
        for file, subtitles in [("video_youtube_16x9.mp4", False), ("video_facebook_16x9.mp4", True)]:
            probe = json.loads(
                subprocess.check_output(
                    ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(output / file)],
                    text=True,
                )
            )
            video = next(stream for stream in probe["streams"] if stream["codec_type"] == "video")
            sound = next(stream for stream in probe["streams"] if stream["codec_type"] == "audio")
            if (video["width"], video["height"], video["codec_name"], sound["codec_name"]) != (
                1920,
                1080,
                "h264",
                "aac",
            ) or abs(float(probe["format"]["duration"]) - main["duration"]) > 0.25:
                raise ValueError("Invalid supplemental delivery streams")
            supplemental.append(dict(main, file=file, subtitles=subtitles))
        for short in props["short_deliveries"]:
            file = short["file"]
            probe = json.loads(
                subprocess.check_output(
                    ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(output / file)],
                    text=True,
                )
            )
            video = next(stream for stream in probe["streams"] if stream["codec_type"] == "video")
            sound = next(stream for stream in probe["streams"] if stream["codec_type"] == "audio")
            duration = float(probe["format"]["duration"])
            if (video["width"], video["height"], video["codec_name"], sound["codec_name"]) != (
                1080,
                1920,
                "h264",
                "aac",
            ) or abs(duration - short["props"]["duration"]) > 0.25:
                raise ValueError("Invalid short delivery streams")
            supplemental.append(
                dict(
                    file=file,
                    language="vi",
                    aspect_ratio="9:16",
                    subtitles=True,
                    width=1080,
                    height=1920,
                    duration=duration,
                    video_codec="h264",
                    audio_codec="aac",
                )
            )
    files = {
        p.name: {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "size": p.stat().st_size}
        for p in output.iterdir()
        if p.is_file() and p.suffix in (".mp4", ".png", ".srt", ".json", ".md") and p.name != "render-result.json"
    }
    result = {
        "request_id": expected_id,
        "operation": "render",
        "processing_location": "colab",
        "outputs": deliveries,
        "device": device,
        "files": files,
        "supplemental_outputs": supplemental,
        "elapsed_seconds": time.monotonic() - started,
        "processing": ["timeline", "subtitles", "layout", "render", "encode", "ffprobe"],
        "quality_approval": False,
    }
    (output / "render-result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    with zipfile.ZipFile(output.with_suffix(".zip"), "w", zipfile.ZIP_DEFLATED) as archive:
        for name in ["render-result.json", *files]:
            archive.write(output / name, name)
    return result
