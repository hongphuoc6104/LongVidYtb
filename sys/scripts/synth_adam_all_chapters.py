#!/usr/bin/env python3
"""
Synthesizes Chapters 2–8 with Adam (+22% to +25% speed) using OmniVoice on Colab Tesla T4 GPU.
Uses 100% Vietnamese phonetic normalized text from phonetic_normalized_script_8ch.json.
Outputs broadcast-grade 48kHz Stereo WAV and generates spoken cues JSON for all 8 chapters.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

PROJ_ROOT = Path(__file__).resolve().parents[2]
BUNDLE_DIR = PROJ_ROOT / "sys" / "exports" / "ancient_humans_bundle"
AUDIO_DIR = BUNDLE_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

ACCOUNT_CLI = str(PROJ_ROOT / "sys" / "colab_bridge" / "account_cli.py")
ACCOUNT_DIR = f"{os.path.expanduser('~')}/.config/video-pilot/colab/profiles/{account}" if (account := "account-01") else ""
PY_BIN = f"{os.path.expanduser('~')}/.local/share/uv/tools/google-colab-cli/bin/python"


def run_colab_cmd(args: list[str], timeout: int = 300, input_text: str | None = None):
    argv = [PY_BIN, ACCOUNT_CLI, ACCOUNT_DIR, *args]
    return subprocess.run(argv, input=input_text, capture_output=True, text=True, check=True, timeout=timeout)


COLAB_WORKER_PY = """#!/usr/bin/env python3
import os
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import json, sys, time
from pathlib import Path
import numpy as np
import soundfile as sf
import torch
from huggingface_hub import snapshot_download
from omnivoice import OmniVoice
from scipy.signal import resample_poly

SR = 48000
out_dir = Path("/content/output_audio")
out_dir.mkdir(parents=True, exist_ok=True)

with open("/content/phonetic_normalized_script_8ch.json", "r", encoding="utf-8") as f:
    all_scripts = json.load(f)

print("Loading cached OmniVoice on Colab T4...", flush=True)
local = snapshot_download("kjanh/KhanhTTS-OmniVoice", revision="20d056b8ea5d8d578b4cbaf1f703012fa3798a84")
model = OmniVoice.from_pretrained(local, device_map="cuda:0", dtype=torch.float16)
print("OmniVoice model ready!", flush=True)

ref_audio = "/content/voices/adam/reference.wav"
ref_text = "A predator is an animal that hunts other animals for food."
prompt = model.create_voice_clone_prompt(ref_audio=ref_audio, ref_text=ref_text)

CHAPTER_SPEEDS = {
    "ch2": 1.24,
    "ch3": 1.25,
    "ch4": 1.25,
    "ch5": 1.25,
    "ch6": 1.24,
    "ch7": 1.22,
    "ch8": 1.22,
}

target_chapters = sys.argv[1:] if len(sys.argv) > 1 else ["ch2", "ch3", "ch4", "ch5", "ch6", "ch7", "ch8"]

for ch_key in target_chapters:
    out_wav = out_dir / f"{ch_key}_narration_spoken.wav"
    out_cues = out_dir / f"{ch_key}_spoken_cues.json"
    if out_wav.is_file() and out_wav.stat().st_size > 50000 and out_cues.is_file():
        print(f"SKIP {ch_key}: already exists ({out_wav.stat().st_size} bytes)", flush=True)
        continue

    items = all_scripts[ch_key]
    texts = [it["normalized_text"].strip() for it in items]
    pauses = [0.35 if i < len(texts) - 1 else 0.50 for i in range(len(texts))]
    spd = CHAPTER_SPEEDS.get(ch_key, 1.22)

    print(f"--- Synthesizing {ch_key} ({len(texts)} sentences, speed={spd}) ---", flush=True)
    t0 = time.time()
    torch.manual_seed(42)
    generated = model.generate(
        text=texts,
        language=["vi"] * len(texts),
        voice_clone_prompt=[prompt] * len(texts),
        speed=[spd] * len(texts),
        num_step=32,
    )
    dt = time.time() - t0

    segments = []
    cues = []
    current_time = 0.0

    for idx, (gen_w, pause_sec) in enumerate(zip(generated, pauses)):
        if isinstance(gen_w, torch.Tensor):
            w = gen_w.detach().cpu().numpy().squeeze().astype(np.float32)
        else:
            w = np.asarray(gen_w, dtype=np.float32).squeeze()

        w_48k = resample_poly(w, 2, 1).astype(np.float32)
        peak = float(np.max(np.abs(w_48k))) if w_48k.size else 0.0
        if peak > 0.89:
            w_48k = w_48k * (0.89 / peak)

        sent_dur = len(w_48k) / SR
        start_time = current_time
        end_time = start_time + sent_dur

        cues.append(
            {
                "index": idx + 1,
                "text": texts[idx],
                "start": round(start_time, 3),
                "end": round(end_time, 3),
                "duration": round(sent_dur, 3),
            }
        )

        segments.append(w_48k)
        current_time = end_time

        if pause_sec > 0:
            pause_samples = int(round(pause_sec * SR))
            segments.append(np.zeros(pause_samples, dtype=np.float32))
            current_time += pause_sec

    full_mono = np.concatenate(segments)
    full_stereo = np.column_stack([full_mono, full_mono])

    sf.write(str(out_wav), full_stereo, SR, subtype="PCM_16")
    with open(out_cues, "w", encoding="utf-8") as f:
        json.dump(cues, f, ensure_ascii=False, indent=2)

    print(f"SAVED {ch_key}: duration={current_time:.2f}s (gen in {dt:.1f}s)", flush=True)

print("ALL_CHAPTERS_SYNTH_OK", flush=True)
"""


def main():
    print("=== SYNTHESIZING CHAPTERS 2–8 ADAM VOICE ON COLAB T4 GPU ===", flush=True)
    worker_local = Path("/tmp/colab_tts_worker.py")
    worker_local.write_text(COLAB_WORKER_PY, encoding="utf-8")
    run_colab_cmd(["upload", "-s", "video-pilot-tts", str(worker_local), "/content/colab_tts_worker.py"], timeout=120)

    # Run in 2 batches ([ch2, ch3, ch4, ch5] then [ch6, ch7, ch8]) via standalone python3 subprocess
    for batch_idx, batch in enumerate([["ch2", "ch3", "ch4", "ch5"], ["ch6", "ch7", "ch8"]], start=1):
        print(f"\n[Batch {batch_idx}/2] Running Colab T4 synthesis for {batch}...", flush=True)
        exec_code = f"""
import subprocess, sys
p = subprocess.run([sys.executable, "-u", "/content/colab_tts_worker.py", *{batch!r}], capture_output=True, text=True)
print(p.stdout)
if p.returncode != 0:
    print("STDERR:", p.stderr)
    raise RuntimeError("Batch failed")
"""
        res = run_colab_cmd(["exec", "-s", "video-pilot-tts", "--timeout", "900"], timeout=920, input_text=exec_code)
        print(res.stdout, flush=True)
        if "ALL_CHAPTERS_SYNTH_OK" not in res.stdout:
            raise RuntimeError(f"Colab synthesis batch {batch} failed:\n{res.stderr}")

        for ch_key in batch:
            colab_wav = f"/content/output_audio/{ch_key}_narration_spoken.wav"
            colab_cues = f"/content/output_audio/{ch_key}_spoken_cues.json"
            local_wav = AUDIO_DIR / f"{ch_key}_narration_spoken.wav"
            local_cues = AUDIO_DIR / f"{ch_key}_spoken_cues.json"
            print(f"Downloading {ch_key} audio & cues...", flush=True)
            run_colab_cmd(["download", "-s", "video-pilot-tts", colab_wav, str(local_wav)], timeout=180)
            run_colab_cmd(["download", "-s", "video-pilot-tts", colab_cues, str(local_cues)], timeout=120)
            print(f"  -> {local_wav.name} ({local_wav.stat().st_size / (1024*1024):.2f} MB)", flush=True)

    if (AUDIO_DIR / "ch1_adam_p22.wav").is_file():
        shutil.copy2(AUDIO_DIR / "ch1_adam_p22.wav", AUDIO_DIR / "ch1_narration_spoken.wav")
    if (AUDIO_DIR / "ch1_adam_p22_cues.json").is_file():
        shutil.copy2(AUDIO_DIR / "ch1_adam_p22_cues.json", AUDIO_DIR / "ch1_spoken_cues.json")

    print("\n=== ALL 8 CHAPTERS AUDIO & CUES READY IN ADAM VOICE ===", flush=True)


if __name__ == "__main__":
    main()
