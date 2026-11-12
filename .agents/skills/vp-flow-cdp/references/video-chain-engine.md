# Flow Video Chain Engine (`vp-flow-video`)

Located in `sys/flow_video/` with execution via `sys/tools/run_flow_video_chain.py`, the Flow Video Chain Engine transforms sequences of still keyframes into continuous cinematic video powered by `Omni 1.2 Flash` (`omni_1_2_flash` / `omni_flash`, family `macaron_cookie`).

## 1. Dual Chaining Modes
- **Mode A — `daisy_chain` (`F0 -> F1 -> F2 -> ... -> FN`)**:
  - Clip 0 keeps full frames (`trim_first_frame = False`); clips $i \ge 1$ apply `trim=start_frame=1,setpts=PTS-STARTPTS` for zero-stutter seams.
- **Mode B — `scene_pairs` (`(A1 -> B1), (A2 -> B2), ...`)**:
  - Smooth speed-fit ($0.7 \le \text{raw}/\text{target} \le 1.35$): `setpts=(target/raw)*PTS`.
  - Final-frame hold ($\text{target} > \text{raw} \times 1.35$): `tpad=stop_mode=clone`.
  - Speed cap ($\text{target} < \text{raw} \times 0.7$): max $1.35\times$ + trim.

## 2. Default Model, Auto-Duration & Credit Cost
- `start_end_frames` (`nprQif`) / `start_frame` (`eb1hJf`):
  - $\le 4.8\text{s} \rightarrow 4\text{s}$ (`12c`, `macaron_cookie_i2v_fl_4s` / `macaron_cookie_i2v_4s`)
  - $\le 6.8\text{s} \rightarrow 6\text{s}$ (`18c`, `macaron_cookie_i2v_fl_6s` / `macaron_cookie_i2v_6s`)
  - $\le 8.8\text{s} \rightarrow 8\text{s}$ (`24c`, `macaron_cookie_i2v_fl_8s` / `macaron_cookie_i2v_8s`)
  - $> 8.8\text{s} \rightarrow 10\text{s}$ (`30c`, `macaron_cookie_i2v_fl_10s` / `macaron_cookie_i2v_10s`)
- Alternate Veo 3.1 models (8s): `veo_3_1_lite` (10c), `veo_3_1_fast` (20c), `veo_3_1_quality` (100c).

## 3. Audio & Lip-Sync Governance
- Native Veo audio is muted by default (`keep_veo_audio=False`).
- `no_talking_prompt_guard` appends `", silent visual storytelling, no talking, no lip movement"` unless `--allow-talking` is passed.
- External voiceover (`--audio <path>`) normalizes to `-11.0 LUFS` / `-1.0 dBTP` (`--normalize-lufs`).

## 4. CLI Examples
```bash
# Daisy chain from frame directory:
PYTHONPATH=sys python3 sys/tools/run_flow_video_chain.py \
  --frames-dir sys/runs/explainer_v1/frames --mode daisy_chain \
  --aspect 16:9 --model omni_flash --auto-duration \
  --audio sys/runs/explainer_v1/audio/voiceover.wav \
  --output video/flow_video/explainer_chain.mp4 --max-workers 6

# Scene pairs from JSON spec:
PYTHONPATH=sys python3 sys/tools/run_flow_video_chain.py \
  --spec sys/runs/story_job/video_chain_spec.json \
  --output video/flow_video/story_final.mp4 --max-workers 8

# Dry-run (0 credits):
PYTHONPATH=sys python3 sys/tools/run_flow_video_chain.py \
  --frames-dir tests/fixtures/sample_frames --mode daisy_chain --dry-run
```
