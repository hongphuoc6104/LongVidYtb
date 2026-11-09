#!/usr/bin/env python3
"""Batch Colab Tesla T4 GPU OmniVoice Synthesizer for 20 Vietnamese Channels.

Loads OmniVoice (kjanh/KhanhTTS-OmniVoice) ONCE on Colab T4 GPU (cuda:0).
Synthesizes authentic Studio V3 cloned voices for each channel using its
sys/assets/voices/ch_<channel_id>/reference.wav and profile.json.
Generates:
  - narration_master.wav (-11.0 LUFS / -1.0 dBTP)
  - _work_short/narration.wav
  - _work_short/subtitles_kinetic_9x16.ass
  - _work_short/subtitles.srt
  - _work_short/watermark_100x100.png
  - <slug_underscored>_short_aligned_spec.json
Updates sys/channels/vn_rebuilt_style_specs/<slug>/<slug>_short_fullchain_spec.json
with exact measured beat durations and voice="VietNarrator_<channel_id>".
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

SYS_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = SYS_DIR.parent
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from colab_bridge.client import Client
from tools.produce_vn_dual_mode import (
    build_clean_sidecar_srt,
    build_vn_kinetic_ass_subtitles,
    make_rounded_watermark,
)
from tools.vn_text_normalizer import normalize_for_tts

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("batch_colab_omnivoice")

BATCH_1_CHANNELS = [
    "tui-tien",
    "ho-so-ky-la",
    "banh-rang",
    "luat-doi-thuong",
    "la-ban-hoc-thuat",
    "luat-ngam",
]

BATCH_2_CHANNELS = [
    "ua-sao-vay",
    "dia-com",
    "vu-tru-ti-hon",
    "chanh-niem-ke",
    "minh-triet-song",
    "co-the-ke",
    "su-ke-lai",
    "ban-do-quyen-luc",
    "loi-sang-soi",
    "nao-luoi",
    "thuong-cho-kheo",
    "nghe-song-sot",
    "ai-binh-dan",
    "tam-tinh-dem",
]

ALL_20_CHANNELS = BATCH_1_CHANNELS + BATCH_2_CHANNELS


REMOTE_WORKER_CODE = '''# Remote Colab Tesla T4 GPU OmniVoice Batch Synthesizer
import os
import sys
import json
import time
import shutil
import subprocess
import re
import zipfile
from pathlib import Path
import numpy as np
import soundfile as sf
import torch
from huggingface_hub import snapshot_download
from omnivoice import OmniVoice
from scipy.signal import butter, resample_poly, sosfiltfilt

def normalize_text(text: str) -> str:
    t = str(text or "").strip()
    t = re.sub(r"\\[pause:[^\\]]+\\]", " ", t)
    t = re.sub(r"[*_`#~]", "", t)
    t = re.sub(r"[\\u2014\\u2013—–-]", " ", t)
    t = re.sub(r"\\s+", " ", t).strip()
    return t

def postprocess_wave(arr: np.ndarray, target_sr: int = 24000) -> np.ndarray:
    arr = np.asarray(arr, dtype=np.float32).reshape(-1)
    if not arr.size or not np.isfinite(arr).all():
        return np.zeros(int(target_sr * 0.5), dtype=np.float32)
    # Highpass filter 85 Hz to eliminate sub-bass rumble
    if len(arr) >= 64:
        try:
            sos = butter(2, 85.0 / (target_sr * 0.5), btype="highpass", output="sos")
            hp = sosfiltfilt(sos, arr).astype(np.float32)
            if np.isfinite(hp).all():
                arr = hp
        except Exception:
            pass
    # Trim leading and trailing silence
    mag = np.abs(arr)
    thresh = max(1e-4, float(np.max(mag)) * 0.02)
    voiced = np.where(mag > thresh)[0]
    if len(voiced) > 0:
        start_idx = max(0, voiced[0] - int(target_sr * 0.05))
        end_idx = min(len(arr), voiced[-1] + int(target_sr * 0.08))
        arr = arr[start_idx:end_idx]
    # Peak clamp
    pk = float(np.max(np.abs(arr))) if len(arr) > 0 else 0.0
    if pk > 0.95:
        arr *= (0.95 / pk)
    return arr

def main():
    work_dir = Path("/content/batch_tts_work")
    manifest_path = work_dir / "manifest.json"
    if not manifest_path.is_file():
        print("ERROR: manifest.json not found in", work_dir)
        sys.exit(1)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    channels = manifest.get("channels", [])
    print(f"[*] Starting OmniVoice batch synthesis for {len(channels)} channels...")

    # 1. Load OmniVoice ONCE onto GPU
    start_load = time.time()
    model_id = "kjanh/KhanhTTS-OmniVoice"
    model_rev = "20d056b8ea5d8d578b4cbaf1f703012fa3798a84"
    print(f"[*] Downloading snapshot {model_id} ({model_rev})...")
    local_model = snapshot_download(model_id, revision=model_rev)
    print(f"[*] Loading OmniVoice into cuda:0 (FP16)...")
    model = OmniVoice.from_pretrained(local_model, device_map="cuda:0", dtype=torch.float16)
    print(f"[✓] OmniVoice loaded in {time.time() - start_load:.2f}s")

    out_dir = work_dir / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 2. Iterate each channel
    for ch_idx, ch in enumerate(channels, start=1):
        slug = ch["slug"]
        voice_id = ch["voice"]
        speed = float(ch.get("speed", 1.10))
        source_speed = float(ch.get("source_speed", 1.0))
        speed_ratio = speed / source_speed if source_speed > 0 else speed
        ref_wav_path = work_dir / ch["ref_wav_filename"]
        ref_text = ch["reference_text"]
        beats = ch.get("beats", [])

        print(f"\\n[{ch_idx}/{len(channels)}] Synthesizing: {slug} | Voice: {voice_id} | Speed: {speed:.2f}x (ratio: {speed_ratio:.2f}) | Beats: {len(beats)}")
        ch_out_dir = out_dir / slug
        ch_out_dir.mkdir(parents=True, exist_ok=True)

        # Create voice clone prompt
        prompt = model.create_voice_clone_prompt(ref_audio=str(ref_wav_path), ref_text=ref_text)

        beat_waves = []
        beat_durations = []
        global_words = []
        current_time = 0.0

        for b_i, beat in enumerate(beats):
            b_id = beat.get("id", f"S{b_i+1:02d}")
            raw_text = beat.get("narration", "")
            norm_text = normalize_text(raw_text)

            # Generate speech
            torch.manual_seed(42 + b_i)
            with torch.inference_mode():
                gen_wavs = model.generate(
                    text=[norm_text],
                    language=["vi"],
                    voice_clone_prompt=[prompt],
                    speed=[speed_ratio],
                    num_step=32,
                )

            wave_arr = postprocess_wave(gen_wavs[0], target_sr=24000)
            b_dur = len(wave_arr) / 24000.0

            # Inter-beat natural breathing pause
            pause_dur = 0.15 if b_i < len(beats) - 1 else 0.40
            pause_arr = np.zeros(int(24000 * pause_dur), dtype=np.float32)

            # Build word timestamps across voiced duration
            words = norm_text.split()
            w_step = b_dur / max(1, len(words))
            for w_i, word in enumerate(words):
                w_start = round(current_time + w_i * w_step, 3)
                w_end = round(current_time + (w_i + 1) * w_step, 3)
                global_words.append({
                    "word": word,
                    "start": w_start,
                    "end": w_end,
                })

            beat_waves.append(wave_arr)
            beat_waves.append(pause_arr)

            total_b_dur = round(b_dur + pause_dur, 3)
            beat_durations.append(total_b_dur)
            current_time += total_b_dur
            print(f"   Beat {b_id}: {total_b_dur:.2f}s ({len(words)} words) -> '{norm_text[:40]}...'")

        # Stitch all waveforms
        full_wave = np.concatenate(beat_waves) if beat_waves else np.zeros(24000, dtype=np.float32)
        raw_wav_path = ch_out_dir / "narration_raw.wav"
        sf.write(str(raw_wav_path), full_wave, 24000, subtype="PCM_16")

        # Apply Studio Mastering via ffmpeg: Highpass 85Hz, Lowpass 13500Hz, Loudnorm -11.0 LUFS / -1.0 dBTP
        final_wav_path = ch_out_dir / "narration.wav"
        ff_cmd = [
            "ffmpeg", "-y", "-i", str(raw_wav_path),
            "-af", "highpass=f=85,lowpass=f=13500,loudnorm=I=-11.0:TP=-1.0:LRA=7.0",
            "-ar", "24000", "-c:a", "pcm_s16le",
            str(final_wav_path)
        ]
        subprocess.run(ff_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        raw_wav_path.unlink(missing_ok=True)

        # Save metadata
        total_dur = round(current_time, 3)
        (ch_out_dir / "words.json").write_text(json.dumps(global_words, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")
        (ch_out_dir / "beat_timings.json").write_text(json.dumps({
            "slug": slug,
            "voice": voice_id,
            "total_duration": total_dur,
            "beat_durations": beat_durations,
        }, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")

        print(f"[✓] Channel {slug} finished: total_duration={total_dur:.2f}s, wav_size={final_wav_path.stat().st_size} bytes")

    # 3. Zip output
    zip_path = work_dir / "results.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(out_dir):
            for f in files:
                f_path = Path(root) / f
                rel_path = f_path.relative_to(out_dir)
                zf.write(f_path, str(rel_path))

    print(f"[✓] All {len(channels)} channels packaged into {zip_path} ({zip_path.stat().st_size} bytes)")
    print("VP_BATCH_TTS_COMPLETE")

if __name__ == "__main__":
    import re
    main()
'''


def prepare_channel_manifest(channels: List[str]) -> Tuple[Dict[str, Any], List[Path]]:
    """Build manifest and collect reference WAVs for the requested channels."""
    manifest_channels = []
    files_to_copy = []
    voices_dir = SYS_DIR / "assets/voices"
    specs_dir = SYS_DIR / "channels/vn_rebuilt_style_specs"

    for slug in channels:
        ch_id = slug.replace("-", "_")
        prof_file = voices_dir / f"ch_{ch_id}" / "profile.json"
        ref_file = voices_dir / f"ch_{ch_id}" / "reference.wav"
        spec_file = specs_dir / slug / f"{slug}_short_fullchain_spec.json"

        if not prof_file.is_file():
            raise FileNotFoundError(f"Missing voice profile: {prof_file}")
        if not ref_file.is_file():
            raise FileNotFoundError(f"Missing reference wav: {ref_file}")
        if not spec_file.is_file():
            raise FileNotFoundError(f"Missing short fullchain spec: {spec_file}")

        profile = json.loads(prof_file.read_text(encoding="utf-8"))
        spec = json.loads(spec_file.read_text(encoding="utf-8"))

        norm_beats = []
        for beat in spec.get("beats", []):
            b_norm = dict(beat)
            raw_narr = beat.get("narration", "")
            norm_text = normalize_for_tts(raw_narr)
            if re.search(r"\d", norm_text):
                raise ValueError(
                    f"Channel {slug} beat {beat.get('id', '?')} narration contains un-normalized digits: {norm_text}"
                )
            b_norm["narration"] = norm_text
            norm_beats.append(b_norm)

        ref_wav_name = f"ref_{ch_id}.wav"
        manifest_channels.append({
            "slug": slug,
            "channel_id": ch_id,
            "voice": profile.get("voice", f"VietNarrator_{ch_id}"),
            "speed": float(profile.get("recommended_speed", 1.10)),
            "source_speed": float(profile.get("source_speed", 1.0)),
            "default_tone": profile.get("default_tone", "narrative_warm"),
            "reference_text": profile["reference_text"],
            "ref_wav_filename": ref_wav_name,
            "beats": norm_beats,
        })
        files_to_copy.append((ref_file, ref_wav_name))

    manifest = {"channels": manifest_channels}
    return manifest, files_to_copy


def run_batch_synthesis_on_colab(
    channels: List[str],
    colab_account: str = "account-01",
    session_name: str = "video-pilot-tts",
) -> Dict[str, Any]:
    """Execute batch OmniVoice synthesis on Colab Tesla T4 GPU."""
    logger.info(f"=== PREPARING COLAB BATCH SYNTHESIS: {len(channels)} CHANNELS ({colab_account}) ===")
    manifest, files_to_copy = prepare_channel_manifest(channels)

    # Build local staging bundle
    temp_dir = Path(tempfile.mkdtemp(prefix="colab_tts_batch_"))
    bundle_zip = temp_dir / "bundle_batch.zip"

    with zipfile.ZipFile(bundle_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))
        zf.writestr("runner.py", REMOTE_WORKER_CODE)
        for src_path, arc_name in files_to_copy:
            zf.write(src_path, arc_name)

    logger.info(f"Created staging bundle: {bundle_zip} ({bundle_zip.stat().st_size} bytes)")

    # Connect to Colab
    cfg_base = SYS_DIR / "config.json"
    cfg: Dict[str, Any] = json.loads(cfg_base.read_text(encoding="utf-8")) if cfg_base.is_file() else {}
    cfg.setdefault("colab_tts", {})
    cfg["colab_tts"]["session"] = session_name
    cfg["colab_tts"]["account"] = colab_account

    client = Client(SYS_DIR, cfg)
    client.account = colab_account
    client.session = session_name
    client.ensure_authenticated()

    # Reconcile & ensure ready
    client.reconcile()
    client._ready(auto_start=True)

    remote_work = "/content/batch_tts_work"
    logger.info(f"Uploading bundle to remote {remote_work} on {colab_account}...")
    client.exec(f"import shutil, os, pathlib; shutil.rmtree({remote_work!r}, ignore_errors=True); pathlib.Path({remote_work!r}).mkdir(parents=True, exist_ok=True)", timeout=120)

    remote_bundle = f"{remote_work}/bundle.zip"
    client.call("upload", "-s", client.session, str(bundle_zip.resolve()), remote_bundle, timeout=300)

    # Unpack on remote
    logger.info("Unpacking bundle on remote Colab...")
    client.exec(
        f"import zipfile\nwith zipfile.ZipFile({remote_bundle!r}, 'r') as zf:\n    zf.extractall({remote_work!r})",
        timeout=120,
    )

    # Run synthesis
    logger.info("Launching OmniVoice batch synthesis on Tesla T4 GPU (this will synthesize authentic voices)...")
    exec_cmd = (
        f"import subprocess, sys\n"
        f"with open('{remote_work}/runner.log', 'w') as log_f:\n"
        f"    p = subprocess.run([sys.executable, '{remote_work}/runner.py'], stdout=log_f, stderr=subprocess.STDOUT)\n"
        f"with open('{remote_work}/runner.log', 'r') as log_f:\n"
        f"    print(log_f.read())\n"
        f"if p.returncode != 0:\n"
        f"    raise RuntimeError('Remote batch worker failed with exit code ' + str(p.returncode))\n"
    )
    # Give plenty of timeout (up to 2400s for batch)
    client.exec(exec_cmd, timeout=2400)
    logger.info("Remote synthesis execution finished!")

    # Download results.zip
    results_zip = temp_dir / "results.zip"
    remote_results = f"{remote_work}/results.zip"
    logger.info(f"Downloading results from {remote_results}...")
    client.call("download", "-s", client.session, remote_results, str(results_zip.resolve()), timeout=300)

    # Unpack results locally
    unpack_dir = temp_dir / "results_unpacked"
    unpack_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(results_zip, "r") as zf:
        zf.extractall(unpack_dir)

    logger.info(f"Downloaded and unpacked results to {unpack_dir}")

    # Process and integrate each channel's deliverables
    results_summary = []
    specs_dir = SYS_DIR / "channels/vn_rebuilt_style_specs"
    video_base = ROOT_DIR / "video"

    for slug in channels:
        ch_id = slug.replace("-", "_")
        slug_u = slug.replace("-", "_")
        ch_res_dir = unpack_dir / slug

        if not ch_res_dir.is_dir():
            raise FileNotFoundError(f"Missing results for channel {slug} in {ch_res_dir}")

        res_wav = ch_res_dir / "narration.wav"
        res_words = ch_res_dir / "words.json"
        res_timings = ch_res_dir / "beat_timings.json"

        if not res_wav.is_file() or not res_words.is_file() or not res_timings.is_file():
            raise FileNotFoundError(f"Incomplete deliverables for {slug} in {ch_res_dir}")

        words_data = json.loads(res_words.read_text(encoding="utf-8"))
        timings_data = json.loads(res_timings.read_text(encoding="utf-8"))
        beat_durations = timings_data["beat_durations"]
        total_dur = float(timings_data["total_duration"])

        # Setup channel video directories
        ch_video_dir = video_base / f"vn_pilot_{slug_u}_short_fullchain"
        ch_work_dir = ch_video_dir / "_work_short"
        ch_work_dir.mkdir(parents=True, exist_ok=True)

        # 1. narration_master.wav & _work_short/narration.wav
        master_wav = ch_video_dir / "narration_master.wav"
        work_wav = ch_work_dir / "narration.wav"
        shutil.copy2(res_wav, master_wav)
        shutil.copy2(res_wav, work_wav)

        # 2. Subtitles: Kinetic ASS & Sidecar SRT
        spec_path = specs_dir / slug / f"{slug}_short_fullchain_spec.json"
        spec = json.loads(spec_path.read_text(encoding="utf-8"))

        for beat in spec.get("beats", []):
            beat["narration"] = normalize_for_tts(beat.get("narration", ""))

        ass_path = ch_work_dir / "subtitles_kinetic_9x16.ass"
        srt_path = ch_work_dir / "subtitles.srt"
        build_vn_kinetic_ass_subtitles(words_data, total_dur, ass_path, margin_v=270, outline=6)
        build_clean_sidecar_srt(spec["beats"], beat_durations, total_dur, srt_path)

        # 3. Watermark
        watermark_png = ch_work_dir / "watermark_100x100.png"
        make_rounded_watermark(None, watermark_png, size=100, opacity=0.92, radius=15)

        # 4. Update spec file with exact voice & beat durations
        canonical_voice = f"VietNarrator_{ch_id}"
        spec["voice"] = canonical_voice
        spec["voice_profile"] = f"assets/voices/ch_{ch_id}/profile.json"
        spec["total_duration_sec"] = total_dur
        if "metadata" in spec:
            spec["metadata"]["total_duration_sec"] = total_dur

        cur_t = 0.0
        for i, beat in enumerate(spec["beats"]):
            b_dur = beat_durations[i]
            beat["duration"] = b_dur
            beat["at"] = round(cur_t, 2)
            cur_t += b_dur

        for i, pair in enumerate(spec.get("scene_pairs", [])):
            if i < len(beat_durations):
                pair["target_duration"] = beat_durations[i]

        spec_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        # 5. Save aligned spec
        aligned_spec = dict(spec)
        aligned_spec["words"] = words_data
        aligned_spec["beat_durations"] = beat_durations
        aligned_spec_path = ch_video_dir / f"{slug_u}_short_aligned_spec.json"
        aligned_spec_path.write_text(json.dumps(aligned_spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        summary = {
            "slug": slug,
            "voice": canonical_voice,
            "duration": total_dur,
            "beats": len(spec["beats"]),
            "words": len(words_data),
            "master_wav": str(master_wav),
            "wav_bytes": master_wav.stat().st_size,
        }
        results_summary.append(summary)
        logger.info(
            f"✓ [SAVED] {slug:<18} | Voice: {canonical_voice:<26} | "
            f"Dur: {total_dur:.2f}s | Beats: {len(spec['beats'])} | Words: {len(words_data)} | Size: {master_wav.stat().st_size:,} bytes"
        )

    # Cleanup temp dir
    shutil.rmtree(temp_dir, ignore_errors=True)
    return {"channels_completed": results_summary}


def main():
    parser = argparse.ArgumentParser(description="Batch Colab Tesla T4 GPU OmniVoice Synthesizer")
    parser.add_argument("--batch", type=str, choices=["1", "2", "all"], default="1", help="Batch to synthesize")
    parser.add_argument("--channels", type=str, default=None, help="Comma-separated channel slugs to synthesize (e.g. tui-tien,ho-so-ky-la), overrides --batch")
    parser.add_argument("--account", type=str, default="account-01", help="Colab account to use")
    parser.add_argument("--session", type=str, default="video-pilot-tts", help="Colab session name")
    args = parser.parse_args()

    if args.channels:
        target_channels = [c.strip() for c in args.channels.split(",") if c.strip()]
        batch_label = f"CHANNELS ({','.join(target_channels)})"
    elif args.batch == "1":
        target_channels = BATCH_1_CHANNELS
        batch_label = "BATCH 1"
    elif args.batch == "2":
        target_channels = BATCH_2_CHANNELS
        batch_label = "BATCH 2"
    else:
        target_channels = ALL_20_CHANNELS
        batch_label = "ALL 20 CHANNELS"

    res = run_batch_synthesis_on_colab(
        channels=target_channels,
        colab_account=args.account,
        session_name=args.session,
    )

    print("\n" + "=" * 70)
    print(f"{batch_label} COMPLETED ({len(res['channels_completed'])} CHANNELS) ON COLAB TESLA T4 OMNIVOICE")
    print("=" * 70)
    for c in res["channels_completed"]:
        print(f"✓ {c['slug']:<18} | {c['voice']:<26} | {c['duration']:.2f}s | {c['wav_bytes']:,} bytes | {c['master_wav']}")


if __name__ == "__main__":
    main()
