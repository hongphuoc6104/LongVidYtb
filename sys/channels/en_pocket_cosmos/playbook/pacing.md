# Pacing, Voice & Audio Mastering — Pocket Cosmos (`en_pocket_cosmos`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `EnNarrator_en_pocket_cosmos` (`sys/assets/voices/ch_en_pocket_cosmos/profile.json`)
- **Recommended Speaking Rate:** `1.15x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `480s–720s` (~8–12 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `35s–50s`
- **Pause & Cadence Discipline:** Nhịp đọc thiên văn điện ảnh trầm hùng ~132 WPM: Nghỉ 0.22s sau mệnh đề định vị không gian sâu; beat-pause 0.38s sau miêu tả bão ngọc bích; dramatic-pause 0.45s sau câu hỏi tu từ triết học về sự sống; pause 0.30s trước lời mời gọi khám phá tương lai.
- **Camera Transition Pace:** Supersampled 2x zoompan mô phỏng camera viễn vọng không gian James Webb bay lượn (push_in, pan_right, zoom_out, tilt_up), kết hợp chuyển cảnh xfade 0.28s (fade, smoothleft, smoothright, smoothup, smoothdown) tạo cảm giác trôi dạt êm ái giữa các vì sao.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: scifi_biotech_xray`)
- **Primary / Secondary Stems:** `bgm_scifi_biotech_pad.wav` / `bgm_geopolitics_pulse.wav`
- **Pre-Climax Silence Vacuum Stem:** `heartbeat_lub_dub.wav` at ~65% arc (`beat_index` calibrated per episode)
