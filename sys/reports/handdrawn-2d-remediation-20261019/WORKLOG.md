# Implementation progress — 2026-10-20

## Location and provenance

Implementation runs on `codex/handdrawn-2d-implementation` in the managed `handdrawn-2d-remediation` worktree. The planning branch and original checkout remain available. Another active task changed the original Impostor builder and blueprint exports during implementation; a 59-file snapshot was preserved before isolation under the original checkout's planning report directory. The original checkout was not reset or cleaned.

The new change depends on inherited registry 1.6.0/compiler and authoring work. Those related dependencies are reviewed as part of the engine change. Unrelated inherited blueprint exports, issue logs and the other task's new five-scene Impostor rewrite are excluded from the implementation commit. Their original files and snapshot are preserved. Archived builders explicitly retain their old style; the generic new-topic default is 1.7.0.

## Implemented code (provider acceptance remains separate)

- Add immutable registry 1.7.0 with clear black outlines, flat fills, explanatory static objects/diagrams and explicit contextual entities. Preserve prior registry files/pins.
- Remove the universal CH01 fallback from story-row construction. Compile new scene prompts with explicit human presence; reject ambiguous flags and identity references on human-free scenes. Support object variations without facial-expression requirements.
- Add production explanation bindings and short-format validation. Matching numbers and blank inputs no longer certify See-Say alignment. Structural term/quote bindings do not claim semantic accuracy.
- Enforce 45–60 measured seconds for new reference-led shorts at the actual audio/video duration gate; retain legacy duration behavior.
- Add explicit pool/single-profile policy, filter configured profiles through frozen session authorization, validate dependency cycles/missing parents, launch bounded candidates under lifecycle tracking and serialize each profile's requests.
- Keep Base ownership, record worker capacity/fallback and request timing intervals, reject foreign/unavailable owners and use exact profile paths rather than directory-name substrings.
- Route new production through the thread-safe Flow bridge instead of the compatibility wrapper that swaps global functions.
- Honor the requested model on the direct path, run the final ownership callback on the actual worker, and never turn a post-send transport error into an unsent request or silently switch transport.
- Synchronize skills and critique/CI test selection with the new contract. Preserve GPU, secrecy, source-fidelity, full-frame and teardown requirements.

## Verification obtained

- The selected conveyor run passed stations 1–5: 466 tests, 16 subtests, 3 warnings, AST checks and lint. This run used existing dependency runtime and `VP_MEDIA_ROOT` pointing to genuine historical assets in the original checkout. Those media checks do not certify new videos.
- Additional post-change targeted checks passed; see the saved logs and subsequent exact-commit CI. The new dispatcher regression uses the real scheduling loop with a controlled transport and a barrier to verify overlapping independent roots and same-owner variations. It does not certify live multi-profile generation.
- Six calibration cases are prepared in `calibration.json`: five compiled requests and one object variation awaiting a real Base. None was submitted; none is certified visually.
- A bounded read of the actual Flow page confirmed the existing project and its visible Upload menu. Inspection did not submit generation, navigate, clear cookies or reload the page. Temporary browsers opened for inspection were closed by the lifecycle manager.

## Remaining gates and concrete next actions

1. **P0 recovery remains unresolved.** The old SC10 request first required UI evidence via the official reconcile command. During concurrent work, its original job directory disappeared from the observed location. The old request was not reset/reissued. Locate the other task's preserved job/archive before touching its journal. Provider thumbnails alone are not sufficient identity evidence.
2. **P1/P2 style attachment is unfinished.** Add a verified uploader/provenance record and distinct style-reference semantics for the real supported provider slot. Do not mark a screenshot as attached from its filename or invent a media UUID. Keep source crops/edits in the approved image workflow.
3. **P3 semantics remains bounded.** The deterministic gate checks authored traceability and rejects known numerical false positives. A complete meaning judgment still requires actual source/image inspection; no 100% score is produced.
4. **P4 live acceptance is pending.** After style uploads and account health/identity are established, demonstrate two authorized profiles with actual overlapping request intervals, then test six only if capacity allows.
5. **P5/P6 are not complete.** Generate and inspect calibration images first, then author the three new five-scene shorts with verified claims, synthesize through Colab and render new MP4/SRT outputs. Existing MP4s are not the new deliverables.
6. **P7 needs exact-head CI and final media acceptance.** Local stages 1–5 are evidence for code only; stage 6 requires a committed change and actual GitHub checks. No final objective-complete certification is issued by this progress record.
