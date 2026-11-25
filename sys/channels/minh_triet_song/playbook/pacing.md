# Pacing, Voice & Audio Mastering — Minh Triết Sống (`minh_triet_song`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `VietNarrator_minh_triet_song` (`sys/assets/voices/ch_minh_triet_song/profile.json`)
- **Recommended Speaking Rate:** `1.04x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `600s–960s` (~10–16 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `45s–60s`
- **Pause & Cadence Discipline:** Nhịp đọc đĩnh đạc, dứt khoát, điềm tĩnh, đầy nội lực 138 WPM: Micro-pause 0.22s sau mệnh đề tha nhân; beat-pause 0.40s sau khẳng định tư cách; dramatic-pause 0.45s khi nêu danh triết gia; pause 0.32s trước nguyên tắc hành động.
- **Camera Transition Pace:** Supersampled 2x zoompan phong cách chiaroscuro uy nghiêm kết hợp xfade 0.28s: push_in vào gương mặt tượng đá La Mã, smoothleft lướt qua rặng thông gió núi, smoothdown theo vết khắc trên phiến đá, và fade đĩnh đạc vào ánh bình minh.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: zen_reflective_swell`)
- **Primary / Secondary Stems:** `bgm_zen_night_healing.wav` / `bgm_zen_night_healing.wav`
- **Pre-Climax Silence Vacuum Stem:** `singing_bowl_zen.wav` at ~65% arc (`beat_index` calibrated per episode)
