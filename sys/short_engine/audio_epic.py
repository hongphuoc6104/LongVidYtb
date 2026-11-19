"""Colab T4 OmniVoice Audio Synthesis, 6-Mode Prosody Sculpting & Heroic 5-Act Epic Score."""
from __future__ import annotations

import copy
import hashlib
import json
import logging
import math
import re
import shutil
import subprocess
import tempfile
import threading
import time
import wave
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
from colab_bridge.client import Client
from colab_bridge.pool_manager import ColabPoolDispatcher, ColabPoolManager
from fx_warehouse.audio_sfx_bgm import BGM_DIR, SFX_DIR, ensure_warehouse_audio_assets, synthesize_bespoke_topic_sfx
from fx_warehouse.audio_suspense_v2 import (
    _compute_voice_sidechain_gain,
    _ensure_stereo,
    _read_wav_stereo,
    _write_wav_stereo,
    place_stereo_sfx,
)
from scipy.signal import butter, sosfilt
from tools.cta_tone_linter import lint_cta
from tools.produce_vn_dual_mode import build_clean_sidecar_srt, load_voice_profile
from tools.vn_text_normalizer import detect_unnormalized_tokens
from visual_pacing import check_see_say_beat_density
from voice_prosody import BASELINE_LUFS, DYNAMIC_MICRO_GAIN_DB, resolve_delivery_profile, split_text_with_pauses

from . import ROOT_DIR, SYS_DIR, TARGET_SR, VIETSUB_FONT_SIZE, measure_ebur128, select_idle_colab_accounts

logger = logging.getLogger("produce_serialized_short.audio_epic")

MIN_BEAT_DURATION_SEC = 1.60
MAX_BEAT_DURATION_SEC = 5.65
MIN_TOTAL_DURATION_SEC = 95.0
MAX_TOTAL_DURATION_SEC = 175.0
ATEMPO_MIN = 1.04
ATEMPO_MAX = 1.38
KINETIC_RED_ASS = "&H00303BFF"
KINETIC_YELLOW_ASS = "&H0000E6FF"

BGM_DUCK_SPEECH_DB = -23.0
BGM_SWELL_PAUSE_DB = -16.5
HEROIC_SPEECH_DUCK_DB = -17.5
HEROIC_PAUSE_SWELL_DB = -12.5
RAIN_VACUUM_DB = -24.0
HEARTBEAT_VACUUM_DB = -10.0

REMOTE_TTS_WORKER_CODE = r'''# Remote Colab Tesla T4 OmniVoice Per-Segment Runner
import json, re, zipfile
from pathlib import Path
import numpy as np, soundfile as sf, torch
from huggingface_hub import snapshot_download
from omnivoice import OmniVoice
from scipy.signal import butter, resample_poly, sosfiltfilt


def clean_tts_text(text: str) -> str:
    t = re.sub(r"\[pause:[^\]]+\]", " ", str(text or "").strip())
    t = re.sub(r"(?<=[^\W\d_])-(?=[^\W\d_])", " ", t)
    return re.sub(r"\s+", " ", re.sub(r"[\u2014\u2013—–]", " ", re.sub(r"[*_`#~]", "", t))).strip()


def _strip_leading_prompt_bleed(w: np.ndarray, sr: int = 48000) -> np.ndarray:
    hop = max(1, sr // 100)
    nf, sample_idx = len(w) // hop, np.where(np.abs(w) >= 0.010)[0]
    if nf < 45 or not len(sample_idx):
        return w
    rms, b_start = np.sqrt(np.mean(w[: nf * hop].reshape(nf, hop) ** 2, axis=1)), int(sample_idx[0]) // hop
    if b_start > 15:
        return w
    for g_start in range(b_start + 1, min(b_start + 7, nf - 22)):
        if rms[g_start] < 0.008:
            if float(np.max(rms[b_start:g_start])) >= 0.035:
                return w
            s_cands = np.where(rms[g_start:] >= 0.014)[0]
            if not len(s_cands):
                return w
            s_start = g_start + int(s_cands[0])
            if (s_start - g_start) >= 12 and int(np.sum(rms[g_start:s_start] < 0.008)) >= (s_start - g_start - 1):
                if int(np.sum(rms[s_start : min(nf, s_start + 25)] >= 0.015)) >= 10:
                    return w[max(0, (s_start - 3) * hop) :]
    return w


def _trim_silence(w: np.ndarray, sr: int = 48000, threshold: float = 0.008, lead_ms: int = 25, trail_ms: int = 30, fade_ms: int = 8) -> np.ndarray:
    w = _strip_leading_prompt_bleed(np.asarray(w, dtype=np.float32).reshape(-1), sr=sr)
    idx = np.where(np.abs(w) >= threshold)[0]
    if not idx.size:
        return w
    soft_coda = np.where(np.abs(w[int(idx[-1]) : min(len(w), int(idx[-1]) + round(0.09 * sr))]) >= min(threshold, 0.006))[0]
    last_v = int(idx[-1]) + (int(soft_coda[-1]) if soft_coda.size else 0)
    start, end = max(0, int(idx[0]) - round(lead_ms * sr / 1000)), min(len(w), last_v + 1 + round(trail_ms * sr / 1000))
    trimmed = w[start:end].copy()
    fade = min(round(fade_ms * sr / 1000), len(trimmed) // 4)
    fi, fo = min(fade, max(0, int(idx[0]) - start)), min(fade, max(0, end - 1 - last_v))
    if fi > 1:
        trimmed[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)
    if fo > 1:
        trimmed[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)
    return trimmed


def _utterance_acoustic_score(w: np.ndarray, synth_text: str, sr: int = 48000) -> tuple[bool, float]:
    w = np.asarray(w, dtype=np.float32).reshape(-1)
    if not w.size:
        return False, -999.0
    n_words, dur = len(re.findall(r"[^\W\d_]+", synth_text or "")), len(w) / float(sr)
    if n_words <= 2:
        return dur >= 0.20, dur
    hop = max(1, sr // 100)
    nf = len(w) // hop
    if nf < 10:
        return False, -999.0
    rms = np.sqrt(np.mean(w[: nf * hop].reshape(nf, hop) ** 2, axis=1))
    voiced_s, v_idx = float(np.sum(rms >= 0.008)) * (hop / float(sr)), np.where(rms >= 0.008)[0]
    max_gap = float(np.max(np.diff(v_idx) - 1)) * (hop / float(sr)) if len(v_idx) > 1 else 0.0
    gap_limit = 0.78 if re.search(r"[,.;:!?]", (synth_text or "").strip()[:-1]) else 0.40
    return (voiced_s >= max(0.28, n_words * 0.095)) and (max_gap <= gap_limit), (voiced_s / max(1, n_words)) - max(0.0, max_gap - gap_limit) * 2.0


def postprocess_48k(arr: np.ndarray, src_sr: int = 24000) -> np.ndarray:
    arr = np.asarray(arr, dtype=np.float32).reshape(-1)
    if arr.size == 0 or not np.isfinite(arr).all():
        return np.zeros(0, dtype=np.float32)
    if src_sr != 48000:
        arr = resample_poly(arr, 48000 // src_sr if 48000 % src_sr == 0 else 48000, 1 if 48000 % src_sr == 0 else src_sr).astype(np.float32)
    if len(arr) >= 64:
        try:
            hp = sosfiltfilt(butter(2, 85.0 / 24000.0, btype="highpass", output="sos"), arr).astype(np.float32)
            if np.isfinite(hp).all():
                arr = hp
        except Exception:
            pass
    pk = float(np.max(np.abs(arr))) if len(arr) else 0.0
    arr = _trim_silence(arr * (0.95 / pk if pk > 0.95 else 1.0), sr=48000)
    pk2 = float(np.max(np.abs(arr))) if len(arr) else 0.0
    return arr * (0.95 / pk2) if pk2 > 0.95 else arr


def main() -> None:
    assert torch.cuda.is_available(), "COLAB_GPU_REQUIRED: CUDA unavailable"
    assert "T4" in torch.cuda.get_device_name(0), f"COLAB_GPU_REQUIRED: expected Tesla T4, got {torch.cuda.get_device_name(0)}"
    work = Path("/content/vp_short_tts_work")
    manifest = json.loads((work / "manifest.json").read_text(encoding="utf-8"))
    default_speed = float(manifest.get("base_omnivoice_speed", 1.06))
    local_model = snapshot_download(str(manifest.get("model_id", "kjanh/KhanhTTS-OmniVoice")), revision=str(manifest.get("model_rev", "20d056b8ea5d8d578b4cbaf1f703012fa3798a84")))
    model = OmniVoice.from_pretrained(local_model, device_map="cuda:0", dtype=torch.float16)
    prompt = model.create_voice_clone_prompt(ref_audio=str(work / manifest["ref_wav_filename"]), ref_text=manifest["reference_text"])
    out_wavs = work / "out_wavs"
    out_wavs.mkdir(parents=True, exist_ok=True)
    meta = {}
    for idx, item in enumerate(manifest["items"]):
        key, text = item["key"], clean_tts_text(item["tts_text"])
        item_speed, gidx, syl = float(item.get("omni_speed", default_speed)), int(item.get("index", idx)), len(text.split())
        min_ok, max_ok, good, best_fb, best_sc = max(0.45, syl / 7.5), max(4.2, syl / 1.8 + 1.8), None, None, -1e9
        for attempt in range(3):
            torch.manual_seed(307 + gidx * 17 + attempt * 43)
            with torch.inference_mode():
                wavs = model.generate(text=[text], language=["vi"], voice_clone_prompt=[prompt], speed=[item_speed], num_step=32)
            arr = postprocess_48k(wavs[0], src_sr=24000)
            dur, rms = len(arr) / 48000.0, (float(np.sqrt(np.mean(arr**2))) if len(arr) else 0.0)
            bounds_ok = len(arr) > 0 and rms >= 0.005 and (min_ok <= dur <= max_ok)
            sc_ok, sc = _utterance_acoustic_score(arr, text, sr=48000)
            if bounds_ok and sc > best_sc:
                best_sc, best_fb = sc, arr
            if bounds_ok and sc_ok:
                good = arr
                break
        good = good if good is not None else best_fb
        if good is None:
            raise RuntimeError(f"Failed valid OmniVoice synthesis for {key} after 3 attempts")
        sf.write(str(out_wavs / f"{key}.wav"), good, 48000, subtype="PCM_16")
        meta[key] = {"duration": round(len(good) / 48000.0, 4), "syllables": syl, "omni_speed": item_speed}
    (work / "shard_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    with zipfile.ZipFile(work / "results.zip", "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(work / "shard_meta.json", "shard_meta.json")
        for p in sorted(out_wavs.glob("*.wav")):
            zf.write(p, f"wavs/{p.name}")


if __name__ == "__main__":
    main()
'''


def _fmt_ass_ts(sec: float) -> str:
    """Format seconds into ASS timestamp `H:MM:SS.CC`."""
    cs = max(0, int(round(sec * 100.0)))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _parse_ass_ts(ts: str) -> float:
    """Parse ASS timestamp `H:MM:SS.CC` into seconds."""
    parts = ts.strip().split(":")
    if len(parts) != 3:
        raise ValueError(f"Invalid ASS timestamp: {ts!r}")
    s_str, frac_str = parts[2].split(".", 1) if "." in parts[2] else (parts[2], "0")
    return int(parts[0]) * 3600.0 + int(parts[1]) * 60.0 + int(s_str) + float(f"0.{frac_str}")


def _run_ffmpeg_wav(in_wav: Path, af: str, out_wav: Path) -> None:
    """Transcode WAV through an FFmpeg audio filter graph to 48kHz stereo PCM16."""
    subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", str(in_wav), "-af", af, "-ar", str(TARGET_SR), "-ac", "2", "-c:a", "pcm_s16le", str(out_wav)], check=True, capture_output=True)


def _utterance_ok(wav_path: Path, syl_count: int) -> bool:
    """Verify synthesized raw WAV exists, matches 48kHz PCM16, and meets duration/RMS bounds."""
    if not wav_path.is_file() or wav_path.stat().st_size < 8000:
        return False
    try:
        with wave.open(str(wav_path), "rb") as wf:
            sr, nf, ch, sw, raw = wf.getframerate(), wf.getnframes(), wf.getnchannels(), wf.getsampwidth(), wf.readframes(wf.getnframes())
        if sr != TARGET_SR or sw != 2 or ch not in (1, 2):
            return False
        dur = nf / float(sr)
        rms = float(np.sqrt(np.mean((np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0) ** 2))) if nf else 0.0
        return rms >= 0.004 and max(0.45, syl_count / 7.5) <= dur <= max(4.2, syl_count / 1.8 + 1.8)
    except Exception:
        return False


def polish_lufs_true_peak(wav_path: Path, target_lufs: float = -11.0, max_tp_db: float = -1.0, tp_guard_margin_db: float = 0.25) -> dict[str, float]:
    """Iteratively calibrate integrated LUFS and true-peak ceiling on WAV audio."""
    metrics = measure_ebur128(wav_path)
    for _ in range(6):
        cur_i, cur_tp = metrics["integrated_lufs"], metrics["true_peak_dbtp"]
        if abs(cur_i - target_lufs) <= 0.15 and cur_tp <= max_tp_db:
            return metrics
        tmp_p = wav_path.with_suffix(".polish.wav")
        limit_lin = 10 ** ((max_tp_db - tp_guard_margin_db) / 20.0)
        _run_ffmpeg_wav(wav_path, f"volume={target_lufs - cur_i:+.3f}dB,aresample=192000,alimiter=limit={limit_lin:.6f}:attack=3:release=45:level=disabled,aresample={TARGET_SR}", tmp_p)
        shutil.move(str(tmp_p), str(wav_path))
        metrics = measure_ebur128(wav_path)
    return metrics


def _run_colab_tts_shards(missing_items: list[dict[str, Any]], *, channel_id: str, ref_wav: Path, ref_text: str, base_speed: float, raw_dir: Path, max_workers: int = 3) -> None:
    """Dispatch missing speech segments across idle Colab Tesla T4 GPUs via OmniVoice."""
    if not missing_items:
        return
    session_name = f"vp-tts-{channel_id[:16]}"
    pool_accounts = select_idle_colab_accounts(session_name, max_accounts=max(4, max_workers + 1), min_seconds=450.0)
    if not pool_accounts:
        raise RuntimeError("No healthy idle Colab T4 accounts available for TTS")
    worker_count = max(1, min(max_workers, len(pool_accounts), len(missing_items)))
    pm = ColabPoolManager(accounts_config=[{"id": acc, "role": "tts", "session": session_name} for acc in pool_accounts], session_name=session_name)
    dispatcher = ColabPoolDispatcher(pm, max_retries_per_task=4)
    shards: list[list[dict[str, Any]]] = [[] for _ in range(worker_count)]
    for i, item in enumerate(missing_items):
        shards[i % worker_count].append(item)
    tasks = [{"id": f"tts_shard_{idx}", "index": idx, "items": shard} for idx, shard in enumerate(shards)]

    cfg_base_path = SYS_DIR / "config.json"
    cfg_base: dict[str, Any] = json.loads(cfg_base_path.read_text(encoding="utf-8")) if cfg_base_path.is_file() else {}
    vi_cfg = cfg_base.get("colab_tts", {}).get("models", {}).get("vi", {})
    model_id, model_rev = str(vi_cfg.get("repo_id") or "kjanh/KhanhTTS-OmniVoice"), str(vi_cfg.get("revision") or "20d056b8ea5d8d578b4cbaf1f703012fa3798a84")
    guard_lock, unconfirmed_streak, started_accounts = threading.Lock(), 0, set()

    def _run_shard(worker: Any, task: dict[str, Any]) -> dict[str, Any]:
        nonlocal unconfirmed_streak
        with guard_lock:
            if unconfirmed_streak >= 2:
                raise RuntimeError("ABORT_FAILOVER: 2 consecutive COLAB_EXEC_UNCONFIRMED failures")
            started_accounts.add(worker.account_id)
        shard_id, temp_dir, client = task["id"], Path(tempfile.mkdtemp(prefix=f"vp_short_{task['id']}_")), None
        try:
            bundle_zip = temp_dir / "bundle.zip"
            manifest = {"channel_id": channel_id, "base_omnivoice_speed": base_speed, "ref_wav_filename": "ref_voice.wav", "reference_text": ref_text, "model_id": model_id, "model_rev": model_rev, "items": task["items"]}
            with zipfile.ZipFile(bundle_zip, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
                zf.writestr("runner.py", REMOTE_TTS_WORKER_CODE)
                zf.write(ref_wav, "ref_voice.wav")
            cfg = copy.deepcopy(cfg_base)
            cfg.setdefault("colab_tts", {}).update({"account": worker.account_id, "session": worker.session_name, "_session_explicit": True})
            client = Client(SYS_DIR, cfg)
            client.account, client.session = worker.account_id, worker.session_name
            client.ensure_authenticated()
            snap_cur = client._budgets().snapshot(f"colab:{worker.account_id}")
            has_t4 = any(it.get("session") == client.session and it.get("device") == "T4" for it in snap_cur.get("allocated_sessions", []))
            client._ready(auto_start=False) if has_t4 else client.start()
            try:
                client.exec("import omnivoice, soundfile, scipy", timeout=45)
            except Exception:
                client.setup()
            rw = "/content/vp_short_tts_work"
            client.exec(f"import shutil, pathlib; shutil.rmtree({rw!r}, ignore_errors=True); pathlib.Path({rw!r}).mkdir(parents=True, exist_ok=True)", timeout=120)
            with guard_lock:
                unconfirmed_streak = 0
            client.call("upload", "-s", client.session, str(bundle_zip.resolve()), f"{rw}/bundle.zip", timeout=300)
            client.exec(
                f"import zipfile, subprocess, sys\nwith zipfile.ZipFile('{rw}/bundle.zip', 'r') as zf: zf.extractall('{rw}')\n"
                f"with open('{rw}/runner.log', 'w') as lf: p = subprocess.run([sys.executable, '{rw}/runner.py'], stdout=lf, stderr=subprocess.STDOUT)\n"
                f"print(open('{rw}/runner.log').read())\nif p.returncode != 0: raise RuntimeError(f'Remote TTS runner exited {{p.returncode}}')\n",
                timeout=1800,
            )
            res_zip = temp_dir / "results.zip"
            client.call("download", "-s", client.session, f"{rw}/results.zip", str(res_zip.resolve()), timeout=300)
            with zipfile.ZipFile(res_zip, "r") as zf:
                for member in zf.namelist():
                    if member.startswith("wavs/") and member.endswith(".wav"):
                        (raw_dir / Path(member).name).write_bytes(zf.read(member))
            return {"shard": shard_id, "account": worker.account_id, "count": len(task["items"])}
        except Exception as exc:
            if "COLAB_EXEC_UNCONFIRMED" in str(exc):
                with guard_lock:
                    unconfirmed_streak += 1
            raise
        finally:
            if client is not None:
                try:
                    client.stop()
                except Exception as stop_err:
                    logger.warning("[%s] client.stop warning: %s", worker.account_id, stop_err)
            shutil.rmtree(temp_dir, ignore_errors=True)

    try:
        dispatcher.dispatch_all(tasks, _run_shard, max_concurrency=len(tasks), role="tts")
    finally:
        if started_accounts:
            pm.stop_pool(sorted(started_accounts), unassign_server=True)


def _process_speech_segment(raw_wav: Path, post_wav: Path, *, atempo: float, eq_chain: str, micro_gain_db: float) -> dict[str, Any]:
    """Apply tempo stretch, EQ, `-14 LUFS` baseline calibration, and per-mode micro gain."""
    shaped_wav = post_wav.with_suffix(".shaped.wav")
    eq_part = f",{eq_chain}" if eq_chain else ""
    _run_ffmpeg_wav(raw_wav, f"atempo={atempo:.4f}{eq_part},aformat=sample_fmts=s16:channel_layouts=stereo", shaped_wav)
    base_tp_ceiling = min(-1.6, -1.2 - max(0.0, float(micro_gain_db)))
    base_metrics = polish_lufs_true_peak(shaped_wav, target_lufs=BASELINE_LUFS, max_tp_db=base_tp_ceiling, tp_guard_margin_db=0.15)
    _run_ffmpeg_wav(shaped_wav, f"volume={micro_gain_db:+.2f}dB", post_wav)
    shaped_wav.unlink(missing_ok=True)
    arr = _read_wav_stereo(post_wav, target_sr=TARGET_SR)
    return {"waveform": arr, "duration_sec": len(arr) / float(TARGET_SR), "baseline_lufs": base_metrics["integrated_lufs"], "baseline_tp_dbtp": base_metrics["true_peak_dbtp"]}


def _beat_voice_params(beat: dict[str, Any]) -> dict[str, Any]:
    """Resolve explicit beat voice profile params with widened dynamic-contrast micro gain."""
    mode_key = str(beat.get("delivery_mode") or "").strip()
    ssot = resolve_delivery_profile(mode_key)
    vp = beat.get("voice_profile_params")
    if isinstance(vp, dict) and vp:
        merged = dict(ssot)
        merged.update(vp)
        if mode_key in DYNAMIC_MICRO_GAIN_DB:
            merged["micro_gain_db"] = float(DYNAMIC_MICRO_GAIN_DB[mode_key])
        return merged
    return ssot


def _assemble_single_beat(beat: dict[str, Any], *, raw_dir: Path, post_dir: Path, atempo_override: float | None = None) -> dict[str, Any]:
    """Assemble speech segments, explicit pauses, and trailing beat gap into 48kHz stereo."""
    bid, vp = str(beat["beat_id"]), _beat_voice_params(beat)
    atempo_val = float(np.clip(float(atempo_override if atempo_override is not None else vp["atempo"]), ATEMPO_MIN, ATEMPO_MAX))
    eq_chain, micro_gain_db, gap_after_sec = str(vp.get("eq_chain") or "").strip(), float(vp.get("micro_gain_db", 0.0)), float(vp.get("gap_after_sec", 0.14))
    parts_meta: list[dict[str, Any]] = []
    chunks: list[np.ndarray] = []
    cur_samples = seg_idx = 0
    speech_dur = pause_dur = 0.0
    for item in split_text_with_pauses(beat["tts_text"]):
        if item["type"] == "speech":
            seg_key = f"{bid}_seg{seg_idx:02d}"
            seg_res = _process_speech_segment(raw_dir / f"{seg_key}.wav", post_dir / f"{seg_key}.wav", atempo=atempo_val, eq_chain=eq_chain, micro_gain_db=micro_gain_db)
            arr, s0 = seg_res["waveform"], cur_samples / float(TARGET_SR)
            cur_samples += len(arr)
            dur = len(arr) / float(TARGET_SR)
            speech_dur += dur
            chunks.append(arr)
            parts_meta.append({"type": "speech", "key": seg_key, "seg_idx": seg_idx, "text": item["text"], "local_start_sec": s0, "local_end_sec": cur_samples / float(TARGET_SR), "duration_sec": dur, "baseline_lufs": seg_res["baseline_lufs"], "waveform": arr})
            seg_idx += 1
        elif item["type"] == "pause":
            n_p = max(0, int(round(float(item["seconds"]) * TARGET_SR)))
            if n_p > 0:
                p0, cur_samples = cur_samples / float(TARGET_SR), cur_samples + n_p
                dur = n_p / float(TARGET_SR)
                pause_dur += dur
                chunks.append(np.zeros((n_p, 2), dtype=np.float32))
                parts_meta.append({"type": "pause", "local_start_sec": p0, "local_end_sec": cur_samples / float(TARGET_SR), "duration_sec": dur})
    n_gap = max(0, int(round(gap_after_sec * TARGET_SR)))
    if n_gap > 0:
        chunks.append(np.zeros((n_gap, 2), dtype=np.float32))
        cur_samples += n_gap
    return {
        "beat_id": bid, "atempo_used": round(atempo_val, 4), "micro_gain_db": micro_gain_db, "gap_after_sec": round(n_gap / float(TARGET_SR), 6),
        "pause_sec": round(pause_dur, 6), "speech_duration_sec": round(speech_dur, 6), "duration_sec": cur_samples / float(TARGET_SR),
        "n_samples": cur_samples, "waveform": np.vstack(chunks) if chunks else np.zeros((0, 2), dtype=np.float32), "parts": parts_meta,
    }


def _extract_segment_words_acoustic(seg_wave: np.ndarray, text: str, global_offset: float) -> list[dict[str, Any]]:
    """Align spoken tokens against 10ms RMS energy envelope for frame-tight kinetic subtitles."""
    tokens = [tok for tok in re.sub(r"\[pause:[^\]]+\]", " ", text or "").strip().split() if tok.strip()]
    if not tokens or not len(seg_wave):
        return []
    mono = np.sqrt(0.5 * (seg_wave[:, 0] ** 2 + seg_wave[:, 1] ** 2))
    seg_dur, hop = len(mono) / float(TARGET_SR), max(1, TARGET_SR // 100)
    n_frames = len(mono) // hop
    if n_frames < len(tokens):
        step = seg_dur / len(tokens)
        return [{"word": tok, "start": round(global_offset + i * step, 4), "end": round(global_offset + (i + 1) * step, 4), "seg_end": round(global_offset + seg_dur, 4)} for i, tok in enumerate(tokens)]
    rms = np.sqrt(np.mean(mono[: n_frames * hop].reshape(n_frames, hop) ** 2, axis=1) + 1e-12)
    norm_rms = rms / (float(np.max(rms)) + 1e-9)
    cum_e = np.concatenate([[0.0], np.cumsum(0.72 * (norm_rms > 0.04).astype(np.float32) * (norm_rms + 0.10) + 0.28)])
    total_e, w_weights = float(cum_e[-1]), [max(1.5, len(re.sub(r"[^A-Za-zÀ-ỹ0-9]", "", tok))) for tok in tokens]
    total_w, used_w, prev_end, out = float(sum(w_weights)), 0.0, 0.0, []
    for tok, ww in zip(tokens, w_weights, strict=True):
        e0, used_w = (used_w / total_w) * total_e, used_w + ww
        e1 = (used_w / total_w) * total_e
        t0 = min(seg_dur, max(prev_end, int(np.searchsorted(cum_e, e0, side="left")) * hop / float(TARGET_SR)))
        t1 = min(seg_dur, max(t0 + 0.02, int(np.searchsorted(cum_e, e1, side="left")) * hop / float(TARGET_SR)))
        prev_end = t1
        out.append({"word": tok, "start": round(global_offset + t0, 4), "end": round(global_offset + t1, 4), "seg_end": round(global_offset + seg_dur, 4)})
    return out


def _loop_bgm_seamless(stem_path: Path, n_samples: int, trim_edge_sec: float = 0.25, xfade_sec: float = 0.40) -> np.ndarray:
    """Loop a BGM stem seamlessly via equal-power sine/cosine crossfading."""
    raw = _read_wav_stereo(stem_path, target_sr=TARGET_SR)
    trim_n = min(len(raw) // 6, int(round(trim_edge_sec * TARGET_SR)))
    core = raw[trim_n : len(raw) - trim_n].copy() if len(raw) > trim_n * 3 else raw.copy()
    xf = min(len(core) // 4, int(round(xfade_sec * TARGET_SR)))
    stride, out = max(1, len(core) - xf), np.zeros((n_samples + len(core), 2), dtype=np.float32)
    fi, fo = np.sin(np.linspace(0.0, math.pi * 0.5, xf, dtype=np.float32))[:, None], np.cos(np.linspace(0.0, math.pi * 0.5, xf, dtype=np.float32))[:, None]
    pos, first = 0, True
    while pos < n_samples:
        tile = core.copy()
        if not first and xf > 1:
            tile[:xf] *= fi
        if xf > 1:
            tile[-xf:] *= fo
        out[pos : pos + len(tile)] += tile
        pos, first = pos + stride, False
    return out[:n_samples].astype(np.float32)


def _compute_active_speech_rms(voice_buf: np.ndarray) -> float:
    """Measure active speech RMS over voiced 10ms frames."""
    mono, hop = np.sqrt(0.5 * (voice_buf[:, 0] ** 2 + voice_buf[:, 1] ** 2)), max(1, TARGET_SR // 100)
    nf = len(mono) // hop
    if nf == 0:
        return float(np.sqrt(np.mean(mono**2))) + 1e-8
    frm = np.sqrt(np.mean(mono[: nf * hop].reshape(nf, hop) ** 2, axis=1))
    act = frm[frm > 0.015]
    return float(np.sqrt(np.mean(act**2))) if len(act) else float(np.sqrt(np.mean(mono**2))) + 1e-8


def _stem_active_rms(stem: np.ndarray, mode: str = "rms") -> float:
    """Measure active RMS or 96th-percentile transient RMS of an SFX stem."""
    mono = np.sqrt(0.5 * (stem[:, 0] ** 2 + stem[:, 1] ** 2))
    if not len(mono):
        return 1e-6
    if mode == "transient":
        win = max(1, int(round(0.045 * TARGET_SR)))
        if len(mono) <= win:
            return float(np.sqrt(np.mean(mono**2))) + 1e-8
        sq = np.convolve(mono.astype(np.float64) ** 2, np.ones(win, dtype=np.float64) / win, mode="valid")
        return float(np.sqrt(max(1e-12, float(np.percentile(sq, 96)))))
    act = mono[mono > max(1e-4, float(np.max(mono)) * 0.08)]
    return float(np.sqrt(np.mean((act if len(act) >= 64 else mono) ** 2))) + 1e-8


def synthesize_heroic_epic_score(measured_beats: list[dict[str, Any]], short_spec: dict[str, Any], n_samples: int, sr: int = TARGET_SR) -> np.ndarray:
    """Synthesize a stereo 48kHz 5-Act heroic Vietnamese epic score synced to `measured_beats`."""
    if n_samples <= 0 or not measured_beats:
        return np.zeros((max(0, n_samples), 2), dtype=np.float32)
    buf, rng = np.zeros((n_samples, 2), dtype=np.float64), np.random.default_rng(1789)
    bgm_plan = dict(short_spec.get("bgm_plan") or {})
    vac_bid = str((bgm_plan.get("silence_vacuum") or {}).get("beat_id") or "")
    climax_ids = {str(x) for x in (bgm_plan.get("climax_beats") or [])}
    proud_ids = {str(x) for x in (bgm_plan.get("proud_beats") or [])}

    def _mix(sig: np.ndarray, t_sec: float, gain: float = 1.0, pan: float = 0.0) -> None:
        i0 = int(round(t_sec * sr))
        if i0 >= n_samples or len(sig) == 0:
            return
        th = (float(np.clip(pan, -0.95, 0.95)) + 1.0) * math.pi * 0.25
        st = np.column_stack([sig * math.cos(th), sig * math.sin(th)]) if sig.ndim == 1 else sig
        s0, d0 = max(0, -i0), max(0, i0)
        ln = min(len(st) - s0, n_samples - d0)
        if ln > 0:
            buf[d0 : d0 + ln] += st[s0 : s0 + ln] * gain

    def _war_drum(t_sec: float, gain: float = 0.65, pitch_hz: float = 78.0, punch: float = 1.0) -> None:
        tt = np.arange(int(0.42 * sr), dtype=np.float64) / sr
        body = np.sin(2.0 * np.pi * np.cumsum(pitch_hz * (1.0 + 1.5 * np.exp(-tt / 0.024))) / sr) * np.exp(-tt / (0.14 * punch))
        skin = np.sin(2.0 * np.pi * 2.1 * pitch_hz * tt) * np.exp(-tt / 0.032) * 0.28 + rng.normal(0.0, 0.14, len(tt)) * np.exp(-tt / 0.008)
        _mix((body + skin) * np.minimum(1.0, tt / 0.003), t_sec, gain, pan=-0.06)

    def _bronze_drum(t_sec: float, gain: float = 0.50) -> None:
        tt = np.arange(int(1.65 * sr), dtype=np.float64) / sr
        sig = sum(a * np.sin(2.0 * np.pi * f * tt) * np.exp(-tt / d) for f, a, d in ((59.0, 0.55, 0.58), (118.0, 0.72, 0.92), (177.0, 0.52, 0.72), (312.0, 0.36, 0.50), (468.0, 0.16, 0.30))) * np.minimum(1.0, tt / 0.004)
        _mix(np.column_stack([sig * 0.92, np.roll(sig, int(0.004 * sr)) * 0.98]), t_sec, gain)

    def _brass_pad(t0: float, t1: float, freqs: tuple[float, ...], gain: float = 0.28, bright: float = 0.35, scoop: float = 0.0, cutoff_hz: float = 420.0) -> None:
        s0, s1 = max(0, int(round(t0 * sr))), min(n_samples, int(round(t1 * sr)))
        if s1 <= s0 + 16:
            return
        m, tt = s1 - s0, np.arange(s1 - s0, dtype=np.float64) / sr
        env = np.minimum(1.0, tt / 0.14) * np.minimum(1.0, (m / sr - tt) / 0.16)
        lfo = (1.0 + 0.0025 * np.sin(2.0 * np.pi * 4.6 * tt)) * (1.0 + scoop * np.exp(-tt / 0.08))
        left, right = np.zeros(m, dtype=np.float64), np.zeros(m, dtype=np.float64)
        for k, f0 in enumerate(freqs):
            ph_l, ph_r, w_k = 2.0 * np.pi * np.cumsum(f0 * lfo * 0.9985) / sr, 2.0 * np.pi * np.cumsum(f0 * lfo * 1.0015) / sr, (0.85 if k > 0 else 1.0)
            left += w_k * (np.sin(ph_l) + bright * (0.48 * np.sin(2.0 * ph_l) + 0.24 * np.sin(3.0 * ph_l)))
            right += w_k * (np.sin(ph_r) + bright * (0.48 * np.sin(2.0 * ph_r) + 0.24 * np.sin(3.0 * ph_r)))
        lp_sos = butter(3, min(0.95, float(cutoff_hz) / (0.5 * sr)), btype="lowpass", output="sos")
        left = sosfilt(lp_sos, left)
        right = sosfilt(lp_sos, right)
        norm = gain / max(1.0, len(freqs) * 0.85)
        buf[s0:s1, 0] += left * env * norm
        buf[s0:s1, 1] += right * env * norm

    def _cymbal_swell(t_peak: float, dur: float = 1.4, gain: float = 0.26) -> None:
        m = max(32, int(dur * sr))
        tt = np.arange(m, dtype=np.float64) / sr
        filt = sosfilt(butter(2, [3400.0 / (0.5 * sr), min(0.95, 11500.0 / (0.5 * sr))], btype="bandpass", output="sos"), rng.normal(0.0, 1.0, m))
        _mix(np.column_stack([filt * 0.9, np.roll(filt, 9) * 0.95]) * ((tt / dur) ** 2.4 * np.exp(-np.maximum(0.0, tt - 0.78 * dur) / 0.22))[:, None], max(0.0, t_peak - 0.75 * dur), gain)

    seen_vac, sections = False, []
    for mb in measured_beats:
        bid, act, role = str(mb["beat_id"]), int(mb.get("act") or 1), str(mb.get("role") or mb.get("beat_role") or "").lower()
        if (vac_bid and bid == vac_bid) or role == "silence_vacuum":
            sec, seen_vac = "silence_vacuum", True
        elif bid in climax_ids or (not climax_ids and act == 4 and (seen_vac or not vac_bid or role in ("climax", "eruption"))):
            sec = "act4_climax"
        elif bid in proud_ids or act >= 5:
            sec = "act5_proud"
        else:
            sec = "act1" if act == 1 else "act2_3"
        sections.append((mb, sec))

    climax_chords = ((73.42, 146.83, 174.61, 220.00), (58.27, 116.54, 146.83, 174.61), (65.41, 130.81, 164.81, 196.00), (73.42, 146.83, 174.61, 220.00), (55.00, 110.00, 138.59, 164.81), (73.42, 146.83, 185.00, 220.00))
    proud_chords = ((73.42, 146.83, 185.00, 220.00), (98.00, 146.83, 196.00, 246.94), (55.00, 110.00, 164.81, 220.00), (73.42, 146.83, 185.00, 293.66))
    act23_starts = [float(mb["start_sec"]) for mb, s in sections if s == "act2_3"]
    t23_0 = min(act23_starts) if act23_starts else 0.0
    t23_span = max(1.0, (max(float(mb["end_sec"]) for mb, s in sections if s == "act2_3") - t23_0) if act23_starts else 1.0)
    climax_bounds = [(float(mb["start_sec"]), float(mb["end_sec"])) for mb, s in sections if s == "act4_climax"]
    if climax_bounds:
        c_t0, c_t1 = climax_bounds[0][0], climax_bounds[-1][1]
        for k, chord in enumerate(climax_chords):
            _brass_pad(c_t0 + (c_t1 - c_t0) * (k / 6.0), c_t0 + (c_t1 - c_t0) * ((k + 1) / 6.0), chord, gain=0.52, bright=0.52, cutoff_hz=720.0)

    climax_idx = proud_idx = 0
    for idx_s, (mb, sec) in enumerate(sections):
        t0, t1 = float(mb["start_sec"]), float(mb["end_sec"])
        dur, role, deliv = max(0.05, t1 - t0), str(mb.get("role") or mb.get("beat_role") or "").lower(), str(mb.get("delivery_mode") or "").lower()
        if sec == "act1":
            if idx_s == 0:
                _bronze_drum(t0, gain=0.50)
                _war_drum(t0, gain=0.62, pitch_hz=68.0, punch=1.4)
            _brass_pad(t0, t1, (73.42, 110.00, 146.83), gain=0.22, bright=0.16, cutoff_hz=420.0)
            for t in np.arange(t0 + 0.77, max(t0 + 0.77, t1 - 0.12), 60.0 / 78.0):
                _war_drum(float(t), gain=0.36, pitch_hz=74.0)
        elif sec == "act2_3":
            is_whisper = deliv == "tense_whisper"
            _brass_pad(t0, t1, (73.42, 110.00, 174.61) if idx_s % 2 == 0 else (65.41, 110.00, 164.81), gain=0.14 if is_whisper else 0.24, bright=0.18 if is_whisper else 0.25, cutoff_hz=420.0)
            prog = float(np.clip((t0 - t23_0) / t23_span, 0.0, 1.0))
            step = 60.0 / (88.0 + 20.0 * prog)
            drum_scale = 0.50 if is_whisper else 1.0
            for k_step, t in enumerate(np.arange(t0, max(t0, t1 - 0.08), step)):
                _war_drum(float(t), gain=(0.40 if k_step % 2 == 0 else 0.25) * drum_scale, pitch_hz=80.0 if k_step % 2 == 0 else 96.0)
            if not is_whisper and (role in ("twist", "strategy", "mechanism") or deliv in ("urgent_escalation", "tactical_breakdown") or prog > 0.65):
                for r_i in range(8):
                    rt = max(t0, t1 - 1.15) + r_i * (1.05 / 8.0)
                    if rt < t1:
                        _war_drum(rt, gain=0.16 + 0.36 * (r_i / 7.0), pitch_hz=88.0, punch=0.7)
        elif sec == "silence_vacuum":
            s0, s1 = max(0, int(round(t0 * sr))), min(n_samples, int(round(t1 * sr)))
            if s1 > s0:
                ft = min(s1 - s0, int(0.06 * sr))
                if ft > 1:
                    buf[s0 : s0 + ft] *= np.linspace(1.0, 0.0, ft, dtype=np.float64)[:, None]
                buf[s0 + ft : s1] = 0.0
                r_dur = min(0.85, dur * 0.35)
                rm = max(32, int(round(r_dur * sr)))
                rtt = np.arange(rm, dtype=np.float64) / sr
                prog_r = rtt / max(1e-6, r_dur)
                rumble_bp = butter(3, [45.0 / (0.5 * sr), 160.0 / (0.5 * sr)], btype="bandpass", output="sos")
                timpani_src_l = rng.normal(0.0, 0.70, rm) * (0.65 + 0.35 * np.cos(2.0 * np.pi * (9.0 + 7.0 * prog_r) * rtt))
                timpani_src_r = rng.normal(0.0, 0.70, rm) * (0.65 + 0.35 * np.cos(2.0 * np.pi * (9.0 + 7.0 * prog_r) * rtt + 0.4))
                for k_roll in range(7):
                    k_idx = int(round((k_roll + 0.35) * (rm / 7.5)))
                    k_len = min(rm - k_idx, int(0.18 * sr))
                    if k_len > 8:
                        kt = np.arange(k_len, dtype=np.float64) / sr
                        stroke = np.sin(2.0 * np.pi * np.cumsum((56.0 + 2.5 * k_roll) * (1.0 + 0.8 * np.exp(-kt / 0.02))) / sr) * np.exp(-kt / 0.09)
                        w_stroke = 0.25 + 0.75 * (k_roll / 6.0)
                        timpani_src_l[k_idx : k_idx + k_len] += stroke * w_stroke
                        timpani_src_r[k_idx : k_idx + k_len] += stroke * w_stroke * 0.96
                r_rumble_l = sosfilt(rumble_bp, timpani_src_l)
                r_rumble_r = sosfilt(rumble_bp, timpani_src_r)
                r_rumble_l = (r_rumble_l / max(1e-6, float(np.max(np.abs(r_rumble_l))))) * 0.58
                r_rumble_r = (r_rumble_r / max(1e-6, float(np.max(np.abs(r_rumble_r))))) * 0.58
                air_bp = butter(2, [200.0 / (0.5 * sr), min(0.94, 1200.0 / (0.5 * sr))], btype="bandpass", output="sos")
                r_air = sosfilt(air_bp, rng.normal(0.0, 0.14, rm))
                r_env = (prog_r ** 2.2) * np.minimum(1.0, rtt / 0.04) * 0.42
                _mix(np.column_stack([(r_rumble_l + r_air) * r_env, (r_rumble_r + np.roll(r_air, 11)) * r_env]), t1 - r_dur)
        elif sec == "act4_climax":
            if climax_idx == 0:
                _brass_pad(t0, min(t1, t0 + 2.0), (36.71, 73.42, 110.00, 174.61, 293.66), gain=0.72, bright=0.65, scoop=0.018, cutoff_hz=720.0)
                _bronze_drum(t0, gain=0.78)
                _war_drum(t0, gain=0.88, pitch_hz=68.0, punch=1.5)
                _cymbal_swell(t0 + 0.18, dur=1.2, gain=0.40)
            for k_step, t in enumerate(np.arange(t0, max(t0, t1 - 0.05), 60.0 / 124.0)):
                _war_drum(float(t), gain=0.84 if k_step % 4 == 0 else 0.58, pitch_hz=74.0 if k_step % 2 == 0 else 92.0, punch=1.2)
                if k_step % 4 == 0:
                    _bronze_drum(float(t), gain=0.58)
            if idx_s + 1 < len(sections) and sections[idx_s + 1][1] != "act4_climax":
                _cymbal_swell(t1, dur=1.35, gain=0.34)
            climax_idx += 1
        elif sec == "act5_proud":
            is_last = idx_s == len(sections) - 1
            _brass_pad(t0, t1, proud_chords[-1] if is_last else proud_chords[proud_idx % len(proud_chords)], gain=0.40, bright=0.40, cutoff_hz=720.0)
            for k_step, t in enumerate(np.arange(t0, max(t0, t1 - 0.18), 60.0 / 92.0)):
                _war_drum(float(t), gain=0.54 if k_step % 2 == 0 else 0.34, pitch_hz=76.0)
                if k_step == 0:
                    _bronze_drum(float(t), gain=0.40)
            if is_last:
                _war_drum(max(t0, t1 - 0.16), gain=0.90, pitch_hz=66.0, punch=1.5)
                _bronze_drum(max(t0, t1 - 0.16), gain=0.68)
            proud_idx += 1

    buf = np.nan_to_num(buf, nan=0.0, posinf=0.0, neginf=0.0)
    pk = float(np.max(np.abs(buf))) if len(buf) else 0.0
    return (buf * (0.92 / pk) if pk > 0.92 else buf).astype(np.float32)


def _apply_vacuum_duck(vac_env: np.ndarray, s_vs: int, s_vz: int, s_zero_end: int) -> None:
    """Smoothly fade BGM into zero across `[s_vs, s_zero_end]` leaving risers untouched."""
    if s_vz > s_vs:
        vac_env[s_vs:s_vz] = np.cos(np.linspace(0.0, math.pi * 0.5, s_vz - s_vs, dtype=np.float32)) ** 2
    vac_env[s_vz:s_zero_end] = 0.0


def _build_bgm_and_sfx_bed(voice_buf: np.ndarray, measured_beats: list[dict[str, Any]], short_spec: dict[str, Any], work_dir: Path) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Build voice-sidechained BGM (heroic epic score or dual-BGM) and calibrated SFX bed."""
    n_samples = len(voice_buf)
    voice_active_rms = _compute_active_speech_rms(voice_buf)
    voice_active_db = 20.0 * math.log10(max(1e-8, voice_active_rms))
    ensure_warehouse_audio_assets()
    bgm_plan, by_id = dict(short_spec.get("bgm_plan") or {}), {str(b["beat_id"]): b for b in measured_beats}
    vac_spec = bgm_plan.get("silence_vacuum") or {}
    vac_bid = str(vac_spec.get("beat_id") or "")
    vb = by_id.get(vac_bid) if vac_bid else None
    v_pauses = [p for p in vb["parts"] if p["type"] == "pause"] if vb else []
    p_vac_start = float(v_pauses[0]["global_start_sec"]) if v_pauses else 0.0
    p_vac_end = float(v_pauses[0]["global_end_sec"]) if v_pauses else 0.0
    vac_env = np.ones(n_samples, dtype=np.float32)

    if str(bgm_plan.get("mode") or "") == "heroic_vietnam_epic":
        score = synthesize_heroic_epic_score(measured_beats, short_spec, n_samples, sr=TARGET_SR)
        climax_slices = [score[int(round(float(by_id[b]["start_sec"]) * TARGET_SR)) : int(round(float(by_id[b]["end_sec"]) * TARGET_SR))] for b in (str(x) for x in (bgm_plan.get("climax_beats") or [])) if b in by_id]
        ref_rms = max(1e-6, float(np.sqrt(np.mean((np.vstack(climax_slices) if climax_slices else score) ** 2))))
        speech_db, pause_db = float(bgm_plan.get("speech_level_db", HEROIC_SPEECH_DUCK_DB)), float(bgm_plan.get("pause_level_db", HEROIC_PAUSE_SWELL_DB))
        rel_duck = _compute_voice_sidechain_gain(voice_buf, n_samples, TARGET_SR, duck_db=(speech_db - pause_db))
        bgm_ducked = (score * (voice_active_rms / ref_rms)) * ((10.0 ** (pause_db / 20.0)) * rel_duck)[:, None]
        if vb:
            s_vs, s_ve = max(0, int(round(float(vb["start_sec"]) * TARGET_SR))), min(n_samples, int(round(float(vb["end_sec"]) * TARGET_SR)))
            r_dur = min(0.85, max(0.05, float(vb["end_sec"]) - float(vb["start_sec"])) * 0.35)
            s_riser = max(s_vs + 16, min(s_ve, s_ve - int(round(r_dur * TARGET_SR))))
            s_vz = min(s_riser, max(s_vs + 16, int(round((p_vac_start - 0.12) * TARGET_SR))) if p_vac_end > p_vac_start else s_vs + int(round(0.06 * TARGET_SR)))
            _apply_vacuum_duck(vac_env, s_vs, s_vz, s_riser)
    else:
        prim, sec_n = str(bgm_plan.get("primary_bgm") or "bgm_geopolitics_pulse.wav"), str(bgm_plan.get("secondary_bgm") or "bgm_forensic_noir_drone.wav")
        noir_loop, pulse_loop = _loop_bgm_seamless(BGM_DIR / sec_n, n_samples), _loop_bgm_seamless(BGM_DIR / prim, n_samples)
        noir_loop *= voice_active_rms / (float(np.sqrt(np.mean(noir_loop**2))) + 1e-8)
        pulse_loop *= voice_active_rms / (float(np.sqrt(np.mean(pulse_loop**2))) + 1e-8)
        pw, act_dyn = np.zeros(n_samples, dtype=np.float32), list(bgm_plan.get("act_dynamics") or [])
        if act_dyn:
            for seg in act_dyn:
                r_str = str(seg.get("beats", ""))
                if str(seg.get("bgm", "")) == prim and "-" in r_str and all(x in by_id for x in r_str.split("-", 1)):
                    b0, b1 = r_str.split("-", 1)
                    pw[max(0, int(round(by_id[b0]["start_sec"] * TARGET_SR))) : min(n_samples, int(round(by_id[b1]["end_sec"] * TARGET_SR)))] = 1.0
        else:
            pw[:] = 1.0
        bgm_raw = noir_loop * np.sqrt(np.clip(1.0 - pw, 0.0, 1.0))[:, None] + pulse_loop * np.sqrt(pw)[:, None]
        rel_duck = _compute_voice_sidechain_gain(voice_buf, n_samples, TARGET_SR, duck_db=(BGM_DUCK_SPEECH_DB - BGM_SWELL_PAUSE_DB))
        bgm_ducked = bgm_raw * ((10.0 ** (BGM_SWELL_PAUSE_DB / 20.0)) * rel_duck)[:, None]
        if vb and p_vac_end > p_vac_start:
            s_vs, s_ve = int(round(vb["start_sec"] * TARGET_SR)), int(round(vb["end_sec"] * TARGET_SR))
            _apply_vacuum_duck(vac_env, s_vs, max(s_vs + 16, int(round((p_vac_start - 0.12) * TARGET_SR))), s_ve)

    fi, fo = min(n_samples // 10, int(0.25 * TARGET_SR)), min(n_samples // 10, int(0.35 * TARGET_SR))
    if fi > 1:
        vac_env[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)
    if fo > 1:
        vac_env[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)
    bgm_final = bgm_ducked * vac_env[:, None]

    sfx_buf, est_by_id, placed_events, bespoke_cache = np.zeros((n_samples, 2), dtype=np.float32), {str(b["beat_id"]): b for b in short_spec["beats"]}, [], {}
    for cue in short_spec.get("sfx_cues") or []:
        bid = str(cue["beat_id"])
        if bid not in by_id or bid not in est_by_id:
            continue
        mb, eb, stem_name = by_id[bid], est_by_id[bid], str(cue["stem"])
        est_dur = max(0.1, float(eb.get("duration_sec") or eb.get("duration") or 4.0))
        if cue.get("is_bespoke") or cue.get("bespoke_sfx_spec"):
            if stem_name not in bespoke_cache:
                b_out = work_dir / stem_name
                synthesize_bespoke_topic_sfx(dict(cue.get("bespoke_sfx_spec") or {"profile": "historical_resonance", "topic": stem_name, "freq_hz": 118.0, "dur": 1.65}), output_path=b_out)
                bespoke_cache[stem_name] = b_out
            stem_path = bespoke_cache[stem_name]
        else:
            stem_path = SFX_DIR / stem_name
        if not stem_path.is_file():
            raise FileNotFoundError(f"Missing SFX stem: {stem_path}")
        stem = _ensure_stereo(_read_wav_stereo(stem_path, target_sr=TARGET_SR))
        if bid == vac_bid and stem_name == str(vac_spec.get("heartbeat_stem") or "heartbeat_lub_dub.wav") and p_vac_end > p_vac_start:
            placed_at = max(0.0, 0.5 * (p_vac_start + p_vac_end) - 0.295)
        elif bid == vac_bid and stem_name == "night_rain_soft.wav":
            placed_at, stem = float(mb["start_sec"]), stem[: min(len(stem), int(round(mb["duration_sec"] * TARGET_SR)))].copy()
        else:
            placed_at = float(mb["start_sec"]) + float(cue.get("offset_sec", 0.1)) * (float(mb["duration_sec"]) / est_dur)
        nom_g = float(cue.get("gain", 0.8))
        if bid == vac_bid and stem_name == "heartbeat_lub_dub.wav":
            stem_rms, t_db = _stem_active_rms(stem, "rms"), HEARTBEAT_VACUUM_DB
        elif stem_name == "night_rain_soft.wav":
            stem_rms, t_db = _stem_active_rms(stem, "rms"), RAIN_VACUUM_DB if bid == vac_bid else float(np.clip(RAIN_VACUUM_DB + 2.0 * (nom_g - 0.45), -26.0, -22.5))
        elif stem_name in ("card_lock_thud.wav", "whoosh_soft.wav", "ding_insight.wav"):
            stem_rms, t_db = _stem_active_rms(stem, "transient"), float(np.clip(-15.5 + 3.0 * (nom_g - 0.72), -17.5, -13.5))
        else:
            stem_rms, t_db = _stem_active_rms(stem, "rms"), float(np.clip(-14.5 + 3.5 * (nom_g - 0.90), -16.5, -13.0))
        stem_cal = stem * float((voice_active_rms * (10.0 ** (t_db / 20.0))) / max(1e-8, stem_rms))
        cur_pk, max_pk = (float(np.max(np.abs(stem_cal))) if len(stem_cal) else 0.0), voice_active_rms * 1.15
        if cur_pk > max_pk and not (bid == vac_bid and stem_name == "heartbeat_lub_dub.wav"):
            stem_cal *= max_pk / cur_pk
        raw_offset_sec = float(cue.get("offset_sec", 0.1))
        rel_beat_offset = placed_at - float(mb["start_sec"])
        early_attenuated = bid != vac_bid and (raw_offset_sec < 0.28 or rel_beat_offset < 0.30)
        if early_attenuated:
            stem_cal *= 0.67
            t_db -= 3.5
        place_stereo_sfx(sfx_buf, stem_cal, start_sec=placed_at, pan=float(cue.get("pan", 0.0)), gain=1.0, sr=TARGET_SR)
        placed_events.append({"beat_id": bid, "stem": stem_name, "placed_at_sec": round(placed_at, 4), "target_rel_voice_db": round(t_db, 2), "early_beat_ducked": early_attenuated})

    return bgm_final, sfx_buf, {"voice_active_rms_db": round(voice_active_db, 2), "placed_events": placed_events}


def _partition_phrase_clause(clause: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """Partition a clause into readable 2–4 syllable phrase chunks (5 -> 3+2, avoiding 1-word tails)."""
    chunks: list[list[dict[str, Any]]] = []
    i, n = 0, len(clause)
    while i < n:
        r = n - i
        if r <= 3:
            k = r
        elif r == 4:
            k = 4 if sum(len(x["_clean"]) for x in clause[i : i + 4]) <= 22 else 2
        elif r == 5:
            k = 3
        elif r == 6:
            k = 3
        elif r == 7:
            k = 4 if sum(len(x["_clean"]) for x in clause[i : i + 4]) <= 22 else 3
        else:
            k = 3
        chunks.append(clause[i : i + k])
        i += k
    return chunks


def _group_words_into_phrases(words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group consecutive words of the same `(beat_id, seg_idx)` into meaningful 2–4 word phrases."""
    segments: list[tuple[tuple[str, int], list[dict[str, Any]]]] = []
    for w in words:
        raw = str(w.get("word", "")).strip().replace("{", "").replace("}", "")
        clean = re.sub(r"^[.,;:!?\"'“”‘’()\[\]]+|[.,;:!?\"'“”‘’()\[\]]+$", "", raw)
        if not clean:
            continue
        item = {
            **w,
            "_clean": clean,
            "_ends_punct": bool(re.search(r"[,.;:!?…—–][\"'”’)\]]*$", raw)),
            "_emphatic": bool(re.search(r"[!?][\"'”’)\]]*$", raw)),
            "_colon_end": bool(re.search(r":[\"'”’)\]]*$", raw)),
        }
        seg_key = (str(w.get("beat_id", "")), int(w.get("seg_idx", 0)))
        if not segments or segments[-1][0] != seg_key:
            segments.append((seg_key, [item]))
        else:
            segments[-1][1].append(item)

    phrase_records: list[dict[str, Any]] = []
    for seg_key, seg_words in segments:
        clauses: list[list[dict[str, Any]]] = []
        cur_clause: list[dict[str, Any]] = []
        for item in seg_words:
            cur_clause.append(item)
            if item["_ends_punct"]:
                clauses.append(cur_clause)
                cur_clause = []
        if cur_clause:
            clauses.append(cur_clause)

        raw_chunks: list[tuple[int, list[dict[str, Any]]]] = []
        for cl_idx, clause in enumerate(clauses):
            for ch in _partition_phrase_clause(clause):
                raw_chunks.append((cl_idx, ch))

        # Rebalance/merge any single-word trailing/leading chunk inside a multi-word segment
        fixed: list[tuple[int, list[dict[str, Any]]]] = []
        for cl_idx, ch in raw_chunks:
            if len(ch) == 1 and fixed:
                prev_cl, prev_ch = fixed[-1]
                if len(prev_ch) <= 3:
                    prev_ch.extend(ch)
                else:
                    combined = prev_ch + ch
                    fixed[-1] = (prev_cl, combined[:3])
                    fixed.append((cl_idx, combined[3:]))
            else:
                fixed.append((cl_idx, ch))
        if len(fixed) >= 2 and len(fixed[0][1]) == 1:
            first_cl, first_ch = fixed[0]
            nxt_cl, nxt_ch = fixed[1]
            if len(nxt_ch) <= 3:
                fixed[1] = (nxt_cl, first_ch + nxt_ch)
                fixed.pop(0)
            else:
                combined = first_ch + nxt_ch
                fixed[0] = (first_cl, combined[:2])
                fixed[1] = (nxt_cl, combined[2:])

        for cl_idx, ch in fixed:
            emphatic = any(x["_emphatic"] for x in ch)
            phrase_records.append({
                "seg_key": seg_key,
                "clause_idx": cl_idx,
                "words": ch,
                "text": " ".join(x["_clean"] for x in ch),
                "start": float(ch[0]["start"]),
                "end": float(ch[-1]["end"]),
                "seg_end": float(ch[-1].get("seg_end", ch[-1]["end"])),
                "emphatic": emphatic,
            })
    return phrase_records


def write_short_kinetic_ass_2k(words: list[dict[str, Any]], total_duration: float, out_ass: Path) -> Path:
    """Write 2K phrase-grouped kinetic ASS subtitles (`Noto Sans,132`, outline 8, shadow 5, MarginV=470)."""
    ass_lines = [
        "[Script Info]", "ScriptType: v4.00+", "PlayResX: 1440", "PlayResY: 2560", "WrapStyle: 2", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: KineticRed,Noto Sans,{VIETSUB_FONT_SIZE},{KINETIC_RED_ASS},{KINETIC_RED_ASS},&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,8,5,2,60,60,470,1",
        f"Style: KineticYellow,Noto Sans,{VIETSUB_FONT_SIZE},{KINETIC_YELLOW_ASS},{KINETIC_YELLOW_ASS},&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,8,5,2,60,60,470,1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    phrases = _group_words_into_phrases(words)
    for idx, ph in enumerate(phrases):
        ws = max(0.0, float(ph["start"]))
        we = float(ph["end"])
        se = float(ph.get("seg_end", total_duration))
        if idx + 1 < len(phrases):
            next_ws = float(phrases[idx + 1]["start"])
            we = min(next_ws, se + 0.04, max(we, we + 0.08))
        else:
            we = min(total_duration, se + 0.05, max(we, we + 0.08))
        we = min(total_duration, we)
        if we <= ws + 0.02:
            we = min(total_duration, ws + 0.05)
        style = "KineticRed" if ph["emphatic"] else "KineticYellow"
        if ph["text"]:
            ass_lines.append(f"Dialogue: 0,{_fmt_ass_ts(ws)},{_fmt_ass_ts(we)},{style},,0,0,0,,{ph['text']}")
    out_ass.parent.mkdir(parents=True, exist_ok=True)
    out_ass.write_text("\n".join(ass_lines) + "\n", encoding="utf-8")
    return out_ass


def slice_ass_for_window(ass_path: Path, start_sec: float, end_sec: float, out_ass: Path) -> Path:
    """Slice ASS subtitles to `[start_sec, end_sec)` shifting timestamps to `[0, end_sec - start_sec]`."""
    if end_sec <= start_sec:
        raise ValueError(f"Invalid ASS slice window: [{start_sec}, {end_sec})")
    win_dur, header_lines, dialogue_lines, in_events = end_sec - start_sec, [], [], False
    for line in ass_path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s == "[Events]":
            in_events = True
            header_lines.append(line)
        elif in_events and s.startswith("Dialogue:"):
            parts = s[len("Dialogue:") :].lstrip().split(",", 9)
            if len(parts) < 10:
                continue
            ev_s, ev_e = _parse_ass_ts(parts[1]), _parse_ass_ts(parts[2])
            if ev_e <= start_sec or ev_s >= end_sec:
                continue
            rel_s, rel_e = max(0.0, max(ev_s, start_sec) - start_sec), min(win_dur, min(ev_e, end_sec) - start_sec)
            if rel_e - rel_s < 0.02:
                if rel_s + 0.02 <= win_dur:
                    rel_e = rel_s + 0.02
                elif rel_e - 0.02 >= 0.0:
                    rel_s = rel_e - 0.02
                else:
                    continue
            parts[1], parts[2] = _fmt_ass_ts(rel_s), _fmt_ass_ts(rel_e)
            dialogue_lines.append("Dialogue: " + ",".join(parts))
        elif not in_events or s.startswith("Format:"):
            header_lines.append(line)
    out_ass.parent.mkdir(parents=True, exist_ok=True)
    out_ass.write_text("\n".join(header_lines + dialogue_lines) + "\n", encoding="utf-8")
    return out_ass


def run_audio_stage(short_spec: dict[str, Any], spec_dir: Path, work_root: Path, *, colab_tts_workers: int = 3) -> dict[str, Any]:
    """Synthesize speech segments on Colab T4, sculpt cinema prosody, mix BGM/SFX, and emit timings."""
    t0 = time.monotonic()
    channel_id, job_id = str(short_spec["channel_id"]), str(short_spec["job_id"])
    profile = load_voice_profile(channel_id, root=ROOT_DIR)
    ref_wav = SYS_DIR / "assets/voices" / f"ch_{channel_id}" / "reference.wav"
    if not ref_wav.is_file():
        raise FileNotFoundError(f"Missing voice reference WAV: {ref_wav}")
    if profile.get("sha256") and hashlib.sha256(ref_wav.read_bytes()).hexdigest() != profile["sha256"]:
        raise RuntimeError(f"Voice reference sha256 mismatch for {channel_id}")
    source_speed = float(profile.get("source_speed", 1.0))

    raw_dir, post_dir = work_root / "audio_work" / "raw_wavs", work_root / "audio_work" / "post_wavs"
    raw_dir.mkdir(parents=True, exist_ok=True)
    post_dir.mkdir(parents=True, exist_ok=True)

    all_items: list[dict[str, Any]] = []
    g_idx = 0
    for b in short_spec["beats"]:
        bid, omni_speed = str(b["beat_id"]), float(_beat_voice_params(b)["omni_speed"])
        parts = [p for p in split_text_with_pauses(b["tts_text"]) if p["type"] == "speech"]
        if not parts:
            raise RuntimeError(f"Beat {bid} has no speech segments")
        for seg_idx, sp in enumerate(parts):
            stxt = sp["text"].strip()
            if "[pause:" in stxt.lower() or re.search(r"\d", stxt) or detect_unnormalized_tokens(stxt):
                raise ValueError(f"Invalid TTS text on {bid}_seg{seg_idx:02d}: {stxt}")
            all_items.append({"index": g_idx, "key": f"{bid}_seg{seg_idx:02d}", "beat_id": bid, "seg_idx": seg_idx, "tts_text": stxt, "omni_speed": round(omni_speed / source_speed, 4), "syllables": len(stxt.split())})
            g_idx += 1

    missing = [it for it in all_items if not _utterance_ok(raw_dir / f"{it['key']}.wav", it["syllables"])]
    if missing:
        _run_colab_tts_shards(missing, channel_id=channel_id, ref_wav=ref_wav, ref_text=profile["reference_text"], base_speed=float(short_spec.get("base_omnivoice_speed", 1.06)), raw_dir=raw_dir, max_workers=colab_tts_workers)
    still_bad = [it["key"] for it in all_items if not _utterance_ok(raw_dir / f"{it['key']}.wav", it["syllables"])]
    if still_bad:
        raise RuntimeError(f"Invalid/missing synthesized WAVs: {still_bad}")

    assembled: list[dict[str, Any]] = []
    for b in short_spec["beats"]:
        res = _assemble_single_beat(b, raw_dir=raw_dir, post_dir=post_dir)
        for _ in range(3):
            if res["duration_sec"] <= MAX_BEAT_DURATION_SEC:
                break
            speech_target = max(0.30, 5.56 - (res["pause_sec"] + res["gap_after_sec"]))
            new_at = min(ATEMPO_MAX, max(ATEMPO_MIN, round(res["atempo_used"] * (max(0.30, res["speech_duration_sec"]) / speech_target), 4)))
            if abs(new_at - res["atempo_used"]) < 1e-4:
                break
            res = _assemble_single_beat(b, raw_dir=raw_dir, post_dir=post_dir, atempo_override=new_at)
        assembled.append(res)

    voice_buf = np.vstack([r["waveform"] for r in assembled])
    _write_wav_stereo(work_root / "narration_voice_only.wav", voice_buf, sr=TARGET_SR)

    measured_beats, short_words, cur_sample = [], [], 0
    for idx_b, (b, r) in enumerate(zip(short_spec["beats"], assembled, strict=True)):
        b_start, cur_sample = round(cur_sample / float(TARGET_SR), 6), cur_sample + r["n_samples"]
        b_end = round(cur_sample / float(TARGET_SR), 6)
        for part in r["parts"]:
            part["global_start_sec"], part["global_end_sec"] = round(b_start + part["local_start_sec"], 6), round(b_start + part["local_end_sec"], 6)
            if part["type"] == "speech":
                for w in _extract_segment_words_acoustic(part["waveform"], part["text"], global_offset=part["global_start_sec"]):
                    w.update({"beat_id": b["beat_id"], "seg_idx": part["seg_idx"]})
                    short_words.append(w)
        vp = _beat_voice_params(b)
        measured_beats.append({
            "index": idx_b, "beat_id": str(b["beat_id"]), "act": b.get("act"), "role": b.get("role") or b.get("beat_role"),
            "delivery_mode": b.get("delivery_mode"), "omni_speed": float(vp["omni_speed"]), "atempo_spec": float(vp["atempo"]),
            "atempo_used": r["atempo_used"], "micro_gain_db": r["micro_gain_db"], "gap_after_sec": r["gap_after_sec"],
            "pause_sec": r["pause_sec"], "display_text": b["display_text"], "tts_text": b["tts_text"],
            "speech_duration_sec": r["speech_duration_sec"], "duration_sec": round(b_end - b_start, 6),
            "start_sec": b_start, "end_sec": b_end, "parts": r["parts"], "segments": [{k: v for k, v in p.items() if k != "waveform"} for p in r["parts"]],
        })

    bgm_buf, sfx_buf, mix_diag = _build_bgm_and_sfx_bed(voice_buf, measured_beats, short_spec, work_root)
    pre_mix = voice_buf + bgm_buf + sfx_buf
    max_pk = float(np.max(np.abs(pre_mix))) if len(pre_mix) else 0.0
    if max_pk > 0.88:
        pre_mix = pre_mix * (0.88 / max_pk)

    short_master = spec_dir / "narration_master.wav"
    _write_wav_stereo(short_master, pre_mix, sr=TARGET_SR)
    master_ebur = polish_lufs_true_peak(short_master, target_lufs=-11.0, max_tp_db=-1.0, tp_guard_margin_db=0.25)
    with wave.open(str(short_master), "rb") as mwf:
        short_dur = round(mwf.getnframes() / float(TARGET_SR), 6)

    clean_beats = [{k: v for k, v in mb.items() if k != "parts"} for mb in measured_beats]
    (spec_dir / "audio_timings.json").write_text(
        json.dumps({
            "job_id": job_id, "total_duration_sec": short_dur, "bgm_mix_enabled": True,
            "master_lufs": master_ebur["integrated_lufs"], "master_true_peak_dbtp": master_ebur["true_peak_dbtp"],
            "ebur128": master_ebur, "mix_diagnostics": {k: v for k, v in mix_diag.items() if k != "placed_events"},
            "sfx_events_placed": mix_diag["placed_events"], "beats": clean_beats, "words": short_words,
        }, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    ass_path = write_short_kinetic_ass_2k(short_words, short_dur, work_root / "subtitles_kinetic_2k.ass")
    srt_path = build_clean_sidecar_srt(short_spec["beats"], [b["duration_sec"] for b in clean_beats], short_dur, spec_dir / "subtitles.srt")

    s_lint = spec_dir / "_work_short" / "lint"
    if (s_lint / "brief.json").is_file() and (s_lint / "content.json").is_file():
        s_brief = json.loads((s_lint / "brief.json").read_text(encoding="utf-8"))
        s_brief["estimated_duration_sec"] = short_dur
        s_content = json.loads((s_lint / "content.json").read_text(encoding="utf-8"))
        for sc, tm in zip(s_content["scenes"], clean_beats, strict=True):
            sc["start"], sc["end"], sc["duration"] = tm["start_sec"], tm["end_sec"], tm["duration_sec"]
        last_b, cta_plan = clean_beats[-1], short_spec.get("cta_plan") or {}
        b_syl, c_syl = max(1, len(str(cta_plan.get("bridge", "")).split())), max(1, len(str(cta_plan.get("close", "")).split()))
        cta_errs = lint_cta(s_brief, s_content, timings={"total_duration": short_dur, "bridge_start": last_b["start_sec"], "close_start": round(last_b["start_sec"] + last_b["duration_sec"] * (b_syl / float(b_syl + c_syl)), 4)})
        vp_errs = check_see_say_beat_density(s_content["scenes"], format_profile="serialized_detail_short")
        if cta_errs or vp_errs:
            raise RuntimeError(f"Post-TTS lint failed: cta={cta_errs}, visual_pacing={vp_errs}")

    return {"status": "completed", "elapsed_sec": round(time.monotonic() - t0, 2), "short_duration_sec": short_dur, "master_ebur128": master_ebur, "short_ass": str(ass_path), "short_srt": str(srt_path), "master_wav": str(short_master)}
