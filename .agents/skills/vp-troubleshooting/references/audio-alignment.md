# Troubleshooting Audio Alignment & Subtitle Pacing

## 1. Symptoms
- Voiceover reads too quickly or too slowly relative to the narrative rhythm.
- SRT subtitles lead or lag spoken narration by 0.5s to 1.0s.
- Total WAV file duration deviates by more than 0.25s from the scene duration planned in the brief.

---

## 2. Proven Remedies

### 1. Calibrate Speech Rates
- Standard English voiceover is calibrated at rate `0.92` (clear, unhurried learner pace).
- Run the calibration script when updating voice models:
  ```bash
  python3 sys/scripts/calibrate_speech_rates.py
  ```

### 2. Handle Silence Padding
- Each dialogue beat between scenes requires a natural pause of at least `0.25s - 0.4s` to allow Remotion to cut visual beats cleanly with spoken lines.
- For interactive learner practice/repetition scenes, maintain a trailing silence buffer of `3.0s - 5.0s`.

### 3. Physical Duration Measurement
Use `ffprobe` to measure exact WAV duration instead of theoretical estimates:
```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 sys/runs/<job>/revisions/audio/<rev>/narration.wav
```
The duration discrepancy between rendered video and audio file must not exceed `0.25s`.
