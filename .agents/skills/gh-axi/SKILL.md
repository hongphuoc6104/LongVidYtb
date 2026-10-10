---
name: gh-axi
description: Token-optimized GitHub CLI wrapper using TOON format for Issues, Pull Requests, CI runs, and releases.
---

# GH-AXI — Token-Efficient GitHub Operations

`gh-axi` wraps GitHub CLI (`gh`) to output data in TOON (Token-Oriented Object Notation) format, saving 70-80% context tokens for AI coding agents.

## Key Capabilities
- **Issues**: `gh-axi issue list`, `gh-axi issue view <number>`
- **Pull Requests**:
  - `gh-axi pr list`: List active pull requests.
  - `gh-axi pr view <number>`: View structured details of a PR.
  - `gh-axi pr create --title "<title>" --body "<file-or-text>"`: Create a new pull request.
- **CI / Actions**:
  - `gh-axi run list`: List recent CI runs in compact format.
  - `gh-axi run watch <run-id>`: Monitor workflow run until completion.
  - `gh-axi run view <run-id>`: View run failure causes with minimal token consumption.

## Conveyor Integration
- Used in **Station 5** of `./pipeline` to submit conventional pull requests with test evidence.
- Used in **Station 6** of `./pipeline` to monitor GitHub Actions until Green.
