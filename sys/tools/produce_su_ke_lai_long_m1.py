#!/usr/bin/env python3
"""Parameterized Turnkey M1-Flex V9.2 Long-Form Production Engine (`produce_su_ke_lai_long_m1.py`). Reusable, flexible production engine for `su_ke_lai` (and historical analytical) long-form (`6–12` chapters, `60–120` beats, `9–15` minutes) IMAX `2.39:1` moving-cinema documentaries. Implements the "Tựa Tựa Khuôn, Không Phải Y Đúc" (`M1-Flex V9.2`) creative preset architecture while enforcing all V4/V9.2 Non-Negotiable Quality & Anti-Dizziness Invariants: 1. `--color-preset {golden_dawn_1789,river_mist_teal_gold,monsoon_siege_contrast,imperial_torch_amber}`: - `golden_dawn_1789`: Warm golden dawn (`lift=0.18, warmth=0.14`, default for open-field dawn campaigns). - `river_mist_teal_gold`: Crisp river-fog silver-teal shadows with warm bronze/fire highlights (`lift=0.17, warmth=0.06`, ideal for naval campaigns like Bạch Đằng 938/1288, Rạch Gầm 1785). - `monsoon_siege_contrast`: High-clarity slate & ember contrast (`lift=0.16, warmth=0.09`, ideal for mountain/fortress sieges like Chi Lăng 1427, Thành Cổ). - `imperial_torch_amber`: Deep court bronze & torchlight clarity (`lift=0.19, warmth=0.16`, ideal for dynastic intrigue & strategic council episodes). 2. `--chapter-style {minimal_center_card,in_scene_cinema_title}`: - `minimal_center_card`: `3.2s–3.6s` dimmed moving-cinema card (`0.56..0.72` vignette) with tracked `CHƯƠNG I..N` + 3–4 word core title (`0` bottom subtitle sentence, `0` gold divider bar). - `in_scene_cinema_title`: Netflix-style chapter title overlay directly on the first `3.5s` of the opening chapter scene at full brightness without a separate card pause. 3. `--chain-pattern {balanced_2beat,dynamic_1_2_3beat,epic_3beat}`: - `balanced_2beat`: 2 beats per `8.0s` Flow `.mp4` clip (`0.00->3.30s` + `3.30->6.60s` unbroken playback). - `dynamic_1_2_3beat`: Adaptive pacing — 3-beat (`0.00->2.20->4.40->6.60s`) long-take chains for opening/aftermath chapters, 2-beat (`0.00->3.30->6.60s`) chains for tactical setup, and 1-beat (`0.00->5.20s` `1.0x` real-time speed) rapid cuts during battle climax chapters. - `epic_3beat`: 3 beats per `8.0s`/`10.0s` Flow `.mp4` clip (`0.00->2.20->4.40->6.60s`) for slower strategic/biographical episodes. 4. `--keyword-density <float 0.15..0.30>` (default `0.22`): - Automatically enforces sparse single-line verbatim emphasis keywords (`~18–28%` of beats, `>= 70–72%` text-free pure cinema, NEVER on the first beat of any chapter `beat_*0`, `top_word == ""` always, compact `66px@1080p / 88px@1440p` ivory-gold `#FFF5D6`). 5. `--resolution {1080p,1440p,360p}` (default `1080p` `1920x1080`; `1440p` `2560x1440` 2K; `360p` `640x360`), `--total-shards <int>` (default `8`), `--stage {build-timeline,render-shard,assemble,full-cc-srt,validate-flex-spec}`. 6. Hard-Coded Permanent Safety Locks: - `0%` Pillow-drawn 2D/3D cartoon maps (`map_dive` / `_render_3d_map_dive` permanently banned). - `0%` horizontal whip-slides (`directional_flow_chain_transition` permanently banned; only `0.0s` intra-chain continuous cut and calm stationary `0.20s` optical cross-dissolve `0px` shift). - `0` text on top/bottom pure-black IMAX `2.39:1` bars (only bottom-right `@SuKeLaiVN` logo). - `100%` moving `.mp4` video verification (`--require-moving-video`)."""
from __future__ import annotations
import argparse
import bisect
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
import wave
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
TOOLS_DIR = Path(__file__).resolve().parent; SYS_DIR = TOOLS_DIR.parent; REPO_ROOT = SYS_DIR.parent
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))
M1_FLEX_ENGINE_VERSION = '9.2.0'; M1_FLEX_PATTERN_ID = 'su_ke_lai_long_v9_2_m1_flex_engine'
DEFAULT_JOB_ID = 'vn_su_ke_lai_1789_ngoc_hoi_dong_da_full_m1'; DEFAULT_RUN_DIR = SYS_DIR / 'runs' / DEFAULT_JOB_ID
DEFAULT_SCRIPT = DEFAULT_RUN_DIR / 'script_1789_from_scratch.json'; DEFAULT_AUDIO_DIR = DEFAULT_RUN_DIR / 'audio'
DEFAULT_FRAMES_DIR = DEFAULT_RUN_DIR / 'frames'; DEFAULT_RAW_CLIPS_DIR = DEFAULT_RUN_DIR / 'raw_clips'
DEFAULT_TIMELINE = DEFAULT_RUN_DIR / 'timeline_1789_full.json'; DEFAULT_MASTER_WAV = DEFAULT_RUN_DIR / 'master_audio_1789_full.wav'
DEFAULT_SRT = DEFAULT_RUN_DIR / 'subtitles_impact_keywords.srt'; DEFAULT_FULL_CC_SRT = DEFAULT_RUN_DIR / 'subtitles_vi_full_cc.srt'
VIDEO_OUT_DIR = REPO_ROOT / 'video' / DEFAULT_JOB_ID; FINAL_FILENAME = 'mau_M1_voi_chien_1789_imax_chu_no_23_tu_chuan_full.mp4'
SHOWCASE_FILENAME = 'mau_M1_1789_10chapters_showcase.jpg'
WATERMARK_PATH = REPO_ROOT / 'sys' / 'channels' / 'su_ke_lai' / 'assets' / 'watermark_150x150.png'
FONT_DIR_CNK = REPO_ROOT / 'sys' / 'assets' / 'fonts' / 'chanh_niem_ke'; FONT_BARLOW = str(FONT_DIR_CNK / 'BarlowCondensed-ExtraBold.ttf')
FONT_OSWALD = str(FONT_DIR_CNK / 'Oswald-Bold.ttf'); FONT_MONO = str(FONT_DIR_CNK / 'IBMPlexMono-Bold.ttf')
FONT_SANS = '/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf'; CLIP_CLEAN_MAX_SEC = 6.6; CHAIN_FIRST_HALF = (0.0, 3.3)
CHAIN_SECOND_HALF = (3.3, 6.6); CHAIN_THIRD_WINDOWS = ((0.0, 2.2), (2.2, 4.4), (4.4, 6.6)); CHAIN_SINGLE_WINDOW = (0.0, 5.2)
MIN_CLIP_BYTES = 180000
PERMANENTLY_BANNED_TRANSITIONS: tuple[str, ...] = ('directional_flow_chain_transition', 'horizontal_whip_slide', 'dust_smoke_cloud', 'river_mist_map_dive', 'procedural_fog_wipe', 'procedural_mist_wipe')
PERMANENTLY_BANNED_INSERTS: tuple[str, ...] = ('map_dive', '_render_3d_map_dive', 'pillow_2d_cartoon_map', 'pillow_3d_cartoon_map')
COLOR_PRESETS: dict[str, dict[str, Any]] = {'golden_dawn_1789': {'lift': 0.18, 'warmth': 0.14, 'shadow_teal': 0.05, 'contrast': 1.14, 'gamma_ceiling': 0.85, 'description': 'Warm golden dawn (lift=0.18, warmth=0.14, default for open-field dawn campaigns like Ngọc Hồi 1789)'}, 'river_mist_teal_gold': {'lift': 0.17, 'warmth': 0.06, 'shadow_teal': 0.09, 'contrast': 1.15, 'gamma_ceiling': 0.85, 'description': 'Crisp river-fog silver-teal shadows with warm bronze/fire highlights (lift=0.17, warmth=0.06, naval campaigns like Bạch Đằng 938/1288, Rạch Gầm 1785)'}, 'monsoon_siege_contrast': {'lift': 0.16, 'warmth': 0.09, 'shadow_teal': 0.07, 'contrast': 1.18, 'gamma_ceiling': 0.85, 'description': 'High-clarity slate & ember contrast (lift=0.16, warmth=0.09, mountain/fortress sieges like Chi Lăng 1427, Thành Cổ)'}, 'imperial_torch_amber': {'lift': 0.19, 'warmth': 0.16, 'shadow_teal': 0.03, 'contrast': 1.13, 'gamma_ceiling': 0.85, 'description': 'Deep court bronze & torchlight clarity (lift=0.19, warmth=0.16, dynastic intrigue & strategic council episodes)'}}
CHAPTER_STYLES: dict[str, dict[str, Any]] = {'minimal_center_card': {'insert_card_beat': True, 'card_duration_sec': 3.6, 'in_scene_overlay_sec': 0.0, 'dim_vignette_range': (0.56, 0.72), 'card_subtitle': '', 'gold_divider_line': False, 'description': '3.2s-3.6s dimmed moving-cinema card with tracked CHƯƠNG I..N + 3-4 word core title (0 subtitle, 0 divider)'}, 'in_scene_cinema_title': {'insert_card_beat': False, 'card_duration_sec': 0.0, 'in_scene_overlay_sec': 3.5, 'dim_vignette_range': (1.0, 1.0), 'card_subtitle': '', 'gold_divider_line': False, 'description': 'Netflix-style chapter title overlay directly on the first 3.5s of the opening chapter scene at full brightness without a separate card pause'}}
CHAIN_PATTERNS: dict[str, dict[str, Any]] = {'balanced_2beat': {'default_beats_per_chain': 2, 'windows': (CHAIN_FIRST_HALF, CHAIN_SECOND_HALF), 'description': '2 beats per 8.0s Flow .mp4 clip (0.00->3.30s + 3.30->6.60s unbroken continuous playback)'}, 'dynamic_1_2_3beat': {'default_beats_per_chain': 'adaptive_1_2_3', 'windows': {1: (CHAIN_SINGLE_WINDOW,), 2: (CHAIN_FIRST_HALF, CHAIN_SECOND_HALF), 3: CHAIN_THIRD_WINDOWS}, 'description': 'Adaptive pacing: 3-beat long-take chains for opening/aftermath, 2-beat chains for setup, and 1-beat rapid cuts during battle climax chapters'}, 'epic_3beat': {'default_beats_per_chain': 3, 'windows': CHAIN_THIRD_WINDOWS, 'description': '3 beats per 8.0s/10.0s Flow .mp4 clip (0.00->2.20->4.40->6.60s) for slower strategic/biographical episodes'}}
NARRATIVE_ARCHETYPES: dict[str, dict[str, Any]] = {'blitz_campaign': {'label_vi': 'Chiến Dịch Thần Tốc (Blitz Campaign)', 'chapters_range': (8, 10), 'recommended_color_preset': 'golden_dawn_1789', 'recommended_chapter_style': 'minimal_center_card', 'recommended_chain_pattern': 'balanced_2beat', 'recommended_keyword_density': 0.22, 'examples': ('Ngọc Hồi – Đống Đa 1789', 'Chiến dịch mùa xuân 1789')}, 'siege_and_trap_anatomy': {'label_vi': 'Giải Phẫu Vây Thành & Tử Địa (Siege & Trap Anatomy)', 'chapters_range': (6, 8), 'recommended_color_preset': 'monsoon_siege_contrast', 'recommended_chapter_style': 'minimal_center_card', 'recommended_chain_pattern': 'dynamic_1_2_3beat', 'recommended_keyword_density': 0.24, 'examples': ('Chi Lăng – Xương Giang 1427', 'Vây thành Đông Quan', 'Phòng tuyến Như Nguyệt 1077')}, 'commander_rivalry_duel': {'label_vi': 'Song Đấu Kỳ Phùng Địch Thủ (Commander Rivalry Duel)', 'chapters_range': (8, 11), 'recommended_color_preset': 'imperial_torch_amber', 'recommended_chapter_style': 'in_scene_cinema_title', 'recommended_chain_pattern': 'epic_3beat', 'recommended_keyword_density': 0.2, 'examples': ('Lý Thường Kiệt vs Quách Quỳ', 'Trần Hưng Đạo vs Thoát Hoan', 'Nguyễn Huệ vs Tôn Sĩ Nghị')}, 'naval_and_river_ambush': {'label_vi': 'Thủy Chiến & Đại Phục Kích Sông Nước (Naval & River Ambush)', 'chapters_range': (7, 9), 'recommended_color_preset': 'river_mist_teal_gold', 'recommended_chapter_style': 'in_scene_cinema_title', 'recommended_chain_pattern': 'dynamic_1_2_3beat', 'recommended_keyword_density': 0.22, 'examples': ('Bạch Đằng 938', 'Bạch Đằng 1288', 'Rạch Gầm – Xoài Mút 1785')}}
RESOLUTION_SPECS: dict[str, dict[str, Any]] = {'360p': {'width': 640, 'height': 360, 'scale': 1.0, 'bar_h': 38, 'act_h': 284, 'grade_w': 640, 'grade_h': 284, 'watermark_size': 34, 'watermark_margin': 10, 'chapter_title_px': 30, 'keyword_px': 22}, '1080p': {'width': 1920, 'height': 1080, 'scale': 3.0, 'bar_h': 114, 'act_h': 852, 'grade_w': 1280, 'grade_h': 568, 'watermark_size': 84, 'watermark_margin': 30, 'chapter_title_px': 90, 'keyword_px': 66}, '1440p': {'width': 2560, 'height': 1440, 'scale': 4.0, 'bar_h': 152, 'act_h': 1136, 'grade_w': 1280, 'grade_h': 568, 'watermark_size': 112, 'watermark_margin': 36, 'chapter_title_px': 120, 'keyword_px': 88}}
WIDTH = 1920; HEIGHT = 1080; S = 3.0
FPS = 30; BAR_H = 114; ACT_H = 852
GRADE_W = 1280; GRADE_H = 568; TARGET_SR = 48000
TOTAL_SHARDS = 8; WATERMARK_SIZE = 84; WATERMARK_MARGIN = 30
CHAPTER_CARD_SEC = 3.6; IN_SCENE_CHAPTER_OVERLAY_SEC = 3.5; INTER_CHAPTER_PAUSE_SEC = 0.25
OUTRO_TAIL_SEC = 0.9; ROMANS = ('I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII')
DEFAULT_CHAPTER_META: dict[int, dict[str, str]] = {1: {'header': 'CHƯƠNG I', 'main_word': '29 VẠN QUÂN THANH', 'subtitle': '', 'tone': 'crimson'}, 2: {'header': 'CHƯƠNG II', 'main_word': 'HÀNH QUÂN THẦN TỐC', 'subtitle': '', 'tone': 'gold'}, 3: {'header': 'CHƯƠNG III', 'main_word': '5 ĐẠO QUÂN TÂY SƠN', 'subtitle': '', 'tone': 'gold'}, 4: {'header': 'CHƯƠNG IV', 'main_word': 'ĐÊM HẠ ĐỒN HÀ HỒI', 'subtitle': '', 'tone': 'gold'}, 5: {'header': 'CHƯƠNG V', 'main_word': 'TỬ ĐỊA NGỌC HỒI', 'subtitle': '', 'tone': 'crimson'}, 6: {'header': 'CHƯƠNG VI', 'main_word': 'MỘC BÀI RƠM ƯỚT', 'subtitle': '', 'tone': 'gold'}, 7: {'header': 'CHƯƠNG VII', 'main_word': 'VOI CHIẾN & HỎA HỔ', 'subtitle': '', 'tone': 'fire'}, 8: {'header': 'CHƯƠNG VIII', 'main_word': 'BIỂN LỬA ĐỐNG ĐA', 'subtitle': '', 'tone': 'fire'}, 9: {'header': 'CHƯƠNG IX', 'main_word': 'TIẾN VÀO THĂNG LONG', 'subtitle': '', 'tone': 'gold'}, 10: {'header': 'CHƯƠNG X', 'main_word': 'NƯỚC CỜ GIẢ VƯƠNG', 'subtitle': '', 'tone': 'gold'}, 11: {'header': 'CHƯƠNG XI', 'main_word': 'DI SẢN CHIẾN LƯỢC', 'subtitle': '', 'tone': 'gold'}, 12: {'header': 'CHƯƠNG XII', 'main_word': 'PHÁN XÉT LỊCH SỬ', 'subtitle': '', 'tone': 'gold'}}
_FONT_CACHE: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}; _GRADE_LUT_CACHE: dict[int, np.ndarray] = {}
_FAST_GRADE_CACHE: dict[tuple[int, int, int], tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}
_FLARE_GRID_CACHE: dict[tuple[int, int], tuple[np.ndarray, np.ndarray]] = {}
_GRAIN_RING_CACHE: dict[tuple[int, int, int, int], list[tuple[np.ndarray, np.ndarray]]] = {}
_CARD_VIGNETTE_CACHE: dict[tuple[int, int], np.ndarray] = {}; _SFX_CACHE: dict[str, np.ndarray] = {}
def get_resolution_geometry(resolution: str='1080p') -> dict[str, Any]:
    res_key = str(resolution or '1080p').strip().lower()
    if res_key not in RESOLUTION_SPECS:
        raise ValueError(f'Unsupported resolution {resolution!r}; choose from {tuple(RESOLUTION_SPECS.keys())}')
    return dict(RESOLUTION_SPECS[res_key])
def set_active_resolution(resolution: str='1080p') -> dict[str, Any]:
    global WIDTH, HEIGHT, S, BAR_H, ACT_H, GRADE_W, GRADE_H, WATERMARK_SIZE, WATERMARK_MARGIN; geom = get_resolution_geometry(resolution)
    WIDTH = int(geom['width']); HEIGHT = int(geom['height']); S = float(geom['scale'])
    BAR_H = int(geom['bar_h']); ACT_H = int(geom['act_h']); GRADE_W = int(geom['grade_w'])
    GRADE_H = int(geom['grade_h']); WATERMARK_SIZE = int(geom['watermark_size']); WATERMARK_MARGIN = int(geom['watermark_margin'])
    return geom
def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x
def _ease_out_cubic(x: float) -> float:
    t = _clamp01(x)
    return 1.0 - (1.0 - t) ** 3
def _ease_in_out_cubic(x: float) -> float:
    t = _clamp01(x)
    return 4.0 * t * t * t if t < 0.5 else 1.0 - (-2.0 * t + 2.0) ** 3 / 2.0
def get_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    key = (path, max(8, int(size)))
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = ImageFont.truetype(path, key[1])
    return _FONT_CACHE[key]
def _run(cmd: list[str], *, check: bool=True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=check, capture_output=True, text=True)
def _resolve_path(raw: str | Path | None) -> Path | None:
    if not raw:
        return None
    p = Path(str(raw))
    if not p.is_absolute():
        p = REPO_ROOT / p
    return p
def _read_wav_stereo_f32(path: Path) -> np.ndarray:
    with wave.open(str(path), 'rb') as wf:
        sr = wf.getframerate(); ch = wf.getnchannels(); sw = wf.getsampwidth()
        raw = wf.readframes(wf.getnframes())
    if sw != 2:
        raise ValueError(f'Expected 16-bit PCM WAV at {path}, got sampwidth={sw}')
    arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if ch == 1:
        stereo = np.stack([arr, arr], axis=1)
    else:
        stereo = arr.reshape(-1, ch)[:, :2]
    if sr != TARGET_SR:
        with tempfile.TemporaryDirectory(prefix='vp_sr48_') as td:
            tmp = Path(td) / 'sr48.wav'
            _run(['ffmpeg', '-y', '-v', 'error', '-i', str(path), '-ar', str(TARGET_SR), '-ac', '2', '-c:a', 'pcm_s16le', str(tmp)])
            return _read_wav_stereo_f32(tmp)
    return stereo.astype(np.float32)
def _write_wav_stereo_i16(path: Path, data: np.ndarray) -> None:
    arr = np.asarray(data, dtype=np.float32)
    if arr.ndim == 1:
        arr = np.stack([arr, arr], axis=1)
    pcm = np.clip(np.round(arr * 32767.0), -32768, 32767).astype(np.int16); path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), 'wb') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(TARGET_SR)
        wf.writeframes(pcm.tobytes())
def _extract_beat_words_acoustic(beat_wave: np.ndarray, text: str, beat_id: str, global_offset: float) -> list[dict[str, Any]]:
    """Align spoken tokens against 10ms RMS energy envelope for millisecond target_keyword sync."""
    tokens = [tok for tok in re.sub('\\[pause:[^\\]]+\\]', ' ', text or '').strip().split() if tok.strip()]
    if not tokens or not len(beat_wave):
        return []
    mono = np.sqrt(0.5 * (beat_wave[:, 0] ** 2 + beat_wave[:, 1] ** 2)); seg_dur = len(mono) / float(TARGET_SR); hop = max(1, TARGET_SR // 100)
    n_frames = len(mono) // hop
    if n_frames < len(tokens):
        step = seg_dur / len(tokens)
        return [{'beat_id': beat_id, 'word': tok, 'start': round(global_offset + i * step, 4), 'end': round(global_offset + (i + 1) * step, 4)} for i, tok in enumerate(tokens)]
    rms = np.sqrt(np.mean(mono[:n_frames * hop].reshape(n_frames, hop) ** 2, axis=1) + 1e-12); norm_rms = rms / (float(np.max(rms)) + 1e-09)
    cum_e = np.concatenate([[0.0], np.cumsum(0.72 * (norm_rms > 0.04).astype(np.float32) * (norm_rms + 0.1) + 0.28)]); total_e = float(cum_e[-1])
    w_weights = [max(1.5, len(re.sub('[^A-Za-zÀ-ỹ0-9]', '', tok))) for tok in tokens]; total_w = float(sum(w_weights)); used_w = 0.0
    prev_end = 0.0; out: list[dict[str, Any]] = []
    for tok, ww in zip(tokens, w_weights, strict=True):
        e0 = used_w / total_w * total_e; used_w += ww; e1 = used_w / total_w * total_e
        t0 = min(seg_dur, max(prev_end, int(np.searchsorted(cum_e, e0, side='left')) * hop / float(TARGET_SR)))
        t1 = min(seg_dur, max(t0 + 0.02, int(np.searchsorted(cum_e, e1, side='left')) * hop / float(TARGET_SR))); prev_end = t1
        out.append({'beat_id': beat_id, 'word': tok, 'start': round(global_offset + t0, 4), 'end': round(global_offset + t1, 4)})
    return out
def _find_word_offset(words: list[dict[str, Any]], beat_id: str, beat_start: float, needle: str) -> float:
    """Locate exact spoken offset of `target_keyword` (single-word or multi-word phrase) inside a beat."""
    raw_needle = re.sub('[^\\wÀ-ỹ\\s]', ' ', str(needle or '').lower()).strip()
    if not raw_needle:
        return 0.28
    needle_tokens = [t for t in raw_needle.split() if t]; beat_words = [w for w in words if w.get('beat_id') == beat_id]
    cleaned_words = [re.sub('[^\\wÀ-ỹ]', '', str(w.get('word', '')).lower()) for w in beat_words]
    if len(needle_tokens) > 1:
        k = len(needle_tokens)
        for i in range(0, len(cleaned_words) - k + 1):
            if cleaned_words[i:i + k] == needle_tokens:
                return max(0.0, float(beat_words[i]['start']) - beat_start)
    first = needle_tokens[0]
    for idx_w, cw in enumerate(cleaned_words):
        if cw == first or (len(first) >= 3 and first in cw):
            return max(0.0, float(beat_words[idx_w]['start']) - beat_start)
    for tok in needle_tokens[1:]:
        if len(tok) < 3:
            continue
        for idx_w, cw in enumerate(cleaned_words):
            if cw == tok or tok in cw:
                return max(0.0, float(beat_words[idx_w]['start']) - beat_start)
    return 0.28
def _synth_tactile_sfx(kind: str) -> np.ndarray:
    """Synthesize stereo 48kHz period-authentic tactile SFX hits & chapter gongs."""
    if kind in _SFX_CACHE:
        return _SFX_CACHE[kind]
    rng = np.random.default_rng(1789 + sum((ord(c) for c in kind)))
    if kind == 'chapter_gong':
        dur = 2.95; n = int(round(dur * TARGET_SR)); t = np.arange(n, dtype=np.float32) / float(TARGET_SR)
        td = np.maximum(0.0, t - 0.05); drum_env = (t >= 0.05).astype(np.float32) * np.exp(-td * 3.6)
        drum_ph = 2.0 * math.pi * (42.0 * td + 52.0 * (1.0 - np.exp(-td * 12.0)) / 12.0); drum = 0.85 * np.sin(drum_ph) * drum_env
        tg = np.maximum(0.0, t - 0.1); gong_env = (t >= 0.1).astype(np.float32) * (1.0 - np.exp(-tg * 9.0)) * np.exp(-tg * 1.15)
        tail_fade = np.clip((dur - t) / 0.35, 0.0, 1.0)
        gong = (0.5 * np.sin(2.0 * math.pi * 110.0 * tg + 0.4 * np.sin(2.0 * math.pi * 2.2 * tg)) + 0.34 * np.sin(2.0 * math.pi * 165.4 * tg) + 0.24 * np.sin(2.0 * math.pi * 238.5 * tg) * np.exp(-tg * 0.8) + 0.16 * np.sin(2.0 * math.pi * 362.0 * tg) * np.exp(-tg * 1.5) + 0.1 * np.sin(2.0 * math.pi * 518.0 * tg) * np.exp(-tg * 2.4)) * gong_env
        noise = rng.normal(0.0, 0.18, size=n).astype(np.float32)
        lp = np.convolve(noise, np.ones(64, dtype=np.float32) / 64.0, mode='same') * gong_env; mono = (drum + gong * 0.92 + lp * 0.35) * tail_fade
    elif kind == 'war_drum':
        dur = 0.5; n = int(round(dur * TARGET_SR)); t = np.arange(n, dtype=np.float32) / float(TARGET_SR)
        phase = 2.0 * math.pi * (46.0 * t + 56.0 * (1.0 - np.exp(-t * 14.0)) / 14.0); body = np.sin(phase) * np.exp(-t * 4.5)
        bronze = 0.28 * np.sin(2.0 * math.pi * 168.0 * t) * np.exp(-t * 6.8)
        hit = rng.normal(0.0, 0.25, size=n).astype(np.float32) * np.exp(-t * 62.0); mono = body + bronze + hit
    elif kind == 'elephant_trumpet':
        dur = 0.62; n = int(round(dur * TARGET_SR)); t = np.arange(n, dtype=np.float32) / float(TARGET_SR)
        stomp = 0.85 * np.sin(2.0 * math.pi * (44.0 * t + 48.0 * (1.0 - np.exp(-t * 12.0)) / 12.0)) * np.exp(-t * 5.2)
        s_tr = np.maximum(0.0, np.sin(math.pi * np.clip(t / 0.48, 0.0, 1.0))); f_tr = 310.0 + 210.0 * s_tr ** 0.85 - 80.0 * (t / dur)
        ph = 2.0 * math.pi * np.cumsum(f_tr) / float(TARGET_SR); s_env = np.maximum(0.0, np.sin(math.pi * np.clip(t / 0.55, 0.0, 1.0)))
        env = s_env ** 1.2 * np.exp(-t * 2.2); brass = (0.42 * np.sin(ph) + 0.28 * np.sin(2.0 * ph) + 0.16 * np.sin(3.0 * ph)) * env
        mono = stomp + brass * 0.72
    elif kind == 'fire_roar':
        dur = 0.56; n = int(round(dur * TARGET_SR)); t = np.arange(n, dtype=np.float32) / float(TARGET_SR)
        noise = rng.normal(0.0, 1.0, size=n).astype(np.float32); lp = np.convolve(noise, np.ones(26, dtype=np.float32) / 26.0, mode='same')
        env = (1.0 - np.exp(-t * 28.0)) * np.exp(-t * 4.4)
        sub = 0.72 * np.sin(2.0 * math.pi * (52.0 * t + 44.0 * (1.0 - np.exp(-t * 16.0)) / 16.0)) * np.exp(-t * 6.5)
        crackle = (rng.uniform(0, 1, size=n) > 0.992).astype(np.float32) * rng.normal(0, 0.9, size=n) * env
        mono = lp * env * 1.35 + sub + crackle * 0.45
    else:
        dur = 0.48; n = int(round(dur * TARGET_SR)); t = np.arange(n, dtype=np.float32) / float(TARGET_SR)
        sub = 0.78 * np.sin(2.0 * math.pi * (48.0 * t + 50.0 * (1.0 - np.exp(-t * 15.0)) / 15.0)) * np.exp(-t * 5.5)
        ring = 0.34 * np.sin(2.0 * math.pi * 520.0 * t) * np.exp(-t * 8.0) + 0.22 * np.sin(2.0 * math.pi * 885.0 * t) * np.exp(-t * 11.0) + 0.14 * np.sin(2.0 * math.pi * 1410.0 * t) * np.exp(-t * 15.0)
        mono = sub + ring
    mono = np.nan_to_num(mono, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32); peak = float(np.max(np.abs(mono))) + 1e-06
    mono = (mono / peak).astype(np.float32); stereo = np.stack([mono, mono * 0.96], axis=1); _SFX_CACHE[kind] = stereo
    return stereo
def _synth_heroic_war_drum_undertone(total_n: int, beats: list[dict[str, Any]]) -> np.ndarray:
    """Synthesize subtle, dignified war-drum & low-brass undertone ducked cleanly under voice."""; bed = np.zeros((total_n, 2), dtype=np.float32)
    nd = int(round(0.4 * TARGET_SR)); td = np.arange(nd, dtype=np.float32) / float(TARGET_SR)
    ph = 2.0 * math.pi * (56.0 * td + 36.0 * (1.0 - np.exp(-td * 12.0)) / 12.0)
    stroke_m = (np.sin(ph) * np.exp(-td * 5.6) + 0.16 * np.sin(2.0 * math.pi * 112.0 * td) * np.exp(-td * 8.0)).astype(np.float32)
    stroke_m *= np.minimum(1.0, td / 0.004); stroke_st = np.stack([stroke_m * 0.96, np.roll(stroke_m, 7) * 0.96], axis=1)
    for b in beats:
        t0 = float(b['out_start']); t1 = float(b['out_end']); ch = int(b['chapter_idx'])
        if b['kind'] == 'chapter_card':
            continue
        if ch in (6, 7, 8):
            step_s = 60.0 / 106.0; amp = 0.85
        elif ch in (4, 5):
            step_s = 60.0 / 92.0; amp = 0.65
        else:
            step_s = 60.0 / 76.0; amp = 0.48
        k = 0; t_cur = t0 + 0.15
        while t_cur < t1 - 0.12:
            i0 = int(round(t_cur * TARGET_SR)); ln = min(nd, total_n - i0)
            if ln > 0:
                w = amp * (1.0 if k % 4 == 0 else 0.58); bed[i0:i0 + ln] += stroke_st[:ln] * w
            t_cur += step_s; k += 1
    tt = np.arange(total_n, dtype=np.float32) / float(TARGET_SR)
    drone = (0.14 * np.sin(2.0 * math.pi * 73.42 * tt) + 0.07 * np.sin(2.0 * math.pi * 146.83 * tt)).astype(np.float32); bed[:, 0] += drone
    bed[:, 1] += drone * 0.98; pk = float(np.max(np.abs(bed))) + 1e-06
    return (bed / pk).astype(np.float32)
def _measure_ebur128(media_path: Path) -> dict[str, float]:
    res = _run(['ffmpeg', '-v', 'info', '-i', str(media_path), '-af', 'ebur128=peak=true', '-f', 'null', '-'])
    m_i = re.findall('^\\s*I:\\s*(-?\\d+(?:\\.\\d+)?)\\s+LUFS', res.stderr, re.MULTILINE)
    m_tp = re.findall('^\\s*Peak:\\s*(-?\\d+(?:\\.\\d+)?)\\s+dBFS', res.stderr, re.MULTILINE)
    return {'integrated_lufs': float(m_i[-1]) if m_i else 0.0, 'true_peak_dbtp': float(m_tp[-1]) if m_tp else 0.0}
def _normalize_audio_master(in_wav: Path, out_wav: Path, *, target_lufs: float=-11.0, max_tp_db: float=-1.25) -> dict[str, float]:
    """2-pass EBU R128 loudnorm + iterative polish to hit -11.0 LUFS (±0.2) and <= -1.25 dBTP headroom."""
    p1 = _run(['ffmpeg', '-y', '-i', str(in_wav), '-af', f'loudnorm=I={target_lufs:.1f}:TP={max_tp_db:.2f}:LRA=7:print_format=json', '-f', 'null', '-'])
    m = re.search('\\{[^{}]*\\"input_i\\"[^{}]*\\}', p1.stderr, re.DOTALL)
    if not m:
        raise RuntimeError(f'loudnorm pass 1 failed: {p1.stderr[-400:]}')
    st = json.loads(m.group(0)); limit_lin = 10.0 ** ((max_tp_db - 0.15) / 20.0)
    af2 = f"loudnorm=I={target_lufs:.1f}:TP={max_tp_db:.2f}:LRA=7:linear=true:measured_I={st['input_i']}:measured_TP={st['input_tp']}:measured_LRA={st['input_lra']}:measured_thresh={st['input_thresh']}:offset={st['target_offset']}:print_format=json,aresample=192000,alimiter=limit={limit_lin:.6f}:attack=2:release=40:level=disabled,aresample={TARGET_SR}"
    _run(['ffmpeg', '-y', '-v', 'error', '-i', str(in_wav), '-af', af2, '-ar', str(TARGET_SR), '-ac', '2', '-c:a', 'pcm_s16le', str(out_wav)])
    eb = _measure_ebur128(out_wav)
    for _ in range(4):
        if abs(eb['integrated_lufs'] - target_lufs) <= 0.2 and eb['true_peak_dbtp'] <= -1.0:
            break
        tmp = out_wav.with_suffix('.polish.wav'); delta = target_lufs - eb['integrated_lufs']
        af_p = f'volume={delta:+.3f}dB,aresample=192000,alimiter=limit={limit_lin:.6f}:attack=2:release=40:level=disabled,aresample={TARGET_SR}'
        _run(['ffmpeg', '-y', '-v', 'error', '-i', str(out_wav), '-af', af_p, '-ar', str(TARGET_SR), '-ac', '2', '-c:a', 'pcm_s16le', str(tmp)])
        shutil.move(str(tmp), str(out_wav)); eb = _measure_ebur128(out_wav)
    return eb
def validate_m1_flex_options(*, color_preset: str='golden_dawn_1789', chapter_style: str='minimal_center_card', chain_pattern: str='balanced_2beat', keyword_density: float=0.22, resolution: str='1080p', total_shards: int=8, archetype: str='blitz_campaign') -> dict[str, Any]:
    if color_preset not in COLOR_PRESETS:
        raise ValueError(f'Unsupported --color-preset {color_preset!r}; valid: {tuple(COLOR_PRESETS.keys())}')
    if chapter_style not in CHAPTER_STYLES:
        raise ValueError(f'Unsupported --chapter-style {chapter_style!r}; valid: {tuple(CHAPTER_STYLES.keys())}')
    if chain_pattern not in CHAIN_PATTERNS:
        raise ValueError(f'Unsupported --chain-pattern {chain_pattern!r}; valid: {tuple(CHAIN_PATTERNS.keys())}')
    kd = float(keyword_density)
    if kd < 0.15 - 1e-06 or kd > 0.3 + 1e-06:
        raise ValueError(f'--keyword-density must be between 0.15 and 0.30 (got {keyword_density})')
    if resolution not in RESOLUTION_SPECS:
        raise ValueError(f'Unsupported --resolution {resolution!r}; valid: {tuple(RESOLUTION_SPECS.keys())}')
    if int(total_shards) < 1 or int(total_shards) > 32:
        raise ValueError(f'--total-shards must be in 1..32 (got {total_shards})')
    if archetype not in NARRATIVE_ARCHETYPES:
        raise ValueError(f'Unsupported --archetype {archetype!r}; valid: {tuple(NARRATIVE_ARCHETYPES.keys())}')
    return {'engine_version': M1_FLEX_ENGINE_VERSION, 'pattern_id': M1_FLEX_PATTERN_ID, 'color_preset': color_preset, 'color_params': dict(COLOR_PRESETS[color_preset]), 'chapter_style': chapter_style, 'chapter_style_params': dict(CHAPTER_STYLES[chapter_style]), 'chain_pattern': chain_pattern, 'chain_pattern_params': dict(CHAIN_PATTERNS[chain_pattern]), 'keyword_density': round(kd, 4), 'resolution': resolution, 'resolution_geometry': get_resolution_geometry(resolution), 'total_shards': int(total_shards), 'archetype': archetype, 'archetype_params': dict(NARRATIVE_ARCHETYPES[archetype]), 'safety_locks': {'pillow_2d_3d_cartoon_maps_pct': 0.0, 'map_dive_allowed': False, 'horizontal_whip_slides_pct': 0.0, 'directional_flow_chain_transition_allowed': False, 'black_bar_text_allowed': False, 'chapter_opening_beat_keyword_allowed': False, 'two_tier_top_word_allowed': False, 'chapter_card_subtitle_allowed': False, 'chapter_card_gold_divider_allowed': False}}
def _extract_fallback_keyword(text: str) -> str:
    """Extract a crisp 2-3 word uppercase verbatim phrase from spoken narration text when promoting a beat."""
    cleaned = re.sub('\\[pause:[^\\]]+\\]', ' ', text or ''); tokens = [re.sub('[^\\wÀ-ỹ]', '', tok) for tok in cleaned.split()]
    tokens = [t for t in tokens if len(t) >= 2]
    if not tokens:
        return 'ĐẠI VIỆT'
    for i, tok in enumerate(tokens):
        if any((ch.isdigit() for ch in tok)) and i + 1 < len(tokens):
            span = tokens[i:min(len(tokens), i + 3)]
            return ' '.join(span).upper()
    mid = max(0, min(len(tokens) - 2, len(tokens) // 3)); span = tokens[mid:min(len(tokens), mid + 2)]
    return ' '.join(span).upper()
def enforce_sparse_keyword_density(grouped: dict[int, list[tuple[int, dict[str, Any]]]], *, keyword_density: float=0.22) -> dict[int, tuple[bool, str, str]]:
    """Enforce sparse single-line verbatim keyword density (`0.15..0.30`) across all narration beats. Invariants enforced: 1. First beat of EVERY chapter (`local_pos == 0` / `beat_*0`) is ALWAYS `show_keyword=False, main_word=""`. 2. `top_word` is ALWAYS `""` (single-line only). 3. Total active keyword count matches `round(total_beats * keyword_density)` within `[15%, 30%]`, distributed evenly across chapters with `>= 2` beats spacing whenever possible."""
    kd = float(keyword_density)
    if kd < 0.15 - 1e-06 or kd > 0.3 + 1e-06:
        raise ValueError(f'keyword_density must be in [0.15, 0.30], got {keyword_density}')
    chapter_ids = sorted(grouped.keys()); all_beats: list[tuple[int, int, int, dict[str, Any]]] = []
    for cidx in chapter_ids:
        for local_pos, (g_idx, b) in enumerate(grouped[cidx]):
            all_beats.append((cidx, local_pos, g_idx, b))
    total_n = len(all_beats)
    if total_n == 0:
        return {}
    min_k = max(1, int(math.ceil(total_n * 0.15 - 1e-06))); max_k = max(min_k, int(math.floor(total_n * 0.3 + 1e-06)))
    target_k = max(min_k, min(max_k, int(round(total_n * kd)))); initial_active: list[int] = []; candidate_words: dict[int, tuple[str, str]] = {}
    for cidx, local_pos, g_idx, b in all_beats:
        bid = str(b.get('beat_id') or f'beat_{g_idx:03d}')
        is_opener = local_pos == 0 or bool(re.fullmatch('beat_\\d*0', bid) and len(grouped[cidx]) == 10 and (local_pos == 0))
        raw_main = str(b.get('main_word') or '').strip().upper(); raw_target = str(b.get('target_keyword') or b.get('sync_word') or '').strip()
        text = str(b.get('text') or b.get('tts_text') or b.get('display_text') or '').strip()
        if not raw_main:
            raw_main = raw_target.upper() if raw_target else _extract_fallback_keyword(text)
        if not raw_target:
            raw_target = raw_main.split()[0] if raw_main else ''
        candidate_words[g_idx] = (raw_main, raw_target)
        if not is_opener and bool(b.get('show_keyword', bool(b.get('main_word')))) and bool(str(b.get('main_word') or '').strip()):
            initial_active.append(g_idx)
    selected_set: set[int] = set(initial_active)
    if len(selected_set) > target_k:
        ordered_active = sorted(selected_set)
        keep_indices = [ordered_active[int(round(i * (len(ordered_active) - 1) / max(1, target_k - 1)))] for i in range(target_k)] if target_k > 1 else [ordered_active[len(ordered_active) // 2]]
        selected_set = set(keep_indices)
        while len(selected_set) < target_k:
            for g in ordered_active:
                if g not in selected_set:
                    selected_set.add(g)
                    if len(selected_set) == target_k:
                        break
    elif len(selected_set) < target_k:
        eligible_by_ch: dict[int, list[int]] = {}
        for cidx in chapter_ids:
            ch_list = grouped[cidx]; preferred_positions = [2, 5, 8, 3, 6, 4, 7, 1, 9] + list(range(10, len(ch_list))); ordered_g: list[int] = []
            for lp in preferred_positions:
                if 1 <= lp < len(ch_list):
                    ordered_g.append(ch_list[lp][0])
            eligible_by_ch[cidx] = ordered_g
        for min_gap in (2, 1, 0):
            made_progress = True
            while len(selected_set) < target_k and made_progress:
                made_progress = False
                for cidx in sorted(chapter_ids, key=lambda c: sum((1 for g, _ in grouped[c] if g in selected_set))):
                    if len(selected_set) >= target_k:
                        break
                    for g in eligible_by_ch.get(cidx, []):
                        if g in selected_set:
                            continue
                        if all((abs(g - sg) > min_gap for sg in selected_set)):
                            selected_set.add(g); made_progress = True; break
    decisions: dict[int, tuple[bool, str, str]] = {}
    for cidx, local_pos, g_idx, _ in all_beats:
        if local_pos == 0 or g_idx not in selected_set:
            decisions[g_idx] = (False, '', '')
        else:
            mw, tw = candidate_words[g_idx]; decisions[g_idx] = (True, mw, tw)
    return decisions
def plan_chain_assignments(grouped: dict[int, list[tuple[int, dict[str, Any]]]], *, chain_pattern: str='balanced_2beat') -> dict[int, dict[str, Any]]:
    """Assign each narration beat `g_idx` to a continuous video chain and clip playback window."""
    if chain_pattern not in CHAIN_PATTERNS:
        raise ValueError(f'Unsupported chain_pattern {chain_pattern!r}')
    chapter_ids = sorted(grouped.keys()); n_chapters = len(chapter_ids); assignments: dict[int, dict[str, Any]] = {}
    chain_counter = 0
    for ch_pos, cidx in enumerate(chapter_ids):
        ch_beats = grouped[cidx]; g_indices = [g_idx for g_idx, _ in ch_beats]; idx_cursor = 0
        if chain_pattern == 'balanced_2beat':
            chunk_sizes = [2] * ((len(g_indices) + 1) // 2)
        elif chain_pattern == 'epic_3beat':
            chunk_sizes = []; rem = len(g_indices)
            while rem > 0:
                sz = 3 if rem >= 3 else rem; chunk_sizes.append(sz); rem -= sz
        else:
            chunk_sizes = []; rem = len(g_indices)
            if n_chapters == 1:
                cycle = [3, 2, 1]; ci = 0
                while rem > 0:
                    sz = min(rem, cycle[ci % len(cycle)]); chunk_sizes.append(sz); rem -= sz
                    ci += 1
            elif ch_pos == 0 or (n_chapters >= 3 and ch_pos == n_chapters - 1):
                while rem > 0:
                    sz = 3 if rem >= 3 else 2 if rem == 2 else 1; chunk_sizes.append(sz); rem -= sz
            elif n_chapters >= 3 and int(n_chapters * 0.55) <= ch_pos <= int(n_chapters * 0.8) or (n_chapters == 2 and ch_pos == 1):
                while rem > 0:
                    sz = 1; chunk_sizes.append(sz); rem -= sz
            else:
                while rem > 0:
                    sz = 2 if rem >= 2 else 1; chunk_sizes.append(sz); rem -= sz
        for c_size in chunk_sizes:
            group = g_indices[idx_cursor:idx_cursor + c_size]
            if not group:
                break
            idx_cursor += len(group); eff_len = len(group); chain_id = f'chain_{chain_counter:02d}'
            if eff_len == 1:
                windows = (CHAIN_SINGLE_WINDOW,)
            elif eff_len == 2:
                windows = (CHAIN_FIRST_HALF, CHAIN_SECOND_HALF)
            else:
                windows = CHAIN_THIRD_WINDOWS
            for slot, g_idx in enumerate(group):
                w0, w1 = windows[min(slot, len(windows) - 1)]
                assignments[g_idx] = {'chain_idx': chain_counter, 'video_chain_id': chain_id, 'chain_length': eff_len, 'chain_slot': slot, 'clip_start_sec': w0, 'clip_end_sec': w1}
            chain_counter += 1
    return assignments
def _parse_script_1789(script_path: Path) -> tuple[dict[int, dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    data = json.loads(script_path.read_text(encoding='utf-8')); chapters_map: dict[int, dict[str, Any]] = {}
    for idx_c, ch in enumerate(data.get('chapters') or data.get('chapter_cards') or [], start=1):
        cidx = int(ch.get('chapter_index') or ch.get('chapter_idx') or ch.get('index') or idx_c); chapters_map[cidx] = dict(ch)
    if isinstance(data.get('beats'), list) and data['beats']:
        beats_raw = list(data['beats'])
    elif isinstance(data.get('chapters'), list):
        beats_raw = []
        for idx_c, ch in enumerate(data['chapters'], start=1):
            cidx = int(ch.get('chapter_index') or ch.get('chapter_idx') or idx_c)
            for b in ch.get('beats') or []:
                merged = dict(b); merged.setdefault('chapter_index', cidx); merged.setdefault('chapter_header', ch.get('chapter_header') or ch.get('header'))
                beats_raw.append(merged)
    else:
        raise RuntimeError(f'Could not locate beats in {script_path}')
    script_cfg = dict(data.get('m1_flex_config') or {})
    for k in ('color_preset', 'chapter_style', 'chain_pattern', 'keyword_density', 'resolution', 'archetype', 'job_id'):
        if k in data and k not in script_cfg:
            script_cfg[k] = data[k]
    return (chapters_map, beats_raw, script_cfg)
def _infer_tone(sfx_type: str, chapter_idx: int, top_word: str, main_word: str) -> str:
    txt = f'{top_word} {main_word}'.lower()
    if sfx_type == 'fire_roar' or any((k in txt for k in ('lửa', 'hỏa', 'cháy', '900', 'thiêu', 'đại bác'))):
        return 'fire'
    if chapter_idx in (1, 5) or any((k in txt for k in ('tử địa', '29 vạn', '20 vạn', 'tự vẫn', 'đứt gãy', 'sát'))):
        return 'crimson'
    return 'gold'
def _fmt_srt_ts(sec: float) -> str:
    ms_total = max(0, int(round(sec * 1000.0))); hh = ms_total // 3600000; mm = ms_total % 3600000 // 60000
    ss = ms_total % 60000 // 1000; ms = ms_total % 1000
    return f'{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}'
def write_impact_keywords_srt(timeline: dict[str, Any], srt_path: Path) -> None:
    lines: list[str] = []; idx = 1
    for b in timeline['beats']:
        if b['kind'] == 'chapter_card':
            t0 = float(b['hit_sec']); t1 = max(t0 + 0.5, float(b['hold_end_sec'])); lines.append(str(idx))
            lines.append(f'{_fmt_srt_ts(t0)} --> {_fmt_srt_ts(t1)}'); lines.append(str(b['top_word'])); lines.append(str(b['main_word']))
            lines.append(''); idx += 1
        else:
            in_scene_ch = b.get('in_scene_chapter_title')
            if isinstance(in_scene_ch, dict) and in_scene_ch.get('main_word'):
                t0 = float(b['out_start']) + 0.12; t1 = min(float(b['out_end']) - 0.1, float(b['out_start']) + float(in_scene_ch.get('duration_sec', 3.5)))
                lines.append(str(idx)); lines.append(f'{_fmt_srt_ts(t0)} --> {_fmt_srt_ts(max(t0 + 0.5, t1))}')
                lines.append(str(in_scene_ch.get('header') or f"CHƯƠNG {b.get('chapter_roman', 'I')}")); lines.append(str(in_scene_ch['main_word']))
                lines.append(''); idx += 1
            if not b.get('show_keyword') or not str(b.get('main_word', '')).strip():
                continue
            t0 = float(b['hit_sec']); t1 = max(t0 + 0.5, float(b['hold_end_sec'])); lines.append(str(idx))
            lines.append(f'{_fmt_srt_ts(t0)} --> {_fmt_srt_ts(t1)}'); lines.append(str(b['main_word'])); lines.append('')
            idx += 1
    srt_path.parent.mkdir(parents=True, exist_ok=True); srt_path.write_text('\n'.join(lines), encoding='utf-8')
def write_full_cc_srt(timeline: dict[str, Any] | Path, full_cc_srt_path: Path) -> dict[str, Any]:
    """Generate full closed-caption Vietnamese narration `.srt` (`subtitles_vi_full_cc.srt`) for YouTube CC."""
    if isinstance(timeline, Path):
        data = json.loads(timeline.read_text(encoding='utf-8'))
    else:
        data = timeline
    lines: list[str] = []; idx = 1; narr_cues = 0
    for b in data.get('beats', []):
        t0 = float(b['out_start']); t1 = max(t0 + 0.45, float(b['out_end']) - 0.04)
        if b['kind'] == 'chapter_card':
            header = str(b.get('top_word') or b.get('chapter_header') or '').strip(); title = str(b.get('main_word') or '').strip()
            lbl = f'[{header} — {title}]' if header and title else f'[{header or title}]'; lines.append(str(idx))
            lines.append(f'{_fmt_srt_ts(t0)} --> {_fmt_srt_ts(t1)}'); lines.append(unicodedata.normalize('NFC', lbl)); lines.append('')
            idx += 1
        else:
            raw_txt = str(b.get('display_text') or '').strip()
            clean_txt = unicodedata.normalize('NFC', re.sub('\\s+', ' ', re.sub('\\[pause:[^\\]]+\\]', ' ', raw_txt)).strip())
            if not clean_txt:
                continue
            lines.append(str(idx)); lines.append(f'{_fmt_srt_ts(t0)} --> {_fmt_srt_ts(t1)}'); lines.append(clean_txt)
            lines.append(''); idx += 1; narr_cues += 1
    full_cc_srt_path.parent.mkdir(parents=True, exist_ok=True); full_cc_srt_path.write_text('\n'.join(lines), encoding='utf-8')
    return {'full_cc_srt': str(full_cc_srt_path), 'total_cues': idx - 1, 'narration_cues': narr_cues}
def _resolve_beat_video_clip(raw_clips_dir: Path, beat_id: str, g_idx: int, *, chain_info: dict[str, Any] | None=None, is_chapter_card: bool=False) -> tuple[Path | None, float, float, str]:
    """Resolve real moving `.mp4` clip for a beat honoring the active `--chain-pattern`."""
    if chain_info is not None:
        chain_idx = int(chain_info['chain_idx']); chain_id = str(chain_info['video_chain_id']); cs = float(chain_info['clip_start_sec'])
        ce = float(chain_info['clip_end_sec'])
    else:
        chain_idx = max(0, int(g_idx) // 2); chain_id = f'chain_{chain_idx:02d}'
        cs, ce = CHAIN_FIRST_HALF if is_chapter_card or int(g_idx) % 2 == 0 else CHAIN_SECOND_HALF
    beat_mp4 = raw_clips_dir / f'{beat_id}.mp4'
    if not is_chapter_card and beat_mp4.is_file() and (beat_mp4.stat().st_size >= MIN_CLIP_BYTES):
        return (beat_mp4.resolve(), cs, min(CLIP_CLEAN_MAX_SEC, ce), chain_id)
    chain_mp4 = raw_clips_dir / f'{chain_id}.mp4'
    if chain_mp4.is_file() and chain_mp4.stat().st_size >= MIN_CLIP_BYTES:
        if is_chapter_card:
            return (chain_mp4.resolve(), CHAIN_FIRST_HALF[0], CHAIN_FIRST_HALF[1], chain_id)
        return (chain_mp4.resolve(), cs, min(CLIP_CLEAN_MAX_SEC, ce), chain_id)
    fallback_idx = max(0, int(g_idx) // 2); fallback_mp4 = raw_clips_dir / f'chain_{fallback_idx:02d}.mp4'
    if fallback_mp4.is_file() and fallback_mp4.stat().st_size >= MIN_CLIP_BYTES:
        if is_chapter_card:
            return (fallback_mp4.resolve(), CHAIN_FIRST_HALF[0], CHAIN_FIRST_HALF[1], chain_id)
        return (fallback_mp4.resolve(), cs, min(CLIP_CLEAN_MAX_SEC, ce), chain_id)
    return (None, cs, min(CLIP_CLEAN_MAX_SEC, ce), chain_id)
def build_timeline_and_master_audio(script_path: Path, audio_dir: Path, frames_dir: Path, timeline_path: Path, master_wav_path: Path, srt_path: Path, video_out_dir: Path, raw_clips_dir: Path=DEFAULT_RAW_CLIPS_DIR, *, color_preset: str | None=None, chapter_style: str | None=None, chain_pattern: str | None=None, keyword_density: float | None=None, resolution: str | None=None, total_shards: int | None=None, archetype: str | None=None, full_cc_srt_path: Path | None=None, skip_audio_master: bool=False) -> dict[str, Any]:
    t0 = time.time(); chapters_map, beats_raw, script_cfg = _parse_script_1789(script_path)
    eff_archetype = str(archetype or script_cfg.get('archetype') or 'blitz_campaign').strip().lower()
    arch_defaults = NARRATIVE_ARCHETYPES.get(eff_archetype, NARRATIVE_ARCHETYPES['blitz_campaign'])
    eff_color_preset = str(color_preset or script_cfg.get('color_preset') or arch_defaults['recommended_color_preset']).strip().lower()
    eff_chapter_style = str(chapter_style or script_cfg.get('chapter_style') or 'minimal_center_card').strip().lower()
    eff_chain_pattern = str(chain_pattern or script_cfg.get('chain_pattern') or 'balanced_2beat').strip().lower()
    eff_kw_density = float(keyword_density if keyword_density is not None else script_cfg.get('keyword_density', 0.22))
    eff_resolution = str(resolution or script_cfg.get('resolution') or '1080p').strip().lower()
    eff_shards = int(total_shards if total_shards is not None else script_cfg.get('total_shards', TOTAL_SHARDS))
    flex_spec = validate_m1_flex_options(color_preset=eff_color_preset, chapter_style=eff_chapter_style, chain_pattern=eff_chain_pattern, keyword_density=eff_kw_density, resolution=eff_resolution, total_shards=eff_shards, archetype=eff_archetype)
    geom = set_active_resolution(eff_resolution); color_params = COLOR_PRESETS[eff_color_preset]
    chapter_params = CHAPTER_STYLES[eff_chapter_style]; grouped: dict[int, list[tuple[int, dict[str, Any]]]] = {}
    for g_idx, b in enumerate(beats_raw):
        cidx = int(b.get('chapter_index') or b.get('chapter_idx') or g_idx // 10 + 1); grouped.setdefault(cidx, []).append((g_idx, b))
    chapter_ids = sorted(grouped.keys())
    if not chapter_ids:
        raise RuntimeError(f'No chapters found in {script_path}')
    kw_decisions = enforce_sparse_keyword_density(grouped, keyword_density=eff_kw_density)
    chain_assignments = plan_chain_assignments(grouped, chain_pattern=eff_chain_pattern); wav_waves: dict[str, np.ndarray] = {}
    missing_audio: list[str] = []; missing_frames: list[str] = []
    for g_idx, b in enumerate(beats_raw):
        bid = str(b.get('beat_id') or f'beat_{g_idx:03d}'); wp = audio_dir / f'{bid}.wav'; fp = frames_dir / f'{bid}.png'
        if not wp.is_file() or wp.stat().st_size < 1000:
            missing_audio.append(str(wp))
        else:
            wav_waves[bid] = _read_wav_stereo_f32(wp)
        if not fp.is_file() or fp.stat().st_size < 500:
            missing_frames.append(str(fp))
    if missing_audio:
        raise FileNotFoundError(f'Missing {len(missing_audio)} beat WAV(s), first 5: {missing_audio[:5]}')
    if missing_frames:
        print(f'[build_timeline] WARN: {len(missing_frames)} beat PNG(s) not yet on disk (first 5: {missing_frames[:5]}); proceeding with audio-driven timeline.', flush=True)
    beats_out: list[dict[str, Any]] = []; chapters_out: list[dict[str, Any]] = []; cur_frame = 0
    beat_global_idx = 0
    for ch_pos, cidx in enumerate(chapter_ids):
        ch_beats = grouped[cidx]; roman = ROMANS[cidx - 1] if 1 <= cidx <= len(ROMANS) else str(cidx); ch_meta_raw = chapters_map.get(cidx, {})
        ch_def = DEFAULT_CHAPTER_META.get(cidx, {}); first_beat = ch_beats[0][1]; first_g_idx = ch_beats[0][0]
        first_bid = str(first_beat.get('beat_id') or f'beat_{first_g_idx:03d}'); header = f'CHƯƠNG {roman}'; card_top = f'CHƯƠNG {roman}'
        card_main = str(ch_meta_raw.get('main_word') or ch_meta_raw.get('title_main') or ch_meta_raw.get('title') or ch_def.get('main_word') or header).strip().upper()
        card_sub = ''; card_tone = str(ch_meta_raw.get('tone') or ch_def.get('tone') or 'gold').lower(); ch_start_frame = cur_frame
        ch_start_sec = cur_frame / float(FPS)
        if chapter_params['insert_card_beat']:
            card_frames = int(round(float(chapter_params['card_duration_sec']) * FPS)); card_end_frame = cur_frame + card_frames
            card_start_sec = cur_frame / float(FPS); card_end_sec = card_end_frame / float(FPS)
            card_vpath, card_cs, card_ce, card_vcid = _resolve_beat_video_clip(raw_clips_dir, first_bid, first_g_idx, chain_info=chain_assignments.get(first_g_idx), is_chapter_card=True)
            beats_out.append({'idx': beat_global_idx, 'kind': 'chapter_card', 'chapter_style': eff_chapter_style, 'chapter_idx': cidx, 'chapter_roman': roman, 'chapter_header': header, 'beat_id': f'CH{cidx:02d}_CARD', 'audio_wav_src': '', 'out_start': round(card_start_sec, 6), 'out_end': round(card_end_sec, 6), 'start_frame': cur_frame, 'end_frame': card_end_frame, 'display_text': '', 'show_keyword': True, 'top_word': card_top, 'main_word': card_main, 'card_subtitle': '', 'gold_divider_line': False, 'hit_sec': round(card_start_sec + 0.15, 6), 'hold_end_sec': round(card_end_sec - 0.25, 6), 'tone': card_tone, 'sfx_kind': 'chapter_gong', 'anchor_x': int(round(320 * S)), 'anchor_y': int(round(180 * S)), 'align': 'center', 'micro_tag': '', 'chain_group_id': '', 'chain_role': 'chapter_card', 'use_3d_map_dive': False, 'map_theme': '', 'primary_media_path': str((frames_dir / f'{first_bid}.png').resolve()), 'video_clip_path': str(card_vpath) if card_vpath else '', 'clip_start_sec': round(card_cs, 4), 'clip_end_sec': round(card_ce, 4), 'video_chain_id': card_vcid, 'cy': 0.44, 'zoom_start': 1.0, 'zoom_end': 1.0, 'pan_dx': 0.0, 'color_preset': eff_color_preset, 'grade_lift': float(color_params['lift']), 'grade_warmth': float(color_params['warmth'])})
            beat_global_idx += 1; cur_frame = card_end_frame
        for local_pos, (g_idx, b) in enumerate(ch_beats):
            bid = str(b.get('beat_id') or f'beat_{g_idx:03d}'); wav_arr = wav_waves[bid]; wav_dur = len(wav_arr) / float(TARGET_SR)
            is_first_in_ch = local_pos == 0; is_last_in_ch = local_pos == len(ch_beats) - 1
            is_last_overall = ch_pos == len(chapter_ids) - 1 and is_last_in_ch
            extra_tail = OUTRO_TAIL_SEC if is_last_overall else INTER_CHAPTER_PAUSE_SEC if is_last_in_ch else 0.06
            beat_frames = max(45, int(round((wav_dur + extra_tail) * FPS))); b_start_frame = cur_frame; b_end_frame = cur_frame + beat_frames
            out_start = b_start_frame / float(FPS); out_end = b_end_frame / float(FPS); out_dur = out_end - out_start
            display_text = str(b.get('text') or b.get('tts_text') or b.get('display_text') or '').strip()
            show_kw, main_w, decision_target = kw_decisions.get(g_idx, (False, '', ''))
            if is_first_in_ch:
                show_kw = False; main_w = ''; decision_target = ''
            top_w = ''
            target_kw = str(b.get('target_keyword') or b.get('sync_word') or decision_target or (main_w.split()[0] if main_w else '')).strip() if show_kw else ''
            sfx_kind = str(b.get('sfx_type') or b.get('sfx_kind') or 'war_drum').strip().lower()
            if sfx_kind not in ('war_drum', 'elephant_trumpet', 'fire_roar', 'steel_drum'):
                sfx_kind = 'war_drum'
            align = str(b.get('anchor_side') or b.get('align') or ('left' if g_idx % 2 == 0 else 'right')).strip().lower()
            if align not in ('left', 'right'):
                align = 'left' if g_idx % 2 == 0 else 'right'
            tone = str(b.get('tone') or _infer_tone(sfx_kind, cidx, top_w, main_w)).lower(); chain_info = chain_assignments[g_idx]
            chain_group_id = str(b.get('chain_group_id') or chain_info['video_chain_id']).strip()
            chain_role = 'start' if chain_info['chain_slot'] == 0 else 'end' if chain_info['chain_slot'] == chain_info['chain_length'] - 1 else 'middle'
            if show_kw:
                words = _extract_beat_words_acoustic(wav_arr, display_text, bid, out_start); kw_off = _find_word_offset(words, bid, out_start, target_kw)
                hold_dur = 2.45; max_delay = max(0.18, out_dur - 2.35); hit_off = max(0.15, min(kw_off, max_delay))
                hit_sec = out_start + hit_off; hold_end = min(out_end - 0.14, hit_sec + hold_dur)
            else:
                kw_off = 0.0; hit_sec = out_start; hold_end = out_start
            raw_ax_360 = int(b.get('anchor_x_360') or (28 if align == 'left' else 612)); raw_ay_360 = max(58, min(64, int(b.get('anchor_y_360') or 61)))
            vpath, clip_cs, clip_ce, vcid = _resolve_beat_video_clip(raw_clips_dir, bid, g_idx, chain_info=chain_info, is_chapter_card=False)
            in_scene_title: dict[str, Any] | None = None
            if eff_chapter_style == 'in_scene_cinema_title' and is_first_in_ch:
                in_scene_title = {'header': card_top, 'main_word': card_main, 'tone': card_tone, 'duration_sec': IN_SCENE_CHAPTER_OVERLAY_SEC, 'full_brightness': True, 'card_subtitle': '', 'gold_divider_line': False}
            beats_out.append({'idx': beat_global_idx, 'kind': 'narration', 'chapter_style': eff_chapter_style, 'is_chapter_opener': is_first_in_ch, 'in_scene_chapter_title': in_scene_title, 'chapter_idx': cidx, 'chapter_roman': roman, 'chapter_header': str(b.get('chapter_header') or header).strip(), 'beat_id': bid, 'audio_wav_src': str((audio_dir / f'{bid}.wav').resolve()), 'out_start': round(out_start, 6), 'out_end': round(out_end, 6), 'start_frame': b_start_frame, 'end_frame': b_end_frame, 'wav_duration_sec': round(wav_dur, 4), 'display_text': display_text, 'show_keyword': show_kw, 'target_keyword': target_kw, 'keyword_offset_sec': round(kw_off, 4), 'top_word': '', 'main_word': main_w, 'card_subtitle': '', 'gold_divider_line': False, 'hit_sec': round(hit_sec, 6), 'hold_end_sec': round(hold_end, 6), 'tone': tone, 'sfx_kind': sfx_kind, 'anchor_x': raw_ax_360, 'anchor_y': raw_ay_360, 'align': align, 'micro_tag': '', 'chain_group_id': chain_group_id, 'chain_role': chain_role, 'chain_pattern': eff_chain_pattern, 'chain_length': int(chain_info['chain_length']), 'chain_slot': int(chain_info['chain_slot']), 'use_3d_map_dive': False, 'map_theme': '', 'primary_media_path': str((frames_dir / f'{bid}.png').resolve()), 'video_clip_path': str(vpath) if vpath else '', 'clip_start_sec': round(clip_cs, 4), 'clip_end_sec': round(clip_ce, 4), 'video_chain_id': vcid, 'cy': 0.44, 'zoom_start': 1.0, 'zoom_end': 1.0, 'pan_dx': 0.0, 'color_preset': eff_color_preset, 'grade_lift': float(color_params['lift']), 'grade_warmth': float(color_params['warmth'])})
            beat_global_idx += 1; cur_frame = b_end_frame
        ch_end_frame = cur_frame
        chapters_out.append({'chapter_idx': cidx, 'roman': roman, 'header': header, 'title_top': card_top, 'title_main': card_main, 'subtitle': card_sub, 'chapter_style': eff_chapter_style, 'start_sec': round(ch_start_sec, 6), 'end_sec': round(ch_end_frame / float(FPS), 6), 'start_frame': ch_start_frame, 'end_frame': ch_end_frame, 'narration_beats': len(ch_beats)})
    total_frames = cur_frame; total_sec = total_frames / float(FPS); shards_spec: dict[str, dict[str, Any]] = {}
    video_out_dir.mkdir(parents=True, exist_ok=True)
    for sid in range(1, eff_shards + 1):
        sf = (sid - 1) * total_frames // eff_shards; ef = sid * total_frames // eff_shards
        shards_spec[str(sid)] = {'shard_id': sid, 'start_frame': sf, 'end_frame': ef, 'frame_count': ef - sf, 'start_sec': round(sf / float(FPS), 6), 'end_sec': round(ef / float(FPS), 6), 'duration_sec': round((ef - sf) / float(FPS), 3), 'output_video': str((video_out_dir / f'shard_{sid}_video.mp4').resolve())}
    if skip_audio_master:
        eb = {'integrated_lufs': -11.0, 'true_peak_dbtp': -1.25}
    else:
        total_n = int(round(total_sec * TARGET_SR)); voice_buf = np.zeros((total_n, 2), dtype=np.float32); fade_n = int(round(0.016 * TARGET_SR))
        for b in beats_out:
            if b['kind'] != 'narration':
                continue
            seg = wav_waves[b['beat_id']].copy()
            if len(seg) > 2 * fade_n:
                seg[:fade_n] *= np.linspace(0.0, 1.0, fade_n, dtype=np.float32)[:, None]
                seg[-fade_n:] *= np.linspace(1.0, 0.0, fade_n, dtype=np.float32)[:, None]
            oi0 = int(round(float(b['out_start']) * TARGET_SR)); ol = min(len(seg), total_n - oi0)
            if ol > 0:
                voice_buf[oi0:oi0 + ol] += seg[:ol]
        mono_v = np.sqrt(0.5 * (voice_buf[:, 0] ** 2 + voice_buf[:, 1] ** 2)); active_samples = mono_v[mono_v > 0.015]
        voice_rms = float(np.sqrt(np.mean(active_samples ** 2))) if active_samples.size else float(np.sqrt(np.mean(mono_v ** 2))) + 1e-06
        hop = TARGET_SR // 20; nf_sc = max(1, total_n // hop)
        env_50ms = np.sqrt(np.mean(mono_v[:nf_sc * hop].reshape(nf_sc, hop) ** 2, axis=1) + 1e-10); is_speech = (env_50ms > 0.012).astype(np.float32)
        k_sm = max(1, int(round(0.35 * 20))); speech_sm = np.convolve(is_speech, np.ones(k_sm, dtype=np.float32) / k_sm, mode='same')
        speech_full = np.interp(np.arange(total_n, dtype=np.float32), np.arange(nf_sc, dtype=np.float32) * hop, speech_sm).astype(np.float32)
        undertone = _synth_heroic_war_drum_undertone(total_n, beats_out); u_rms = float(np.sqrt(np.mean(undertone ** 2))) + 1e-06
        undertone_norm = undertone * (voice_rms / u_rms); g_speech = 10.0 ** (-22.5 / 20.0); g_pause = 10.0 ** (-16.5 / 20.0)
        u_gain = g_pause + (g_speech - g_pause) * speech_full; mix = voice_buf + undertone_norm * u_gain[:, None]
        sfx_gain_impact = voice_rms * 10.0 ** (-14.0 / 20.0) * 2.0; sfx_gain_gong = voice_rms * 10.0 ** (-7.5 / 20.0) * 1.9
        for b in beats_out:
            if b['kind'] == 'chapter_card':
                gong = _synth_tactile_sfx('chapter_gong') * sfx_gain_gong; i0 = max(0, int(round((float(b['out_start']) + 0.08) * TARGET_SR)))
                il = min(len(gong), total_n - i0)
                if il > 0:
                    mix[i0:i0 + il] += gong[:il]
            else:
                if b.get('in_scene_chapter_title'):
                    gong = _synth_tactile_sfx('chapter_gong') * (sfx_gain_gong * 0.45); i0 = max(0, int(round(float(b['out_start']) * TARGET_SR)))
                    il = min(len(gong), total_n - i0)
                    if il > 0:
                        mix[i0:i0 + il] += gong[:il]
                if b.get('show_keyword') and b.get('main_word'):
                    is_hero = b['tone'] in ('fire', 'crimson'); gain = sfx_gain_impact * (1.0 if is_hero else 0.85); sfx = _synth_tactile_sfx(b['sfx_kind']) * gain
                    i0 = max(0, int(round(float(b['hit_sec']) * TARGET_SR))); il = min(len(sfx), total_n - i0)
                    if il > 0:
                        mix[i0:i0 + il] += sfx[:il]
        tail_sfx = _synth_tactile_sfx('war_drum') * (sfx_gain_impact * 0.9); ti0 = max(0, int(round((total_sec - 0.8) * TARGET_SR)))
        til = min(len(tail_sfx), total_n - ti0)
        if til > 0:
            mix[ti0:ti0 + til] += tail_sfx[:til]
        ef_n = min(total_n // 10, int(round(0.15 * TARGET_SR)))
        if ef_n > 1:
            mix[-ef_n:] *= np.linspace(1.0, 0.0, ef_n, dtype=np.float32)[:, None]
        master_wav_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='m1_flex_aud_') as td:
            raw_wav = Path(td) / 'raw_mix.wav'; _write_wav_stereo_i16(raw_wav, mix)
            eb = _normalize_audio_master(raw_wav, master_wav_path, target_lufs=-11.0, max_tp_db=-1.25)
    narr_count = sum((1 for b in beats_out if b['kind'] == 'narration'))
    kw_count = sum((1 for b in beats_out if b['kind'] == 'narration' and b.get('show_keyword')))
    unique_chains = sorted({b['video_chain_id'] for b in beats_out if b['kind'] == 'narration' and b.get('video_chain_id')})
    chain_len_hist: dict[int, int] = {}; seen_chains: set[str] = set()
    for b in beats_out:
        if b['kind'] == 'narration':
            cid = str(b.get('video_chain_id') or '')
            if cid and cid not in seen_chains:
                seen_chains.add(cid); cl = int(b.get('chain_length', 2)); chain_len_hist[cl] = chain_len_hist.get(cl, 0) + 1
    job_id = str(script_cfg.get('job_id') or timeline_path.parent.name or DEFAULT_JOB_ID)
    timeline = {'job_id': job_id, 'engine_version': M1_FLEX_ENGINE_VERSION, 'pattern_id': M1_FLEX_PATTERN_ID, 'm1_flex_config': flex_spec, 'resolution': eff_resolution, 'width': int(geom['width']), 'height': int(geom['height']), 'fps': FPS, 'total_frames': total_frames, 'total_sec': round(total_sec, 6), 'chapter_count': len(chapters_out), 'chapter_style': eff_chapter_style, 'color_preset': eff_color_preset, 'chain_pattern': eff_chain_pattern, 'chain_count': len(unique_chains), 'chain_length_histogram': chain_len_hist, 'narration_beat_count': narr_count, 'moving_video_beats_ready': sum((1 for b in beats_out if b['kind'] == 'narration' and bool(b.get('video_clip_path')))), 'raw_clips_dir': str(raw_clips_dir.resolve()), 'emphasis_keyword_count': kw_count, 'emphasis_keyword_density': round(kw_count / float(max(1, narr_count)), 4), 'text_free_beat_count': narr_count - kw_count, 'text_free_ratio': round((narr_count - kw_count) / float(max(1, narr_count)), 4), 'chapter_card_count': sum((1 for b in beats_out if b['kind'] == 'chapter_card')), 'in_scene_chapter_title_count': sum((1 for b in beats_out if b['kind'] == 'narration' and bool(b.get('in_scene_chapter_title')))), 'audio_wav': str(master_wav_path.resolve()), 'audio_ebur128': eb, 'video_out_dir': str(video_out_dir.resolve()), 'total_shards': eff_shards, 'shards': shards_spec, 'chapters': chapters_out, 'beats': beats_out}
    timeline_path.parent.mkdir(parents=True, exist_ok=True)
    timeline_path.write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding='utf-8'); write_impact_keywords_srt(timeline, srt_path)
    cc_out = full_cc_srt_path or timeline_path.parent / 'subtitles_vi_full_cc.srt'; write_full_cc_srt(timeline, cc_out)
    print(json.dumps({'action': 'build_timeline', 'engine_version': M1_FLEX_ENGINE_VERSION, 'elapsed_sec': round(time.time() - t0, 2), 'total_sec': round(total_sec, 2), 'total_frames': total_frames, 'resolution': f"{geom['width']}x{geom['height']} ({eff_resolution})", 'color_preset': eff_color_preset, 'chapter_style': eff_chapter_style, 'chain_pattern': eff_chain_pattern, 'chain_length_histogram': chain_len_hist, 'chapters': len(chapters_out), 'narration_beats': narr_count, 'emphasis_keywords': kw_count, 'keyword_density': timeline['emphasis_keyword_density'], 'audio_ebur128': eb, 'timeline_json': str(timeline_path), 'master_wav': str(master_wav_path), 'srt': str(srt_path), 'full_cc_srt': str(cc_out)}, ensure_ascii=False, indent=2), flush=True)
    return timeline
class ShardFFmpegWriter:
    def __init__(self, out_mp4: Path, width: int=WIDTH, height: int=HEIGHT, fps: int=FPS, crf: int=16, preset: str='fast') -> None:
        self.out_mp4 = Path(out_mp4); self.out_mp4.parent.mkdir(parents=True, exist_ok=True); self.width = int(width)
        self.height = int(height); self.fps = int(fps); self.crf = int(crf)
        self.preset = preset; self.frames_written = 0; self._proc: subprocess.Popen[bytes] | None = None
    def __enter__(self) -> 'ShardFFmpegWriter':
        level_v = '5.1' if self.width >= 2560 else '4.1'
        cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{self.width}x{self.height}', '-r', str(self.fps), '-i', 'pipe:0', '-an', '-c:v', 'libx264', '-threads', '4', '-preset', self.preset, '-crf', str(self.crf), '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level:v', level_v, '-g', str(self.fps), '-bf', '2', '-video_track_timescale', str(self.fps * 1000), '-movflags', '+faststart', str(self.out_mp4)]
        self._proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        return self
    def write_frame(self, arr: np.ndarray) -> None:
        assert self._proc is not None and self._proc.stdin is not None
        if arr.dtype != np.uint8:
            arr = np.clip(arr, 0, 255).astype(np.uint8)
        if not arr.flags['C_CONTIGUOUS']:
            arr = np.ascontiguousarray(arr)
        self._proc.stdin.write(memoryview(arr)); self.frames_written += 1
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._proc is None:
            return
        if self._proc.stdin is not None:
            try:
                self._proc.stdin.close()
            except OSError:
                pass
        stderr = self._proc.stderr.read().decode('utf-8', errors='replace') if self._proc.stderr else ''; rc = self._proc.wait()
        if exc_type is None and rc != 0:
            raise RuntimeError(f'FFmpeg writer failed (rc={rc}): {stderr}')
class _MovingClipDecoder:
    """Sequential-optimized OpenCV `.mp4` frame reader (native 1280x720, zero downscale) & 6.60s clear-air clamp."""
    def __init__(self, path: Path, *, max_w: int=1280, cache_frames: int=8) -> None:
        self.path = Path(path); self.max_w = int(max_w); self.cache_frames = max(2, int(cache_frames))
        self.cap = cv2.VideoCapture(str(self.path))
        if not self.cap.isOpened():
            raise RuntimeError(f'Unable to open moving video clip: {self.path}')
        fps = float(self.cap.get(cv2.CAP_PROP_FPS) or 0.0); self.fps = fps if 5.0 <= fps <= 120.0 else 24.0
        fc = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0); self.frame_count = max(1, fc); self.duration_sec = self.frame_count / self.fps
        self.max_clean_sec = min(CLIP_CLEAN_MAX_SEC, max(0.0, self.duration_sec - 0.12)); self._next_idx = 0
        self._frames: OrderedDict[int, np.ndarray] = OrderedDict(); self._last_valid: np.ndarray | None = None
    def _decode_rgb(self, bgr: np.ndarray) -> np.ndarray:
        h, w = bgr.shape[:2]
        if w > self.max_w:
            nh = max(16, int(round(h * (self.max_w / float(w))))); bgr = cv2.resize(bgr, (self.max_w, nh), interpolation=cv2.INTER_AREA)
        return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    def get_frame_rgb(self, idx: int) -> np.ndarray:
        idx = max(0, min(self.frame_count - 1, int(idx)))
        if idx in self._frames:
            self._frames.move_to_end(idx)
            return self._frames[idx]
        if idx == self._next_idx:
            ok, bgr = self.cap.read(); self._next_idx = idx + 1
        elif self._next_idx < idx <= self._next_idx + 5:
            ok, bgr = (False, None)
            while self._next_idx <= idx:
                cur_i = self._next_idx; ok, bgr = self.cap.read(); self._next_idx += 1
                if not ok or bgr is None:
                    break
                if cur_i >= idx - 1:
                    rgb_tmp = self._decode_rgb(bgr); self._frames[cur_i] = rgb_tmp; self._last_valid = rgb_tmp
                    while len(self._frames) > self.cache_frames:
                        self._frames.popitem(last=False)
            if idx in self._frames:
                return self._frames[idx]
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, idx); ok, bgr = self.cap.read(); self._next_idx = idx + 1
        if not ok or bgr is None:
            if self._last_valid is not None:
                return self._last_valid
            raise RuntimeError(f'Failed decoding frame {idx} from {self.path}')
        rgb = self._decode_rgb(bgr); self._last_valid = rgb; self._frames[idx] = rgb
        while len(self._frames) > self.cache_frames:
            self._frames.popitem(last=False)
        return rgb
    def sample_at_sec(self, sec: float) -> np.ndarray:
        clamped_t = max(0.0, min(self.max_clean_sec, float(sec))); f_pos = clamped_t * self.fps
        i0 = max(0, min(self.frame_count - 1, int(math.floor(f_pos)))); i1 = min(self.frame_count - 1, i0 + 1); frac = f_pos - i0
        f0 = self.get_frame_rgb(i0)
        if i1 == i0 or frac <= 0.04:
            return f0
        f1 = self.get_frame_rgb(i1)
        if frac >= 0.96:
            return f1
        return cv2.addWeighted(f0, 1.0 - frac, f1, frac, 0.0)
    def close(self) -> None:
        try:
            self.cap.release()
        except Exception:
            pass
        self._frames.clear()
class ShardFrameBank:
    """Memory-bounded LRU moving-video (.mp4) + image cache & pure-black IMAX chrome builder."""
    def __init__(self, *, max_images: int=24, max_clips: int=4) -> None:
        self.max_images = max_images; self.max_clips = max(2, int(max_clips)); self._img_cache: OrderedDict[str, np.ndarray] = OrderedDict()
        self._clip_cache: OrderedDict[str, _MovingClipDecoder] = OrderedDict()
        wm = Image.open(WATERMARK_PATH).convert('RGBA').resize((WATERMARK_SIZE, WATERMARK_SIZE), Image.Resampling.LANCZOS)
        arr = np.asarray(wm, dtype=np.float32); arr[:, :, 3] = np.clip(arr[:, :, 3] * 0.88, 0.0, 255.0)
        self.wm_alpha = (arr[:, :, 3:4] / 255.0).astype(np.float32); self.wm_rgb = arr[:, :, :3].astype(np.float32)
        self.wm_x0 = WIDTH - WATERMARK_SIZE - WATERMARK_MARGIN; self.wm_y0 = HEIGHT - BAR_H + max(0, (BAR_H - WATERMARK_SIZE) // 2)
    def build_static_imax_chrome(self) -> np.ndarray:
        """100% pure cinema black IMAX 2.39:1 bars (0 text) + 1px*S gold border hairlines + bottom-right logo."""
        chrome = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8); hair_h = max(1, int(round(1.0 * S)))
        gold_rgb = np.array([154, 125, 69], dtype=np.uint8); gold_core = np.array([186, 152, 84], dtype=np.uint8)
        chrome[BAR_H - hair_h:BAR_H, :, :] = gold_rgb
        if hair_h >= 3:
            chrome[BAR_H - 2, :, :] = gold_core
        chrome[HEIGHT - BAR_H:HEIGHT - BAR_H + hair_h, :, :] = gold_rgb
        if hair_h >= 3:
            chrome[HEIGHT - BAR_H + 1, :, :] = gold_core
        return self.apply_watermark_fast(chrome)
    def sample_video_frame(self, path: Path, sec: float) -> np.ndarray:
        key = str(path); dec = self._clip_cache.get(key)
        if dec is not None:
            self._clip_cache.move_to_end(key)
        else:
            dec = _MovingClipDecoder(path, max_w=1280, cache_frames=8); self._clip_cache[key] = dec
            while len(self._clip_cache) > self.max_clips:
                _, old_dec = self._clip_cache.popitem(last=False); old_dec.close()
        return dec.sample_at_sec(sec)
    def close(self) -> None:
        for dec in self._clip_cache.values():
            dec.close()
        self._clip_cache.clear(); self._img_cache.clear()
    def load_image(self, path: Path) -> np.ndarray:
        key = str(path)
        if key in self._img_cache:
            self._img_cache.move_to_end(key)
            return self._img_cache[key]
        bgr = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if bgr is None:
            raise FileNotFoundError(f'Unable to read beat frame image: {path}')
        h, w = bgr.shape[:2]
        if w > WIDTH:
            nh = max(16, int(round(h * (float(WIDTH) / w)))); bgr = cv2.resize(bgr, (WIDTH, nh), interpolation=cv2.INTER_AREA)
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB); self._img_cache[key] = rgb
        while len(self._img_cache) > self.max_images:
            self._img_cache.popitem(last=False)
        return rgb
    def apply_watermark_fast(self, frame_rgb: np.ndarray) -> np.ndarray:
        x0, y0 = (self.wm_x0, self.wm_y0); x1, y1 = (x0 + WATERMARK_SIZE, y0 + WATERMARK_SIZE); roi = frame_rgb[y0:y1, x0:x1].astype(np.float32)
        blended = roi * (1.0 - self.wm_alpha) + self.wm_rgb * self.wm_alpha; frame_rgb[y0:y1, x0:x1] = np.clip(blended, 0.0, 255.0).astype(np.uint8)
        return frame_rgb
def crop_25d(rgb: np.ndarray, out_w: int=WIDTH, out_h: int=ACT_H, cy: float=0.44, zoom: float=1.0, dx: float=0.0, dy: float=0.0) -> np.ndarray:
    h, w = rgb.shape[:2]; target_ar = out_w / float(out_h)
    if w / float(h) < target_ar:
        base_w = float(w); base_h = w / target_ar
    else:
        base_h = float(h); base_w = h * target_ar
    cw = max(16.0, base_w / max(1.0, zoom)); ch = max(16.0, base_h / max(1.0, zoom)); cx_px = w * 0.5 + dx * w
    cy_px = h * cy + dy * h; x0 = max(0.0, min(w - cw, cx_px - cw * 0.5)); y0 = max(0.0, min(h - ch, cy_px - ch * 0.5))
    ix0, iy0 = (int(round(x0)), int(round(y0))); ix1 = min(w, max(ix0 + 2, int(round(x0 + cw)))); iy1 = min(h, max(iy0 + 2, int(round(y0 + ch))))
    roi = rgb[iy0:iy1, ix0:ix1]
    if roi.shape[1] == out_w and roi.shape[0] == out_h:
        return roi
    return cv2.resize(roi, (out_w, out_h), interpolation=cv2.INTER_LANCZOS4)
def _get_flare_grids(h: int, w: int) -> tuple[np.ndarray, np.ndarray]:
    key = (h, w)
    if key not in _FLARE_GRID_CACHE:
        yg = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]
        xg_env = np.exp(-(np.linspace(-1.0, 1.0, w, dtype=np.float32)[None, :] * 1.15) ** 2); _FLARE_GRID_CACHE[key] = (yg, xg_env)
    return _FLARE_GRID_CACHE[key]
def _get_fast_grade_tables(lift: float, warmth: float, flare_boost: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    key = (int(round(lift * 1000)), int(round(warmth * 1000)), int(round(flare_boost * 1000)))
    if key not in _FAST_GRADE_CACHE:
        x = np.arange(256, dtype=np.float32) / 255.0; gamma = min(0.85, max(0.76, 0.94 - lift * 0.65)); y = np.power(np.clip(x, 0.0001, 1.0), gamma)
        y = np.clip((y - 0.46) * 1.14 + 0.48, 0.0, 1.0); tone_u8 = np.clip(np.round(y * 255.0), 0, 255).astype(np.uint8)
        hi = np.clip((x - 0.48) * 1.9, 0.0, 1.0); sh = np.clip(1.0 - x * 1.7, 0.0, 1.0); dr = (warmth * hi + 0.025) * 255.0
        dg = (warmth * 0.58 * hi + 0.015) * 255.0; db = (0.05 * sh - warmth * 0.2 * hi + 0.01) * 255.0; pos = np.zeros((256, 1, 3), dtype=np.uint8)
        pos[:, 0, 0] = np.clip(np.round(np.maximum(dr, 0.0)), 0, 255); pos[:, 0, 1] = np.clip(np.round(np.maximum(dg, 0.0)), 0, 255)
        pos[:, 0, 2] = np.clip(np.round(np.maximum(db, 0.0)), 0, 255); neg_b = np.clip(np.round(np.maximum(-db, 0.0)), 0, 255).astype(np.uint8)
        bright_u8 = np.clip(np.round(np.clip((x - 0.68) * 2.5, 0.0, 1.0) * 255.0), 0, 255).astype(np.uint8); s_gain = 0.36 + 0.55 * flare_boost
        st_lut = np.zeros((256, 1, 3), dtype=np.uint8); st_lut[:, 0, 0] = np.clip(np.round(x * 255.0 * 0.68 * s_gain), 0, 255)
        st_lut[:, 0, 1] = np.clip(np.round(x * 255.0 * 0.46 * s_gain), 0, 255)
        st_lut[:, 0, 2] = np.clip(np.round(x * 255.0 * 0.22 * s_gain), 0, 255); _FAST_GRADE_CACHE[key] = (tone_u8, pos, neg_b, bright_u8, st_lut)
    return _FAST_GRADE_CACHE[key]
def apply_bright_golden_dawn_grade(rgb: np.ndarray, *, lift: float=0.18, warmth: float=0.14, flare_boost: float=0.0, flare_y_norm: float=0.28, sharpen: bool=False) -> np.ndarray:
    """C++ SIMD LUT-accelerated Cinema Grade supporting all 4 M1-Flex color presets (gamma <= 0.85)."""
    tone_u8, pos, neg_b, bright_u8, st_lut = _get_fast_grade_tables(lift, warmth, flare_boost); h, w = rgb.shape[:2]; out = cv2.LUT(rgb, tone_u8)
    lum = cv2.cvtColor(out, cv2.COLOR_RGB2GRAY); lum3 = cv2.cvtColor(lum, cv2.COLOR_GRAY2RGB); cv2.add(out, cv2.LUT(lum3, pos), dst=out)
    b_sub = cv2.LUT(lum, neg_b); out[:, :, 2] = cv2.subtract(out[:, :, 2], b_sub); br = cv2.LUT(lum, bright_u8)
    br_sm = cv2.resize(br, (max(2, w // 4), max(2, h // 4)), interpolation=cv2.INTER_AREA); st_sm = cv2.GaussianBlur(br_sm, (33, 3), 0)
    st_rgb_sm = cv2.LUT(cv2.cvtColor(st_sm, cv2.COLOR_GRAY2RGB), st_lut); st_rgb = cv2.resize(st_rgb_sm, (w, h), interpolation=cv2.INTER_LINEAR)
    cv2.add(out, st_rgb, dst=out)
    if flare_boost > 0.03:
        yg, xg_env = _get_flare_grids(h, w); band = np.exp(-((yg - flare_y_norm) * 16.0) ** 2) * xg_env * (flare_boost * 0.36 * 255.0)
        b_u8 = np.empty((h, w, 3), dtype=np.uint8); b_u8[:, :, 0] = np.clip(band * 1.15, 0.0, 255.0).astype(np.uint8)
        b_u8[:, :, 1] = np.clip(band * 0.78, 0.0, 255.0).astype(np.uint8); b_u8[:, :, 2] = np.clip(band * 0.32, 0.0, 255.0).astype(np.uint8)
        cv2.add(out, b_u8, dst=out)
    if sharpen:
        blur = cv2.GaussianBlur(out, (0, 0), 1.0)
        return cv2.addWeighted(out, 1.16, blur, -0.16, 0)
    return out
def _apply_film_grain_fast(arr: np.ndarray, *, strength: float=0.011, seed: int=0) -> np.ndarray:
    """Apply pre-generated 35mm fine grain strictly inside active cinema window (pure black IMAX bars)."""
    if strength <= 0.0:
        return arr
    g_key = (HEIGHT, WIDTH, BAR_H, ACT_H); ring = _GRAIN_RING_CACHE.get(g_key)
    if not ring:
        ring = []; scale = np.float32(255.0 * strength)
        for idx in range(16):
            rng = np.random.default_rng(178900 + idx); g_act = np.rint(rng.standard_normal((ACT_H, WIDTH, 1), dtype=np.float32) * scale).astype(np.int16)
            g_pos = np.clip(g_act, 0, 255).astype(np.uint8); g_neg = np.clip(-g_act, 0, 255).astype(np.uint8)
            ring.append((np.repeat(g_pos, 3, axis=2), np.repeat(g_neg, 3, axis=2)))
        _GRAIN_RING_CACHE[g_key] = ring
    g_pos, g_neg = ring[seed & 15]; act_view = arr[BAR_H:BAR_H + ACT_H]; cv2.add(act_view, g_pos, dst=act_view)
    cv2.subtract(act_view, g_neg, dst=act_view)
    return arr
@dataclass
class TimelineBeat:
    idx: int; kind: str; chapter_style: str
    is_chapter_opener: bool; in_scene_chapter_title: dict[str, Any] | None; chapter_idx: int
    chapter_roman: str; chapter_header: str; beat_id: str
    out_start: float; out_end: float; start_frame: int
    end_frame: int; show_keyword: bool; top_word: str
    main_word: str; card_subtitle: str; hit_sec: float
    hold_end_sec: float; tone: str; anchor_x: int
    anchor_y: int; align: str; micro_tag: str
    chain_group_id: str; chain_role: str; use_3d_map_dive: bool
    map_theme: str; primary_media_path: Path; video_clip_path: Path | None
    clip_start_sec: float; clip_end_sec: float; video_chain_id: str
    cy: float; zoom_start: float; zoom_end: float
    pan_dx: float; color_preset: str; grade_lift: float
    grade_warmth: float
def load_timeline(timeline_path: Path, *, raw_clips_dir: Path | None=None, resolution_override: str | None=None) -> tuple[dict[str, Any], list[TimelineBeat], list[int]]:
    data = json.loads(timeline_path.read_text(encoding='utf-8'))
    eff_res = str(resolution_override or data.get('resolution') or '1080p').strip().lower(); set_active_resolution(eff_res)
    clips_dir = raw_clips_dir or _resolve_path(data.get('raw_clips_dir')) or DEFAULT_RAW_CLIPS_DIR
    tl_color_preset = str(data.get('color_preset') or 'golden_dawn_1789')
    tl_color_params = COLOR_PRESETS.get(tl_color_preset, COLOR_PRESETS['golden_dawn_1789'])
    tl_chapter_style = str(data.get('chapter_style') or 'minimal_center_card'); beats: list[TimelineBeat] = []; starts: list[int] = []
    narr_idx = 0
    for i, b in enumerate(data['beats']):
        p = _resolve_path(b['primary_media_path']); assert p is not None; sf = int(b['start_frame'])
        kind = str(b['kind']); bid = str(b['beat_id']); vpath = _resolve_path(b.get('video_clip_path'))
        if vpath is not None and (not vpath.is_file() or vpath.stat().st_size < MIN_CLIP_BYTES):
            vpath = None
        if vpath is not None:
            vpath = vpath.resolve()
        cs = float(b.get('clip_start_sec', 0.0)); ce = float(b.get('clip_end_sec', 0.0)); vcid = str(b.get('video_chain_id') or '')
        cy = float(b.get('cy', 0.44)); color_preset = str(b.get('color_preset') or tl_color_preset)
        c_params = COLOR_PRESETS.get(color_preset, tl_color_params); grade_lift = float(b.get('grade_lift', c_params['lift']))
        grade_warmth = float(b.get('grade_warmth', c_params['warmth'])); ch_style = str(b.get('chapter_style') or tl_chapter_style)
        if kind == 'narration':
            m_num = re.search('beat_(\\d+)', bid); g_idx = int(m_num.group(1)) if m_num else narr_idx; narr_idx += 1
            if vpath is None:
                vpath, disc_cs, disc_ce, disc_vcid = _resolve_beat_video_clip(clips_dir, bid, g_idx, is_chapter_card=False)
                if ce <= cs:
                    cs, ce = (disc_cs, disc_ce)
                if not vcid:
                    vcid = disc_vcid
            elif ce <= cs:
                cs, ce = CHAIN_FIRST_HALF if g_idx % 2 == 0 else CHAIN_SECOND_HALF
            if not vcid:
                vcid = f'chain_{g_idx // 2:02d}'
        else:
            ch_i = max(1, int(b.get('chapter_idx', 1))); g_idx = (ch_i - 1) * 10
            if vpath is None:
                vpath, disc_cs, disc_ce, disc_vcid = _resolve_beat_video_clip(clips_dir, f'beat_{g_idx:03d}', g_idx, is_chapter_card=True)
                if ce <= cs:
                    cs, ce = (disc_cs, disc_ce)
                if not vcid:
                    vcid = disc_vcid
            elif ce <= cs:
                cs, ce = CHAIN_FIRST_HALF
        ce = min(CLIP_CLEAN_MAX_SEC, ce) if vpath is not None else 0.0; raw_ax = int(b['anchor_x']); raw_ay = int(b['anchor_y'])
        scaled_ax = int(round(raw_ax * S)) if raw_ax <= 640 else raw_ax; scaled_ay = int(round(raw_ay * S)) if raw_ay <= 360 else raw_ay
        is_opener = bool(b.get('is_chapter_opener', False)); show_kw = bool(b.get('show_keyword', bool(str(b.get('main_word', '')).strip())))
        if kind == 'narration' and is_opener:
            show_kw = False
        beats.append(TimelineBeat(idx=int(b.get('idx', i)), kind=kind, chapter_style=ch_style, is_chapter_opener=is_opener, in_scene_chapter_title=b.get('in_scene_chapter_title') if isinstance(b.get('in_scene_chapter_title'), dict) else None, chapter_idx=int(b['chapter_idx']), chapter_roman=str(b['chapter_roman']), chapter_header=str(b['chapter_header']), beat_id=bid, out_start=float(b['out_start']), out_end=float(b['out_end']), start_frame=sf, end_frame=int(b['end_frame']), show_keyword=show_kw, top_word='' if kind == 'narration' else str(b.get('top_word', '')), main_word=str(b.get('main_word', '')) if kind == 'chapter_card' or show_kw else '', card_subtitle='', hit_sec=float(b['hit_sec']), hold_end_sec=float(b['hold_end_sec']), tone=str(b.get('tone', 'gold')), anchor_x=scaled_ax, anchor_y=scaled_ay, align=str(b['align']), micro_tag='', chain_group_id=str(b.get('chain_group_id', '')), chain_role=str(b.get('chain_role', '')), use_3d_map_dive=False, map_theme='', primary_media_path=p, video_clip_path=vpath, clip_start_sec=cs, clip_end_sec=ce, video_chain_id=vcid, cy=0.44, zoom_start=1.0, zoom_end=1.0, pan_dx=0.0, color_preset=color_preset, grade_lift=grade_lift, grade_warmth=grade_warmth))
        starts.append(sf)
    return (data, beats, starts)
def _tone_colors(tone: str) -> tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]:
    if tone == 'fire':
        return ((255, 206, 98), (255, 246, 226), (255, 118, 24))
    if tone == 'crimson':
        return ((255, 212, 118), (255, 238, 216), (242, 54, 28))
    return ((255, 218, 112), (255, 249, 232), (248, 166, 28))
def _compute_dignified_title_anim(t: float, beat: TimelineBeat) -> tuple[float, float, float]:
    """Subtle 1.06x -> 1.00x (0.16s ease-out cubic) pop-in, 2.2-2.6s steady hold, 0.25s fade-out."""
    if not beat.show_keyword or not beat.main_word:
        return (0.0, 1.0, 0.0)
    if t < beat.hit_sec or t > beat.hold_end_sec:
        return (0.0, 1.0, 0.0)
    dt = t - beat.hit_sec; rem = beat.hold_end_sec - t; alpha = _clamp01(dt / 0.1) * _clamp01(rem / 0.25)
    scale = 1.06 - 0.06 * _ease_out_cubic(dt / 0.16) if dt < 0.16 else 1.0
    return (alpha, scale, 0.0)
def _wrap_lines(dr: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int, max_lines: int=2) -> list[str]:
    words = text.split(); lines: list[str] = []; cur = ''
    for wd in words:
        cand = f'{cur} {wd}'.strip(); bb = dr.textbbox((0, 0), cand, font=font)
        if bb[2] - bb[0] <= max_w:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    if len(lines) <= max_lines:
        return lines
    kept = lines[:max_lines - 1]; tail = ' '.join(lines[max_lines - 1:])
    while tail and dr.textbbox((0, 0), tail + '…', font=font)[2] - dr.textbbox((0, 0), tail + '…', font=font)[0] > max_w:
        parts = tail.split()
        if len(parts) <= 1:
            break
        tail = ' '.join(parts[:-1])
    kept.append(tail + '…')
    return kept
@dataclass
class OverlayROI:
    """Tightly bounded pre-multiplied RGBA overlay ROI for fast sub-millisecond compositing."""; x0: int; y0: int
    x1: int; y1: int; fg_premult: np.ndarray
    inv_alpha: np.ndarray
def _pack_roi(layer_rgba: Image.Image, x0: int, y0: int) -> OverlayROI | None:
    arr = np.asarray(layer_rgba, dtype=np.uint8); lh, lw = arr.shape[:2]; cx0 = max(0, x0)
    cy0 = max(BAR_H, y0); cx1 = min(WIDTH, x0 + lw); cy1 = min(BAR_H + ACT_H, y0 + lh)
    if cx1 <= cx0 or cy1 <= cy0:
        return None
    sub = arr[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]; a_u8 = sub[:, :, 3]; ys, xs = np.nonzero(a_u8)
    if ys.size == 0:
        return None
    ty0, ty1 = (int(ys.min()), int(ys.max()) + 1); tx0, tx1 = (int(xs.min()), int(xs.max()) + 1); tight = sub[ty0:ty1, tx0:tx1]
    alpha = tight[:, :, 3:4].astype(np.float32) * (1.0 / 255.0); fg_premult = tight[:, :, :3].astype(np.float32) * alpha
    inv_alpha = (1.0 - alpha).astype(np.float32)
    return OverlayROI(x0=cx0 + tx0, y0=cy0 + ty0, x1=cx0 + tx1, y1=cy0 + ty1, fg_premult=fg_premult, inv_alpha=inv_alpha)
def _composite_roi_onto_rgb(base_rgb: np.ndarray, roi: OverlayROI | None) -> None:
    if roi is None:
        return
    dst = base_rgb[roi.y0:roi.y1, roi.x0:roi.x1]; blended = dst.astype(np.float32) * roi.inv_alpha + roi.fg_premult
    np.clip(blended, 0.0, 255.0, out=blended); dst[:] = blended.astype(np.uint8)
_MEASURE_IMG = Image.new('RGBA', (8, 8), (0, 0, 0, 0)); _MEASURE_DRAW = ImageDraw.Draw(_MEASURE_IMG)
def _measure_tracked_text(text: str, font: ImageFont.FreeTypeFont, tracking: float) -> tuple[int, int, int, int, list[tuple[str, float]]]:
    nfc = unicodedata.normalize('NFC', text)
    if not nfc:
        return (0, 0, 0, 0, [])
    cur_x = 0.0; placements: list[tuple[str, float]] = []; min_x, min_y = (10 ** 9, 10 ** 9)
    max_x, max_y = (-10 ** 9, -10 ** 9); n = len(nfc)
    for idx, ch in enumerate(nfc):
        placements.append((ch, cur_x)); bb = _MEASURE_DRAW.textbbox((0, 0), ch, font=font)
        if bb[2] > bb[0] and bb[3] > bb[1]:
            min_x = min(min_x, int(math.floor(cur_x + bb[0]))); min_y = min(min_y, int(bb[1])); max_x = max(max_x, int(math.ceil(cur_x + bb[2])))
            max_y = max(max_y, int(bb[3]))
        adv = float(font.getlength(ch)); cur_x += adv + (tracking if idx < n - 1 else 0.0)
    if min_x > max_x:
        return (0, 0, int(math.ceil(cur_x)), 0, placements)
    return (min_x, min_y, max_x, max_y, placements)
def _draw_tracked_text(dr: ImageDraw.ImageDraw, x: float, y: float, placements: list[tuple[str, float]], font: ImageFont.FreeTypeFont, *, fill: tuple[int, int, int, int], stroke_width: int=0, stroke_fill: tuple[int, int, int, int] | None=None) -> None:
    for ch, dx in placements:
        if stroke_width > 0 and stroke_fill is not None:
            dr.text((x + dx, y), ch, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
        else:
            dr.text((x + dx, y), ch, font=font, fill=fill)
def _render_monumental_title_layer(top_word: str, main_word: str, anchor_x: int, anchor_y: int, *, align: str='left', tone: str='gold', alpha: float=1.0, scale: float=1.0, flare: float=0.0, top_size: int=0, main_size: int=22) -> OverlayROI | None:
    """Refined sparse single-line emphasis keyword (22 * S = 66px@1080p / 88px@1440p, ivory-gold #FFF5D6, ROI-only)."""
    del top_word, tone, flare, top_size; text = unicodedata.normalize('NFC', str(main_word or '').strip())
    if alpha <= 0.02 or not text:
        return None
    ivory_gold = (255, 245, 214); eff_main = float(max(18, min(24, main_size)))
    f_main = get_font(FONT_BARLOW, max(16, int(round(eff_main * S * scale)))); bb_main = _MEASURE_DRAW.textbbox((0, 0), text, font=f_main)
    max_text_w = WIDTH - int(round(80 * S))
    while bb_main[2] - bb_main[0] > max_text_w and eff_main > 16:
        eff_main -= 1.0; f_main = get_font(FONT_BARLOW, max(16, int(round(eff_main * S * scale))))
        bb_main = _MEASURE_DRAW.textbbox((0, 0), text, font=f_main)
    tw, th = (bb_main[2] - bb_main[0], bb_main[3] - bb_main[1]); margin_x = int(round(20 * S))
    bx0 = anchor_x if align == 'left' else anchor_x - tw if align == 'right' else anchor_x - tw // 2
    bx0 = max(margin_x, min(WIDTH - tw - margin_x, bx0))
    by0 = max(BAR_H + int(round(8 * S)), min(HEIGHT - BAR_H - th - int(round(10 * S)), anchor_y - th // 2)); scrim_px = int(round(18 * S))
    scrim_py = int(round(9 * S)); blur_r = 10.0 * S; pad_x = scrim_px + int(math.ceil(blur_r * 2.2))
    pad_y = scrim_py + int(math.ceil(blur_r * 2.2)); rx0 = max(0, bx0 - pad_x); ry0 = max(BAR_H, by0 - pad_y)
    rx1 = min(WIDTH, bx0 + tw + pad_x); ry1 = min(BAR_H + ACT_H, by0 + th + pad_y); rw, rh = (rx1 - rx0, ry1 - ry0)
    if rw <= 2 or rh <= 2:
        return None
    lx_box = bx0 - rx0; ly_box = by0 - ry0; lx_main = lx_box - bb_main[0]
    ly_main = ly_box - bb_main[1]; sw, sh = (max(4, rw // 2), max(4, rh // 2)); scrim_sm = Image.new('RGBA', (sw, sh), (0, 0, 0, 0))
    sdr = ImageDraw.Draw(scrim_sm)
    sdr.ellipse([(lx_box - scrim_px) // 2, (ly_box - scrim_py) // 2, (lx_box + tw + scrim_px) // 2, (ly_box + th + scrim_py) // 2], fill=(6, 8, 12, int(round(42 * alpha))))
    scrim_sm = scrim_sm.filter(ImageFilter.GaussianBlur(radius=blur_r * 0.5)); layer = scrim_sm.resize((rw, rh), Image.Resampling.BILINEAR)
    fg = Image.new('RGBA', (rw, rh), (0, 0, 0, 0)); dr = ImageDraw.Draw(fg); a255 = int(round(252 * alpha))
    sh_far = int(round(188 * alpha)); sh_near = int(round(218 * alpha)); st_a = int(round(180 * alpha))
    off_far = max(2, int(round(1.8 * S))); off_near = max(1, int(round(0.9 * S))); stroke_w = max(1, int(round(0.9 * S)))
    dr.text((lx_main + off_far, ly_main + off_far), text, font=f_main, fill=(4, 4, 8, sh_far))
    dr.text((lx_main + off_near, ly_main + off_near), text, font=f_main, fill=(4, 4, 8, sh_near))
    dr.text((lx_main, ly_main), text, font=f_main, fill=(*ivory_gold, a255), stroke_width=stroke_w, stroke_fill=(14, 10, 8, st_a))
    layer.alpha_composite(fg)
    return _pack_roi(layer, rx0, ry0)
def _render_chapter_card_overlay(beat: TimelineBeat, *, alpha: float, scale: float, filament_prog: float=1.0, kicker_override: str | None=None, title_override: str | None=None, tone_override: str | None=None) -> OverlayROI | None:
    """V4/V9.2 Minimalist Zero-Box Chapter Title: ONLY tracked `CHƯƠNG I..N` + 3-4 punchy words (30*S), 0 divider, 0 subtitle."""
    del filament_prog
    if alpha <= 0.02:
        return None
    top_rgb, main_rgb, glow_rgb = _tone_colors(tone_override or beat.tone or 'gold')
    kicker = (kicker_override or f'CHƯƠNG {beat.chapter_roman}').strip().upper()
    title = (title_override or beat.main_word or beat.chapter_header).strip().upper(); kicker_sz = 15.0 * S; title_sz = 30.0 * S
    kicker_track = 3.2 * S * scale; title_track = 1.8 * S * scale; f_kicker = get_font(FONT_OSWALD, max(12, int(round(kicker_sz * scale))))
    f_title = get_font(FONT_BARLOW, max(20, int(round(title_sz * scale))))
    k_minx, k_miny, k_maxx, k_maxy, k_pl = _measure_tracked_text(kicker, f_kicker, kicker_track)
    t_minx, t_miny, t_maxx, t_maxy, t_pl = _measure_tracked_text(title, f_title, title_track); max_title_w = int(round(560 * S))
    while t_maxx - t_minx > max_title_w and title_sz > 22.0 * S:
        title_sz -= 2.0 * S; f_title = get_font(FONT_BARLOW, max(20, int(round(title_sz * scale))))
        t_minx, t_miny, t_maxx, t_maxy, t_pl = _measure_tracked_text(title, f_title, title_track)
    kw, kh = (max(1, k_maxx - k_minx), max(1, k_maxy - k_miny)); tw, th = (max(1, t_maxx - t_minx), max(1, t_maxy - t_miny))
    gap_y = int(round(13 * S)); total_h = kh + gap_y + th; y0 = max(BAR_H + int(round(24 * S)), BAR_H + ACT_H // 2 - total_h // 2)
    xk = (WIDTH - kw) // 2 - k_minx; yk = y0 - k_miny; xt = (WIDTH - tw) // 2 - t_minx
    yt = y0 + kh + gap_y - t_miny; glow_r = 8.5 * S; pad = int(math.ceil(glow_r * 2.4)) + int(round(10 * S))
    bx_left = min((WIDTH - kw) // 2, (WIDTH - tw) // 2); bx_right = max((WIDTH + kw) // 2, (WIDTH + tw) // 2); rx0 = max(0, bx_left - pad)
    ry0 = max(BAR_H, y0 - pad); rx1 = min(WIDTH, bx_right + pad); ry1 = min(BAR_H + ACT_H, y0 + total_h + pad)
    rw, rh = (rx1 - rx0, ry1 - ry0)
    if rw <= 2 or rh <= 2:
        return None
    lxk, lyk = (xk - rx0, yk - ry0); lxt, lyt = (xt - rx0, yt - ry0); gw, gh = (max(4, rw // 2), max(4, rh // 2))
    glow_full = Image.new('RGBA', (rw, rh), (0, 0, 0, 0)); gdr = ImageDraw.Draw(glow_full); ga = int(round(165 * alpha))
    _draw_tracked_text(gdr, lxk, lyk, k_pl, f_kicker, fill=(*glow_rgb, int(ga * 0.68)))
    _draw_tracked_text(gdr, lxt, lyt, t_pl, f_title, fill=(*glow_rgb, ga))
    glow_sm = glow_full.resize((gw, gh), Image.Resampling.BILINEAR).filter(ImageFilter.GaussianBlur(radius=glow_r * 0.5))
    layer = glow_sm.resize((rw, rh), Image.Resampling.BILINEAR); fg = Image.new('RGBA', (rw, rh), (0, 0, 0, 0)); dr = ImageDraw.Draw(fg)
    a255, sh_a, st_a = (int(round(255 * alpha)), int(round(230 * alpha)), int(round(215 * alpha))); k_sh = max(2, int(round(1.8 * S)))
    t_sh_x = max(2, int(round(2.5 * S))); t_sh_y = max(3, int(round(3.2 * S))); k_sw = max(1, int(round(1.3 * S)))
    t_sw = max(2, int(round(2.2 * S))); _draw_tracked_text(dr, lxk + k_sh, lyk + k_sh, k_pl, f_kicker, fill=(6, 6, 10, sh_a))
    _draw_tracked_text(dr, lxk, lyk, k_pl, f_kicker, fill=(*top_rgb, a255), stroke_width=k_sw, stroke_fill=(16, 10, 8, st_a))
    _draw_tracked_text(dr, lxt + t_sh_x, lyt + t_sh_y, t_pl, f_title, fill=(5, 5, 9, sh_a))
    _draw_tracked_text(dr, lxt, lyt, t_pl, f_title, fill=(*main_rgb, a255), stroke_width=t_sw, stroke_fill=(16, 10, 8, st_a))
    layer.alpha_composite(fg)
    return _pack_roi(layer, rx0, ry0)
def _get_card_dim_u8(h: int=GRADE_H, w: int=GRADE_W) -> np.ndarray:
    """Brightened chapter-card vignette (0.56..0.72) cached by grade resolution."""; key = (h, w); u8 = _CARD_VIGNETTE_CACHE.get(key)
    if u8 is None:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.clip(np.hypot((xx / max(1.0, w - 1.0) - 0.5) * 1.65, (yy / max(1.0, h - 1.0) - 0.5) * 2.0), 0.0, 1.6)
        mask = np.clip(0.72 - 0.14 * r ** 1.4, 0.56, 0.72)[:, :, None].astype(np.float32)
        u8 = np.repeat(np.clip(np.round(mask * 255.0), 0, 255).astype(np.uint8), 3, axis=2); _CARD_VIGNETTE_CACHE[key] = u8
    return u8
def _upscale_and_sharpen_active(act_grade: np.ndarray) -> np.ndarray:
    """Upscale graded active window to (WIDTH, ACT_H) via INTER_LANCZOS4 + crisp C++ detail sharpener."""
    if act_grade.shape[1] != WIDTH or act_grade.shape[0] != ACT_H:
        act = cv2.resize(act_grade, (WIDTH, ACT_H), interpolation=cv2.INTER_LANCZOS4)
    else:
        act = act_grade
    blur = cv2.GaussianBlur(act, (0, 0), 1.05)
    return cv2.addWeighted(act, 1.28, blur, -0.28, 0)
def _sample_active_window(bank: ShardFrameBank, beat: TimelineBeat, t: float, *, flare: float=0.0) -> np.ndarray:
    dur = max(0.01, beat.out_end - beat.out_start); u = _clamp01((t - beat.out_start) / dur)
    use_video = beat.video_clip_path is not None and beat.video_clip_path.is_file()
    if use_video:
        assert beat.video_clip_path is not None; c0 = max(0.0, min(CLIP_CLEAN_MAX_SEC - 0.1, beat.clip_start_sec))
        c1 = max(c0 + 0.1, min(CLIP_CLEAN_MAX_SEC, beat.clip_end_sec)); src_t = c0 + u * (c1 - c0)
        src = bank.sample_video_frame(beat.video_clip_path, src_t)
    else:
        src = bank.load_image(beat.primary_media_path)
    act_1280 = crop_25d(src, GRADE_W, GRADE_H, cy=0.44, zoom=1.0, dx=0.0, dy=0.0)
    act_1280 = apply_bright_golden_dawn_grade(act_1280, lift=beat.grade_lift, warmth=beat.grade_warmth, flare_boost=flare, sharpen=False)
    if beat.kind == 'chapter_card':
        dim_u8 = _get_card_dim_u8(GRADE_H, GRADE_W); dimmed = cv2.multiply(act_1280, dim_u8, scale=1.0 / 255.0)
        cv2.add(dimmed, (8, 5, 0, 0), dst=dimmed)
        return _upscale_and_sharpen_active(dimmed)
    return _upscale_and_sharpen_active(act_1280)
def _ffprobe_info(media_path: Path) -> dict[str, Any]:
    pr = _run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames,sample_rate,channels', '-of', 'json', str(media_path)])
    info = json.loads(pr.stdout); streams = info.get('streams', []); v_s = next((s for s in streams if s.get('codec_type') == 'video'), {})
    a_s = next((s for s in streams if s.get('codec_type') == 'audio'), {})
    return {'duration_sec': round(float(info.get('format', {}).get('duration', 0.0)), 3), 'size_bytes': int(info.get('format', {}).get('size', 0)), 'video_codec': v_s.get('codec_name'), 'width': int(v_s.get('width', 0)), 'height': int(v_s.get('height', 0)), 'r_frame_rate': v_s.get('r_frame_rate'), 'nb_frames': int(v_s['nb_frames']) if v_s.get('nb_frames') and str(v_s['nb_frames']).isdigit() else None, 'audio_codec': a_s.get('codec_name'), 'audio_sample_rate': int(a_s['sample_rate']) if a_s.get('sample_rate') else None, 'audio_channels': int(a_s['channels']) if a_s.get('channels') else None}
def _is_same_continuous_clip(a: TimelineBeat, b: TimelineBeat) -> bool:
    """True iff two adjacent narration beats belong to the exact same continuous chain and .mp4 clip."""
    return a.kind == 'narration' and b.kind == 'narration' and (a.video_clip_path is not None) and (b.video_clip_path is not None) and (a.video_clip_path == b.video_clip_path) and (not a.video_chain_id or not b.video_chain_id or a.video_chain_id == b.video_chain_id)
def render_shard(timeline_path: Path, shard_id: int, out_override: Path | None=None, *, raw_clips_dir: Path | None=None, require_moving_video: bool=False, max_frames: int | None=None, resolution_override: str | None=None) -> dict[str, Any]:
    t0 = time.time(); data, beats, starts = load_timeline(timeline_path, raw_clips_dir=raw_clips_dir, resolution_override=resolution_override)
    sh = data['shards'][str(shard_id)]; start_frame, end_frame = (int(sh['start_frame']), int(sh['end_frame']))
    if max_frames is not None and max_frames > 0:
        end_frame = min(end_frame, start_frame + int(max_frames))
    out_mp4 = out_override or Path(sh['output_video']); n_frames = end_frame - start_frame
    if n_frames <= 0:
        raise RuntimeError(f'Invalid shard {shard_id} range [{start_frame}, {end_frame})')
    shard_narr_beats = [b for b in beats if b.kind == 'narration' and b.end_frame > start_frame and (b.start_frame < end_frame)]
    missing_vids = [b.beat_id for b in shard_narr_beats if b.video_clip_path is None or not b.video_clip_path.is_file()]
    if require_moving_video and missing_vids:
        raise FileNotFoundError(f'[shard {shard_id}] --require-moving-video failed: {len(missing_vids)}/{len(shard_narr_beats)} narration beats lack moving .mp4 clips (first 8: {missing_vids[:8]})')
    print(f'[shard {shard_id}] Moving-video coverage: {len(shard_narr_beats) - len(missing_vids)}/{len(shard_narr_beats)} narration beats backed by real .mp4 clips ({WIDTH}x{HEIGHT} @ {FPS}fps)', flush=True)
    bank = ShardFrameBank(max_images=24, max_clips=4); tr_half_dissolve = 0.1; title_steady_cache: dict[int, OverlayROI | None] = {}
    card_steady_cache: dict[int, OverlayROI | None] = {}; frame = bank.build_static_imax_chrome().copy(); ay_min = BAR_H + int(round(18 * S))
    ay_max = HEIGHT - BAR_H - int(round(22 * S))
    print(f'[shard {shard_id}] Rendering frames [{start_frame}, {end_frame}) ({n_frames}f = {n_frames / FPS:.2f}s) -> {out_mp4}', flush=True)
    with ShardFFmpegWriter(out_mp4, WIDTH, HEIGHT, FPS, crf=16, preset='fast') as writer:
        for local_i, fi in enumerate(range(start_frame, end_frame)):
            t = fi / float(FPS); b_idx = max(0, min(len(beats) - 1, bisect.bisect_right(starts, fi) - 1)); beat = beats[b_idx]
            in_scene_ch = beat.in_scene_chapter_title; show_in_scene_ch = False; in_scene_alpha = 0.0
            in_scene_scale = 1.0
            if beat.kind == 'chapter_card':
                dt, rem = (t - beat.out_start, beat.out_end - t); alpha = _clamp01(dt / 0.2) * _clamp01(rem / 0.25)
                scale = 1.06 - 0.06 * _ease_out_cubic(_clamp01(dt / 0.24)); flare = 0.0
            else:
                if in_scene_ch is not None:
                    ov_dur = min(beat.out_end - beat.out_start - 0.1, float(in_scene_ch.get('duration_sec', IN_SCENE_CHAPTER_OVERLAY_SEC)))
                    dt_ch = t - beat.out_start
                    if 0.0 <= dt_ch <= ov_dur:
                        show_in_scene_ch = True; rem_ch = ov_dur - dt_ch; in_scene_alpha = _clamp01(dt_ch / 0.2) * _clamp01(rem_ch / 0.25)
                        in_scene_scale = 1.06 - 0.06 * _ease_out_cubic(_clamp01(dt_ch / 0.24))
                alpha, scale, flare = _compute_dignified_title_anim(t, beat)
            act = _sample_active_window(bank, beat, t, flare=flare)
            if b_idx > 0:
                prev_b = beats[b_idx - 1]
                if not _is_same_continuous_clip(prev_b, beat) and t - beat.out_start < tr_half_dissolve:
                    prev_act = _sample_active_window(bank, prev_b, prev_b.out_end - 0.01, flare=0.0); p = 0.5 + (t - beat.out_start) / (2.0 * tr_half_dissolve)
                    e = _ease_in_out_cubic(p); act = cv2.addWeighted(prev_act, 1.0 - e, act, e, 0.0)
            if b_idx < len(beats) - 1:
                next_b = beats[b_idx + 1]
                if not _is_same_continuous_clip(beat, next_b) and beat.out_end - t < tr_half_dissolve:
                    next_act = _sample_active_window(bank, next_b, next_b.out_start + 0.01, flare=0.0); p = 0.5 - (beat.out_end - t) / (2.0 * tr_half_dissolve)
                    e = _ease_in_out_cubic(p); act = cv2.addWeighted(act, 1.0 - e, next_act, e, 0.0)
            frame[BAR_H:BAR_H + ACT_H, :, :] = act
            if beat.kind == 'chapter_card':
                if alpha > 0.02:
                    if alpha > 0.995 and abs(scale - 1.0) < 0.0001:
                        if b_idx not in card_steady_cache:
                            card_steady_cache[b_idx] = _render_chapter_card_overlay(beat, alpha=1.0, scale=1.0)
                            if len(card_steady_cache) > 4:
                                card_steady_cache.pop(next(iter(card_steady_cache)))
                        ov_roi = card_steady_cache[b_idx]
                    else:
                        ov_roi = _render_chapter_card_overlay(beat, alpha=alpha, scale=scale)
                    _composite_roi_onto_rgb(frame, ov_roi)
            elif show_in_scene_ch and in_scene_ch is not None and (in_scene_alpha > 0.02):
                k_ov = str(in_scene_ch.get('header') or f'CHƯƠNG {beat.chapter_roman}'); t_ov = str(in_scene_ch.get('main_word') or beat.chapter_header)
                tone_ov = str(in_scene_ch.get('tone') or beat.tone or 'gold')
                if in_scene_alpha > 0.995 and abs(in_scene_scale - 1.0) < 0.0001:
                    if b_idx not in card_steady_cache:
                        card_steady_cache[b_idx] = _render_chapter_card_overlay(beat, alpha=1.0, scale=1.0, kicker_override=k_ov, title_override=t_ov, tone_override=tone_ov)
                        if len(card_steady_cache) > 4:
                            card_steady_cache.pop(next(iter(card_steady_cache)))
                    ov_roi = card_steady_cache[b_idx]
                else:
                    ov_roi = _render_chapter_card_overlay(beat, alpha=in_scene_alpha, scale=in_scene_scale, kicker_override=k_ov, title_override=t_ov, tone_override=tone_ov)
                _composite_roi_onto_rgb(frame, ov_roi)
            elif beat.show_keyword and beat.main_word and (alpha > 0.02):
                ay_clamped = max(ay_min, min(ay_max, beat.anchor_y))
                if alpha > 0.995 and abs(scale - 1.0) < 0.0001:
                    if b_idx not in title_steady_cache:
                        title_steady_cache[b_idx] = _render_monumental_title_layer('', beat.main_word, beat.anchor_x, ay_clamped, align=beat.align, tone=beat.tone, alpha=1.0, scale=1.0, flare=0.0, main_size=22)
                        if len(title_steady_cache) > 6:
                            title_steady_cache.pop(next(iter(title_steady_cache)))
                    ov_roi = title_steady_cache[b_idx]
                else:
                    ov_roi = _render_monumental_title_layer('', beat.main_word, beat.anchor_x, ay_clamped, align=beat.align, tone=beat.tone, alpha=alpha, scale=scale, flare=0.0, main_size=22)
                _composite_roi_onto_rgb(frame, ov_roi)
            _apply_film_grain_fast(frame, strength=0.011, seed=fi); writer.write_frame(frame)
            if (local_i + 1) % 600 == 0 or local_i + 1 == n_frames:
                el = time.time() - t0
                print(f'[shard {shard_id}] {local_i + 1}/{n_frames}f ({100.0 * (local_i + 1) / n_frames:.1f}%) · {el:.1f}s ({(local_i + 1) / max(0.01, el):.1f} fps)', flush=True)
    bank.close(); elapsed = max(0.01, time.time() - t0)
    result = {'shard_id': shard_id, 'output_video': str(out_mp4), 'resolution': f'{WIDTH}x{HEIGHT}', 'start_frame': start_frame, 'end_frame': end_frame, 'expected_frames': n_frames, 'moving_video_beats_in_shard': len(shard_narr_beats) - len(missing_vids), 'total_narration_beats_in_shard': len(shard_narr_beats), 'elapsed_sec': round(elapsed, 2), 'render_fps': round(n_frames / elapsed, 2), 'ffprobe': _ffprobe_info(out_mp4)}
    print(f'[shard {shard_id}] DONE -> {json.dumps(result, ensure_ascii=False)}', flush=True)
    return result
def _grab_frame_at(mp4_path: Path, sec: float) -> Image.Image:
    cap = cv2.VideoCapture(str(mp4_path)); fps = cap.get(cv2.CAP_PROP_FPS) or float(FPS); total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    idx = max(0, min(max(0, total - 1), int(round(sec * fps)))); cap.set(cv2.CAP_PROP_POS_FRAMES, idx); ok, bgr = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError(f'Failed grabbing frame @{sec:.2f}s from {mp4_path}')
    return Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB), mode='RGB')
def _fmt_mmss(sec: float) -> str:
    m = int(sec // 60)
    return f'{m:02d}:{sec - m * 60:04.1f}'
def build_10chapter_20panel_showcase(final_mp4: Path, beats: list[TimelineBeat], probe: dict[str, Any], ebur: dict[str, float], board_path: Path) -> None:
    """Build 20-frame (Chapters x 2 Panels) contact sheet verifying every chapter header & scene."""; by_ch: dict[int, list[TimelineBeat]] = {}
    for b in beats:
        by_ch.setdefault(b.chapter_idx, []).append(b)
    ch_ids = sorted(by_ch.keys())[:12]; tw, th = (480, 270); left_w = 310
    pad_x, pad_y = (16, 14); hdr_h, col_hdr_h = (104, 40); row_h = th + 8
    W = left_w + 2 * (tw + pad_x) + pad_x; H = hdr_h + col_hdr_h + len(ch_ids) * (row_h + pad_y) + 42
    board = Image.new('RGB', (W, H), (12, 14, 20)); dr = ImageDraw.Draw(board); dr.rectangle([0, 0, W, hdr_h - 4], fill=(18, 22, 32))
    dr.line([(0, hdr_h - 4), (W, hdr_h - 4)], fill=(246, 198, 78), width=3)
    dr.text((24, 14), f'MẪU M1-FLEX V9.2 · {len(ch_ids)} CHƯƠNG TỐI GIẢN · KHUNG HÌNH KIỂM ĐỊNH (IMAX 2.39:1)', font=get_font(FONT_BARLOW, 30), fill=(255, 232, 148))
    dur_m = int(probe['duration_sec'] // 60); dur_s = probe['duration_sec'] - dur_m * 60
    kw_total = sum((1 for b in beats if b.kind == 'narration' and b.show_keyword)); narr_total = sum((1 for b in beats if b.kind == 'narration'))
    dr.text((24, 62), f"Thời lượng: {dur_m:02d}m{dur_s:04.1f}s ({probe['duration_sec']:.1f}s) · {probe['width']}x{probe['height']}@30fps · {ebur['integrated_lufs']:.1f} LUFS / TP {ebur['true_peak_dbtp']:.1f} dBTP · {kw_total}/{narr_total} từ khóa · 0 chữ thanh đen", font=get_font(FONT_SANS, 14), fill=(212, 222, 236))
    col_titles = [('CỘT 1 · TIÊU ĐỀ CHƯƠNG TỐI GIẢN (ZERO SUBTITLE)', 'Chỉ CHƯƠNG I..N + 3-4 từ chính · 0 đường kẻ · cảnh nền sáng rõ'), ('CỘT 2 · ĐIỆN ẢNH IMAX & TỪ KHÓA LƯỢC GIÃN', 'Từ khóa đơn dòng tinh gọn · thanh đen sạch 100%')]
    for ci, (ct, cs) in enumerate(col_titles):
        cx = left_w + ci * (tw + pad_x)
        dr.rounded_rectangle([cx, hdr_h + 4, cx + tw, hdr_h + col_hdr_h], radius=5, fill=(22, 28, 40), outline=(92, 108, 136), width=1)
        dr.text((cx + 12, hdr_h + 6), ct, font=get_font(FONT_BARLOW, 16), fill=(255, 232, 162))
        dr.text((cx + 12, hdr_h + 24), cs, font=get_font(FONT_MONO, 9), fill=(176, 196, 218))
    accent_cycle = [(248, 198, 76), (255, 146, 56), (238, 186, 84), (244, 92, 68), (255, 168, 62), (248, 208, 92), (242, 136, 66), (244, 92, 68), (255, 198, 86), (236, 188, 96)]
    for ri, cid in enumerate(ch_ids):
        c_beats = by_ch[cid]; accent = accent_cycle[ri % len(accent_cycle)]; ry = hdr_h + col_hdr_h + 10 + ri * (row_h + pad_y)
        card_b = next((b for b in c_beats if b.kind == 'chapter_card'), c_beats[0])
        narr_beats = [b for b in c_beats if b.kind != 'chapter_card'] or c_beats
        kw_beats = [b for b in narr_beats if b.show_keyword and b.main_word]
        act_b = kw_beats[min(len(kw_beats) - 1, 1 if len(kw_beats) > 1 else 0)] if kw_beats else narr_beats[0]
        if card_b.kind == 'chapter_card':
            ts_card = min(card_b.out_end - 0.5, card_b.out_start + (card_b.out_end - card_b.out_start) * 0.5); ch_title_lbl = card_b.main_word
        else:
            ts_card = min(card_b.out_end - 0.3, card_b.out_start + 1.5)
            ch_title_lbl = str((card_b.in_scene_chapter_title or {}).get('main_word') or card_b.chapter_header)
        ts_act = min(act_b.hold_end_sec - 0.35, max(act_b.hit_sec + 0.45, act_b.hit_sec + 0.85)) if act_b.show_keyword and act_b.main_word else act_b.out_start + (act_b.out_end - act_b.out_start) * 0.5
        dr.rounded_rectangle([14, ry, left_w - 14, ry + th], radius=8, fill=(20, 24, 34), outline=accent, width=2)
        dr.rectangle([14, ry, 24, ry + th], fill=accent)
        dr.text((34, ry + 12), f'CHƯƠNG {card_b.chapter_roman}', font=get_font(FONT_BARLOW, 32), fill=accent)
        dr.text((34, ry + 52), ch_title_lbl[:28], font=get_font(FONT_BARLOW, 22), fill=(250, 246, 234))
        kw_list_lbl = ' · '.join((b.main_word for b in kw_beats)) or '(thuần điện ảnh)'; y_sub = ry + 90
        for ln in _wrap_lines(dr, f'Từ khóa ({len(kw_beats)}): {kw_list_lbl}', get_font(FONT_SANS, 12), left_w - 60, max_lines=4):
            dr.text((34, y_sub), ln, font=get_font(FONT_SANS, 12), fill=(188, 202, 220)); y_sub += 18
        dr.rounded_rectangle([34, ry + th - 58, left_w - 26, ry + th - 36], radius=4, fill=(30, 36, 50))
        dr.text((42, ry + th - 53), f'{_fmt_mmss(c_beats[0].out_start)} -> {_fmt_mmss(c_beats[-1].out_end)} ({len(narr_beats)} nhịp)', font=get_font(FONT_MONO, 10), fill=(242, 220, 152))
        dr.rounded_rectangle([34, ry + th - 30, left_w - 26, ry + th - 10], radius=4, fill=(26, 30, 42))
        dr.text((42, ry + th - 25), f"TỪ KHÓA: {act_b.main_word or '(điện ảnh thuần)'}"[:32], font=get_font(FONT_MONO, 9), fill=accent)
        for ci, (ts, tag_lbl) in enumerate([(ts_card, 'THẺ CHƯƠNG'), (ts_act, f'{act_b.beat_id} · {act_b.main_word[:16]}')]):
            cx = left_w + ci * (tw + pad_x); tile = _grab_frame_at(final_mp4, ts).resize((tw, th), Image.Resampling.LANCZOS); board.paste(tile, (cx, ry))
            dr.rectangle([cx, ry, cx + tw, ry + th], outline=accent, width=2); pill_txt = f'{_fmt_mmss(ts)} · {tag_lbl}'
            pw = min(tw - 60, dr.textbbox((0, 0), pill_txt, font=get_font(FONT_MONO, 9))[2] + 14)
            dr.rounded_rectangle([cx + tw - pw - 36, ry + th - 22, cx + tw - 36, ry + th - 6], radius=3, fill=(10, 12, 18))
            dr.text((cx + tw - pw - 30, ry + th - 20), pill_txt, font=get_font(FONT_MONO, 9), fill=accent)
    rel_lbl = final_mp4.relative_to(REPO_ROOT) if final_mp4.is_relative_to(REPO_ROOT) else final_mp4
    dr.text((24, H - 28), f'File đầy đủ: {rel_lbl}', font=get_font(FONT_SANS, 13), fill=(192, 204, 222))
    board_path.parent.mkdir(parents=True, exist_ok=True); board.save(board_path, quality=93)
def assemble_full_video(timeline_path: Path, video_out_dir: Path | None=None, *, final_filename: str=FINAL_FILENAME, showcase_filename: str=SHOWCASE_FILENAME) -> dict[str, Any]:
    t0 = time.time(); data, beats, _ = load_timeline(timeline_path); out_dir = video_out_dir or Path(data.get('video_out_dir') or VIDEO_OUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True); shard_keys = sorted((int(k) for k in data['shards'].keys())); shard_paths: list[Path] = []
    for sid in shard_keys:
        sp = Path(data['shards'][str(sid)]['output_video'])
        if not sp.is_file() or sp.stat().st_size == 0:
            raise FileNotFoundError(f'Missing or empty shard {sid} video: {sp}')
        shard_paths.append(sp)
    audio_wav = Path(data['audio_wav'])
    if not audio_wav.is_file() or audio_wav.stat().st_size == 0:
        raise FileNotFoundError(f'Missing master audio WAV: {audio_wav}')
    final_mp4 = out_dir / final_filename; showcase_jpg = out_dir / showcase_filename
    with tempfile.TemporaryDirectory(prefix='vp_m1_flex_asm_') as td:
        concat_txt = Path(td) / 'shards.txt'
        concat_txt.write_text('\n'.join((f"file '{sp.resolve().as_posix()}'" for sp in shard_paths)) + '\n', encoding='utf-8')
        _run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', str(concat_txt), '-i', str(audio_wav), '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-af', 'aresample=192000,alimiter=limit=0.77:attack=2:release=40:level=disabled,aresample=48000', '-c:a', 'aac', '-b:a', '256k', '-ar', str(TARGET_SR), '-ac', '2', '-shortest', '-movflags', '+faststart', str(final_mp4)])
    probe = _ffprobe_info(final_mp4); ebur = _measure_ebur128(final_mp4)
    build_10chapter_20panel_showcase(final_mp4, beats, probe, ebur, showcase_jpg)
    summary = {'final_mp4': str(final_mp4), 'showcase_jpg': str(showcase_jpg), 'shards_concatenated': len(shard_paths), 'elapsed_sec': round(time.time() - t0, 2), 'ffprobe': probe, 'ebur128': ebur}
    print(f'[assemble] DONE -> {json.dumps(summary, indent=2, ensure_ascii=False)}', flush=True)
    return summary
def _resolve_job_paths(args: argparse.Namespace) -> dict[str, Path]:
    job_dir = Path(args.job_dir).resolve() if args.job_dir else DEFAULT_RUN_DIR
    if args.script is not None:
        script_p = Path(args.script).resolve()
    else:
        candidates = [job_dir / 'script_1789_from_scratch.json', job_dir / 'script.json', *sorted(job_dir.glob('script*_from_scratch.json')), job_dir / 'content.json']
        script_p = next((c for c in candidates if c.is_file()), job_dir / 'script.json')
    audio_dir = Path(args.audio_dir).resolve() if args.audio_dir else job_dir / 'audio'
    frames_dir = Path(args.frames_dir).resolve() if args.frames_dir else job_dir / 'frames'
    raw_clips_dir = Path(args.raw_clips_dir).resolve() if args.raw_clips_dir else job_dir / 'raw_clips'
    timeline_p = Path(args.timeline).resolve() if args.timeline else job_dir / 'timeline_1789_full.json' if (job_dir / 'timeline_1789_full.json').is_file() else job_dir / 'timeline_m1_full.json'
    master_wav_p = Path(args.master_wav).resolve() if args.master_wav else job_dir / 'master_audio_1789_full.wav' if (job_dir / 'master_audio_1789_full.wav').is_file() else job_dir / 'master_audio_m1_full.wav'
    srt_p = Path(args.srt).resolve() if args.srt else job_dir / 'subtitles_impact_keywords.srt'
    full_cc_p = Path(args.full_cc_srt_path).resolve() if args.full_cc_srt_path else job_dir / 'subtitles_vi_full_cc.srt'
    out_dir_raw = args.output_dir or args.out_dir; out_dir = Path(out_dir_raw).resolve() if out_dir_raw else REPO_ROOT / 'video' / job_dir.name
    return {'job_dir': job_dir, 'script': script_p, 'audio_dir': audio_dir, 'frames_dir': frames_dir, 'raw_clips_dir': raw_clips_dir, 'timeline': timeline_p, 'master_wav': master_wav_p, 'srt': srt_p, 'full_cc_srt': full_cc_p, 'output_dir': out_dir}
def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Parameterized Turnkey M1-Flex V9.2 Long-Form Production Engine (Sử Kể Lại IMAX 2.39:1)')
    parser.add_argument('--stage', choices=('build-timeline', 'render-shard', 'assemble', 'full-cc-srt', 'validate-flex-spec'), default=None, help='Execution stage to run')
    parser.add_argument('--build-timeline', action='store_true', help='Build master audio, timeline JSON, impact SRT & full CC SRT')
    parser.add_argument('--shard', type=int, default=None, help='Render video shard 1..N')
    parser.add_argument('--max-frames', type=int, default=None, help='Optional cap on rendered frames for --shard benchmarking')
    parser.add_argument('--assemble', action='store_true', help='Losslessly concat shards + mux AAC 256k audio + 20-frame showcase')
    parser.add_argument('--full-cc-srt', action='store_true', help='Generate full Vietnamese narration closed-caption .srt from timeline')
    parser.add_argument('--validate-flex-spec', action='store_true', help='Validate M1-Flex V9.2 creative preset & safety invariants')
    parser.add_argument('--job-dir', type=Path, default=None, help='Job directory under sys/runs/<job_id>')
    parser.add_argument('--script', type=Path, default=None, help='Path to script JSON')
    parser.add_argument('--audio-dir', type=Path, default=None, help='Directory with beat_XXX.wav files')
    parser.add_argument('--frames-dir', type=Path, default=None, help='Directory with beat_XXX.png files')
    parser.add_argument('--raw-clips-dir', type=Path, default=None, help='Directory with chain_XX.mp4 / beat_XXX.mp4 clips')
    parser.add_argument('--require-moving-video', action='store_true', help='Fail fast if any shard narration beat lacks a moving .mp4 clip')
    parser.add_argument('--timeline', type=Path, default=None, help='Path to timeline JSON')
    parser.add_argument('--master-wav', type=Path, default=None, help='Path to master audio WAV')
    parser.add_argument('--srt', type=Path, default=None, help='Path to subtitles_impact_keywords.srt')
    parser.add_argument('--full-cc-srt-path', type=Path, default=None, help='Path to subtitles_vi_full_cc.srt')
    parser.add_argument('--output-dir', type=Path, default=None, help='Output directory for shards, final MP4 & showcase')
    parser.add_argument('--out-dir', type=Path, default=None, help='Alias for --output-dir')
    parser.add_argument('--out', type=Path, default=None, help='Optional output path override for --shard')
    parser.add_argument('--color-preset', choices=tuple(COLOR_PRESETS.keys()), default='golden_dawn_1789', help='Cinema color grade preset')
    parser.add_argument('--chapter-style', choices=tuple(CHAPTER_STYLES.keys()), default='minimal_center_card', help='Chapter title transition style')
    parser.add_argument('--chain-pattern', choices=tuple(CHAIN_PATTERNS.keys()), default='balanced_2beat', help='Continuous Flow .mp4 chain rhythm pattern')
    parser.add_argument('--keyword-density', type=float, default=0.22, help='Sparse single-line verbatim keyword density in [0.15, 0.30] (default: 0.22)')
    parser.add_argument('--resolution', choices=tuple(RESOLUTION_SPECS.keys()), default='1080p', help='Render resolution: 1080p (1920x1080), 1440p (2560x1440 2K), or 360p (640x360)')
    parser.add_argument('--total-shards', type=int, default=TOTAL_SHARDS, help='Number of parallel frame shards (default: 8)')
    parser.add_argument('--archetype', choices=tuple(NARRATIVE_ARCHETYPES.keys()), default='blitz_campaign', help='Narrative campaign archetype (6-12 chapters)')
    parser.add_argument('--skip-audio-master', action='store_true', help='Skip 2-pass FFmpeg loudnorm master WAV build during fast timeline testing')
    return parser
def main(argv: list[str] | None=None) -> int:
    parser = build_arg_parser(); args = parser.parse_args(argv); paths = _resolve_job_paths(args)
    stage = args.stage
    if not (stage or args.build_timeline or args.shard or args.assemble or args.full_cc_srt or args.validate_flex_spec):
        parser.error('Specify --stage {build-timeline,render-shard,assemble,full-cc-srt,validate-flex-spec} or a stage flag')
    if stage == 'validate-flex-spec' or args.validate_flex_spec:
        spec = validate_m1_flex_options(color_preset=args.color_preset, chapter_style=args.chapter_style, chain_pattern=args.chain_pattern, keyword_density=args.keyword_density, resolution=args.resolution, total_shards=args.total_shards, archetype=args.archetype)
        print(json.dumps(spec, ensure_ascii=False, indent=2), flush=True)
    if stage == 'build-timeline' or args.build_timeline:
        build_timeline_and_master_audio(script_path=paths['script'], audio_dir=paths['audio_dir'], frames_dir=paths['frames_dir'], timeline_path=paths['timeline'], master_wav_path=paths['master_wav'], srt_path=paths['srt'], video_out_dir=paths['output_dir'], raw_clips_dir=paths['raw_clips_dir'], color_preset=args.color_preset, chapter_style=args.chapter_style, chain_pattern=args.chain_pattern, keyword_density=args.keyword_density, resolution=args.resolution, total_shards=args.total_shards, archetype=args.archetype, full_cc_srt_path=paths['full_cc_srt'], skip_audio_master=args.skip_audio_master)
    if stage == 'render-shard' or args.shard is not None:
        if args.shard is None:
            parser.error('--stage render-shard requires --shard <1..N>')
        render_shard(paths['timeline'], int(args.shard), out_override=args.out, raw_clips_dir=paths['raw_clips_dir'], require_moving_video=args.require_moving_video, max_frames=args.max_frames, resolution_override=args.resolution if args.resolution else None)
    if stage == 'assemble' or args.assemble:
        assemble_full_video(paths['timeline'], video_out_dir=paths['output_dir'])
    if stage == 'full-cc-srt' or args.full_cc_srt:
        res = write_full_cc_srt(paths['timeline'], paths['full_cc_srt']); print(json.dumps(res, ensure_ascii=False, indent=2), flush=True)
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
