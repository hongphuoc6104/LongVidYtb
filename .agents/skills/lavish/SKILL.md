---
name: lavish
description: Visual review surface and editor for agent-generated HTML artifacts, reports, and dashboards.
---

# Lavish — Interactive HTML Review Surface

`lavish-axi` allows AI agents to serve rich interactive HTML artifacts and reports directly to the user's browser for human-in-the-loop inspection, visual critique, and feedback.

## Key Capabilities
- **Review Artifact**: `lavish-axi <html-file>` (serves the HTML artifact via local express server and opens in browser).
- **Wait for Feedback**: `lavish-axi poll <html-file>` (long-polls for reviewer comments or approval).
- **Reply to User**: `lavish-axi reply <html-file> --agent-reply "<msg>"`
- **Export Portable**: `lavish-axi export <html-file> --out <dest.html>` (inlines local assets for sharing).

## Conveyor Integration
- Used in **Station 1** of `./pipeline` to open the generated Adversarial Critique report (`sys/reports/critique_review.html`) for visual review when requested.
