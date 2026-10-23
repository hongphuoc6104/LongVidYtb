# Project: Video Pilot Full Pipeline Integration (Audio & Video into Core)

## Architecture
- **Language / Runtime**: Python 3.12+ (local venv) / Node.js 20+ (Remotion renderer)
- **Branch Strategy**: Strict development on `module-core` in `/home/hongphuoc6104/Desktop/vp-agent-core`.
- **Integrity Guarantee**: Selective porting of `module-audio` (`223ff27` & `474d15e`) and `module-video` (`1c69f38`). Branch-isolation deletions from `104b007` and `1c69f38` are strictly prohibited.
- **Pipeline Flow**:
  1. Content & Narrative: `sys/content/research_story_architect.py` (Schema 3.0, 1.7.0 handdrawn visual contracts, anti-formulaic storytelling)
  2. Spoken Cadence: `sys/tools/vn_text_normalizer.py`, `sys/tools/script_cadence_checker.py`
  3. Audio Synthesis & Mastering: `sys/audio_pipeline.py`, `sys/audio_processing.py` (Voice-forward -11 LUFS / -1.0 dBTP, Colab T4 OmniVoice TTS)
  4. Visual Asset Generation: `sys/image_pipeline.py`, `sys/flow_cdp/`, `sys/flow_prompts/` (5-tier Flow CDP dynamic profile pool)
  5. Remotion Video Rendering: `sys/renderer/` (`render.mjs`, `outputs.mjs`, `srt.mjs`), `sys/render_cli.py`, `sys/omni_render.py` (Local & Colab T4 headless EGL + NVENC)
  6. Unified Orchestrator: `sys/pilot.py` (seamless outline -> dialogue -> audio -> images -> video chain)

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Baseline Core Preservation | Verify & commit 1.7.0 handdrawn contracts, see-say alignment, and sycophancy blueprint | M1 | Core Workspace |
| 2 | Audio Pipeline Engine | Voice-forward 7-stage mastering chain, -11 LUFS config, parallel TTS dispatcher, micro-SFX | M2 | module-audio |
| 3 | Audio Cadence & Tests | `vn_text_normalizer`, `script_cadence_checker`, and 19 audio test suites | M2 | module-audio |
| 4 | Remotion Standalone Renderer | `render_cli.py`, `sys/renderer/*`, `srt.mjs`, `thumbnail_spec`, 6-8 thread T4 parallelism | M3 | module-video |
| 5 | Colab Bridge Multi-Job | Support both TTS worker (`worker.py`) and Render worker (`job_worker.py`), pool auto-reconnect | M3 | module-video |
| 6 | Video Packaging & Tests | `omni_render`, `camera_motion`, `subtitles`, and video test suites / fixtures | M3 | module-video |
| 7 | Shared Contracts Reconciliation | Merge `sys/config.json` (-11 LUFS + video + flow), format profiles, explainer/output contracts | M4 | Core / Audio / Video |
| 8 | Unified `sys/pilot.py` | Full E2E pipeline runner without deprecated audioop, connecting all stages | M4 | Core / Audio / Video |
| 9 | Full Test Suite & Lint Pass | 100% green pytest across all suites (`pytest sys/tests/`) and `ruff check` | M5 | Core Repo |
| 10 | Git Cleanliness & Push | Clean working tree and push `module-core` to `origin/module-core` | M5 | Git Remote |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Baseline Verification & Commit | Clean up ruff in sycophancy, stage, and commit core baseline changes | none | READY |
| 2 | Audio Pipeline Selective Integration | Port audio engine, config, tools, and 19 test suites | M1 | READY |
| 3 | Video Pipeline Selective Integration | Port renderer, package.json, colab bridge, omni_render, video tests | M1 | READY |
| 4 | Shared Contracts & Orchestrator Reconciliation | Reconcile config.json, pilot.py, contracts, and test fixtures | M2, M3 | PENDING |
| 5 | Full Verification, Clean Git & Push | Run full pytest, ruff, clean status, commit and push to origin/module-core | M4 | PENDING |

## Interface Contracts
### `sys/config.json`
- `"audio_lufs": -11.0`
- `"audio_peak_db": -1.0`
- Renderer and Flow CDP profiles unified.

### `sys/colab_bridge/`
- `worker.py` (OmniVoice TTS worker) from `module-audio`
- `job_worker.py` (Remotion render worker) from `module-video`
- `client.py`: auto-reconnect on `COLAB_SESSION_NOT_FOUND`
- `pool_manager.py`: ledger release and multi-job dispatcher
- `job_protocol.py`: contains `scripts/story_plan.py` in required remote sources

### `sys/pilot.py`
- Replaces `audioop.rms` with numpy `_rms` helper.
- Integrates `run_audio` and `run_video` cleanly with 1.7.0 content and Flow CDP image pipelines.

## Code Layout
- `sys/content/`: Narrative & storytelling logic (1.7.0 contracts)
- `sys/flow_cdp/`, `sys/flow_prompts/`: Image generation engine
- `sys/image_pipeline.py`: Flow CDP coordinator
- `sys/audio_pipeline.py`, `sys/audio_processing.py`: Audio mastering and TTS coordinator
- `sys/renderer/`: Remotion rendering scripts (`render.mjs`, `outputs.mjs`, `srt.mjs`)
- `sys/colab_bridge/`: Remote GPU orchestration
- `sys/tests/`: Hermetic unit and integration tests
- `video/<job>/`: Final MP4/SRT outputs
- `sys/runs/<job>/`: Intermediate run assets
