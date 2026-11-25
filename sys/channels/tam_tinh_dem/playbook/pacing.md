# Pacing, Voice & Audio Mastering — Tâm Tĩnh Đêm (`tam_tinh_dem`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `VietNarrator_tam_tinh_dem` (`sys/assets/voices/ch_tam_tinh_dem/profile.json`)
- **Recommended Speaking Rate:** `1.04x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `600s–960s` (~10–16 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `45s–60s`
- **Pause & Cadence Discipline:** Nhịp đọc thủ thỉ, êm dịu, ấm áp, ru êm giấc ngủ 128 WPM: Micro-pause 0.28s sau lời gọi đêm khuya; beat-pause 0.45s sau lời vỗ về nỗ lực; dramatic-pause 0.52s sau ẩn dụ dòng sông; pause 0.40s dẫn vào giấc ngủ bình yên.
- **Camera Transition Pace:** Chuyển động máy quay bồng bềnh không trọng lực giữa đêm sao Studio Ghibli kết hợp xfade 0.28s: smoothleft trượt trên mặt hồ lấp lánh ánh trăng, smoothdown nhìn ánh đèn lồng vàng ấm, smoothup hướng về bầu trời sao thênh thang, và fade dần vào màn đêm êm ái.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: zen_reflective_swell`)
- **Primary / Secondary Stems:** `bgm_zen_night_healing.wav` / `bgm_zen_night_healing.wav`
- **Pre-Climax Silence Vacuum Stem:** `singing_bowl_zen.wav` at ~65% arc (`beat_index` calibrated per episode)
