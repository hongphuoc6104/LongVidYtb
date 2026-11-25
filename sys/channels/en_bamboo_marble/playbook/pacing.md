# Pacing, Voice & Audio Mastering — Bamboo & Marble (`en_bamboo_marble`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `EnNarrator_en_bamboo_marble` (`sys/assets/voices/ch_en_bamboo_marble/profile.json`)
- **Recommended Speaking Rate:** `1.04x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `480s–720s` (~8–12 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `35s–50s`
- **Pause & Cadence Discipline:** Nhịp điệu tự sự chiêm nghiệm 141 WPM: Nghỉ 0.22s sau mệnh đề mệt mỏi; nghỉ 0.38s sau thói quen cứng nhắc; nghỉ sâu 0.45s sau câu hỏi bước ngoặt ('what if surrender is the secret?'); nghỉ 0.35s sau ẩn dụ nước mềm xuyên đá cứng.
- **Camera Transition Pace:** Chuyển động máy quay anamorphic 35mm hoài niệm: push_in trong gian trà thất Kyoto tĩnh lặng, smoothleft dưới mái hiên chùa mưa rơi, smoothup xuyên qua rừng tre uốn gió, smoothdown trên suối nước đá cuội, và fade trầm tĩnh vào hoàng hôn.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: zen_reflective_swell`)
- **Primary / Secondary Stems:** `bgm_zen_night_healing.wav` / `bgm_zen_night_healing.wav`
- **Pre-Climax Silence Vacuum Stem:** `singing_bowl_zen.wav` at ~65% arc (`beat_index` calibrated per episode)
