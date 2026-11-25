# Pacing, Voice & Audio Mastering — Túi Tiền Biết Nói (`tui_tien`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `VietNarrator_tui_tien` (`sys/assets/voices/ch_tui_tien/profile.json`)
- **Recommended Speaking Rate:** `1.16x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `600s–900s` (~10–15 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `45s–60s`
- **Pause & Cadence Discipline:** Nhịp đọc đĩnh đạc, tính toán nhanh 148 WPM: Micro-pause 0.22s sau mệnh đề giá bán; beat-pause 0.38s sau khi lật tẩy giá vốn; dramatic-pause 0.45s sau câu hỏi tu từ để người xem giật mình nhẩm lại chi tiêu; pause 0.30s trước kết luận đòn bẩy tài chính.
- **Camera Transition Pace:** Supersampled 2x zoompan mượt mà kết hợp chuyển cảnh xfade 0.28s: smoothright khi lia dọc hóa đơn thanh toán, smoothleft khi quay lại ví tiền, smoothup khi nâng tầm mắt vào bảng chi phí, và fade mềm khi chuyển bối cảnh studio sản phẩm.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: curious_explainer_momentum`)
- **Primary / Secondary Stems:** `bgm_curious_acoustic_loop.wav` / `bgm_scifi_biotech_pad.wav`
- **Pre-Climax Silence Vacuum Stem:** `clock_tick.wav` at ~65% arc (`beat_index` calibrated per episode)
