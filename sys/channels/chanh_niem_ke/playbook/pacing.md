# Pacing, Voice & Audio Mastering — Hiểu Tận Gốc (`chanh_niem_ke`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `VietNarrator_chanh_niem_ke` (`sys/assets/voices/ch_chanh_niem_ke/profile.json`)
- **Recommended Speaking Rate:** `1.18x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `540s–840s` (~9–14 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `45s–60s`
- **Pause & Cadence Discipline:** Nhịp KTTV Studio V3 (226-232 âm tiết/phút Hook & Body, 248-256 âm tiết/phút Outro): pause_after_s biến thiên theo ngữ cảnh (0.48-0.75s thở bình thường, 0.90-1.35s nhấn điểm nghẽn, 2.50-4.80s mỗi ~45-55s nhường chỗ cho Sparse Realistic Foley SFX).
- **Camera Transition Pace:** Bipolar V5.0 chuyển cảnh giữa World A (bản đồ GIS Web Mercator DEM + ghim tọa độ) và World B (sa bàn giấy nhăn #DCDCD7, mặt cắt UE5 3D, clip Omni 1.2 Flash 6s và quét bút nhớ #FAD01A).

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: geopolitical_strategic_pulse`)
- **Primary / Secondary Stems:** `bgm_geopolitics_pulse.wav` / `bgm_forensic_noir_drone.wav`
- **Pre-Climax Silence Vacuum Stem:** `heartbeat_lub_dub.wav` at ~65% arc (`beat_index` calibrated per episode)
