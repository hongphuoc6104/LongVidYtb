# Pacing, Voice & Audio Mastering — Vũ Trụ Tí Hon (`vu_tru_ti_hon`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `VietNarrator_vu_tru_ti_hon` (`sys/assets/voices/ch_vu_tru_ti_hon/profile.json`)
- **Recommended Speaking Rate:** `1.15x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `720s–1020s` (~12–17 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `40s–55s`
- **Pause & Cadence Discipline:** Nhịp đọc trầm hùng, sâu lắng, đậm chất điện ảnh IMAX 134 WPM: Micro-pause 0.25s sau ẩn dụ hạt đậu; beat-pause 0.42s sau khi hố đen hình thành; dramatic-pause 0.50s sau ranh giới chân trời sự kiện; pause 0.35s trước câu kết triết lý không gian.
- **Camera Transition Pace:** Supersampled 2x zoompan trôi dạt vũ trụ không trọng lực kết hợp xfade 0.28s: smoothleft trượt theo vành đai bồi tụ rực sáng, smoothup vút qua bóng tối chân trời sự kiện, smoothdown theo tia plasma năng lượng, và fade hòa tan vào nền trời đêm đen thẳm.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: scifi_biotech_xray`)
- **Primary / Secondary Stems:** `bgm_scifi_biotech_pad.wav` / `bgm_geopolitics_pulse.wav`
- **Pre-Climax Silence Vacuum Stem:** `heartbeat_lub_dub.wav` at ~65% arc (`beat_index` calibrated per episode)
