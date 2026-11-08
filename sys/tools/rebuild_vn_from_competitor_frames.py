#!/usr/bin/env python3
"""Rebuild Vietnamese channels from scratch by studying 1-FPS full frames AND second-by-second
spoken dialogue, cadence, pauses, and transitions of real competitor videos.

Workflow per channel:
1. `extract-competitor`: Downloads a real competitor YouTube video (via yt-dlp native HTTP download),
   extracts:
   - `competitor_hook_20s.mp4` (00:00..00:20 hook segment)
   - `competitor_segment_20s.mp4` (20s core explanation segment)
   - `competitor_segment_20s.mp3` (audio stream for multimodal listening)
   - `competitor_acoustic_telemetry.json` (FFmpeg silencedetect pause intervals, speech bursts, cadence ratio)
   - `frame_01s.jpg` .. `frame_20s.jpg` (20 consecutive 1-FPS full frames)
2. Subagent inspects `competitor_segment_20s.mp4`, `competitor_hook_20s.mp4`, `competitor_acoustic_telemetry.json`,
   and all 20 frames via `read_file`, analyzes the exact spoken dialogue structure, sentence pairing,
   rhetorical pivots, acoustic pause durations (`pause_after_sec`), camera movements (`camera_motion`),
   and smooth transitions (`transition`), and writes `<channel>_rebuilt_spec.json`.
3. `validate-specs`: Validates all 20 Vietnamese rebuilt specs against syllable caps (B01 <= 18 syllables),
   pause bounds (0.10s-0.85s), camera/transition enums, forbidden doodle/text artifacts, and banned CTAs.
4. `build-pilot`:
   - Synthesizes per-beat narration via `edge_tts.Communicate(..., boundary="WordBoundary")` with
     exact competitor-modeled breath/dramatic pauses (`pause_after_sec`) between beats, normalized
     to `-11.0 LUFS / -1.0 dBTP` (mapping `VietNarrator` -> `vi-VN-NamMinhNeural`).
   - Builds Vietnamese-standard 1-word alternating Red (`#FF3B30`) & Yellow (`#FFE600`) kinetic
     subtitles (`subtitles_kinetic_9x16.ass`, `Arial Bold 100px`, `Outline=6`, `Shadow=4`, `MarginV=270`)
     for `9:16`, plus clean phrase-level `subtitles.srt` for `16:9` sidecar.
   - Renders `9:16` and `16:9` MP4s with 2x-supersampled sub-pixel `zoompan` camera motion (zero snap!)
     and smooth competitor-matched `xfade` transitions (`smoothleft`, `smoothright`, `smoothup`,
     `smoothdown`, `fade`).
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SYS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = SYS_DIR.parent
BRAIN_DIR = Path("/home/hongphuoc6104/.gemini/antigravity/brain/4b456dc0-d03d-4734-ba17-fa75e7d0a639")
COMP_FRAMES_DIR = BRAIN_DIR / "competitor_frames_vn"
REBUILT_PILOTS_DIR = BRAIN_DIR / "rebuilt_pilots_vn"
REPO_SPECS_DIR = SYS_DIR / "channels/vn_rebuilt_style_specs"

for _p in (str(SYS_DIR), str(SYS_DIR / "tools"), str(ROOT_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tools.rebuild_en_from_competitor_frames import (  # noqa: E402
    VALID_XFADE_TRANSITIONS,
    analyze_acoustic_pauses,
    build_vn_kinetic_1word_ass_and_srt,
    generate_flow_images_for_spec,
    make_channel_watermark,
    render_vn_frame_video,
    synthesize_beats_with_competitor_cadence,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("rebuild_vn_competitor")

COMPETITOR_VN_VIDEO_TARGETS: Dict[str, Dict[str, Any]] = {
    "tui-tien": {
        "channel_id": "tui_tien",
        "channel_slug": "tui-tien",
        "niche": "Tiền và kinh tế đời sống (Consumer Economics & Behavioral Pricing)",
        "competitor_name": "Two Cents PBS / WSJ Consumer Economics / Tài Chính & Kinh Doanh",
        "search_query": "ytsearch1:Two Cents PBS consumer spending pricing grocery traps",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "VietNarrator",
    },
    "banh-rang": {
        "channel_id": "banh_rang",
        "channel_slug": "banh-rang",
        "niche": "Kinh tế vĩ mô, lạm phát & chuỗi cung ứng (Macroeconomics & Industrial Logistics)",
        "competitor_name": "Practical Engineering / Wendover Productions",
        "search_query": "ytsearch1:Wendover Productions container shipping global supply chain",
        "start_sec": 20,
        "duration_sec": 20,
        "voice": "VietNarrator",
    },
    "luat-doi-thuong": {
        "channel_id": "luat_doi_thuong",
        "channel_slug": "luat-doi-thuong",
        "niche": "Pháp luật đời sống & Hợp đồng dân sự (Consumer Law & Civil Rights)",
        "competitor_name": "LegalEagle / CNBC Make It / Luật Sư X",
        "search_query": "ytsearch1:LegalEagle terms of service hidden legal contracts",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "VietNarrator",
    },
    "la-ban-hoc-thuat": {
        "channel_id": "la_ban_hoc_thuat",
        "channel_slug": "la-ban-hoc-thuat",
        "niche": "Mô hình tư duy & Nghịch lý khoa học (Mental Models & Epistemology)",
        "competitor_name": "Veritasium / 3Blue1Brown / Spiderum",
        "search_query": "ytsearch1:Veritasium scientific paradox intuition experiment",
        "start_sec": 20,
        "duration_sec": 20,
        "voice": "VietNarrator",
    },
    "luat-ngam": {
        "channel_id": "luat_ngam",
        "channel_slug": "luat-ngam",
        "niche": "Tâm lý học đám đông & Góc khuất thao túng (Mass Psychology & Manipulation)",
        "competitor_name": "Fern TV / Academy of Ideas / CDTeam",
        "search_query": "ytsearch1:Fern TV mass psychology manipulation behavior",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "VietNarrator",
    },
    "ua-sao-vay": {
        "channel_id": "ua_sao_vay",
        "channel_slug": "ua-sao-vay",
        "niche": "Nghịch lý khoa học & Hiện tượng đời thường (Curiosity & Everyday Science)",
        "competitor_name": "Veritasium / Zack D. Films",
        "search_query": "ytsearch1:Zack D. Films why does human body react blink",
        "start_sec": 10,
        "duration_sec": 20,
        "voice": "VietNarrator",
    },
    "dia-com": {
        "channel_id": "dia_com",
        "channel_slug": "dia-com",
        "niche": "Khoa học ẩm thực & Hóa học phản ứng nhiệt (Culinary Science & Food Physics)",
        "competitor_name": "America's Test Kitchen / Modernist Cuisine",
        "search_query": "ytsearch1:Americas Test Kitchen science of cooking Maillard reaction",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "VietNarrator",
    },
    "vu-tru-ti-hon": {
        "channel_id": "vu_tru_ti_hon",
        "channel_slug": "vu-tru-ti-hon",
        "niche": "Vật lý thiên văn & Không gian sâu (Astrophysics & Deep Space)",
        "competitor_name": "Melodysheep / Astrum",
        "search_query": "ytsearch1:Melodysheep space planets deep universe voyage",
        "start_sec": 20,
        "duration_sec": 20,
        "voice": "VietNarrator",
    },
    "chanh-niem-ke": {
        "channel_id": "chanh_niem_ke",
        "channel_slug": "chanh-niem-ke",
        "niche": "Tâm lý trị liệu & Chánh niệm (Mindfulness & Emotional Balance)",
        "competitor_name": "Pursuit of Wonder / Aperture",
        "search_query": "ytsearch1:Pursuit of Wonder mindfulness peace solitude anxiety",
        "start_sec": 20,
        "duration_sec": 20,
        "voice": "VietNarrator",
    },
    "minh-triet-song": {
        "channel_id": "minh_triet_song",
        "channel_slug": "minh-triet-song",
        "niche": "Triết học thực hành & Khắc kỷ (Stoicism & Applied Wisdom)",
        "competitor_name": "Einzelgänger / Daily Stoic",
        "search_query": "ytsearch1:Einzelganger stoicism Marcus Aurelius control emotions",
        "start_sec": 20,
        "duration_sec": 20,
        "voice": "VietNarrator",
    },
    "co-the-ke": {
        "channel_id": "co_the_ke",
        "channel_slug": "co-the-ke",
        "niche": "Sinh lý học y khoa & Cơ thể 3D (Medical Physiology & Human Body 3D)",
        "competitor_name": "Nucleus Medical Media / Zack D. Films",
        "search_query": "ytsearch1:Nucleus Medical Media 3D digestive system human body",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "VietNarrator",
    },
    "su-ke-lai": {
        "channel_id": "su_ke_lai",
        "channel_slug": "su-ke-lai",
        "niche": "Lịch sử quân sự & Chiến thuật cổ đại (Military History & Geopolitics)",
        "competitor_name": "Kings and Generals / Epic History TV / Fern",
        "search_query": "ytsearch1:Kings and Generals ancient tactical battle documentary",
        "start_sec": 25,
        "duration_sec": 20,
        "voice": "VietNarrator",
    },
    "ho-so-ky-la": {
        "channel_id": "ho_so_ky_la",
        "channel_slug": "ho-so-ky-la",
        "niche": "Hồ sơ trinh thám & Kỳ án chưa lời giải (Forensic Mysteries & Unsolved Archives)",
        "competitor_name": "LEMMiNO / Fern",
        "search_query": "ytsearch1:LEMMiNO mystery investigative crime archival documentary",
        "start_sec": 25,
        "duration_sec": 20,
        "voice": "VietNarrator",
    },
    "ban-do-quyen-luc": {
        "channel_id": "ban_do_quyen_luc",
        "channel_slug": "ban-do-quyen-luc",
        "niche": "Địa chính trị & Điểm nghẽn chiến lược (Geopolitics & Strategic Chokepoints)",
        "competitor_name": "RealLifeLore / Johnny Harris",
        "search_query": "ytsearch1:RealLifeLore strategic maritime chokepoints geopolitical maps",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "VietNarrator",
    },
    "loi-sang-soi": {
        "channel_id": "loi_sang_soi",
        "channel_slug": "loi-sang-soi",
        "niche": "Biểu tượng thần thoại & Triết học cổ điển (Mythology & Ancient Metaphors)",
        "competitor_name": "BibleProject / Caravaggio Chiaroscuro",
        "search_query": "ytsearch1:BibleProject ancient visual parables narrative wisdom",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "VietNarrator",
    },
    "nao-luoi": {
        "channel_id": "nao_luoi",
        "channel_slug": "nao-luoi",
        "niche": "Khoa học thần kinh, dopamine & thói quen (Neuroscience & Behavioral Habits)",
        "competitor_name": "Kurzgesagt Habit Science / Huberman Lab / The Paint Explainer",
        "search_query": "ytsearch1:Kurzgesagt habit dopamine neuroplasticity procrastination",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "VietNarrator",
    },
    "thuong-cho-kheo": {
        "channel_id": "thuong_cho_kheo",
        "channel_slug": "thuong-cho-kheo",
        "niche": "Tâm lý học gắn bó & Giao tiếp cảm xúc (Attachment Psychology & Relationships)",
        "competitor_name": "The School of Life / Cinema Therapy",
        "search_query": "ytsearch1:The School of Life relationships emotional communication attachment",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "VietNarrator",
    },
    "nghe-song-sot": {
        "channel_id": "nghe_song_sot",
        "channel_slug": "nghe-song-sot",
        "niche": "Chiến lược công sở, đàm phán & thăng tiến (Workplace Strategy & Career Leverage)",
        "competitor_name": "Wall Street Journal / Harvard Business Review / Casgains",
        "search_query": "ytsearch1:Wall Street Journal executive career salary negotiation leverage",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "VietNarrator",
    },
    "ai-binh-dan": {
        "channel_id": "ai_binh_dan",
        "channel_slug": "ai-binh-dan",
        "niche": "Ứng dụng AI thực tế & Tối ưu năng suất (Applied AI & Workflow Automation)",
        "competitor_name": "Jeff Su / Fireship / Matt Wolfe",
        "search_query": "ytsearch1:Jeff Su practical AI automation productivity workflow tutorial",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "VietNarrator",
    },
    "tam-tinh-dem": {
        "channel_id": "tam_tinh_dem",
        "channel_slug": "tam-tinh-dem",
        "niche": "Tản văn đêm muộn & Giấc ngủ bình yên (Midnight Solitude & Sleep Fables)",
        "competitor_name": "Pursuit of Wonder / Studio Ghibli Nocturnal",
        "search_query": "ytsearch1:Pursuit of Wonder peaceful night bedtime contemplation essay",
        "start_sec": 20,
        "duration_sec": 20,
        "voice": "VietNarrator",
    },
}

VALID_CAMERAS = {
    "push_in",
    "pan_right",
    "pan_left",
    "tilt_up",
    "tilt_down",
    "zoom_out",
    "orbit_right",
    "orbit_left",
    "static_hold",
}

BANNED_CTAS = {
    "like",
    "share",
    "subscribe",
    "đăng ký",
    "bấm like",
    "chia sẻ",
    "bấm theo dõi",
    "hãy theo dõi",
    "nhớ like",
}

FORBIDDEN_POSITIVE_PROMPT_PATTERNS = [
    re.compile(r"(?<!no\s)(?<!zero\s)\b(?:stickman|stickmen|stick-man)\b", re.I),
    re.compile(r"(?<!no\s)(?<!zero\s)\b(?:kawaii|chibi)\b", re.I),
    re.compile(r"(?<!no\s)(?<!zero\s)\b(?:chalkboard|blackboard)\b", re.I),
    re.compile(r"(?<!no\s)(?<!zero\s)\b(?:doodle|hand-drawn doodle)\b", re.I),
]


def resolve_voice_for_tts(voice: str) -> str:
    """Map canonical voice to high-fidelity neural voice identity, preserving Studio V3 channel profiles."""
    v = (voice or "").strip()
    if not v:
        return "VietNarrator"
    # Never collapse channel-specific Studio V3 voices to generic voices
    return v


def count_vietnamese_syllables(text: str) -> int:
    """Accurate syllable counter for Vietnamese spoken narration."""
    clean = re.sub(r"[*_`#~]", "", text or "")
    clean = re.sub(r"[\u2014\u2013—–-]", " ", clean).replace("/", " ")
    tokens = [tok.strip(".,;:?!'\"()[]") for tok in clean.split() if tok.strip(".,;:?!'\"()[]")]
    return len(tokens)


def validate_spec_data(spec_data: Dict[str, Any], file_path: Optional[Path] = None) -> List[str]:
    """Validate a single Vietnamese rebuilt spec dictionary against all SSOT rules."""
    violations: List[str] = []
    slug = spec_data.get("channel_slug") or (file_path.parent.name if file_path else "unknown")

    # 1. Required top-level fields
    for field in (
        "channel_id",
        "channel_slug",
        "competitor_name",
        "voice",
        "competitor_dialogue_formula",
        "beats",
    ):
        if field not in spec_data:
            violations.append(f"[{slug}] Missing required top-level field '{field}'")

    # 2. Formula verification
    formula = spec_data.get("competitor_dialogue_formula", {})
    if not isinstance(formula, dict):
        violations.append(f"[{slug}] 'competitor_dialogue_formula' must be an object")
    else:
        for f_field in (
            "competitor_verbatim_transcript_20s",
            "sentence_structure_formula_vi",
            "pause_and_cadence_formula_vi",
            "transition_and_camera_formula_vi",
        ):
            if not formula.get(f_field):
                violations.append(f"[{slug}] Formula missing '{f_field}'")

    # 3. Beats structure: exactly 8 beats
    beats = spec_data.get("beats", [])
    if not isinstance(beats, list) or len(beats) != 8:
        violations.append(f"[{slug}] Expected exactly 8 beats, found {len(beats) if isinstance(beats, list) else 0}")
        return violations

    # 4. Opening Hook syllable cap: B01 <= 18 syllables
    b01 = beats[0]
    b01_narr = str(b01.get("narration", "")).strip()
    b01_syl = count_vietnamese_syllables(b01_narr)
    if b01_syl > 18:
        violations.append(f"[{slug}] Hook Beat B01 exceeds 18 syllables ({b01_syl} syllables): '{b01_narr}'")

    # 5. Beat-level checks
    for idx, beat in enumerate(beats, 1):
        bid = beat.get("beat_id") or f"B{idx:02d}"

        # Formula stage
        if not beat.get("formula_stage"):
            violations.append(f"[{slug}] {bid} missing 'formula_stage'")

        # Pause duration: [0.10s, 0.85s]
        p_val = beat.get("pause_after_sec")
        if p_val is None:
            violations.append(f"[{slug}] {bid} missing 'pause_after_sec'")
        else:
            try:
                p_float = float(p_val)
                if not (0.10 <= p_float <= 0.85):
                    violations.append(f"[{slug}] {bid} pause_after_sec {p_float} outside allowed bounds [0.10, 0.85]")
            except (ValueError, TypeError):
                violations.append(f"[{slug}] {bid} pause_after_sec {p_val!r} is not a valid number")

        # Camera motion enum
        cam = str(beat.get("camera_motion", "")).strip()
        if cam not in VALID_CAMERAS:
            violations.append(f"[{slug}] {bid} camera_motion '{cam}' not in VALID_CAMERAS: {sorted(VALID_CAMERAS)}")

        # Transition enum
        trans = str(beat.get("transition", "")).strip()
        if trans not in VALID_XFADE_TRANSITIONS:
            violations.append(
                f"[{slug}] {bid} transition '{trans}' not in VALID_XFADE_TRANSITIONS: {sorted(VALID_XFADE_TRANSITIONS)}"
            )

        # Narration banned CTAs
        narr = str(beat.get("narration", "")).lower()
        for cta in BANNED_CTAS:
            if re.search(r"\b" + re.escape(cta) + r"\b", narr):
                violations.append(f"[{slug}] {bid} narration contains banned CTA '{cta}': '{narr}'")

        # Prompt forbidden doodle/text artifacts
        prompt = str(beat.get("prompt", ""))
        for pat in FORBIDDEN_POSITIVE_PROMPT_PATTERNS:
            m = pat.search(prompt)
            if m:
                violations.append(f"[{slug}] {bid} prompt contains forbidden positive style artifact: '{m.group(0)}'")

    return violations


def validate_all_vn_specs(target_slug: Optional[str] = None) -> Tuple[bool, List[str]]:
    """Validate all 20 Vietnamese rebuilt style specs, returning (is_valid, all_violations)."""
    if target_slug:
        slugs = [target_slug.strip().replace("_", "-")]
    else:
        slugs = sorted(COMPETITOR_VN_VIDEO_TARGETS.keys())

    all_violations: List[str] = []
    checked_count = 0

    for slug in slugs:
        spec_path = REPO_SPECS_DIR / slug / f"{slug}_rebuilt_spec.json"
        if not spec_path.is_file():
            all_violations.append(f"Missing spec file for {slug}: {spec_path}")
            continue

        try:
            data = json.loads(spec_path.read_text(encoding="utf-8"))
        except Exception as exc:
            all_violations.append(f"JSON decode error in {spec_path}: {exc}")
            continue

        violations = validate_spec_data(data, file_path=spec_path)
        all_violations.extend(violations)
        checked_count += 1

    return (len(all_violations) == 0, all_violations)


def extract_vn_competitor_frames(
    channel_slug: str,
    custom_query: Optional[str] = None,
    start_sec: Optional[int] = None,
    duration_sec: int = 20,
) -> Dict[str, Any]:
    """Download competitor video, extract 20s hook + 20s body MP4/MP3, acoustic pause telemetry, and 1-FPS frames."""
    target = COMPETITOR_VN_VIDEO_TARGETS.get(channel_slug)
    if not target and not custom_query:
        raise ValueError(f"Unknown channel slug '{channel_slug}' and no --query provided.")

    query = custom_query or target["search_query"]
    s_sec = start_sec if start_sec is not None else int(target.get("start_sec", 15))
    d_sec = duration_sec or int(target.get("duration_sec", 20))

    out_dir = COMP_FRAMES_DIR / channel_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_mp4 = out_dir / "competitor_source.mp4"
    clip_mp4 = out_dir / "competitor_segment_20s.mp4"
    clip_mp3 = out_dir / "competitor_segment_20s.mp3"
    hook_mp4 = out_dir / "competitor_hook_20s.mp4"

    if not raw_mp4.is_file() or raw_mp4.stat().st_size < 50_000:
        logger.info(f"[{channel_slug}] Downloading competitor reference via '{query}'...")
        cmd_dl = [
            "yt-dlp",
            "--no-playlist",
            "-f",
            "18/best[ext=mp4][height<=720]/best[ext=mp4]",
            "--write-info-json",
            "-o",
            str(raw_mp4),
            query,
        ]
        subprocess.run(cmd_dl, check=True, timeout=180)

    # Extract 20-second core reference clip locally
    if not clip_mp4.is_file() or clip_mp4.stat().st_size < 20_000 or start_sec is not None:
        cmd_clip = [
            "ffmpeg",
            "-y",
            "-ss",
            str(s_sec),
            "-t",
            str(d_sec),
            "-i",
            str(raw_mp4),
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "20",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            str(clip_mp4),
        ]
        subprocess.run(cmd_clip, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # Extract 20-second opening Hook clip (00:00..00:20) to study hook formula
    if not hook_mp4.is_file() or hook_mp4.stat().st_size < 20_000:
        cmd_hook = [
            "ffmpeg",
            "-y",
            "-ss",
            "0",
            "-t",
            "20",
            "-i",
            str(raw_mp4),
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "20",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            str(hook_mp4),
        ]
        subprocess.run(cmd_hook, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # Extract MP3 for listening
    if not clip_mp3.is_file() or clip_mp3.stat().st_size < 5_000:
        cmd_mp3 = ["ffmpeg", "-y", "-i", str(clip_mp4), "-vn", "-c:a", "libmp3lame", "-q:a", "2", str(clip_mp3)]
        subprocess.run(cmd_mp3, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # Acoustic pause detection
    acoustic_meta = analyze_acoustic_pauses(clip_mp4, total_dur=d_sec)
    (out_dir / "competitor_acoustic_telemetry.json").write_text(
        json.dumps(acoustic_meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Extract exactly 20 1-FPS full frames
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    existing_frames = sorted(frames_dir.glob("frame_*.jpg"))
    if len(existing_frames) < 20:
        cmd_fps = [
            "ffmpeg",
            "-y",
            "-i",
            str(clip_mp4),
            "-vf",
            "fps=1",
            "-q:v",
            "2",
            str(frames_dir / "frame_%02ds.jpg"),
        ]
        subprocess.run(cmd_fps, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    frames = sorted(str(p) for p in frames_dir.glob("frame_*.jpg"))
    res = {
        "channel_slug": channel_slug,
        "competitor_name": target.get("competitor_name") if target else "Custom",
        "segment_mp4": str(clip_mp4),
        "hook_mp4": str(hook_mp4),
        "segment_mp3": str(clip_mp3),
        "acoustic_telemetry": acoustic_meta,
        "frames_extracted": len(frames),
        "frames": frames[:20],
    }
    return res


def build_vn_pilot_from_spec(
    spec_path: Path,
    profile_names: Optional[List[str]] = None,
    max_workers: int = 4,
    force_images: bool = False,
    both_native: bool = False,
) -> Dict[str, Any]:
    """Execute full Vietnamese pilot build (Audio + 1-Word Red/Yellow ASS + Flow images + 9:16 & 16:9 MP4s)."""
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    channel_slug = spec["channel_slug"]
    target_cfg = COMPETITOR_VN_VIDEO_TARGETS.get(channel_slug, {})
    raw_voice = spec.get("voice") or target_cfg.get("voice", "VietNarrator")
    voice = resolve_voice_for_tts(raw_voice)
    beats = spec["beats"]

    pilot_dir = REBUILT_PILOTS_DIR / channel_slug
    pilot_dir.mkdir(parents=True, exist_ok=True)
    img_dir = pilot_dir / "images"
    audio_dir = pilot_dir / "audio"

    # Keep artifact copy and repo copy synchronized
    artifact_spec_p = pilot_dir / f"{channel_slug}_rebuilt_spec.json"
    if spec_path.resolve() != artifact_spec_p.resolve():
        shutil.copy2(spec_path, artifact_spec_p)
    repo_spec_dir = REPO_SPECS_DIR / channel_slug
    repo_spec_dir.mkdir(parents=True, exist_ok=True)
    repo_spec_p = repo_spec_dir / f"{channel_slug}_rebuilt_spec.json"
    if spec_path.resolve() != repo_spec_p.resolve():
        shutil.copy2(spec_path, repo_spec_p)

    # 1. Per-beat audio synthesis with competitor pauses & WordBoundary alignment
    norm_wav, total_dur, beat_durations, global_words = synthesize_beats_with_competitor_cadence(
        beats=beats,
        voice=voice,
        audio_dir=audio_dir,
    )
    ass_path = audio_dir / "subtitles_kinetic_9x16.ass"
    srt_path = audio_dir / "subtitles.srt"
    build_vn_kinetic_1word_ass_and_srt(
        beats=beats,
        beat_durations=beat_durations,
        global_words=global_words,
        total_dur=total_dur,
        ass_path=ass_path,
        srt_path=srt_path,
        margin_v=270,
    )

    # 2. Flow CDP image generation (9:16 and 16:9)
    images_map = generate_flow_images_for_spec(
        channel_slug=channel_slug,
        beats=beats,
        img_dir=img_dir,
        profile_names=profile_names,
        max_workers=max_workers,
        force_regenerate=force_images,
        both_native=both_native,
    )

    if len(images_map["9x16"]) < len(beats) or len(images_map["16x9"]) < len(beats):
        raise RuntimeError(
            f"[{channel_slug}] Incomplete Flow image generation: "
            f"9x16={len(images_map['9x16'])}/{len(beats)}, 16x9={len(images_map['16x9'])}/{len(beats)}"
        )

    # 3. Watermark icon
    wm_png = pilot_dir / "watermark_100px.png"
    make_channel_watermark(channel_slug=channel_slug, out_png=wm_png, size=100)

    # 4. Render 9:16 MP4
    mp4_9x16 = pilot_dir / f"{channel_slug}_pilot_9x16.mp4"
    render_vn_frame_video(
        frames=images_map["9x16"],
        beats=beats,
        beat_durations=beat_durations,
        audio_path=norm_wav,
        ass_path=ass_path,
        srt_path=srt_path,
        watermark_png=wm_png,
        out_mp4=mp4_9x16,
        aspect="9:16",
    )

    # 5. Render 16:9 MP4
    mp4_16x9 = pilot_dir / f"{channel_slug}_pilot_16x9.mp4"
    render_vn_frame_video(
        frames=images_map["16x9"],
        beats=beats,
        beat_durations=beat_durations,
        audio_path=norm_wav,
        ass_path=ass_path,
        srt_path=srt_path,
        watermark_png=wm_png,
        out_mp4=mp4_16x9,
        aspect="16:9",
    )

    # 6. Publish canonical outputs to video/<slug>/
    vid_short_dir = ROOT_DIR / "video" / f"{channel_slug}-short"
    vid_long_dir = ROOT_DIR / "video" / f"{channel_slug}-long"
    vid_short_dir.mkdir(parents=True, exist_ok=True)
    vid_long_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(mp4_9x16, vid_short_dir / f"{channel_slug}-test-20s-9x16.mp4")
    shutil.copy2(srt_path, vid_short_dir / f"{channel_slug}-test-20s-9x16.srt")
    shutil.copy2(ass_path, vid_short_dir / "subtitles_kinetic_9x16.ass")
    shutil.copy2(mp4_16x9, vid_long_dir / f"{channel_slug}-pilot-16x9.mp4")
    shutil.copy2(srt_path, vid_long_dir / f"{channel_slug}-pilot-16x9.srt")

    # 7. Extract 1-FPS verification frames from rendered 9:16 pilot
    verify_dir = pilot_dir / "rendered_frames_9x16"
    verify_dir.mkdir(parents=True, exist_ok=True)
    for old_vf in verify_dir.glob("pilot_frame_*s.jpg"):
        old_vf.unlink()
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(mp4_9x16),
            "-vf",
            "fps=1",
            "-q:v",
            "2",
            str(verify_dir / "pilot_frame_%02ds.jpg"),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    report = {
        "channel_slug": channel_slug,
        "status": "SUCCESS",
        "duration_sec": round(total_dur, 2),
        "beats_count": len(beats),
        "words_count": len(global_words),
        "beat_durations_sec": beat_durations,
        "subtitle_style_9x16": "VN_KINETIC_1WORD_RED_YELLOW_ASS (Arial 100px, #FF3B30 / #FFE600, Outline=6, MarginV=270)",
        "transition_engine": "2x_supersampled_zoompan_plus_xfade",
        "mp4_9x16": str(mp4_9x16),
        "mp4_16x9": str(mp4_16x9),
        "canonical_short_mp4": str(vid_short_dir / f"{channel_slug}-test-20s-9x16.mp4"),
        "canonical_long_mp4": str(vid_long_dir / f"{channel_slug}-pilot-16x9.mp4"),
        "rendered_frames_dir": str(verify_dir),
    }
    (pilot_dir / "pilot_build_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    shutil.copy2(pilot_dir / "pilot_build_report.json", repo_spec_dir / "pilot_build_report.json")
    logger.info(f"[✓] [{channel_slug}] Built 9:16 & 16:9 Pilot Videos ({total_dur:.2f}s) -> {mp4_9x16}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Competitor 1-FPS frame + dialogue cadence extractor & VN-frame pilot rebuilder for 20 VN channels."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # 1. list
    sub.add_parser("list", help="List all 20 Vietnamese channels and competitor targets")

    # 2. validate-specs
    p_val = sub.add_parser("validate-specs", help="Validate all 20 Vietnamese rebuilt style specs")
    p_val.add_argument("--slug", default=None, help="Optional single channel slug to validate")

    # 3. extract-competitor
    p_ext = sub.add_parser(
        "extract-competitor", help="Extract competitor hook/body MP4, MP3, acoustic pauses & 20 frames"
    )
    p_ext.add_argument("--channel", required=True, help="Channel slug, e.g. tui-tien")
    p_ext.add_argument("--query", default=None, help="Optional custom yt-dlp search query or URL")
    p_ext.add_argument("--start-sec", type=int, default=None, help="Start second in competitor video")
    p_ext.add_argument("--duration-sec", type=int, default=20, help="Duration in seconds (default: 20)")

    # 4. build-pilot
    p_bld = sub.add_parser("build-pilot", help="Build 9:16 & 16:9 pilot videos from rebuilt spec JSON")
    p_bld.add_argument("--spec", required=True, help="Path to <channel>_rebuilt_spec.json")
    p_bld.add_argument("--profiles", default=None, help="Comma-separated Flow profile names")
    p_bld.add_argument("--workers", type=int, default=4, help="Max concurrent Flow workers")
    p_bld.add_argument("--force-images", action="store_true", help="Force regenerate Flow images")

    args = parser.parse_args()

    if args.cmd == "list":
        print(f"{'#':<3} | {'Slug':<18} | {'Competitor Benchmark':<45} | {'Voice':<14} | Niche")
        print("-" * 120)
        for idx, (slug, tgt) in enumerate(COMPETITOR_VN_VIDEO_TARGETS.items(), 1):
            print(
                f"{idx:<3} | {slug:<18} | {tgt['competitor_name'][:43]:<45} | {tgt.get('voice', 'VietNarrator'):<14} | {tgt['niche']}"
            )
        sys.exit(0)

    elif args.cmd == "validate-specs":
        is_valid, violations = validate_all_vn_specs(target_slug=args.slug)
        if is_valid:
            target_str = f"'{args.slug}'" if args.slug else "all 20 Vietnamese channels"
            print(f"[✓] Specification validation PASSED for {target_str}. (0 violations)")
            sys.exit(0)
        else:
            print(f"[✗] Specification validation FAILED with {len(violations)} violations:")
            for v in violations:
                print(f"  - {v}")
            sys.exit(1)

    elif args.cmd == "extract-competitor":
        res = extract_vn_competitor_frames(
            channel_slug=args.channel,
            custom_query=args.query,
            start_sec=args.start_sec,
            duration_sec=args.duration_sec,
        )
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.cmd == "build-pilot":
        profs = [x.strip() for x in args.profiles.split(",") if x.strip()] if args.profiles else None
        res = build_vn_pilot_from_spec(
            spec_path=Path(args.spec),
            profile_names=profs,
            max_workers=args.workers,
            force_images=args.force_images,
        )
        print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
