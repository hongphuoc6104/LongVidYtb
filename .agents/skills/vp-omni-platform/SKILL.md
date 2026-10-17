---
name: vp-omni-platform
description: Author and verify shared-image YouTube, Facebook and standalone Reels/TikTok deliverables.
---

# Omni-platform contracts

- New briefs opt in with `omni_platform: true`, `reframe_mode: true`, a Vietnamese `16:9` master and explicit outputs. Existing snapshots remain immutable.
- Author 2–3 `spinoff_shorts`, each with unique `id`, `hook_title`, `opening_hook` (at most 18 syllables, no pause tag) and four `body` entries. Each entry declares `parent_scene_id`, `image_id`, and `segment_text` matching an unambiguous contiguous run of complete spoken TTS sentence chunks. This creates five standalone scenes after prepending the new hook. Choose a self-contained argument; never use raw middle chapters.
- Use `research_story_architect.py --omni-plan <JSON>` to freeze those authored references before creating the job. This flag does not invent editorial references from unrelated template shorts. After normal job setup, `pilot.py run <JOB>` routes synthesis and rendering through Colab.
- Hooks synthesize in the master TTS request at canonical speed `1.0` (`VietNarrator`). Body audio comes from the mastered parent WAV at speed `1.0` on Colab. Reject hooks over 3 seconds, shorts outside measured 45–60 seconds, and body visual holds outside 0.83–3.80 seconds.
- Generate one 16:9 image set. Portrait close-ups use normalized focus coordinates; wide shots use an editorial canvas. Preserve the full-frame image contract and provider sidecars.
- Portrait captions use acoustic word timestamps when available, left 56, width 820, bottom 400. Logo moves to top 120/right 32 at 1080×1920. Unsupported/mismatched word timestamps show plain captions.
- Original procedural WAV assets have reproducible sources. Ambient gains are relative amplitude, not verified LUFS targets. Foley names are editorial approximations. Unrecognized descriptive cues are not synthesized as arbitrary sounds.
- Publish verified supplemental MP4/PNG/SRT/Markdown artifacts through the approved manifest and atomic publication path. Do not overwrite a different previously published asset.
- Local contract/PCM tests do not certify actual T4, Flow, visual layout, final mix loudness or platform engagement. Inspect real rendered media before asserting production readiness. CI certification requires a clean committed tree and actual successful GitHub runs.
