#!/usr/bin/env python3
"""Video Pilot — Universal E2E Short Production Runner for Channels (Wave 4).

Executes full end-to-end production for Short-Video (short_9x16):
- Stage A: Flow CDP Full-Frame Images + Native Thumbnail (revisions/images/1/)
- Stage B: Wave 4 Studio-Clean Fast Audio TTS (revisions/audio/1/)
- Stage C: Remote Colab T4 Headless Remotion Render (revisions/render/1/ -> video/<job_id>/)
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import logging
import re
import shutil
import subprocess
import sys
import wave
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image

SYS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = SYS_DIR.parent
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import audio_processing as ap  # noqa: E402
from channels.registry import get_channel  # noqa: E402
from colab_bridge.client import Client, ColabError  # noqa: E402
from colab_bridge.job_protocol import build_render_request  # noqa: E402
from colab_bridge.protocol import build_request  # noqa: E402
from flow_prompts import compile as compile_flow_prompt  # noqa: E402
from flow_prompts.compiler import CHARACTER_FREE_DIRECTIVE  # noqa: E402
from scripts.subtitles import audit_cues, subtitle_cues  # noqa: E402
from tools.vn_text_normalizer import normalize_for_tts  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("produce_channel_short_e2e")

CANDIDATE_ACCOUNTS: List[str] = [
    "account-01",
    "account-03",
    "account-04",
    "account-05",
    "account-06",
    "account-07",
    "account-08",
    "account-09",
    "account-10",
    "account-11",
    "account-12",
    "account-13",
    "account-14",
    "account-15",
    "account-16",
    "account-17",
    "account-18",
    "account-19",
    "account-20",
]

SENTENCE_RE = re.compile(r'(?<=[.!?…;])\s+|(?<=[.!?…;]["\'”’])\s+')
SENTENCE_END_CHARS = ('.', '!', '?', '…', ';', ':', '”', '"', '’', "'")


def split_long_sentence_at_middle_comma(sentence: str) -> List[str]:
    """If sentence has > 18 words and contains commas, split at the comma closest to the middle."""
    words = sentence.split()
    if len(words) <= 18 or "," not in sentence:
        return [sentence]

    comma_indices = [m.start() for m in re.finditer(r",", sentence)]
    if not comma_indices:
        return [sentence]

    target_mid = len(words) / 2.0
    best_idx = -1
    best_diff = float("inf")

    for idx in comma_indices:
        before = sentence[:idx].strip()
        after = sentence[idx + 1:].strip()
        w1 = len(before.split())
        w2 = len(after.split())
        if w1 == 0 or w2 == 0:
            continue
        diff = abs(w1 - target_mid)
        if diff < best_diff:
            best_diff = diff
            best_idx = idx

    if best_idx == -1:
        return [sentence]

    part1 = sentence[:best_idx].strip()
    part2 = sentence[best_idx + 1:].strip()

    res = [part1]
    if len(part2.split()) > 18 and "," in part2:
        res.extend(split_long_sentence_at_middle_comma(part2))
    else:
        res.append(part2)

    return res


def split_into_clauses(text: str) -> List[str]:
    """Split narration into natural spoken clauses/sentences for OmniVoice."""
    clean = text.strip()
    if not clean:
        return []

    raw_sentences = [s.strip() for s in SENTENCE_RE.split(clean) if s.strip()]
    clauses: List[str] = []
    for s in raw_sentences:
        clauses.extend(split_long_sentence_at_middle_comma(s))

    return [c for c in clauses if c]


def concat_mono_pcm16_wavs(wav_paths: List[Path], out_wav: Path) -> None:
    """Concatenate 48kHz mono PCM16 WAV files without transcoding loss."""
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_wav), "wb") as outfile:
        outfile.setnchannels(1)
        outfile.setsampwidth(2)
        outfile.setframerate(48000)
        for p in wav_paths:
            with wave.open(str(p), "rb") as infile:
                if (infile.getnchannels(), infile.getsampwidth(), infile.getframerate()) != (1, 2, 48000):
                    tmp_conv = p.with_name(f"conv_{p.name}")
                    cmd = [
                        "ffmpeg", "-y", "-i", str(p),
                        "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le",
                        str(tmp_conv),
                    ]
                    subprocess.run(cmd, check=True, capture_output=True)
                    with wave.open(str(tmp_conv), "rb") as cin:
                        outfile.writeframes(cin.readframes(cin.getnframes()))
                    tmp_conv.unlink(missing_ok=True)
                else:
                    outfile.writeframes(infile.readframes(infile.getnframes()))


def resolve_channel_ids(raw_id: str) -> Tuple[str, str]:
    """Normalize user channel identifier into (channel_id, channel_slug)."""
    clean = raw_id.strip()
    if clean.startswith("channel-"):
        clean = clean[len("channel-"):]
    if clean.startswith("ch_"):
        clean = clean[len("ch_"):]
    channel_id = clean.replace("-", "_")
    channel_slug = clean.replace("_", "-")
    return channel_id, channel_slug


def find_voice_profile(sys_dir: Path, channel_id: str, channel_slug: str) -> Tuple[Path, Dict[str, Any]]:
    """Locate channel voice profile and ensure local presence inside sys_dir/assets/voices/ch_<channel_id>."""
    target_dir = sys_dir / f"assets/voices/ch_{channel_id}"
    local_profile = target_dir / "profile.json"
    if local_profile.is_file() and (target_dir / "reference.wav").is_file():
        return local_profile, json.loads(local_profile.read_text(encoding="utf-8"))

    candidates = [
        sys_dir / f"assets/voices/ch_{channel_id}/profile.json",
        sys_dir / f"assets/voices/{channel_id}/profile.json",
        Path(f"/home/hongphuoc6104/Desktop/vp-channels/channel-{channel_slug}/sys/assets/voices/ch_{channel_id}/profile.json"),
        Path(f"/home/hongphuoc6104/Desktop/vp-channels/channel-{channel_slug}/sys/assets/voices/{channel_id}/profile.json"),
        Path(f"/home/hongphuoc6104/Desktop/vp-agent-core/sys/assets/voices/ch_{channel_id}/profile.json"),
        Path(f"/home/hongphuoc6104/Desktop/vp-agent-core/sys/assets/voices/{channel_id}/profile.json"),
    ]
    found_profile: Optional[Path] = None
    for p in candidates:
        if p.is_file():
            found_profile = p
            break

    if not found_profile:
        fallback = sys_dir / "assets/voices/viet_narrator/profile.json"
        if not fallback.is_file():
            fallback = Path("/home/hongphuoc6104/Desktop/vp-agent-core/sys/assets/voices/viet_narrator/profile.json")
        found_profile = fallback

    profile_data = json.loads(found_profile.read_text(encoding="utf-8"))
    ref_name = profile_data.get("reference_wav", "reference.wav")
    src_ref = found_profile.parent / ref_name

    target_dir.mkdir(parents=True, exist_ok=True)
    if found_profile.resolve() != local_profile.resolve():
        shutil.copy2(found_profile, local_profile)
    if src_ref.is_file() and not (target_dir / ref_name).is_file():
        shutil.copy2(src_ref, target_dir / ref_name)

    return local_profile, profile_data


def compile_channel_scene_prompt(
    ch: Any,
    brief: Dict[str, Any],
    content: Dict[str, Any],
    sc: Dict[str, Any],
    img: Dict[str, Any],
    aspect_ratio: str = "9:16",
) -> str:
    """Compile custom channel scene prompt adhering to each channel's distinct visual identity."""
    s1 = (
        f"Requested aspect ratio: {aspect_ratio}. Render a complete 100% full-bleed vertical {aspect_ratio} "
        "2D illustration extending continuously to all four edges with zero letterbox bars, zero subtitle boxes, "
        "zero UI chrome, and zero dark vignette."
    )
    palette_str = ", ".join(ch.visual.palette) if hasattr(ch.visual, "palette") else "#FFFFFF"
    s2 = f"Visual Style ({ch.visual.profile_id}): {brief.get('style') or ch.visual.style_description} Palette: {palette_str}."

    has_char = bool(img.get("has_character", True))
    if has_char:
        char_map = {c["id"]: c for c in content.get("characters", [])}
        cids = img.get("character_ids") or sc.get("character_ids") or []
        char_descs = []
        for cid in cids:
            c = char_map.get(cid)
            if c:
                char_descs.append(
                    f"Character {c.get('name', cid)}: {c.get('appearance', '')}. Outfit: {c.get('outfit', '')}."
                )
        if char_descs:
            s3 = " ".join(char_descs)
        else:
            s3 = f"Character: {ch.visual.cast_appearance}. Outfit: {ch.visual.outfit}."
    else:
        s3 = CHARACTER_FREE_DIRECTIVE

    s4 = f"Scene Composition & Action: {img['description']}"

    visible_text = img.get("visible_text") or []
    if visible_text:
        text_labels = ", ".join(
            f'"{t}"' if isinstance(t, str) else f'"{t.get("text", "")}"' for t in visible_text
        )
        s5 = f"Render concise uppercase Vietnamese hand-lettered labels (< 5% frame height) for exact text: {text_labels}."
    else:
        s5 = "Strict zero-text policy: render zero words, letters, numbers, speech bubbles, or watermarks anywhere in the frame."

    return f"{s1}\n\n{s2}\n\n{s3}\n\n{s4}\n\n{s5}"


def compile_channel_thumb_prompt(
    ch: Any,
    brief: Dict[str, Any],
    thumb_prompt: str,
    thumb_text: str,
    aspect_ratio: str = "9:16",
) -> str:
    """Compile custom channel thumbnail prompt with native canvas lettering and zero text cards."""
    s1 = (
        f"Requested aspect ratio: {aspect_ratio}. Render a complete 100% full-bleed vertical {aspect_ratio} "
        "2D thumbnail illustration extending continuously to all four edges with zero letterbox bars, "
        "zero subtitle boxes, zero UI chrome, and zero dark vignette."
    )
    palette_str = ", ".join(ch.visual.palette) if hasattr(ch.visual, "palette") else "#FFFFFF"
    s2 = f"Visual Style ({ch.visual.profile_id}): {ch.visual.style_description} Palette: {palette_str}."
    s3 = f"Character Cast: {ch.visual.cast_appearance}. Outfit: {ch.visual.outfit}."
    s4 = f"Thumbnail Composition & Rule: {ch.visual.thumbnail_rule} Visual Scene: {thumb_prompt}"
    s5 = (
        f'Native hand-lettered hook text integrated directly onto the flat background canvas '
        f'(strictly zero rectangular text cards, banners, or gradient overlays covering artwork): "{thumb_text}"'
    )
    return f"{s1}\n\n{s2}\n\n{s3}\n\n{s4}\n\n{s5}"


def stage_a_images(
    sys_dir: Path,
    job_dir: Path,
    channel_id: str,
    brief: Dict[str, Any],
    content: Dict[str, Any],
    flow_profiles_arg: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute Stage A: Flow CDP Full-Frame Images + Native Thumbnail."""
    logger.info(f"[*] GIAI ĐOẠN A: Kiểm tra và chuẩn bị ảnh Flow CDP cho {job_dir.name} (kênh: {channel_id}, 9:16)...")
    img_rev_dir = job_dir / "revisions/images/1"
    img_rev_dir.mkdir(parents=True, exist_ok=True)

    aspect_ratio = "9:16"
    target_size = (1080, 1920)

    is_nao_luoi = (channel_id == "nao_luoi")
    ch_profile = None if is_nao_luoi else get_channel(channel_id)

    # 1. Compile items to generate
    items_to_generate: List[Dict[str, Any]] = []
    for sc in content.get("scenes", []):
        for img in sc.get("images", []):
            req_id = img["id"]
            target_jpg = img_rev_dir / f"{req_id}_9x16.jpg"
            target_json = img_rev_dir / f"{req_id}_9x16.json"
            shot = img.get("shot_type", "full_scene")
            if shot == "variation":
                shot = "full_scene"

            if is_nao_luoi:
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
                final_prompt = compiled["prompt"]
            else:
                final_prompt = compile_channel_scene_prompt(
                    ch_profile, brief, content, sc, img, aspect_ratio=aspect_ratio
                )

            items_to_generate.append({
                "id": req_id,
                "scene_id": sc["id"],
                "prompt": final_prompt,
                "target_jpg": target_jpg,
                "target_json": target_json,
                "aspect": aspect_ratio,
                "is_thumb": False,
            })

    # Native Thumbnail item
    thumb_id = "THUMBNAIL_9x16"
    thumb_jpg = img_rev_dir / f"{thumb_id}.jpg"
    thumb_json = img_rev_dir / f"{thumb_id}.json"
    thumb_spec = brief.get("packaging", {}).get("thumbnail_spec", {})
    thumb_prompt = thumb_spec.get("thumbnail_prompt") or thumb_spec.get("visual_hook", "Minimal flat doodle canvas.")
    thumb_text = thumb_spec.get("text_overlay", "VIDEO PILOT")

    if is_nao_luoi:
        upper_text = thumb_text.upper()
        lower_prompt = thumb_prompt.lower()
        if any(w in upper_text for w in ["GIỜ", "THỜI GIAN", "PHÚT", "GIÂY"]) and not any(
            w in lower_prompt for w in ["clock", "timer", "watch", "hourglass"]
        ):
            thumb_prompt = f"{thumb_prompt}. Concrete prop: glowing digital alarm clock showing 02:00 on nightstand."
        if any(w in upper_text for w in ["TRÁCH", "LƯỜI", "TRÌ HOÃN"]) and not any(
            w in lower_prompt for w in ["desk", "book", "phone", "task"]
        ):
            thumb_prompt = f"{thumb_prompt}. Concrete prop: glowing smartphone and heavy task notebook on study desk."

        thumb_compiled = compile_flow_prompt(
            "NanoBanana2Lite",
            "scene",
            {
                "description": thumb_prompt,
                "aspect_ratio": aspect_ratio,
                "allowed_text": [thumb_text] if thumb_text else [],
                "shot_type": "full_scene",
                "has_character": True,
                "character_free": False,
            },
            version="1.7.0",
        )
        final_thumb_prompt = thumb_compiled["prompt"]
    else:
        final_thumb_prompt = compile_channel_thumb_prompt(
            ch_profile, brief, thumb_prompt, thumb_text, aspect_ratio=aspect_ratio
        )

    items_to_generate.append({
        "id": thumb_id,
        "scene_id": "THUMBNAIL",
        "prompt": final_thumb_prompt,
        "target_jpg": thumb_jpg,
        "target_json": thumb_json,
        "aspect": aspect_ratio,
        "is_thumb": True,
    })

    # 2. Check if all items already valid on disk
    pending_items: List[Dict[str, Any]] = []
    for it in items_to_generate:
        jpg = it["target_jpg"]
        js = it["target_json"]
        if jpg.is_file() and js.is_file() and jpg.stat().st_size > 5000:
            try:
                with Image.open(jpg) as im:
                    im.verify()
                meta = json.loads(js.read_text(encoding="utf-8"))
                if meta.get("forgeId") or meta.get("media_id"):
                    continue
            except Exception:
                pass
        pending_items.append(it)

    if not pending_items:
        logger.info(f"  [✓] Toàn bộ {len(items_to_generate)} ảnh cảnh và Thumbnail đã tồn tại hợp lệ. Bỏ qua Flow CDP!")
    else:
        logger.info(f"  [+] Cần sinh mới trên Flow CDP: {len(pending_items)}/{len(items_to_generate)} ảnh...")
        from flow_cdp.cdp_direct_client import PROFILES
        from flow_cdp.persistent_pool import PersistentWorkerPool

        # Profile filtering
        if flow_profiles_arg:
            allowed_set = {p.strip() for p in flow_profiles_arg.split(",") if p.strip()}
            assigned_profiles = [p for p in PROFILES if p.get("name") in allowed_set or p.get("id") in allowed_set]
            if not assigned_profiles:
                logger.warning(f"No profiles matched '{flow_profiles_arg}', using all available.")
                assigned_profiles = list(PROFILES)
        else:
            assigned_profiles = list(PROFILES)

        workers_count = min(len(assigned_profiles), 3)
        logger.info(
            f"  [+] Khởi tạo PersistentWorkerPool ({workers_count} workers, "
            f"profiles: {[p['name'] for p in assigned_profiles[:workers_count]]})..."
        )
        pool = PersistentWorkerPool(
            target_workers=workers_count,
            profiles=assigned_profiles,
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
            timeout_sec = max(300.0, len(pending_items) * 75.0)
            completed = pool.wait_completion(timeout=timeout_sec)
            if not completed or pool.shared_queue.qsize() > 0:
                raise RuntimeError(f"Flow pool timeout hoặc chưa hoàn tất: {pool.get_status()}")

    # 3. Verify resolutions with PIL
    for it in items_to_generate:
        jpg = it["target_jpg"]
        if not jpg.is_file():
            raise FileNotFoundError(f"Missing output image file: {jpg}")
        with Image.open(jpg) as im:
            if im.size != target_size:
                im_resized = im.resize(target_size, Image.Resampling.LANCZOS)
                im_resized.save(jpg, format="JPEG", quality=95)
            else:
                im.verify()

        # Ensure sidecar JSON exists
        js = it["target_json"]
        if not js.is_file():
            sidecar_data = {
                "jobId": it["id"],
                "forgeId": f"local-{it['id']}",
                "aspect_ratio": it["aspect"],
                "prompt": it["prompt"],
                "status": "verified",
            }
            js.write_text(json.dumps(sidecar_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # 4. Copy thumbnail to job_dir root
    if thumb_jpg.is_file():
        dest_thumb = job_dir / "thumbnail_9x16.jpg"
        shutil.copy2(thumb_jpg, dest_thumb)

    # 5. Build output.json & images.json
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
        "payload": {
            "items": manifest_items,
            "thumbnail": "revisions/images/1/THUMBNAIL_9x16.jpg",
            "format": "9:16",
        },
        "checks": {"passed": True, "errors": []},
    }
    (img_rev_dir / "output.json").write_text(json.dumps(images_output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    images_manifest = {
        "checkpoint": "final",
        "items": manifest_items,
    }
    (img_rev_dir / "images.json").write_text(json.dumps(images_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (job_dir / "images.json").write_text(json.dumps(images_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    logger.info(f"  [✓] Giai đoạn A hoàn tất: {len(manifest_items)} ảnh cảnh + 1 Native Thumbnail")
    return images_output


def stage_b_audio(
    sys_dir: Path,
    job_dir: Path,
    channel_id: str,
    channel_slug: str,
    brief: Dict[str, Any],
    content: Dict[str, Any],
    colab_account: str = "account-01",
    session_name: str = "video-pilot-tts",
    force_audio: bool = False,
) -> Tuple[Dict[str, Any], Optional[Client], Optional[str]]:
    """Execute Stage B: Wave 4 Studio-Clean Fast Audio TTS via Colab OmniVoice."""
    logger.info(f"[*] GIAI ĐOẠN B: Tổng hợp giọng kể OmniVoice Wave 4 cho {job_dir.name}...")
    audio_rev_dir = job_dir / "revisions/audio/1"
    audio_rev_dir.mkdir(parents=True, exist_ok=True)

    narration_wav = audio_rev_dir / "narration.wav"
    audio_out_json = audio_rev_dir / "output.json"
    subtitles_srt = audio_rev_dir / "subtitles.srt"

    # Reuse if already valid and force_audio is False
    if not force_audio and narration_wav.is_file() and audio_out_json.is_file() and subtitles_srt.is_file():
        try:
            saved = json.loads(audio_out_json.read_text(encoding="utf-8"))
            payload = saved.get("payload", saved)
            if payload.get("duration") and payload.get("segments") and payload.get("tracks"):
                logger.info(
                    f"  [✓] Âm thanh đã tồn tại hợp lệ ({payload['duration']:.2f}s). "
                    "Bỏ qua tái tổng hợp (dùng --force-audio nếu muốn tạo lại)."
                )
                return payload, None, payload.get("account_used")
        except Exception:
            pass

    # 1. Voice profile resolution
    profile_path, profile = find_voice_profile(sys_dir, channel_id, channel_slug)
    voice_name = profile.get("voice", f"VietNarrator_{channel_slug}")
    rel_profile = str(profile_path.relative_to(sys_dir))

    tts_speed = float(profile.get("recommended_speed", profile.get("source_speed", 1.0)))
    target_lufs = float(profile.get("audio_lufs", -14.0))
    target_peak = float(profile.get("audio_peak_db", -1.5))
    voice_chain = profile.get("audio_voice_chain") or ap.VOICE_CHAIN

    # 2. Build scenes plan with snappy Wave 4 cadence pauses
    scenes = content.get("scenes", [])
    scenes_plan: List[Dict[str, Any]] = []
    for sc in scenes:
        narration = sc.get("narration", "").strip()
        norm_narration = normalize_for_tts(narration)
        clauses = split_into_clauses(norm_narration)
        if not clauses:
            clauses = [norm_narration]
        gaps = [0.10 if not c.endswith(SENTENCE_END_CHARS) else 0.18 for c in clauses[:-1]]
        scenes_plan.append({
            "scene_id": sc["id"],
            "texts": clauses,
            "gaps": gaps,
            "tail": 0.20,
            "tone": None,
        })

    # 3. Colab configuration
    base_cfg_path = sys_dir / "config.json"
    cfg: Dict[str, Any] = json.loads(base_cfg_path.read_text(encoding="utf-8")) if base_cfg_path.is_file() else {}
    cfg["voices"] = {"vi": rel_profile, "en": rel_profile}
    cfg["tts_voice"] = voice_name
    cfg["en_voice"] = voice_name
    cfg["tts_speed"] = tts_speed
    cfg["audio_lufs"] = target_lufs
    cfg["audio_peak_db"] = target_peak
    cfg["audio_voice_chain"] = voice_chain

    cfg.setdefault("colab_tts", {})
    cfg["colab_tts"]["session"] = session_name
    cfg["colab_tts"]["_session_explicit"] = True
    cfg["colab_tts"]["batch_size"] = 1
    cfg["colab_tts"]["num_step"] = 32
    cfg["colab_tts"]["timeout_seconds"] = 1800
    cfg["colab_tts"]["models"] = {
        "vi": {
            "id": "kjanh/KhanhTTS-OmniVoice",
            "revision": "20d056b8ea5d8d578b4cbaf1f703012fa3798a84",
        },
        "en": {
            "id": "kjanh/KhanhTTS-OmniVoice",
            "revision": "20d056b8ea5d8d578b4cbaf1f703012fa3798a84",
        },
    }

    request = build_request(sys_dir, cfg, scenes_plan, assemble=False)
    logger.info(f"Built Colab TTS request ID: {request['request_id']} with {len(request.get('items', []))} items")

    # 4. Failover synthesis execution
    accounts_to_try: List[str] = [colab_account] + [a for a in CANDIDATE_ACCOUNTS if a != colab_account]
    account_used: Optional[str] = None
    client_used: Optional[Client] = None
    cache_base = job_dir / "cache/colab-tts"
    cache_base.mkdir(parents=True, exist_ok=True)

    for acc in accounts_to_try:
        logger.info(f"Trying Colab OmniVoice synthesis on {acc}...")
        acc_cfg = copy.deepcopy(cfg)
        acc_cfg["colab_tts"]["account"] = acc
        acc_cfg["colab_tts"]["job_id"] = job_dir.name

        try:
            client = Client(sys_dir, acc_cfg)
            client.account = acc
            client.session = session_name

            try:
                client.reconcile()
            except Exception:
                pass
            try:
                client._ready(auto_start=True)
            except Exception as ex_ready:
                logger.warning(f"Account {acc} _ready failed: {ex_ready}")

            client.synthesize(request, audio_rev_dir, cache_base / acc)
            account_used = acc
            client_used = client
            logger.info(f"Colab OmniVoice synthesis succeeded on {acc}")
            break
        except (ColabError, Exception) as ex:
            logger.warning(f"Synthesis on {acc} failed ({type(ex).__name__}): {ex}. Failing over...")
            continue

    if not account_used:
        raise RuntimeError(f"All candidate Colab accounts failed for job {job_dir.name}: {accounts_to_try}")

    # 5. Process segments & word timestamps
    tts_result_file = audio_rev_dir / "tts-result.json"
    if not tts_result_file.is_file():
        raise FileNotFoundError(f"Missing {tts_result_file}")

    tts_res = json.loads(tts_result_file.read_text(encoding="utf-8"))
    synced_segments = tts_res.get("segments", [])

    segments: List[Dict[str, Any]] = []
    wav_parts: List[Path] = []
    current_time = 0.0

    for seg_info in synced_segments:
        sc_id = seg_info["scene_id"]
        text = seg_info["text"]
        part_wav = audio_rev_dir / seg_info["path"]
        wav_parts.append(part_wav)

        with wave.open(str(part_wav), "rb") as w:
            total_dur = w.getnframes() / w.getframerate()

        content_dur = float(seg_info.get("content_duration", total_dur))
        words = text.split()

        # Word timestamps MUST be 0-indexed relative to segment start (0.0 .. content_dur)
        existing_wts = seg_info.get("word_timestamps")
        valid_existing = False
        if isinstance(existing_wts, list) and len(existing_wts) == len(words):
            try:
                prev_e = 0.0
                all_good = True
                for wt in existing_wts:
                    s_rel = float(wt["start"])
                    e_rel = float(wt["end"])
                    if not (0.0 <= prev_e - 0.02 <= s_rel < e_rel <= content_dur + 0.05):
                        all_good = False
                        break
                    prev_e = s_rel
                valid_existing = all_good
            except Exception:
                valid_existing = False

        if valid_existing and existing_wts:
            word_timestamps = existing_wts
        else:
            word_dur = content_dur / max(1, len(words))
            word_timestamps = []
            for i, w in enumerate(words):
                w_start = round(i * word_dur, 3)
                w_end = round((i + 1) * word_dur, 3)
                if i == len(words) - 1:
                    w_end = min(w_end, round(content_dur, 3))
                    w_end = max(w_end, w_start + 0.01)
                word_timestamps.append({
                    "word": w,
                    "start": w_start,
                    "end": w_end,
                })

        seg = {
            "scene_id": sc_id,
            "text": text,
            "path": f"revisions/audio/1/{part_wav.name}",
            "start": round(current_time, 3),
            "end": round(current_time + total_dur, 3),
            "content_end": round(current_time + content_dur, 3),
            "word_timestamps": word_timestamps,
        }
        segments.append(seg)
        current_time += total_dur

    total_duration = round(current_time, 3)
    cues = subtitle_cues(segments, aspect_ratio="9:16")

    # Audit cues to guarantee zero caption defects on Colab
    cue_audit = audit_cues(cues, aspect_ratio="9:16")
    if cue_audit.get("errors"):
        raise ValueError(f"Subtitle technical defects found: {cue_audit['errors']}")

    # 6. Concatenate & Master
    raw_narration = audio_rev_dir / "narration_raw.wav"
    concat_mono_pcm16_wavs(wav_parts, raw_narration)
    shutil.copy2(raw_narration, narration_wav)
    raw_narration.unlink(missing_ok=True)

    temp_work = audio_rev_dir / "master_work_tmp.wav"
    ap.master(narration_wav, temp_work, {"audio_lufs": target_lufs, "audio_peak_db": target_peak, "audio_voice_chain": voice_chain})

    # 7. Measure loudness with ffmpeg loudnorm
    r_measure = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", str(narration_wav), "-af", "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    m_json: Dict[str, Any] = {}
    try:
        s_idx = r_measure.stderr.rindex("{")
        e_idx = r_measure.stderr.rindex("}") + 1
        m_json = json.loads(r_measure.stderr[s_idx:e_idx])
    except Exception:
        pass

    measured_lufs = float(m_json.get("input_i", target_lufs))
    measured_tp = float(m_json.get("input_tp", target_peak))

    # 8. Write subtitles.srt
    def fmt_time(seconds: float) -> str:
        ms = round(seconds * 1000)
        return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"

    srt_lines = []
    for i, c in enumerate(cues, 1):
        srt_lines.append(f"{i}\n{fmt_time(c['start'])} --> {fmt_time(c['end'])}\n{c['text']}\n")
    subtitles_srt.write_text("\n".join(srt_lines), encoding="utf-8")

    # 9. Build scene metadata
    scenes_meta = []
    for sc in content.get("scenes", []):
        sc_segs = [s for s in segments if s["scene_id"] == sc["id"]]
        if sc_segs:
            scenes_meta.append({
                "id": sc["id"],
                "start": sc_segs[0]["start"],
                "end": sc_segs[-1]["end"],
                "duration": round(sc_segs[-1]["end"] - sc_segs[0]["start"], 3),
            })

    # 10. Write output.json & audio-result.json
    audio_output = {
        "schema_version": "1.0",
        "job_id": job_dir.name,
        "module": "audio",
        "revision": 1,
        "files": [f"revisions/audio/1/{p.name}" for p in audio_rev_dir.glob("*.wav")] + ["revisions/audio/1/subtitles.srt"],
        "payload": {
            "wav": "revisions/audio/1/narration.wav",
            "srt": "revisions/audio/1/subtitles.srt",
            "duration": total_duration,
            "segments": segments,
            "scenes": scenes_meta,
            "cues": cues,
            "measured_lufs": measured_lufs,
            "measured_peak_dbtp": measured_tp,
            "account_used": account_used,
            "engine": "colab-omnivoice",
            "tracks": {
                "vi": {
                    "wav": "revisions/audio/1/narration.wav",
                    "srt": "revisions/audio/1/subtitles.srt",
                    "duration": total_duration,
                    "segments": segments,
                    "cues": cues,
                }
            },
        },
    }
    audio_out_json.write_text(json.dumps(audio_output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (audio_rev_dir / "audio-result.json").write_text(json.dumps(audio_output["payload"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    logger.info(
        f"  [✓] Giai đoạn B hoàn tất: {len(segments)} phân đoạn, thời lượng: {total_duration:.2f}s, "
        f"âm học: {measured_lufs:.2f} LUFS / {measured_tp:.2f} dBTP trên {account_used}"
    )
    return audio_output["payload"], client_used, account_used


def stage_c_render(
    sys_dir: Path,
    job_dir: Path,
    root_dir: Path,
    brief: Dict[str, Any],
    content: Dict[str, Any],
    images_payload: Dict[str, Any],
    audio_payload: Dict[str, Any],
    colab_account: str = "account-01",
    session_name: str = "video-pilot-tts",
) -> Tuple[Path, Optional[Client], Optional[str], Dict[str, Any]]:
    """Execute Stage C: Remote Colab T4 Headless Remotion Render."""
    logger.info(f"[*] GIAI ĐOẠN C: Render video Remotion từ xa trên Colab T4 cho {job_dir.name}...")
    render_dir = job_dir / "revisions/render/1"
    cache_dir = job_dir / "cache/colab-render"
    video_deliv_dir = root_dir / "video" / job_dir.name

    render_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)
    video_deliv_dir.mkdir(parents=True, exist_ok=True)

    def resolve_path(rel_path: str) -> Path:
        p = job_dir / rel_path
        if p.is_file():
            return p
        p2 = job_dir / "revisions" / rel_path
        if p2.is_file():
            return p2
        p3 = sys_dir / rel_path
        if p3.is_file():
            return p3
        raise FileNotFoundError(f"Cannot resolve render asset path: {rel_path}")

    # Build render request
    images_manifest = {"checkpoint": "final", "items": images_payload.get("items", [])}
    request = build_render_request(sys_dir, brief, content, images_manifest, audio_payload, resolve_path)
    (render_dir / "request-colab-render.json").write_text(
        json.dumps(request, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # Configure Colab Client
    base_cfg_path = sys_dir / "config.json"
    cfg: Dict[str, Any] = json.loads(base_cfg_path.read_text(encoding="utf-8")) if base_cfg_path.is_file() else {}
    cfg.setdefault("colab_tts", {})
    cfg["colab_tts"]["session"] = session_name
    cfg["colab_tts"]["_session_explicit"] = True
    cfg["colab_tts"]["render_timeout_seconds"] = 5400

    accounts_to_try: List[str] = [colab_account] + [a for a in CANDIDATE_ACCOUNTS if a != colab_account]
    account_used: Optional[str] = None
    client_used: Optional[Client] = None

    for acc in accounts_to_try:
        logger.info(f"Submitting render request to Colab {acc} ({session_name})...")
        acc_cfg = copy.deepcopy(cfg)
        acc_cfg["colab_tts"]["account"] = acc

        try:
            client = Client(sys_dir, acc_cfg)
            client.account = acc
            client.session = session_name

            try:
                client.reconcile()
            except Exception:
                pass
            try:
                client._ready(auto_start=True)
            except Exception as ex_ready:
                logger.warning(f"Render account {acc} _ready failed: {ex_ready}")

            client.render(request, render_dir, cache_dir / acc)
            account_used = acc
            client_used = client
            logger.info(f"Colab render succeeded on {acc}")
            break
        except (ColabError, Exception) as ex:
            logger.warning(f"Render on {acc} failed ({type(ex).__name__}): {ex}. Failing over...")
            continue

    if not account_used:
        raise RuntimeError(f"All candidate Colab accounts failed for render {job_dir.name}: {accounts_to_try}")

    res_path = render_dir / "render-result.json"
    if not res_path.is_file():
        raise RuntimeError("render-result.json missing after extraction")

    # Locate rendered MP4
    source_mp4 = render_dir / "video_9x16.mp4"
    if not source_mp4.is_file():
        source_mp4 = render_dir / "video.mp4"
    if not source_mp4.is_file():
        raise FileNotFoundError(f"No rendered video file found in {render_dir}")

    # Copy deliverables
    final_mp4 = video_deliv_dir / f"{job_dir.name}.mp4"
    named_mp4 = video_deliv_dir / "video_9x16.mp4"
    shutil.copy2(source_mp4, final_mp4)
    shutil.copy2(source_mp4, named_mp4)

    # Subtitles
    srt_source = render_dir / "subtitles.srt"
    if not srt_source.is_file():
        srt_source = job_dir / "revisions/audio/1/subtitles.srt"
    if srt_source.is_file():
        shutil.copy2(srt_source, video_deliv_dir / f"{job_dir.name}.srt")
        shutil.copy2(srt_source, video_deliv_dir / "subtitles.srt")

    # Thumbnail
    thumb_source = job_dir / "thumbnail_9x16.jpg"
    if not thumb_source.is_file():
        thumb_source = job_dir / "revisions/images/1/THUMBNAIL_9x16.jpg"
    if thumb_source.is_file():
        shutil.copy2(thumb_source, video_deliv_dir / "thumbnail_9x16.jpg")
        shutil.copy2(thumb_source, video_deliv_dir / "cover.jpg")

    # Copy to Orchestrator brain folder for inspection
    orch_dir = Path("/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f")
    if orch_dir.is_dir():
        try:
            shutil.copy2(final_mp4, orch_dir / f"{job_dir.name}.mp4")
            if thumb_source.is_file():
                shutil.copy2(thumb_source, orch_dir / f"{job_dir.name}_thumb.jpg")
            logger.info(f"Copied {job_dir.name}.mp4 and thumbnail to orchestrator brain folder: {orch_dir}")
        except Exception as ex_orch:
            logger.warning(f"Could not copy to orchestrator brain: {ex_orch}")

    # FFprobe validation
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_streams", "-show_format",
        "-of", "json",
        str(final_mp4),
    ]
    probe_data = json.loads(subprocess.check_output(probe_cmd, text=True))
    video_stream = next((s for s in probe_data.get("streams", []) if s.get("codec_type") == "video"), None)
    audio_stream = next((s for s in probe_data.get("streams", []) if s.get("codec_type") == "audio"), None)

    if not video_stream or not audio_stream:
        raise ValueError(f"Missing video or audio stream in rendered file: {final_mp4}")

    width = int(video_stream.get("width", 0))
    height = int(video_stream.get("height", 0))
    v_codec = video_stream.get("codec_name", "")
    a_codec = audio_stream.get("codec_name", "")
    duration = float(probe_data.get("format", {}).get("duration", 0.0))
    fps_raw = video_stream.get("avg_frame_rate", "30/1")
    fps_eval = eval(fps_raw) if "/" in fps_raw else float(fps_raw)
    size_mb = final_mp4.stat().st_size / (1024 * 1024)

    assert width == 1080 and height == 1920, f"Expected 1080x1920, got {width}x{height}"
    assert v_codec in ("h264", "h264_nvenc"), f"Expected h264 video codec, got {v_codec}"
    assert a_codec == "aac", f"Expected aac audio codec, got {a_codec}"
    assert round(fps_eval) == 30, f"Expected 30 fps, got {fps_eval}"

    render_report = {
        "job_id": job_dir.name,
        "video_path": str(final_mp4),
        "resolution": f"{width}x{height}",
        "fps": fps_eval,
        "v_codec": v_codec,
        "a_codec": a_codec,
        "duration": duration,
        "size_mb": size_mb,
        "account_used": account_used,
    }

    # Write output manifest for render module
    output_manifest = {
        "schema_version": "1.0",
        "job_id": job_dir.name,
        "module": "render",
        "revision": 1,
        "input_versions": {
            "content": hashlib.sha256((job_dir / "content.json").read_bytes()).hexdigest(),
            "images": hashlib.sha256((job_dir / "revisions/images/1/output.json").read_bytes()).hexdigest(),
            "audio": hashlib.sha256((job_dir / "revisions/audio/1/output.json").read_bytes()).hexdigest(),
        },
        "payload": {
            "video": f"video/{job_dir.name}/video_9x16.mp4",
            "duration": duration,
            "resolution": f"{width}x{height}",
            "fps": fps_eval,
            "video_codec": v_codec,
            "audio_codec": a_codec,
            "size_mb": size_mb,
            "account_used": account_used,
        },
    }
    (render_dir / "output.json").write_text(json.dumps(output_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    logger.info(f"  [✓] Giai đoạn C hoàn tất: Xuất bản video tại {video_deliv_dir}")
    return final_mp4, client_used, account_used, render_report


def produce_channel_short(
    channel_arg: str,
    job_id_arg: Optional[str] = None,
    colab_account: str = "account-01",
    flow_profiles_arg: Optional[str] = None,
    force_audio: bool = False,
    session_name: str = "video-pilot-tts",
) -> Dict[str, Any]:
    channel_id, channel_slug = resolve_channel_ids(channel_arg)
    job_id = job_id_arg or f"{channel_slug}-week1-9x16"

    # Resolve job_dir and appropriate sys_dir
    candidate_job_dirs = [
        SYS_DIR / "runs" / job_id,
        Path(f"/home/hongphuoc6104/Desktop/vp-channels/channel-{channel_slug}/sys/runs/{job_id}"),
        Path(f"/home/hongphuoc6104/Desktop/vp-agent-core/sys/runs/{job_id}"),
    ]
    job_dir = None
    for cd in candidate_job_dirs:
        if cd.is_dir() and (cd / "content.json").is_file():
            job_dir = cd
            break

    if not job_dir:
        raise FileNotFoundError(f"Could not locate job directory for job '{job_id}' (searched: {candidate_job_dirs})")

    active_sys_dir = job_dir.parents[1] if (job_dir.parents[1] / "config.json").is_file() else SYS_DIR
    active_root_dir = active_sys_dir.parent

    logger.info("=" * 72)
    logger.info(f"  STARTING E2E SHORT PRODUCTION: {job_id}")
    logger.info(f"  Channel: {channel_id} (slug: {channel_slug})")
    logger.info(f"  Job Dir: {job_dir}")
    logger.info(f"  Sys Dir: {active_sys_dir}")
    logger.info("=" * 72)

    brief = json.loads((job_dir / "brief.json").read_text(encoding="utf-8"))
    content = json.loads((job_dir / "content.json").read_text(encoding="utf-8"))

    last_active_client: Optional[Client] = None
    last_active_account: Optional[str] = None

    try:
        # Stage A: Images
        images_output = stage_a_images(
            sys_dir=active_sys_dir,
            job_dir=job_dir,
            channel_id=channel_id,
            brief=brief,
            content=content,
            flow_profiles_arg=flow_profiles_arg,
        )

        # Stage B: Audio
        audio_payload, audio_client, audio_account = stage_b_audio(
            sys_dir=active_sys_dir,
            job_dir=job_dir,
            channel_id=channel_id,
            channel_slug=channel_slug,
            brief=brief,
            content=content,
            colab_account=colab_account,
            session_name=session_name,
            force_audio=force_audio,
        )
        if audio_client:
            last_active_client = audio_client
        if audio_account:
            last_active_account = audio_account

        # Stage C: Remote Render
        final_mp4, render_client, render_account, render_report = stage_c_render(
            sys_dir=active_sys_dir,
            job_dir=job_dir,
            root_dir=active_root_dir,
            brief=brief,
            content=content,
            images_payload=images_output,
            audio_payload=audio_payload,
            colab_account=audio_account or colab_account,
            session_name=session_name,
        )
        if render_client:
            last_active_client = render_client
        if render_account:
            last_active_account = render_account

        summary = {
            "status": "SUCCESS",
            "job_id": job_id,
            "channel": channel_id,
            "deliverables": {
                "mp4": str(final_mp4),
                "srt": str(active_root_dir / "video" / job_id / f"{job_id}.srt"),
                "thumbnail": str(active_root_dir / "video" / job_id / "thumbnail_9x16.jpg"),
            },
            "render": render_report,
            "audio": {
                "duration": audio_payload["duration"],
                "measured_lufs": audio_payload.get("measured_lufs"),
                "measured_peak_dbtp": audio_payload.get("measured_peak_dbtp"),
                "account_used": audio_account,
            },
            "images": {
                "count": len(images_output.get("items", [])),
            },
        }

        print("\n" + "=" * 72)
        print("  E2E PRODUCTION COMPLETE:")
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        print("=" * 72 + "\n")
        return summary

    finally:
        # Strict teardown: stop session so zero idle T4 GPUs leak!
        if last_active_client and last_active_account:
            try:
                logger.info(f"Stopping Colab session '{session_name}' on {last_active_account}...")
                last_active_client.stop()
                logger.info(f"Cleanly released Colab session on {last_active_account}.")
            except Exception as ex_stop:
                logger.warning(f"Failed stopping Colab session on {last_active_account}: {ex_stop}")


def main():
    parser = argparse.ArgumentParser(description="Video Pilot — Universal E2E Short Production Runner")
    parser.add_argument("--channel", required=False, help="Channel identifier or slug (e.g. nao_luoi, tui_tien)")
    parser.add_argument("--job", required=False, help="Job identifier (defaults to <channel_slug>-week1-9x16)")
    parser.add_argument("--colab-account", default="account-01", help="Target Colab account (with automatic failover)")
    parser.add_argument("--flow-profiles", default=None, help="Comma-separated slice of Chrome profiles (e.g. profile_1,profile_2,profile_3)")
    parser.add_argument("--force-audio", action="store_true", help="Force re-synthesis of Stage B audio + Stage C render even if audio exists")
    parser.add_argument("--session", default="video-pilot-tts", help="Colab session name")
    args = parser.parse_args()

    channel = args.channel
    if not channel:
        if ROOT_DIR.name.startswith("channel-"):
            channel = ROOT_DIR.name[len("channel-"):]
        else:
            parser.error("--channel is required when running outside a channel directory")

    produce_channel_short(
        channel_arg=channel,
        job_id_arg=args.job,
        colab_account=args.colab_account,
        flow_profiles_arg=args.flow_profiles,
        force_audio=args.force_audio,
        session_name=args.session,
    )


if __name__ == "__main__":
    main()
