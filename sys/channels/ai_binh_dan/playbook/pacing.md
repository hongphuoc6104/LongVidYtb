# Pacing, Voice & Audio Mastering — AI Bình Dân (`ai_binh_dan`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `VietNarrator_ai_binh_dan` (`sys/assets/voices/ch_ai_binh_dan/profile.json`)
- **Recommended Speaking Rate:** `1.16x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `600s–1200s` (~10–20 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `30s–60s`
- **Pause & Cadence Discipline:** Nhịp đọc hào hứng, nhanh nhẹn, rõ ràng, thực dụng 150 WPM: Micro-pause 0.18s sau câu hỏi thời gian lãng phí; beat-pause 0.32s sau khi nêu đòn bẩy câu lệnh; dramatic-pause 0.42s sau kết quả 40 giây; pause 0.25s trước lời tặng công thức thực chiến.
- **Camera Transition Pace:** Zoompan mượt mà trên giao diện dark-mode và bàn phím cơ kết hợp xfade 0.28s: smoothright trượt dọc câu prompt mẫu, smoothup nhìn bảng kết quả phân tích tự động, smoothdown lia tay gõ phím, và fade sáng sang bảng tóm tắt 3 bước.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: curious_explainer_momentum`)
- **Primary / Secondary Stems:** `bgm_curious_acoustic_loop.wav` / `bgm_scifi_biotech_pad.wav`
- **Pre-Climax Silence Vacuum Stem:** `clock_tick.wav` at ~65% arc (`beat_index` calibrated per episode)
