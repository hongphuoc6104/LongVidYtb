---
name: vp-development
description: "Upgrade Video Pilot engine code, rules, skills, tests, and migration tools."
---

# Development & Conveyor Quality Assurance

Use development scope from permissions and the requested plan. Preserve current local edits, jobs/auth/evidence. Prefer an isolated checkout or branch; keep a concise requirement/evidence handoff so new chat continues the full objective.

## 1. The 6-Station No-Mistake Conveyor (`./pipeline`)
All code modifications, new features, and bug fixes must pass the 6-station development conveyor before handoff:

- `./pipeline status`: Run before starting work to verify environment runtime, tooling (Python, ruff, pytest, git, ffprobe/ffmpeg, node), and directory invariants.
- `./pipeline run`: Run continuously during development and as a mandatory gate before handoff. Executes all 6 stations in sequence (fail-fast):
  1. **Station 1 (Critique)**: Headless Colab safety flags, secret leakage scanner, visual cast invariant (`sys/reports/critique_review.html`).
  2. **Station 2 (Test & AST Proof)**: AST validation ensuring 100% active assertions (`assert`, `pytest.raises`), executes `pytest`, and records immutable proof log in `sys/logs/proofs/`.
  3. **Station 3 (Docs Sync)**: Validates `PLAYBOOK.md` schema compliance across all 6 mandatory fields.
  4. **Station 4 (Lint)**: Static syntax analysis with `compileall` and `ruff check` (0 errors, 0 warnings).
  5. **Station 5 (PR Preparation)**: Generates Conventional PR draft with test evidence from Station 2.
  6. **Station 6 (CI Watch & Green Certification)**: Generates immutable `green_certified_<timestamp>.json` verification.
- `./pipeline station <1..6>`: Run any station independently for isolated debugging.
- `./pipeline video [--job ID] [--step STEP]`: Production runner for Video Pilot tasks.

## 2. Supreme 4-Step Bug Resolution Protocol & Playbook Discipline
When encountering or fixing any defect, adhere to the 4-step protocol:
$$\text{1. E2E Reproduction} \longrightarrow \text{2. Root Cause Analysis} \longrightarrow \text{3. Architectural Fix} \longrightarrow \text{4. E2E Verification & Playbook Entry}$$

Every resolved bug must be documented in [PLAYBOOK.md](../../../PLAYBOOK.md) conforming strictly to all 6 mandatory schema fields (verified via `playbook_validator.py`).

**Skill Extraction Threshold**: When `PLAYBOOK.md` exceeds 200 lines or accumulates $\ge 3$ lessons on the same topic, the knowledge must be modularized into a dedicated Skill in `.agents/skills/`.

## 3. High-Leverage Architecture & Invariants
- Implement observable behavior, not only wording. Test auto without reviewer, review checkpoints, grant persistence, version compatibility/ownership and no duplicate submissions.
- Remote/local boundary and English portrait audio/timeline require actual routing tests. Keep legacy data read-compatible and migrate via official commands with old/new provenance and rollback.
- Do not claim live Flow/T4/media from fixtures or delete failing tests to simulate compliance. Never fake a human TTY or edit baseline/DB/journal by hand.
- Layered pipeline changes must keep `tests/test_layered_pipeline.py`, `test_matte_sticker.py`, flow prompt and remote render tests green, and be proven by a real E2E job (Flow stickers → Colab matte/render) before claiming support.
