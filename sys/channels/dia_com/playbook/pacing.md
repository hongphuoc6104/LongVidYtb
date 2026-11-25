# Pacing, Voice & Audio Mastering — Đĩa Cơm Khoa Học (`dia_com`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `VietNarrator_dia_com` (`sys/assets/voices/ch_dia_com/profile.json`)
- **Recommended Speaking Rate:** `1.15x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `600s–840s` (~10–14 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `40s–55s`
- **Pause & Cadence Discipline:** Nhịp đọc ấm áp, sinh động, chuẩn mực khoa học đời sống 145 WPM: Micro-pause 0.22s sau mệnh đề so sánh; beat-pause 0.38s sau khi đặt câu hỏi hương vị; dramatic-pause 0.45s khi nhắc đến phản ứng Maillard; pause 0.30s trước mẹo vặt căn bếp.
- **Camera Transition Pace:** Chuyển động probe lens macro siêu cận cảnh kết hợp xfade 0.28s: smoothright trượt dọc thớ thịt xèo xèo, smoothup theo làn khói thơm bốc lên, smoothdown vào bề mặt chảo gang, và fade mềm sang cấu trúc phân tử mô phỏng.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: scifi_biotech_xray`)
- **Primary / Secondary Stems:** `bgm_scifi_biotech_pad.wav` / `bgm_geopolitics_pulse.wav`
- **Pre-Climax Silence Vacuum Stem:** `heartbeat_lub_dub.wav` at ~65% arc (`beat_index` calibrated per episode)
