#!/usr/bin/env python3
"""Video Pilot — High-Speed Long Explainer TTS Synthesizer & Masterer on Colab Tesla T4.

Synthesizes full 240-350 beat Long explainer audio using authentic Studio V3 Human Voice
clones (OmniVoice on Colab Tesla T4 GPU), masters to -11.0 LUFS / -1.0 dBTP, and aligns
beat durations, sidecar subtitles.srt, and FFMETADATA1 chapters.
"""

from __future__ import annotations

import argparse
import copy
import json
import logging
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Tuple

SYS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = SYS_DIR.parent
for _p in (str(ROOT_DIR), str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from colab_bridge.client import Client
from tools.produce_vn_dual_mode import (
    BANNED_DEPRECATED_VOICE_SHA256S,
    HARDCODED_CHANNEL_VOICE_LOCKS,
    SU_KE_LAI_SHARED_VOICE_SHA256,
    load_voice_profile,
    verify_channel_voice_lock,
)
from tools.vn_text_normalizer import normalize_for_tts

__all__ = [
    "BANNED_DEPRECATED_VOICE_SHA256S",
    "HARDCODED_CHANNEL_VOICE_LOCKS",
    "SU_KE_LAI_SHARED_VOICE_SHA256",
    "load_voice_profile",
    "synthesize_long_channel",
    "verify_channel_voice_lock",
]

ROOT = ROOT_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("synthesize_vn_long_omnivoice")


def resolve_channel_ids(raw_id: str) -> Tuple[str, str]:
    clean = raw_id.strip()
    if clean.startswith("channel-"):
        clean = clean[len("channel-"):]
    if clean.startswith("ch_"):
        clean = clean[len("ch_"):]
    channel_id = clean.replace("-", "_")
    channel_slug = clean.replace("_", "-")
    return channel_id, channel_slug


def format_srt_time(sec: float) -> str:
    total_ms = int(round(sec * 1000))
    hours = total_ms // 3600000
    remainder = total_ms % 3600000
    minutes = remainder // 60000
    remainder = remainder % 60000
    seconds = remainder // 1000
    millis = remainder % 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


REMOTE_WORKER_SCRIPT = """
import os, sys, json, time, wave
import numpy as np
import soundfile as sf
import torch
from huggingface_hub import snapshot_download
from omnivoice import OmniVoice
from scipy.signal import butter, resample_poly, sosfiltfilt

SR = 48000

def _strip_leading_prompt_bleed(w, sr=SR):
    hop = max(1, sr // 100)
    nf = len(w) // hop
    if nf < 45:
        return w
    rms = np.sqrt(np.mean(w[: nf * hop].reshape(nf, hop) ** 2, axis=1))
    sample_idx = np.where(np.abs(w) >= 0.010)[0]
    if not len(sample_idx):
        return w
    b_start = int(sample_idx[0]) // hop
    if b_start > 15:
        return w
    for g_start in range(b_start + 1, min(b_start + 7, nf - 22)):
        if rms[g_start] < 0.008:
            if float(np.max(rms[b_start:g_start])) >= 0.035:
                return w
            cut_idx = int(np.where(np.abs(w[g_start * hop :]) >= 0.010)[0][0]) + g_start * hop
            fade = min(round(0.010 * sr), len(w) - cut_idx)
            trimmed = w[cut_idx:].copy()
            if fade > 0:
                trimmed[:fade] *= np.linspace(0.0, 1.0, fade, dtype=np.float32)
            return trimmed
    return w

def _trim_silence(w, sr=SR, threshold=0.008, lead_ms=35, trail_ms=45, fade_ms=10):
    w = np.asarray(w, dtype=np.float32).reshape(-1)
    if not w.size:
        return w
    w = _strip_leading_prompt_bleed(w, sr=sr)
    idx = np.where(np.abs(w) >= threshold)[0]
    if not idx.size:
        return w
    soft_coda = np.where(np.abs(w[int(idx[-1]) : min(len(w), int(idx[-1]) + round(0.09 * sr))]) >= min(threshold, 0.006))[0]
    last_voiced = int(idx[-1]) + (int(soft_coda[-1]) if soft_coda.size else 0)
    lead = round(lead_ms * sr / 1000)
    trail = round(trail_ms * sr / 1000)
    start = max(0, int(idx[0]) - lead)
    end = min(len(w), last_voiced + 1 + trail)
    trimmed = w[start:end].copy()
    fade = min(round(fade_ms * sr / 1000), len(trimmed) // 4)
    if fade > 0:
        trimmed[:fade] *= np.linspace(0.0, 1.0, fade, dtype=np.float32)
        trimmed[-fade:] *= np.linspace(1.0, 0.0, fade, dtype=np.float32)
    return trimmed

def synthesize_batch_job(ref_wav_path, payload_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(payload_path, 'r', encoding='utf-8') as f:
        payload = json.load(f)

    global model
    if 'model' not in globals() or model is None:
        print('Loading OmniVoice on Colab...')
        local = snapshot_download('kjanh/KhanhTTS-OmniVoice', revision='20d056b8ea5d8d578b4cbaf1f703012fa3798a84')
        model = OmniVoice.from_pretrained(local, device_map='cuda:0', dtype=torch.float16)

    ref_text = payload['ref_text']
    speed = float(payload.get('speed', 1.0))
    batch_size = int(payload.get('batch_size', 8))
    num_step = int(payload.get('num_step', 32))
    gap_sec = float(payload.get('gap_sec', 0.22))
    gap_samples = round(gap_sec * SR)

    print(f'Creating prompt for {ref_wav_path}...')
    t0 = time.time()
    prompt = model.create_voice_clone_prompt(ref_audio=ref_wav_path, ref_text=ref_text)
    print(f'Prompt created in {time.time()-t0:.2f}s')

    sos = butter(2, 85.0 / (SR * 0.5), btype='highpass', output='sos')

    all_pieces = []
    beat_meta = []

    if 'sentence_groups' in payload and payload['sentence_groups']:
        sentence_groups = payload['sentence_groups']
        total_groups = len(sentence_groups)
        total_beats = sum(len(g.get('beats', [])) for g in sentence_groups)
        print(f'Synthesizing {total_groups} sentence groups ({total_beats} beats) in batches of {batch_size}...')

        t_start = time.time()
        for g_idx in range(0, total_groups, batch_size):
            chunk_groups = sentence_groups[g_idx : g_idx + batch_size]
            texts = [g['text'] for g in chunk_groups]

            t_batch0 = time.time()
            gen = model.generate(
                text=texts,
                language=['vi'] * len(chunk_groups),
                voice_clone_prompt=[prompt] * len(chunk_groups),
                speed=[speed] * len(chunk_groups),
                num_step=num_step
            )
            batch_sec = time.time() - t_batch0

            for item_idx, raw_w in enumerate(gen):
                g_info = chunk_groups[item_idx]
                arr = np.asarray(raw_w, dtype=np.float32).reshape(-1)
                arr = resample_poly(arr, 2, 1).astype(np.float32)  # 24k -> 48k
                if len(arr) >= 32:
                    arr = sosfiltfilt(sos, arr).astype(np.float32)
                pk = float(np.max(np.abs(arr)))
                if pk > 0.89:
                    arr *= (0.89 / pk)
                arr = _trim_silence(arr, sr=SR)
                if not arr.size:
                    arr = np.zeros(int(SR * 0.2), dtype=np.float32)

                group_content_dur = len(arr) / float(SR)
                group_total_dur = (len(arr) + gap_samples) / float(SR)

                all_pieces.append(arr)
                all_pieces.append(np.zeros(gap_samples, dtype=np.float32))

                beats_in_group = g_info.get('beats', [])
                tot_words = sum(b.get('word_count', 1) for b in beats_in_group)
                accum_tot = 0.0
                accum_cont = 0.0

                for b_i, b_in in enumerate(beats_in_group):
                    wc = b_in.get('word_count', 1)
                    ratio = wc / float(tot_words) if tot_words > 0 else (1.0 / len(beats_in_group))
                    if b_i < len(beats_in_group) - 1:
                        b_tot = round(group_total_dur * ratio, 4)
                        b_cont = round(group_content_dur * ratio, 4)
                        accum_tot += b_tot
                        accum_cont += b_cont
                    else:
                        b_tot = round(group_total_dur - accum_tot, 4)
                        b_cont = round(group_content_dur - accum_cont, 4)

                    beat_meta.append({
                        'beat_id': b_in['id'],
                        'text': b_in['text'],
                        'content_duration': b_cont,
                        'total_duration': b_tot,
                    })

            print(f'  Progress: {min(g_idx + batch_size, total_groups)}/{total_groups} groups ({batch_sec:.2f}s/batch)')

        print(f'All {total_groups} sentence groups ({total_beats} beats) generated in {time.time()-t_start:.2f}s')

    else:
        beats = payload.get('beats', [])
        total_beats = len(beats)
        print(f'Synthesizing {total_beats} beats in batches of {batch_size}...')

        t_start = time.time()
        for b_idx in range(0, total_beats, batch_size):
            chunk = beats[b_idx:b_idx + batch_size]
            texts = [b['text'] for b in chunk]

            t_batch0 = time.time()
            gen = model.generate(
                text=texts,
                language=['vi'] * len(chunk),
                voice_clone_prompt=[prompt] * len(chunk),
                speed=[speed] * len(chunk),
                num_step=num_step
            )
            batch_sec = time.time() - t_batch0

            for item_idx, raw_w in enumerate(gen):
                arr = np.asarray(raw_w, dtype=np.float32).reshape(-1)
                arr = resample_poly(arr, 2, 1).astype(np.float32) # 24k -> 48k
                if len(arr) >= 32:
                    arr = sosfiltfilt(sos, arr).astype(np.float32)
                pk = float(np.max(np.abs(arr)))
                if pk > 0.89:
                    arr *= (0.89 / pk)
                arr = _trim_silence(arr, sr=SR)
                dur = len(arr) / float(SR)

                beat_info = chunk[item_idx]
                beat_meta.append({
                    'beat_id': beat_info['id'],
                    'text': beat_info['text'],
                    'content_duration': round(dur, 4),
                    'total_duration': round(dur + gap_sec, 4)
                })

                all_pieces.append(arr)
                all_pieces.append(np.zeros(gap_samples, dtype=np.float32))

            print(f'  Progress: {min(b_idx + batch_size, total_beats)}/{total_beats} beats ({batch_sec:.2f}s/batch)')

        print(f'All {total_beats} beats generated in {time.time()-t_start:.2f}s')

    master_arr = np.concatenate(all_pieces) if all_pieces else np.zeros(SR, dtype=np.float32)
    raw_master_path = os.path.join(out_dir, 'raw_narration.wav')
    sf.write(raw_master_path, master_arr, SR, subtype='PCM_16')

    meta_path = os.path.join(out_dir, 'metadata.json')
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total_duration': round(len(master_arr) / float(SR), 4),
            'beats': beat_meta
        }, f, ensure_ascii=False, indent=2)

    print(f'Successfully wrote {raw_master_path} and {meta_path}')
"""


def synthesize_long_channel(
    channel_arg: str,
    spec_path_arg: Optional[str] = None,
    out_dir_arg: Optional[str] = None,
    account: str = "account-05",
    session: str = "vp-vn-long-1794089419",
    batch_size: int = 8,
    num_step: int = 32,
    target_lufs: float = -11.0,
    target_peak: float = -1.0,
) -> Path:
    channel_id, channel_slug = resolve_channel_ids(channel_arg)
    logger.info(f"=== Synthesizing Long Explainer Audio for {channel_id} ({channel_slug}) on Colab T4 OmniVoice ===")

    # 1. Voice profile resolution
    profile = load_voice_profile(channel_id, root=ROOT)
    voice_dir = SYS_DIR / f"assets/voices/ch_{channel_id}"
    ref_wav = voice_dir / profile.get("reference_wav", "reference.wav")
    if not ref_wav.is_file():
        raise FileNotFoundError(f"Missing reference wav: {ref_wav}")
    ref_text = profile["reference_text"]
    recommended_speed = float(profile.get("recommended_speed", 1.0))
    voice_chain = profile.get("audio_voice_chain") or "highpass=f=85,equalizer=f=190:t=q:w=1.2:g=-2.0,equalizer=f=3000:t=q:w=1.2:g=1.4,lowpass=f=13500"

    # 2. Spec resolution (prefer canonical repo master specs first)
    if spec_path_arg and Path(spec_path_arg).is_file():
        spec_p = Path(spec_path_arg)
    else:
        cands = [
            SYS_DIR / f"channels/vn_rebuilt_style_specs/{channel_slug}/{channel_slug}_long_305_master_spec.json",
            SYS_DIR / f"channels/vn_rebuilt_style_specs/{channel_slug}/{channel_slug}_long_310_master_spec.json",
            SYS_DIR / f"channels/vn_rebuilt_style_specs/{channel_slug}/{channel_slug}_long_master_spec.json",
            ROOT_DIR / f"video/vn_pilot_{channel_id}_long_305/{channel_id}_long_305_aligned_spec.json",
            ROOT_DIR / f"video/vn_pilot_{channel_id}_long_310/{channel_id}_long_310_aligned_spec.json",
        ]
        spec_p = None
        for c in cands:
            if c.is_file():
                spec_p = c
                break
        if not spec_p:
            raise FileNotFoundError(f"Cannot find long spec for channel {channel_slug}")

    logger.info(f"Loading spec: {spec_p}")
    spec = json.loads(spec_p.read_text(encoding="utf-8"))
    beats = spec.get("beats", spec.get("visual_states", []))
    if not beats:
        raise ValueError(f"Spec has 0 beats: {spec_p}")

    # Set up output directories
    if out_dir_arg:
        out_dir = Path(out_dir_arg)
    else:
        out_dir = ROOT_DIR / f"video/vn_pilot_{channel_id}_long"
    out_dir.mkdir(parents=True, exist_ok=True)
    work_dir = out_dir / "_work_long"
    work_dir.mkdir(parents=True, exist_ok=True)

    # 3. Prepare payload
    # Normalize narration in-place for all beats first
    for b in beats:
        raw_narr = (b.get("narration") or "").strip()
        norm_narr = normalize_for_tts(raw_narr)
        b["narration"] = norm_narr

    # Group consecutive beats into sentence_groups
    has_anchor_ids = any(re.match(r"^(CH\d+_A\d+)", (b.get("beat_id") or b.get("id") or "")) for b in beats)

    grouped_raw_beats = []
    if has_anchor_ids:
        current_prefix = None
        current_group = []
        for b in beats:
            b_id = b.get("beat_id") or b.get("id") or ""
            m = re.match(r"^(CH\d+_A\d+)", b_id)
            prefix = m.group(1) if m else b_id
            if current_prefix is None or prefix == current_prefix:
                current_prefix = prefix
                current_group.append(b)
            else:
                grouped_raw_beats.append((current_prefix, current_group))
                current_prefix = prefix
                current_group = [b]
        if current_group:
            grouped_raw_beats.append((current_prefix, current_group))
    else:
        current_group = []
        for b in beats:
            current_group.append(b)
            narr = (b.get("narration") or "").strip()
            ends_sentence = narr.endswith((".", "?", "!")) and not (narr.endswith("...") or narr.endswith("…"))
            if len(current_group) >= 3 or ends_sentence:
                g_id = current_group[0].get("beat_id") or current_group[0].get("id") or f"G{len(grouped_raw_beats)+1:03d}"
                grouped_raw_beats.append((g_id, current_group))
                current_group = []
        if current_group:
            g_id = current_group[0].get("beat_id") or current_group[0].get("id") or f"G{len(grouped_raw_beats)+1:03d}"
            grouped_raw_beats.append((g_id, current_group))

    sentence_groups = []
    payload_beats = []

    for g_id, g_beats in grouped_raw_beats:
        processed_texts = []
        g_beat_entries = []

        for b in g_beats:
            b_id = b.get("beat_id") or b.get("id")
            norm_narr = (b.get("narration") or "").strip()
            t = norm_narr

            processed_texts.append(t)
            wc = max(1, len(norm_narr.split()))
            g_beat_entries.append({
                "id": b_id,
                "text": norm_narr or "...",
                "word_count": wc
            })
            payload_beats.append({
                "id": b_id,
                "text": norm_narr or "..."
            })

        comb_text = re.sub(r"\s+", " ", " ".join(processed_texts)).strip()
        if not comb_text:
            comb_text = "..."

        sentence_groups.append({
            "group_id": g_id,
            "text": comb_text,
            "beats": g_beat_entries
        })

    payload = {
        "channel_id": channel_id,
        "ref_text": ref_text,
        "speed": recommended_speed,
        "batch_size": batch_size,
        "num_step": num_step,
        "gap_sec": 0.22,
        "sentence_groups": sentence_groups,
        "beats": payload_beats
    }

    local_payload_p = work_dir / "tts_payload.json"
    local_payload_p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    local_worker_p = work_dir / "remote_worker.py"
    local_worker_p.write_text(REMOTE_WORKER_SCRIPT, encoding="utf-8")

    # 4. Colab Upload & Execution
    base_cfg = json.loads((SYS_DIR / "config.json").read_text())
    base_cfg.setdefault("colab_tts", {})
    base_cfg["colab_tts"]["account"] = account
    base_cfg["colab_tts"]["session"] = session
    base_cfg["colab_tts"]["_session_explicit"] = True
    base_cfg["colab_tts"]["job_id"] = session

    client = Client(SYS_DIR, base_cfg)
    client.account = account
    client.session = session
    client.ensure_authenticated()
    try:
        client.reconcile()
    except Exception:
        pass
    client.session = session
    client._ready(auto_start=True)

    remote_dir = f"/tmp/vp_long_tts_{channel_id}"
    client.exec(f"import os; os.makedirs('{remote_dir}', exist_ok=True)")

    logger.info(f"Uploading assets to Colab ({client.account}:{client.session})...")
    client.call("upload", "-s", client.session, str(ref_wav.resolve()), f"{remote_dir}/ref.wav")
    client.call("upload", "-s", client.session, str(local_payload_p.resolve()), f"{remote_dir}/payload.json")
    client.call("upload", "-s", client.session, str(local_worker_p.resolve()), f"{remote_dir}/worker.py")

    exec_cmd = f"""
import sys
if '{remote_dir}' not in sys.path:
    sys.path.insert(0, '{remote_dir}')
import worker
worker.synthesize_batch_job(
    ref_wav_path='{remote_dir}/ref.wav',
    payload_path='{remote_dir}/payload.json',
    out_dir='{remote_dir}/out'
)
"""
    logger.info("Executing remote batch synthesis on Tesla T4 GPU OmniVoice...")
    t_synth0 = time.time()
    exec_res = client.exec(exec_cmd, timeout=1200)
    logger.info(f"Colab synthesis finished in {time.time()-t_synth0:.2f}s:\n{exec_res}")

    # 5. Download results
    raw_master_colab = f"{remote_dir}/out/raw_narration.wav"
    meta_colab = f"{remote_dir}/out/metadata.json"
    local_raw_wav = work_dir / "raw_narration.wav"
    local_meta_json = work_dir / "tts_metadata.json"

    client.call("download", "-s", client.session, raw_master_colab, str(local_raw_wav.resolve()))
    client.call("download", "-s", client.session, meta_colab, str(local_meta_json.resolve()))

    if not local_raw_wav.is_file() or local_raw_wav.stat().st_size < 1000:
        raise RuntimeError(f"Downloaded audio missing or corrupted: {local_raw_wav}")

    logger.info(f"Downloaded raw audio: {local_raw_wav} ({local_raw_wav.stat().st_size} bytes)")

    # 6. Audio Mastering to -11.0 LUFS / -1.0 dBTP
    mastered_wav = out_dir / "narration_master.wav"
    filter_chain = f"{voice_chain},loudnorm=I={target_lufs}:TP={target_peak}:LRA=7.0"
    cmd_master = [
        "ffmpeg", "-y", "-i", str(local_raw_wav),
        "-af", filter_chain,
        "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le",
        str(mastered_wav)
    ]
    subprocess.run(cmd_master, check=True, capture_output=True)
    shutil.copy2(mastered_wav, work_dir / "narration.wav")
    logger.info(f"Mastered audio saved to: {mastered_wav}")

    # 7. Update Spec, Subtitles, Chapters
    meta_data = json.loads(local_meta_json.read_text(encoding="utf-8"))
    beat_dur_map = {b["beat_id"]: b["total_duration"] for b in meta_data["beats"]}

    curr_time = 0.0
    srt_entries = []
    updated_beats = []

    for _idx, b in enumerate(beats):
        b_copy = copy.deepcopy(b)
        b_id = b_copy.get("beat_id") or b_copy.get("id")
        dur = float(beat_dur_map.get(b_id, b_copy.get("duration", 2.5)))
        b_copy["at"] = round(curr_time, 4)
        b_copy["duration"] = round(dur, 4)
        b_copy["hold"] = round(dur, 4)
        updated_beats.append(b_copy)

        narr = (b_copy.get("narration") or "").strip()
        if narr:
            srt_start = format_srt_time(curr_time)
            srt_end = format_srt_time(curr_time + dur)
            srt_entries.append(f"{len(srt_entries)+1}\n{srt_start} --> {srt_end}\n{narr}\n")

        curr_time += dur

    total_dur = round(curr_time, 4)
    spec["total_duration_sec"] = total_dur
    if "metadata" in spec and isinstance(spec["metadata"], dict):
        spec["metadata"]["total_duration_sec"] = total_dur
    spec["beats"] = updated_beats
    if "visual_states" in spec:
        spec["visual_states"] = updated_beats

    # Update chapters
    chapters = spec.get("chapters", [])
    if chapters:
        num_ch = len(chapters)
        has_beat_ch_idx = any(b.get("chapter_index") is not None for b in updated_beats)
        if has_beat_ch_idx:
            for i, ch in enumerate(chapters):
                ch_idx = ch.get("chapter_index", i + 1)
                ch_beats = [b for b in updated_beats if b.get("chapter_index") == ch_idx]
                if ch_beats:
                    ch["start_sec"] = round(ch_beats[0]["at"], 3)
                    ch["end_sec"] = round(ch_beats[-1]["at"] + ch_beats[-1]["duration"], 3)
                else:
                    prev_end = chapters[i - 1]["end_sec"] if i > 0 else 0.0
                    ch["start_sec"] = prev_end
                    ch["end_sec"] = prev_end
            if chapters:
                chapters[0]["start_sec"] = 0.0
                chapters[-1]["end_sec"] = total_dur
        else:
            ch_beats = total_dur / num_ch
            c_start = 0.0
            for i, ch in enumerate(chapters):
                ch["start_sec"] = round(c_start, 3)
                c_end = total_dur if i == num_ch - 1 else round(c_start + ch_beats, 3)
                ch["end_sec"] = c_end
                c_start = c_end

    # Write subtitles.srt
    srt_content = "\n".join(srt_entries) + "\n"
    (out_dir / f"{out_dir.name}_16x9.srt").write_text(srt_content, encoding="utf-8")
    (work_dir / "subtitles.srt").write_text(srt_content, encoding="utf-8")

    # Write chapters_metadata.txt
    lines = [";FFMETADATA1", f"title={channel_slug.upper()} Explainer Master", "artist=Video Pilot", ""]
    for ch in chapters:
        s_ms = int(round(float(ch["start_sec"]) * 1000))
        e_ms = int(round(float(ch["end_sec"]) * 1000))
        lines.extend([
            "[CHAPTER]",
            "TIMEBASE=1/1000",
            f"START={s_ms}",
            f"END={e_ms}",
            f"title={ch.get('title', 'Chapter')}",
            ""
        ])
    (work_dir / "chapters_metadata.txt").write_text("\n".join(lines), encoding="utf-8")

    # Save aligned spec
    spec["voice"] = f"VietNarrator_{channel_id}"
    spec["voice_profile"] = f"sys/assets/voices/ch_{channel_id}/profile.json"

    aligned_spec_p = out_dir / f"{channel_id}_long_aligned_spec.json"
    aligned_spec_p.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"Saved aligned spec to: {aligned_spec_p}")

    if "305" in spec_p.name or "310" in spec_p.name or len(beats) in (305, 310):
        dense_aligned_spec_p = out_dir / f"{channel_id}_long_{len(beats)}_aligned_spec.json"
        dense_aligned_spec_p.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info(f"Saved dense aligned spec to: {dense_aligned_spec_p}")

    # Also keep sys/channels/vn_rebuilt_style_specs synchronized
    repo_master_spec = SYS_DIR / f"channels/vn_rebuilt_style_specs/{channel_slug}/{channel_slug}_long_master_spec.json"
    repo_master_spec.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"Saved master spec to: {repo_master_spec}")

    return mastered_wav


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synthesize Long Explainer Audio on Colab T4 OmniVoice")
    parser.add_argument("--channel", "-c", required=True, help="Channel identifier (e.g. tui_tien, ho_so_ky_la)")
    parser.add_argument("--spec", "-s", help="Path to input spec JSON")
    parser.add_argument("--out-dir", "-o", help="Output directory")
    parser.add_argument("--account", "-a", default="account-05", help="Colab account ID")
    parser.add_argument("--session", default="vp-vn-long-1794089419", help="Colab session name")
    parser.add_argument("--batch-size", type=int, default=8, help="Batch size for T4 generation")
    parser.add_argument("--num-step", type=int, default=32, help="Diffusion steps")
    args = parser.parse_args()

    synthesize_long_channel(
        channel_arg=args.channel,
        spec_path_arg=args.spec,
        out_dir_arg=args.out_dir,
        account=args.account,
        session=args.session,
        batch_size=args.batch_size,
        num_step=args.num_step,
    )
