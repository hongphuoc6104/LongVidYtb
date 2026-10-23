"""Sample-preserving audio preparation, sidechain BGM ducking, and studio micro-SFX mixer."""
import json
import math
import shutil
import struct
import subprocess
import wave
from pathlib import Path


class AudioProcessingError(RuntimeError):
    pass


Blocked = AudioProcessingError


def frames_of(path):
    with wave.open(str(path)) as wav:
        return wav.getnframes()


def run_ffmpeg(cmd, log):
    """Run one ffmpeg step, appending its command and output to `log`.

    Distinguishes "ffmpeg is not installed" (FileNotFoundError from the OS,
    nothing to log) from "ffmpeg ran and exited non-zero" (logged for postmortem)
    so master()'s caller gets an accurate Blocked message either way.
    """
    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError as err:
        raise Blocked('ffmpeg not found on PATH; install ffmpeg to master narration audio') from err
    with open(log, 'a') as f:
        f.write('$ ' + ' '.join(cmd) + '\n' + r.stdout + r.stderr + '\n')
    return r


# Voice-forward chain for TTS narration (OmniVoice VietNarrator is breathy and
# dark: energy above 3 kHz sits ~24 dB under the full band, which reads as a
# whisper on phone speakers). Rumble cut, de-mud, presence lift, de-ess, then a
# gentle leveller plus a fast peak catcher so the crest factor drops enough to
# reach a loud target without the limiter grinding (the old "louder = harsh").
VOICE_CHAIN = (
    'highpass=f=80,'
    'equalizer=f=250:t=q:w=1:g=-2,'
    'equalizer=f=3200:t=q:w=1.2:g=3.5,'
    'highshelf=f=9000:g=1.5,'
    'deesser=i=0.4:m=0.5:f=0.5,'
    'acompressor=threshold=-22dB:ratio=3:attack=4:release=90:knee=4:makeup=1,'
    'acompressor=threshold=-10dB:ratio=8:attack=1:release=40:knee=2'
)
# alimiter is sample-peak only; keep margin so inter-sample true peak stays under target.
TRUE_PEAK_MARGIN_DB = 0.7


def _measure(path, log):
    r = run_ffmpeg(['ffmpeg', '-v', 'info', '-i', str(path), '-af', 'loudnorm=print_format=json', '-f', 'null', '-'], log)
    try:
        return json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
    except ValueError:
        return None


def master(src, dst, cfg):
    """Voice EQ + dynamics, then closed-loop static gain to target loudness under a peak limiter.

    loudnorm is used for ANALYSIS only: its dynamic mode pads and resamples to
    192 kHz, which would break the +/-30 ms duration gates in pilot.checks.
    alimiter needs level=disabled or it auto-normalises straight back to 0 dBFS.
    Gain is re-measured once after limiting and corrected, since limiting eats
    loudness. Every filter here is sample-preserving; the frame count is asserted anyway.
    """
    log = dst.parent / (dst.stem + '.log')
    chain = cfg.get('audio_voice_chain', VOICE_CHAIN)
    r = run_ffmpeg(['ffmpeg', '-y', '-i', str(src), '-af', chain, '-ar', '48000', '-c:a', 'pcm_s16le', str(dst)], log)
    if r.returncode or not (dst.exists() and dst.stat().st_size > 1000):
        raise Blocked(f'Audio mastering (EQ) failed; see {log.name}')
    m = _measure(dst, log)
    if m is None:
        dst.unlink(missing_ok=True)
        raise Blocked(f'Audio mastering (loudness analysis) failed; see {log.name}')
    peak = float(cfg.get('audio_peak_db', -1.0))
    target = float(cfg.get('audio_lufs', -11.))
    limit = 10 ** ((peak - TRUE_PEAK_MARGIN_DB) / 20)
    input_i = float(m['input_i'])
    if math.isinf(input_i) or input_i < -70.0:
        # Silent or sub-gated audio: preserve silence without infinite gain
        gain = 0.0
    else:
        gain = target - input_i
    final = dst.with_name('narration_lv.wav')
    for _ in range(2):
        r = run_ffmpeg(
            ['ffmpeg', '-y', '-i', str(dst), '-af',
             f'volume={gain:.2f}dB,alimiter=limit={limit:.4f}:attack=2:release=60:level=disabled',
             '-ar', '48000', '-c:a', 'pcm_s16le', str(final)],
            log,
        )
        if r.returncode:
            break
        got = _measure(final, log)
        if got is None:
            break
        got_i = float(got['input_i'])
        if math.isinf(got_i) or abs(got_i - target) <= 0.3:
            break
        gain += min(3.0, target - got_i)
    dst.unlink(missing_ok=True)
    if r.returncode:
        final.unlink(missing_ok=True)
        raise Blocked(f'Audio mastering (gain/limiter) failed; see {log.name}')
    if not (final.exists() and final.stat().st_size > 1000):
        raise Blocked(f'Audio mastering produced an invalid file; see {log.name}')
    if frames_of(final) != frames_of(src):
        final.unlink(missing_ok=True)
        raise Blocked(f'Audio mastering changed frame count; refusing to replace source; see {log.name}')
    shutil.move(str(final), str(src))


def synthesize_micro_sfx(kind: str, duration_sec: float = 0.22, sr: int = 48000, amplitude: float = 0.14) -> list[int]:
    """Deterministic studio micro-SFX generator in 48kHz PCM16 (pop, whoosh, pencil_stroke, soft_riser)."""
    n_samples = max(1, round(duration_sec * sr))
    samples = []
    for i in range(n_samples):
        t = i / sr
        u = i / max(1, n_samples - 1)
        if kind == 'pop':
            # Warm resonant sine drop (240Hz -> 85Hz) with fast exponential decay
            freq = 85.0 + 155.0 * math.exp(-18.0 * u)
            env = math.sin(min(1.0, u * 8.0) * math.pi * 0.5) * math.exp(-7.5 * u)
            val = math.sin(2.0 * math.pi * freq * t) * env
        elif kind == 'whoosh':
            # Aerodynamic multi-harmonic sweep with bell envelope
            env = math.sin(u * math.pi) ** 1.6
            mod = math.sin(2.0 * math.pi * (95.0 + 210.0 * math.sin(u * math.pi)) * t)
            shimmer = 0.5 * math.sin(2.0 * math.pi * 430.0 * t + math.sin(t * 1700.0))
            val = (0.65 * mod + 0.35 * shimmer) * env
        elif kind == 'pencil_stroke':
            # Textured paper friction grain for draw_on reveals
            env = math.sin(u * math.pi) * (0.7 + 0.3 * math.sin(2.0 * math.pi * 14.0 * t))
            grain = math.sin(i * 12.9898) * 43758.5453
            noise = (grain - math.floor(grain)) * 2.0 - 1.0
            val = noise * env * 0.55
        else:
            # 'soft_riser': gentle warm harmonic swell
            env = (u ** 1.5) * math.sin(u * math.pi)
            val = 0.7 * math.sin(2.0 * math.pi * (110.0 + 110.0 * u) * t) * env
        pcm = max(-32767, min(32767, int(val * amplitude * 32767)))
        samples.append(pcm)
    return samples


def mix_sound_design(
    narration_wav: Path,
    output_wav: Path,
    cfg: dict | None = None,
    bgm_wav: Path | None = None,
    sfx_events: list[dict] | None = None,
) -> dict:
    """Sample-exact studio mixer combining narration with sidechain-ducked BGM and timed micro-SFX.

    Automatically raises BGM volume during narrative pauses and ducks BGM smoothly
    (attack ~45ms, release ~380ms) whenever voice activity is detected, while
    maintaining exact PCM frame count equality with `narration_wav`.
    """
    cfg = cfg or {}
    narration_wav = Path(narration_wav)
    output_wav = Path(output_wav)
    with wave.open(str(narration_wav), 'rb') as wf:
        channels, sampwidth, sr, nframes, _, _ = wf.getparams()
        if (channels, sampwidth) != (1, 2):
            raise Blocked('mix_sound_design expects mono 16-bit PCM narration WAV')
        if nframes <= 0:
            raise Blocked('mix_sound_design expects non-empty narration audio')
        raw_voice = wf.readframes(nframes)
    voice_samples = list(struct.unpack(f'<{nframes}h', raw_voice))

    # Optional BGM loading (looped to match nframes)
    bgm_samples = [0] * nframes
    if bgm_wav and Path(bgm_wav).is_file():
        with wave.open(str(bgm_wav), 'rb') as bf:
            b_ch, b_sw, b_sr, b_nf, _, _ = bf.getparams()
            if b_sw == 2 and b_nf > 0:
                b_raw = bf.readframes(b_nf)
                b_unpacked = struct.unpack(f'<{b_nf * b_ch}h', b_raw)
                mono_bgm = b_unpacked[::b_ch] if b_ch > 1 else b_unpacked
                if mono_bgm:
                    m_len = len(mono_bgm)
                    bgm_samples = [mono_bgm[i % m_len] for i in range(nframes)]

    # Envelope-guided Sidechain Ducking (windowed speech activity detector)
    duck_gain = float(cfg.get('bgm_duck_gain', 0.07))
    swell_gain = float(cfg.get('bgm_swell_gain', 0.20))
    voice_thresh = int(cfg.get('sidechain_threshold_pcm', 450))
    block_size = max(1, sr // 50)  # 20ms blocks
    n_blocks = (nframes + block_size - 1) // block_size
    block_gains = [swell_gain] * n_blocks

    current_gain = swell_gain
    attack_coeff = 0.45   # fast ducking (~45ms)
    release_coeff = 0.06  # smooth musical swell recovery (~380ms)
    for b_idx in range(n_blocks):
        start_i = b_idx * block_size
        end_i = min(nframes, start_i + block_size)
        peak_v = max((abs(voice_samples[j]) for j in range(start_i, end_i)), default=0)
        target = duck_gain if peak_v >= voice_thresh else swell_gain
        coeff = attack_coeff if target < current_gain else release_coeff
        current_gain = current_gain + coeff * (target - current_gain)
        block_gains[b_idx] = current_gain

    # Overlay micro-SFX events at exact timestamps
    sfx_buffer = [0] * nframes
    sfx_applied = 0
    for ev in (sfx_events or []):
        kind = str(ev.get('kind', 'pop'))
        at_sec = float(ev.get('at', 0.0))
        dur_sec = float(ev.get('duration', 0.22))
        amp = float(ev.get('amplitude', 0.14))
        start_frame = max(0, min(nframes - 1, round(at_sec * sr)))
        sfx_pcm = synthesize_micro_sfx(kind, duration_sec=dur_sec, sr=sr, amplitude=amp)
        for k, s_val in enumerate(sfx_pcm):
            idx = start_i = start_frame + k
            if idx >= nframes:
                break
            sfx_buffer[idx] = max(-32767, min(32767, sfx_buffer[idx] + s_val))
        sfx_applied += 1

    # Final sample-exact mix with soft ceiling protection
    mixed = []
    for i in range(nframes):
        g = block_gains[i // block_size]
        total_val = voice_samples[i] + int(bgm_samples[i] * g) + sfx_buffer[i]
        mixed.append(max(-32767, min(32767, total_val)))

    output_wav.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output_wav), 'wb') as out_wf:
        out_wf.setparams((1, 2, sr, nframes, 'NONE', 'not compressed'))
        out_wf.writeframes(struct.pack(f'<{nframes}h', *mixed))

    if frames_of(output_wav) != nframes:
        raise Blocked('mix_sound_design altered frame count')
    return {
        'frames': nframes,
        'sample_rate': sr,
        'sfx_events_applied': sfx_applied,
        'bgm_mixed': bool(bgm_wav and Path(bgm_wav).is_file()),
    }
