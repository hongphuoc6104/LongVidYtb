# Pacing, Voice & Audio Mastering — Kindred Sketch (`en_kindred_sketch`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `EnNarrator_en_kindred_sketch` (`sys/assets/voices/ch_en_kindred_sketch/profile.json`)
- **Recommended Speaking Rate:** `1.16x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `480s–720s` (~8–12 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `35s–50s`
- **Pause & Cadence Discipline:** Nhịp đọc trầm ấm, thấu cảm ~138 WPM: Micro-pause 0.22s sau mệnh đề điều kiện mở đầu; beat-pause 0.38s sau phán đoán; dramatic-pause 0.45s sau câu hỏi tu từ để người xem tự nhìn nhận bản thân; pause 0.30s trước kết luận đắt giá.
- **Camera Transition Pace:** Chuyển động máy quay cận cảnh nhẹ nhàng (push_in, pan_left, tilt_up) tái hiện không gian ăn tối thân mật, kết hợp hiệu ứng xfade 0.28s (smoothleft khi đổi góc nhìn giữa hai người, smoothup/smoothdown khi đổi trạng thái cảm xúc, và fade khi mở đầu/kết thúc).

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: curious_explainer_momentum`)
- **Primary / Secondary Stems:** `bgm_curious_acoustic_loop.wav` / `bgm_scifi_biotech_pad.wav`
- **Pre-Climax Silence Vacuum Stem:** `clock_tick.wav` at ~65% arc (`beat_index` calibrated per episode)
