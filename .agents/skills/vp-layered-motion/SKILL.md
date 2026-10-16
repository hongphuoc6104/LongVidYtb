---
name: vp-layered-motion
description: "Deprecated. Do not use for new Video Pilot jobs."
---

# Deprecated: layered cut-out workflow

This skill is retained only as a migration notice for older job records. It is no longer part of the standard production workflow.

For new jobs, author complete full-frame images as `kind: "scene"` and synchronize them with narration through `beats[]`. Use `based_on` with explicit `preserve` and `change` for in-place variations. Do not create `kind: "background"` or `kind: "sticker"` assets, populate `layers[]`, or run `matte_sticker.py`.

Follow [vp-production](../vp-production/SKILL.md) and its [full-frame visual beat guide](../vp-production/references/visuals.md) for current instructions. Existing layered job records are not migrated or rendered by the standard pipeline.
