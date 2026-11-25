# Pacing, Voice & Audio Mastering — Luật Ngầm Đám Đông (`luat_ngam`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `VietNarrator_luat_ngam` (`sys/assets/voices/ch_luat_ngam/profile.json`)
- **Recommended Speaking Rate:** `1.14x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `600s–900s` (~10–15 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `45s–60s`
- **Pause & Cadence Discipline:** Nhịp đọc điềm tĩnh, trầm ấm, bí ẩn kiểu phim tài liệu điều tra 140 WPM: Micro-pause 0.22s sau tình huống quan sát; beat-pause 0.38s sau suy nghĩ ngây thơ; dramatic-pause 0.45s sau đòn lật tẩy đám đông; pause 0.30s trước quy luật ngầm chốt lại.
- **Camera Transition Pace:** Zoompan mượt mà không snap 1-frame kết hợp xfade 0.28s: smoothdown từ góc nhìn sa bàn trên cao xuống dòng người, smoothleft theo bước chân di chuyển, smoothup quét qua hệ thống đèn chiếu, và fade mềm khi chuyển vào căn phòng điều khiển.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: forensic_noir_suspense`)
- **Primary / Secondary Stems:** `bgm_forensic_noir_drone.wav` / `bgm_geopolitics_pulse.wav`
- **Pre-Climax Silence Vacuum Stem:** `heartbeat_lub_dub.wav` at ~65% arc (`beat_index` calibrated per episode)
