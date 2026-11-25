# Pacing, Voice & Audio Mastering — First Principles Ink (`en_first_principles`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `EnNarrator_en_first_principles` (`sys/assets/voices/ch_en_first_principles/profile.json`)
- **Recommended Speaking Rate:** `1.16x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `480s–720s` (~8–12 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `35s–50s`
- **Pause & Cadence Discipline:** Nhịp đọc 145 WPM có biến thiên: Nghỉ ngắn 0.22s (micro-pause) sau mệnh đề điều kiện; nghỉ 0.42s (beat-pause) sau câu nghịch lý và sau câu hỏi tu từ để người xem kịp tự hỏi; nghỉ 0.32s giữa các mệnh đề giải thích cơ chế.
- **Camera Transition Pace:** Supersampled 2x zoompan không giật (loại bỏ hoàn toàn snap 1-frame của zoom_out), kết hợp chuyển cảnh xfade mượt 0.28s: smoothleft khi lia ngang theo trục, smoothup/smoothdown khi theo phương trọng lực, và fade/dissolve mềm khi đổi góc cận cảnh ổ bi.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: curious_explainer_momentum`)
- **Primary / Secondary Stems:** `bgm_curious_acoustic_loop.wav` / `bgm_scifi_biotech_pad.wav`
- **Pre-Climax Silence Vacuum Stem:** `clock_tick.wav` at ~65% arc (`beat_index` calibrated per episode)
