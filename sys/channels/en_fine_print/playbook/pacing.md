# Pacing, Voice & Audio Mastering — Everyday Fine Print (`en_fine_print`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `EnNarrator_en_fine_print` (`sys/assets/voices/ch_en_fine_print/profile.json`)
- **Recommended Speaking Rate:** `1.16x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `480s–720s` (~8–12 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `35s–50s`
- **Pause & Cadence Discipline:** Nhịp đọc đĩnh đạc giọng luật sư điều tra ~142 WPM: Nghỉ ngắn 0.22s sau mệnh đề điều kiện; nghỉ 0.38s sau khi lật tẩy kỳ vọng; nghỉ 0.45s sau câu hỏi tu từ để khán giả tự vấn; nghỉ 0.25-0.35s giữa các điều khoản pháp lý.
- **Camera Transition Pace:** Zoompan mượt mà không snap 1-frame; chuyển cảnh xfade 0.28s: fade khi chuyển sang hồ sơ, smoothdown khi quét theo trang giấy in, smoothleft/smoothright khi quét dòng chữ bôi vàng highlighter quang học.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: curious_explainer_momentum`)
- **Primary / Secondary Stems:** `bgm_curious_acoustic_loop.wav` / `bgm_scifi_biotech_pad.wav`
- **Pre-Climax Silence Vacuum Stem:** `clock_tick.wav` at ~65% arc (`beat_index` calibrated per episode)
