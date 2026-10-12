# Remote TTS Synthesis Engine (`OmniVoice` on Colab T4)

This reference documents the remote voice-cloning and audio assembly pipeline implemented in [`sys/colab_bridge/protocol.py`](../../../../sys/colab_bridge/protocol.py), [`sys/colab_bridge/worker.py`](../../../../sys/colab_bridge/worker.py), and [`sys/tools/vn_text_normalizer.py`](../../../../sys/tools/vn_text_normalizer.py).

---

## 1. Mandatory Pre-Synthesis Vietnamese Phonetic Normalization (`ERR-20261010-08` & `ERR-20261010-06`)

Multilingual voice-clone models (`kjanh/KhanhTTS-OmniVoice`) and Azure `edge-tts` suffer from two critical frontend tokenizer issues when given raw Vietnamese scripts:
1. **OmniVoice English Phoneme Fallback (`ERR-20261010-08`)**: Digits (`50.000`, `1963`, `17`, `81%`), slashes (`/`), and unaccented foreign proper nouns (`Richard Lee`, `Ju/'hoansi`, `Kalahari`, `Botswana`) trigger the English phoneme dictionary inside Vietnamese sentences.
2. **Edge-TTS Empty Audio Payload (`ERR-20261010-06`)**: Mid-sentence ellipses (`...`, `…`) or em-dashes (`—`, `–`) crash the Azure `vi-VN` SSML tokenizer with `NoAudioReceived`.

### Mandatory Rule
Before constructing any TTS request or invoking synthesis, pass all Vietnamese text through [`sys/tools/vn_text_normalizer.py`](../../../../sys/tools/vn_text_normalizer.py):
- Converts 100% of numbers, years, thousands (`50.000` -> `năm mươi nghìn`), and percentages (`81%` -> `tám mươi mốt phần trăm`) into spelled-out Vietnamese words.
- Maps foreign anthropological/scientific names to hyphenated Vietnamese phonetics (`Richard Lee` -> `Ri-chát Li`, `Ju/'hoansi` -> `Giu-hoan-si`).
- Normalizes `...`, `…`, `—`, `–`, `:`, `;` into standard commas (`,`) or periods (`.`).

---

## 2. Voice Profiles & Reference Checksums (`protocol.py`)

Voice clone profiles reside in `sys/assets/voices/<voice_name>/profile.json` (`adam` for Vietnamese, `reference-narrator` for English) and are mapped at the top level of `sys/config.json` under `voices`.
`load_profiles()` enforces strict validation before uploading to Colab:
- `profile['voice']` and `profile['language']` must match the active configuration.
- `reference_wav` must exist, match its SHA-256 `profile['sha256']`, and have a duration strictly between **3 and 15 seconds** (`3 <= frames / framerate <= 15`).
- `source_speed` must be positive and finite. Effective generation speed passed to OmniVoice is scaled as `item['speed'] / profile['source_speed']` to prevent double-slowdown.
- Model revision (`models[lang]['revision']`) must be a pinned 40-character hexadecimal Hugging Face commit hash (`20d056b8ea5d8d578b4cbaf1f703012fa3798a84`).

---

## 3. Persistent Kernel Caching & Batch OOM Recovery (`worker.py`)

[`sys/colab_bridge/worker.py`](../../../../sys/colab_bridge/worker.py) is imported into the persistent Jupyter kernel on Colab T4 (`sys.modules['vp_tts_' + worker_sha256[:16]]`) so subsequent synthesis requests reuse GPU memory without reloading weights:

1. **Hardware Verification**:
   - Checks `torch.cuda.is_available()` and `'T4' in torch.cuda.get_device_name(0)`. Never falls back to CPU (`COLAB_GPU_REQUIRED`).
2. **In-Memory Weight & Prompt Retention**:
   - Global `_MODEL` holds `OmniVoice.from_pretrained(local, device_map='cuda:0', dtype=torch.float16)`.
   - Global `_PROMPTS` caches `_MODEL.create_voice_clone_prompt(ref_audio=..., ref_text=...)` keyed by `(sha256, reference_text)`.
3. **Waveform Cache on Remote Disk**:
   - Each utterance is hashed by `(item, model, profile, seed, steps, worker_hash)` and cached in `/content/video-pilot-tts/audio-cache/<sha256>.wav` at `48000 Hz` (`SR = 48000`).
4. **Bounded Batching & Automatic OOM Halving**:
   - Utterances are grouped by `retake` index (seeded with `req['seed'] + take` so retakes never collide in cache) and processed in batches of `batch_size` (default `4`, `num_step=32`).
   - If `torch.cuda.OutOfMemoryError` occurs:
     - Halves batch size (`4 -> 2 -> 1`), runs `gc.collect()` and `torch.cuda.empty_cache()`, and retries the batch.
     - Only raises `COLAB_GPU_OOM` if `size == 1` still exhausts VRAM.

---

## 4. Boundary Silence Trimming, Acoustic Tail Buffers & Assembly Validation (`ERR-20261011-02`)

1. **Mandatory Utterance Boundary Silence Trimming (`_trim_silence`)**:
   - `OmniVoice` natively emits `50–180ms` of leading silence and `180–420ms` of trailing silence per utterance. Concatenating raw utterances with artificial pauses causes audible hesitation (`0.65s–1.35s` gaps).
   - `worker.py` applies `_trim_silence(w, sr=48000, threshold=0.012, lead_ms=25, trail_ms=30, fade_ms=8)` right after `resample_poly` and peak normalization so every cached WAV retains only a natural `25ms` onset and `30ms` release with an `8ms` click-free linear fade.
   - Multi-chapter assembly scripts (`generate_spoken_narration.py`) apply `trim_pcm16_stereo_silence()` and calibrated post-trim pauses: `0.20s` for short sentences (`< 8` words), `0.28s` for standard sentences, and `0.48s` for `[pause:800ms]`/`[pause:900ms]` dramatic pivots.

2. **Loudness & Scene Tail Assembly**:
   - When `request['assemble'] = True`, `worker.py` uploads and invokes `audio_processing.py`, `subtitles.py`, and `media_packaging.py` on Colab to master the final track:
   - **Loudness Normalization**: Targets `audio_lufs: -14.0` and `audio_peak_db: -1.5`.
   - **Acoustic Silence Constants**:
     - Intermediate scene boundary: $P_{\text{tail}} = 0.70\text{s}$ (`para`).
     - Final scene boundary: $P_{\text{tail}} = 0.35\text{s}$ (`tail`).
     - Minor clause / comma pause: $P_{\text{comma}} = 0.30\text{s}$ (`minor`).
   - **Result Verification (`validate_result`)**:
     - Downloads `/content/video-pilot-tts/<request_id>/output.zip`, verifies no symlinks or unexpected file extensions, validates finite positive durations for every WAV and segment, and writes `tts.log`.

