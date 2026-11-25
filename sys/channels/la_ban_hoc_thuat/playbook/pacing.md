# Pacing, Voice & Audio Mastering — La Bàn Học Thuật (`la_ban_hoc_thuat`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `VietNarrator_la_ban_hoc_thuat` (`sys/assets/voices/ch_la_ban_hoc_thuat/profile.json`)
- **Recommended Speaking Rate:** `1.16x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `660s–960s` (~11–16 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `45s–60s`
- **Pause & Cadence Discipline:** Nhịp đọc truyền cảm hứng, khúc chiết, chuẩn mực học giả 143 WPM: Micro-pause 0.22s sau mệnh đề trải nghiệm; beat-pause 0.38s sau khi chỉ ra sự lãng phí thời gian; dramatic-pause 0.45s sau câu hỏi phá vỡ định kiến tự ti; pause 0.32s trước nguyên lý Feynman.
- **Camera Transition Pace:** Zoompan 2x mượt mà kết hợp xfade 0.28s: smoothleft khi quét qua trang sách dày, smoothup khi nâng tầm sang sơ đồ tư duy, smoothdown khi chỉ vào trang giấy ghi chú thực hành, và fade nhẹ vào thí nghiệm quang học.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: curious_explainer_momentum`)
- **Primary / Secondary Stems:** `bgm_curious_acoustic_loop.wav` / `bgm_scifi_biotech_pad.wav`
- **Pre-Climax Silence Vacuum Stem:** `clock_tick.wav` at ~65% arc (`beat_index` calibrated per episode)
