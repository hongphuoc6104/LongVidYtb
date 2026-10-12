# Video Pilot — Agent Invariants & Governance

## 1. Architecture & Layout (SSOT)
- **Mission**: Automate short and long-form explainer video production per brief specs.
- **Directory Invariant**: `sys/` (engine/tools/data), `sys/runs/<job>/` (assets), `video/<job>/` (final MP4/SRT). Keep root clean of temporary files.

## 2. Technical Ethos & Conveyor
- **Code Standards**: No monkey-patches, fake test passes, or manual DB edits. Modular, type-hinted code only.
- **6-Station Conveyor (`./pipeline run`)**: St1 (Critique via `critique_review.html` & `lavish-axi`) -> St2 (AST Proof & Pytest) -> St3 (Docs Sync / `PLAYBOOK.md`) -> St4 (Lint / `ruff`) -> St5 (PR Prep / `treehouse` & `gh-axi`) -> St6 (CI Watch / Green Certification).
- **Tooling Stack**: `treehouse` (worktrees), `gh-axi` (TOON GitHub CLI), `lavish-axi` (HTML review surface).

## 3. Pipelines & Role Separation
- **Topic-to-Video Chain (`vp-production`)**: New explainer topics run `vp-research-architect` (Schema 3.0 `brief.json`/`content.json`, `sys/format_profiles.py`) -> `vp-scriptwriting` (`vn_text_normalizer.py` + `script_cadence_checker.py` drift <= 0.3s) -> `vp-layered-motion` (`background` + `sticker` layers/beats) -> `pilot.py` Engine 4 (`outline -> dialogue -> audio -> images -> video`; vocab jobs start via `vocab/bank.py start`).
- **Video & Audio (Colab T4 GPU Priority — vp-colab-bridge)**: Launch via python3 pilot.py or sys/colab_bridge/. Standard engine: sys/renderer/render.mjs (strictly no ad-hoc ffmpeg scripts).
- **Image Generation (`vp-flow-cdp`)**: 3 Chrome profiles pool (`sys/flow_cdp/`), patch partitioning (2-4 shots/patch), auto-failover on `PUBLIC_ERROR_UNUSUAL_ACTIVITY`, minimal contract (valid AI image + `.json` sidecar; never draw mock images with PIL).

## 4. Headless Colab Safety & Multi-T4 Parallel Acceleration
- **Mandatory Headless Execution (Rule 4)**: Colab T4 lacks physical display (no X11). Remotion and Chromium must always execute via `sys/colab_bridge/chrome-wrapper.sh` with verified flags (`--no-sandbox`, `--disable-dev-shm-usage`, `--disable-gpu-rasterization`, `--run-all-compositor-stages-before-draw`, `DISABLE_FROM_SURFACE=true`). Prohibit ad-hoc virtual display hacks that trigger ANGLE/GL socket hangs and timeout aborts.
- **High-Throughput Multi-T4 Pool**: Achieve parallel render acceleration by offloading multi-chapter workloads concurrently across isolated Colab T4 accounts (`ColabPoolManager` & `ColabPoolDispatcher`), ensuring clean orphan process cleanup (`pkill -9`) and automated quota failover.

## 5. Execution Modes & Bug Discipline
- **Modes**: Auto (autonomous E2E), Review (checkpoint pauses: script, audio, images, video), Stop & Handoff (immediate halt preserving assets).
- **Bug Protocol**: 4-step protocol (Reproduction -> Root Cause -> Fix -> Playbook) and 6 fields in `PLAYBOOK.md`. No mocks/tampering. Extract to `.agents/skills/` when `PLAYBOOK.md` > 200 lines or >= 3 lessons/topic.

## 6. Anti-Hallucination & Anti-Laziness Guard
- **Script & Diversity Fidelity**: Preserve 100% vocabulary, facts (`<= 20` syllables), captions, and templates in `sys/prompt_templates.py`. Strict Forward Chronology and zero formulaic bridges; 100% PASS on `sys/tools/script_diversity_linter.py`.
- **Visual Cast Invariant**: Anonymous stick-figures only (round white head, thick black outline, dot/oval eyes, thin limbs, bright background). Rule-of-Thirds stickers (`0.35`, `0.64`) and semantic camera motion (no `% 5` cycling or mechanical clichés).
- **Verification Integrity**: File existence != valid content. Inspect outputs via `ffprobe` (dimensions, audio sync, H.264/AAC). Report genuine stdout/stderr.

## 7. Communication & Language Standards
- **User Communication**: Natural, concise **Vietnamese**, addressing core tasks directly.
- **Technical & Source**: **English** for code, variables, commits, schemas, and prompts; **English/Vietnamese** permitted for playbooks and storytelling skills.
- **Script Materials**: Preserve 100% exact English spelling (including pronoun `I`).
