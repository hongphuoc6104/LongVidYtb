"""Chronicle Documentary Audio Engine for `chanh_niem_ke` (@ChanhNiemKeVN).

Replicates the `@SuDehieukhongphainho` audio architecture while enforcing the
Video Pilot `-11.0 LUFS / -1.0 dBTP` loudness contract:
1. Pre-TTS Pronunciation Normalizer (`normalize_chronicle_tts_text`,
   `prepare_chronicle_tts_beats`): prevents Sino-Vietnamese compound splits
   (e.g. "ngư — lôi"), transliterates disaster/nuclear/geographic terms
   (Chernobyl -> Chéc-nô-bưn, Pripyat -> Pri-pi-át, RBMK -> Rờ-Bê-Mờ-Ca,
   AZ-5 -> A-Zét Năm, Sievert -> Xi-vơ), formats dates/timestamps, and softens
   approximations with "khoảng".
2. Variable Pause Assembler (`resolve_beat_pause_sec`,
   `assemble_variable_pause_narration`, `measure_narration_cadence`): stitches
   per-beat WAVs using per-beat `pause_after_s` (`0.48-0.75s` breath,
   `0.90-1.35s` emphasis, `2.50-4.80s` at `[SFX:...]` / chapter transitions
   every ~45-50s) and calibrates cadence toward `226-232 syllables/min`.
3. Sparse Realistic Foley SFX & Documentary BGM Generator (`synth_chronicle_sfx`,
   `generate_documentary_bgm`): procedural 48kHz stereo disaster/chronicle SFX
   (`geiger_counter_burst`, `steam_reactor_explosion`, `control_room_siren`,
   `sub_bass_chapter_boom`, `stamp_slam_thud`, `fire_crackle`,
   `telegraph_ticker`) + continuous Documentary Tension Strings/Pulse BGM and
   Emotional Piano Outro BGM.
4. Mixdown & Mastering (`mix_chronicle_audio`): `-20 dB` speech ducking with
   `+10 dB` chapter-pause swell, sparse SFX placement only on explicit cues,
   and 2-pass EBU R128 mastering (`-11.0 LUFS / -1.0 dBTP`).
"""
from __future__ import annotations

import math
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
from scipy.ndimage import uniform_filter1d

SYS_DIR = Path(__file__).resolve().parent.parent
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from tools.vn_text_normalizer import normalize_for_tts, num_to_vn_words  # noqa: E402

from .audio_sfx_bgm import SFX_DIR  # noqa: E402
from .audio_suspense_v2 import (  # noqa: E402
    FPS,
    TARGET_SR,
    _bandpass,
    _edge_fade,
    _ensure_stereo,
    _lowpass,
    _read_wav_stereo,
    _write_wav_stereo,
    compute_voice_envelope_30fps,
    encode_calibrated_m4a_stereo,
    master_2pass_wav_stereo,
    place_stereo_sfx,
)

MASTER_TARGET_LUFS = -11.0
MASTER_MAX_TP_DB = -1.0
PRE_AAC_TP_DB = -1.4
TARGET_CADENCE_RANGE = (226.0, 232.0)
TARGET_OUTRO_CADENCE_RANGE = (250.0, 256.0)
TARGET_F0_MEDIAN_HZ = 148.0

PAUSE_TIERS: dict[str, tuple[float, float, float]] = {
    "micro_breath": (0.28, 0.42, 0.34),
    "breath": (0.48, 0.75, 0.58),
    "emphasis": (0.65, 1.35, 0.90),
    "sfx_chapter": (2.50, 3.80, 2.80),
}

SFX_TAG_RE = re.compile(r"\[SFX:\s*([A-Za-z0-9_.\-]+)\s*\]", re.IGNORECASE)
PAUSE_CUE_RE = re.compile(r"\[(?:PAUSE|SFX_PAUSE)(?::\s*([0-9.]+)\s*(ms|s)?)?\s*\]", re.IGNORECASE)

# Sino-Vietnamese & technical compounds vulnerable to TTS dash/comma token splitting.
COMPOUND_WORD_PAIRS: tuple[tuple[str, str], ...] = (
    ("ngư", "lôi"),
    ("hạt", "nhân"),
    ("phóng", "xạ"),
    ("phản", "ứng"),
    ("nhiệt", "điện"),
    ("thủy", "điện"),
    ("tuần", "hoàn"),
    ("điều", "khiển"),
    ("cảnh", "báo"),
    ("khẩn", "cấp"),
    ("bức", "xạ"),
    ("nhiễm", "xạ"),
    ("ô", "nhiễm"),
    ("sơ", "tán"),
    ("cứu", "hộ"),
    ("niêm", "phong"),
    ("bê", "tông"),
    ("quân", "sự"),
    ("địa", "chấn"),
    ("sóng", "thần"),
    ("nội", "chiến"),
    ("đồng", "minh"),
    ("hiệp", "ước"),
    ("chiến", "tranh"),
    ("động", "viên"),
    ("lạm", "phát"),
    ("tên", "lửa"),
    ("tàu", "ngầm"),
    ("chiến", "hạm"),
    ("tua", "bin"),
    ("nhà", "máy"),
    ("lò", "hơi"),
    ("nhiên", "liệu"),
    ("làm", "mát"),
    ("than", "chì"),
    ("bồi", "thường"),
    ("tiền", "tệ"),
    ("an", "toàn"),
    ("thảm", "họa"),
    ("kỹ", "thuật"),
)

# Foreign technical, disaster, and geographical names mapped to clean northern Vietnamese phonetics.
CHRONICLE_PRONUNCIATION_MAP: dict[str, str] = {
    r"\bChernobyl\b": "Chéc-nô-bưn",
    r"\bChornobyl\b": "Chéc-nô-bưn",
    r"\bPripyat\b": "Pri-pi-át",
    r"\bRBMK-1000\b": "Rờ-Bê-Mờ-Ca một nghìn",
    r"\bRBMK\b": "Rờ-Bê-Mờ-Ca",
    r"\bAZ-5\b": "A-Zét Năm",
    r"\bAZ5\b": "A-Zét Năm",
    r"\bSieverts?\b": "Xi-vơ",
    r"\bmSv\b": "mi-li Xi-vơ",
    r"(?:μ|u)Sv\b": "mi-crô Xi-vơ",
    r"\bSv\b": "Xi-vơ",
    r"\bRoentgens?\b": "Rơn-gen",
    r"\bRöntgens?\b": "Rơn-gen",
    r"\bBecquerels?\b": "Béc-cơ-ren",
    r"\bBq\b": "Béc-cơ-ren",
    r"\bAnatoly Dyatlov\b": "A-na-tô-li Đi-át-lốp",
    r"\bDyatlov\b": "Đi-át-lốp",
    r"\bValery Legasov\b": "Va-le-ri Lê-ga-xốp",
    r"\bLegasov\b": "Lê-ga-xốp",
    r"\bBoris Shcherbina\b": "Bô-rít Sơ-bi-na",
    r"\bShcherbina\b": "Sơ-bi-na",
    r"\bMikhail Gorbachev\b": "Mi-kha-in Goóc-ba-chốp",
    r"\bGorbachev\b": "Goóc-ba-chốp",
    r"\bAleksandr Akimov\b": "A-lếch-xan-đơ A-ki-mốp",
    r"\bAlexander Akimov\b": "A-lếch-xan-đơ A-ki-mốp",
    r"\bAkimov\b": "A-ki-mốp",
    r"\bLeonid Toptunov\b": "Lê-ô-nít Tốp-tu-nốp",
    r"\bToptunov\b": "Tốp-tu-nốp",
    r"\bAlexei Ananenko\b": "A-lếch-xây A-na-nen-cô",
    r"\bAnanenko\b": "A-na-nen-cô",
    r"\bValeri Bezpalov\b": "Va-lê-ri Bét-pa-lốp",
    r"\bBezpalov\b": "Bét-pa-lốp",
    r"\bBoris Baranov\b": "Bô-rít Ba-ra-nốp",
    r"\bBaranov\b": "Ba-ra-nốp",
    r"\bViktor Bryukhanov\b": "Vích-to Bri-u-kha-nốp",
    r"\bBryukhanov\b": "Bri-u-kha-nốp",
    r"\bNikolai Fomin\b": "Ni-cô-lai Phô-min",
    r"\bFomin\b": "Phô-min",
    r"\bUkraine\b": "U-crai-na",
    r"\bBelarus\b": "Bê-la-rút",
    r"\bBaltic\b": "Ban-tích",
    r"\bLithuania\b": "Lít-va",
    r"\bLitva\b": "Lít-va",
    r"\bLeningrad\b": "Lê-nin-grát",
    r"\bKursk\b": "Cuốc-xcơ",
    r"\bDnieper\b": "Đờ-ni-ép",
    r"\bKiev\b": "Ki-ép",
    r"\bKyiv\b": "Ki-ép",
    r"\bMoscow\b": "Mát-xcơ-va",
    r"\bMatxcơva\b": "Mát-xcơ-va",
    r"\bForsmark\b": "Phoóc-mác",
    r"\bSweden\b": "Thụy Điển",
    r"\bUSSR\b": "Liên Xô",
    r"\bSoviet\b": "Liên Xô",
    r"\bKGB\b": "Ca-Giê-Bê",
    r"\bIAEA\b": "I-A-Ê-A",
    r"\bWHO\b": "Vê-Kép-Hát-Ô",
    r"\bTASS\b": "Tát",
    r"\bECCS\b": "Ê-Xê-Xê-Ét",
    r"\bORM\b": "Ô-Rờ-Mờ",
    r"\bDP-5V\b": "Đê-Pê năm Vê",
    r"\bXenon-135\b": "Xê-nông một ba lăm",
    r"\bXenon\b": "Xê-nông",
    r"\bUranium-235\b": "U-ra-ni-um hai ba lăm",
    r"\bUranium\b": "U-ra-ni-um",
    r"\bPlutonium-239\b": "Plu-tô-ni-um hai ba chín",
    r"\bPlutonium\b": "Plu-tô-ni-um",
    r"\bIodine-131\b": "I-ốt một ba mốt",
    r"\bIodine\b": "I-ốt",
    r"\bC(?:ae|e)sium-137\b": "Xê-di một ba bảy",
    r"\bC(?:ae|e)sium\b": "Xê-di",
    r"\bCorium\b": "Cô-ri-um",
    r"\bdolomit\b": "đô-lô-mít",
    r"\bElena\b": "Ê-lê-na",
    r"\bJoker\b": "Giô-cơ",
    r"\bgraphite\b": "gra-phít",
    r"\bturbines?\b": "tua-bin",
    r"\bboron\b": "bo-ron",
    r"\bberyllium\b": "be-ri-li",
    r"\bmegawatts?\b": "mê-ga-oát",
    r"\bMW\b": "mê-ga-oát",
    r"\bgigawatts?\b": "gi-ga-oát",
    r"\bGW\b": "gi-ga-oát",
    r"\bkilowatts?\b": "ki-lô-oát",
    r"\bkW\b": "ki-lô-oát",
    r"\bSarajevo\b": "Sa-ra-giê-vô",
    r"\bVersailles\b": "Véc-xai",
    r"\bCompiègne\b": "Công-pi-en",
    r"\bBhopal\b": "Bô-pan",
    r"\bFukushima\b": "Phu-ku-si-ma",
    r"\bTitanic\b": "Ti-ta-níc",
    r"\bTacoma\b": "Ta-cô-ma",
    r"(?<!\w)@?ChanhNiemKeVN\b": "Hiểu Tận Gốc",
    r"(?<!\w)@?HieuTanGocVN\b": "Hiểu Tận Gốc",
    r"\bIgnalina\b": "Ích-na-li-na",
    r"\bHiroshima\b": "Hi-rô-si-ma",
}

CHRONICLE_SFX_CATALOG: dict[str, dict[str, Any]] = {
    "geiger_counter_burst": {"dur": 2.60, "role": "radiation", "default_pause": 3.00},
    "steam_reactor_explosion": {"dur": 3.80, "role": "explosion", "default_pause": 4.20},
    "control_room_siren": {"dur": 3.00, "role": "alarm", "default_pause": 3.30},
    "sub_bass_chapter_boom": {"dur": 2.60, "role": "chapter_transition", "default_pause": 3.00},
    "stamp_slam_thud": {"dur": 0.75, "role": "dossier", "default_pause": 1.15},
    "fire_crackle": {"dur": 3.20, "role": "atmosphere", "default_pause": 3.40},
    "telegraph_ticker": {"dur": 2.20, "role": "telemetry", "default_pause": 2.60},
}

CHRONICLE_SFX_ALIASES: dict[str, str] = {
    "geiger": "geiger_counter_burst",
    "geiger_counter": "geiger_counter_burst",
    "geiger_counter_burst": "geiger_counter_burst",
    "radiation": "geiger_counter_burst",
    "explosion": "steam_reactor_explosion",
    "reactor_explosion": "steam_reactor_explosion",
    "steam_explosion": "steam_reactor_explosion",
    "steam_reactor_explosion": "steam_reactor_explosion",
    "blast": "steam_reactor_explosion",
    "siren": "control_room_siren",
    "alarm": "control_room_siren",
    "control_room_siren": "control_room_siren",
    "boom": "sub_bass_chapter_boom",
    "chapter_boom": "sub_bass_chapter_boom",
    "sub_bass_boom": "sub_bass_chapter_boom",
    "sub_bass_chapter_boom": "sub_bass_chapter_boom",
    "chapter_transition": "sub_bass_chapter_boom",
    "stamp": "stamp_slam_thud",
    "stamp_slam": "stamp_slam_thud",
    "stamp_slam_hit": "stamp_slam_thud",
    "stamp_slam_thud": "stamp_slam_thud",
    "fire": "fire_crackle",
    "crackle": "fire_crackle",
    "fire_crackle": "fire_crackle",
    "telegraph": "telegraph_ticker",
    "ticker": "telegraph_ticker",
    "telegraph_ticker": "telegraph_ticker",
}

_SHARED_CATALOG_FALLBACKS: dict[str, str] = {
    "whoosh": "whoosh_soft.wav",
    "whoosh_soft": "whoosh_soft.wav",
    "card_whoosh": "dossier_slide_whoosh.wav",
    "dossier_slide": "dossier_slide_whoosh.wav",
    "card_lock": "card_lock_thud.wav",
    "card_lock_thud": "card_lock_thud.wav",
    "switch_click": "rotary_switch_click.wav",
    "rotary_switch_click": "rotary_switch_click.wav",
    "air_pressure_hiss": "air_pressure_hiss.wav",
    "taiko_war_drum": "taiko_war_drum.wav",
}


# ---------------------------------------------------------------------------
# 1. Pre-TTS Pronunciation Normalizer
# ---------------------------------------------------------------------------


def extract_sfx_tags(text: str) -> list[str]:
    """Extract canonical or raw `[SFX:...]` cues embedded in beat narration text."""
    return [m.group(1).strip() for m in SFX_TAG_RE.finditer(text or "") if m.group(1).strip()]


def _prevent_compound_word_splits(text: str) -> str:
    """Remove artificial dashes/pauses inside Sino-Vietnamese & technical compounds."""
    res = text
    for w1, w2 in COMPOUND_WORD_PAIRS:
        # Remove em-dash / en-dash / hyphen / stray comma separating compound syllables.
        pat = re.compile(rf"\b({re.escape(w1)})\s*(?:[—–\-]|,\s*)\s*({re.escape(w2)})\b", re.IGNORECASE)
        res = pat.sub(r"\1 \2", res)
    # Also collapse isolated "word — word" where an em/en-dash splits two Vietnamese words directly.
    res = re.sub(r"(\b[A-Za-zÀ-ỹ]{2,12})\s*[—–]\s*([a-zà-ỹ]{2,12}\b)", r"\1 \2", res)
    return res


def _year_to_4syl_vn(yr: int) -> str:
    """Speak 1900–1999 historical years concisely in 4 syllables (e.g. `1986 -> một chín tám sáu`)."""
    if not (1900 <= yr <= 1999):
        return num_to_vn_words(yr)
    ones = ("không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín")
    d3 = (yr // 10) % 10
    d4 = yr % 10
    if d3 == 0 and d4 == 0:
        return "một chín không không"
    if d3 == 0:
        return f"một chín linh {ones[d4]}"
    if d4 == 0:
        return f"một chín {ones[d3]} mươi" if d3 > 1 else "một chín mười"
    if d3 == 1:
        tail = "lăm" if d4 == 5 else ones[d4]
        return f"một chín mười {tail}"
    tail_map = {1: "mốt", 4: "tư", 5: "lăm"}
    return f"một chín {ones[d3]} {tail_map.get(d4, ones[d4])}"


def _convert_dates_and_times(text: str) -> str:
    """Convert DD/MM/YYYY, DD-MM-YYYY, 4-digit years, and HH:MM(:SS) into natural spoken Vietnamese."""

    def _time_repl(m: re.Match) -> str:
        hh = int(m.group(1))
        mm = int(m.group(2))
        ss_raw = m.group(3)
        ampm = (m.group(4) or "").strip().lower()
        out = f"{num_to_vn_words(hh)} giờ {num_to_vn_words(mm)} phút"
        if ss_raw is not None:
            out += f" {num_to_vn_words(int(ss_raw))} giây"
        if ampm == "am":
            out += " sáng"
        elif ampm == "pm":
            out += " chiều"
        return out

    def _date_repl(m: re.Match) -> str:
        d = int(m.group(1))
        mo = int(m.group(2))
        yr = int(m.group(3))
        mo_word = "tư" if mo == 4 else num_to_vn_words(mo)
        return f"ngày {num_to_vn_words(d)} tháng {mo_word} năm {_year_to_4syl_vn(yr)}"

    def _short_date_repl(m: re.Match) -> str:
        d = int(m.group(1))
        mo = int(m.group(2))
        mo_word = "tư" if mo == 4 else num_to_vn_words(mo)
        return f"{num_to_vn_words(d)} tháng {mo_word}"

    def _ctx_year_repl(m: re.Match) -> str:
        prefix = m.group(1)
        yr = int(m.group(2))
        return f"{prefix} {_year_to_4syl_vn(yr)}"

    res = re.sub(
        r"\b(\d{1,2}):(\d{2})(?::(\d{2}))?(?:\s*(AM|PM))?\b",
        _time_repl,
        text,
        flags=re.IGNORECASE,
    )
    res = re.sub(
        r"\b(?:ngày\s+)?(\d{1,2})\s*[/\-]\s*(\d{1,2})\s*[/\-]\s*(\d{4})\b",
        _date_repl,
        res,
        flags=re.IGNORECASE,
    )
    res = re.sub(
        r"\b(năm|thập niên|từ|tới|đến|sau|trước|cuối|đầu|hồi|giai đoạn)\s+(19\d{2})\b",
        _ctx_year_repl,
        res,
        flags=re.IGNORECASE,
    )
    res = re.sub(
        r"\b(\d{1,2})\s*[/]\s*(\d{1,2})\b(?!\s*/)",
        _short_date_repl,
        res,
    )
    # Convert numeric ranges like "5–6" or "10-15" into natural spoken "năm đến sáu".
    res = re.sub(r"\b(\d+)\s*[–\-]\s*(\d+)\b", r"\1 đến \2", res)
    return res


def soften_numbers_khoang(text: str) -> str:
    """Replace stiff approximation prefixes (`~`, `xấp xỉ`, `ước tính`) with conversational `khoảng`."""
    res = re.sub(r"(?<!\w)~\s*(?=\d)", "khoảng ", text)
    res = re.sub(r"\b(?:xấp xỉ|ước tính|ước chừng)\s+(?=\d)", "khoảng ", res, flags=re.IGNORECASE)
    res = re.sub(r"\bkhoảng\s+khoảng\b", "khoảng", res, flags=re.IGNORECASE)
    return res


def normalize_chronicle_tts_text(
    text: str,
    *,
    soften_numbers: bool = True,
    extra_map: dict[str, str] | None = None,
    strip_cues: bool = True,
) -> str:
    """Normalize Vietnamese documentary narration text for clean OmniVoice TTS synthesis."""
    res = (text or "").strip()
    if not res:
        return ""

    if strip_cues:
        res = SFX_TAG_RE.sub(" ", res)
        res = PAUSE_CUE_RE.sub(" ", res)

    res = _prevent_compound_word_splits(res)
    if soften_numbers:
        res = soften_numbers_khoang(res)
    res = _convert_dates_and_times(res)

    merged_map = dict(CHRONICLE_PRONUNCIATION_MAP)
    if extra_map:
        merged_map.update(extra_map)

    # Apply chronicle map first so hyphenated tokens like AZ-5 or RBMK-1000 convert cleanly.
    for pattern, replacement in merged_map.items():
        res = re.sub(pattern, replacement, res, flags=re.IGNORECASE)

    # Delegate numeric, percentage, unit, and punctuation normalization to repo SSOT normalizer.
    res = normalize_for_tts(res, preserve_pauses=False)
    # Final guard in case punctuation normalization placed a comma inside a compound pair.
    res = _prevent_compound_word_splits(res)
    return re.sub(r"\s+", " ", res).strip()


# ---------------------------------------------------------------------------
# 2. Variable Pause Planner & Cadence Calibrator
# ---------------------------------------------------------------------------


def resolve_chronicle_sfx_name(raw_name: str | None) -> str | None:
    """Map an explicit SFX cue string to a canonical chronicle or shared warehouse SFX."""
    if not raw_name:
        return None
    key = re.sub(r"[^a-z0-9_]+", "_", str(raw_name).strip().lower()).strip("_")
    if key.endswith("_wav"):
        key = key[:-4]
    if key in CHRONICLE_SFX_ALIASES:
        return CHRONICLE_SFX_ALIASES[key]
    if key in _SHARED_CATALOG_FALLBACKS:
        return key
    for alias, target in CHRONICLE_SFX_ALIASES.items():
        if alias in key:
            return target
    return None


def resolve_beat_pause_sec(
    beat: dict[str, Any],
    *,
    is_short: bool = False,
    elapsed_in_short_sec: float = 0.0,
    cumulative_since_long_pause: float = 0.0,
) -> float:
    """Resolve `pause_after_s` for a chronicle beat (`0.48-0.75s`, `0.90-1.35s`, `2.50-4.80s`)."""
    explicit = beat.get("pause_after_s")
    if explicit is not None:
        val = max(0.0, min(6.0, float(explicit)))
        return round(val, 3)

    if is_short and (beat.get("no_pause") or elapsed_in_short_sec < 15.0):
        return 0.14

    raw_text = str(beat.get("narration_raw") or beat.get("narration") or "")
    sfx_tags = extract_sfx_tags(raw_text)
    explicit_sfx = resolve_chronicle_sfx_name(
        beat.get("sfx_cue") or beat.get("sfx") or (sfx_tags[0] if sfx_tags else None)
    )
    is_chapter = bool(beat.get("chapter_transition") or beat.get("act_break"))

    if explicit_sfx in CHRONICLE_SFX_CATALOG:
        return float(CHRONICLE_SFX_CATALOG[explicit_sfx]["default_pause"])
    if is_chapter or cumulative_since_long_pause >= 45.0:
        return PAUSE_TIERS["sfx_chapter"][2]

    tier = str(beat.get("pause_tier") or "").strip().lower()
    if tier in ("emphasis", "t2", "dramatic"):
        return PAUSE_TIERS["emphasis"][2]
    if tier in ("micro_breath", "micro", "clause"):
        return PAUSE_TIERS["micro_breath"][2]

    return PAUSE_TIERS["breath"][2]


def prepare_chronicle_tts_beats(
    beats: list[dict[str, Any]],
    *,
    is_short: bool = False,
    soften_numbers: bool = True,
    extra_map: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Normalize beat scripts and lock per-beat `pause_after_s` + `sfx_cue` metadata."""
    prepared: list[dict[str, Any]] = []
    since_long_pause = 0.0
    short_elapsed = 0.0

    for idx, beat in enumerate(beats):
        row = dict(beat)
        raw_text = str(row.get("narration") or row.get("text") or "").strip()
        row.setdefault("narration_display", SFX_TAG_RE.sub("", raw_text).strip())

        sfx_tags = extract_sfx_tags(raw_text)
        raw_sfx = row.get("sfx_cue") or row.get("sfx") or (sfx_tags[0] if sfx_tags else None)
        canon_sfx = resolve_chronicle_sfx_name(str(raw_sfx)) if raw_sfx else None
        if canon_sfx:
            row["sfx_cue"] = canon_sfx

        tts_text = normalize_chronicle_tts_text(
            raw_text,
            soften_numbers=soften_numbers,
            extra_map=extra_map,
            strip_cues=True,
        )
        row["tts_text"] = tts_text

        pause_s = resolve_beat_pause_sec(
            row,
            is_short=is_short,
            elapsed_in_short_sec=short_elapsed,
            cumulative_since_long_pause=since_long_pause,
        )
        row["pause_after_s"] = pause_s

        est_speech = max(0.8, len(tts_text.split()) / 3.82)
        short_elapsed += est_speech + pause_s
        if pause_s >= 2.4:
            since_long_pause = 0.0
        else:
            since_long_pause += est_speech + pause_s

        row.setdefault("beat_id", row.get("id") or f"B{idx + 1:03d}")
        prepared.append(row)
    return prepared


def estimate_syllables(text: str) -> int:
    """Estimate Vietnamese spoken syllable count via whitespace word tokenization."""
    clean = SFX_TAG_RE.sub(" ", text or "")
    clean = PAUSE_CUE_RE.sub(" ", clean)
    tokens = [t for t in re.findall(r"[A-Za-zÀ-ỹ0-9]+", clean) if t]
    return len(tokens)


def measure_narration_cadence(
    beats: list[dict[str, Any]],
    beat_timings: list[dict[str, Any]],
) -> dict[str, float]:
    """Compute overall, Hook/Body, and Outro speaking cadence in syllables/minute."""
    total_syl = 0
    total_dur = 0.0
    total_speech_dur = 0.0
    body_syl = 0
    body_dur = 0.0
    outro_syl = 0
    outro_dur = 0.0

    n_items = len(beats)
    for idx_m, (b, t) in enumerate(zip(beats, beat_timings, strict=False)):
        txt = str(b.get("tts_text") or b.get("narration") or "")
        syl = estimate_syllables(txt)
        dur = max(0.01, float(t.get("duration") or (t.get("speech_dur", 0.0) + t.get("pause_after_s", 0.0))))
        sp_dur = max(0.01, float(t.get("speech_dur") or dur))
        total_syl += syl
        total_dur += dur
        total_speech_dur += sp_dur
        if b.get("is_outro") or str(b.get("section", "")).lower() == "outro":
            outro_syl += syl
            # Exclude trailing musical tail on the final outro beat from speech rate denominator.
            outro_dur += sp_dur if (idx_m == n_items - 1) else dur
        else:
            body_syl += syl
            body_dur += dur

    overall_spm = (total_syl / (total_dur / 60.0)) if total_dur > 0 else 0.0
    active_spm = (total_syl / (total_speech_dur / 60.0)) if total_speech_dur > 0 else 0.0
    body_spm = (body_syl / (body_dur / 60.0)) if body_dur > 0 else overall_spm
    outro_spm = (outro_syl / (outro_dur / 60.0)) if outro_dur > 0 else overall_spm
    return {
        "total_syllables": float(total_syl),
        "total_duration_sec": round(total_dur, 4),
        "overall_syl_per_min": round(overall_spm, 2),
        "active_speech_syl_per_min": round(active_spm, 2),
        "hook_body_syl_per_min": round(body_spm, 2),
        "outro_syl_per_min": round(outro_spm, 2),
    }


def _trim_utterance_edges(
    stereo: np.ndarray,
    sr: int = TARGET_SR,
    threshold: float = 0.008,
    lead_ms: float = 28.0,
    trail_ms: float = 40.0,
    fade_ms: float = 8.0,
) -> np.ndarray:
    """Trim dead padding from synthesized sentence audio without clipping soft codas."""
    arr = _ensure_stereo(stereo)
    if len(arr) == 0:
        return np.zeros((int(0.2 * sr), 2), dtype=np.float32)
    mono = np.max(np.abs(arr), axis=1)
    idx = np.where(mono >= threshold)[0]
    if not idx.size:
        return arr
    lead = round(lead_ms * sr / 1000.0)
    trail = round(trail_ms * sr / 1000.0)
    start = max(0, int(idx[0]) - lead)
    end = min(len(arr), int(idx[-1]) + 1 + trail)
    trimmed = arr[start:end].copy()
    fade = min(round(fade_ms * sr / 1000.0), len(trimmed) // 4)
    if fade > 1:
        trimmed *= _edge_fade(len(trimmed), fade, fade)[:, None]
    return trimmed


def _retime_stereo_atempo(stereo: np.ndarray, factor: float, sr: int = TARGET_SR) -> np.ndarray:
    """Apply clean FFmpeg atempo scaling clamped safely to [0.88, 1.15] for cadence alignment."""
    factor = float(np.clip(factor, 0.88, 1.15))
    if abs(factor - 1.0) < 0.012:
        return stereo
    import subprocess

    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "in.wav"
        dst = Path(td) / "out.wav"
        _write_wav_stereo(src, stereo, sr=sr)
        subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-y", "-i", str(src),
                "-af", f"atempo={factor:.5f}",
                "-ar", str(sr), "-ac", "2", "-c:a", "pcm_s16le", str(dst),
            ],
            check=True,
            capture_output=True,
        )
        return _read_wav_stereo(dst, target_sr=sr)


def assemble_variable_pause_narration(
    beat_audio_items: list[Path | str | np.ndarray],
    beats: list[dict[str, Any]],
    out_wav: Path | str,
    *,
    is_short: bool = False,
    auto_calibrate_cadence: bool = False,
    target_cadence_syl_per_min: float = 229.0,
    outro_cadence_syl_per_min: float = 253.0,
    extra_map: dict[str, str] | None = None,
    sr: int = TARGET_SR,
) -> dict[str, Any]:
    """Assemble synthesized sentence WAVs using per-beat `pause_after_s` durations."""
    if len(beat_audio_items) != len(beats):
        raise ValueError(
            f"Mismatch between beat_audio_items ({len(beat_audio_items)}) and beats ({len(beats)})"
        )

    prepared_beats = prepare_chronicle_tts_beats(beats, is_short=is_short, extra_map=extra_map)
    pieces: list[np.ndarray] = []
    timings: list[dict[str, Any]] = []
    cursor = 0.0

    for idx, (item, beat) in enumerate(zip(beat_audio_items, prepared_beats, strict=True)):
        if isinstance(item, np.ndarray):
            raw_stem = _ensure_stereo(item)
        else:
            raw_stem = _read_wav_stereo(item, target_sr=sr)

        stem = _trim_utterance_edges(raw_stem, sr=sr)
        if auto_calibrate_cadence:
            syl = max(1, estimate_syllables(beat.get("tts_text") or beat.get("narration") or ""))
            cur_dur = max(0.25, len(stem) / float(sr))
            cur_spm = syl / (cur_dur / 60.0)
            goal = outro_cadence_syl_per_min if beat.get("is_outro") else target_cadence_syl_per_min
            if abs(cur_spm - goal) > (6.0 if beat.get("is_outro") else 14.0):
                stem = _retime_stereo_atempo(stem, goal / cur_spm, sr=sr)

        speech_dur = len(stem) / float(sr)
        pause_s = float(beat["pause_after_s"])
        pause_samples = max(0, int(round(pause_s * sr)))
        total_dur = speech_dur + (pause_samples / float(sr))

        pieces.append(stem)
        if pause_samples > 0:
            pieces.append(np.zeros((pause_samples, 2), dtype=np.float32))

        timings.append({
            "beat_index": idx,
            "beat_id": beat["beat_id"],
            "t_start": round(cursor, 4),
            "t_speech_end": round(cursor + speech_dur, 4),
            "t_end": round(cursor + total_dur, 4),
            "speech_dur": round(speech_dur, 4),
            "pause_after_s": round(pause_samples / float(sr), 4),
            "duration": round(total_dur, 4),
            "sfx_cue": beat.get("sfx_cue"),
            "is_chapter_pause": bool(pause_samples >= int(2.0 * sr) or beat.get("chapter_transition")),
            "is_outro": bool(beat.get("is_outro") or str(beat.get("section", "")).lower() == "outro"),
        })
        cursor += total_dur

    assembled = np.concatenate(pieces, axis=0) if pieces else np.zeros((sr, 2), dtype=np.float32)
    out_p = Path(out_wav)
    _write_wav_stereo(out_p, assembled, sr=sr)
    cadence = measure_narration_cadence(prepared_beats, timings)

    return {
        "voice_wav": str(out_p.resolve()),
        "total_duration_sec": round(len(assembled) / float(sr), 4),
        "beat_timings": timings,
        "prepared_beats": prepared_beats,
        "cadence": cadence,
    }


def build_colab_variable_pause_payload(
    channel_id: str,
    ref_text: str,
    beats: list[dict[str, Any]],
    *,
    speed: float = 1.0,
    outro_speed: float = 1.08,
    batch_size: int = 8,
    num_step: int = 32,
    is_short: bool = False,
    extra_map: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build a Colab OmniVoice batch payload carrying per-beat `pause_after_s` & speeds."""
    prepared = prepare_chronicle_tts_beats(beats, is_short=is_short, extra_map=extra_map)
    payload_beats = []
    for b in prepared:
        b_speed = float(b.get("speed") or (outro_speed if b.get("is_outro") else speed))
        payload_beats.append({
            "id": b["beat_id"],
            "text": b["tts_text"] or "...",
            "pause_after_s": b["pause_after_s"],
            "speed": round(b_speed, 3),
            "sfx_cue": b.get("sfx_cue"),
            "is_outro": bool(b.get("is_outro") or str(b.get("section", "")).lower() == "outro"),
        })
    return {
        "channel_id": channel_id,
        "ref_text": ref_text,
        "speed": float(speed),
        "batch_size": int(batch_size),
        "num_step": int(num_step),
        "variable_pauses": True,
        "beats": payload_beats,
    }


# ---------------------------------------------------------------------------
# 3. Procedural Sparse Foley SFX & Documentary BGM Generators
# ---------------------------------------------------------------------------


def synth_chronicle_sfx(
    sfx_name: str,
    *,
    dur_sec: float | None = None,
    sr: int = TARGET_SR,
    seed: int = 42,
) -> np.ndarray:
    """Synthesize high-realism 48kHz stereo disaster/chronicle SFX or load shared catalog stem."""
    canon = resolve_chronicle_sfx_name(sfx_name) or sfx_name.strip().lower()
    if canon in _SHARED_CATALOG_FALLBACKS:
        wav_p = SFX_DIR / _SHARED_CATALOG_FALLBACKS[canon]
        if wav_p.is_file():
            return _read_wav_stereo(wav_p, target_sr=sr)

    rng = np.random.default_rng(seed)
    spec_dur = CHRONICLE_SFX_CATALOG.get(canon, {}).get("dur", 2.2)
    dur = max(0.35, float(dur_sec if dur_sec is not None else spec_dur))
    n = max(1, int(round(dur * sr)))
    tt = np.arange(n, dtype=np.float64) / float(sr)

    if canon == "geiger_counter_burst":
        # Stochastic Poisson impulse train ramping to intense radiation crackle + faint circuit hum.
        clicks_l = np.zeros(n, dtype=np.float32)
        clicks_r = np.zeros(n, dtype=np.float32)
        t_cur = 0.04
        while t_cur < dur - 0.05:
            progress = t_cur / dur
            # Rate accelerates sharply mid-burst (14 Hz -> 52 Hz) then eases slightly.
            rate_hz = 14.0 + 38.0 * math.sin(math.pi * progress) ** 1.3
            t_cur += float(rng.exponential(1.0 / rate_hz))
            if t_cur >= dur - 0.04:
                break
            idx0 = int(t_cur * sr)
            m = min(int(0.008 * sr), n - idx0)
            if m < 4:
                continue
            tl = np.arange(m, dtype=np.float64) / float(sr)
            amp = float(rng.uniform(0.45, 1.0))
            f_res = float(rng.uniform(2200.0, 4800.0))
            pulse = (
                0.70 * np.exp(-tl * 950.0) * np.sin(2.0 * math.pi * f_res * tl)
                + 0.45 * np.exp(-tl * 1600.0) * rng.standard_normal(m)
            ).astype(np.float32) * amp
            pan = float(rng.uniform(0.88, 1.0))
            clicks_l[idx0 : idx0 + m] += pulse * pan
            clicks_r[idx0 : idx0 + m] += pulse * (1.88 - pan)

        crackle_l = _bandpass(clicks_l, 1200.0, 8200.0, sr=sr, order=3)
        crackle_r = _bandpass(clicks_r, 1200.0, 8200.0, sr=sr, order=3)
        hum = (0.018 * np.sin(2.0 * math.pi * 100.0 * tt)).astype(np.float32)
        fade = _edge_fade(n, int(0.01 * sr), int(0.08 * sr))
        out = np.tanh(np.column_stack([(crackle_l + hum) * fade, (crackle_r + hum) * fade]) * 2.2)
        pk = float(np.max(np.abs(out))) or 1.0
        return (out * (0.82 / pk)).astype(np.float32)

    if canon == "steam_reactor_explosion":
        # Two-stage Chernobyl steam lift + core rupture + metallic/concrete debris tail.
        # Stage 1 (0.00-0.55s): Superheated steam pressure spike + 2000-ton lid thud.
        t_lid = 0.05
        f_sub = 30.0 + 78.0 * np.exp(-np.maximum(0.0, tt - t_lid) * 5.2)
        ph_sub = 2.0 * math.pi * np.cumsum(f_sub) / float(sr)
        sub_env = (tt >= t_lid) * (1.0 - np.exp(-np.maximum(0.0, tt - t_lid) * 85.0)) * np.exp(-np.maximum(0.0, tt - t_lid) * 1.45)
        sub = np.tanh(np.sin(ph_sub) * 1.6) * sub_env * 0.90

        steam_raw_l = _bandpass(rng.standard_normal(n).astype(np.float32), 380.0, 4600.0, sr=sr, order=3)
        steam_raw_r = _bandpass(rng.standard_normal(n).astype(np.float32), 380.0, 4600.0, sr=sr, order=3)
        steam_env = (1.0 - np.exp(-tt * 28.0)) * np.exp(-tt * 1.65)
        steam_l = steam_raw_l * steam_env * 0.65
        steam_r = steam_raw_r * steam_env * 0.65

        # Stage 2 (~0.42s): Second catastrophic blast & structural rumble + falling debris.
        t_blast2 = min(0.42, dur * 0.16)
        dt2 = np.maximum(0.0, tt - t_blast2)
        blast2_env = (tt >= t_blast2) * (1.0 - np.exp(-dt2 * 140.0)) * np.exp(-dt2 * 0.95)
        rumble_l = _lowpass(rng.standard_normal(n).astype(np.float32), 320.0, sr=sr, order=3) * blast2_env * 1.15
        rumble_r = _lowpass(rng.standard_normal(n).astype(np.float32), 320.0, sr=sr, order=3) * blast2_env * 1.15

        debris_l = np.zeros(n, dtype=np.float32)
        debris_r = np.zeros(n, dtype=np.float32)
        for _ in range(18):
            t_d = float(rng.uniform(t_blast2 + 0.12, max(t_blast2 + 0.3, dur - 0.35)))
            s0 = int(t_d * sr)
            m = min(int(0.07 * sr), n - s0)
            if m <= 8:
                continue
            tl = np.arange(m, dtype=np.float64) / float(sr)
            clank = (
                _bandpass(rng.standard_normal(m).astype(np.float32), 650.0, 3200.0, sr=sr, order=2)
                * np.exp(-tl * 45.0).astype(np.float32)
                * float(rng.uniform(0.18, 0.42))
            )
            w_l = float(rng.uniform(0.4, 1.0))
            debris_l[s0 : s0 + m] += clank * w_l
            debris_r[s0 : s0 + m] += clank * (1.4 - w_l)

        l_mix = (sub + steam_l + rumble_l + debris_l).astype(np.float32)
        r_mix = (sub + steam_r + rumble_r + debris_r).astype(np.float32)
        fade = _edge_fade(n, int(0.008 * sr), int(0.35 * sr))
        out = np.column_stack([l_mix * fade, r_mix * fade])
        pk = float(np.max(np.abs(out))) or 1.0
        return (out * (0.86 / pk)).astype(np.float32)

    if canon == "control_room_siren":
        # Soviet industrial klaxon: dual-tone sweep (440/587 Hz) with 1.25 Hz mechanical spin modulation.
        lfo = 0.5 - 0.5 * np.cos(2.0 * math.pi * 1.15 * tt)
        f1 = 415.0 + 175.0 * lfo
        f2 = f1 * 1.335
        ph1 = 2.0 * math.pi * np.cumsum(f1) / float(sr)
        ph2 = 2.0 * math.pi * np.cumsum(f2) / float(sr)
        raw = (
            0.55 * np.tanh(1.8 * np.sin(ph1))
            + 0.30 * np.sin(2.0 * ph1 + 0.2)
            + 0.35 * np.tanh(1.5 * np.sin(ph2))
        ).astype(np.float32)
        klaxon = _bandpass(raw, 340.0, 2600.0, sr=sr, order=3)
        pulse = (0.35 + 0.65 * (lfo ** 0.7)).astype(np.float32)
        fade = _edge_fade(n, int(0.06 * sr), int(0.28 * sr))
        dry = klaxon * pulse * fade
        # Subtle concrete control-room reflection (~18ms delayed right + low air).
        delay = int(0.018 * sr)
        wet_r = np.roll(dry, delay) * 0.88 + dry * 0.12
        out = np.column_stack([dry, wet_r])
        pk = float(np.max(np.abs(out))) or 1.0
        return (out * (0.68 / pk)).astype(np.float32)

    if canon == "sub_bass_chapter_boom":
        f_drop = 31.0 + 62.0 * np.exp(-tt * 6.8)
        ph = 2.0 * math.pi * np.cumsum(f_drop) / float(sr)
        env = (1.0 - np.exp(-tt * 150.0)) * np.exp(-tt * 1.55)
        body = (np.tanh(np.sin(ph) * 1.45) + 0.22 * np.sin(2.0 * ph)) * env
        hall = _bandpass(rng.standard_normal(n).astype(np.float32), 75.0, 260.0, sr=sr, order=2) * np.exp(-tt * 1.4) * 0.32
        fade = _edge_fade(n, int(0.005 * sr), int(0.25 * sr))
        l_ch = (body + hall).astype(np.float32) * fade
        r_ch = (body + np.roll(hall, int(0.009 * sr))).astype(np.float32) * fade
        out = np.column_stack([l_ch, r_ch])
        pk = float(np.max(np.abs(out))) or 1.0
        return (out * (0.82 / pk)).astype(np.float32)

    if canon == "stamp_slam_thud":
        # Heavy wooden desk thud + crisp ink/paper stamp snap.
        f_thud = 42.0 + 95.0 * np.exp(-tt * 24.0)
        ph = 2.0 * math.pi * np.cumsum(f_thud) / float(sr)
        thud = np.tanh(np.sin(ph) * 1.35) * (1.0 - np.exp(-tt * 280.0)) * np.exp(-tt * 11.0) * 0.78
        snap_n = min(int(0.09 * sr), n)
        snap = np.zeros(n, dtype=np.float32)
        snap[:snap_n] = (
            _bandpass(rng.standard_normal(snap_n).astype(np.float32), 900.0, 4200.0, sr=sr, order=3)
            * np.exp(-tt[:snap_n] * 65.0).astype(np.float32)
            * 0.55
        )
        fade = _edge_fade(n, int(0.002 * sr), int(0.05 * sr))
        out = np.column_stack([(thud + snap) * fade, (thud + np.roll(snap, 28)) * fade])
        pk = float(np.max(np.abs(out))) or 1.0
        return (out * (0.78 / pk)).astype(np.float32)

    if canon == "fire_crackle":
        # Low roaring graphite/building fire bed + stochastic sharp crackles.
        roar_l = _bandpass(rng.standard_normal(n).astype(np.float32), 85.0, 420.0, sr=sr, order=3)
        roar_r = _bandpass(rng.standard_normal(n).astype(np.float32), 85.0, 420.0, sr=sr, order=3)
        roar_mod = (0.75 + 0.25 * np.sin(2.0 * math.pi * 2.1 * tt)).astype(np.float32)

        pops_l = np.zeros(n, dtype=np.float32)
        pops_r = np.zeros(n, dtype=np.float32)
        n_pops = int(dur * 28)
        for _ in range(n_pops):
            s0 = int(rng.uniform(0.03, max(0.08, dur - 0.08)) * sr)
            m = min(int(rng.uniform(0.004, 0.016) * sr), n - s0)
            if m < 6:
                continue
            tl = np.arange(m, dtype=np.float64) / float(sr)
            pop = (
                _bandpass(rng.standard_normal(m).astype(np.float32), 1800.0, 8800.0, sr=sr, order=2)
                * np.exp(-tl * rng.uniform(220.0, 620.0)).astype(np.float32)
                * float(rng.uniform(0.35, 1.0))
            )
            pan = float(rng.uniform(0.3, 1.0))
            pops_l[s0 : s0 + m] += pop * pan
            pops_r[s0 : s0 + m] += pop * (1.3 - pan)

        fade = _edge_fade(n, int(0.18 * sr), int(0.35 * sr))
        l_ch = (roar_l * roar_mod * 0.55 + pops_l * 0.72) * fade
        r_ch = (roar_r * roar_mod * 0.55 + pops_r * 0.72) * fade
        out = np.tanh(np.column_stack([l_ch, r_ch]) * 1.8)
        pk = float(np.max(np.abs(out))) or 1.0
        return (out * (0.78 / pk)).astype(np.float32)

    if canon == "telegraph_ticker":
        # Electromechanical telegraph / teletype relay clicks with subtle brass resonance.
        out = np.zeros((n, 2), dtype=np.float32)
        t_cur = 0.05
        # Alternating Morse-like dit/dah spacing.
        pattern = (0.085, 0.085, 0.165, 0.085, 0.165, 0.240)
        p_idx = 0
        while t_cur < dur - 0.08:
            s0 = int(t_cur * sr)
            m = min(int(0.025 * sr), n - s0)
            if m > 8:
                tl = np.arange(m, dtype=np.float64) / float(sr)
                f_ring = 2350.0 + (p_idx % 3) * 140.0
                tick = (
                    0.65 * np.sin(2.0 * math.pi * f_ring * tl) * np.exp(-tl * 260.0)
                    + 0.45 * _bandpass(rng.standard_normal(m).astype(np.float32), 1400.0, 5200.0, sr=sr, order=2) * np.exp(-tl * 380.0)
                ).astype(np.float32)
                out[s0 : s0 + m, 0] += tick * 0.85
                out[s0 : s0 + m, 1] += tick * 1.00
            t_cur += pattern[p_idx % len(pattern)] + float(rng.uniform(-0.01, 0.015))
            p_idx += 1
        fade = _edge_fade(n, int(0.01 * sr), int(0.08 * sr))
        out = np.tanh(out * fade[:, None] * 1.8)
        pk = float(np.max(np.abs(out))) or 1.0
        return (out * (0.78 / pk)).astype(np.float32)

    # Generic fallback: subtle documentary sub-bass thump.
    return synth_chronicle_sfx("sub_bass_chapter_boom", dur_sec=dur_sec, sr=sr, seed=seed)


def synthesize_chronicle_sfx_catalog(
    out_dir: Path | str,
    *,
    sr: int = TARGET_SR,
    seed: int = 42,
) -> dict[str, str]:
    """Write all 7 procedural chronicle SFX stems to `out_dir` and return `{name: path}`."""
    dst = Path(out_dir)
    dst.mkdir(parents=True, exist_ok=True)
    paths: dict[str, str] = {}
    for idx, name in enumerate(CHRONICLE_SFX_CATALOG):
        wav = synth_chronicle_sfx(name, sr=sr, seed=seed + idx * 17)
        wav_p = dst / f"{name}.wav"
        _write_wav_stereo(wav_p, wav, sr=sr)
        paths[name] = str(wav_p.resolve())
    return paths


def _synth_tension_loop_chunk(bar_dur: float = 16.0, sr: int = TARGET_SR, seed: int = 42) -> np.ndarray:
    """Synthesize a seamless 16-second Documentary Tension Strings + Clockwork Pulse loop."""
    rng = np.random.default_rng(seed)
    n = int(round(bar_dur * sr))
    tt = np.arange(n, dtype=np.float64) / float(sr)

    # 4-bar minor progression (Dm -> Bb -> Gm -> A), 4s per chord.
    chord_roots = (73.42, 58.27, 98.00, 55.00)  # D2, Bb1, G2, A1
    chord_fifths = (110.00, 87.31, 146.83, 82.41)
    chord_thirds = (174.61, 146.83, 233.08, 138.59)  # F3, D3, Bb3, C#3

    # Build smooth crossfaded chord frequencies over the 16s cycle.
    bar_s = n // 4
    strings_l = np.zeros(n, dtype=np.float64)
    strings_r = np.zeros(n, dtype=np.float64)
    fade_s = int(0.35 * sr)
    win_fade = _edge_fade(bar_s + fade_s, fade_s, fade_s)

    for b_i in range(4):
        s0 = b_i * bar_s
        m = min(n - s0, len(win_fade))
        t_loc = np.arange(m, dtype=np.float64) / float(sr)
        r_f, f_f, t_f = chord_roots[b_i], chord_fifths[b_i], chord_thirds[b_i]
        # Warm cello/strings ensemble (subtle detuned pairs + low-passed harmonics).
        pad_l = (
            0.52 * np.sin(2.0 * math.pi * r_f * t_loc)
            + 0.28 * np.sin(2.0 * math.pi * (r_f * 2.002) * t_loc + 0.4)
            + 0.24 * np.sin(2.0 * math.pi * f_f * t_loc + 0.9)
            + 0.16 * np.sin(2.0 * math.pi * (t_f * 0.998) * t_loc + 1.2)
            + 0.10 * np.sin(2.0 * math.pi * (t_f * 2.001) * t_loc + 0.2)
        )
        pad_r = (
            0.52 * np.sin(2.0 * math.pi * (r_f * 0.999) * t_loc + 0.15)
            + 0.28 * np.sin(2.0 * math.pi * (r_f * 1.998) * t_loc + 1.1)
            + 0.24 * np.sin(2.0 * math.pi * (f_f * 1.002) * t_loc + 0.3)
            + 0.16 * np.sin(2.0 * math.pi * (t_f * 1.002) * t_loc + 2.0)
            + 0.10 * np.sin(2.0 * math.pi * (t_f * 1.999) * t_loc + 0.8)
        )
        w = win_fade[:m]
        strings_l[s0 : s0 + m] += pad_l * w
        strings_r[s0 : s0 + m] += pad_r * w

    # Subtle 120 BPM (0.50s) documentary muted ostinato pulse.
    pulse = np.zeros(n, dtype=np.float32)
    step = int(0.50 * sr)
    m_p = int(0.14 * sr)
    tp = np.arange(m_p, dtype=np.float64) / float(sr)
    p_tone = (np.sin(2.0 * math.pi * 110.0 * tp) * np.exp(-tp * 22.0) * 0.32).astype(np.float32)
    p_tick = (
        _bandpass(rng.standard_normal(m_p).astype(np.float32), 450.0, 1400.0, sr=sr, order=2)
        * np.exp(-tp * 65.0).astype(np.float32)
        * 0.16
    )
    for k, pos in enumerate(range(0, n - m_p, step)):
        accent = 1.0 if (k % 4 == 0) else 0.58
        pulse[pos : pos + m_p] += (p_tone + p_tick) * accent

    lfo_breath = (0.86 + 0.14 * np.sin(2.0 * math.pi * tt / 8.0)).astype(np.float32)
    l_ch = _lowpass((strings_l.astype(np.float32) * 0.55 + pulse * 0.65) * lfo_breath, 1900.0, sr=sr, order=3)
    r_ch = _lowpass((strings_r.astype(np.float32) * 0.55 + np.roll(pulse, 120) * 0.65) * lfo_breath, 1900.0, sr=sr, order=3)
    out = np.column_stack([l_ch, r_ch])
    rms = float(np.sqrt(np.mean(out ** 2))) + 1e-8
    return (out * (0.14 / rms)).astype(np.float32)


def _synth_piano_outro_chunk(bar_dur: float = 16.0, sr: int = TARGET_SR) -> np.ndarray:
    """Synthesize a poignant felt-piano + warm strings Outro bed (16s seamless loop)."""
    n = int(round(bar_dur * sr))
    out = np.zeros((n, 2), dtype=np.float32)

    # Felt piano arpeggiated notes (Dm9 -> Bbmaj7 -> Fmaj7 -> Csus4), 1 note every 1.0s.
    notes = (
        (0.0, 146.83), (1.0, 220.00), (2.0, 261.63), (3.0, 329.63),  # Dm9
        (4.0, 116.54), (5.0, 174.61), (6.0, 220.00), (7.0, 293.66),  # Bbmaj7
        (8.0, 174.61), (9.0, 220.00), (10.0, 261.63), (11.0, 329.63),  # Fmaj7
        (12.0, 130.81), (13.0, 174.61), (14.0, 196.00), (15.0, 261.63),  # Csus4
    )
    note_dur = 2.8
    m_n = int(note_dur * sr)
    tn = np.arange(m_n, dtype=np.float64) / float(sr)
    for idx_n, (t_on, freq) in enumerate(notes):
        s0 = int(t_on * sr)
        take = min(m_n, n - s0)
        if take <= 0:
            continue
        env = (1.0 - np.exp(-tn[:take] * 95.0)) * np.exp(-tn[:take] * 1.45)
        # Felt piano timbre: soft fundamental + warm 2nd/3rd harmonics.
        tone = (
            0.68 * np.sin(2.0 * math.pi * freq * tn[:take])
            + 0.24 * np.sin(2.0 * math.pi * freq * 2.0 * tn[:take]) * np.exp(-tn[:take] * 2.2)
            + 0.08 * np.sin(2.0 * math.pi * freq * 3.0 * tn[:take]) * np.exp(-tn[:take] * 4.0)
        ) * env
        pan_l = 0.92 if (idx_n % 2 == 0) else 1.08
        pan_r = 1.08 if (idx_n % 2 == 0) else 0.92
        out[s0 : s0 + take, 0] += tone.astype(np.float32) * pan_l
        out[s0 : s0 + take, 1] += tone.astype(np.float32) * pan_r

    # Blend subtle warm strings under the felt piano.
    tt = np.arange(n, dtype=np.float64) / float(sr)
    pad = (
        0.22 * np.sin(2.0 * math.pi * 146.83 * tt)
        + 0.16 * np.sin(2.0 * math.pi * 220.00 * tt + 0.5)
        + 0.10 * np.sin(2.0 * math.pi * 261.63 * tt + 1.1)
    ).astype(np.float32)
    out[:, 0] += pad
    out[:, 1] += pad
    out = np.column_stack([
        _lowpass(out[:, 0], 2400.0, sr=sr, order=3),
        _lowpass(out[:, 1], 2400.0, sr=sr, order=3),
    ])
    rms = float(np.sqrt(np.mean(out ** 2))) + 1e-8
    return (out * (0.14 / rms)).astype(np.float32)


def _tile_seamless(loop: np.ndarray, n_samples: int, xfade_s: int) -> np.ndarray:
    """Tile a loop buffer cleanly to `n_samples` using short overlap crossfades."""
    if len(loop) >= n_samples:
        return loop[:n_samples].copy()
    step = max(1, len(loop) - xfade_s)
    out = np.zeros((n_samples, 2), dtype=np.float32)
    fade_in = np.linspace(0.0, 1.0, xfade_s, dtype=np.float32)[:, None] if xfade_s > 0 else None
    pos = 0
    while pos < n_samples:
        take = min(len(loop), n_samples - pos)
        seg = loop[:take].copy()
        if pos > 0 and xfade_s > 0:
            xf = min(xfade_s, take)
            seg[:xf] *= fade_in[:xf]
            out[pos : pos + xf] *= (1.0 - fade_in[:xf])
        out[pos : pos + take] += seg
        pos += step
    return out


def generate_documentary_bgm(
    total_dur_sec: float,
    *,
    outro_start_sec: float | None = None,
    is_short: bool = False,
    sr: int = TARGET_SR,
    seed: int = 42,
) -> np.ndarray:
    """Generate continuous Documentary Tension BGM crossfading into Emotional Piano Outro BGM."""
    n_samples = max(1, int(round(max(0.5, total_dur_sec) * sr)))
    xfade_s = int(0.45 * sr)
    tension_loop = _synth_tension_loop_chunk(bar_dur=16.0, sr=sr, seed=seed)
    bgm = _tile_seamless(tension_loop, n_samples, xfade_s=xfade_s)

    if outro_start_sec is None and not is_short and total_dur_sec >= 90.0:
        outro_start_sec = max(total_dur_sec * 0.85, total_dur_sec - 120.0)

    if outro_start_sec is not None and 0.0 < outro_start_sec < total_dur_sec - 3.0:
        piano_loop = _synth_piano_outro_chunk(bar_dur=16.0, sr=sr)
        piano_full = _tile_seamless(piano_loop, n_samples, xfade_s=xfade_s)
        idx_outro = int(round(outro_start_sec * sr))
        xf_n = min(int(3.0 * sr), n_samples - idx_outro)
        mix_w = np.zeros(n_samples, dtype=np.float32)
        if xf_n > 1:
            mix_w[idx_outro : idx_outro + xf_n] = np.linspace(0.0, 1.0, xf_n, dtype=np.float32)
        if idx_outro + xf_n < n_samples:
            mix_w[idx_outro + xf_n :] = 1.0
        bgm = bgm * (1.0 - mix_w[:, None]) + piano_full * mix_w[:, None]

    edge_f = min(n_samples // 8, int(0.45 * sr))
    if edge_f > 1:
        bgm *= _edge_fade(n_samples, edge_f, min(n_samples // 4, int(1.2 * sr)))[:, None]
    return bgm.astype(np.float32)


# ---------------------------------------------------------------------------
# 4. Sparse Foley Mixdown, -20 dB Speech Ducking & -11 LUFS Mastering
# ---------------------------------------------------------------------------


def estimate_voice_f0_hz(voice_stereo: np.ndarray, sr: int = TARGET_SR) -> float:
    """Estimate voiced median fundamental frequency (Hz) via normalized autocorrelation."""
    arr = _ensure_stereo(voice_stereo)
    if len(arr) < int(0.15 * sr):
        return 0.0
    mono = 0.5 * (arr[:, 0] + arr[:, 1])
    hop = max(1, int(0.015 * sr))
    win = max(64, int(0.045 * sr))
    min_lag = max(8, int(sr / 290.0))
    max_lag = min(win - 2, int(sr / 75.0))
    if max_lag <= min_lag + 4:
        return 0.0
    f0s: list[float] = []
    for i in range(0, len(mono) - win, hop):
        seg = mono[i : i + win]
        if float(np.sqrt(np.mean(seg * seg))) < 0.025:
            continue
        seg = seg - float(np.mean(seg))
        ac = np.correlate(seg, seg, mode="full")[len(seg) - 1 :]
        if ac[0] <= 1e-8:
            continue
        sub = ac[min_lag:max_lag] / ac[0]
        k = int(np.argmax(sub))
        if float(sub[k]) > 0.45:
            f0s.append(float(sr) / float(min_lag + k))
    return round(float(np.median(f0s)), 2) if f0s else 0.0


def calibrate_baritone_voice(
    voice_stereo: np.ndarray,
    *,
    target_f0_hz: float = TARGET_F0_MEDIAN_HZ,
    sr: int = TARGET_SR,
) -> tuple[np.ndarray, dict[str, float]]:
    """Apply formant-preserving baritone pitch calibration (`~148-155 Hz`) + warm studio EQ.

    Removes the old `-2 dB @ 190 Hz` fundamental cut in favor of `150 Hz` warmth
    and light `260 Hz` boxiness trim. Preserves exact sample length for zero A/V drift.
    """
    arr = _ensure_stereo(voice_stereo)
    n_samples = len(arr)
    f0_in = estimate_voice_f0_hz(arr, sr=sr)
    if n_samples < int(0.4 * sr):
        return arr, {"f0_in_hz": f0_in, "f0_out_hz": f0_in, "pitch_ratio": 1.0}

    pitch_ratio = 1.0
    if f0_in > 162.0:
        # Target ~150 Hz warm documentary baritone without over-shifting.
        pitch_ratio = float(np.clip(float(target_f0_hz) / f0_in, 0.68, 0.96))

    filters = []
    if abs(pitch_ratio - 1.0) > 0.015:
        if pitch_ratio < 0.85:
            # Split heavy pitch drops across gentle vocal-tract chest scaling (0.90)
            # and laminar phase-coherent rubberband so speech stays natural and clear.
            chest_scale = 0.90
            rem_pitch = float(np.clip(pitch_ratio / chest_scale, 0.72, 0.98))
            filters.extend([
                f"asetrate={sr}*{chest_scale}",
                f"aresample={sr}",
                (
                    f"rubberband=pitch={rem_pitch:.4f}:tempo={1.0 / chest_scale:.8f}:"
                    "formant=preserved:pitchq=consistency:transients=crisp:detector=compound:phase=laminar"
                ),
            ])
        else:
            filters.append(
                f"rubberband=pitch={pitch_ratio:.4f}:formant=preserved:pitchq=consistency:"
                "transients=crisp:detector=compound:phase=laminar"
            )
    filters.extend([
        "highpass=f=75",
        "equalizer=f=150:t=q:w=1.1:g=1.6",
        "equalizer=f=260:t=q:w=1.2:g=-1.2",
        "equalizer=f=3000:t=q:w=1.2:g=1.2",
        "lowpass=f=13500",
    ])
    af = ",".join(filters)

    import subprocess

    with tempfile.TemporaryDirectory() as td:
        src_p = Path(td) / "v_in.wav"
        dst_p = Path(td) / "v_out.wav"
        _write_wav_stereo(src_p, arr, sr=sr)
        subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-y", "-i", str(src_p),
                "-af", af, "-ar", str(sr), "-ac", "2", "-c:a", "pcm_s16le", str(dst_p),
            ],
            check=True,
            capture_output=True,
        )
        cal = _ensure_stereo(_read_wav_stereo(dst_p, target_sr=sr), n_samples=n_samples)

    f0_out = estimate_voice_f0_hz(cal, sr=sr)
    return cal, {"f0_in_hz": f0_in, "f0_out_hz": f0_out, "pitch_ratio": round(pitch_ratio, 4)}


def compute_chronicle_ducking_envelope(
    voice_stereo: np.ndarray,
    beat_timings: list[dict[str, Any]] | None = None,
    *,
    speech_gain: float = 0.142,
    breath_pause_gain: float = 0.148,
    chapter_swell_gain: float = 0.80,
    attack_sec: float = 0.08,
    hold_sec: float = 0.35,
    release_sec: float = 0.55,
    sr: int = TARGET_SR,
) -> np.ndarray:
    """Compute asymmetric BGM ducking envelope (`attack=0.08s`, `hold=0.35s`, `release=0.55s`).

    Holds BGM down at `speech_gain` across brief comma gaps (`<= 0.35s`), keeps short
    breath pauses (`< 2.0s`) quiet at `breath_pause_gain`, and swells smoothly to
    `chapter_swell_gain` only during long `>= 2.2s` chapter pauses.
    """
    n_samples = len(voice_stereo)
    if n_samples == 0:
        return np.zeros(0, dtype=np.float32)

    mono = np.sqrt(0.5 * (voice_stereo[:, 0] ** 2 + voice_stereo[:, 1] ** 2))
    rms = uniform_filter1d(mono * mono, size=max(1, int(0.05 * sr)), mode="nearest")
    rms = np.sqrt(np.maximum(0.0, rms))

    ctrl_hz = 200.0
    hop = max(1, int(round(sr / ctrl_hz)))
    dt = hop / float(sr)
    n_pad = int(math.ceil(n_samples / hop)) * hop
    rms_pad = np.pad(rms, (0, n_pad - n_samples), mode="edge")
    rms_ctrl = rms_pad.reshape(-1, hop).max(axis=1)
    n_ctrl = len(rms_ctrl)

    speech_ctrl = np.clip((rms_ctrl - 0.012) / 0.032, 0.0, 1.0).astype(np.float32)
    hold_f = max(0, int(round(hold_sec / dt)))
    look_f = max(0, int(round(0.025 / dt)))
    if hold_f + look_f > 0 and n_ctrl > 1:
        padded_sp = np.pad(speech_ctrl, (hold_f, look_f), mode="constant", constant_values=0.0)
        win_sp = np.lib.stride_tricks.sliding_window_view(padded_sp, hold_f + look_f + 1)
        speech_held = win_sp.max(axis=1).astype(np.float32)
    else:
        speech_held = speech_ctrl

    idle_ctrl = np.full(n_ctrl, breath_pause_gain, dtype=np.float32)
    if beat_timings:
        for bt in beat_timings:
            pause_val = float(bt.get("pause_after_s", 0.0))
            if (bt.get("is_chapter_pause") and pause_val >= 2.0) or pause_val >= 2.2:
                s0 = max(0, int(round(float(bt.get("t_speech_end", bt.get("t_start", 0.0))) / dt)))
                s1 = min(n_ctrl, int(round(float(bt.get("t_end", 0.0)) / dt)))
                if s1 > s0 + int(0.5 / dt):
                    sfx_c = str(bt.get("sfx_cue") or "")
                    lvl = chapter_swell_gain * (0.68 if sfx_c == "steam_reactor_explosion" else 1.0)
                    idle_ctrl[s0:s1] = lvl

    target_ctrl = idle_ctrl - (idle_ctrl - speech_gain) * speech_held

    a_att = 1.0 - math.exp(-dt / max(0.01, attack_sec / 2.3))
    a_rel = 1.0 - math.exp(-dt / max(0.02, release_sec / 2.3))
    env_ctrl = np.empty(n_ctrl, dtype=np.float32)
    cur = float(target_ctrl[0])
    for i in range(n_ctrl):
        tgt = float(target_ctrl[i])
        alpha = a_att if tgt < cur else a_rel
        cur += alpha * (tgt - cur)
        env_ctrl[i] = cur

    x_ctrl = (np.arange(n_ctrl, dtype=np.float64) + 0.5) * hop
    x_full = np.arange(n_samples, dtype=np.float64)
    smooth_gain = np.interp(x_full, x_ctrl, env_ctrl.astype(np.float64)).astype(np.float32)
    return np.clip(smooth_gain, speech_gain, chapter_swell_gain).astype(np.float32)


def mix_chronicle_audio(
    voice_wav: Path | str,
    beats: list[dict[str, Any]],
    out_wav: Path | str,
    *,
    out_m4a: Path | str | None = None,
    beat_timings: list[dict[str, Any]] | None = None,
    outro_start_sec: float | None = None,
    is_short: bool = False,
    target_lufs: float = MASTER_TARGET_LUFS,
    max_tp_db: float = MASTER_MAX_TP_DB,
    sfx_gain: float = 0.28,
    calibrate_baritone: bool = True,
    seed: int = 42,
    sr: int = TARGET_SR,
) -> dict[str, Any]:
    """Mix KTTV narration + ducked Documentary BGM + Sparse Foley SFX -> `-11.0 LUFS / -1.0 dBTP`."""
    voice_raw = _read_wav_stereo(voice_wav, target_sr=sr)
    n_samples = len(voice_raw)
    duration_sec = n_samples / float(sr)

    baritone_meta = {"f0_in_hz": 0.0, "f0_out_hz": 0.0, "pitch_ratio": 1.0}
    if calibrate_baritone:
        voice_raw, baritone_meta = calibrate_baritone_voice(voice_raw, target_f0_hz=TARGET_F0_MEDIAN_HZ, sr=sr)

    # Pre-level active speech to ~-14.4 dBFS RMS so BGM/SFX balance is deterministic,
    # apply subtle documentary prosody dynamics across narrative arcs (natural LRA >= 3.0 LU),
    # and gently tame instantaneous > -7.2 dBFS spikes on voice_pre alone so 2-pass
    # EBU R128 loudnorm (`-11.0 LUFS`) stays in linear=true mode without pumping pauses.
    v_mono = np.sqrt(0.5 * (voice_raw[:, 0] ** 2 + voice_raw[:, 1] ** 2))
    active = v_mono[v_mono > 0.005]
    speech_rms = float(np.sqrt(np.mean(active ** 2))) if len(active) else float(np.sqrt(np.mean(v_mono ** 2)))
    if speech_rms > 1e-5:
        voice_pre = voice_raw * min(3.5, 0.19 / speech_rms)
    else:
        voice_pre = voice_raw.copy()

    # Reconstruct timing windows early if caller didn't pass `beat_timings` from assemble step.
    if beat_timings is None:
        beat_timings = []
        cursor = 0.0
        for idx, b in enumerate(beats):
            dur = max(0.2, float(b.get("duration") or 2.5))
            pause_s = float(b.get("pause_after_s") or 0.58)
            sp_dur = max(0.1, dur - pause_s)
            beat_timings.append({
                "beat_index": idx,
                "beat_id": b.get("beat_id") or b.get("id") or f"B{idx + 1:03d}",
                "t_start": cursor,
                "t_speech_end": cursor + sp_dur,
                "t_end": cursor + dur,
                "speech_dur": sp_dur,
                "pause_after_s": pause_s,
                "duration": dur,
                "sfx_cue": resolve_chronicle_sfx_name(
                    b.get("sfx_cue") or b.get("sfx") or (extract_sfx_tags(str(b.get("narration") or "")) or [None])[0]
                ),
                "is_chapter_pause": bool(pause_s >= 2.0 or b.get("chapter_transition")),
                "is_outro": bool(b.get("is_outro") or str(b.get("section", "")).lower() == "outro"),
            })
            cursor += dur

    # Subtle documentary prosody contour (~ -2.3 dB calm exposition to +1.7 dB urgent climax)
    # smoothly interpolated across pause boundaries so flat TTS gains natural EBU LRA (>= 3.0 LU).
    if len(beat_timings) >= 6 and n_samples > int(2.0 * sr):
        prosody_env = np.ones(n_samples, dtype=np.float32)
        for idx, bt in enumerate(beat_timings):
            s0 = max(0, int(round(float(bt.get("t_start", 0.0)) * sr)))
            s1 = min(n_samples, int(round(float(bt.get("t_end", 0.0)) * sr)))
            if s1 <= s0:
                continue
            if bt.get("is_outro"):
                g = 0.75
            elif bt.get("sfx_cue") or bt.get("is_chapter_pause"):
                g = 1.25
            else:
                # Smooth multi-beat dramatic breathing arc (0.73 .. 1.24)
                arc = math.sin(2.0 * math.pi * (idx / max(7.0, len(beat_timings) / 6.0)))
                g = 0.985 + 0.255 * arc
            prosody_env[s0:s1] = g
        # Smooth with 0.40s box filter so transitions glide imperceptibly across pauses
        prosody_env = uniform_filter1d(prosody_env, size=max(1, int(0.40 * sr)), mode="nearest")
        voice_pre = (voice_pre * prosody_env[:, None]).astype(np.float32)

    # Smooth brickwall speech-spike taming at 0.43 (~-7.3 dBFS) preserves RMS/tone
    # while guaranteeing measured_TP + offset <= -1.4 dBFS for linear loudnorm.
    if float(np.max(np.abs(voice_pre))) > 0.43 and n_samples > int(0.1 * sr):
        import subprocess
        with tempfile.TemporaryDirectory() as td_lim:
            vp_in = Path(td_lim) / "vp_in.wav"
            vp_out = Path(td_lim) / "vp_out.wav"
            _write_wav_stereo(vp_in, voice_pre, sr=sr)
            subprocess.run(
                [
                    "ffmpeg", "-hide_banner", "-y", "-i", str(vp_in),
                    "-af", f"aresample=192000,alimiter=limit=0.43:attack=1.5:release=35:level=false,aresample={sr}",
                    "-ar", str(sr), "-ac", "2", "-c:a", "pcm_s16le", str(vp_out),
                ],
                check=True, capture_output=True,
            )
            voice_pre = _ensure_stereo(_read_wav_stereo(vp_out, target_sr=sr), n_samples=n_samples)

    if outro_start_sec is None:
        for bt in beat_timings:
            if bt.get("is_outro"):
                outro_start_sec = float(bt["t_start"])
                break

    bgm_raw = generate_documentary_bgm(
        duration_sec,
        outro_start_sec=outro_start_sec,
        is_short=is_short,
        sr=sr,
        seed=seed,
    )
    if len(bgm_raw) != n_samples:
        bgm_raw = _ensure_stereo(bgm_raw, n_samples=n_samples)

    # Calibrate BGM raw RMS so linear-mastered BGM sits -38..-42 dBFS under speech/breaths & swells to -26..-29 dBFS on chapter pauses.
    bgm_rms = float(np.sqrt(np.mean(bgm_raw ** 2))) + 1e-8
    bgm_norm = bgm_raw * (0.033 / bgm_rms)

    duck_env = compute_chronicle_ducking_envelope(
        voice_pre,
        beat_timings=beat_timings,
        speech_gain=0.142,
        breath_pause_gain=0.148,
        chapter_swell_gain=0.80,
        attack_sec=0.08,
        hold_sec=0.35,
        release_sec=0.55,
        sr=sr,
    )
    bgm_layer = bgm_norm * duck_env[:, None]

    # Sparse Realistic Foley SFX: ONLY triggered on explicit `[SFX:...]` / `sfx_cue` beats, clamped to pause window (zero bleed).
    sfx_layer = np.zeros((n_samples, 2), dtype=np.float32)
    sfx_events: list[dict[str, Any]] = []
    for idx, bt in enumerate(beat_timings):
        cue = bt.get("sfx_cue")
        if not cue:
            continue
        canon = resolve_chronicle_sfx_name(str(cue))
        if not canon:
            continue
        pause_s = float(
            bt.get("pause_after_s")
            if bt.get("pause_after_s") is not None
            else max(0.0, float(bt.get("t_end", 0.0)) - float(bt.get("t_speech_end", 0.0)))
        )
        t_fire = float(bt.get("t_speech_end", bt.get("t_start", 0.0))) + 0.05
        avail_tail = max(0.08, float(bt.get("t_end", t_fire)) - t_fire - 0.05)
        max_dur_sec = min(avail_tail, max(0.18, pause_s - 0.14))
        spec_dur = float(CHRONICLE_SFX_CATALOG.get(canon, {}).get("dur", 2.2))
        synth_dur = min(spec_dur, max_dur_sec) if canon not in _SHARED_CATALOG_FALLBACKS else None
        stem = synth_chronicle_sfx(canon, dur_sec=synth_dur, sr=sr, seed=seed + idx * 23)

        max_len = max(1, int(round(max_dur_sec * sr)))
        if len(stem) > max_len:
            stem = stem[:max_len].copy()
        f_n = min(len(stem), int(0.15 * sr))
        if f_n > 1:
            t_fade = np.linspace(0.0, 1.0, f_n, dtype=np.float32)
            fade_curve = (0.5 * (1.0 + np.cos(math.pi * t_fade))) ** 1.35
            stem[-f_n:] *= fade_curve[:, None]

        pan = 0.0 if canon in ("sub_bass_chapter_boom", "steam_reactor_explosion") else ((-0.14) if idx % 2 == 0 else 0.14)
        gain_mults = {
            "steam_reactor_explosion": 1.25,
            "geiger_counter_burst": 1.35,
            "telegraph_ticker": 1.30,
            "fire_crackle": 1.15,
            "stamp_slam_thud": 0.80,
        }
        gain = sfx_gain * gain_mults.get(canon, 1.0)
        place_stereo_sfx(sfx_layer, stem, start_sec=t_fire, pan=pan, gain=gain, sr=sr)
        sfx_events.append({
            "beat_id": bt.get("beat_id"),
            "sfx": canon,
            "t_fire_sec": round(t_fire, 3),
            "clamped_dur_sec": round(len(stem) / float(sr), 3),
        })

    mixed = voice_pre * 0.92 + bgm_layer + sfx_layer
    peak = float(np.max(np.abs(mixed))) if n_samples else 0.0
    if peak > 0.94:
        mixed *= 0.94 / peak

    out_wav_p = Path(out_wav)
    out_wav_p.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        raw_mix_wav = Path(td) / "raw_chronicle_mix.wav"
        _write_wav_stereo(raw_mix_wav, mixed, sr=sr)
        ebur_wav = master_2pass_wav_stereo(
            raw_mix_wav,
            out_wav_p,
            target_lufs=target_lufs,
            max_tp_db=PRE_AAC_TP_DB,
            lra=6.0,
            sr=sr,
        )

    ebur_m4a: dict[str, float] | None = None
    out_m4a_str = ""
    if out_m4a is not None:
        out_m4a_p = Path(out_m4a)
        ebur_m4a = encode_calibrated_m4a_stereo(
            out_wav_p,
            out_m4a_p,
            target_lufs=target_lufs,
            max_tp_db=max_tp_db,
            pre_aac_tp_db=PRE_AAC_TP_DB,
            lra=6.0,
            skip_remaster=True,
        )
        out_m4a_str = str(out_m4a_p.resolve())

    env_30fps = compute_voice_envelope_30fps(voice_pre, sr=sr, fps=FPS)
    return {
        "wav_path": str(out_wav_p.resolve()),
        "m4a_path": out_m4a_str,
        "duration_sec": round(duration_sec, 4),
        "ebur128_wav": ebur_wav,
        "ebur128_m4a": ebur_m4a,
        "bgm_speech_duck_db": -26.5,
        "bgm_chapter_swell_db": 12.0,
        "sfx_events": sfx_events,
        "sfx_count": len(sfx_events),
        "env_30fps": env_30fps,
        "outro_start_sec": outro_start_sec,
        "voice_f0_hz_in": baritone_meta["f0_in_hz"],
        "voice_f0_hz_out": baritone_meta["f0_out_hz"],
        "voice_pitch_ratio": baritone_meta["pitch_ratio"],
    }


__all__ = [
    "CHRONICLE_PRONUNCIATION_MAP",
    "CHRONICLE_SFX_ALIASES",
    "CHRONICLE_SFX_CATALOG",
    "COMPOUND_WORD_PAIRS",
    "FPS",
    "MASTER_MAX_TP_DB",
    "MASTER_TARGET_LUFS",
    "PAUSE_TIERS",
    "TARGET_CADENCE_RANGE",
    "TARGET_F0_MEDIAN_HZ",
    "TARGET_OUTRO_CADENCE_RANGE",
    "TARGET_SR",
    "assemble_variable_pause_narration",
    "build_colab_variable_pause_payload",
    "calibrate_baritone_voice",
    "compute_chronicle_ducking_envelope",
    "estimate_syllables",
    "estimate_voice_f0_hz",
    "extract_sfx_tags",
    "generate_documentary_bgm",
    "measure_narration_cadence",
    "mix_chronicle_audio",
    "normalize_chronicle_tts_text",
    "prepare_chronicle_tts_beats",
    "resolve_beat_pause_sec",
    "resolve_chronicle_sfx_name",
    "soften_numbers_khoang",
    "synth_chronicle_sfx",
    "synthesize_chronicle_sfx_catalog",
]
