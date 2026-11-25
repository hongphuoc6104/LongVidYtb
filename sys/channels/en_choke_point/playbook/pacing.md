# Pacing, Voice & Audio Mastering — Choke Point Maps (`en_choke_point`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `EnNarrator_en_choke_point` (`sys/assets/voices/ch_en_choke_point/profile.json`)
- **Recommended Speaking Rate:** `1.18x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `480s–720s` (~8–12 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `35s–50s`
- **Pause & Cadence Discipline:** Nhịp đọc khẩn trương kịch tính địa chính trị ~150 WPM: Nghỉ ngắn 0.22s sau mệnh đề quy mô; nghỉ 0.38s sau khi chốt số lượng container; nghỉ 0.42s sau câu hỏi giả định khủng hoảng; nghỉ 0.25-0.35s giữa các chi tiết hải trình.
- **Camera Transition Pace:** Zoompan mượt mà không snap 1-frame; chuyển cảnh xfade 0.28s: fade khi chuyển góc nhìn vệ tinh quỹ đạo, smoothdown/smoothup khi lia dọc kênh đào Suez, smoothleft/smoothright khi quét theo luồng hàng hải eo biển Hormuz và Malacca.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: geopolitical_strategic_pulse`)
- **Primary / Secondary Stems:** `bgm_geopolitics_pulse.wav` / `bgm_forensic_noir_drone.wav`
- **Pre-Climax Silence Vacuum Stem:** `heartbeat_lub_dub.wav` at ~65% arc (`beat_index` calibrated per episode)
