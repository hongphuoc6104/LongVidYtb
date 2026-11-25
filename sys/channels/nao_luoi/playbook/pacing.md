# Pacing, Voice & Audio Mastering — Não Lười (`nao_luoi`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `VietNarrator_nao_luoi` (`sys/assets/voices/ch_nao_luoi/profile.json`)
- **Recommended Speaking Rate:** `1.16x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `480s–720s` (~8–12 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `30s–45s`
- **Pause & Cadence Discipline:** Nhịp đọc sắc bén, dí dỏm, thông thái, khích lệ 144 WPM: Micro-pause 0.22s sau câu hỏi trúng tim đen; beat-pause 0.38s sau khi lật ngược nguyên nhân sinh học; dramatic-pause 0.45s sau hiện tượng bão hòa thụ thể; pause 0.30s trước giải pháp 90 giây.
- **Camera Transition Pace:** Supersampled 2x zoompan mượt mà kết hợp xfade 0.28s: smoothup hướng lên thùy trán đang phát sáng, smoothleft lia dọc đường truyền tín hiệu synap, smoothdown hạ xuống màn hình điện thoại, và fade mềm mại khi chuyển cảnh đời thường.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: curious_explainer_momentum`)
- **Primary / Secondary Stems:** `bgm_curious_acoustic_loop.wav` / `bgm_scifi_biotech_pad.wav`
- **Pre-Climax Silence Vacuum Stem:** `clock_tick.wav` at ~65% arc (`beat_index` calibrated per episode)
