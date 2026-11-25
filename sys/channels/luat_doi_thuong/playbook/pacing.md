# Pacing, Voice & Audio Mastering — Luật Đời Thường (`luat_doi_thuong`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `VietNarrator_luat_doi_thuong` (`sys/assets/voices/ch_luat_doi_thuong/profile.json`)
- **Recommended Speaking Rate:** `1.16x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `600s–900s` (~10–15 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `45s–60s`
- **Pause & Cadence Discipline:** Nhịp đọc chắc chắn, đanh thép, tin cậy của luật sư tư vấn 142 WPM: Micro-pause 0.22s sau mệnh đề điều kiện; beat-pause 0.38s sau khi chỉ rõ thiệt hại; dramatic-pause 0.45s sau câu hỏi tu từ truy vấn trách nhiệm; pause 0.30s trước điều khoản chốt hạ.
- **Camera Transition Pace:** Zoompan mượt mà kết hợp xfade 0.28s: smoothdown lia dọc theo trang giấy hợp đồng, smoothleft/smoothright quét qua dòng chữ được bôi vàng, và fade tĩnh lặng khi chuyển sang góc cận cảnh con dấu sáp và cân công lý.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: curious_explainer_momentum`)
- **Primary / Secondary Stems:** `bgm_curious_acoustic_loop.wav` / `bgm_scifi_biotech_pad.wav`
- **Pre-Climax Silence Vacuum Stem:** `clock_tick.wav` at ~65% arc (`beat_index` calibrated per episode)
