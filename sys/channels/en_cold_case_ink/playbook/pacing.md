# Pacing, Voice & Audio Mastering — Cold Case Ink (`en_cold_case_ink`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `EnNarrator_en_cold_case_ink` (`sys/assets/voices/ch_en_cold_case_ink/profile.json`)
- **Recommended Speaking Rate:** `1.14x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `480s–720s` (~8–12 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `35s–50s`
- **Pause & Cadence Discipline:** Nhịp đọc trầm mặc lạnh lùng phong cách noir điều tra Anh quốc ~135 WPM: Nghỉ ngắn 0.22s sau mệnh đề thời gian; nghỉ 0.38s sau hành động bước đi; nghỉ sâu 0.45s sau câu hỏi tu từ để âm thanh sương đêm vang vọng; nghỉ 0.25-0.35s giữa các chứng cứ pháp y.
- **Camera Transition Pace:** Zoompan mượt mà không snap 1-frame; chuyển cảnh xfade 0.28s: fade khi chuyển góc sa bàn 3D, smoothdown khi lia từ mái nhà xuống ngõ hẻm, smoothleft/smoothright khi quét theo sợi chỉ đỏ trên bản đồ Whitechapel.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: forensic_noir_suspense`)
- **Primary / Secondary Stems:** `bgm_forensic_noir_drone.wav` / `bgm_geopolitics_pulse.wav`
- **Pre-Climax Silence Vacuum Stem:** `heartbeat_lub_dub.wav` at ~65% arc (`beat_index` calibrated per episode)
