"""48kHz Stereo Procedural Suspense Audio Engine v2 & Calibrated Mastering.

Implements the upgraded 1.10x thriller/forensic audio architecture for Video Pilot:
- 4-Act evolving tension BGM (`compose_4act_tension_bgm`) with variants A/B/C,
  asymmetric voice-driven RMS sidechain ducking (25ms attack / 280ms release),
  and mandatory dead-air dropout windows before reveals.
- Authentic Boeing 737-300 warning horn (`synth_boeing_737_warning_horn`),
  Master Caution dual-chime (`synth_master_caution_chime`), and pressurized air-leak
  turbulence (`synth_air_leak_turbulence`).
- Synced transitions (`synth_riser_to_subdrop`, `synth_chapter_stinger`) and
  sub-preserving stereo SFX placement (`L/R ±20%`, center low sub).
- VHF Cockpit Radio / CVR static bed (`add_vhf_cockpit_bed`) and 360-2900Hz
  radio texture filter (`apply_vhf_radio_texture`).
- Linked-stereo 2-pass EBU R128 mastering (`master_2pass_wav_stereo`) and
  mono-collapse-free calibrated AAC 256k encoding (`encode_calibrated_m4a_stereo`),
  verifying `-11.0 ± 0.4 LUFS` and `true_peak_dbfs <= -1.0 dBTP` on both outputs.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import tempfile
import wave
from pathlib import Path
from typing import Any

import numpy as np
from scipy.ndimage import maximum_filter1d, uniform_filter1d
from scipy.signal import butter, sosfilt, sosfiltfilt

TARGET_SR = 48000
FPS = 30

VARIANT_PROFILES: dict[str, dict[str, Any]] = {
    "A": {
        "name": "Forensic Telemetry",
        "bgm_idle_gain": 0.165,
        "bgm_duck_db": -5.5,
        "act_gains": (0.95, 1.00, 1.08, 1.05, 0.90),
        "pulse_emphasis": 1.00,
        "cello_emphasis": 0.85,
        "dropout_scale": 1.00,
        "sfx_gain": 1.00,
    },
    "B": {
        "name": "LEMMiNO Chiaroscuro Noir",
        "bgm_idle_gain": 0.145,
        "bgm_duck_db": -6.8,
        "act_gains": (0.85, 0.88, 0.98, 0.94, 0.92),
        "pulse_emphasis": 0.42,
        "cello_emphasis": 1.38,
        "dropout_scale": 1.35,
        "sfx_gain": 0.86,
    },
    "C": {
        "name": "Vox/Fincher Kinetic",
        "bgm_idle_gain": 0.185,
        "bgm_duck_db": -4.8,
        "act_gains": (1.05, 1.15, 1.18, 1.20, 0.96),
        "pulse_emphasis": 1.45,
        "cello_emphasis": 0.95,
        "dropout_scale": 0.85,
        "sfx_gain": 1.12,
    },
}

_HELIOS_VHF_IDS = {
    "S1_B01", "S3_B03", "B00",
    "S005", "S046", "S065", "S066", "S069", "S075", "S103", "S104",
}
_HELIOS_HORN_IDS = {
    "S2_B03", "S2_B04", "B07", "B08",
    "S053", "S054", "S055", "S056", "S057", "S058", "S065", "S070", "S109",
}
_HELIOS_CAUTION_IDS = {"S073"}
_HELIOS_AIR_LEAK_IDS = {"S2_B02", "B05", "S033", "S034", "S035", "S067"}
_HELIOS_DROP_IDS = {"S1_B04", "S2_B04", "S3_B03", "S4_B01", "S4_B03", "B08", "B14", "B15", "S012", "S051", "S077", "S103", "S114"}


def _resolve_variant(variant: str) -> tuple[str, dict[str, Any]]:
    raw = str(variant or "A").strip().upper()
    if raw.startswith("OPTION_") and len(raw) == 8:
        raw = raw[-1]
    if raw not in VARIANT_PROFILES:
        raise ValueError(f"Unsupported suspense audio variant {variant!r}; expected 'A', 'B', or 'C'")
    return raw, VARIANT_PROFILES[raw]


def _ensure_stereo(data: np.ndarray, n_samples: int | None = None) -> np.ndarray:
    arr = np.asarray(data, dtype=np.float32)
    if arr.ndim == 1:
        arr = np.column_stack([arr, arr])
    elif arr.ndim == 2:
        if arr.shape[1] == 1:
            arr = np.column_stack([arr[:, 0], arr[:, 0]])
        elif arr.shape[1] > 2:
            arr = arr[:, :2]
    else:
        raise ValueError(f"Expected 1D or 2D audio array, got shape {arr.shape}")

    if n_samples is not None:
        if len(arr) < n_samples:
            pad = np.zeros((n_samples - len(arr), 2), dtype=np.float32)
            arr = np.vstack([arr, pad])
        elif len(arr) > n_samples:
            arr = arr[:n_samples]
    return np.ascontiguousarray(arr, dtype=np.float32)


def _read_wav_stereo(path: Path | str, target_sr: int = TARGET_SR) -> np.ndarray:
    p = Path(path)
    with wave.open(str(p), "rb") as wf:
        sr = wf.getframerate()
        nch = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        nf = wf.getnframes()
        if sr == target_sr and sampwidth == 2:
            raw = np.frombuffer(wf.readframes(nf), dtype=np.int16).astype(np.float32) / 32768.0
            arr = raw.reshape(-1, nch)
            return _ensure_stereo(arr)

    with tempfile.TemporaryDirectory() as td:
        conv = Path(td) / "conv48k.f32"
        subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-y", "-i", str(p),
                "-ar", str(target_sr), "-ac", "2", "-f", "f32le", str(conv),
            ],
            capture_output=True,
            check=True,
        )
        arr = np.frombuffer(conv.read_bytes(), dtype=np.float32).reshape(-1, 2)
        return np.ascontiguousarray(arr, dtype=np.float32)


def _write_wav_stereo(path: Path | str, data: np.ndarray, sr: int = TARGET_SR) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    stereo = _ensure_stereo(data)
    pcm = np.clip(np.round(stereo * 32767.0), -32768, 32767).astype(np.int16)
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(int(sr))
        wf.writeframes(pcm.tobytes())


def _lowpass(sig: np.ndarray, cutoff: float, sr: int = TARGET_SR, order: int = 4, zero_phase: bool = False) -> np.ndarray:
    nyq = sr * 0.5
    wn = max(10.0 / nyq, min(0.99, cutoff / nyq))
    sos = butter(order, wn, btype="lowpass", output="sos")
    if zero_phase and len(sig) > 32:
        return sosfiltfilt(sos, sig.astype(np.float64)).astype(np.float32)
    return sosfilt(sos, sig).astype(np.float32)


def _highpass(sig: np.ndarray, cutoff: float, sr: int = TARGET_SR, order: int = 3) -> np.ndarray:
    nyq = sr * 0.5
    wn = max(8.0 / nyq, min(0.98, cutoff / nyq))
    sos = butter(order, wn, btype="highpass", output="sos")
    return sosfilt(sos, sig).astype(np.float32)


def _bandpass(sig: np.ndarray, low: float, high: float, sr: int = TARGET_SR, order: int = 3) -> np.ndarray:
    nyq = sr * 0.5
    lo = max(10.0 / nyq, min(0.94, low / nyq))
    hi = max(lo + 0.01, min(0.99, high / nyq))
    sos = butter(order, [lo, hi], btype="bandpass", output="sos")
    return sosfilt(sos, sig).astype(np.float32)


def _peaking_eq_filter(sig: np.ndarray, freq_hz: float, q: float, gain_db: float, sr: int = TARGET_SR) -> np.ndarray:
    """Apply an RBJ peaking EQ biquad filter cleanly via SciPy sosfilt."""
    a_lin = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * math.pi * (freq_hz / float(sr))
    alpha = math.sin(w0) / (2.0 * max(0.1, q))
    cos_w0 = math.cos(w0)
    b0 = 1.0 + alpha * a_lin
    b1 = -2.0 * cos_w0
    b2 = 1.0 - alpha * a_lin
    a0 = 1.0 + alpha / a_lin
    a1 = -2.0 * cos_w0
    a2 = 1.0 - alpha / a_lin
    sos = np.array([[b0 / a0, b1 / a0, b2 / a0, 1.0, a1 / a0, a2 / a0]], dtype=np.float64)
    return sosfilt(sos, sig.astype(np.float64)).astype(np.float32)


def _edge_fade(n: int, fade_in: int, fade_out: int) -> np.ndarray:
    env = np.ones(n, dtype=np.float32)
    fi = min(n, max(0, fade_in))
    fo = min(n, max(0, fade_out))
    if fi > 1:
        env[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)
    if fo > 1:
        env[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)
    return env


def measure_ebur128(path: Path | str) -> dict[str, float]:
    """Measure integrated LUFS and true peak (dBTP) using FFmpeg ebur128=peak=true."""
    res = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    m_i = re.findall(r"\bI:\s*(-?\d+(?:\.\d+)?)\s*LUFS", res.stderr)
    m_tp = re.findall(r"\bPeak:\s*(-?\d+(?:\.\d+)?)\s*dBFS", res.stderr)
    m_lra = re.findall(r"\bLRA:\s*(-?\d+(?:\.\d+)?)\s*LU", res.stderr)
    return {
        "integrated_lufs": float(m_i[-1]) if m_i else -99.0,
        "true_peak_dbfs": float(m_tp[-1]) if m_tp else 0.0,
        "lra_lu": float(m_lra[-1]) if m_lra else 0.0,
    }


def apply_stereo_pan(
    sig: np.ndarray,
    pan: float = 0.0,
    sr: int = TARGET_SR,
    sub_crossover_hz: float = 120.0,
    max_pan: float = 0.20,
) -> np.ndarray:
    """Apply subtle L/R stereo imaging (±20% default) while keeping sub-bass centered."""
    stereo = _ensure_stereo(sig)
    if len(stereo) == 0:
        return stereo
    p = float(np.clip(pan, -abs(max_pan), abs(max_pan)))
    if abs(p) < 1e-4:
        return stereo.copy()

    # Keep low frequencies strictly centered using zero-phase crossover so (sig - sub) cancels sub cleanly
    if sub_crossover_hz > 10.0 and len(stereo) > 64:
        sub_l = _lowpass(stereo[:, 0], sub_crossover_hz, sr=sr, order=3, zero_phase=True)
        sub_r = _lowpass(stereo[:, 1], sub_crossover_hz, sr=sr, order=3, zero_phase=True)
        sub_center = 0.5 * (sub_l + sub_r)
        hi_l = stereo[:, 0] - sub_l
        hi_r = stereo[:, 1] - sub_r
    else:
        sub_center = np.zeros(len(stereo), dtype=np.float32)
        hi_l = stereo[:, 0]
        hi_r = stereo[:, 1]

    # Constant-power subtle pan: at p=+0.20, gain_l ~= 0.88, gain_r ~= 1.10 (~±20% delta)
    theta = (p + 1.0) * (math.pi * 0.25)
    gl = math.cos(theta) * math.sqrt(2.0)
    gr = math.sin(theta) * math.sqrt(2.0)

    out = np.empty_like(stereo)
    out[:, 0] = sub_center + hi_l * gl
    out[:, 1] = sub_center + hi_r * gr
    return out


def place_stereo_sfx(
    buf: np.ndarray,
    sfx: np.ndarray,
    start_sec: float,
    pan: float = 0.0,
    gain: float = 1.0,
    sr: int = TARGET_SR,
    sub_crossover_hz: float = 120.0,
    max_pan: float = 0.20,
) -> None:
    """Mix mono or stereo SFX into `buf` at `start_sec` with subtle L/R ±20% imaging and centered sub."""
    if len(buf) == 0 or len(sfx) == 0:
        return
    panned = apply_stereo_pan(sfx, pan=pan, sr=sr, sub_crossover_hz=sub_crossover_hz, max_pan=max_pan)
    if abs(gain - 1.0) > 1e-6:
        panned = panned * float(gain)

    s0 = int(round(start_sec * sr))
    if s0 >= len(buf):
        return
    if s0 < 0:
        panned = panned[-s0:]
        s0 = 0
    n = min(len(panned), len(buf) - s0)
    if n <= 0:
        return
    buf[s0 : s0 + n] += panned[:n]


# ---------------------------------------------------------------------------
# Procedural Aviation & Thriller SFX Synthesizers (48kHz Stereo)
# ---------------------------------------------------------------------------

def synth_boeing_737_warning_horn(
    dur_sec: float = 2.6,
    sr: int = TARGET_SR,
    pulsed: bool = True,
    gain: float = 0.14,
) -> np.ndarray:
    """Synthesize authentic Boeing 737-300 Classic Takeoff Config / Cabin Alt warning horn.

    Uses ~510 Hz fundamental + 1020/1530/2040/2550 Hz nasal saw-square harmonics,
    420-3200 Hz bandpass, and sharp 2.0 Hz (250ms ON / 250ms OFF) gate.
    """
    n = max(1, int(round(max(0.05, dur_sec) * sr)))
    tt = np.arange(n, dtype=np.float64) / float(sr)

    # Slight dual-detune mechanical piezo instability (~510Hz + 511.8Hz)
    f0 = 510.0 + 1.2 * np.sin(2.0 * math.pi * 6.5 * tt)
    ph1 = 2.0 * math.pi * np.cumsum(f0) / float(sr)
    ph2 = 2.0 * math.pi * np.cumsum(f0 * 1.0035) / float(sr)

    # Nasal saw + odd-heavy square cluster: 510, 1020, 1530, 2040, 2550 Hz
    weights = (1.00, 0.72, 0.88, 0.46, 0.56)
    core_l = np.zeros(n, dtype=np.float64)
    core_r = np.zeros(n, dtype=np.float64)
    for k, w in enumerate(weights, start=1):
        core_l += w * np.sin(k * ph1 + 0.14 * k)
        core_r += w * np.sin(k * ph2 + 0.31 * k)

    # Gentle electromechanical saturation + 420-3200 Hz aviation horn bandpass
    horn_l = _bandpass(np.tanh(core_l * 0.65).astype(np.float32), 420.0, 3200.0, sr=sr, order=4)
    horn_r = _bandpass(np.tanh(core_r * 0.65).astype(np.float32), 420.0, 3200.0, sr=sr, order=4)

    # Normalize continuous core RMS cleanly before gating so `gain` tracks -19 dBFS calibration
    rms_core = float(np.sqrt(np.mean(0.5 * (horn_l ** 2 + horn_r ** 2)))) + 1e-8
    norm_scale = 0.55 / rms_core
    horn_l *= norm_scale
    horn_r *= norm_scale

    if pulsed:
        # Sharp 2.0 Hz gate: 250ms ON / 250ms OFF with 4ms anti-click micro-ramps
        cycle = np.mod(tt, 0.50)
        on_win = (cycle < 0.25).astype(np.float64)
        ramp_s = max(1, int(0.004 * sr))
        kern = np.hanning(ramp_s * 2 + 1)
        kern /= kern.sum()
        gate = np.convolve(on_win, kern, mode="same").astype(np.float32)
    else:
        gate = np.ones(n, dtype=np.float32)

    fade = _edge_fade(n, int(0.006 * sr), int(0.015 * sr))
    env = gate * fade * float(gain)

    # Subtle cockpit acoustic reflection offset on right channel (~0.9ms + slight level tilt)
    shift = max(1, int(0.0009 * sr))
    horn_r_spatial = np.roll(horn_r, shift) * 0.94 + horn_l * 0.06
    out = np.column_stack([horn_l * env, horn_r_spatial * env]).astype(np.float32)
    return out


def synth_master_caution_chime(
    dur_sec: float = 0.85,
    sr: int = TARGET_SR,
    gain: float = 0.13,
) -> np.ndarray:
    """Synthesize clean aviation Master Caution dual-chime (784 Hz -> 523.25 Hz)."""
    n = max(1, int(round(max(0.25, dur_sec) * sr)))
    tt = np.arange(n, dtype=np.float64) / float(sr)

    t_second = min(0.32, dur_sec * 0.40)
    s_second = int(round(t_second * sr))

    # First chime: 784 Hz (G5)
    t1 = tt
    env1 = (1.0 - np.exp(-t1 * 260.0)) * np.exp(-t1 * 7.5)
    c1 = (0.78 * np.sin(2.0 * math.pi * 784.0 * t1) + 0.18 * np.sin(2.0 * math.pi * 1568.0 * t1)) * env1

    # Second chime: 523.25 Hz (C5)
    c2 = np.zeros(n, dtype=np.float64)
    if n > s_second:
        t2 = np.arange(n - s_second, dtype=np.float64) / float(sr)
        env2 = (1.0 - np.exp(-t2 * 260.0)) * np.exp(-t2 * 5.2)
        c2[s_second:] = (
            0.80 * np.sin(2.0 * math.pi * 523.25 * t2)
            + 0.16 * np.sin(2.0 * math.pi * 1046.5 * t2)
        ) * env2

    mono = ((c1 + c2) * float(gain)).astype(np.float32) * _edge_fade(n, int(0.004 * sr), int(0.025 * sr))
    out = np.column_stack([mono * 1.03, np.roll(mono, max(1, int(0.0007 * sr))) * 0.97]).astype(np.float32)
    return out


def synth_air_leak_turbulence(
    dur_sec: float = 1.8,
    sr: int = TARGET_SR,
    gain: float = 0.11,
    seed: int = 42,
) -> np.ndarray:
    """Synthesize pressurized outflow valve air-leak hiss & turbulence (1.2-6 kHz)."""
    rng = np.random.default_rng(seed)
    n = max(1, int(round(max(0.20, dur_sec) * sr)))
    tt = np.arange(n, dtype=np.float64) / float(sr)

    raw_l = rng.standard_normal(n).astype(np.float32)
    raw_r = rng.standard_normal(n).astype(np.float32)
    hiss_l = _bandpass(raw_l, 1200.0, 6000.0, sr=sr, order=3)
    hiss_r = _bandpass(raw_r, 1200.0, 6000.0, sr=sr, order=3)

    # Subtle pressurized whistle bleed resonance + fuselage low-end buffet
    whistle = (
        0.16 * np.sin(2.0 * math.pi * (2420.0 + 35.0 * np.sin(2.0 * math.pi * 2.4 * tt)) * tt)
        + 0.10 * np.sin(2.0 * math.pi * 3680.0 * tt)
    ).astype(np.float32)
    buffet = _bandpass(rng.standard_normal(n).astype(np.float32), 85.0, 280.0, sr=sr, order=2) * 0.18

    mod_l = (0.72 + 0.28 * np.sin(2.0 * math.pi * 3.1 * tt + 0.3)).astype(np.float32)
    mod_r = (0.72 + 0.28 * np.sin(2.0 * math.pi * 3.4 * tt + 1.4)).astype(np.float32)
    macro_env = (np.sin(math.pi * tt / max(0.05, dur_sec)) ** 0.65).astype(np.float32)

    l_ch = (hiss_l * mod_l + whistle * 0.35 * mod_l + buffet) * macro_env
    r_ch = (hiss_r * mod_r + whistle * 0.35 * mod_r + buffet) * macro_env

    rms = float(np.sqrt(np.mean(0.5 * (l_ch ** 2 + r_ch ** 2)))) + 1e-8
    scale = (0.45 / rms) * float(gain)
    fade = _edge_fade(n, int(0.03 * sr), int(0.06 * sr))
    return np.column_stack([l_ch * scale * fade, r_ch * scale * fade]).astype(np.float32)


def synth_riser_to_subdrop(
    riser_dur: float = 0.65,
    gap_dur: float = 0.45,
    drop_dur: float = 0.42,
    sr: int = TARGET_SR,
    riser_gain: float = 0.14,
    drop_gain: float = 0.22,
    seed: int = 42,
) -> np.ndarray:
    """Synthesize reverse filtered riser (55->220 Hz) -> silence gap -> sub-bass drop (85->36 Hz)."""
    rng = np.random.default_rng(seed)
    n_riser = max(1, int(round(max(0.05, riser_dur) * sr)))
    n_gap = max(0, int(round(max(0.0, gap_dur) * sr)))
    n_drop = max(1, int(round(max(0.05, drop_dur) * sr)))
    n_tot = n_riser + n_gap + n_drop
    out = np.zeros((n_tot, 2), dtype=np.float32)

    # 1. Filtered Riser: 55 -> 220 Hz sweep + filtered reverse air tension
    t_r = np.arange(n_riser, dtype=np.float64) / float(sr)
    u_r = t_r / max(1e-6, riser_dur)
    freq_r = 55.0 + (220.0 - 55.0) * (u_r ** 1.7)
    ph_r = 2.0 * math.pi * np.cumsum(freq_r) / float(sr)
    tonal_r = np.sin(ph_r) + 0.35 * np.sin(2.0 * ph_r + 0.4)
    air_l = _bandpass(rng.standard_normal(n_riser).astype(np.float32), 260.0, 2200.0, sr=sr, order=2)
    air_r = _bandpass(rng.standard_normal(n_riser).astype(np.float32), 260.0, 2200.0, sr=sr, order=2)
    env_r = ((u_r ** 2.1) * (1.0 - np.exp(-(1.0 - u_r) * 14.0))).astype(np.float32)
    riser_l = (tonal_r.astype(np.float32) * 0.55 + air_l * 0.75) * env_r * float(riser_gain)
    riser_r = (tonal_r.astype(np.float32) * 0.55 + air_r * 0.75) * env_r * float(riser_gain)
    out[:n_riser, 0] = riser_l
    out[:n_riser, 1] = riser_r

    # 2. Gap [n_riser : n_riser + n_gap] remains exact 0.0 dead air

    # 3. Sub-Bass Drop: 85 -> 36 Hz centered sub + subtle stereo upper click
    t_d = np.arange(n_drop, dtype=np.float64) / float(sr)
    freq_d = 36.0 + (85.0 - 36.0) * np.exp(-t_d * 10.5)
    ph_d = 2.0 * math.pi * np.cumsum(freq_d) / float(sr)
    env_d = (1.0 - np.exp(-t_d * 220.0)) * np.exp(-t_d * 6.5)
    sub_d = (np.tanh(np.sin(ph_d) * 1.35) * env_d * float(drop_gain)).astype(np.float32)
    sub_d *= _edge_fade(n_drop, 0, int(0.025 * sr))

    # Tiny stereo click transient (0..25ms) for translation on laptop/phone speakers
    m_clk = min(n_drop, int(0.025 * sr))
    clk = _bandpass(rng.standard_normal(m_clk).astype(np.float32), 700.0, 2400.0, sr=sr, order=2)
    clk *= np.exp(-np.arange(m_clk, dtype=np.float32) / float(sr) * 180.0) * (float(drop_gain) * 0.25)

    d0 = n_riser + n_gap
    out[d0:, 0] = sub_d
    out[d0:, 1] = sub_d
    out[d0 : d0 + m_clk, 0] += clk * 0.92
    out[d0 : d0 + m_clk, 1] += clk * 1.08
    return out


def synth_chapter_stinger(
    sr: int = TARGET_SR,
    dur_sec: float = 1.30,
    gain: float = 0.18,
    seed: int = 42,
) -> np.ndarray:
    """Synthesize 48kHz stereo forensic metallic chapter stinger with centered sub anchor."""
    rng = np.random.default_rng(seed)
    n = max(1, int(round(max(0.40, dur_sec) * sr)))

    # Pre-impact short reverse breath (0..120ms), hit at t_hit = 0.10s
    t_hit = min(0.10, dur_sec * 0.15)
    s_hit = int(round(t_hit * sr))
    out = np.zeros((n, 2), dtype=np.float32)

    if s_hit > 16:
        t_pre = np.arange(s_hit, dtype=np.float64) / float(sr)
        pre_env = (t_pre / max(1e-6, t_hit)) ** 2.2
        pre_l = _bandpass(rng.standard_normal(s_hit).astype(np.float32), 450.0, 2800.0, sr=sr, order=2) * pre_env
        pre_r = _bandpass(rng.standard_normal(s_hit).astype(np.float32), 450.0, 2800.0, sr=sr, order=2) * pre_env
        out[:s_hit, 0] += pre_l * (float(gain) * 0.45)
        out[:s_hit, 1] += pre_r * (float(gain) * 0.45)

    m = n - s_hit
    if m > 0:
        t_p = np.arange(m, dtype=np.float64) / float(sr)
        # Centered sub-bass thud (92 -> 35 Hz)
        f_sub = 35.0 + (92.0 - 35.0) * np.exp(-t_p * 8.5)
        ph_sub = 2.0 * math.pi * np.cumsum(f_sub) / float(sr)
        sub = np.tanh(np.sin(ph_sub) * 1.35) * (1.0 - np.exp(-t_p * 240.0)) * np.exp(-t_p * 4.5)

        # Metallic forensic anvil/sonar chord partials with subtle L/R stereo shimmer
        partials = ((412.0, 0.34, 3.8), (654.0, 0.24, 4.4), (1118.0, 0.16, 5.5), (1742.0, 0.10, 7.0))
        metal_l = np.zeros(m, dtype=np.float64)
        metal_r = np.zeros(m, dtype=np.float64)
        for idx_p, (fp, amp, dec) in enumerate(partials):
            env_m = (1.0 - np.exp(-t_p * 300.0)) * np.exp(-t_p * dec)
            metal_l += amp * env_m * np.sin(2.0 * math.pi * fp * t_p + 0.2 * idx_p)
            metal_r += amp * env_m * np.sin(2.0 * math.pi * (fp * 1.0025) * t_p + 0.9 * idx_p)

        # Crisp transient click
        snap = _bandpass(rng.standard_normal(m).astype(np.float32), 1100.0, 4200.0, sr=sr, order=2)
        snap *= np.exp(-t_p.astype(np.float32) * 55.0) * 0.35

        fade = _edge_fade(m, 0, int(0.08 * sr))
        out[s_hit:, 0] += ((sub * 0.85 + metal_l * 0.50).astype(np.float32) + snap * 0.90) * fade * float(gain)
        out[s_hit:, 1] += ((sub * 0.85 + metal_r * 0.50).astype(np.float32) + snap * 1.10) * fade * float(gain)

    return out


# ---------------------------------------------------------------------------
# VHF Cockpit Radio Static Bed & 360-2900Hz Radio Texture
# ---------------------------------------------------------------------------

def _synth_ptt_click(sr: int, is_end: bool = False, seed: int = 11) -> np.ndarray:
    rng = np.random.default_rng(seed)
    dur = 0.080 if is_end else 0.048
    n = max(8, int(round(dur * sr)))
    tt = np.arange(n, dtype=np.float64) / float(sr)

    noise = _bandpass(rng.standard_normal(n).astype(np.float32), 600.0, 3400.0, sr=sr, order=2)
    squelch_env = np.exp(-tt * (48.0 if is_end else 72.0)).astype(np.float32)
    click = noise * squelch_env * 0.14

    if is_end:
        # Short classic aviation VHF roger-click chirp (1820 -> 1480 Hz)
        f_chirp = 1820.0 - 340.0 * (tt / max(1e-6, dur))
        ph = 2.0 * math.pi * np.cumsum(f_chirp) / float(sr)
        chirp = np.sin(ph) * (1.0 - np.exp(-tt * 350.0)) * np.exp(-tt * 38.0)
        click += (chirp * 0.09).astype(np.float32)

    click *= _edge_fade(n, int(0.002 * sr), int(0.006 * sr))
    return np.column_stack([click * 0.94, click * 1.06]).astype(np.float32)


def add_vhf_cockpit_bed(
    audio_stereo: np.ndarray,
    start_sec: float = 0.0,
    end_sec: float | None = None,
    sr: int = TARGET_SR,
    bed_db: float = -26.0,
    add_ptt: bool = True,
    seed: int = 42,
    dur_sec: float | None = None,
) -> np.ndarray:
    """Layer -26 dBFS VHF cockpit radio static bed (360-2900Hz) + PTT squelch roger-clicks."""
    out = _ensure_stereo(audio_stereo).copy()
    tot_sec = len(out) / float(sr)
    if end_sec is None:
        end_sec = (start_sec + dur_sec) if dur_sec is not None else tot_sec

    s0 = max(0, int(round(start_sec * sr)))
    s1 = min(len(out), int(round(end_sec * sr)))
    if s1 <= s0 + 16:
        return out

    n = s1 - s0
    rng = np.random.default_rng(seed)
    tt = np.arange(n, dtype=np.float64) / float(sr)

    static_l = _bandpass(rng.standard_normal(n).astype(np.float32), 360.0, 2900.0, sr=sr, order=3)
    static_r = _bandpass(rng.standard_normal(n).astype(np.float32), 360.0, 2900.0, sr=sr, order=3)
    # Faint cockpit 400Hz aviation inverter + 1450Hz carrier hum
    hum = (0.08 * np.sin(2.0 * math.pi * 400.0 * tt) + 0.05 * np.sin(2.0 * math.pi * 1200.0 * tt)).astype(np.float32)
    bed_l = static_l + hum
    bed_r = static_r + hum

    rms = float(np.sqrt(np.mean(0.5 * (bed_l ** 2 + bed_r ** 2)))) + 1e-8
    target_rms = 10.0 ** (float(bed_db) / 20.0)
    scale = target_rms / rms
    fade = _edge_fade(n, int(0.025 * sr), int(0.030 * sr))

    out[s0:s1, 0] += bed_l * scale * fade
    out[s0:s1, 1] += bed_r * scale * fade

    if add_ptt:
        ptt_in = _synth_ptt_click(sr, is_end=False, seed=seed + 1)
        ptt_out = _synth_ptt_click(sr, is_end=True, seed=seed + 2)
        place_stereo_sfx(out, ptt_in, start_sec=s0 / float(sr), pan=-0.12, gain=0.85, sr=sr)
        end_t = max(s0 / float(sr), (s1 / float(sr)) - (len(ptt_out) / float(sr)))
        place_stereo_sfx(out, ptt_out, start_sec=end_t, pan=0.12, gain=0.85, sr=sr)

    return out


def apply_vhf_radio_texture(
    audio_stereo: np.ndarray,
    start_sec: float = 0.0,
    end_sec: float | None = None,
    sr: int = TARGET_SR,
    bed_db: float = -26.0,
    add_ptt: bool = True,
    drive: float = 2.2,
    seed: int = 42,
    dur_sec: float | None = None,
) -> np.ndarray:
    """Apply 360-2900 Hz VHF radio bandpass, mid-presence EQ, subtle crush/saturation & static bed."""
    out = _ensure_stereo(audio_stereo).copy()
    tot_sec = len(out) / float(sr)
    if end_sec is None:
        end_sec = (start_sec + dur_sec) if dur_sec is not None else tot_sec

    s0 = max(0, int(round(start_sec * sr)))
    s1 = min(len(out), int(round(end_sec * sr)))
    if s1 <= s0 + 32:
        return out

    seg = out[s0:s1].copy()
    in_rms = float(np.sqrt(np.mean(seg ** 2))) + 1e-8

    proc = np.empty_like(seg)
    for ch in range(2):
        # 360-2900 Hz VHF radio bandpass + +4.5dB @ 1450 Hz nasal radio clarity
        bp = _bandpass(seg[:, ch], 360.0, 2900.0, sr=sr, order=4)
        eq = _peaking_eq_filter(bp, freq_hz=1450.0, q=1.2, gain_db=4.5, sr=sr)
        # Soft VHF compression/saturation + subtle 11-bit quantization texture
        norm_eq = eq / (float(np.max(np.abs(eq))) + 1e-6)
        sat = np.tanh(norm_eq * float(drive)) / math.tanh(float(drive))
        crushed = np.round(sat * 1024.0) / 1024.0
        proc[:, ch] = 0.78 * sat + 0.22 * crushed

    proc_rms = float(np.sqrt(np.mean(proc ** 2))) + 1e-8
    proc *= (in_rms * 0.96) / proc_rms

    # Smooth 15ms crossfade into surrounding clean audio
    xf = min(len(seg) // 4, int(0.015 * sr))
    if xf > 1:
        w = np.ones(len(seg), dtype=np.float32)
        w[:xf] = np.linspace(0.0, 1.0, xf, dtype=np.float32)
        w[-xf:] = np.linspace(1.0, 0.0, xf, dtype=np.float32)
        out[s0:s1] = seg * (1.0 - w[:, None]) + proc * w[:, None]
    else:
        out[s0:s1] = proc

    return add_vhf_cockpit_bed(
        out,
        start_sec=s0 / float(sr),
        end_sec=s1 / float(sr),
        sr=sr,
        bed_db=bed_db,
        add_ptt=add_ptt,
        seed=seed,
    )


# ---------------------------------------------------------------------------
# 4-Act Evolving Suspense BGM + Asymmetric Sidechain Ducking + Dropouts
# ---------------------------------------------------------------------------

def _classify_beat_act(beat: dict[str, Any], idx: int, total_beats: int) -> int:
    """Map beat metadata to Act 1..4 (or 5 for final verdict)."""
    if "act" in beat:
        try:
            a = int(beat["act"])
            if 1 <= a <= 5:
                return a
        except (TypeError, ValueError):
            pass

    ch = str(beat.get("chapter_id", "")).upper()
    if ch.startswith("CH") and ch[2:].isdigit():
        cnum = int(ch[2:])
        if cnum <= 2:
            return 1
        if cnum <= 5:
            return 2
        if cnum <= 8:
            return 3
        return 4

    sc = str(beat.get("scene_id", "")).upper()
    if sc.startswith("SC") and sc[2:].isdigit():
        snum = int(sc[2:])
        if snum <= 1:
            return 1
        if snum <= 3:
            return 2
        if snum <= 5:
            return 3
        return 4

    if "style_idx" in beat:
        try:
            return min(4, max(1, int(beat["style_idx"]) + 1))
        except (TypeError, ValueError):
            pass

    bid = str(beat.get("beat_id", "")).upper()
    if bid.startswith("S1_"):
        return 1
    if bid.startswith("S2_"):
        return 2
    if bid.startswith("S3_"):
        return 3
    if bid.startswith("S4_"):
        return 4

    frac = idx / max(1, total_beats)
    if frac < 0.22:
        return 1
    if frac < 0.50:
        return 2
    if frac < 0.78:
        return 3
    return 4


def _resolve_act_boundaries(beats: list[dict[str, Any]] | None, total_dur: float) -> tuple[float, float, float, float, float]:
    """Return (t1_end, t2_end, t3_end, t_flameout_start, t_verdict_start)."""
    if not beats:
        return (
            total_dur * 0.22,
            total_dur * 0.50,
            total_dur * 0.78,
            total_dur * 0.895,
            total_dur * 0.920,
        )

    acts = [_classify_beat_act(b, i, len(beats)) for i, b in enumerate(beats)]
    t1_end = total_dur * 0.22
    t2_end = total_dur * 0.50
    t3_end = total_dur * 0.78

    for b, a in zip(beats, acts, strict=True):
        if a >= 2:
            t1_end = float(b.get("start_sec", t1_end))
            break
    for b, a in zip(beats, acts, strict=True):
        if a >= 3:
            t2_end = float(b.get("start_sec", t2_end))
            break
    for b, a in zip(beats, acts, strict=True):
        if a >= 4:
            t3_end = float(b.get("start_sec", t3_end))
            break

    # Ensure strictly monotonic non-degenerate act durations
    t1_end = float(np.clip(t1_end, total_dur * 0.08, total_dur * 0.45))
    t2_end = float(np.clip(t2_end, t1_end + total_dur * 0.08, total_dur * 0.68))
    t3_end = float(np.clip(t3_end, t2_end + total_dur * 0.08, total_dur * 0.88))

    # Locate flameout / verdict transition inside Act 4
    t_flame = t3_end + (total_dur - t3_end) * 0.45
    t_verd = t3_end + (total_dur - t3_end) * 0.56
    for b in beats:
        bid = str(b.get("beat_id", "")).upper()
        sid = str(b.get("sent_id", "")).upper()
        txt = f"{b.get('sub_text', '')} {b.get('display_text', '')}".lower()
        t_b = float(b.get("start_sec", 0.0))
        if t_b >= t3_end - 0.5 and (
            bid in ("S4_B01", "B15") or sid == "S114" or "cạn sạch" in txt or "hai động cơ" in txt or "tắt" in txt
        ):
            t_flame = t_b
            t_verd = float(b.get("end_sec", t_b + 1.2))
            break
    for b in beats:
        bid = str(b.get("beat_id", "")).upper()
        sid = str(b.get("sent_id", "")).upper()
        if bid in ("S4_B03", "B16") or sid in ("S117", "S118"):
            t_verd = max(t_flame + 0.35, float(b.get("start_sec", t_verd)))
            break

    t_flame = float(np.clip(t_flame, t3_end + 0.1, max(t3_end + 0.2, total_dur - 0.5)))
    t_verd = float(np.clip(t_verd, t_flame + 0.25, max(t_flame + 0.30, total_dur - 0.25)))
    return t1_end, t2_end, t3_end, t_flame, t_verd


def _resolve_dropout_windows(
    beats: list[dict[str, Any]] | None,
    drop_windows: list[Any] | None,
    total_dur: float,
    dropout_scale: float,
    t_flame: float,
    t_verd: float,
) -> list[tuple[float, float]]:
    windows: list[tuple[float, float]] = []

    if drop_windows:
        for item in drop_windows:
            if isinstance(item, (tuple, list)) and len(item) >= 2:
                w0, w1 = float(item[0]), float(item[1])
            elif isinstance(item, dict):
                w0 = float(item.get("start_sec", 0.0))
                w1 = float(item.get("end_sec", w0 + float(item.get("duration", 1.2))))
            else:
                continue
            if w1 > w0:
                windows.append((max(0.0, w0), min(total_dur, w1)))

    if beats:
        default_len = (1.35 if total_dur > 120.0 else 0.45) * dropout_scale
        for idx, b in enumerate(beats):
            if "drop_windows" in b and isinstance(b["drop_windows"], list):
                for item in b["drop_windows"]:
                    if isinstance(item, (tuple, list)) and len(item) >= 2:
                        windows.append((max(0.0, float(item[0])), min(total_dur, float(item[1]))))

            bgm_drop = b.get("bgm_drop")
            bid = str(b.get("beat_id", "")).upper()
            sid = str(b.get("sent_id", "")).upper()
            is_auto_reveal = (bid in _HELIOS_DROP_IDS or sid in _HELIOS_DROP_IDS) and idx > 0
            if not bgm_drop and not is_auto_reveal:
                continue

            t0 = float(b.get("start_sec", 0.0))
            t1 = float(b.get("end_sec", t0 + float(b.get("duration", 1.0))))
            if isinstance(bgm_drop, dict):
                if "start_sec" in bgm_drop and "end_sec" in bgm_drop:
                    windows.append((max(0.0, float(bgm_drop["start_sec"])), min(total_dur, float(bgm_drop["end_sec"]))))
                    continue
                dlen = float(bgm_drop.get("duration", default_len)) * dropout_scale
                mode = str(bgm_drop.get("mode", "before")).lower()
            elif isinstance(bgm_drop, (int, float)) and not isinstance(bgm_drop, bool):
                dlen = float(bgm_drop) * dropout_scale
                mode = str(b.get("bgm_drop_mode", "before")).lower()
            else:
                # For explicit beat["bgm_drop"]=True or auto reveal
                prev_end = float(beats[idx - 1].get("end_sec", t0)) if idx > 0 else 0.0
                gap_before = max(0.0, t0 - prev_end)
                if sid == "S114" or bid in ("S4_B01", "B15"):
                    dlen = min(max(0.45, t1 - t0), 1.45 * dropout_scale)
                    mode = "during" if total_dur > 120.0 else "before"
                else:
                    dlen = max(gap_before, default_len * (1.0 if bgm_drop else 0.72))
                    mode = str(b.get("bgm_drop_mode", "before")).lower()

            if dlen <= 0.02:
                continue
            if mode == "during" or t0 < 0.15:
                windows.append((max(0.0, t0), min(total_dur, t0 + dlen)))
            else:
                windows.append((max(0.0, t0 - dlen), min(total_dur, t0 + 0.04)))

    # Always ensure an Engine-Flameout dead-air dropout in Act 4
    flame_dur = min(max(0.35, t_verd - t_flame), (1.40 if total_dur > 120.0 else 0.48) * dropout_scale)
    if flame_dur > 0.15:
        windows.append((max(0.0, t_flame), min(total_dur, t_flame + flame_dur)))

    return windows


def _compute_voice_sidechain_gain(
    voice_stereo: np.ndarray | None,
    n_samples: int,
    sr: int,
    duck_db: float,
) -> np.ndarray:
    """Compute smooth voice-driven RMS sidechain ducking gain (25ms atk / 280ms rel)."""
    if voice_stereo is None or n_samples == 0:
        return np.ones(n_samples, dtype=np.float32)

    voice = _ensure_stereo(voice_stereo, n_samples=n_samples)
    v_mono = np.sqrt(0.5 * (voice[:, 0] ** 2 + voice[:, 1] ** 2))
    if float(np.max(v_mono)) < 1e-5:
        return np.ones(n_samples, dtype=np.float32)

    # 10ms RMS smoothed signal decimated to 500 Hz control rate (2ms steps); float64 + max(0) avoids float32 running-sum negative NaN
    win_rms = max(1, int(round(0.010 * sr)))
    v_sq = (v_mono.astype(np.float64)) ** 2
    rms_full = np.sqrt(np.maximum(0.0, uniform_filter1d(v_sq, size=win_rms)))
    ctrl_sr = 500
    step = max(1, sr // ctrl_sr)
    rms_ctrl = np.nan_to_num(rms_full[::step], nan=0.0, posinf=1.0, neginf=0.0)

    # Adaptive active-speech threshold calibrated for -12 LUFS speech and quieter test tones
    active_vals = rms_ctrl[rms_ctrl > 0.004]
    ref_speech = float(np.percentile(active_vals, 75)) if len(active_vals) else 0.08
    thresh_lo = max(0.005, min(0.018, ref_speech * 0.16))
    thresh_hi = max(thresh_lo + 0.02, min(0.090, ref_speech * 0.72))
    target = np.clip((rms_ctrl - thresh_lo) / (thresh_hi - thresh_lo), 0.0, 1.0)

    # Asymmetric follower: 25ms attack, 280ms release
    dt = step / float(sr)
    a_atk = 1.0 - math.exp(-dt / 0.025)
    a_rel = 1.0 - math.exp(-dt / 0.280)
    env_ctrl = np.empty_like(target)
    cur = float(target[0])
    env_ctrl[0] = cur
    target_list = target.tolist()
    out_list = [cur]
    for val in target_list[1:]:
        if val > cur:
            cur += a_atk * (val - cur)
        else:
            cur += a_rel * (val - cur)
        out_list.append(cur)
    env_ctrl = np.asarray(out_list, dtype=np.float32)

    x_ctrl = np.arange(len(env_ctrl), dtype=np.float64) * step
    x_full = np.arange(n_samples, dtype=np.float64)
    duck_env = np.interp(x_full, x_ctrl, env_ctrl).astype(np.float32)

    duck_lin = 10.0 ** (float(duck_db) / 20.0)
    return (1.0 - (1.0 - duck_lin) * np.clip(duck_env, 0.0, 1.0)).astype(np.float32)


def _synth_act1_aerial_mystery(n: int, sr: int, rng: np.random.Generator, profile: dict[str, Any]) -> np.ndarray:
    """Act 1: Cold Aerial Mystery (<900Hz pulse, D2/Eb2 sub-drone & cold spatial harmonics)."""
    out = np.zeros((n, 2), dtype=np.float32)
    cello_w = float(profile["cello_emphasis"])
    pulse_w = float(profile["pulse_emphasis"])
    chunk = sr * 20
    for s0 in range(0, n, chunk):
        s1 = min(n, s0 + chunk)
        t = (np.arange(s0, s1, dtype=np.float64)) / float(sr)
        sub = (
            0.46 * cello_w * np.sin(2.0 * math.pi * 36.71 * t)
            + 0.42 * np.sin(2.0 * math.pi * 73.42 * t)
            + 0.14 * np.sin(2.0 * math.pi * 77.78 * t + 0.5)
        )
        pad_l = sub + 0.24 * np.sin(2.0 * math.pi * 110.00 * t + 0.3) + 0.16 * np.sin(2.0 * math.pi * 220.0 * t)
        pad_r = sub + 0.24 * np.sin(2.0 * math.pi * 110.35 * t + 1.0) + 0.16 * np.sin(2.0 * math.pi * 220.6 * t + 0.6)
        # Cold <900 Hz radar-like harmonic pulse
        pulse = 0.72 + 0.28 * pulse_w * (0.5 + 0.5 * np.sin(2.0 * math.pi * 0.65 * t))
        overtone = 0.12 * pulse_w * np.sin(2.0 * math.pi * 587.33 * t) * (np.sin(2.0 * math.pi * 0.325 * t) ** 4)
        out[s0:s1, 0] = (pad_l * pulse + overtone * 0.88).astype(np.float32)
        out[s0:s1, 1] = (pad_r * pulse + overtone * 1.12).astype(np.float32)

    air_l = _bandpass(rng.standard_normal(n).astype(np.float32), 180.0, 820.0, sr=sr, order=2) * 0.16
    air_r = _bandpass(rng.standard_normal(n).astype(np.float32), 180.0, 820.0, sr=sr, order=2) * 0.16
    out[:, 0] = _lowpass(out[:, 0] + air_l, 880.0, sr=sr, order=4)
    out[:, 1] = _lowpass(out[:, 1] + air_r, 880.0, sr=sr, order=4)
    return out


def _synth_act2_hangar_clockwork(n: int, sr: int, rng: np.random.Generator, profile: dict[str, Any]) -> np.ndarray:
    """Act 2: Mechanical Hangar Clockwork Tension (120 BPM ticks + dissonant minor-2nd swell)."""
    out = np.zeros((n, 2), dtype=np.float32)
    pulse_w = float(profile["pulse_emphasis"])
    cello_w = float(profile["cello_emphasis"])
    tot_dur = max(1e-3, n / float(sr))

    chunk = sr * 20
    for s0 in range(0, n, chunk):
        s1 = min(n, s0 + chunk)
        t = np.arange(s0, s1, dtype=np.float64) / float(sr)
        swell = 0.75 + 0.35 * (t / tot_dur)
        sub = 0.44 * cello_w * np.sin(2.0 * math.pi * 73.42 * t)
        l_ch = sub + 0.28 * np.sin(2.0 * math.pi * 110.0 * t) + 0.18 * np.sin(2.0 * math.pi * 155.56 * t + 0.2) + 0.12 * np.sin(2.0 * math.pi * 311.13 * t)
        r_ch = sub + 0.28 * np.sin(2.0 * math.pi * 110.3 * t + 0.8) + 0.18 * np.sin(2.0 * math.pi * 155.95 * t + 1.1) + 0.12 * np.sin(2.0 * math.pi * 311.85 * t)
        out[s0:s1, 0] = (l_ch * swell * 0.72).astype(np.float32)
        out[s0:s1, 1] = (r_ch * swell * 0.72).astype(np.float32)

    # 120 BPM mechanical clockwork ticks (or 60 BPM sparser in variant B, 240 BPM accents in variant C)
    bpm = 60.0 if pulse_w < 0.6 else 120.0
    step_sec = 60.0 / bpm
    tick_dur = 0.024
    m_tk = int(tick_dur * sr)
    t_tk = np.arange(m_tk, dtype=np.float64) / float(sr)
    tick_base = (np.sin(2.0 * math.pi * 1950.0 * t_tk) + 0.55 * np.sin(2.0 * math.pi * 3120.0 * t_tk)) * np.exp(-t_tk * 190.0)
    tick_noise = _bandpass(rng.standard_normal(m_tk).astype(np.float32), 1400.0, 4200.0, sr=sr, order=2) * np.exp(-t_tk.astype(np.float32) * 220.0)
    tick_wav = (tick_base.astype(np.float32) * 0.18 + tick_noise * 0.12) * pulse_w

    idx_t = 0
    t_cur = 0.06
    while t_cur + tick_dur < tot_dur:
        s0 = int(round(t_cur * sr))
        m = min(m_tk, n - s0)
        accent = 1.15 if (idx_t % 4 == 0) else 0.78
        pan = -0.18 if (idx_t % 2 == 0) else 0.18
        gl = 1.0 - max(0.0, pan)
        gr = 1.0 - max(0.0, -pan)
        out[s0 : s0 + m, 0] += tick_wav[:m] * accent * gl
        out[s0 : s0 + m, 1] += tick_wav[:m] * accent * gr
        idx_t += 1
        t_cur += step_sec

    out[:, 0] = _lowpass(out[:, 0], 4500.0, sr=sr, order=2)
    out[:, 1] = _lowpass(out[:, 1], 4500.0, sr=sr, order=2)
    return out


def _synth_act3_hypoxia_sweep(n: int, sr: int, rng: np.random.Generator, profile: dict[str, Any]) -> np.ndarray:
    """Act 3: Hypoxia Low-Pass Sweep (2500 -> 450 Hz) + 52 BPM Heartbeat + frozen shimmer."""
    cello_w = float(profile["cello_emphasis"])
    raw_pad = np.zeros((n, 2), dtype=np.float32)

    chunk = sr * 20
    for s0 in range(0, n, chunk):
        s1 = min(n, s0 + chunk)
        t = np.arange(s0, s1, dtype=np.float64) / float(sr)
        # Wide harmonic bed spanning 73 Hz .. 2200 Hz so the 2500->450Hz LPF sweep is vividly audible
        base_l = (
            0.38 * cello_w * np.sin(2.0 * math.pi * 73.42 * t)
            + 0.28 * np.sin(2.0 * math.pi * 146.83 * t)
            + 0.22 * np.sin(2.0 * math.pi * 220.00 * t + 0.3)
            + 0.18 * np.sin(2.0 * math.pi * 440.00 * t + 0.7)
            + 0.16 * np.sin(2.0 * math.pi * 698.46 * t)
            + 0.14 * np.sin(2.0 * math.pi * 1046.50 * t)
            + 0.12 * np.sin(2.0 * math.pi * 1567.98 * t)
        )
        base_r = (
            0.38 * cello_w * np.sin(2.0 * math.pi * 73.42 * t)
            + 0.28 * np.sin(2.0 * math.pi * 147.20 * t + 0.4)
            + 0.22 * np.sin(2.0 * math.pi * 220.55 * t + 0.9)
            + 0.18 * np.sin(2.0 * math.pi * 441.10 * t + 0.2)
            + 0.16 * np.sin(2.0 * math.pi * 700.20 * t + 0.5)
            + 0.14 * np.sin(2.0 * math.pi * 1049.10 * t + 1.1)
            + 0.12 * np.sin(2.0 * math.pi * 1571.50 * t + 0.8)
        )
        raw_pad[s0:s1, 0] = base_l.astype(np.float32)
        raw_pad[s0:s1, 1] = base_r.astype(np.float32)

    shimmer_l = _bandpass(rng.standard_normal(n).astype(np.float32), 550.0, 2500.0, sr=sr, order=2) * 0.22
    shimmer_r = _bandpass(rng.standard_normal(n).astype(np.float32), 550.0, 2500.0, sr=sr, order=2) * 0.22
    raw_pad[:, 0] += shimmer_l
    raw_pad[:, 1] += shimmer_r

    # Zero-phase multi-band lowpass sweep 2500 Hz -> 1250 Hz -> 750 Hz -> 450 Hz
    u = np.linspace(0.0, 1.0, n, dtype=np.float32)
    swept = np.empty_like(raw_pad)
    cutoffs = (2500.0, 1250.0, 750.0, 450.0)
    for ch in range(2):
        bands = [_lowpass(raw_pad[:, ch], fc, sr=sr, order=4, zero_phase=True) for fc in cutoffs]
        pos = u * (len(cutoffs) - 1)
        idx0 = np.clip(np.floor(pos).astype(np.int32), 0, len(cutoffs) - 2)
        frac = (pos - idx0).astype(np.float32)
        acc = np.zeros(n, dtype=np.float32)
        for bi in range(len(cutoffs) - 1):
            mask = idx0 == bi
            if np.any(mask):
                acc[mask] = bands[bi][mask] * (1.0 - frac[mask]) + bands[bi + 1][mask] * frac[mask]
        swept[:, ch] = acc * 0.72

    # Overlay 52 BPM muted hypoxic heartbeat (period = 60/52 = 1.1538s) centered on sub
    hb_period = 60.0 / 52.0
    m1 = int(0.18 * sr)
    t1 = np.arange(m1, dtype=np.float64) / float(sr)
    f1 = 33.0 + (66.0 - 33.0) * np.exp(-t1 * 18.0)
    lub = (np.tanh(np.sin(2.0 * math.pi * np.cumsum(f1) / float(sr)) * 1.45) * (1.0 - np.exp(-t1 * 180.0)) * np.exp(-t1 * 16.0) * 0.56).astype(np.float32)

    m2 = int(0.22 * sr)
    t2 = np.arange(m2, dtype=np.float64) / float(sr)
    f2 = 30.0 + (54.0 - 30.0) * np.exp(-t2 * 16.0)
    dub = (np.tanh(np.sin(2.0 * math.pi * np.cumsum(f2) / float(sr)) * 1.40) * (1.0 - np.exp(-t2 * 160.0)) * np.exp(-t2 * 14.0) * 0.40).astype(np.float32)

    tot_dur = n / float(sr)
    t_hb = 0.08
    while t_hb + 0.40 < tot_dur:
        s_a = int(round(t_hb * sr))
        na = min(m1, n - s_a)
        if na > 0:
            swept[s_a : s_a + na, 0] += lub[:na]
            swept[s_a : s_a + na, 1] += lub[:na]
        s_b = int(round((t_hb + 0.25) * sr))
        nb = min(m2, n - s_b)
        if nb > 0:
            swept[s_b : s_b + nb, 0] += dub[:nb]
            swept[s_b : s_b + nb, 1] += dub[:nb]
        t_hb += hb_period

    return swept


def _synth_act4_rescue_and_verdict(
    n: int,
    sr: int,
    rng: np.random.Generator,
    profile: dict[str, Any],
    s_verdict: int,
) -> np.ndarray:
    """Act 4: Urgent Heroic Rescue Ostinato (before s_verdict) + Solemn Forensic Verdict (after)."""
    out = np.zeros((n, 2), dtype=np.float32)
    pulse_w = float(profile["pulse_emphasis"])
    cello_w = float(profile["cello_emphasis"])

    # 4a: Heroic Rescue Ostinato [0 : s_verdict]
    n_osc = max(0, min(n, s_verdict))
    if n_osc > 0:
        notes = (146.83, 146.83, 220.00, 174.61, 146.83, 130.81, 164.81, 220.00)
        step_sec = 0.22 if pulse_w > 1.1 else 0.25
        m_step = int(step_sec * sr)
        t_step = np.arange(m_step, dtype=np.float64) / float(sr)
        env_note = (1.0 - np.exp(-t_step * 90.0)) * np.exp(-t_step * 6.5)

        t_cur = 0.0
        idx_n = 0
        tot_osc = n_osc / float(sr)
        while t_cur + 0.05 < tot_osc:
            s0 = int(round(t_cur * sr))
            m = min(m_step, n_osc - s0)
            fn = notes[idx_n % len(notes)]
            note = (0.65 * np.sin(2.0 * math.pi * fn * t_step[:m]) + 0.25 * np.sin(2.0 * math.pi * (fn * 2.0) * t_step[:m])) * env_note[:m]
            pan = 0.14 * math.sin(idx_n * 0.9)
            out[s0 : s0 + m, 0] += (note * 0.34 * pulse_w * (1.0 - pan)).astype(np.float32)
            out[s0 : s0 + m, 1] += (note * 0.34 * pulse_w * (1.0 + pan)).astype(np.float32)
            idx_n += 1
            t_cur += step_sec

        # Driving rescue bass bed
        t_b = np.arange(n_osc, dtype=np.float64) / float(sr)
        bass = (0.45 * np.sin(2.0 * math.pi * 73.42 * t_b) + 0.25 * np.sin(2.0 * math.pi * 110.0 * t_b)).astype(np.float32)
        p_bass = (0.72 + 0.28 * np.sin(2.0 * math.pi * 2.0 * t_b)).astype(np.float32)
        out[:n_osc, 0] += bass * p_bass * 0.65
        out[:n_osc, 1] += bass * p_bass * 0.65

    # 4b: Solemn Forensic Verdict [s_verdict : n]
    n_v = max(0, n - n_osc)
    if n_v > 0:
        t_v = np.arange(n_v, dtype=np.float64) / float(sr)
        u_v = t_v / max(1e-3, n_v / float(sr))
        # D minor -> D suspended solemn string resolution
        vib = 1.0 + 0.0025 * np.sin(2.0 * math.pi * 4.5 * t_v)
        f_3rd = 174.61 * (1.0 - 0.5 * u_v) + 164.81 * (0.5 * u_v)
        cello_l = (
            0.46 * cello_w * np.sin(2.0 * math.pi * 73.42 * t_v)
            + 0.30 * np.sin(2.0 * math.pi * 110.00 * vib * t_v)
            + 0.22 * np.sin(2.0 * math.pi * 146.83 * vib * t_v)
            + 0.16 * np.sin(2.0 * math.pi * f_3rd * vib * t_v)
        )
        cello_r = (
            0.46 * cello_w * np.sin(2.0 * math.pi * 73.42 * t_v + 0.15)
            + 0.30 * np.sin(2.0 * math.pi * 110.22 * vib * t_v + 0.6)
            + 0.22 * np.sin(2.0 * math.pi * 147.12 * vib * t_v + 0.9)
            + 0.16 * np.sin(2.0 * math.pi * (f_3rd * 1.002) * vib * t_v + 0.4)
        )
        verd_l = _lowpass(cello_l.astype(np.float32), 950.0, sr=sr, order=3) * 0.72
        verd_r = _lowpass(cello_r.astype(np.float32), 950.0, sr=sr, order=3) * 0.72
        out[n_osc:, 0] += verd_l
        out[n_osc:, 1] += verd_r

    out[:, 0] = _lowpass(out[:, 0], 3200.0, sr=sr, order=3)
    out[:, 1] = _lowpass(out[:, 1], 3200.0, sr=sr, order=3)
    return out


def compose_4act_tension_bgm(
    n_samples: int,
    voice_stereo: np.ndarray | None,
    beats: list[dict[str, Any]] | None,
    variant: str = "A",
    sr: int = TARGET_SR,
    seed: int = 42,
    drop_windows: list[tuple[float, float]] | None = None,
) -> np.ndarray:
    """Synthesize 4-Act evolving tension BGM with voice sidechain ducking and dead-air dropouts."""
    if n_samples <= 0:
        return np.zeros((0, 2), dtype=np.float32)

    _, profile = _resolve_variant(variant)
    rng = np.random.default_rng(seed)
    total_dur = n_samples / float(sr)

    t1_end, t2_end, t3_end, t_flame, t_verd = _resolve_act_boundaries(beats, total_dur)
    s1 = int(round(t1_end * sr))
    s2 = int(round(t2_end * sr))
    s3 = int(round(t3_end * sr))
    s_verd = int(round(t_verd * sr))

    # Crossfade margin between acts (up to 0.75s)
    xf = min(int(0.75 * sr), max(16, n_samples // 24))
    bgm = np.zeros((n_samples, 2), dtype=np.float32)

    def _add_act_slice(a0: int, a1: int, synth_fn: Any, gain_scale: float) -> None:
        p0 = max(0, a0 - xf)
        p1 = min(n_samples, a1 + xf)
        if p1 <= p0:
            return
        stem = synth_fn(p1 - p0) * float(gain_scale)
        env = np.ones(p1 - p0, dtype=np.float32)
        if a0 > p0:
            k = min(len(env), a0 - p0 + (xf if a0 > 0 else 0))
            env[:k] = np.sin(np.linspace(0.0, math.pi * 0.5, k, dtype=np.float32)) ** 2
        if p1 > a1:
            k = min(len(env), p1 - a1 + (xf if a1 < n_samples else 0))
            env[-k:] = np.cos(np.linspace(0.0, math.pi * 0.5, k, dtype=np.float32)) ** 2
        bgm[p0:p1] += stem * env[:, None]

    g1, g2, g3, g4, _g5 = profile["act_gains"]
    _add_act_slice(0, s1, lambda m: _synth_act1_aerial_mystery(m, sr, rng, profile), g1)
    _add_act_slice(s1, s2, lambda m: _synth_act2_hangar_clockwork(m, sr, rng, profile), g2)
    _add_act_slice(s2, s3, lambda m: _synth_act3_hypoxia_sweep(m, sr, rng, profile), g3)
    _add_act_slice(
        s3,
        n_samples,
        lambda m: _synth_act4_rescue_and_verdict(m, sr, rng, profile, max(0, s_verd - max(0, s3 - xf))),
        g4,
    )

    # Normalize baseline RMS cleanly so idle BGM sits right at calibrated level before ducking
    rms = float(np.sqrt(np.mean(bgm ** 2))) + 1e-8
    bgm *= float(profile["bgm_idle_gain"]) / max(rms, 0.08)

    # Smooth macro fade-in / fade-out
    fade_io = min(n_samples // 6, int(0.45 * sr))
    if fade_io > 1:
        bgm[:fade_io] *= np.linspace(0.0, 1.0, fade_io, dtype=np.float32)[:, None]
        bgm[-fade_io:] *= np.linspace(1.0, 0.0, fade_io, dtype=np.float32)[:, None]

    # Voice-driven RMS sidechain ducking (25ms attack, 280ms release, -4.5 to -7.0 dB)
    duck_gain = _compute_voice_sidechain_gain(voice_stereo, n_samples, sr, duck_db=float(profile["bgm_duck_db"]))
    bgm *= duck_gain[:, None]

    # Mandatory dead-air dropout windows before shocking reveals / flameout
    windows = _resolve_dropout_windows(beats, drop_windows, total_dur, float(profile["dropout_scale"]), t_flame, t_verd)
    if windows:
        drop_env = np.ones(n_samples, dtype=np.float32)
        fade_d = max(1, int(0.045 * sr))
        for w0, w1 in windows:
            i0 = max(0, int(round(w0 * sr)))
            i1 = min(n_samples, int(round(w1 * sr)))
            if i1 <= i0 + 8:
                continue
            local = np.zeros(i1 - i0, dtype=np.float32)
            fo = min(fade_d, (i1 - i0) // 3)
            fi = min(fade_d, (i1 - i0) // 3)
            if fo > 1:
                local[:fo] = np.linspace(1.0, 0.0, fo, dtype=np.float32)
            if fi > 1:
                local[-fi:] = np.linspace(0.0, 1.0, fi, dtype=np.float32)
            drop_env[i0:i1] = np.minimum(drop_env[i0:i1], local)
        bgm *= drop_env[:, None]

    return bgm.astype(np.float32)


# ---------------------------------------------------------------------------
# Beat-Synced SFX Layer & VHF Integration
# ---------------------------------------------------------------------------

def _synth_sub_boom(dur: float = 0.80, f_start: float = 92.0, f_end: float = 34.0, amp: float = 0.22, sr: int = TARGET_SR) -> np.ndarray:
    n = max(1, int(round(dur * sr)))
    tt = np.arange(n, dtype=np.float64) / float(sr)
    freq = f_end + (f_start - f_end) * np.exp(-tt * 7.5)
    ph = 2.0 * math.pi * np.cumsum(freq) / float(sr)
    env = (1.0 - np.exp(-tt * 140.0)) * np.exp(-tt * 4.2)
    mono = (np.tanh(np.sin(ph) * 1.45) * env * amp).astype(np.float32) * _edge_fade(n, 0, int(0.02 * sr))
    return np.column_stack([mono, mono]).astype(np.float32)


def _synth_tick(freq: float = 2400.0, dur: float = 0.018, amp: float = 0.08, sr: int = TARGET_SR, seed: int = 3) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = max(1, int(round(dur * sr)))
    tt = np.arange(n, dtype=np.float64) / float(sr)
    w = (np.sin(2.0 * math.pi * freq * tt) + 0.35 * rng.standard_normal(n)) * np.exp(-tt * 260.0) * amp
    return np.column_stack([w, w]).astype(np.float32)


def _synth_whoosh(dur: float = 0.35, amp: float = 0.09, sr: int = TARGET_SR, seed: int = 7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = max(1, int(round(dur * sr)))
    tt = np.arange(n, dtype=np.float64) / float(sr)
    raw = rng.standard_normal(n).astype(np.float32)
    lo = _bandpass(raw, 180.0, 620.0, sr=sr, order=2)
    hi = _bandpass(raw, 620.0, 1800.0, sr=sr, order=2)
    env = (np.sin(math.pi * tt / max(1e-6, dur)) ** 1.6).astype(np.float32)
    mix = (lo * (1.0 - 0.5 * (tt / max(1e-6, dur)).astype(np.float32)) + hi * 0.4) * env * amp * 2.2
    return np.column_stack([mix, np.roll(mix, max(1, int(0.0012 * sr)))]).astype(np.float32)


def _synth_radar_ping(dur: float = 0.65, amp: float = 0.095, sr: int = TARGET_SR) -> np.ndarray:
    n = max(1, int(round(dur * sr)))
    tt = np.arange(n, dtype=np.float64) / float(sr)
    ping = (0.8 * np.sin(2.0 * math.pi * 1340.0 * tt) + 0.2 * np.sin(2.0 * math.pi * 2680.0 * tt))
    env = (1.0 - np.exp(-tt * 220.0)) * np.exp(-tt * 6.0)
    mono = (ping * env * amp).astype(np.float32)
    return np.column_stack([mono, np.roll(mono, max(1, int(0.001 * sr)))]).astype(np.float32)


def _compose_suspense_sfx_layer(
    beats: list[dict[str, Any]] | None,
    n_samples: int,
    variant: str,
    sr: int,
    seed: int,
) -> np.ndarray:
    sfx = np.zeros((n_samples, 2), dtype=np.float32)
    if not beats:
        return sfx

    _, profile = _resolve_variant(variant)
    g_sfx = float(profile["sfx_gain"])
    rng = np.random.default_rng(seed)

    def _trigger_cue(kind: str, t_at: float, dur_hint: float, pan: float, gain_mul: float, local_seed: int) -> None:
        k = kind.lower().strip()
        if k in ("boeing_horn", "boeing_737_warning_horn", "warning_horn", "horn"):
            stem = synth_boeing_737_warning_horn(dur_sec=min(max(0.55, dur_hint), 2.8), sr=sr, pulsed=True, gain=0.14 * g_sfx * gain_mul)
            place_stereo_sfx(sfx, stem, t_at, pan=pan or 0.10, sr=sr)
        elif k in ("master_caution", "master_caution_chime", "caution_chime", "chime"):
            stem = synth_master_caution_chime(dur_sec=min(max(0.45, dur_hint), 1.1), sr=sr, gain=0.13 * g_sfx * gain_mul)
            place_stereo_sfx(sfx, stem, t_at, pan=pan or -0.10, sr=sr)
        elif k in ("air_leak", "air_leak_turbulence", "air_hiss", "pressure_hiss"):
            stem = synth_air_leak_turbulence(dur_sec=min(max(0.60, dur_hint), 2.4), sr=sr, gain=0.11 * g_sfx * gain_mul, seed=local_seed)
            place_stereo_sfx(sfx, stem, t_at, pan=pan or 0.08, sr=sr)
        elif k in ("riser_subdrop", "riser_to_subdrop", "riser"):
            stem = synth_riser_to_subdrop(sr=sr, riser_gain=0.14 * g_sfx * gain_mul, drop_gain=0.22 * g_sfx * gain_mul, seed=local_seed)
            # Align so subdrop lands cleanly at t_at
            place_stereo_sfx(sfx, stem, t_at - 1.10, pan=pan, sr=sr)
        elif k in ("heartbeat", "lub_dub"):
            place_stereo_sfx(sfx, _synth_sub_boom(0.18, 64.0, 34.0, 0.22 * g_sfx * gain_mul, sr), t_at, pan=0.0, sr=sr)
            place_stereo_sfx(sfx, _synth_sub_boom(0.22, 54.0, 30.0, 0.16 * g_sfx * gain_mul, sr), t_at + 0.25, pan=0.0, sr=sr)
        elif k in ("chapter_stinger", "stinger", "chapter_bumper"):
            stem = synth_chapter_stinger(sr=sr, dur_sec=min(max(0.8, dur_hint), 1.6), gain=0.18 * g_sfx * gain_mul, seed=local_seed)
            place_stereo_sfx(sfx, stem, t_at, pan=pan, sr=sr)
        elif k in ("sub_boom", "boom", "impact"):
            stem = _synth_sub_boom(dur=min(max(0.35, dur_hint), 1.0), amp=0.22 * g_sfx * gain_mul, sr=sr)
            place_stereo_sfx(sfx, stem, t_at, pan=0.0, sr=sr)
        elif k in ("stamp_hit", "stamp"):
            place_stereo_sfx(sfx, _synth_sub_boom(0.55, 125.0, 33.0, 0.25 * g_sfx * gain_mul, sr), t_at, pan=0.0, sr=sr)
            snap = _bandpass(rng.standard_normal(int(0.08 * sr)).astype(np.float32), 900.0, 3200.0, sr=sr)
            snap *= np.exp(-np.arange(len(snap), dtype=np.float32) / float(sr) * 70.0) * (0.20 * g_sfx * gain_mul)
            place_stereo_sfx(sfx, snap, t_at, pan=pan or -0.08, sr=sr)
        elif k in ("radar_ping", "sonar_ping"):
            place_stereo_sfx(sfx, _synth_radar_ping(0.65, 0.095 * g_sfx * gain_mul, sr), t_at, pan=pan or 0.14, sr=sr)
        elif k in ("rotary_switch", "switch_click"):
            place_stereo_sfx(sfx, _synth_tick(1450.0, 0.028, 0.18 * g_sfx * gain_mul, sr, local_seed), t_at, pan=-0.16, sr=sr)
            place_stereo_sfx(sfx, _synth_tick(2100.0, 0.032, 0.22 * g_sfx * gain_mul, sr, local_seed + 1), t_at + 0.26, pan=-0.12, sr=sr)
        elif k in ("typewriter", "ticks"):
            for j in range(6):
                place_stereo_sfx(sfx, _synth_tick(2750.0 + j * 45.0, 0.016, 0.045 * g_sfx * gain_mul, sr, local_seed + j), t_at + j * 0.068, pan=0.18, sr=sr)
        elif k in ("jet_flyby", "flyby"):
            m = int(min(max(0.6, dur_hint), 1.55) * sr)
            tt = np.arange(m, dtype=np.float64) / float(sr)
            jet = _bandpass(rng.standard_normal(m).astype(np.float32), 220.0, 1150.0, sr=sr)
            whine = np.sin(2.0 * math.pi * np.cumsum(420.0 - 240.0 * (tt / max(0.4, tt[-1]))) / float(sr))
            env = np.exp(-((tt - 0.42) ** 2) / 0.11).astype(np.float32)
            core = (jet * 0.15 + whine.astype(np.float32) * 0.03) * env * g_sfx * gain_mul
            p_l = np.clip(1.15 - tt / max(0.4, tt[-1]), 0.30, 1.0).astype(np.float32)
            p_r = np.clip(0.30 + tt / max(0.4, tt[-1]), 0.30, 1.0).astype(np.float32)
            place_stereo_sfx(sfx, np.column_stack([core * p_l, core * p_r]), t_at, pan=0.0, sr=sr)
        elif k in ("whoosh", "laser_whoosh"):
            place_stereo_sfx(sfx, _synth_whoosh(min(0.45, max(0.20, dur_hint)), 0.09 * g_sfx * gain_mul, sr, local_seed), t_at, pan=pan, sr=sr)

    prev_group = None
    for idx, b in enumerate(beats):
        t0 = float(b.get("start_sec", 0.0))
        dur = max(0.15, float(b.get("duration", 1.5)))
        bid = str(b.get("beat_id", "")).upper()
        sid = str(b.get("sent_id", "")).upper()
        cur_group = b.get("chapter_id") or b.get("scene_id") or b.get("style_idx")

        # 1. Explicit cue list or single sfx key
        explicit_cues = b.get("sfx_cues")
        if isinstance(explicit_cues, list) and explicit_cues:
            for j, c in enumerate(explicit_cues):
                if isinstance(c, dict):
                    _trigger_cue(
                        str(c.get("type", c.get("sfx", "sub_boom"))),
                        t0 + float(c.get("offset_sec", 0.0)),
                        float(c.get("dur_sec", min(dur, 1.8))),
                        float(c.get("pan", 0.0)),
                        float(c.get("gain", 1.0)),
                        seed + idx * 31 + j,
                    )
            prev_group = cur_group
            continue

        single_sfx = b.get("sfx_type") or b.get("sfx")
        if isinstance(single_sfx, str) and single_sfx.strip():
            _trigger_cue(
                single_sfx,
                t0 + float(b.get("sfx_offset_sec", 0.0)),
                float(b.get("sfx_dur_sec", min(dur, 2.2))),
                float(b.get("sfx_pan", 0.14 if idx % 2 else -0.14)),
                float(b.get("sfx_gain", 1.0)),
                seed + idx * 17,
            )
            prev_group = cur_group
            continue

        # 2. Automatic chapter/style transitions: riser->subdrop or chapter stinger
        if idx > 0 and cur_group is not None and cur_group != prev_group:
            if b.get("chapter_bumper"):
                _trigger_cue("chapter_stinger", max(0.0, t0 - 1.25), 1.30, 0.0, 1.0, seed + idx * 19)
            else:
                _trigger_cue("riser_subdrop", t0, 1.52, 0.0, 1.0, seed + idx * 19)
        elif idx > 0:
            _trigger_cue("whoosh", max(0.0, t0 - 0.12), 0.28, 0.16 if idx % 2 else -0.16, 0.65, seed + idx * 7)

        # 3. Helios 522 semantic beat matching
        if bid in _HELIOS_HORN_IDS or sid in _HELIOS_HORN_IDS:
            _trigger_cue("boeing_horn", t0 + 0.10, min(2.4, max(0.55, dur - 0.18)), 0.12, 1.0, seed + idx * 13)
        if bid in _HELIOS_CAUTION_IDS or sid in _HELIOS_CAUTION_IDS:
            _trigger_cue("master_caution", t0 + 0.15, 0.85, -0.12, 1.0, seed + idx * 13)
        if bid in _HELIOS_AIR_LEAK_IDS or sid in _HELIOS_AIR_LEAK_IDS:
            _trigger_cue("air_leak", t0 + 0.08, min(1.9, dur), 0.10, 1.0, seed + idx * 13)

        if bid in ("S1_B01", "B00"):
            _trigger_cue("jet_flyby", t0 + 0.05, min(dur, 1.5), 0.0, 1.0, seed + 101)
            _trigger_cue("typewriter", t0 + 0.14, 0.6, 0.18, 0.9, seed + 102)
        elif bid in ("S1_B02", "B01"):
            _trigger_cue("typewriter", t0 + 0.12, 0.55, 0.16, 0.8, seed + 103)
        elif bid in ("S1_B03", "B02"):
            _trigger_cue("sub_boom", t0 + 0.20, 0.85, 0.0, 1.0, seed + 104)
        elif bid in ("S1_B04",):
            _trigger_cue("stamp_hit", t0 + 0.28, 0.55, -0.06, 1.05, seed + 105)
        elif bid in ("S2_B01", "B03"):
            _trigger_cue("rotary_switch", t0 + 0.22, 0.55, -0.14, 1.0, seed + 106)
        elif bid in ("S4_B01",):
            _trigger_cue("radar_ping", t0 + 0.22, 0.65, 0.15, 1.0, seed + 107)
        elif bid in ("S4_B02",):
            _trigger_cue("laser_whoosh", t0 + 0.05, 0.45, 0.18, 1.1, seed + 108)
        elif bid in ("S4_B03",):
            _trigger_cue("stamp_hit", t0 + 0.52, 0.55, 0.0, 1.0, seed + 109)
        elif bid in ("S4_B04", "B17"):
            _trigger_cue("sub_boom", t0 + 0.22, 0.92, 0.0, 1.05, seed + 110)

        prev_group = cur_group

    return sfx


# ---------------------------------------------------------------------------
# Linked-Stereo EBU R128 Mastering & Calibrated AAC 256k Encoder
# ---------------------------------------------------------------------------

def _polish_wav_stereo_lufs(
    wav_path: Path,
    target_lufs: float = -11.0,
    max_tp_db: float = -1.4,
    sr: int = TARGET_SR,
) -> dict[str, float]:
    ebur = measure_ebur128(wav_path)
    limit_lin = min(0.92, 10.0 ** (float(max_tp_db) / 20.0))
    for _ in range(4):
        lufs = float(ebur["integrated_lufs"])
        tp = float(ebur["true_peak_dbfs"])
        if -11.30 <= lufs <= -10.70 and tp <= max_tp_db:
            break
        delta = float(target_lufs) - lufs
        gain_db = max(-3.5, min(3.5, delta + (0.14 if delta > 0.1 else 0.0)))
        tmp = wav_path.with_suffix(".polish_v2.wav")
        af = (
            f"aresample=192000,volume={gain_db:+.3f}dB,"
            f"alimiter=limit={limit_lin:.4f}:level=false:attack=2:release=40,aresample={sr}"
        )
        subprocess.run(
            ["ffmpeg", "-hide_banner", "-y", "-i", str(wav_path), "-af", af, "-ar", str(sr), "-ac", "2", "-c:a", "pcm_s16le", str(tmp)],
            check=True,
            capture_output=True,
            text=True,
        )
        tmp.replace(wav_path)
        ebur = measure_ebur128(wav_path)
    return ebur


def master_2pass_wav_stereo(
    src_wav: Path | str,
    dst_wav: Path | str,
    target_lufs: float = -11.0,
    max_tp_db: float = -1.4,
    lra: float = 4.5,
    sr: int = TARGET_SR,
) -> dict[str, float]:
    """Run 2-pass linked-stereo EBU R128 loudnorm + true-peak ceiling polish on WAV."""
    src_p = Path(src_wav)
    dst_p = Path(dst_wav)
    dst_p.parent.mkdir(parents=True, exist_ok=True)

    p1 = subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-y", "-i", str(src_p),
            "-af", f"loudnorm=I={target_lufs:.1f}:TP={max_tp_db:.1f}:LRA={lra:.1f}:print_format=json",
            "-f", "null", "-",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    matches = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", p1.stderr, flags=re.DOTALL)
    if matches:
        stats = json.loads(matches[-1])
        use_linear = all(
            str(stats.get(k, "inf")).lower() not in ("inf", "-inf", "nan")
            for k in ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset")
        )
        if use_linear:
            af = (
                f"loudnorm=I={target_lufs:.1f}:TP={max_tp_db:.1f}:LRA={lra:.1f}:"
                f"measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:"
                f"measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:"
                f"offset={stats['target_offset']}:linear=true"
            )
        else:
            af = f"loudnorm=I={target_lufs:.1f}:TP={max_tp_db:.1f}:LRA={lra:.1f}"
    else:
        af = f"loudnorm=I={target_lufs:.1f}:TP={max_tp_db:.1f}:LRA={lra:.1f}"

    subprocess.run(
        ["ffmpeg", "-hide_banner", "-y", "-i", str(src_p), "-af", af, "-ar", str(sr), "-ac", "2", "-c:a", "pcm_s16le", str(dst_p)],
        check=True,
        capture_output=True,
        text=True,
    )
    return _polish_wav_stereo_lufs(dst_p, target_lufs=target_lufs, max_tp_db=max_tp_db, sr=sr)


def encode_calibrated_m4a_stereo(
    wav_path: Path | str,
    out_m4a: Path | str,
    target_lufs: float = -11.0,
    max_tp_db: float = -1.0,
    pre_aac_tp_db: float = -1.4,
    lra: float = 4.5,
    skip_remaster: bool = False,
) -> dict[str, float]:
    """Transcode 48kHz WAV to stereo AAC 256k preserving true (N, 2) stereo imaging.

    Pre-normalizes via 2-pass loudnorm (`I=-11.0:TP=-1.4:LRA=4.5`) unless
    `skip_remaster=True` (or the input WAV already satisfies `target_lufs ± 0.30`
    and `pre_aac_tp_db`), then runs an adaptive linked-stereo peak-limiter loop
    so the decoded `.m4a` verifies at `-11.0 ± 0.4 LUFS` and `true_peak_dbfs <= -1.0 dBTP`.
    """
    src_wav = Path(wav_path)
    dst_m4a = Path(out_m4a)
    dst_m4a.parent.mkdir(parents=True, exist_ok=True)

    win = 1536  # Covers AAC MDCT frame (~21.3ms) + priming margin
    kern = np.hanning(win * 2 + 1).astype(np.float32)
    kern /= float(kern.sum())
    thresholds = (0.85, 0.81, 0.77, 0.73, 0.69)
    stats: dict[str, float] = {"integrated_lufs": -99.0, "true_peak_dbfs": 0.0, "lra_lu": 0.0}

    with tempfile.TemporaryDirectory() as td:
        td_p = Path(td)
        effective_skip = bool(skip_remaster)
        if not effective_skip:
            try:
                pre_stats = measure_ebur128(src_wav)
                if (
                    (target_lufs - 0.30) <= float(pre_stats.get("integrated_lufs", -99.0)) <= (target_lufs + 0.30)
                    and float(pre_stats.get("true_peak_dbfs", 0.0)) <= float(pre_aac_tp_db)
                ):
                    effective_skip = True
            except Exception:
                effective_skip = False

        if effective_skip:
            # Input WAV is already mastered — preserve natural LRA and encode AAC 256k directly.
            dn = _read_wav_stereo(src_wav, target_sr=TARGET_SR).copy()
        else:
            norm_wav = td_p / "loudnorm_pre_aac.wav"
            master_2pass_wav_stereo(
                src_wav,
                norm_wav,
                target_lufs=target_lufs,
                max_tp_db=pre_aac_tp_db,
                lra=lra,
                sr=TARGET_SR,
            )
            # Preserve full linked stereo (N, 2) — NEVER collapse to mono [c0, c0]
            dn = _read_wav_stereo(norm_wav, target_sr=TARGET_SR).copy()
        tw = td_p / "pre_aac_iter.wav"
        tr = td_p / "dec192_stereo.f32"

        for p_idx, thr in enumerate(thresholds):
            _write_wav_stereo(tw, dn, sr=TARGET_SR)
            subprocess.run(
                [
                    "ffmpeg", "-hide_banner", "-y", "-i", str(tw),
                    "-c:a", "aac", "-b:a", "256k", "-ar", str(TARGET_SR), "-ac", "2",
                    str(dst_m4a),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            stats = measure_ebur128(dst_m4a)
            if (target_lufs - 0.40) <= stats["integrated_lufs"] <= (target_lufs + 0.40) and stats["true_peak_dbfs"] <= max_tp_db:
                break

            # Decode AAC back at 4x oversampling (192 kHz, stereo) for linked-stereo true-peak correction
            subprocess.run(
                [
                    "ffmpeg", "-hide_banner", "-y", "-i", str(dst_m4a),
                    "-ar", "192000", "-ac", "2", "-f", "f32le", str(tr),
                ],
                capture_output=True,
                check=True,
            )
            dec192 = np.frombuffer(tr.read_bytes(), dtype=np.float32).reshape(-1, 2)
            n48 = min(len(dn), len(dec192) // 4)
            if n48 > 0:
                pk_stereo = np.max(np.abs(dec192[: n48 * 4].reshape(n48, 4, 2)), axis=(1, 2))
                over = np.maximum(1.0, pk_stereo / float(thr))
                gain_down = 1.0 / np.maximum(1.0, np.convolve(maximum_filter1d(over, size=win), kern, mode="same"))
                dn[:n48] *= gain_down[:, None]

                if stats["integrated_lufs"] < (target_lufs - 0.30):
                    boost = min(1.06, 10.0 ** ((target_lufs - stats["integrated_lufs"]) / 20.0))
                    low_mask = pk_stereo < (float(thr) * 0.85)
                    dn[:n48][low_mask] *= float(boost)
                elif stats["integrated_lufs"] > (target_lufs + 0.30):
                    trim = max(0.94, 10.0 ** ((target_lufs - stats["integrated_lufs"]) / 20.0))
                    dn[:n48] *= float(trim)

            if p_idx == len(thresholds) - 1:
                # Final safety check iteration
                _write_wav_stereo(tw, dn, sr=TARGET_SR)
                subprocess.run(
                    [
                        "ffmpeg", "-hide_banner", "-y", "-i", str(tw),
                        "-c:a", "aac", "-b:a", "256k", "-ar", str(TARGET_SR), "-ac", "2",
                        str(dst_m4a),
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                stats = measure_ebur128(dst_m4a)

    if not ((target_lufs - 0.40) <= stats["integrated_lufs"] <= (target_lufs + 0.40) and stats["true_peak_dbfs"] <= max_tp_db):
        raise RuntimeError(f"Calibrated stereo AAC out of contract for {dst_m4a}: {stats}")
    return stats


# ---------------------------------------------------------------------------
# End-to-End Suspense Mix Orchestrator
# ---------------------------------------------------------------------------

def compute_voice_envelope_30fps(
    voice_stereo: np.ndarray,
    sr: int = TARGET_SR,
    fps: int = FPS,
) -> list[float]:
    """Compute normalized [0.0, 1.0] 30fps RMS envelope from clean voice track for HUDs."""
    stereo = _ensure_stereo(voice_stereo)
    n_samples = len(stereo)
    total_dur = n_samples / float(sr)
    n_frames = max(1, int(round(total_dur * fps)))
    samples_per_frame = sr / float(fps)
    v_mono = np.sqrt(0.5 * (stereo[:, 0] ** 2 + stereo[:, 1] ** 2))

    env_30fps: list[float] = []
    for f_idx in range(n_frames):
        s0 = int(f_idx * samples_per_frame)
        s1 = min(n_samples, max(s0 + 1, int((f_idx + 1) * samples_per_frame)))
        rms = float(np.sqrt(np.mean(v_mono[s0:s1] ** 2))) if s1 > s0 else 0.0
        env_30fps.append(rms)

    max_env = max(env_30fps) if env_30fps else 1.0
    if max_env > 1e-6:
        env_30fps = [round(min(1.0, e / (max_env * 0.85)), 4) for e in env_30fps]
    return env_30fps


def _apply_beat_vhf_cues(
    voice_stereo: np.ndarray,
    beats: list[dict[str, Any]] | None,
    sr: int,
    seed: int,
) -> np.ndarray:
    if not beats:
        return voice_stereo
    out = voice_stereo.copy()
    for idx, b in enumerate(beats):
        t0 = float(b.get("start_sec", 0.0))
        t1 = float(b.get("end_sec", t0 + float(b.get("duration", 0.0))))
        if t1 <= t0 + 0.05:
            continue

        bid = str(b.get("beat_id", "")).upper()
        sid = str(b.get("sent_id", "")).upper()
        vhf_cfg = b.get("vhf_mode", b.get("vhf", b.get("radio_texture")))
        quote_mode = str(b.get("quote_mode", "")).lower()

        if quote_mode == "direct_vhf" or (isinstance(vhf_cfg, str) and vhf_cfg.lower() in ("texture", "radio", "filter", "vhf_filter", "direct_quote")):
            out = apply_vhf_radio_texture(out, start_sec=t0, end_sec=t1, sr=sr, seed=seed + idx * 11)
        elif vhf_cfg or b.get("cvr_bed") or bid in _HELIOS_VHF_IDS or sid in _HELIOS_VHF_IDS:
            out = add_vhf_cockpit_bed(out, start_sec=t0, end_sec=t1, sr=sr, seed=seed + idx * 11)
    return out


def build_suspense_audio_mix(
    voice_wav: Path | str,
    out_wav: Path | str,
    out_m4a: Path | str,
    beats: list[dict[str, Any]] | None,
    variant: str = "A",
    seed: int = 42,
    sr: int = TARGET_SR,
    drop_windows: list[tuple[float, float]] | None = None,
) -> dict[str, Any]:
    """Build complete 48kHz stereo suspense mix (.wav + calibrated .m4a + 30fps HUD envelope)."""
    v_code, _ = _resolve_variant(variant)
    voice_raw = _read_wav_stereo(voice_wav, target_sr=sr)
    n_samples = len(voice_raw)
    duration_sec = n_samples / float(sr)

    # Compute 30fps envelope from clean dry voice before SFX/BGM layering
    env_30fps = compute_voice_envelope_30fps(voice_raw, sr=sr, fps=FPS)

    # Pre-level voice cleanly so BGM/SFX SNR stays deterministic regardless of input gain
    v_mono = np.sqrt(0.5 * (voice_raw[:, 0] ** 2 + voice_raw[:, 1] ** 2))
    active = v_mono[v_mono > 0.005]
    speech_rms = float(np.sqrt(np.mean(active ** 2))) if len(active) else float(np.sqrt(np.mean(v_mono ** 2)))
    if speech_rms > 1e-5:
        target_speech_rms = 0.19  # ~-14.4 dBFS speech RMS (~-12.0 LUFS pre-mix)
        voice_pre = voice_raw * min(3.5, target_speech_rms / speech_rms)
        v_pk = float(np.max(np.abs(voice_pre)))
        if v_pk > 0.85:
            voice_pre *= 0.85 / v_pk
    else:
        voice_pre = voice_raw

    voice_with_vhf = _apply_beat_vhf_cues(voice_pre, beats, sr=sr, seed=seed + 31)
    bgm = compose_4act_tension_bgm(
        n_samples=n_samples,
        voice_stereo=voice_pre,
        beats=beats,
        variant=v_code,
        sr=sr,
        seed=seed,
        drop_windows=drop_windows,
    )
    sfx = _compose_suspense_sfx_layer(beats=beats, n_samples=n_samples, variant=v_code, sr=sr, seed=seed + 17)

    mixed = voice_with_vhf * 0.90 + bgm + sfx
    peak = float(np.max(np.abs(mixed))) if n_samples else 0.0
    if peak > 0.94:
        mixed *= 0.94 / peak

    out_wav_p = Path(out_wav)
    out_m4a_p = Path(out_m4a)
    out_wav_p.parent.mkdir(parents=True, exist_ok=True)
    out_m4a_p.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        raw_mix_wav = Path(td) / "raw_suspense_mix.wav"
        _write_wav_stereo(raw_mix_wav, mixed, sr=sr)
        ebur_wav = master_2pass_wav_stereo(
            raw_mix_wav,
            out_wav_p,
            target_lufs=-11.0,
            max_tp_db=-1.4,
            lra=4.5,
            sr=sr,
        )

    # Verify WAV contract explicitly
    if not (-11.40 <= ebur_wav["integrated_lufs"] <= -10.60 and ebur_wav["true_peak_dbfs"] <= -1.0):
        raise RuntimeError(f"Master WAV loudness out of contract for {out_wav_p}: {ebur_wav}")

    ebur_m4a = encode_calibrated_m4a_stereo(
        out_wav_p,
        out_m4a_p,
        target_lufs=-11.0,
        max_tp_db=-1.0,
        pre_aac_tp_db=-1.4,
        lra=4.5,
    )

    return {
        "wav_path": str(out_wav_p),
        "m4a_path": str(out_m4a_p),
        "variant": v_code,
        "ebur128_wav": ebur_wav,
        "ebur128_m4a": ebur_m4a,
        "env_30fps": env_30fps,
        "duration_sec": round(duration_sec, 6),
        "sample_rate": sr,
        "channels": 2,
    }


__all__ = [
    "FPS",
    "TARGET_SR",
    "VARIANT_PROFILES",
    "add_vhf_cockpit_bed",
    "apply_stereo_pan",
    "apply_vhf_radio_texture",
    "build_suspense_audio_mix",
    "compose_4act_tension_bgm",
    "compute_voice_envelope_30fps",
    "encode_calibrated_m4a_stereo",
    "master_2pass_wav_stereo",
    "measure_ebur128",
    "place_stereo_sfx",
    "synth_air_leak_turbulence",
    "synth_boeing_737_warning_horn",
    "synth_chapter_stinger",
    "synth_master_caution_chime",
    "synth_riser_to_subdrop",
]
