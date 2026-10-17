# Narration pause verification — 2026-10-18

## Scope

Contract tests use a synthetic model to generate real PCM for assembly checks.
No live Colab synthesis, audible quality approval or production MP4 regeneration
is claimed. Existing job assets and journals remain unchanged.

## Recorded results

- Focused initial run: 42 tests, one floating-point adjacent-tag addition failure;
  fixed by stable rounding of adjacent explicit pauses. Subsequent policy tests passed.
- Conveyor stations 1–5: passed (critique, AST integrity, 205 tests plus 8 subtests,
  six-field playbook validation, compile/lint, draft preparation).
- Wider audio/output/story/direction/duration regression: 112 passed, 1 skipped,
  1 failure in test_duration_planning's render-manifest fixture.
- That failure was reproduced in an isolated, unmodified checkout of baseline
  02abf4b: `test_video_uses_current_wav_length_outside_estimate_and_rejects_mismatch`
  raises `Remote props language audio/captions/timeline contract mismatch` at
  job_protocol.py:130. It predates this patch; no test was removed or bypassed.
- Final policy/preview checks and committed-tree conveyor: see fresh proof logs
  under sys/logs/proofs and the attached draft PR for the latest counts.
- GitHub has no Actions workflow in this base branch and run discovery returned
  no runs. Station 6 must remain uncertified until actual successful CI exists.
  A prepared draft or local passing tests are not Green CI certification.

## Existing-script preview

format_v1 plans 3.29/3.51/3.29 seconds of boundary silence for short t1/t2/t3,
and 30.31 seconds for full-frame-16x9-001. The long SC01 plans 1.30 seconds.
These are planned values from the current scripts, not regenerated WAV timings.
Detailed dry-run assumptions and the media acceptance procedure are in
[narration-pause-implementation-plan.md](narration-pause-implementation-plan.md).
