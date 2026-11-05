"""Remote worker: verifies bounded inputs; builds timeline/captions and MP4 on Colab."""

import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path


def _occurrence(text, anchor):
    if isinstance(anchor, str):
        pos = text.find(anchor)
        if pos < 0:
            raise ValueError(f"Anchor quote not in narration: {anchor!r}")
        return pos
    start = 0
    occ = anchor.get("occurrence", 1)
    quote = anchor.get("quote", "")
    last_pos = -1
    for _ in range(occ):
        pos = text.find(quote, start)
        if pos < 0:
            if last_pos >= 0:
                return last_pos
            for word in quote.split():
                p = text.find(word, start)
                if p >= 0:
                    return p
            return max(0, min(start, len(text) - 1))
        last_pos = pos
        start = pos + len(quote)
    return last_pos


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
    by_id = {(im.get("image_id") or im.get("scene_id"), im.get("ratio", ratio)): im for im in images["items"]}
    output = []
    camera_module = load("vp_camera_motion", "scripts/camera_motion.py")
    scene_camera_motions = camera_module.scene_camera_motions

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
        motions = scene_camera_motions(sc)

        seg_spans = []
        cursor = 0
        for seg in spans:
            stext = seg.get("text", "")
            pos = text.find(stext, cursor)
            if pos < 0:
                pos = text.find(stext)
            if pos >= 0:
                seg_spans.append((seg, pos, pos + len(stext)))
                cursor = pos + len(stext)
            else:
                clean_stext = re.sub(r"[^\w\s]", "", stext).strip()
                clean_text = re.sub(r"[^\w\s]", "", text)
                clean_pos = clean_text.find(clean_stext)
                if clean_pos >= 0:
                    seg_spans.append((seg, clean_pos, clean_pos + len(stext)))
                else:
                    seg_spans.append((seg, -1, -1))

        for idx, (bt, motion) in enumerate(zip(sc["beats"], motions, strict=True)):
            offset = _occurrence(text, bt["anchor"][language])
            timing_method = "narration_anchor_interpolated"
            at = None
            if idx == 0 or offset == 0:
                at = start
                timing_method = "measured_sentence_anchor"
            elif seg_spans:
                for seg, p_start, p_end in seg_spans:
                    if p_start >= 0 and p_start <= offset < p_end:
                        if offset == p_start:
                            at = float(seg["start"])
                            timing_method = "measured_sentence_anchor"
                        else:
                            measured = _word_anchor_time(seg, offset - p_start)
                            if measured is not None:
                                at = measured
                                timing_method = "acoustic_word_timestamps"
                            else:
                                prefix = seg["text"][:offset - p_start]
                                prefix_syl = len(prefix.strip().split()) if prefix.strip() else 0
                                total_syl = max(1, len(seg["text"].strip().split()))
                                syllable_ratio = prefix_syl / total_syl
                                seg_content_dur = float(seg.get("content_end", seg["end"])) - float(seg["start"])
                                at = float(seg["start"]) + syllable_ratio * seg_content_dur
                                timing_method = "syllable_interpolated"
                        break

            if at is None:
                prefix = text[:offset]
                prefix_syl = len(prefix.strip().split()) if prefix.strip() else 0
                total_syl = max(1, len(text.strip().split()))
                syllable_ratio = prefix_syl / total_syl
                at = start + syllable_ratio * (spans[-1].get("content_end", end) - start)
                timing_method = "syllable_interpolated"

            rel_at = round(at - start, 4)
            if beats and rel_at <= beats[-1]["at"]:
                rel_at = round(beats[-1]["at"] + 1.0 / 30.0, 4)

            im = by_id.get((bt["image_id"], ratio))
            if im is None and images.get("reframe_mode"):
                im = by_id[(bt["image_id"], "16:9")]
            if im is None:
                raise ValueError("Missing requested image aspect: " + bt["image_id"])
            image_item = next((image for image in sc.get("images", []) if image["id"] == bt["image_id"]), {})
            is_endcard_beat = bool(bt.get("is_endcard") or image_item.get("is_endcard") or bt.get("spec") == "endcard" or image_item.get("spec") == "endcard")
            emphasis_text_beat = bt.get("emphasis_text") or image_item.get("emphasis_text")
            beats.append(
                {
                    "id": bt["id"],
                    "src": im["path"],
                    "at": rel_at,
                    "tempo": bt.get("tempo"),
                    "effect": motion,
                    "camera_motion": motion,
                    "transition": "cut",
                    "focus": bt.get("focus"),
                    "emphasis_text": emphasis_text_beat,
                    "is_endcard": is_endcard_beat,
                    "timing_method": timing_method,
                    "shot_type": image_item.get("shot_type", "full_scene"),
                    "trim_before": bt.get("trim_before", 0),
                    "playback_rate": bt.get("playback_rate", 1.0),
                    "clip_duration": bt.get("clip_duration"),
                }
            )

        if all(beat.get("timing_method") == "narration_anchor_interpolated" for beat in beats):
            pacing_module = load("vp_visual_pacing", "visual_pacing.py")
            smooth_interpolated_beats = pacing_module.smooth_interpolated_beats
            smooth_interpolated_beats(beats, start, end)
        beats[0]["at"] = 0
        for i in range(len(beats) - 1):
            if round(beats[i]["at"] * 30) >= round(beats[i + 1]["at"] * 30):
                beats[i + 1]["at"] = round((round(beats[i]["at"] * 30) + 1) / 30.0, 4)

        scene_dur = max(0.05, float(end) - float(start))
        for i, b_item in enumerate(beats):
            raw_clip_dur = float(b_item.get("clip_duration") or 0.0)
            if raw_clip_dur > 0:
                next_at = float(beats[i + 1]["at"]) if i + 1 < len(beats) else scene_dur
                actual_beat_dur = max(0.15, next_at - float(b_item["at"]))
                avail_clip = max(0.25, raw_clip_dur - (float(b_item.get("trim_before") or 0) / 30.0) - 0.05)
                # Ensure playback_rate covers actual_beat_dur + J/L-cut & crossfade margin without EOF
                safe_rate = avail_clip / (actual_beat_dur + 0.22)
                b_item["playback_rate"] = round(max(0.25, min(1.45, safe_rate)), 3)

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

    t_unpack_start = time.monotonic()
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
    unpack_seconds = round(time.monotonic() - t_unpack_start, 3)

    t_timeline_start = time.monotonic()
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
                errors = pacing.check_see_say_beat_density(
                    scenes, format_profile=plan.get("format_profile", brief.get("format_profile"))
                )
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
        "render_concurrency": 6,
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
    timeline_seconds = round(time.monotonic() - t_timeline_start, 3)

    t_runtime_start = time.monotonic()
    flow_worker = load("vp_flow_video_worker", "colab_bridge/flow_video_worker.py")
    runtime_setup_seconds = round(time.monotonic() - t_runtime_start, 3)

    started = time.monotonic()
    flow_worker.render_props_package(output, require_nvenc=True)
    render_seconds = round(time.monotonic() - started, 3)

    t_ffprobe_start = time.monotonic()
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
    ffprobe_seconds = round(time.monotonic() - t_ffprobe_start, 3)

    t_package_start = time.monotonic()
    layout_data = {}
    if (output / "layout.json").is_file():
        try:
            layout_data = json.loads((output / "layout.json").read_text())
        except Exception:
            layout_data = {}
    files = {
        p.name: {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "size": p.stat().st_size}
        for p in output.iterdir()
        if p.is_file() and p.suffix in (".mp4", ".png", ".srt", ".json", ".md") and p.name != "render-result.json"
    }
    package_seconds = round(time.monotonic() - t_package_start, 3)
    result = {
        "request_id": expected_id,
        "operation": "render",
        "processing_location": "colab",
        "render_engine": "ffmpeg_h264_nvenc",
        "outputs": deliveries,
        "device": device,
        "files": files,
        "supplemental_outputs": supplemental,
        "elapsed_seconds": time.monotonic() - started,
        "remotion_concurrency": layout_data.get("remotion_concurrency"),
        "stage_timings": {
            "unpack_seconds": unpack_seconds,
            "timeline_seconds": timeline_seconds,
            "runtime_setup_seconds": runtime_setup_seconds,
            "render_seconds": render_seconds,
            "ffprobe_seconds": ffprobe_seconds,
            "package_seconds": package_seconds,
        },
        "processing": ["timeline", "subtitles", "layout", "render", "encode", "ffprobe"],
        "quality_approval": False,
    }
    (output / "render-result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    with zipfile.ZipFile(output.with_suffix(".zip"), "w", zipfile.ZIP_DEFLATED) as archive:
        for name in ["render-result.json", *files]:
            archive.write(output / name, name)
    return result
