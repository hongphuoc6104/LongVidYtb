# Pacing, Voice & Audio Mastering — Inside the Vessel (`en_inside_vessel`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `EnNarrator_en_inside_vessel` (`sys/assets/voices/ch_en_inside_vessel/profile.json`)
- **Recommended Speaking Rate:** `1.15x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `480s–720s` (~8–12 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `35s–50s`
- **Pause & Cadence Discipline:** Nhịp đọc y khoa khoa học, chuẩn xác ~140 WPM: Nghỉ 0.22s sau lời dẫn nội soi; beat-pause 0.38s sau khi chứng kiến tế bào hồng cầu; dramatic-pause 0.45s sau câu hỏi về cơ chế chịu áp lực vi mô; pause 0.30s trước kết luận đắt giá về dòng chảy duy trì sinh mệnh.
- **Camera Transition Pace:** Chuyển động camera nội soi 3D trôi bồng bềnh dọc theo lòng mạch (push_in, pan_left, zoom_out, tilt_up), kết hợp xfade 0.28s (smoothright theo chiều dòng chảy máu, smoothdown khi lọt qua mao mạch, fade mềm qua màng nội mô).

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: scifi_biotech_xray`)
- **Primary / Secondary Stems:** `bgm_scifi_biotech_pad.wav` / `bgm_geopolitics_pulse.wav`
- **Pre-Climax Silence Vacuum Stem:** `heartbeat_lub_dub.wav` at ~65% arc (`beat_index` calibrated per episode)
