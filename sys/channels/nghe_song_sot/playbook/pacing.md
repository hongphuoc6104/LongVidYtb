# Pacing, Voice & Audio Mastering — Nghề Sống Sót (`nghe_song_sot`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `VietNarrator_nghe_song_sot` (`sys/assets/voices/ch_nghe_song_sot/profile.json`)
- **Recommended Speaking Rate:** `1.14x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `600s–900s` (~10–15 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `45s–60s`
- **Pause & Cadence Discipline:** Nhịp đọc đĩnh đạc, thực chiến, dứt khoát, chuyên nghiệp 146 WPM: Micro-pause 0.20s sau mệnh đề làm thêm giờ; beat-pause 0.38s sau khi bác bỏ quan niệm cũ; dramatic-pause 0.45s trước khi đưa ra thước đo chi phí thay thế; pause 0.30s trước lời khuyên hành động.
- **Camera Transition Pace:** Supersampled 2x zoompan kiến trúc phòng họp kính hiện đại kết hợp xfade 0.28s: smoothleft lia qua bàn đàm phán, smoothup nhìn tầm view tòa nhà chọc trời, smoothdown hạ xuống bàn cờ chiến lược, và fade sắc nét vào sơ đồ đòn bẩy.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: forensic_noir_suspense`)
- **Primary / Secondary Stems:** `bgm_forensic_noir_drone.wav` / `bgm_geopolitics_pulse.wav`
- **Pre-Climax Silence Vacuum Stem:** `heartbeat_lub_dub.wav` at ~65% arc (`beat_index` calibrated per episode)
