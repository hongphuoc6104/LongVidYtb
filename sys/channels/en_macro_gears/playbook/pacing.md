# Pacing, Voice & Audio Mastering — Macro Gears (`en_macro_gears`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `EnNarrator_en_macro_gears` (`sys/assets/voices/ch_en_macro_gears/profile.json`)
- **Recommended Speaking Rate:** `1.18x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `480s–720s` (~8–12 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `35s–50s`
- **Pause & Cadence Discipline:** Nhịp đọc trầm ấm đĩnh đạc ~145 WPM: Nghỉ ngắn 0.22s sau mệnh đề quy mô; nghỉ 0.38s sau khi hạ thấp tính chất sự việc ('routine'); nghỉ 0.42s trước khi đưa ra kích thước khổng lồ; nghỉ 0.25-0.35s giữa các chi tiết máy và kết cấu.
- **Camera Transition Pace:** Chuyển động zoompan mượt mà không snap 1-frame; chuyển cảnh xfade 0.28s: fade khi chuyển từ vi mô sang vĩ mô, smoothleft/smoothright khi quét theo chiều dài thân tàu, smoothup/smoothdown khi lia cần cẩu gantry và cống đập.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: geopolitical_strategic_pulse`)
- **Primary / Secondary Stems:** `bgm_geopolitics_pulse.wav` / `bgm_forensic_noir_drone.wav`
- **Pre-Climax Silence Vacuum Stem:** `heartbeat_lub_dub.wav` at ~65% arc (`beat_index` calibrated per episode)
