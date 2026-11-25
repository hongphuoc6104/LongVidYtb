# Pacing, Voice & Audio Mastering — Scale & Bone (`en_plain_sight_ai`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `EnNarrator_en_plain_sight_ai` (`sys/assets/voices/ch_en_plain_sight_ai/profile.json`)
- **Recommended Speaking Rate:** `1.15x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `480s–720s` (~8–12 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `35s–50s`
- **Pause & Cadence Discipline:** Zero [pause:...] inside opening Beat 0 (<= 18 words/syllables). Natural 180-350ms inter-clause pauses; single 450-650ms vacuum reset before climax.
- **Camera Transition Pace:** Smooth semantic beat cuts aligned to spoken clause transitions; 0.18-0.28s optical dissolves between distinct scenes.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: scifi_biotech_xray`)
- **Primary / Secondary Stems:** `bgm_scifi_biotech_pad.wav` / `bgm_geopolitics_pulse.wav`
- **Pre-Climax Silence Vacuum Stem:** `heartbeat_lub_dub.wav` at ~65% arc (`beat_index` calibrated per episode)
