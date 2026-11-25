# Pacing, Voice & Audio Mastering — Ủa Sao Vậy? (`ua_sao_vay`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `VietNarrator_ua_sao_vay` (`sys/assets/voices/ch_ua_sao_vay/profile.json`)
- **Recommended Speaking Rate:** `1.15x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `480s–720s` (~8–12 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `20s–35s`
- **Pause & Cadence Discipline:** Nhịp đọc nhanh, dồn dập, tò mò, hào hứng 152 WPM: Micro-pause 0.18s ngay sau câu hỏi 'Ủa sao vậy?'; beat-pause 0.32s sau khi mở lát cắt 3D; dramatic-pause 0.42s trước khi giải thích hậu quả thiếu cơ chế; pause 0.25s kết lại cảm giác kinh ngạc.
- **Camera Transition Pace:** Zoompan bổ nhào cực nhanh vào mặt cắt cơ khí 3D kết hợp xfade 0.28s: smoothup khi lò xo nén lại, smoothdown khi ngòi bút nhô ra, smoothright theo rãnh xoay cam, và fade sáng khi hoàn thành chu trình cơ học.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: scifi_biotech_xray`)
- **Primary / Secondary Stems:** `bgm_scifi_biotech_pad.wav` / `bgm_geopolitics_pulse.wav`
- **Pre-Climax Silence Vacuum Stem:** `heartbeat_lub_dub.wav` at ~65% arc (`beat_index` calibrated per episode)
