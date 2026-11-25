# Pacing, Voice & Audio Mastering — The Second Arrow (`en_second_arrow`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `EnNarrator_en_second_arrow` (`sys/assets/voices/ch_en_second_arrow/profile.json`)
- **Recommended Speaking Rate:** `1.04x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `480s–720s` (~8–12 min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `35s–50s`
- **Pause & Cadence Discipline:** Nhịp đọc suy tư sâu lắng 143 WPM với quãng nghỉ có chủ đích: Nghỉ ngắn 0.22s sau mệnh đề nhát tên đầu; nghỉ 0.42s sau phân định vết thương; nghỉ sâu 0.45s sau câu hỏi tu từ để tâm trí tự soi chiếu; nghỉ 0.38s trước khi đưa ra tấm gương Marcus Aurelius.
- **Camera Transition Pace:** Chuyển động máy quay phong cách chiaroscuro Caravaggio uy nghiêm: push_in vào mũi tên trúng bia đá, zoom_out nhìn bão táp La Mã, push_in cận cảnh tượng đồng Seneca, tilt_up đe rèn sắt, pan_right tượng cẩm thạch dưới mưa, và fade vào bình minh quang đãng trên thềm đền cổ.

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `archetype_dual_5act` (`theme_id: zen_reflective_swell`)
- **Primary / Secondary Stems:** `bgm_zen_night_healing.wav` / `bgm_zen_night_healing.wav`
- **Pre-Climax Silence Vacuum Stem:** `singing_bowl_zen.wav` at ~65% arc (`beat_index` calibrated per episode)
