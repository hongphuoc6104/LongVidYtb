# Full-frame storyboard upgrade and acceptance plan

Status: Implementation and media production completed on 2026-10-16. Acceptance video and SRT delivered; conveyor stations 1–5 verified green.

Execution results: Acceptance video `full-frame-acceptance-video-20261016_r1_final.mp4` (328.23s, 1920x1080 30fps h264/aac, 19 scenes, authentic Flow CDP imagery + Colab T4 OmniVoice TTS + Colab Remotion render) and `subtitles.srt` successfully published to `video/full-frame-acceptance-video-20261016/`. Complete video decoded cleanly with ffprobe/ffmpeg without defects. Conveyor Station 1 (Critique), Station 2 (AST proof & 115 tests passed, 0 failed), Station 3 (Playbook schema 23/23), Station 4 (Ruff/compileall 0 errors), Station 5 (Treehouse & PR draft) all passed green. Evidence: `sys/logs/proofs/test_evidence_20261016_195317.log`.

## Scope and acceptance artifact

Complete the missing full-frame storyboard migration and verify the entire development and production workflow. The acceptance artifact is a newly produced Vietnamese 16:9 video lasting 300–480 seconds, replacing the previously proposed 45–60 second portrait sample. Target duration: approximately six minutes. Proposed topic: why highlighting a textbook can create an illusion of understanding, and how to expose that illusion with a concrete recall task.

Use a dedicated acceptance job under `sys/runs/`; collect the final MP4 and SRT under `video/<job>/`. Declare the experimental duration explicitly in the brief without changing the standard 11–13 minute long-format profile. Review format constraints before choosing the supported job path; do not bypass validators or edit stored job state.

## 1. Re-audit and baseline

- Preserve existing local modifications, job history, authentication, and useful assets.
- Recheck every item from the original migration plan against current code, documentation, tests, and evidence.
- Run `./pipeline status` and `./pipeline run`; record actual station outcomes, errors, source revision, and dirty-tree status.
- Separate implementation defects from missing historical media fixtures; resolve failures honestly without deleting assertions to obtain a passing result.

## 2. Complete the storyboard model and builders

- Standardize the full-frame beat model, including shot type, exact narration anchor, effect, visible text, and optional `based_on`/`preserve`/`change`.
- Migrate demo and active builders from background/sticker source data to authored semantic beats. Keep necessary legacy read compatibility explicit.
- Generate only `kind: "scene"` images with empty layers; validate image/beat coverage and reference ordering.
- Select macro props, integrated full scenes, in-place variations, and white concept cards according to narration.
- Add density validation: four image starts in the first five seconds and eight to nine in approximately the first twelve seconds; inspect actual audio timing and document the exact boundary convention.
- Unify body hold limits in one contract; reconcile the original density target with the existing 0.83–3.80 second hold policy before enforcing checks.

## 3. Complete audio alignment and cadence

- Prefer measured word timestamps for beat placement; explicitly label interpolation fallback when timestamps are unavailable.
- Handle repeated anchors, punctuation, multiple audio chunks, timestamp bounds, and frame collisions.
- Remove penalties based solely on short sentence counts while retaining meaningful cadence checks.
- Enforce zero pause tags in SC01 and add low visual density diagnostics.

## 4. Complete Flow prompts, rendering, and documentation

- Ensure white concept cards override environmental background instructions; ensure variations preserve the declared composition.
- Respect prompt registry versioning and compatibility rules when updating templates.
- Remove active cutout/layer/matte production routes and obsolete skill references; retain legacy utilities only where justified by explicit compatibility needs.
- Reconcile AGENTS, INDEX, production/research/scriptwriting/channel skills and every linked reference.
- Update the existing ERR-20261016-02 lesson with accurate evidence and remaining limitations.

## 5. Development verification

- Run focused behavioral tests for builders, densities, word alignment, prompt compilation, content validation, remote packaging, and rendering contracts.
- Run the entire configured conveyor, including critique, AST/test proof, documentation validation, lint, PR preparation, and CI certification.
- Inspect the conveyor's configured test coverage; run additional relevant suites if the conveyor does not include them.
- Record failures and exact evidence. A partial passing test set does not certify the full pipeline.

## 6. Produce the 5–8 minute acceptance video

- Finalize a research-supported Vietnamese narrative with concrete visual actions, an opening hook, demonstration, explanation, practical application, and closing payoff.
- Use the supported production job/version operations for outline, dialogue, normalized narration, audio, images, timeline, and video.
- Synthesize narration on Colab T4; generate genuine images through Flow CDP, with sidecars and dependency continuity.
- Render through the official remote Colab/Remotion route. Preserve owner/session/request identity on ambiguous failures.
- Exercise all principal shot types, several in-place variation chains, ordinary scene cuts, and captions in the sample.
- Collect all required outputs and terminate tasks/sessions created for this work through their supported lifecycle commands.

## 7. Media acceptance and delivery

- Verify MP4 duration is 300–480 seconds, horizontal dimensions, valid video/audio streams, and complete decoding using the supported inspection route.
- Inspect the full video for missing images, tile gaps, unintended blank frames, duplicated imagery, sticker halos, continuity breaks, subtitle defects, and narration pronunciation.
- Measure and review the first five and twelve seconds against the actual WAV; inspect representative body transitions and the ending.
- Deliver the playable MP4, SRT, job/version identifiers, final source revision, test/conveyor results, and a concise evidence report.
- Package a source snapshot excluding credentials, account state, caches, and unrelated large assets.
- Technical checks and the user's viewing decision are separate acceptance records. Do not claim user acceptance before feedback.

## Completion criteria

All migration requirements are either implemented and evidenced or explicitly recorded as unresolved; required development checks pass; the real 5–8 minute sample is collected and inspected; final artifacts are available for the user to watch. Missing Flow/Colab access is a reported blocker, never a reason to substitute mock images or local rendering.
