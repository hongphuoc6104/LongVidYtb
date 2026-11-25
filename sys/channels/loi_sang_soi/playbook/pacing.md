# Pacing, Voice & Audio Mastering — Lời Sáng Soi (`loi_sang_soi`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `VietNarrator_loi_sang_soi` (`sys/assets/voices/ch_loi_sang_soi/profile.json`)
- **Recommended Speaking Rate:** `1.04x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `600s–960s` (~10–16 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `45s–60s`
- **Pause & Cadence Discipline:** Nhịp đọc ấm áp, truyền cảm, lắng đọng, bao dung 135 WPM: Micro-pause 0.25s sau hành động ra đi; beat-pause 0.40s sau nỗi ân hận trắng tay; dramatic-pause 0.48s trước cái ôm của người cha; pause 0.35s để bài học yêu thương thấm sâu vào tâm hồn.
- **Camera Transition Pace:** Chuyển động máy quay chiaroscuro ngập tràn ánh sáng vàng hổ phách kết hợp xfade 0.28s: smoothleft lia dọc con đường làng cổ xưa, smoothdown nhìn đôi bàn chân lấm bụi, smoothup hướng lên vòm trời chiều ấm áp, và fade trang trọng vào bức họa sơn dầu cổ điển.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: zen_reflective_swell`)
- **Primary / Secondary Stems:** `bgm_zen_night_healing.wav` / `bgm_zen_night_healing.wav`
- **Pre-Climax Silence Vacuum Stem:** `singing_bowl_zen.wav` at ~65% arc (`beat_index` calibrated per episode)
