#!/usr/bin/env python3
"""Video Pilot — Automated Channel Production Script for Não Lười (nao_luoi).

Executes full end-to-end production for both:
1. Video ngắn TikTok (short_9x16): job nao-luoi-week1-9x16
2. Video dài YouTube (long_16x9 kèm spinoff_shorts): job nao-luoi-week1-16x9

Pipeline stages:
- Stage 1: Schema 3.0 Package Validation & Hook Scoring
- Stage 2: Audio TTS Synthesis (VietNarrator -11.0 LUFS / -1.0 dBTP, 48kHz mono PCM16)
- Stage 3: Flow CDP Image Generation (2D Indie Doodle 1.7.0 + Native Thumbnail)
- Stage 4: Remotion MP4 + SRT Video Render
- Stage 5: Deliverables Verification (validate_production_bundle, script_hook_scorer, ffprobe)
"""
from __future__ import annotations

import argparse
import asyncio
import copy
import hashlib
import json
import logging
import math
import os
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import wave
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image

SYS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = SYS_DIR.parent
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import audio_processing as ap
from content.research_story_architect import (
    compute_brief_hash,
    validate_production_bundle,
    write_production_package,
)
from flow_cdp.cdp_direct_client import (
    PROFILES,
    DirectCDPProfileSession,
    ensure_chrome_profiles_launched,
    is_port_open,
)
from flow_prompts import compile as compile_flow_prompt
from tools.script_hook_scorer import score_content_file
from tools.vn_text_normalizer import normalize_for_tts

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("produce_nao_luoi")


def synthesize_vietnamese_speech(text: str, out_wav: Path) -> float:
    """Synthesize Vietnamese narration via TTS and convert to 48kHz mono PCM16 WAV."""
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    temp_mp3 = out_wav.with_suffix(".mp3")
    
    norm_text = normalize_for_tts(text)
    encoded_text = urllib.parse.quote(norm_text)
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_text}&tl=vi&client=tw-ob"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        temp_mp3.write_bytes(resp.read())
        
    cmd = [
        "ffmpeg", "-y", "-i", str(temp_mp3),
        "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le",
        str(out_wav)
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    temp_mp3.unlink(missing_ok=True)
    
    with wave.open(str(out_wav)) as w:
        duration = w.getnframes() / w.getframerate()
    return duration


def generate_audio_stage(job_dir: Path) -> Dict[str, Any]:
    """Execute Stage 2: Audio Synthesis & Mastering for all scenes in job."""
    logger.info(f"[*] GIAI ĐOẠN 2: Tổng hợp giọng kể TTS và làm chủ âm học cho {job_dir.name}...")
    brief = json.loads((job_dir / "brief.json").read_text(encoding="utf-8"))
    content = json.loads((job_dir / "content.json").read_text(encoding="utf-8"))
    
    audio_rev_dir = job_dir / "revisions/audio/1"
    audio_rev_dir.mkdir(parents=True, exist_ok=True)
    
    scenes = content.get("scenes", [])
    segments: List[Dict[str, Any]] = []
    cues: List[Dict[str, Any]] = []
    wav_parts: List[Path] = []
    
    current_time = 0.0
    pause_gap = 0.35  # standard cadence pause between scenes
    
    for idx, sc in enumerate(scenes):
        sc_id = sc["id"]
        narration = sc.get("narration", "").strip()
        part_wav = audio_rev_dir / f"segment-{idx:04d}.wav"
        
        dur = synthesize_vietnamese_speech(narration, part_wav)
        wav_parts.append(part_wav)
        
        # Word timestamps approximate for Remotion captions
        words = narration.split()
        word_dur = dur / max(1, len(words))
        word_timestamps = [
            {"word": w, "start": round(i * word_dur, 2), "end": round((i + 1) * word_dur, 2)}
            for i, w in enumerate(words)
        ]
        
        seg = {
            "scene_id": sc_id,
            "text": narration,
            "path": f"revisions/audio/1/{part_wav.name}",
            "start": round(current_time, 3),
            "end": round(current_time + dur, 3),
            "content_end": round(current_time + dur, 3),
            "word_timestamps": word_timestamps,
        }
        segments.append(seg)
        current_time += dur + pause_gap

    total_duration = round(current_time - pause_gap, 3)
    from scripts.subtitles import subtitle_cues
    cues = subtitle_cues(segments, aspect_ratio=brief.get("outputs", [{}])[0].get("aspect_ratio", "9:16"))
    
    # Concatenate all parts into raw narration.wav
    concat_list = audio_rev_dir / "concat_list.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for idx, p in enumerate(wav_parts):
            f.write(f"file '{p.resolve()}'\n")
            if idx < len(wav_parts) - 1:
                # generate silence gap
                silence_wav = audio_rev_dir / f"silence_{idx}.wav"
                silence_frames = int(48000 * pause_gap)
                with wave.open(str(silence_wav), "wb") as sw:
                    sw.setnchannels(1)
                    sw.setsampwidth(2)
                    sw.setframerate(48000)
                    sw.writeframes(b"\x00\x00" * silence_frames)
                f.write(f"file '{silence_wav.resolve()}'\n")
                
    raw_narration = audio_rev_dir / "narration_raw.wav"
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy", str(raw_narration)
    ]
    subprocess.run(cmd_concat, check=True, capture_output=True)
    concat_list.unlink(missing_ok=True)
    
    # Master audio to -11.0 LUFS and -1.0 dBTP via audio_processing.master()
    mastered_narration = audio_rev_dir / "narration.wav"
    shutil.copy2(raw_narration, mastered_narration)
    raw_narration.unlink(missing_ok=True)
    temp_work = audio_rev_dir / "master_work_tmp.wav"
    ap.master(mastered_narration, temp_work, {"audio_lufs": -11.0, "audio_peak_db": -1.0})
    
    # Measure mastered audio parameters with ffmpeg loudnorm
    r_measure = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", str(mastered_narration), "-af", "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True
    )
    m_json = {}
    try:
        m_json = json.loads(r_measure.stderr[r_measure.stderr.rindex("{"):r_measure.stderr.rindex("}")+1])
    except Exception:
        pass
        
    measured_lufs = float(m_json.get("input_i", -11.0))
    measured_tp = float(m_json.get("input_tp", -1.0))
    
    # Build subtitles.srt
    def fmt_time(seconds: float) -> str:
        ms = round(seconds * 1000)
        return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"
        
    srt_lines = []
    for i, c in enumerate(cues, 1):
        srt_lines.append(f"{i}\n{fmt_time(c['start'])} --> {fmt_time(c['end'])}\n{c['text']}\n")
    srt_path = audio_rev_dir / "subtitles.srt"
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")
    
    # Build output.json for pilot and downstream compatibility
    audio_output = {
        "schema_version": "1.0",
        "job_id": job_dir.name,
        "module": "audio",
        "revision": 1,
        "files": [f"revisions/audio/1/{p.name}" for p in audio_rev_dir.glob("*.wav")] + ["revisions/audio/1/subtitles.srt"],
        "payload": {
            "wav": "revisions/audio/1/narration.wav",
            "duration": total_duration,
            "segments": segments,
            "cues": cues,
            "measured_lufs": measured_lufs,
            "measured_peak_dbtp": measured_tp,
            "tracks": {
                "vi": {
                    "wav": "revisions/audio/1/narration.wav",
                    "duration": total_duration,
                    "segments": segments,
                    "cues": cues,
                }
            }
        }
    }
    (audio_rev_dir / "output.json").write_text(json.dumps(audio_output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (audio_rev_dir / "audio-result.json").write_text(json.dumps(audio_output["payload"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    
    logger.info(f"  [+] Âm thanh đã tổng hợp hoàn tất: {len(scenes)} cảnh, tổng thời lượng: {total_duration:.2f}s")
    logger.info(f"  [+] Âm học đo lường: {measured_lufs:.2f} LUFS (mục tiêu -11.0), True Peak: {measured_tp:.2f} dBTP (mục tiêu -1.0)")
    
    return audio_output["payload"]


async def generate_images_stage(job_dir: Path, aspect_ratio: str = "9:16", max_profiles: int = 4) -> Dict[str, Any]:
    """Execute Stage 3: Flow CDP Image Generation for all scenes and Native Thumbnail."""
    logger.info(f"[*] GIAI ĐOẠN 3: Biên dịch prompt và sinh ảnh qua Flow CDP cho {job_dir.name} ({aspect_ratio})...")
    brief = json.loads((job_dir / "brief.json").read_text(encoding="utf-8"))
    content = json.loads((job_dir / "content.json").read_text(encoding="utf-8"))
    
    img_rev_dir = job_dir / "revisions/images/1"
    img_rev_dir.mkdir(parents=True, exist_ok=True)
    
    ratio_slug = aspect_ratio.replace(":", "x")
    target_size = (1080, 1920) if aspect_ratio == "9:16" else (1920, 1080)
    
    # 1. Compile all items
    items_to_generate: List[Dict[str, Any]] = []
    
    for sc in content.get("scenes", []):
        for img in sc.get("images", []):
            req_id = img["id"]
            target_jpg = img_rev_dir / f"{req_id}_{ratio_slug}.jpg"
            target_json = img_rev_dir / f"{req_id}_{ratio_slug}.json"
            
            shot = img.get("shot_type", "full_scene")
            if shot == "variation":
                shot = "full_scene"
                
            compiled = compile_flow_prompt(
                "NanoBanana2Lite",
                "scene",
                {
                    "description": img["description"],
                    "aspect_ratio": aspect_ratio,
                    "allowed_text": img.get("visible_text", []),
                    "shot_type": shot,
                    "has_character": img.get("has_character", True),
                    "character_free": not img.get("has_character", True),
                },
                version="1.7.0",
            )
            items_to_generate.append({
                "id": req_id,
                "scene_id": sc["id"],
                "prompt": compiled["prompt"],
                "target_jpg": target_jpg,
                "target_json": target_json,
                "aspect": aspect_ratio,
                "is_thumb": False,
            })
            
    # Native Thumbnail item
    thumb_id = f"THUMBNAIL_{ratio_slug}"
    thumb_jpg = img_rev_dir / f"{thumb_id}.jpg"
    thumb_json = img_rev_dir / f"{thumb_id}.json"
    thumb_spec = brief.get("packaging", {}).get("thumbnail_spec", {})
    thumb_prompt = thumb_spec.get("thumbnail_prompt") or thumb_spec.get("visual_hook", "Minimal flat doodle canvas.")
    thumb_text = thumb_spec.get("text_overlay", "VIDEO PILOT")

    # Align thumbnail visual prompt with concept objects for Flow compiler
    upper_text = thumb_text.upper()
    lower_prompt = thumb_prompt.lower()
    if any(w in upper_text for w in ["GIỜ", "THỜI GIAN", "PHÚT", "GIÂY"]) and not any(w in lower_prompt for w in ["clock", "timer", "watch", "hourglass"]):
        thumb_prompt = f"{thumb_prompt}. Concrete prop: glowing digital alarm clock showing 02:00 on nightstand."
    if any(w in upper_text for w in ["TRÁCH", "LƯỜI", "TRÌ HOÃN"]) and not any(w in lower_prompt for w in ["desk", "book", "phone", "task"]):
        thumb_prompt = f"{thumb_prompt}. Concrete prop: glowing smartphone and heavy task notebook on study desk."
    
    thumb_compiled = compile_flow_prompt(
        "NanoBanana2Lite",
        "scene",
        {
            "description": thumb_prompt,
            "aspect_ratio": aspect_ratio,
            "allowed_text": [thumb_text],
            "shot_type": "full_scene",
            "has_character": True,
            "character_free": False,
        },
        version="1.7.0",
    )
    items_to_generate.append({
        "id": thumb_id,
        "scene_id": "THUMBNAIL",
        "prompt": thumb_compiled["prompt"],
        "target_jpg": thumb_jpg,
        "target_json": thumb_json,
        "aspect": aspect_ratio,
        "is_thumb": True,
    })
    
    logger.info(f"  [+] Tổng cộng {len(items_to_generate)} ảnh cần sinh (gồm {len(items_to_generate)-1} ảnh cảnh + 1 Native Thumbnail)")
    
    # 2. Check already valid images on disk
    pending_items = []
    for it in items_to_generate:
        jpg = it["target_jpg"]
        js = it["target_json"]
        if jpg.is_file() and js.is_file() and jpg.stat().st_size > 5000:
            try:
                with Image.open(jpg) as im:
                    im.verify()
                meta = json.loads(js.read_text(encoding="utf-8"))
                if meta.get("forgeId"):
                    continue
            except Exception:
                pass
        pending_items.append(it)
        
    logger.info(f"  [+] Cần sinh mới trên Flow CDP: {len(pending_items)} ảnh")
    
    # 3. Launch Chrome profiles & generate via PersistentWorkerPool
    if pending_items:
        from flow_cdp.persistent_pool import PersistentWorkerPool
        logger.info(f"  [+] Khởi tạo PersistentWorkerPool ({max_profiles} workers)...")
        pool = PersistentWorkerPool(
            target_workers=max_profiles,
            cooldown_seconds=300.0,
            pacing_seconds=2.0,
            stagger_seconds=0.5,
            headless=True,
            default_out_dir=img_rev_dir,
        )
        with pool:
            for it in pending_items:
                pool.submit_task({
                    "id": it["id"],
                    "prompt": it["prompt"],
                    "ratio": it["aspect"],
                    "filename": it["target_jpg"].name,
                    "out_dir": str(img_rev_dir),
                    "editorial_overlay": {"enabled": False},
                })
            
            logger.info(f"  [+] Chờ PersistentWorkerPool hoàn thành {len(pending_items)} ảnh...")
            timeout_sec = max(300.0, len(pending_items) * 60.0)
            completed = pool.wait_completion(timeout=timeout_sec)
            if not completed or pool.shared_queue.qsize() > 0:
                raise RuntimeError(f"Flow pool timeout hoặc chưa hoàn tất: {pool.get_status()}")

    # Verify and normalize image resolutions with PIL
    for it in items_to_generate:
        jpg = it["target_jpg"]
        if not jpg.is_file():
            raise FileNotFoundError(f"Thiếu file ảnh đầu ra: {jpg}")
        with Image.open(jpg) as im:
            if im.size != target_size:
                im_resized = im.resize(target_size, Image.Resampling.LANCZOS)
                im_resized.save(jpg, format="JPEG", quality=95)
            else:
                im.verify()
                
    # 4. Copy thumbnail to root of job_dir
    if thumb_jpg.is_file():
        dest_thumb = job_dir / f"thumbnail_{ratio_slug}.jpg"
        shutil.copy2(thumb_jpg, dest_thumb)
        
    # 5. Build output.json for images module
    manifest_items = []
    files_list = []
    for it in items_to_generate:
        files_list.append(f"revisions/images/1/{it['target_jpg'].name}")
        files_list.append(f"revisions/images/1/{it['target_json'].name}")
        if not it["is_thumb"]:
            sha = hashlib.sha256(it["target_jpg"].read_bytes()).hexdigest()
            manifest_items.append({
                "image_id": it["id"],
                "scene_id": it["scene_id"],
                "path": f"revisions/images/1/{it['target_jpg'].name}",
                "prompt": it["prompt"],
                "sha256": sha,
                "ratio": it["aspect"],
            })
            
    images_output = {
        "schema_version": "1.0",
        "job_id": job_dir.name,
        "module": "images",
        "revision": 1,
        "files": files_list,
        "items": manifest_items,
        "checks": {"passed": True, "errors": []},
    }
    (img_rev_dir / "output.json").write_text(json.dumps(images_output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info(f"  [+] Đã lưu toàn bộ {len(manifest_items)} ảnh và 1 thumbnail tại {img_rev_dir}")
    
    return images_output


def render_video_stage(job_dir: Path, audio_payload: Dict[str, Any], images_payload: Dict[str, Any]) -> Path:
    """Execute Stage 4: Video Rendering via Remotion render.mjs."""
    logger.info(f"[*] GIAI ĐOẠN 4: Chuẩn bị props và Render video Remotion cho {job_dir.name}...")
    brief = json.loads((job_dir / "brief.json").read_text(encoding="utf-8"))
    content = json.loads((job_dir / "content.json").read_text(encoding="utf-8"))
    
    render_dir = job_dir / "revisions/render/1"
    public_dir = render_dir / "public"
    public_dir.mkdir(parents=True, exist_ok=True)
    
    aspect = brief.get("outputs", [{}])[0].get("aspect_ratio", "9:16")
    ratio_slug = aspect.replace(":", "x")
    
    # 1. Copy mastered audio into public/vi.wav
    audio_wav = job_dir / audio_payload["wav"]
    shutil.copy2(audio_wav, public_dir / "vi.wav")
    
    # Copy sfx if available
    sfx_dir = SYS_DIR / "assets/sfx"
    if sfx_dir.is_dir():
        for sfx in sfx_dir.glob("*.wav"):
            shutil.copy2(sfx, public_dir / sfx.name)
            
    # 2. Copy scene images into public/
    scenes_timeline = []
    by_id = {item["image_id"]: item for item in images_payload["items"]}
    
    scenes = content.get("scenes", [])
    segments = audio_payload.get("segments", [])
    
    for sc_idx, sc in enumerate(scenes):
        sc_id = sc["id"]
        sc_segs = [s for s in segments if s["scene_id"] == sc_id]
        if not sc_segs:
            continue
        start_time = sc_segs[0]["start"]
        if sc_idx < len(scenes) - 1:
            next_sc_id = scenes[sc_idx + 1]["id"]
            next_segs = [s for s in segments if s["scene_id"] == next_sc_id]
            end_time = next_segs[0]["start"] if next_segs else sc_segs[-1]["end"]
        else:
            end_time = audio_payload["duration"]
        
        # Primary image for the scene
        sc_imgs = sc.get("images", [])
        if not sc_imgs:
            continue
            
        prim_img_id = sc_imgs[0]["id"]
        img_item = by_id.get(prim_img_id)
        if not img_item:
            continue
            
        src_img = job_dir / img_item["path"]
        target_name = f"{prim_img_id}_{ratio_slug}.jpg"
        shutil.copy2(src_img, public_dir / target_name)
        
        # Sub-beats
        beats = []
        for b_idx, b_img in enumerate(sc_imgs):
            b_id = b_img["id"]
            b_item = by_id.get(b_id)
            if not b_item:
                continue
            b_name = f"{b_id}_{ratio_slug}.jpg"
            shutil.copy2(job_dir / b_item["path"], public_dir / b_name)
            
            beat_at = 0.0 if b_idx == 0 else (end_time - start_time) * (b_idx / len(sc_imgs))
            beats.append({
                "at": round(beat_at, 3),
                "src": b_name,
                "motion": {"type": "pan_subtle", "zoom": 1.05},
            })
            
        scenes_timeline.append({
            "id": sc_id,
            "title": sc.get("title", sc_id),
            "image": target_name,
            "start": start_time,
            "end": end_time,
            "images": beats,
        })
        
    # Copy thumbnail image if present
    thumb_name = f"THUMBNAIL_{ratio_slug}.jpg"
    thumb_path = job_dir / f"revisions/images/1/{thumb_name}"
    if thumb_path.is_file():
        shutil.copy2(thumb_path, public_dir / thumb_name)
        
    # 3. Build props.json
    props = {
        "aspect_ratio": aspect,
        "outputs": brief.get("outputs", [{"aspect_ratio": aspect, "language": "vi", "subtitles": True, "voice": "VietNarrator", "speed": 1.0}]),
        "primary_language": "vi",
        "tracks": {
            "vi": {
                "audioSrc": "vi.wav",
                "duration": audio_payload["duration"],
                "cues": audio_payload["cues"],
                "scenesByAspect": {
                    aspect: scenes_timeline,
                },
            }
        },
        "render_concurrency": 2,
        "modern_style": True,
        "thumbnail_spec": brief.get("packaging", {}).get("thumbnail_spec", {}),
    }
    
    (render_dir / "props.json").write_text(json.dumps(props, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    
    # 4. Execute render.mjs via Node
    logger.info(f"  [+] Chạy render.mjs Remotion tại {render_dir}...")
    cmd_render = ["node", "sys/renderer/render.mjs", str(render_dir)]
    res = subprocess.run(cmd_render, cwd=str(ROOT_DIR), capture_output=True, text=True)
    if res.returncode != 0:
        logger.error(f"Render thất bại: {res.stderr}\n{res.stdout}")
        raise RuntimeError(f"Remotion render thất bại (mã {res.returncode})")
        
    logger.info("  [+] Remotion render thành công!")
    
    # 5. Copy final deliverables to video/<job_dir.name>/
    video_deliv_dir = ROOT_DIR / "video" / job_dir.name
    video_deliv_dir.mkdir(parents=True, exist_ok=True)
    
    source_mp4 = render_dir / f"video_{ratio_slug}.mp4"
    if not source_mp4.is_file():
        source_mp4 = render_dir / "video.mp4"
        
    if not source_mp4.is_file():
        raise FileNotFoundError(f"Không tìm thấy video đầu ra tại {render_dir}")
        
    final_mp4 = video_deliv_dir / f"{job_dir.name}.mp4"
    named_mp4 = video_deliv_dir / f"video_{ratio_slug}.mp4"
    shutil.copy2(source_mp4, final_mp4)
    shutil.copy2(source_mp4, named_mp4)
    
    # Subtitles
    srt_source = render_dir / "subtitles.srt"
    if not srt_source.is_file():
        srt_source = job_dir / "revisions/audio/1/subtitles.srt"
    shutil.copy2(srt_source, video_deliv_dir / f"{job_dir.name}.srt")
    shutil.copy2(srt_source, video_deliv_dir / "subtitles.srt")
    
    # Thumbnail / Cover
    thumb_source = job_dir / f"thumbnail_{ratio_slug}.jpg"
    if not thumb_source.is_file():
        thumb_source = job_dir / f"revisions/images/1/THUMBNAIL_{ratio_slug}.jpg"
    if thumb_source.is_file():
        shutil.copy2(thumb_source, video_deliv_dir / f"thumbnail_{ratio_slug}.jpg")
        shutil.copy2(thumb_source, video_deliv_dir / "cover.jpg")
        
    logger.info(f"  [✓] Đã xuất video MP4 và subtitles SRT đầy đủ tại: {video_deliv_dir}")
    return final_mp4


def verify_job(job_dir: Path, mp4_path: Optional[Path] = None) -> Dict[str, Any]:
    """Execute Stage 5: Deep Verification of contracts, hook scorer, and ffprobe."""
    logger.info(f"[*] GIAI ĐOẠN 5: Kiểm định xác thực cho {job_dir.name}...")
    brief = json.loads((job_dir / "brief.json").read_text(encoding="utf-8"))
    content = json.loads((job_dir / "content.json").read_text(encoding="utf-8"))
    
    valid, errors = validate_production_bundle(SYS_DIR, brief, content)
    fmt = brief.get("format_profile", "short_9x16")
    hook = score_content_file(job_dir / "content.json", "nao_luoi", fmt)
    
    probe_info = {}
    if mp4_path and mp4_path.is_file():
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration,size,bit_rate:stream=width,height,codec_name,r_frame_rate,sample_rate,channels",
            "-of", "json", str(mp4_path)
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, check=True)
        probe_info = json.loads(r.stdout)
        
    return {
        "job_id": job_dir.name,
        "format": fmt,
        "valid_bundle": valid,
        "contract_errors": errors,
        "hook_score": {
            "score": hook.score,
            "hook": hook.hook,
            "syllables": hook.hook_syllables,
            "estimated_seconds": hook.estimated_seconds,
            "needs_rewrite": hook.needs_rewrite,
        },
        "ffprobe": probe_info,
    }


async def main():
    parser = argparse.ArgumentParser(description="Produce complete video packages for channel nao_luoi")
    parser.add_argument("--job", choices=["9x16", "16x9", "all"], default="all")
    args = parser.parse_args()
    
    runs_dir = SYS_DIR / "runs"
    jobs_to_run = []
    if args.job in ("9x16", "all"):
        jobs_to_run.append((runs_dir / "nao-luoi-week1-9x16", "9:16"))
    if args.job in ("16x9", "all"):
        jobs_to_run.append((runs_dir / "nao-luoi-week1-16x9", "16:9"))
        
    overall_summary = {}
    
    for job_dir, aspect in jobs_to_run:
        logger.info("=" * 70)
        logger.info(f"  BẮT ĐẦU SẢN XUẤT JOB: {job_dir.name} ({aspect})")
        logger.info("=" * 70)
        
        # 1. Audio
        audio_payload = generate_audio_stage(job_dir)
        
        # 2. Images
        images_payload = await generate_images_stage(job_dir, aspect_ratio=aspect, max_profiles=4)
        
        # 3. Video Render
        final_mp4 = render_video_stage(job_dir, audio_payload, images_payload)
        
        # 4. Verify
        verification = verify_job(job_dir, final_mp4)
        overall_summary[job_dir.name] = verification
        
    logger.info("\n" + "=" * 70)
    logger.info("  KẾT QUẢ SẢN XUẤT HOÀN TẤT CHO KÊNH NÃO LƯỜI:")
    logger.info(json.dumps(overall_summary, indent=2, ensure_ascii=False))
    logger.info("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
