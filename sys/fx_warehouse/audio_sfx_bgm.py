"""Audio SFX & BGM Sub-Warehouse + Procedural Bespoke Topic SFX Synthesizer.

Manages the 25 shared 48kHz stereo SFX WAVs (`SFX_CATALOG`), 5 Niche BGM loops
(`BGM_CATALOG`), `ensure_warehouse_audio_assets(...)`, and `synthesize_bespoke_topic_sfx(...)`
for generating custom 48kHz stereo WAVs tailored to a specific video/topic when
no shared catalog WAV fits.
"""
from __future__ import annotations

import hashlib
import math
import re
import wave
from pathlib import Path
from typing import Any

import numpy as np
from scipy.signal import butter, sosfilt

SYS_DIR = Path(__file__).resolve().parent.parent
SFX_DIR = SYS_DIR / "assets" / "sfx"
BGM_DIR = SYS_DIR / "assets" / "audio" / "bgm"
TARGET_SR = 48000

EXISTING_SFX_FILES: tuple[str, ...] = (
    "ambient_focus_loop.wav",
    "clock_tick.wav",
    "ding_insight.wav",
    "page_flip.wav",
    "pen_highlight.wav",
    "pop_clean.wav",
    "whoosh_soft.wav",
)

SFX_CATALOG: dict[str, dict[str, Any]] = {
    # Existing base 2D SFX
    "ambient_focus_loop.wav": {"role": "ambient", "archetypes": ["all"]},
    "clock_tick.wav": {"role": "timing", "archetypes": ["all"]},
    "ding_insight.wav": {"role": "insight", "archetypes": ["all"]},
    "page_flip.wav": {"role": "paper", "archetypes": ["all"]},
    "pen_highlight.wav": {"role": "marker", "archetypes": ["all"]},
    "pop_clean.wav": {"role": "pop", "archetypes": ["all"]},
    "whoosh_soft.wav": {"role": "transition", "archetypes": ["all"]},
    # Expanded Warehouse 48kHz Stereo SFX
    "jet_flyby_doppler.wav": {"role": "flyby", "dur": 1.45},
    "typewriter_burst.wav": {"role": "telemetry", "dur": 0.65},
    "cold_wind_gust.wav": {"role": "atmosphere", "dur": 1.10},
    "sub_bass_boom.wav": {"role": "impact", "dur": 0.90},
    "stamp_slam_hit.wav": {"role": "impact", "dur": 0.60},
    "rotary_switch_click.wav": {"role": "mechanical", "dur": 0.45},
    "air_pressure_hiss.wav": {"role": "hiss", "dur": 1.50},
    "caution_chime_double.wav": {"role": "alarm", "dur": 0.85},
    "heartbeat_lub_dub.wav": {"role": "biometric", "dur": 0.95},
    "stopwatch_urgent_tick.wav": {"role": "timing", "dur": 0.50},
    "dossier_slide_whoosh.wav": {"role": "transition", "dur": 0.42},
    "radar_sonar_ping.wav": {"role": "telemetry", "dur": 0.70},
    "laser_split_whoosh.wav": {"role": "transition", "dur": 0.52},
    "card_lock_thud.wav": {"role": "impact", "dur": 0.55},
    "taiko_war_drum.wav": {"role": "epic", "dur": 1.00},
    "braaam_horn_low.wav": {"role": "epic", "dur": 1.40},
    "singing_bowl_zen.wav": {"role": "mindful", "dur": 2.40},
    "night_rain_soft.wav": {"role": "ambient", "dur": 2.50},
}

BGM_CATALOG: dict[str, dict[str, Any]] = {
    "bgm_forensic_noir_drone.wav": {"mood": "dark_forensic", "dur": 12.0},
    "bgm_geopolitics_pulse.wav": {"mood": "tense_pulse", "dur": 12.0},
    "bgm_scifi_biotech_pad.wav": {"mood": "cyan_telemetry", "dur": 12.0},
    "bgm_curious_acoustic_loop.wav": {"mood": "light_curious", "dur": 12.0},
    "bgm_zen_night_healing.wav": {"mood": "calm_warm", "dur": 12.0},
}


def _bandpass(sig: np.ndarray, low: float, high: float, sr: int = TARGET_SR, order: int = 3) -> np.ndarray:
    nyq = sr * 0.5
    lo = max(12.0 / nyq, min(0.95, low / nyq))
    hi = max(lo + 0.01, min(0.99, high / nyq))
    sos = butter(order, [lo, hi], btype="bandpass", output="sos")
    return sosfilt(sos, sig).astype(np.float32)


def _lowpass(sig: np.ndarray, cutoff: float, sr: int = TARGET_SR, order: int = 4) -> np.ndarray:
    nyq = sr * 0.5
    sos = butter(order, min(0.99, cutoff / nyq), btype="lowpass", output="sos")
    return sosfilt(sos, sig).astype(np.float32)


def _write_stereo_wav(path: Path, data: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    peak = float(np.max(np.abs(data))) if len(data) else 0.0
    if peak > 0.89:
        data = data * (0.89 / peak)
    pcm = np.clip(np.round(data * 32767.0), -32768, 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(TARGET_SR)
        wf.writeframes(pcm.tobytes())


def _synth_boom_mono(dur: float, f_start: float, f_end: float, amp: float) -> np.ndarray:
    n = int(round(dur * TARGET_SR))
    tt = np.arange(n, dtype=np.float64) / TARGET_SR
    freq = f_end + (f_start - f_end) * np.exp(-tt * 7.5)
    phase = 2.0 * math.pi * np.cumsum(freq) / TARGET_SR
    env = (1.0 - np.exp(-tt * 140.0)) * np.exp(-tt * 4.2)
    return (np.tanh(np.sin(phase) * 1.45) * env * amp).astype(np.float32)


def _synth_sfx_stem(name: str, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    dur = float(SFX_CATALOG[name].get("dur", 0.6))
    n = int(round(dur * TARGET_SR))
    tt = np.arange(n, dtype=np.float64) / TARGET_SR
    out = np.zeros((n, 2), dtype=np.float32)

    if name == "jet_flyby_doppler.wav":
        jet = _bandpass(rng.standard_normal(n).astype(np.float32), 220.0, 1200.0)
        whine = np.sin(2.0 * math.pi * np.cumsum(430.0 - 250.0 * (tt / max(0.3, tt[-1]))) / TARGET_SR)
        env = np.exp(-((tt - dur * 0.35) ** 2) / 0.10)
        pan_l = np.clip(1.15 - tt / max(0.3, tt[-1]), 0.25, 1.0)
        pan_r = np.clip(0.25 + tt / max(0.3, tt[-1]), 0.25, 1.0)
        core = (jet * 0.45 + whine * 0.12) * env
        out[:, 0], out[:, 1] = core * pan_l, core * pan_r
    elif name == "typewriter_burst.wav":
        for k in range(7):
            s0 = int((0.03 + k * 0.075) * TARGET_SR)
            m = min(int(0.018 * TARGET_SR), n - s0)
            if m > 0:
                t_loc = np.arange(m, dtype=np.float64) / TARGET_SR
                tk = (np.sin(2.0 * math.pi * (2750 + k * 60) * t_loc) + 0.35 * rng.standard_normal(m)) * np.exp(-t_loc * 260.0) * 0.45
                out[s0 : s0 + m, 0] += tk * 0.7
                out[s0 : s0 + m, 1] += tk
    elif name == "cold_wind_gust.wav":
        gust = _bandpass(rng.standard_normal(n).astype(np.float32), 180.0, 720.0)
        env = np.sin(math.pi * tt / dur) ** 1.4
        out[:, 0] = gust * env * 0.65
        out[:, 1] = np.roll(gust, 180) * env * 0.65
    elif name == "sub_bass_boom.wav":
        b = _synth_boom_mono(dur, 94.0, 34.0, 0.78)
        out[:, 0], out[:, 1] = b, b
    elif name == "stamp_slam_hit.wav":
        b = _synth_boom_mono(dur, 128.0, 33.0, 0.72)
        m = min(int(0.08 * TARGET_SR), n)
        snap = _bandpass(rng.standard_normal(m).astype(np.float32), 950.0, 3400.0) * np.exp(-tt[:m] * 70.0) * 0.55
        out[:, 0], out[:, 1] = b, b
        out[:m, 0] += snap
        out[:m, 1] += snap
    elif name == "rotary_switch_click.wav":
        for idx_c, (t_c, f_c) in enumerate(((0.04, 1450.0), (0.22, 2150.0))):
            s0 = int(t_c * TARGET_SR)
            m = min(int(0.032 * TARGET_SR), n - s0)
            t_loc = np.arange(m, dtype=np.float64) / TARGET_SR
            c = (np.sin(2.0 * math.pi * f_c * t_loc) + 0.5 * rng.standard_normal(m)) * np.exp(-t_loc * 220.0) * (0.55 + 0.1 * idx_c)
            out[s0 : s0 + m, 0] += c
            out[s0 : s0 + m, 1] += c * 0.85
    elif name == "air_pressure_hiss.wav":
        hiss = _bandpass(rng.standard_normal(n).astype(np.float32), 1800.0, 5400.0)
        env = (np.sin(math.pi * tt / dur) ** 0.8) * (0.7 + 0.3 * np.sin(2.0 * math.pi * 3.5 * tt))
        out[:, 0], out[:, 1] = hiss * env * 0.55, np.roll(hiss, 95) * env * 0.55
    elif name == "caution_chime_double.wav":
        for t_b in (0.04, 0.42):
            s0 = int(t_b * TARGET_SR)
            m = min(int(0.14 * TARGET_SR), n - s0)
            t_loc = np.arange(m, dtype=np.float64) / TARGET_SR
            beep = (0.65 * np.sin(2.0 * math.pi * 920.0 * t_loc) + 0.35 * np.sin(2.0 * math.pi * 460.0 * t_loc)) * np.sin(math.pi * t_loc / 0.14) ** 0.4 * 0.45
            out[s0 : s0 + m, 0] += beep
            out[s0 : s0 + m, 1] += beep
    elif name == "heartbeat_lub_dub.wav":
        b1 = _synth_boom_mono(0.20, 64.0, 34.0, 0.72)
        b2 = _synth_boom_mono(0.24, 54.0, 31.0, 0.52)
        s0, s1 = int(0.05 * TARGET_SR), int(0.30 * TARGET_SR)
        out[s0 : s0 + len(b1), 0] += b1
        out[s0 : s0 + len(b1), 1] += b1
        m2 = min(len(b2), n - s1)
        out[s1 : s1 + m2, 0] += b2[:m2]
        out[s1 : s1 + m2, 1] += b2[:m2]
    elif name == "stopwatch_urgent_tick.wav":
        for t_tk in (0.04, 0.28):
            s0 = int(t_tk * TARGET_SR)
            m = min(int(0.015 * TARGET_SR), n - s0)
            t_loc = np.arange(m, dtype=np.float64) / TARGET_SR
            tk = np.sin(2.0 * math.pi * 2450.0 * t_loc) * np.exp(-t_loc * 290.0) * 0.5
            out[s0 : s0 + m, 0] += tk * 0.85
            out[s0 : s0 + m, 1] += tk
    elif name in ("dossier_slide_whoosh.wav", "laser_split_whoosh.wav"):
        raw = rng.standard_normal(n).astype(np.float32)
        w = _bandpass(raw, 260.0, 2200.0) * (np.sin(math.pi * tt / dur) ** 1.4) * 0.75
        p = tt / dur
        out[:, 0] = w * (1.0 - 0.65 * p)
        out[:, 1] = w * (0.35 + 0.65 * p)
    elif name == "radar_sonar_ping.wav":
        ping = (0.8 * np.sin(2.0 * math.pi * 1340.0 * tt) + 0.2 * np.sin(2.0 * math.pi * 2680.0 * tt)) * (1.0 - np.exp(-tt * 220.0)) * np.exp(-tt * 6.0) * 0.52
        out[:, 0], out[:, 1] = ping, np.roll(ping, 60)
    elif name == "card_lock_thud.wav":
        for idx_k, (t_c, pan) in enumerate(((0.04, -0.5), (0.18, 0.0), (0.32, 0.5))):
            s0 = int(t_c * TARGET_SR)
            m = min(int(0.03 * TARGET_SR), n - s0)
            t_loc = np.arange(m, dtype=np.float64) / TARGET_SR
            c = np.sin(2.0 * math.pi * (1650.0 + idx_k * 180.0) * t_loc) * np.exp(-t_loc * 160.0) * 0.45
            out[s0 : s0 + m, 0] += c * (1.0 - max(0.0, pan) * 0.4)
            out[s0 : s0 + m, 1] += c * (1.0 - max(0.0, -pan) * 0.4)
    elif name == "taiko_war_drum.wav":
        drum = _synth_boom_mono(dur, 110.0, 42.0, 0.80)
        skin = _bandpass(rng.standard_normal(min(int(0.18 * TARGET_SR), n)).astype(np.float32), 250.0, 1200.0) * np.exp(-tt[: min(int(0.18 * TARGET_SR), n)] * 26.0) * 0.40
        out[:, 0], out[:, 1] = drum, drum
        out[: len(skin), 0] += skin
        out[: len(skin), 1] += skin
    elif name == "braaam_horn_low.wav":
        f0 = 55.0
        harm = sum((0.7 ** k) * np.sin(2.0 * math.pi * f0 * (k + 1) * tt + 0.1 * k) for k in range(6))
        env = (1.0 - np.exp(-tt * 12.0)) * np.exp(-tt * 1.4)
        braaam = _lowpass((np.tanh(harm * 0.65) * env * 0.55).astype(np.float32), 480.0)
        out[:, 0], out[:, 1] = braaam, np.roll(braaam, 120)
    elif name == "singing_bowl_zen.wav":
        bowl = (
            0.55 * np.sin(2.0 * math.pi * 256.0 * tt)
            + 0.30 * np.sin(2.0 * math.pi * 512.0 * tt)
            + 0.12 * np.sin(2.0 * math.pi * 768.2 * tt)
        ) * (1.0 - np.exp(-tt * 35.0)) * np.exp(-tt * 1.15)
        mod = 0.85 + 0.15 * np.sin(2.0 * math.pi * 2.1 * tt)
        out[:, 0] = (bowl * mod * 0.52).astype(np.float32)
        out[:, 1] = (bowl * (1.0 - (mod - 0.85)) * 0.52).astype(np.float32)
    elif name == "night_rain_soft.wav":
        rain_l = _bandpass(rng.standard_normal(n).astype(np.float32), 380.0, 2800.0)
        rain_r = _bandpass(rng.standard_normal(n).astype(np.float32), 380.0, 2800.0)
        fade = np.sin(math.pi * tt / dur) ** 0.5
        out[:, 0], out[:, 1] = rain_l * fade * 0.32, rain_r * fade * 0.32
    return out


def _synth_bgm_loop(name: str, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    dur = float(BGM_CATALOG[name]["dur"])
    n = int(round(dur * TARGET_SR))
    t = np.arange(n, dtype=np.float64) / TARGET_SR

    if name == "bgm_forensic_noir_drone.wav":
        left = 0.45 * np.sin(2 * math.pi * 73.42 * t) + 0.25 * np.sin(2 * math.pi * 110.0 * t + 0.4) + 0.14 * np.sin(2 * math.pi * 174.35 * t)
        right = 0.45 * np.sin(2 * math.pi * 73.68 * t + 0.2) + 0.25 * np.sin(2 * math.pi * 110.30 * t + 0.9) + 0.14 * np.sin(2 * math.pi * 174.85 * t)
        pulse = 0.80 + 0.20 * np.sin(2 * math.pi * 0.5 * t)
        buf = np.column_stack([_lowpass((left * pulse).astype(np.float32), 340.0), _lowpass((right * pulse).astype(np.float32), 340.0)]) * 0.45
    elif name == "bgm_geopolitics_pulse.wav":
        pulse = 0.65 + 0.35 * (np.sin(2 * math.pi * 1.5 * t) ** 2)
        left = 0.48 * np.sin(2 * math.pi * 82.41 * t) + 0.24 * np.sin(2 * math.pi * 123.47 * t)
        right = 0.48 * np.sin(2 * math.pi * 82.65 * t + 0.2) + 0.24 * np.sin(2 * math.pi * 123.80 * t)
        buf = np.column_stack([_lowpass((left * pulse).astype(np.float32), 360.0), _lowpass((right * pulse).astype(np.float32), 360.0)]) * 0.42
    elif name == "bgm_scifi_biotech_pad.wav":
        left = 0.42 * np.sin(2 * math.pi * 110.0 * t) + 0.24 * np.sin(2 * math.pi * 164.81 * t) + 0.12 * np.sin(2 * math.pi * 329.63 * t)
        right = 0.42 * np.sin(2 * math.pi * 110.25 * t + 0.3) + 0.24 * np.sin(2 * math.pi * 165.10 * t) + 0.12 * np.sin(2 * math.pi * 330.15 * t)
        buf = np.column_stack([_lowpass(left.astype(np.float32), 450.0), _lowpass(right.astype(np.float32), 450.0)]) * 0.40
    elif name == "bgm_curious_acoustic_loop.wav":
        pluck = np.zeros(n, dtype=np.float32)
        notes = [261.63, 329.63, 392.00, 329.63, 293.66, 349.23, 440.00, 349.23]
        step_s = int(0.5 * TARGET_SR)
        for i in range(int(dur / 0.5)):
            f = notes[i % len(notes)]
            s0 = i * step_s
            m = min(int(0.45 * TARGET_SR), n - s0)
            tt = np.arange(m, dtype=np.float64) / TARGET_SR
            pluck[s0 : s0 + m] += (np.sin(2 * math.pi * f * tt) * np.exp(-tt * 5.0) * 0.28).astype(np.float32)
        buf = np.column_stack([pluck, np.roll(pluck, 160)])
    else:  # bgm_zen_night_healing.wav
        left = 0.50 * np.sin(2 * math.pi * 128.0 * t) + 0.25 * np.sin(2 * math.pi * 192.0 * t)
        right = 0.50 * np.sin(2 * math.pi * 128.25 * t) + 0.25 * np.sin(2 * math.pi * 192.35 * t)
        rain = _bandpass(rng.standard_normal(n).astype(np.float32), 420.0, 2200.0) * 0.06
        buf = np.column_stack([left.astype(np.float32) * 0.28 + rain, right.astype(np.float32) * 0.28 + np.roll(rain, 140)])

    fade = min(n // 8, int(0.25 * TARGET_SR))
    buf[:fade] *= np.linspace(0.0, 1.0, fade, dtype=np.float32)[:, None]
    buf[-fade:] *= np.linspace(1.0, 0.0, fade, dtype=np.float32)[:, None]
    return buf


def ensure_warehouse_audio_assets(force: bool = False) -> dict[str, list[str]]:
    """Materialize any missing shared SFX/BGM WAV assets into sys/assets/ without altering originals."""
    created_sfx: list[str] = []
    created_bgm: list[str] = []
    SFX_DIR.mkdir(parents=True, exist_ok=True)
    BGM_DIR.mkdir(parents=True, exist_ok=True)

    for idx, name in enumerate(SFX_CATALOG):
        if name in EXISTING_SFX_FILES:
            continue
        p = SFX_DIR / name
        if force or not p.is_file() or p.stat().st_size < 1024:
            _write_stereo_wav(p, _synth_sfx_stem(name, seed=1000 + idx * 17))
            created_sfx.append(name)

    for idx, name in enumerate(BGM_CATALOG):
        p = BGM_DIR / name
        if force or not p.is_file() or p.stat().st_size < 4096:
            _write_stereo_wav(p, _synth_bgm_loop(name, seed=2000 + idx * 29))
            created_bgm.append(name)

    return {"created_sfx": created_sfx, "created_bgm": created_bgm}


def synthesize_bespoke_topic_sfx(
    spec_or_topic: dict[str, Any] | str,
    output_path: str | Path | None = None,
    seed: int = 42,
) -> dict[str, Any]:
    """Procedurally synthesize a custom 48kHz stereo WAV SFX/ambience for a specific video topic."""
    if isinstance(spec_or_topic, str):
        spec: dict[str, Any] = {"topic": spec_or_topic}
    else:
        spec = dict(spec_or_topic)

    topic = str(spec.get("topic", spec.get("headline", "bespoke_topic")))
    profile = str(spec.get("profile", spec.get("kind", "forensic_pulse"))).lower()
    dur = float(max(0.25, min(8.0, float(spec.get("dur", 1.1)))))
    n = int(round(dur * TARGET_SR))
    tt = np.arange(n, dtype=np.float64) / TARGET_SR
    rng = np.random.default_rng(seed)
    out = np.zeros((n, 2), dtype=np.float32)

    if profile in ("maritime_sonar", "geopolitical_radar"):
        f0 = float(spec.get("freq_hz", 980.0))
        ping = (0.75 * np.sin(2.0 * math.pi * f0 * tt) + 0.25 * np.sin(2.0 * math.pi * f0 * 2.0 * tt)) * (1.0 - np.exp(-tt * 180.0)) * np.exp(-tt * 3.8)
        water = _bandpass(rng.standard_normal(n).astype(np.float32), 140.0, 520.0) * 0.14 * np.sin(math.pi * tt / dur)
        out[:, 0] = (ping * 0.50 + water).astype(np.float32)
        out[:, 1] = (np.roll(ping, 96) * 0.50 + np.roll(water, 140)).astype(np.float32)
    elif profile in ("historical_resonance", "earth_rumble"):
        drum = _synth_boom_mono(dur, 118.0, 38.0, 0.72)
        rumble = _lowpass(rng.standard_normal(n).astype(np.float32), 260.0) * (np.sin(math.pi * tt / dur) ** 0.8) * 0.25
        out[:, 0] = (drum + rumble).astype(np.float32)
        out[:, 1] = (drum + np.roll(rumble, 110)).astype(np.float32)
    elif profile in ("cosmic_shimmer", "spark_chime", "tech_bleep"):
        f0 = float(spec.get("freq_hz", 528.0 if profile == "cosmic_shimmer" else 880.0))
        shimmer = (
            0.50 * np.sin(2.0 * math.pi * f0 * tt)
            + 0.30 * np.sin(2.0 * math.pi * (f0 * 1.5) * tt)
            + 0.20 * np.sin(2.0 * math.pi * (f0 * 2.01) * tt)
        ) * (1.0 - np.exp(-tt * 45.0)) * np.exp(-tt * 2.4)
        out[:, 0] = (shimmer * 0.45).astype(np.float32)
        out[:, 1] = (np.roll(shimmer, 75) * 0.45).astype(np.float32)
    elif profile in ("zen_bowl", "warm_pad", "night_ambience", "fireplace_warm"):
        f0 = float(spec.get("freq_hz", 256.0))
        pad = (0.55 * np.sin(2.0 * math.pi * f0 * tt) + 0.30 * np.sin(2.0 * math.pi * f0 * 1.5 * tt)) * (np.sin(math.pi * tt / dur) ** 0.7) * 0.32
        amb = _bandpass(rng.standard_normal(n).astype(np.float32), 320.0, 2000.0) * 0.10 * np.sin(math.pi * tt / dur)
        out[:, 0] = (pad + amb).astype(np.float32)
        out[:, 1] = (pad + np.roll(amb, 160)).astype(np.float32)
    elif profile in ("doodle_pop", "paper_crisp"):
        f0 = float(spec.get("freq_hz", 620.0))
        pop = np.sin(2.0 * math.pi * (f0 + 380.0 * np.exp(-tt * 35.0)) * tt) * np.exp(-tt * 14.0) * 0.55
        out[:, 0], out[:, 1] = pop.astype(np.float32), pop.astype(np.float32)
    else:  # forensic_pulse / noir_tension / biometric_pulse / mechanical_clockwork
        f0 = float(spec.get("freq_hz", 88.0))
        sub = _synth_boom_mono(dur, f0 * 1.5, max(30.0, f0 * 0.45), 0.65)
        tex = _bandpass(rng.standard_normal(n).astype(np.float32), 450.0, 1800.0) * np.exp(-tt * 5.0) * 0.18
        out[:, 0] = (sub + tex).astype(np.float32)
        out[:, 1] = (sub + np.roll(tex, 80)).astype(np.float32)

    fade = min(n // 10, int(0.03 * TARGET_SR))
    if fade > 1:
        out[:fade] *= np.linspace(0.0, 1.0, fade, dtype=np.float32)[:, None]
        out[-fade:] *= np.linspace(1.0, 0.0, fade, dtype=np.float32)[:, None]

    if output_path is not None:
        out_path = Path(output_path)
    else:
        slug = re.sub(r"[^a-z0-9]+", "_", topic.lower()).strip("_")[:36] or "topic"
        digest = hashlib.sha1(f"{topic}:{profile}:{dur}".encode("utf-8")).hexdigest()[:8]
        out_path = SFX_DIR / "bespoke" / f"bespoke_{slug}_{digest}.wav"

    _write_stereo_wav(out_path, out)
    return {
        "path": str(out_path),
        "wav_path": out_path,
        "sample_rate": TARGET_SR,
        "channels": 2,
        "dur": dur,
        "profile": profile,
        "topic": topic,
        "is_bespoke": True,
    }
