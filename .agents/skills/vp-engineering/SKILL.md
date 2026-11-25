---
name: vp-engineering
description: "Engine development, 6-station conveyor (`./pipeline`), machine setup, safe maintenance/Git scoping, gh-axi TOON CLI, and troubleshooting runbook."
---

# VP Engineering & Operations (`vp-engineering`)

Unifies Video Pilot engineering QA, machine bootstrap, scoped maintenance/Git, `gh-axi` GitHub operations, and incident troubleshooting.

## 1. The 6-Station Conveyor (`./pipeline`) & 4-Step Bug Protocol
- `./pipeline status`: Verify runtime tools (Python `.venv`, `ruff`, `pytest`, `git`, `ffmpeg/ffprobe`, `node`).
- `./pipeline run`: Mandatory pre-handoff gate executing all 6 stations:
  1. **Station 1 (Critique):** Headless Colab/Chrome safety flags, secret leak scan, root directory hygiene, visual cast invariant.
  2. **Station 2 (Tests & AST Proof):** AST check requiring 100% active assertions (`assert`, `pytest.raises`), runs `pytest`, writes immutable proof log to `sys/logs/proofs/`.
  3. **Station 3 (Docs Sync):** Validates `PLAYBOOK.md` `<= 200` lines and 6-field schema via `playbook_validator.py`.
  4. **Station 4 (Lint):** `compileall` + `ruff check` (`0` errors).
  5. **Station 5 (PR Draft):** Generates Conventional PR summary with Station 2 proof.
  6. **Station 6 (CI Watch):** Verifies clean Git tree + GitHub Actions green run (`green_certified_*.json`).
- **4-Step Bug Protocol:** `1. Reproduce E2E -> 2. Root Cause -> 3. Fix at Source -> 4. Verify E2E & log 6 fields in PLAYBOOK.md`. Keep `PLAYBOOK.md <= 200` lines; archive older lessons to [historical-playbook.md](references/historical-playbook.md).

## 2. Setup, Maintenance & `gh-axi`
- **Bootstrap (`./pipeline setup`):** Configures `.venv`, tools, and interactive account onboarding (`python3 -m colab_bridge.accounts login-many`, Chrome profiles in `~/.config/video-pilot/`). Never auto-complete OAuth/OTP/CAPTCHA.
- **Maintenance (`sys/maintenance.py`, [maintenance.md](../../../sys/docs/maintenance.md)):** Read-only audit by default; `python3 sys/scripts/clean_production.py --periodic` prunes expired scratch/logs safely keeping latest 5 proof logs. Never wildcard-delete runs/profiles/ledgers. Stage explicit paths (`<= 2000` added lines per `.githooks/pre-commit`); never force-push.
- **`gh-axi` (Token-Optimized GitHub CLI):** Use `gh-axi pr list|view|create` and `gh-axi run list|watch|view` in TOON format during Station 5–6.

## 3. Troubleshooting Quick Index
| Code | Symptom | Reference |
|---|---|---|
| **COLAB-HEADLESS / RENDER** | T4 white screen, `NVENC` error, `>=2` `COLAB_EXEC_UNCONFIRMED` | [colab-headless.md](references/colab-headless.md) · [vp-colab-bridge](../vp-colab-bridge/SKILL.md) |
| **FLOW-CDP-GEN** | Error 7/8 `UNUSUAL_ACTIVITY`, timeout, `CHROME-TMP-BLOAT` | [flow-cdp-generation.md](references/flow-cdp-generation.md) · [vp-flow-cdp](../vp-flow-cdp/SKILL.md) |
| **AUDIO-ALIGN** | Subtitle/beat drift, TTS cutoff, `-11.0 LUFS` mismatch | [audio-alignment.md](references/audio-alignment.md) |
| **CI / VISUAL / NEW-ISSUE** | Full-frame/transport CI failure or new incident template | [visual-ci-regressions.md](references/visual-ci-regressions.md) · [issue-template.md](references/issue-template.md) |
