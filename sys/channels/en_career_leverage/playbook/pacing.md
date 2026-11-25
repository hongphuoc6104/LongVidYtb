# Pacing, Voice & Audio Mastering — Career Leverage (`en_career_leverage`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `EnNarrator_en_career_leverage` (`sys/assets/voices/ch_en_career_leverage/profile.json`)
- **Recommended Speaking Rate:** `1.14x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `480s–720s` (~8–12 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `35s–50s`
- **Pause & Cadence Discipline:** Nhịp đọc đĩnh đạc, dứt khoát của chuyên gia tài chính ~152 WPM: Micro-pause 0.22s sau mệnh đề điều kiện; beat-pause 0.38s sau khi lật tẩy ảo tưởng chăm chỉ; dramatic-pause 0.45s sau câu hỏi nghịch lý đãi ngộ; pause 0.30s trước câu kết luận chiến lược.
- **Camera Transition Pace:** Supersampled 2x zoompan kết hợp xfade 0.28s (smoothleft khi chuyển đổi góc đối thoại trong phòng họp kính, smoothup khi nâng tầm quy mô tòa nhà Manhattan, và fade đĩnh đạc khi chuyển phân cảnh dữ liệu).

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: forensic_noir_suspense`)
- **Primary / Secondary Stems:** `bgm_forensic_noir_drone.wav` / `bgm_geopolitics_pulse.wav`
- **Pre-Climax Silence Vacuum Stem:** `heartbeat_lub_dub.wav` at ~65% arc (`beat_index` calibrated per episode)
