# Troubleshooting Audio Alignment & Subtitle Pacing

## 1. Symptoms
- Voiceover reads too quickly or too slowly relative to the narrative rhythm.
- SRT subtitles lead or lag spoken narration by 0.5s to 1.0s.
- Total WAV file duration deviates by more than 0.25s from the scene duration planned in the brief.

---

## 2. Proven Remedies

### 1. Calibrate Speech Rates
- Canonical voice (`Adam`, `assets/voices/adam/profile.json`) is fixed at `speed: 1.22` (`sys/config.json`) for both `vi` and `en`.
- Run the calibration script when verifying speech rates:
  ```bash
  python3 sys/scripts/calibrate_speech_rates.py
  ```

### 2. Trim Boundary Silence & Apply Calibrated Pauses (`ERR-20261011-02`)
- `OmniVoice.generate()` emits `50–180ms` leading and `180–420ms` trailing silence. Always trim boundary silence via `_trim_silence(w, sr=48000, threshold=0.012, lead_ms=25, trail_ms=30, fade_ms=8)` before caching or stitching.
- After trimming, apply calibrated inter-sentence pauses: `0.20s` for short sentences (`< 8` words), `0.28s` for standard sentences, and `0.48s` for dramatic pivots (`[pause:...]`).
- For interactive learner practice/repetition scenes, maintain a trailing silence buffer of `3.0s - 5.0s`.

### 3. Physical Duration Measurement
Use `ffprobe` to measure exact WAV duration instead of theoretical estimates:
```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 sys/runs/<job>/revisions/audio/<rev>/narration.wav
```
The duration discrepancy between rendered video and audio file must not exceed `0.25s`.

### 4. Cue-Window Allocation & 1:1 Semantic Cue-Shot Mapping (Eliminating Mid-Scene Visual Desync)
- **Root Cause**: Scaling `images[].at` only at coarse scene boundaries (`SC01..SC30`, 18–45s per scene) or capping `max_hold <= 3.80s` across a whole scene shifts excess duration into neighboring shots, causing images to drift 3–27s away from their spoken sentences. Additionally, conversational Vietnamese adaptation often reorders clauses relative to English storyboards.
- **Remedy**:
  1. Partition every scene into exact **Cue Windows** `[cue_i.start, cue_{i+1}.start)` from `ch{N}_spoken_cues.json` (where the last cue in a scene ends at `scene.end`).
  2. Assign 1–6 semantically matching shots to each cue in a declarative mapping (`sys/exports/ancient_humans_bundle/manifest/cue_shot_mapping_8ch.json`) and allocate hold durations strictly inside that cue's window (`sys/exports/ancient_humans_bundle/scripts/rebuild_option_b_templates.py`).
  3. Guarantee `abs(first_shot_abs_at - cue.start) == 0.00s` for 100% of cues, `0.8s <= hold <= 3.80s` (`<= 4.0s`) for all shots, and verify `mp4.stat().st_mtime >= template.stat().st_mtime` via `pytest sys/tests/test_option_b_manifest_and_templates.py`.
