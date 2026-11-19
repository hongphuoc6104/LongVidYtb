"""Single-Pass 4-GPU Colab T4 Renderer, Lossless Concat & Giant >=132px Heroic Banner Compositor."""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import tempfile
import threading
import time
import wave
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from colab_bridge.client import Client
from colab_bridge.pool_manager import ColabPoolDispatcher, ColabPoolManager
from fx_warehouse.hud_widgets import build_bespoke_topic_hud_patch
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import maximum_filter1d
from tools.produce_vn_dual_mode import _compute_bottom_right_delogo_filter, make_rounded_watermark

from short_engine import (
    FPS,
    HEIGHT,
    HUD_MAX_WIDTH,
    MAX_OVERLAY_WORDS,
    MIN_OVERLAY_FONT_SIZE,
    POSTER_FRAMES,
    SCALE_H,
    SCALE_W,
    SYS_DIR,
    WIDTH,
    ffprobe_json,
    logger,
    measure_ebur128,
    select_idle_colab_accounts,
    text_tail,
)
from short_engine.audio_epic import slice_ass_for_window
from short_engine.flow_stage import classify_hybrid_beats

VALID_NVENC_PRESETS = ("p4", "p5", "p6")
VALID_RENDER_MODES = ("single_pass", "two_pass")


def _parse_rate(rate_str: str | None, default: float = 24.0) -> float:
    if not rate_str or "/" not in rate_str:
        return default
    num_s, den_s = rate_str.split("/", 1)
    try:
        num, den = float(num_s), float(den_s)
        return (num / den) if den > 0 else default
    except ValueError:
        return default


def build_kenburns_filter(
    camera_move: str,
    render_frames: int,
    *,
    width: int = WIDTH,
    height: int = HEIGHT,
    fps: int = FPS,
) -> str:
    """Build smooth 1.0 -> 1.06 Ken Burns pan/zoom FFmpeg filter for 2K PNG inputs."""
    n = max(1, int(render_frames) - 1)
    move = (camera_move or "push_in").strip().lower()
    if move == "pull_back":
        zp = f"z='1.06-0.06*(on/{n})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    elif move == "truck_lateral":
        zp = f"z='1.06':x='(iw-iw/zoom)*(on/{n})':y='ih/2-(ih/zoom/2)'"
    elif move == "tracking_alongside":
        zp = f"z='1.06':x='(iw-iw/zoom)*(1.0-on/{n})':y='ih/2-(ih/zoom/2)'"
    elif move == "crane_up":
        zp = f"z='1.06':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(1.0-on/{n})'"
    elif move == "orbit":
        zp = f"z='1.02+0.04*(on/{n})':x='(iw-iw/zoom)*(0.2+0.6*(on/{n}))':y='ih/2-(ih/zoom/2)'"
    else:
        zp = f"z='1.0+0.06*(on/{n})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    up_w, up_h = (int(round(width * 1.15)) // 2) * 2, (int(round(height * 1.15)) // 2) * 2
    return (
        f"scale={up_w}:{up_h}:flags=bicubic:force_original_aspect_ratio=increase,"
        f"crop={up_w}:{up_h},setsar=1,"
        f"zoompan={zp}:d={int(render_frames)}:s={width}x{height}:fps={fps},setsar=1"
    )


def _load_bold_font(size: int, mono: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        ("/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf")
        if mono
        else (
            "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        )
    )
    for fp in candidates:
        if Path(fp).is_file():
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def render_heroic_banner_png(
    stamp_spec: dict[str, Any],
    width: int = WIDTH,
    height: int = HEIGHT,
) -> tuple[Image.Image, int]:
    """Render giant uppercase banner (`>= 132px`, `<= 4` words, zero sublines/boxes)."""
    del height
    text = str(stamp_spec.get("headline") or stamp_spec.get("text") or "").strip().upper()
    words = text.split()
    if not (1 <= len(words) <= MAX_OVERLAY_WORDS):
        raise ValueError(
            f"Heroic banner requires 1..{MAX_OVERLAY_WORDS} words, got {len(words)}: {text!r}"
        )

    font_size = max(MIN_OVERLAY_FONT_SIZE, int(stamp_spec.get("font_size") or 136))
    font = _load_bold_font(font_size, mono=False)
    stroke_w = 9
    max_line_w = min(width - 140, 1260)

    probe_img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(probe_img)
    single_bb = pdraw.textbbox((0, 0), text, font=font, stroke_width=stroke_w)
    if (single_bb[2] - single_bb[0]) <= max_line_w or len(words) == 1:
        lines = [text]
    else:
        best_split = 1
        best_diff = 10**9
        for cut in range(1, len(words)):
            l1, l2 = " ".join(words[:cut]), " ".join(words[cut:])
            w1 = pdraw.textbbox((0, 0), l1, font=font, stroke_width=stroke_w)[2]
            w2 = pdraw.textbbox((0, 0), l2, font=font, stroke_width=stroke_w)[2]
            diff = abs(w1 - w2) + (5000 if max(w1, w2) > max_line_w else 0)
            if diff < best_diff:
                best_diff = diff
                best_split = cut
        lines = [" ".join(words[:best_split]), " ".join(words[best_split:])]

    line_boxes = [pdraw.textbbox((0, 0), ln, font=font, stroke_width=stroke_w) for ln in lines]
    line_ws = [b[2] - b[0] for b in line_boxes]
    line_hs = [b[3] - b[1] for b in line_boxes]
    line_gap = 18
    pad_x, pad_top, underline_gap, bar_h, pad_bot = 36, 18, 22, 8, 22

    canvas_w = min(width - 40, max(line_ws) + pad_x * 2 + 24)
    text_block_h = sum(line_hs) + line_gap * (len(lines) - 1)
    canvas_h = pad_top + text_block_h + underline_gap + bar_h + pad_bot

    banner = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(banner, "RGBA")

    text_color = (
        (255, 253, 245, 255)
        if str(stamp_spec.get("text_color") or "").lower() == "ivory"
        else (255, 216, 102, 255)
    )
    cur_y = pad_top
    for ln, bb, lw, lh in zip(lines, line_boxes, line_ws, line_hs, strict=True):
        x = (canvas_w - lw) // 2 - bb[0]
        y = cur_y - bb[1]
        draw.text((x + 4, y + 7), ln, font=font, fill=(0, 0, 0, 215), stroke_width=stroke_w + 2, stroke_fill=(0, 0, 0, 215))
        draw.text((x, y), ln, font=font, fill=text_color, stroke_width=stroke_w, stroke_fill=(8, 8, 12, 255))
        cur_y += lh + line_gap

    bar_y = pad_top + text_block_h + underline_gap
    bar_w = max(240, min(canvas_w - 60, int(max(line_ws) * 0.72)))
    bx0 = (canvas_w - bar_w) // 2
    draw.rounded_rectangle([bx0 + 2, bar_y + 3, bx0 + bar_w + 2, bar_y + bar_h + 3], radius=4, fill=(0, 0, 0, 175))
    draw.rounded_rectangle([bx0, bar_y, bx0 + bar_w, bar_y + bar_h], radius=4, fill=(198, 44, 34, 245))
    accent_w = max(80, int(bar_w * 0.56))
    ax0 = (canvas_w - accent_w) // 2
    draw.rounded_rectangle([ax0, bar_y, ax0 + accent_w, bar_y + bar_h], radius=4, fill=(255, 216, 102, 255))

    return banner, font_size


def build_hud_stamps(
    short_spec: dict[str, Any],
    timings: dict[str, Any],
    hud_out_dir: Path,
    preview_path: Path,
    bundle_hud_dir: Path | None = None,
    width: int = WIDTH,
    height: int = HEIGHT,
) -> list[dict[str, Any]]:
    """Render banner/HUD PNGs mapped cleanly to measured `audio_timings.json` windows."""
    stamps_spec = list(short_spec.get("hud_stamps") or [])
    if not stamps_spec:
        return []

    beat_by_id = {str(b["beat_id"]): b for b in timings["beats"]}
    total_dur = float(timings["total_duration_sec"])
    hud_out_dir.mkdir(parents=True, exist_ok=True)
    if bundle_hud_dir is not None:
        bundle_hud_dir.mkdir(parents=True, exist_ok=True)

    rendered_cards: list[tuple[dict[str, Any], Image.Image]] = []
    hud_entries: list[dict[str, Any]] = []

    for stamp_spec in stamps_spec:
        beat_id = str(stamp_spec["beat_id"])
        if beat_id not in beat_by_id:
            raise KeyError(f"HUD stamp beat_id {beat_id!r} not found in audio_timings.json")
        tb = beat_by_id[beat_id]
        b_start, b_end = float(tb["start_sec"]), float(tb["end_sec"])
        hud_start = max(0.22, b_start + 0.15)
        hud_end = min(total_dur - 0.15, b_end - 0.12)
        hud_dur = max(1.2, hud_end - hud_start)
        if hud_end <= hud_start:
            raise RuntimeError(f"Invalid HUD window for {beat_id}: {hud_start:.3f}..{hud_end:.3f}")

        kind = str(stamp_spec.get("kind") or "heroic_banner")
        if kind == "heroic_banner":
            patch, font_size = render_heroic_banner_png(stamp_spec, width=width, height=height)
            anchor_y = int(stamp_spec.get("anchor_y", 150))
        else:
            _, _, legacy_patch = build_bespoke_topic_hud_patch(stamp_spec, t_beat=0.45, dur=4.0, amp=0.35, width=width, height=height)
            patch = legacy_patch.convert("RGBA")
            if patch.width > HUD_MAX_WIDTH:
                patch = patch.resize((HUD_MAX_WIDTH, max(1, int(round(patch.height * (HUD_MAX_WIDTH / float(patch.width)))))), Image.Resampling.LANCZOS)
            font_size = int(stamp_spec.get("font_size") or 36)
            anchor_y = int(stamp_spec.get("anchor_y", 110))

        png_name = f"hud_{beat_id}.png"
        png_path = hud_out_dir / png_name
        patch.save(png_path, format="PNG")
        if bundle_hud_dir is not None:
            shutil.copy2(png_path, bundle_hud_dir / png_name)

        entry = {
            "beat_id": beat_id,
            "kind": kind,
            "headline": str(stamp_spec.get("headline", "")),
            "font_size": font_size,
            "arcname": f"hud_stamps/{png_name}",
            "local_path": str(png_path),
            "width": patch.width,
            "height": patch.height,
            "centered_x": (width - patch.width) // 2,
            "anchor_y": anchor_y,
            "hud_start": round(hud_start, 6),
            "hud_end": round(hud_end, 6),
            "hud_dur": round(hud_dur, 6),
            "beat_start_sec": round(b_start, 6),
            "beat_end_sec": round(b_end, 6),
        }
        hud_entries.append(entry)
        rendered_cards.append((entry, patch))

    header_h, label_h, row_gap, footer_pad = 104, 38, 28, 36
    total_h = header_h + footer_pad + sum(label_h + card.height + row_gap for _, card in rendered_cards)
    preview = Image.new("RGBA", (width, total_h), (14, 16, 21, 255))
    draw = ImageDraw.Draw(preview, "RGBA")
    draw.line([(90, header_h - 12), (90, total_h - 16)], fill=(54, 62, 82, 180), width=2)
    draw.line([(width - 90, header_h - 12), (width - 90, total_h - 16)], fill=(54, 62, 82, 180), width=2)

    f_title, f_lbl = _load_bold_font(30), _load_bold_font(22, mono=True)
    draw.text((48, 24), f"{short_spec.get('job_id', 'SHORT')} — GIANT OVERLAY PREVIEW (MIN {MIN_OVERLAY_FONT_SIZE}px)", font=f_title, fill=(246, 232, 198, 255))
    cur_y = header_h
    for entry, card in rendered_cards:
        lbl = f"{entry['beat_id']} | {entry['hud_start']:.2f}s->{entry['hud_end']:.2f}s | {entry['width']}x{entry['height']} | font={entry['font_size']}px"
        draw.text((90, cur_y), lbl, font=f_lbl, fill=(212, 168, 72, 255))
        card_y = cur_y + label_h
        preview.alpha_composite(card, dest=(entry["centered_x"], card_y))
        cur_y = card_y + card.height + row_gap

    preview_path.parent.mkdir(parents=True, exist_ok=True)
    preview.convert("RGB").save(preview_path, format="PNG")
    return hud_entries


def plan_chunked_render_timeline(
    short_spec: dict[str, Any],
    timings: dict[str, Any],
    *,
    visual_mode: str = "hybrid_2k",
    render_mode: str = "single_pass",
    clips_dir: Path | None = None,
    frames_dir: Path | None = None,
    fps: int = FPS,
    poster_frames: int = POSTER_FRAMES,
    width: int = WIDTH,
    height: int = HEIGHT,
    require_media: bool = False,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    """Build exact frame-accurate 4-chunk render plan (`single_pass` 0 overhang or `two_pass`)."""
    if render_mode not in VALID_RENDER_MODES:
        raise ValueError(f"Unsupported render_mode={render_mode!r}; expected {VALID_RENDER_MODES}")

    classified_beats = classify_hybrid_beats(short_spec, visual_mode=visual_mode)
    t_beats = list(timings.get("beats") or [])
    if not classified_beats or len(t_beats) != len(classified_beats):
        raise RuntimeError(f"Beat count mismatch: timings={len(t_beats)} spec={len(classified_beats)}")
    for tb, sb in zip(t_beats, classified_beats, strict=True):
        if str(tb["beat_id"]) != str(sb["beat_id"]):
            raise RuntimeError(f"Beat ID mismatch: timings={tb['beat_id']} spec={sb['beat_id']}")

    total_frames = int(round(float(timings["total_duration_sec"]) * fps))
    cum_frames = int(poster_frames)
    base_list: list[int] = []
    for idx_b, tb in enumerate(t_beats):
        cum_end = total_frames if idx_b == len(t_beats) - 1 else int(round(float(tb["end_sec"]) * fps))
        bf = max(12, cum_end - cum_frames)
        cum_frames = cum_end
        base_list.append(bf)
    base_list[-1] += (total_frames - int(poster_frames)) - sum(base_list)
    assert int(poster_frames) + sum(base_list) == total_frames

    n_beats = len(classified_beats)
    num_chunks = min(4, max(1, n_beats // 5))
    q, r = divmod(n_beats, num_chunks)
    chunk_sizes = [q + (1 if c < r else 0) for c in range(num_chunks)]

    chunk_ends: set[int] = set()
    cur = 0
    for c_len in chunk_sizes:
        cur += c_len
        chunk_ends.add(cur - 1)

    manifest_items: list[dict[str, Any]] = []
    for i, (sb, bf) in enumerate(zip(classified_beats, base_list, strict=True)):
        asset_mode = str(sb["asset_mode"])
        t_mode = str(sb.get("transition_mode") or "seam")
        prev_t_mode = str(classified_beats[i - 1].get("transition_mode") or "seam") if i > 0 else "none"
        prev_asset_mode = str(classified_beats[i - 1]["asset_mode"]) if i > 0 else "none"

        is_last_global = i == n_beats - 1
        is_single_boundary = render_mode == "single_pass" and (i in chunk_ends)
        if is_last_global or is_single_boundary:
            overlap_frames = 0
        elif asset_mode == "flow_video" and t_mode == "frame_link":
            overlap_frames = 2
        else:
            overlap_frames = 5

        render_frames = bf + overlap_frames
        trim_lead = asset_mode == "flow_video" and i > 0 and prev_asset_mode == "flow_video" and prev_t_mode == "frame_link" and ((i - 1) not in chunk_ends or render_mode == "two_pass")

        if asset_mode == "2k_native_kenburns":
            local_src = (frames_dir / f"beat_{i:02d}.png") if frames_dir is not None else None
            if require_media and (local_src is None or not local_src.is_file()):
                raise FileNotFoundError(f"Missing 2K Ken Burns frame: {local_src}")
            cam_move = str(sb.get("camera_move") or "push_in")
            manifest_items.append({
                "index": i, "beat_id": str(sb["beat_id"]), "asset_mode": asset_mode,
                "scene_type": str(sb.get("scene_type") or "live_action"), "transition_mode": t_mode,
                "camera_move": cam_move, "kenburns_filter": build_kenburns_filter(cam_move, render_frames, width=width, height=height, fps=fps),
                "arcname": f"frames/beat_{i:02d}.png", "local_path": str(local_src) if local_src is not None else "",
                "raw_dur": round(render_frames / float(fps), 6), "raw_fps": float(fps),
                "base_frames": bf, "overlap_frames": overlap_frames, "render_frames": render_frames, "trim_lead_frame": False,
            })
        else:
            local_src = (clips_dir / f"clip_{i:02d}.mp4") if clips_dir is not None else None
            if local_src is not None and local_src.is_file():
                rp = ffprobe_json(local_src)
                raw_dur = float(rp["format"]["duration"])
                vs = next(s for s in rp["streams"] if s.get("codec_type") == "video")
                raw_fps = _parse_rate(vs.get("r_frame_rate"), default=24.0)
                if render_frames / float(fps) > raw_dur:
                    raise RuntimeError(f"Clip {i} ({sb['beat_id']}) render_frames={render_frames} exceeds raw_dur={raw_dur:.4f}s")
                if trim_lead and (render_frames / float(fps)) > (raw_dur - 1.0 / raw_fps):
                    raise RuntimeError(f"Clip {i} ({sb['beat_id']}) trim_lead exceeds raw_dur - 1 frame")
            else:
                if require_media:
                    raise FileNotFoundError(f"Missing Flow clip: {local_src}")
                raw_dur, raw_fps = float(sb.get("clip_duration_seconds") or 6.0), 24.0
            manifest_items.append({
                "index": i, "beat_id": str(sb["beat_id"]), "asset_mode": asset_mode,
                "scene_type": str(sb.get("scene_type") or "live_action"), "transition_mode": t_mode,
                "camera_move": str(sb.get("camera_move") or "push_in"), "arcname": f"clips/clip_{i:02d}.mp4",
                "local_path": str(local_src) if local_src is not None else "",
                "raw_dur": round(raw_dur, 6), "raw_fps": round(raw_fps, 4),
                "base_frames": bf, "overlap_frames": overlap_frames, "render_frames": render_frames, "trim_lead_frame": trim_lead,
            })

    chunks_plan: list[dict[str, Any]] = []
    cursor = cum_boundary = 0
    for c_idx, c_len in enumerate(chunk_sizes):
        indices = list(range(cursor, cursor + c_len))
        cursor += c_len
        has_poster = c_idx == 0 and int(poster_frames) > 0
        chunk_base = (int(poster_frames) if has_poster else 0) + sum(manifest_items[k]["base_frames"] for k in indices)
        overhang = manifest_items[indices[-1]]["overlap_frames"]
        chk_start_frame = cum_boundary
        cum_boundary += chunk_base
        chunks_plan.append({
            "chunk_index": c_idx,
            "clip_indices": indices,
            "beat_range": f"{manifest_items[indices[0]]['beat_id']}..{manifest_items[indices[-1]]['beat_id']}",
            "has_poster": has_poster,
            "chunk_start_frame": chk_start_frame,
            "chunk_start_sec": round(chk_start_frame / float(fps), 6),
            "chunk_end_sec": round(cum_boundary / float(fps), 6),
            "chunk_base_frames": chunk_base,
            "overhang_frames": overhang,
            "expected_frames": chunk_base + overhang,
            "pass2_xfade_offset_frames": cum_boundary if (render_mode == "two_pass" and c_idx < num_chunks - 1) else None,
        })

    assert sum(chk["chunk_base_frames"] for chk in chunks_plan) == total_frames
    if render_mode == "single_pass":
        assert all(chk["overhang_frames"] == 0 for chk in chunks_plan)
        assert sum(chk["expected_frames"] for chk in chunks_plan) == total_frames
    return manifest_items, chunks_plan, total_frames


REMOTE_SINGLE_PASS_CHUNK_SCRIPT = r"""import json, shutil, subprocess, time
from pathlib import Path

work = Path(__file__).resolve().parent
t0 = time.time()
gpu_out = subprocess.check_output(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True).strip()
if "T4" not in gpu_out:
    raise RuntimeError(f"Tesla T4 GPU required, got: {gpu_out}")

manifest = json.loads((work / "chunk_manifest.json").read_text(encoding="utf-8"))
pref = str(manifest.get("nvenc_preset", "p4"))
nvenc_args = None
for preset in [pref] + [p for p in ("p4", "p5", "p6") if p != pref]:
    args = [
        "-c:v", "h264_nvenc", "-profile:v", "high", "-level:v", "5.1", "-preset", preset,
        "-rc", "vbr", "-cq", "17", "-b:v", "10M", "-maxrate", "16M", "-bufsize", "24M",
        "-g", "30", "-bf", "0", "-pix_fmt", "yuv420p",
    ]
    pr = subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=256x256:d=0.08:r=30", *args, "-f", "null", "-"], capture_output=True, text=True)
    if pr.returncode == 0:
        nvenc_args = args
        break
if nvenc_args is None:
    raise RuntimeError("COLAB_NVENC_UNAVAILABLE")

fonts_dir = work / "fonts"
if fonts_dir.is_dir():
    lf = Path.home() / ".local/share/fonts"
    lf.mkdir(parents=True, exist_ok=True)
    for ttf in fonts_dir.glob("*.ttf"):
        shutil.copy2(ttf, lf / ttf.name)
    subprocess.run(["fc-cache", "-f", str(lf)], check=False, capture_output=True)

w, h, sw, sh, fps = int(manifest["width"]), int(manifest["height"]), int(manifest["scale_w"]), int(manifest["scale_h"]), int(manifest["fps"])
poster_frames, delogo_f, c_idx = int(manifest["poster_frames"]), str(manifest.get("delogo_filter") or "").strip(), int(manifest["chunk_index"])
has_poster, expected_frames, items = bool(manifest.get("has_poster", False)) and poster_frames > 0, int(manifest["expected_frames"]), manifest["items"]
huds = list(manifest.get("local_huds") or [])
has_ass_events = any(ln.strip().startswith("Dialogue:") for ln in (work / "chunk.ass").read_text(encoding="utf-8").splitlines())

cmd = ["ffmpeg", "-y", "-nostats"]
clip_offset = 0
if has_poster:
    cmd.extend(["-loop", "1", "-framerate", str(fps), "-t", f"{poster_frames / fps + 0.2:.4f}", "-i", "poster_9x16.png"])
    clip_offset = 1
for ce in items:
    cmd.extend(["-i", ce["arcname"]])
hud_offset = clip_offset + len(items)
for hud in huds:
    cmd.extend(["-loop", "1", "-framerate", str(fps), "-t", f"{float(hud['hud_dur']):.4f}", "-i", hud["arcname"]])
wm_idx = hud_offset + len(huds)
cmd.extend(["-i", "watermark_150x150.png"])

fc = []
if has_poster:
    fc.append(f"[0:v]scale={w}:{h}:flags=bicubic:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps={fps},settb=1/{fps},trim=end_frame={poster_frames},setpts=PTS-STARTPTS,fps={fps},settb=1/{fps},format=yuv420p[vposter]")

for li, ce in enumerate(items):
    inp_i, rf = clip_offset + li, int(ce["render_frames"])
    if ce.get("asset_mode") == "2k_native_kenburns":
        fc.append(f"[{inp_i}:v]{ce['kenburns_filter']},unsharp=3:3:0.45:3:3:0.25,setpts=N/({fps}*TB),tpad=stop_mode=clone:stop_duration=0.4,fps={fps},settb=1/{fps},trim=end_frame={rf},setpts=PTS-STARTPTS,fps={fps},settb=1/{fps},format=yuv420p[vc{li}]")
    else:
        raw_dur, raw_fps = float(ce["raw_dur"]), float(ce.get("raw_fps") or 24.0)
        tfirst = bool(ce.get("trim_lead_frame", False))
        ptsf = (rf / float(fps)) / max(1.0, raw_dur - (1.0 / raw_fps if tfirst else 0.0))
        dseg, lt = (f"{delogo_f}," if delogo_f else ""), ("trim=start_frame=1,setpts=PTS-STARTPTS," if tfirst else "")
        fc.append(f"[{inp_i}:v]{lt}scale={sw}:{sh}:flags=bicubic,crop={w}:{h}:(in_w-{w})/2:(in_h-{h})/2,setsar=1,{dseg}unsharp=3:3:0.45:3:3:0.25,setpts={ptsf:.8f}*PTS,tpad=stop_mode=clone:stop_duration=0.6,fps={fps},settb=1/{fps},trim=end_frame={rf},setpts=PTS-STARTPTS,fps={fps},settb=1/{fps},format=yuv420p[vc{li}]")

if len(items) == 1:
    fc.append(f"[vc0]setpts=PTS-STARTPTS,fps={fps},settb=1/{fps}[vchunk]")
else:
    prev, cum_int = "[vc0]", 0
    for k in range(len(items) - 1):
        cum_int += int(items[k]["base_frames"])
        ov = int(items[k]["overlap_frames"])
        ol = "[vchunk]" if k == len(items) - 2 else f"[vx{k}]"
        fc.append(f"{prev}[vc{k + 1}]xfade=transition=fade:duration={ov / fps:.6f}:offset={cum_int / fps:.6f}{ol}" if ov > 0 else f"{prev}[vc{k + 1}]concat=n=2:v=1:a=0{ol}")
        prev = ol

base_prefix = "[vposter][vchunk]concat=n=2:v=1:a=0," if has_poster else "[vchunk]"
fc.append(f"{base_prefix}fps={fps},settb=1/{fps},setsar=1,trim=end_frame={expected_frames},setpts=PTS-STARTPTS,format=yuv420p[vbase]")
cur_v = "[vbase]"
for hi, hud in enumerate(huds):
    hs, he, hd, ay = float(hud["hud_start"]), float(hud["hud_end"]), float(hud["hud_dur"]), int(hud.get("anchor_y", 150))
    fc.append(f"[{hud_offset + hi}:v]format=rgba,settb=1/{fps},fade=t=in:st=0:d=0.20:alpha=1,fade=t=out:st={max(0.1, hd - 0.20):.4f}:d=0.20:alpha=1,setpts=PTS-STARTPTS+{hs:.4f}/TB[hud{hi}]")
    nv = f"[vh{hi}]"
    fc.append(f"{cur_v}[hud{hi}]overlay=(W-w)/2:{ay}:eof_action=pass:enable='between(t,{hs:.4f},{he:.4f})'{nv}")
    cur_v = nv

if has_ass_events:
    fc.append(f"{cur_v}ass=filename='chunk.ass':fontsdir='fonts'[vsub]")
    cur_v = "[vsub]"
fc.append(f"{cur_v}[{wm_idx}:v]overlay=W-w-36:H-h-36,format=yuv420p[vchkout]")

chunk_mp4 = work / f"chunk_{c_idx}.mp4"
cmd.extend(["-filter_complex", ";".join(fc), "-map", "[vchkout]", "-an", *nvenc_args, "-r", str(fps), "-video_track_timescale", "30000", str(chunk_mp4)])
res = subprocess.run(cmd, cwd=str(work), capture_output=True, text=True)
if res.returncode != 0:
    raise RuntimeError(f"SINGLE_PASS_CHUNK_{c_idx}_FAILED:\n" + res.stderr[-2500:])

cp = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=nb_frames,duration", "-of", "json", str(chunk_mp4)], text=True))["streams"][0]
got_f = int(cp.get("nb_frames") or round(float(cp["duration"]) * fps))
if got_f != expected_frames:
    raise RuntimeError(f"SINGLE_PASS_CHUNK_{c_idx}_FRAMES: got={got_f} expected={expected_frames}")
print(f"SINGLE_PASS_CHUNK_{c_idx}_SUCCESS frames={got_f} elapsed={time.time() - t0:.2f}s", flush=True)
"""


REMOTE_PASS1_CHUNK_SCRIPT = r"""import json, subprocess, time
from pathlib import Path

work = Path(__file__).resolve().parent
t0 = time.time()
gpu_out = subprocess.check_output(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True).strip()
if "T4" not in gpu_out:
    raise RuntimeError(f"Tesla T4 GPU required, got: {gpu_out}")
manifest = json.loads((work / "chunk_manifest.json").read_text(encoding="utf-8"))
pref = str(manifest.get("nvenc_preset", "p4"))
nvenc_args = None
for preset in [pref] + [p for p in ("p4", "p5", "p6") if p != pref]:
    args = ["-c:v", "h264_nvenc", "-profile:v", "high", "-preset", preset, "-rc", "vbr", "-cq", "14", "-b:v", "22M", "-maxrate", "34M", "-bufsize", "44M", "-g", "30", "-pix_fmt", "yuv420p"]
    if subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=256x256:d=0.08:r=30", *args, "-f", "null", "-"], capture_output=True).returncode == 0:
        nvenc_args = args
        break
if nvenc_args is None:
    raise RuntimeError("COLAB_NVENC_UNAVAILABLE")

w, h, sw, sh, fps = int(manifest["width"]), int(manifest["height"]), int(manifest["scale_w"]), int(manifest["scale_h"]), int(manifest["fps"])
poster_frames, delogo_f, c_idx = int(manifest["poster_frames"]), str(manifest.get("delogo_filter") or "").strip(), int(manifest["chunk_index"])
has_poster, expected_frames, items = bool(manifest.get("has_poster", False)) and poster_frames > 0, int(manifest["expected_frames"]), manifest["items"]

cmd = ["ffmpeg", "-y", "-nostats"]
clip_offset = 0
if has_poster:
    cmd.extend(["-loop", "1", "-framerate", str(fps), "-t", f"{poster_frames / fps + 0.2:.4f}", "-i", "poster_9x16.png"])
    clip_offset = 1
for ce in items:
    cmd.extend(["-i", ce["arcname"]])

fc = []
if has_poster:
    fc.append(f"[0:v]scale={w}:{h}:flags=bicubic:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps={fps},settb=1/{fps},trim=end_frame={poster_frames},setpts=PTS-STARTPTS,fps={fps},settb=1/{fps},format=yuv420p[vposter]")
for li, ce in enumerate(items):
    inp_i, rf = clip_offset + li, int(ce["render_frames"])
    if ce.get("asset_mode") == "2k_native_kenburns":
        fc.append(f"[{inp_i}:v]{ce['kenburns_filter']},unsharp=3:3:0.45:3:3:0.25,setpts=N/({fps}*TB),tpad=stop_mode=clone:stop_duration=0.4,fps={fps},settb=1/{fps},trim=end_frame={rf},setpts=PTS-STARTPTS,fps={fps},settb=1/{fps},format=yuv420p[vc{li}]")
    else:
        raw_dur, raw_fps = float(ce["raw_dur"]), float(ce.get("raw_fps") or 24.0)
        tfirst = bool(ce.get("trim_lead_frame", False))
        ptsf = (rf / float(fps)) / max(1.0, raw_dur - (1.0 / raw_fps if tfirst else 0.0))
        dseg, lt = (f"{delogo_f}," if delogo_f else ""), ("trim=start_frame=1,setpts=PTS-STARTPTS," if tfirst else "")
        fc.append(f"[{inp_i}:v]{lt}scale={sw}:{sh}:flags=bicubic,crop={w}:{h}:(in_w-{w})/2:(in_h-{h})/2,setsar=1,{dseg}unsharp=3:3:0.45:3:3:0.25,setpts={ptsf:.8f}*PTS,tpad=stop_mode=clone:stop_duration=0.6,fps={fps},settb=1/{fps},trim=end_frame={rf},setpts=PTS-STARTPTS,fps={fps},settb=1/{fps},format=yuv420p[vc{li}]")
if len(items) == 1:
    fc.append(f"[vc0]setpts=PTS-STARTPTS,fps={fps},settb=1/{fps}[vchunk_clips]")
else:
    prev, cum_int = "[vc0]", 0
    for k in range(len(items) - 1):
        cum_int += int(items[k]["base_frames"])
        ov = int(items[k]["overlap_frames"])
        ol = "[vchunk_clips]" if k == len(items) - 2 else f"[vx{k}]"
        fc.append(f"{prev}[vc{k + 1}]xfade=transition=fade:duration={ov / fps:.6f}:offset={cum_int / fps:.6f}{ol}" if ov > 0 else f"{prev}[vc{k + 1}]concat=n=2:v=1:a=0{ol}")
        prev = ol
fc.append((f"[vposter][vchunk_clips]concat=n=2:v=1:a=0," if has_poster else "[vchunk_clips]") + f"fps={fps},settb=1/{fps},setsar=1,trim=end_frame={expected_frames},setpts=PTS-STARTPTS,format=yuv420p[vchkout]")
chunk_mp4 = work / f"chunk_{c_idx}.mp4"
cmd.extend(["-filter_complex", ";".join(fc), "-map", "[vchkout]", "-an", *nvenc_args, "-r", str(fps), str(chunk_mp4)])
res = subprocess.run(cmd, cwd=str(work), capture_output=True, text=True)
if res.returncode != 0:
    raise RuntimeError(f"CHUNK_{c_idx}_NVENC_FAILED:\n" + res.stderr[-2500:])
print(f"PASS1_CHUNK_{c_idx}_SUCCESS elapsed={time.time() - t0:.2f}s", flush=True)
"""


REMOTE_PASS2_SCRIPT = r"""import json, shutil, subprocess, time
from pathlib import Path

work = Path(__file__).resolve().parent
t0 = time.time()
gpu_out = subprocess.check_output(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True).strip()
if "T4" not in gpu_out:
    raise RuntimeError(f"Tesla T4 GPU required, got: {gpu_out}")
manifest = json.loads((work / "manifest.json").read_text(encoding="utf-8"))
pref = str(manifest.get("nvenc_preset", "p4"))
nvenc_args = None
for preset in [pref] + [p for p in ("p4", "p5", "p6") if p != pref]:
    args = ["-c:v", "h264_nvenc", "-profile:v", "high", "-preset", preset, "-rc", "vbr", "-cq", "14", "-b:v", "22M", "-maxrate", "34M", "-bufsize", "44M", "-g", "30", "-pix_fmt", "yuv420p"]
    if subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=256x256:d=0.08:r=30", *args, "-f", "null", "-"], capture_output=True).returncode == 0:
        nvenc_args = args
        break
if nvenc_args is None:
    raise RuntimeError("COLAB_NVENC_UNAVAILABLE")

fonts_dir = work / "fonts"
if fonts_dir.is_dir():
    lf = Path.home() / ".local/share/fonts"
    lf.mkdir(parents=True, exist_ok=True)
    for ttf in fonts_dir.glob("*.ttf"):
        shutil.copy2(ttf, lf / ttf.name)
    subprocess.run(["fc-cache", "-f", str(lf)], check=False, capture_output=True)

fps, total_frames, chunks, hud_stamps = int(manifest["fps"]), int(manifest["total_frames"]), manifest["chunks"], manifest["hud_stamps"]
cmd = ["ffmpeg", "-y", "-nostats"]
for chk in chunks:
    cmd.extend(["-i", f"chunk_{int(chk['chunk_index'])}.mp4"])
hud_offset = len(chunks)
for h_ent in hud_stamps:
    cmd.extend(["-loop", "1", "-framerate", str(fps), "-t", f"{float(h_ent['hud_dur']):.4f}", "-i", h_ent["arcname"]])
wm_idx = hud_offset + len(hud_stamps)
cmd.extend(["-i", "watermark_150x150.png", "-i", "narration.m4a"])
audio_idx = wm_idx + 1

fc = [f"[{c}:v]fps={fps},settb=1/{fps},trim=end_frame={int(chk['expected_frames'])},setpts=PTS-STARTPTS,fps={fps},settb=1/{fps},setsar=1,format=yuv420p[chk{c}]" for c, chk in enumerate(chunks)]
if len(chunks) == 1:
    fc.append(f"[chk0]trim=end_frame={total_frames},setpts=PTS-STARTPTS[vconcat]")
else:
    prev, cum_base = "[chk0]", 0
    for c in range(len(chunks) - 1):
        cum_base += int(chunks[c]["chunk_base_frames"])
        ov = int(chunks[c]["overhang_frames"])
        ol = "[vchunks]" if c == len(chunks) - 2 else f"[vcx{c}]"
        fc.append(f"{prev}[chk{c + 1}]xfade=transition=fade:duration={ov / fps:.6f}:offset={cum_base / fps:.6f}{ol}" if ov > 0 else f"{prev}[chk{c + 1}]concat=n=2:v=1:a=0{ol}")
        prev = ol
    fc.append(f"[vchunks]trim=end_frame={total_frames},setpts=PTS-STARTPTS[vconcat]")

cur_v = "[vconcat]"
for hi, h_ent in enumerate(hud_stamps):
    hs, he, hd, ay = float(h_ent["hud_start"]), float(h_ent["hud_end"]), float(h_ent["hud_dur"]), int(h_ent.get("anchor_y", 150))
    fc.append(f"[{hud_offset + hi}:v]format=rgba,settb=1/{fps},fade=t=in:st=0:d=0.25:alpha=1,fade=t=out:st={max(0.1, hd - 0.25):.4f}:d=0.25:alpha=1,setpts=PTS-STARTPTS+{hs:.4f}/TB[hud{hi}]")
    nv = f"[vh{hi}]"
    fc.append(f"{cur_v}[hud{hi}]overlay=(W-w)/2:{ay}:eof_action=pass:enable='between(t,{hs:.4f},{he:.4f})'{nv}")
    cur_v = nv
fc.append(f"{cur_v}ass=filename='subtitles_kinetic_2k.ass':fontsdir='fonts'[vsub]")
fc.append(f"[vsub][{wm_idx}:v]overlay=W-w-36:H-h-36,format=yuv420p[vout]")

out_mp4 = work / "final_short_2k.mp4"
cmd.extend(["-filter_complex", ";".join(fc), "-map", "[vout]", "-map", f"{audio_idx}:a", *nvenc_args, "-r", str(fps), "-c:a", "copy", "-movflags", "+faststart", str(out_mp4)])
res = subprocess.run(cmd, cwd=str(work), capture_output=True, text=True)
if res.returncode != 0:
    raise RuntimeError("PASS2_NVENC_FAILED:\n" + res.stderr[-2500:])
print(f"PASS2_COMPLETE_SUCCESS elapsed={time.time() - t0:.2f}s", flush=True)
"""


def encode_calibrated_m4a(wav_path: Path, out_m4a: Path, target_lufs: float = -11.0, max_tp_db: float = -1.0) -> dict[str, float]:
    out_m4a.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", str(wav_path), "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2", str(out_m4a)], check=True, capture_output=True)
    stats = measure_ebur128(out_m4a)
    if abs(stats["integrated_lufs"] - target_lufs) <= 0.25 and stats["true_peak_dbtp"] <= max_tp_db:
        return stats

    with wave.open(str(wav_path), "rb") as wf:
        sr, nch, _, nf = wf.getframerate(), wf.getnchannels(), wf.getsampwidth(), wf.getnframes()
        raw = np.frombuffer(wf.readframes(nf), dtype=np.int16).astype(np.float32).reshape(-1, nch) / 32768.0
    if nch == 1:
        raw = np.column_stack([raw[:, 0], raw[:, 0]])

    win = 128
    kern = np.hanning(win * 2 + 1)
    kern /= kern.sum()
    for pre_gain, thr in ((1.05, 0.81), (1.05, 0.79), (1.03, 0.81), (1.03, 0.79), (1.07, 0.79), (1.00, 0.82)):
        boosted = raw * pre_gain
        env = maximum_filter1d(np.max(np.abs(boosted), axis=1), size=win * 2)
        smooth_gain = np.minimum(1.0, np.convolve(1.0 / np.maximum(env / thr, 1.0), kern, mode="same"))
        pcm = np.clip(np.round(np.clip(boosted * smooth_gain[:, None], -0.99, 0.99) * 32767.0), -32768, 32767).astype(np.int16)
        with tempfile.TemporaryDirectory() as td:
            tw = Path(td) / "pre_aac.wav"
            with wave.open(str(tw), "wb") as ow:
                ow.setnchannels(2)
                ow.setsampwidth(2)
                ow.setframerate(sr)
                ow.writeframes(pcm.tobytes())
            subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", str(tw), "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2", str(out_m4a)], check=True, capture_output=True)
            stats = measure_ebur128(out_m4a)
            if stats["true_peak_dbtp"] <= max_tp_db and abs(stats["integrated_lufs"] - target_lufs) <= 0.30:
                return stats
    raise RuntimeError(f"Failed to calibrate narration.m4a: {stats}")


def _dispatch_chunks_parallel(
    *,
    job_id: str,
    manifest_items: list[dict[str, Any]],
    chunks_plan: list[dict[str, Any]],
    poster_png: Path,
    delogo_filter: str,
    nvenc_preset: str,
    out_dir: Path,
    colab_render_workers: int,
    single_pass: bool,
    hud_entries: list[dict[str, Any]] | None = None,
    ass_path: Path | None = None,
    fonts_dir: Path | None = None,
    watermark_png: Path | None = None,
) -> tuple[list[Path], float]:
    t0 = time.monotonic()
    out_dir.mkdir(parents=True, exist_ok=True)
    session_name = f"vp-r1-{job_id[:16]}"
    idle_accounts = select_idle_colab_accounts(session_name, max_accounts=max(4, colab_render_workers + 2), min_seconds=360.0)
    if not idle_accounts:
        raise RuntimeError("No idle budget-verified Colab T4 accounts available for render")

    concurrency = max(1, min(colab_render_workers, len(idle_accounts), len(chunks_plan)))
    logger.info("[Colab Render single_pass=%s] Dispatching %d chunks across %d/%d T4 worker(s): %s", single_pass, len(chunks_plan), concurrency, len(idle_accounts), idle_accounts)

    pm = ColabPoolManager(accounts_config=[{"id": acc, "role": "render", "session": session_name} for acc in idle_accounts], session_name=session_name)
    dispatcher = ColabPoolDispatcher(pm, max_retries_per_task=4)
    cfg_base = json.loads((SYS_DIR / "config.json").read_text(encoding="utf-8"))
    guard_lock = threading.Lock()
    unconfirmed_streak = 0
    started_accounts: set[str] = set()

    def _run_chunk(worker: Any, task: dict[str, Any]) -> Path:
        nonlocal unconfirmed_streak
        with guard_lock:
            if unconfirmed_streak >= 2:
                raise RuntimeError("ABORT_FAILOVER: 2 consecutive COLAB_EXEC_UNCONFIRMED failures")
            started_accounts.add(worker.account_id)

        chk = task["chunk"]
        c_idx = int(chk["chunk_index"])
        c_items = [manifest_items[i] for i in chk["clip_indices"]]
        tmp_dir = Path(tempfile.mkdtemp(prefix=f"vp_sp_chk{c_idx}_"))
        client: Client | None = None
        try:
            local_huds: list[dict[str, Any]] = []
            chk_s, chk_e = float(chk["chunk_start_sec"]), float(chk["chunk_end_sec"])
            chk_dur = max(0.2, chk_e - chk_s)
            if single_pass and hud_entries:
                for h_ent in hud_entries:
                    hs, he = float(h_ent["hud_start"]), float(h_ent["hud_end"])
                    if min(he, chk_e) <= max(hs, chk_s) + 0.05:
                        continue
                    ls, le = max(0.0, hs - chk_s), min(chk_dur, he - chk_s)
                    if le > ls + 0.05:
                        local_huds.append({**h_ent, "hud_start": round(ls, 6), "hud_end": round(le, 6), "hud_dur": round(le - ls, 6)})

            chunk_manifest = {
                "job_id": job_id, "chunk_index": c_idx, "width": WIDTH, "height": HEIGHT,
                "scale_w": SCALE_W, "scale_h": SCALE_H, "fps": FPS, "poster_frames": POSTER_FRAMES,
                "has_poster": chk["has_poster"], "expected_frames": chk["expected_frames"],
                "delogo_filter": delogo_filter, "nvenc_preset": nvenc_preset,
                "items": c_items, "local_huds": local_huds,
            }
            bundle_zip = tmp_dir / f"chunk_{c_idx}_bundle.zip"
            with zipfile.ZipFile(bundle_zip, "w", compression=zipfile.ZIP_STORED) as zf:
                zf.writestr("chunk_manifest.json", json.dumps(chunk_manifest, ensure_ascii=False, indent=2))
                zf.writestr("run_chunk.py", REMOTE_SINGLE_PASS_CHUNK_SCRIPT if single_pass else REMOTE_PASS1_CHUNK_SCRIPT)
                if chk["has_poster"]:
                    zf.write(poster_png, "poster_9x16.png")
                for ce in c_items:
                    zf.write(Path(ce["local_path"]), ce["arcname"])
                if single_pass:
                    assert ass_path is not None and watermark_png is not None
                    chk_ass = tmp_dir / "chunk.ass"
                    slice_ass_for_window(ass_path, chk_s, chk_e, chk_ass)
                    zf.write(chk_ass, "chunk.ass")
                    zf.write(watermark_png, "watermark_150x150.png")
                    if fonts_dir and fonts_dir.is_dir():
                        for ttf in fonts_dir.glob("*.ttf"):
                            zf.write(ttf, f"fonts/{ttf.name}")
                    for hud in local_huds:
                        zf.write(Path(hud["local_path"]), hud["arcname"])

            cfg = copy.deepcopy(cfg_base)
            cfg.setdefault("colab_tts", {}).update({"account": worker.account_id, "session": worker.session_name, "_session_explicit": True, "job_id": job_id})
            client = Client(SYS_DIR, cfg)
            client.account, client.session, client._runtime_role = worker.account_id, worker.session_name, "render"
            client.ensure_authenticated()
            client.start()

            rw = f"/content/vp_r_c{c_idx}"
            client.exec(f"import shutil, pathlib; shutil.rmtree({rw!r}, ignore_errors=True); pathlib.Path({rw!r}).mkdir(parents=True, exist_ok=True)", timeout=90)
            with guard_lock:
                unconfirmed_streak = 0

            client.call("upload", "-s", client.session, str(bundle_zip.resolve()), f"{rw}/bundle.zip", timeout=300)
            client.exec(
                f"import pathlib, zipfile, subprocess, sys\nzp = pathlib.Path({rw + '/bundle.zip'!r})\n"
                f"with zipfile.ZipFile(zp, 'r') as zf: zf.extractall({rw!r})\nzp.unlink(missing_ok=True)\n"
                f"p = subprocess.run([sys.executable, {rw + '/run_chunk.py'!r}], cwd={rw!r}, capture_output=True, text=True)\n"
                f"print(p.stdout)\nif p.returncode != 0: raise RuntimeError(p.stderr[-1500:] + p.stdout[-1500:])\n",
                timeout=900,
            )
            local_chunk = out_dir / f"chunk_{c_idx}.mp4"
            tmp_dl = local_chunk.with_suffix(".mp4.tmp")
            client.call("download", "-s", client.session, f"{rw}/chunk_{c_idx}.mp4", str(tmp_dl.resolve()), timeout=300)
            tmp_dl.replace(local_chunk)
            return local_chunk
        except Exception as exc:
            if "COLAB_EXEC_UNCONFIRMED" in str(exc):
                with guard_lock:
                    unconfirmed_streak += 1
            raise
        finally:
            if client is not None:
                try:
                    client.stop()
                except Exception:
                    pass
            shutil.rmtree(tmp_dir, ignore_errors=True)

    try:
        chunk_paths = dispatcher.dispatch_all([{"id": f"chunk_{chk['chunk_index']}", "chunk": chk} for chk in chunks_plan], _run_chunk, max_concurrency=concurrency, role="render")
    finally:
        if started_accounts:
            pm.stop_pool(sorted(started_accounts), unassign_server=True)
    return chunk_paths, round(time.monotonic() - t0, 2)


def _run_pass2_composite(
    *,
    job_id: str,
    chunk_paths: list[Path],
    chunks_plan: list[dict[str, Any]],
    hud_entries: list[dict[str, Any]],
    total_frames: int,
    nvenc_preset: str,
    ass_path: Path,
    fonts_dir: Path,
    watermark_png: Path,
    narration_m4a: Path,
    out_mp4: Path,
) -> tuple[str, float]:
    t0 = time.monotonic()
    candidates = select_idle_colab_accounts(f"vp-r2-{job_id[:16]}", max_accounts=4, min_seconds=360.0)
    if not candidates:
        raise RuntimeError("No idle budget-verified Colab T4 accounts available for Pass 2")
    cfg_base, pm = json.loads((SYS_DIR / "config.json").read_text(encoding="utf-8")), ColabPoolManager()
    unconfirmed, last_exc = 0, None

    with tempfile.TemporaryDirectory(prefix="vp_pass2_") as td:
        bundle_zip = Path(td) / "pass2_bundle.zip"
        with zipfile.ZipFile(bundle_zip, "w", compression=zipfile.ZIP_STORED) as zf:
            zf.writestr("manifest.json", json.dumps({"job_id": job_id, "fps": FPS, "total_frames": total_frames, "nvenc_preset": nvenc_preset, "chunks": chunks_plan, "hud_stamps": hud_entries}, ensure_ascii=False, indent=2))
            zf.writestr("run_pass2.py", REMOTE_PASS2_SCRIPT)
            for cp in chunk_paths:
                zf.write(cp, cp.name)
            for h_ent in hud_entries:
                zf.write(Path(h_ent["local_path"]), h_ent["arcname"])
            if fonts_dir.is_dir():
                for ttf in fonts_dir.glob("*.ttf"):
                    zf.write(ttf, f"fonts/{ttf.name}")
            zf.write(ass_path, "subtitles_kinetic_2k.ass")
            zf.write(watermark_png, "watermark_150x150.png")
            zf.write(narration_m4a, "narration.m4a")

        for acc in candidates:
            client, started, sess = None, False, f"vp-p2-{int(time.time())}"
            try:
                cfg = copy.deepcopy(cfg_base)
                cfg.setdefault("colab_tts", {}).update({"account": acc, "session": sess, "_session_explicit": True, "job_id": job_id})
                client = Client(SYS_DIR, cfg)
                client.account, client.session, client._runtime_role = acc, sess, "render"
                client.ensure_authenticated()
                client.start()
                started, unconfirmed, rw = True, 0, "/content/vp_short_p2"
                client.exec(f"import shutil, pathlib; shutil.rmtree({rw!r}, ignore_errors=True); pathlib.Path({rw!r}).mkdir(parents=True, exist_ok=True)", timeout=90)
                client.call("upload", "-s", sess, str(bundle_zip.resolve()), f"{rw}/bundle.zip", timeout=300)
                out_log = client.exec(f"import pathlib, zipfile, subprocess, sys\nzp = pathlib.Path({rw + '/bundle.zip'!r})\nwith zipfile.ZipFile(zp, 'r') as zf: zf.extractall({rw!r})\nzp.unlink(missing_ok=True)\np = subprocess.run([sys.executable, {rw + '/run_pass2.py'!r}], cwd={rw!r}, capture_output=True, text=True)\nprint(p.stdout)\nif p.returncode != 0: raise RuntimeError(p.stderr[-2000:] + p.stdout[-2000:])\n", timeout=1200)
                if "PASS2_COMPLETE_SUCCESS" not in out_log:
                    raise RuntimeError(f"Pass 2 missing marker:\n{text_tail(out_log, 1000)}")
                out_mp4.parent.mkdir(parents=True, exist_ok=True)
                tmp_dl = out_mp4.with_suffix(".mp4.tmp")
                client.call("download", "-s", sess, f"{rw}/final_short_2k.mp4", str(tmp_dl.resolve()), timeout=300)
                tmp_dl.replace(out_mp4)
                return acc, round(time.monotonic() - t0, 2)
            except Exception as exc:
                last_exc = exc
                unconfirmed = (unconfirmed + 1) if "COLAB_EXEC_UNCONFIRMED" in str(exc) else 0
                if unconfirmed >= 2:
                    raise RuntimeError(f"Aborted Pass 2 after 2 consecutive COLAB_EXEC_UNCONFIRMED: {exc}") from exc
                logger.warning("[Pass 2] %s failed (%s); failing over...", acc, exc)
            finally:
                if client is not None and started:
                    try:
                        client.stop()
                    except Exception:
                        pass
                    pm.stop_pool([acc], unassign_server=True)
    raise RuntimeError(f"All Colab accounts failed Pass 2: {last_exc}")


def _resolve_ass_and_fonts(spec_dir: Path, work_root: Path) -> tuple[Path, Path]:
    cands = [work_root / "subtitles_kinetic_2k.ass", spec_dir / "_work_short" / "subtitles_kinetic_2k.ass"]
    ass_src = next((p for p in cands if p.is_file()), None)
    if ass_src is None:
        raise FileNotFoundError(f"Missing subtitles_kinetic_2k.ass in {cands}")
    fonts_dir = work_root / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    for cand in (spec_dir / "_work_short" / "fonts", SYS_DIR / "assets" / "fonts" / "chanh_niem_ke", Path("/usr/share/fonts/truetype/noto")):
        if cand.is_dir():
            for ttf in cand.glob("*.ttf"):
                if ("NotoSans" in ttf.name or "DejaVu" in ttf.name) and not (fonts_dir / ttf.name).is_file():
                    shutil.copy2(ttf, fonts_dir / ttf.name)
    return ass_src, fonts_dir


def _local_lossless_concat_mux(chunk_paths: list[Path], narration_m4a: Path, out_mp4: Path, work_dir: Path) -> float:
    t0 = time.monotonic()
    concat_txt = work_dir / "chunks.txt"
    concat_txt.write_text("\n".join(f"file '{cp.resolve().as_posix()}'" for cp in chunk_paths) + "\n", encoding="utf-8")
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    tmp_mp4 = out_mp4.with_suffix(".concat.tmp.mp4")
    subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt),
            "-i", str(narration_m4a), "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", "copy", "-shortest", "-movflags", "+faststart", str(tmp_mp4),
        ],
        check=True,
        capture_output=True,
    )
    tmp_mp4.replace(out_mp4)
    return round(time.monotonic() - t0, 2)


def run_render_stage(
    short_spec: dict[str, Any],
    spec_dir: Path,
    work_root: Path,
    *,
    visual_mode: str = "hybrid_2k",
    render_mode: str = "single_pass",
    colab_render_workers: int = 4,
    nvenc_preset: str = "p4",
    delogo: str = "on",
    prep_only: bool = False,
    out_mp4: Path,
    out_overridden: bool,
    stage_timings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute Distributed 4-GPU Colab T4 Render (`single_pass` + `<2s` lossless concat or `two_pass`)."""
    t0 = time.monotonic()
    job_id, channel_id = str(short_spec["job_id"]), str(short_spec["channel_id"])
    timings = json.loads((spec_dir / "audio_timings.json").read_text(encoding="utf-8"))

    render_work = work_root / "render_2k"
    hud_entries = build_hud_stamps(short_spec, timings, hud_out_dir=render_work / "hud_stamps", preview_path=render_work / "hud_stamps_preview.png", width=WIDTH, height=HEIGHT)
    manifest_items, chunks_plan, total_frames = plan_chunked_render_timeline(
        short_spec, timings, visual_mode=visual_mode, render_mode=render_mode,
        clips_dir=spec_dir / "clips", frames_dir=spec_dir / "frames",
        fps=FPS, poster_frames=POSTER_FRAMES, width=WIDTH, height=HEIGHT, require_media=(not prep_only),
    )

    flow_count = sum(1 for m in manifest_items if m["asset_mode"] == "flow_video")
    kb_count = sum(1 for m in manifest_items if m["asset_mode"] == "2k_native_kenburns")
    delogo_filter = _compute_bottom_right_delogo_filter(WIDTH, HEIGHT) if delogo == "on" else ""

    if prep_only:
        render_work.mkdir(parents=True, exist_ok=True)
        prep = {
            "prep_only": True, "job_id": job_id, "visual_mode": visual_mode, "render_mode": render_mode,
            "total_beats": len(manifest_items), "flow_video_beats": flow_count, "kenburns_2k_beats": kb_count,
            "total_duration_sec": float(timings["total_duration_sec"]), "total_frames": total_frames,
            "poster_frames": POSTER_FRAMES, "sum_base_frames": sum(m["base_frames"] for m in manifest_items),
            "hud_stamps_count": len(hud_entries), "hud_stamps_preview": str(render_work / "hud_stamps_preview.png"),
            "chunks": [{"chunk_index": c["chunk_index"], "beat_range": c["beat_range"], "items": len(c["clip_indices"]), "chunk_base_frames": c["chunk_base_frames"], "overhang_frames": c["overhang_frames"], "expected_frames": c["expected_frames"]} for c in chunks_plan],
            "elapsed_sec": round(time.monotonic() - t0, 2),
        }
        (render_work / "prep_manifest.json").write_text(json.dumps(prep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return prep

    audio_wav, poster_png = spec_dir / "narration_master.wav", spec_dir / "thumbnail_9x16.png"
    ass_src, fonts_dir = _resolve_ass_and_fonts(spec_dir, work_root)
    for req_p in (audio_wav, poster_png, ass_src):
        if not req_p.is_file():
            raise FileNotFoundError(f"Missing required pre-render file: {req_p}")

    wm_src = SYS_DIR / "channels" / channel_id / "assets" / "watermark_150x150.png"
    wm_dst = render_work / "watermark_150x150.png"
    make_rounded_watermark(wm_src, wm_dst, size=150, opacity=0.92, radius=24)

    narration_m4a = render_work / "narration.m4a"
    a_stats = encode_calibrated_m4a(audio_wav, narration_m4a)
    if abs(a_stats["integrated_lufs"] - (-11.0)) > 0.30 or a_stats["true_peak_dbtp"] > -1.0:
        raise RuntimeError(f"narration.m4a failed pre-upload ebur128 gate: {a_stats}")

    chunk_paths, pass1_sec = _dispatch_chunks_parallel(
        job_id=job_id, manifest_items=manifest_items, chunks_plan=chunks_plan,
        poster_png=poster_png, delogo_filter=delogo_filter, nvenc_preset=nvenc_preset,
        out_dir=render_work / "chunks", colab_render_workers=colab_render_workers,
        single_pass=(render_mode == "single_pass"), hud_entries=hud_entries,
        ass_path=ass_src, fonts_dir=fonts_dir, watermark_png=wm_dst,
    )

    if render_mode == "single_pass":
        pass2_sec = _local_lossless_concat_mux(chunk_paths, narration_m4a, out_mp4, render_work)
        pass2_acc = "local_lossless_concat"
    else:
        pass2_acc, pass2_sec = _run_pass2_composite(
            job_id=job_id, chunk_paths=chunk_paths, chunks_plan=chunks_plan, hud_entries=hud_entries,
            total_frames=total_frames, nvenc_preset=nvenc_preset, ass_path=ass_src, fonts_dir=fonts_dir,
            watermark_png=wm_dst, narration_m4a=narration_m4a, out_mp4=out_mp4,
        )

    probe, ebur = ffprobe_json(out_mp4), measure_ebur128(out_mp4)
    v_s = next(s for s in probe["streams"] if s["codec_type"] == "video")
    a_s = next(s for s in probe["streams"] if s["codec_type"] == "audio")
    mp4_dur, wav_dur = float(probe["format"]["duration"]), float(timings["total_duration_sec"])
    got_nb_frames = int(v_s.get("nb_frames") or round(mp4_dur * FPS))

    assert int(v_s["width"]) == WIDTH and int(v_s["height"]) == HEIGHT
    assert v_s["codec_name"] == "h264" and a_s["codec_name"] == "aac" and int(a_s["sample_rate"]) == 48000
    assert abs(mp4_dur - wav_dur) <= 0.20, f"A/V duration mismatch: mp4={mp4_dur:.3f}s wav={wav_dur:.3f}s"
    assert abs(got_nb_frames - total_frames) <= 2, f"MP4 frame count mismatch: got={got_nb_frames} expected={total_frames}"
    assert abs(ebur["integrated_lufs"] - (-11.0)) <= 0.35 and ebur["true_peak_dbtp"] <= -1.0, f"Bad ebur128: {ebur}"

    verify_frames: list[str] = []
    tb_list = timings["beats"]
    sample_indices = sorted({0, min(5, len(tb_list) - 1), min(13, len(tb_list) - 1), len(tb_list) - 1})
    for c_i, b_idx in enumerate(sample_indices):
        tb = tb_list[b_idx]
        ts = 0.5 * (float(tb["start_sec"]) + float(tb["end_sec"]))
        fp = out_mp4.parent / f"verify_chunk{c_i}_{tb['beat_id']}.png"
        subprocess.run(["ffmpeg", "-y", "-ss", f"{ts:.3f}", "-i", str(out_mp4), "-frames:v", "1", str(fp)], check=True, capture_output=True)
        verify_frames.append(str(fp))

    if not out_overridden:
        shutil.copy2(out_mp4, spec_dir / f"{job_id}.mp4")

    rec = {
        "job_id": job_id, "visual_mode": visual_mode, "render_mode": render_mode,
        "nvenc_preset": nvenc_preset, "delogo": delogo, "out_mp4": str(out_mp4),
        "total_beats": len(manifest_items), "flow_video_beats": flow_count, "kenburns_2k_beats": kb_count,
        "render_chunks": len(chunks_plan), "colab_render_workers_requested": colab_render_workers,
        "pass1_sec": pass1_sec, "pass2_sec": pass2_sec, "pass2_account": pass2_acc,
        "render_total_sec": round(time.monotonic() - t0, 2), "stage_timings": stage_timings or {},
        "duration_sec": mp4_dur, "total_frames": got_nb_frames, "size_bytes": out_mp4.stat().st_size,
        "ebur128": ebur, "verify_frames": verify_frames, "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    (out_mp4.parent / "benchmark_timings.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return rec
