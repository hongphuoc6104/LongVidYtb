# Pacing, Voice & Audio Mastering — Thương Cho Khéo (`thuong_cho_kheo`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `VietNarrator_thuong_cho_kheo` (`sys/assets/voices/ch_thuong_cho_kheo/profile.json`)
- **Recommended Speaking Rate:** `1.16x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `600s–900s` (~10–15 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `30s–60s`
- **Pause & Cadence Discipline:** Nhịp đọc thủ thỉ, ấm áp, đồng cảm sâu sắc 136 WPM: Micro-pause 0.22s sau hiện tượng im lặng; beat-pause 0.38s sau diễn giải tiêu cực; dramatic-pause 0.48s sau khi lật mở nguyên nhân tổn thương; pause 0.32s trước giải pháp chữa lành mối quan hệ.
- **Camera Transition Pace:** Chuyển động 35mm ấm áp nhẹ nhàng trên nền ánh đèn vàng kết hợp xfade 0.28s: smoothleft đổi góc nhìn giữa hai người ngồi bên bàn trà, smoothdown nhìn tách trà bốc khói, smoothup nhìn ánh mắt đồng cảm, và fade mềm mại chuyển cảnh.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: curious_explainer_momentum`)
- **Primary / Secondary Stems:** `bgm_curious_acoustic_loop.wav` / `bgm_scifi_biotech_pad.wav`
- **Pre-Climax Silence Vacuum Stem:** `clock_tick.wav` at ~65% arc (`beat_index` calibrated per episode)
