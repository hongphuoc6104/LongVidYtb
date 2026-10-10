# Video Pilot — Agent Invariants & Governance

## 1. Project Architecture & Layout
- **Mission**: Automate short explainer video production for vocabulary and knowledge concepts, covering scriptwriting, narration, image generation, and final video rendering. Target aspect ratio and resolution are configured per job brief without fixed defaults.
- **Folder Structure (Single Source of Truth)**:
  - `sys/`: Pipeline source code, tools, configuration, and runtime data.
  - `sys/runs/<job>/`: Scripts, audio, scenes, prompts, and intermediate assets for each job.
  - `video/<job>/`: Final MP4 videos and complete SRT subtitles.
  - Never create temporary files or operational clutter in the project root directory.

## 2. Technical Ethos & Development Conveyor
- **High-Leverage Execution**:
  - Never apply superficial monkey-patches or edit databases/logs by hand to fake test passes.
  - Write modular, type-hinted, and cleanly structured code adhering to production standards.
- **6-Station No-Mistake Conveyor (`./pipeline run`)**:
  - All feature upgrades and bug fixes must pass the 6-station conveyor before handoff:
    1. *Station 1 (Critique)*: Adversarial security and headless safety check (`sys/reports/critique_review.html`).
    2. *Station 2 (Test & AST Proof)*: 100% active assertions on test functions + immutable proof log.
    3. *Station 3 (Docs Sync)*: Schema validation of `PLAYBOOK.md` (6 mandatory fields).
    4. *Station 4 (Lint)*: `compileall` syntax check and `ruff check` (0 errors, 0 warnings).
    5. *Station 5 (PR Preparation)*: Worktree isolation & conventional PR draft generation.
    6. *Station 6 (CI / Green Certification)*: CI watch or local Green Certification verification.

## 3. Execution Pipelines & Role Separation
- **Video Rendering & Audio Processing (Colab GPU T4 Priority)**:
  - Launch and coordinate via `python3 pilot.py` or the Colab worker (`sys/colab_bridge/`).
  - The entire speech synthesis (TTS) workflow, timeline pacing calculations, and Remotion video rendering prioritize execution on the **Colab GPU T4 preset**.
  - Local video rendering (if authorized) must adhere strictly to Video Pilot's standard engine (`sys/renderer/render.mjs`); never write ad-hoc ffmpeg scripts detached from the primary pipeline.
- **Image Generation (Flow CDP — Skill `vp-flow-cdp`)**:
  - Chrome DevTools Protocol (`sys/flow_cdp/`, Skill `vp-flow-cdp`) handles **image asset generation** across 3 Chrome profiles in parallel.
  - Automatic patch partitioning (2-4 shots/patch) and profile failover upon abnormal activity or rate limiting (`PUBLIC_ERROR_UNUSUAL_ACTIVITY`).
  - Minimal verification contract: valid downloaded image and metadata sidecar (`.json`); no mandatory UI screenshot (`ui-proof.json`).

## 4. Headless Colab Environment Safety
- **Headless Risk Warning**: The Colab T4 environment runs without a physical display (headless, no X11), making Remotion/Playwright Chromium video rendering prone to white tile drops, compositor sync issues, and `/dev/shm` memory exhaustion.
- **Mandatory Safety Flags**:
  - Remotion and Chromium must always be wrapped via an executable shell wrapper script (`chrome-wrapper.sh` / `wrapChromeExecutable`).
  - Mandatory flags: `--no-sandbox`, `--disable-dev-shm-usage`, `--run-all-compositor-stages-before-draw`, `--disable-gpu-rasterization`, `--enable-gpu`, `--ignore-gpu-blocklist`.
  - Mandatory environment variables: `DISABLE_FROM_SURFACE='true'` and `VP_CHROME_PATH`.

## 5. Execution Modes, Bug Discipline & Playbook Governance
- **Execution Modes**:
  - `Auto`: Autonomously plan and execute to final completion without requiring per-step user approval.
  - `Review`: Pause for user confirmation at key checkpoints: script (outline/dialogue), audio, image set, and final video.
  - `Stop & Handoff`: Upon stop instructions, halt sending new tasks immediately while preserving all finished assets and progress for seamless resumption.
- **Supreme 4-Step Bug Resolution Protocol**:
  $$\text{1. E2E Reproduction} \longrightarrow \text{2. Root Cause Analysis} \longrightarrow \text{3. Architectural Fix} \longrightarrow \text{4. E2E Verification & Playbook Entry}$$
  - Issues must be reproduced and verified on the actual execution pipeline of the project. Never rely solely on artificial mock tests to claim an issue is resolved.
  - Never manually alter SQLite databases, log files, baseline hashes, or test assertions to fake test passes.
- **Playbook Governance (`PLAYBOOK.md` & `sys/logs/issues/`)**:
  - Every resolved bug must be documented under `PLAYBOOK.md` conforming strictly to the 6 mandatory fields:
    1. `Triệu chứng (Symptom)`
    2. `Tái hiện E2E (Reproduction Path)`
    3. `Nguyên nhân cốt lõi (Root Cause)`
    4. `Giả định sai (Wrong Assumptions)`
    5. `Giải pháp & Kiểm chứng (Resolution & E2E Proof)`
    6. `Quy tắc phòng ngừa vàng (Golden Rule)`
  - **Skill Extraction Threshold**: When `PLAYBOOK.md` exceeds 200 lines or accumulates $\ge 3$ lessons on the same topic, the knowledge must be modularized into a dedicated Skill under `.agents/skills/`.

## 6. Anti-Hallucination & Anti-Laziness Guard
- **Preserve Scripts & Boundaries (Anti-Corner-Cutting)**:
  - Preserve 100% of vocabulary words, script dialogue, narration, and captions. Never simplify wording, replace advanced vocabulary with easy words, or skip scenes to avoid difficult work.
  - Preserve standard prompt templates in `sys/prompt_templates.py`.
- **Visual Cast Invariant**:
  - Default to the standardized anonymous stick-figure cast: large round white head with thick black outline, dot/oval eyes, thin stick limbs, exactly one torso on bright background.
  - Do not generate photorealistic human characters, detailed faces, or off-spec animated figures.
- **Verification Integrity (No Fabricated Reports)**:
  - File existence does not equal valid content. Never claim a video is "smooth, beautiful, or synced" merely because a file exists on disk.
  - Verify actual technical specifications using inspection tools (`ffprobe` verifying dimensions matching the job brief specification, duration matching audio, H.264/AAC codecs).

## 7. Communication & Language Standards
- **User Communication**: Always communicate with the user in natural, concise **Vietnamese**, addressing the core tasks directly.
- **Technical & Source Code**: Source code, variables, git commits, schemas, technical documentation, rules, skills, logs, and internal prompts must be in **English**.
- **Script Materials**: Preserve 100% exact English spelling (including pronoun `I`, never turn into `Ai`).
