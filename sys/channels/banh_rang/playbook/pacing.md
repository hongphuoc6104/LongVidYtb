# Pacing, Voice & Audio Mastering — Bánh Răng Thế Giới (`banh_rang`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `VietNarrator_banh_rang` (`sys/assets/voices/ch_banh_rang/profile.json`)
- **Recommended Speaking Rate:** `1.18x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `660s–960s` (~11–16 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `45s–60s`
- **Pause & Cadence Discipline:** Nhịp đọc đĩnh đạc, khúc chiết, chuẩn mực kỹ sư hạ tầng 144 WPM: Micro-pause 0.22s sau số liệu vĩ mô; beat-pause 0.38s sau khi nêu tác động vi mô đời thường; dramatic-pause 0.45s sau câu hỏi bánh răng truyền lực; pause 0.32s giữa các mắt xích nhân quả.
- **Camera Transition Pace:** Supersampled 2x zoompan không giật kết hợp xfade 0.28s: smoothleft lia dọc dây chuyền container cảng biển, smoothup theo tháp cẩu gantry, smoothdown khi hạ thấp xuống mặt đường dân sinh, và fade mềm chuyển đổi giữa bản đồ chuỗi cung ứng và hiện trường.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: geopolitical_strategic_pulse`)
- **Primary / Secondary Stems:** `bgm_geopolitics_pulse.wav` / `bgm_forensic_noir_drone.wav`
- **Pre-Climax Silence Vacuum Stem:** `heartbeat_lub_dub.wav` at ~65% arc (`beat_index` calibrated per episode)
