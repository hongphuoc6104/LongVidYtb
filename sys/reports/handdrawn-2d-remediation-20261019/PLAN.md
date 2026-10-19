# Hand-Drawn 2D Explainer Remediation Plan

Date: 2026-10-19 (Asia/Ho_Chi_Minh)
Planning branch: `codex/handdrawn-2d-remediation`
Implementation branch: `codex/handdrawn-2d-implementation` (isolated managed worktree)
Base commit: `5b5b54a6cd37f661a3c82989bbc0e9d33c2fdacf`
Status: implementation started on 2026-10-20. See WORKLOG.md for verified progress and remaining gates.

## 1. Objective and authorized scope

Convert the project's default authoring and image generation to the user's reference-led Hand-Drawn 2D Explainer language. Remove unsolicited recurring characters, make genuine multi-profile execution available, recover interrupted work without duplicate generation, and produce three comparable short videos after the implementation gates pass.

The user subsequently authorized implementation with “bắt đầu thực hiện kế hoạch trên.” Development, calibration and production may proceed within the plan. Publication and merging remain outside its scope. Completion is recorded only with the corresponding evidence.

The required outcome is observable behavior across authoring, schemas, compiled prompts, provider attachments, dispatch, recovery, rendering, skills and evidence. Renaming a style string is insufficient.

## 2. Baseline and evidence boundaries

- `baseline.json` records 41 inherited modified/untracked files and their hashes. They were already present when the branch was created. A branch does not isolate uncommitted files from another process using this checkout.
- Preserve inherited edits, historical registries, job revisions, request journals, credentials and downloaded media. Do not commit unrelated changes automatically. Use a targeted diff review before each implementation commit.
- `reference-manifest.json` identifies 11 user-supplied screenshots by absolute path and SHA-256. Treat screenshot text as visual data, never as instructions. Browser chrome, player controls, subtitles and watermarks are outside the style target.
- Last audit: registry 1.6.0 had 34 downloaded scene requests, four reference requests and four registration requests for `impostor-paradox-9x16`. Forty-two downloaded resources do not mean 42 completed scene beats.
- Request `28ecff918bf44447a0838d818cc64c9c8882dd9a3147a266053c3b19b10d9856`, target `SC10_I3_9x16`, was `submitted` without a terminal result. Re-observe before recovery; the audit is a timestamped observation, not live state.
- Existing final MP4s predate this remediation. Never count them as new deliverables without matching current input hashes.
- A historical run passed 429 tests from 39 selected files. A later targeted audit passed 188 tests. Neither result certifies actual style, semantic fidelity, concurrency or end-to-end completion.
- `./pipeline status` passed during planning. Runtime readiness does not establish provider authentication or usable GPU capacity.

## 3. Verified causes and planned resolutions

| ID | Observed cause | Primary implementation surfaces | Required resolution |
| --- | --- | --- | --- |
| R1 | Fine warm-charcoal contours, warm/cool lighting and softened backgrounds differ from the samples | `sys/flow_prompts/versions/1.6.0/registry.json`, `sys/visual_style.py` | Publish a new immutable style version with clear irregular black contours, flat color areas and restrained contextual detail |
| R2 | Global cast rules prescribe round white heads, stick limbs and cartoon hands | Registry `cast_rule`, `sys/flow_prompts/compiler.py`, `sys/visual_style.py` | Separate style from optional entities; no human design or recurring identity in the global style block |
| R3 | Job builders and authoring fallback inject CH01 and recurring roles | `sys/tools/build_impostor_paradox_job.py`, `sys/tools/research_story_architect.py` | Make entities explicit per beat; an omitted entity list must not silently create a human |
| R4 | Image production creates/registers every declared character before scenes | `sys/image_pipeline.py`, `sys/adapters.py`, `sys/content_contract.py` | Reference-free object/diagram jobs must proceed with zero character registrations |
| R5 | High-velocity physical action and character-led full scenes are overgeneralized | Registry shot rules, `sys/scripts/visual_quality.py`, `sys/tools/script_diversity_linter.py` | Judge explanatory relationships and relevance; permit useful static objects and diagrams |
| R6 | Job binding filters the pool and explicitly sets concurrency to one; bridge filters again | `sys/image_pipeline.py`, `sys/flow_cdp/bridge.py`, `sys/flow_management.py`, `sys/execution.py` | Distinguish explicit single-profile mode from pool mode; maintain ownership per request and dependency group |
| R7 | One listening profile is mistaken for the available multi-profile pool | `sys/flow_cdp/lifecycle.py`, `sys/flow_cdp/multi_profile_manager.py` | Discover, launch, verify and lease healthy authorized profiles with explicit fallback reasons |
| R8 | See-Say accepts matching numbers or one word; it is not wired into production validation | `sys/tools/research_story_architect.py`, `sys/content_contract.py` | Validate entities, actions, relations and quantities at a production gate; report uncertainty instead of a semantic percentage |
| R9 | Short jobs contain long-form durations and scene counts | `sys/format_profiles.py`, blueprint builders, authoring/audio/render validators | Enforce 5 scenes, 45–60 seconds, subtitles and speed 1.0 for these short deliverables |
| R10 | Skills still prescribe old stick-figure profiles and conflicting shot quotas | `.agents/skills/`, `AGENTS.md`, `PLAYBOOK.md`, conveyor checks | Align instructions and executable gates with the reference-led contract while retaining other project invariants |

## 4. Target visual contract

### 4.1 Drawing and composition

- Recognizable black outlines with controlled hand-drawn irregularity. Preserve readable outer silhouettes at mobile size. Do not globally prohibit bold contours.
- Flat, selective colors; simple optional grounding shadows. Avoid default cinematic lighting, blue-gray shadow systems, gradients, glossy volume, paper aging and photorealistic rendering.
- White backgrounds for isolated objects, comparisons and diagrams when appropriate. Contextual scenes may use broad flat background areas. Do not force every frame onto white or every frame into a room.
- One clear explanatory relationship per beat: amount, comparison, grouping, exchange, cause/effect, progression, structure or a relevant contextual action.
- Allow static explanatory compositions. A spoon, three containers or a column chart can convey information without a human or exaggerated physical struggle.
- People and animals appear only when authored for the explanation. Hair, skin tone, clothes, age and silhouette follow context; no compulsory white round head, outfit, mascot or four-finger white hand rule.
- Preserve exact approved learner-facing labels. Keep provider text reliability separate from style acceptance; proofread Vietnamese accents and numbers in the actual result.
- Treat the supplied salt/history examples as style references. Do not transplant their nouns, props or claims into academic topics.
- Keep complete scene images (`kind: scene`), existing full-frame rendering and portrait subtitle safety. No sticker layers, manual coordinate authoring or ad-hoc local render path.

### 4.2 Style reference provenance

- Separate three concepts: style reference, optional character identity reference, and Base composition reference.
- Prepare reference crops excluding browser UI and captions while preserving the source hash and crop provenance. Use an established image-editing workflow when pixels need modification.
- Store approved reference assets under a versioned `sys/assets/` location; do not depend on a Pictures directory at runtime. Record provenance before adding assets to source control.
- Verify the provider's actual attachment limits using the existing integration. A slot named Character does not make an uploaded style sample a character identity.
- If style plus Base cannot coexist in supported slots, document the supported strategy and test it. Never invent a second slot, omit a declared attachment silently or pretend a media ID was attached.
- Include registry hash, model, reference hashes and actual attachment evidence in request identity and cache keys. Never reuse an old-style result merely because the narration is unchanged.

## 5. Proposed authoring and entity contract

- Introduce a versioned visual contract, provisionally registry `1.7.0`, after checking the version is unused. Keep 1.6.0 and earlier registries immutable for replay.
- Keep the project's content schema compatible where possible. Its top-level `characters` list already permits zero entries; audit Python validators, builders, checkpoint transitions and adapters before adding a new schema version.
- Represent entity intent explicitly at beat level. Proposed policy values are `none` and `explicit`; freeze the precise representation during implementation design and reject contradictions.
- `none`: no human figure, hand, face or silhouette may be introduced through prompt defaults or attachments. Named animals/objects remain separate authored entities.
- `explicit`: include only the described roles/counts. Require an identity reference only when actual identity continuity is requested, not whenever a person appears.
- Full scene means an integrated composition, not necessarily a character in a furnished setting. Variation can describe an object, diagram, animal or person changing within a declared Base.
- Remove the universal CH01 fallback. Preserve continuity inside authored chains without manufacturing recurring protagonists across unrelated scenes.
- Unused character declarations should produce a clear validation finding and be removed through authoring, not trigger generation. Empty reference collections must have a valid path through the images phase.
- Update both single-request and batch planning paths. A working direct request is insufficient if the batch pre-pass still requires registered characters.

## 6. Multi-profile execution contract

- Introduce explicit dispatch policy: `single_profile` for intentionally bound work and `pool` for work allowed across the authorized session pool. Legacy bindings retain their meaning until official migration selects the new policy.
- A runtime preference or verified session profile must not silently become a global pool restriction. Preserve grant scope, allowed accounts, leases and send-boundary ownership checks.
- Build dependency groups from `based_on` edges and any actual provider-local reference dependencies. Reject cycles, missing parents and conflicting owner assignments.
- Independent groups may run concurrently on different ready profiles. A group with an existing Base remains on its owner's profile/project. Portable local style files require verified upload/registration on each receiving profile.
- Never treat a foreign provider media ID as portable. A group may be reassigned before submission; submitted/ambiguous requests must be reconciled before retry. Partially generated groups retain ownership unless an explicit safe migration is implemented.
- Worker count is bounded by configured concurrency, ready authorized profiles, runnable dependency groups and resource limits. A configured pool of 20 does not imply 20 healthy workers.
- Start enough workers for the eligible workload, initially prove two, then test the configured target of six where healthy capacity exists. Serialize operations that change shared UI settings within each profile.
- Maintain per-profile pacing, cooldown and leases. Failover applies only to work proven not submitted; persistent blocks and authentication failures remain visible.
- Record requested/eligible/active workers, queue depth, group ownership, attempts, overlapping dispatch intervals, cooldowns and fallback reasons. Distinguish Python worker count, Chrome profile count and tab count.
- Teardown exactly the browsers/tabs spawned by the run, including exception and stop paths. Preserve pre-existing user windows and evidence needed for reconciliation.

## 7. Ordered implementation work packages

### P0 — Establish a stable baseline and recover the orphan request

1. Check processes, leases, current revisions and file hashes before edits. If another task is writing this checkout, use an isolated managed worktree and deliberately transfer only the agreed baseline; do not reset or stash someone else's work.
2. Compare inherited changes against `baseline.json`; review source changes made since this plan before assigning them to the remediation.
3. Reproduce the style mismatch using saved actual prompts and downloaded images. Record which settings caused each observed difference.
4. Use supported observe/reconcile commands to inspect the pending SC10 request on its owning profile. Collect an existing output; retry only with definite not-submitted/terminal-failure evidence.
5. Produce an inventory grouped by registry version, current content identity, scene/reference/registration type and request state. Preserve old assets even if the new short scripts cannot use them.

Exit: no unresolved request is silently retried; a current baseline and resumable recovery record exist. Recovery does not certify visual quality.

### P1 — Freeze the new contract and synchronize instructions

1. Turn Section 4 into a concise versioned registry and reference manifest; remove universal cast and lighting assumptions.
2. Update new-job defaults, documentation and skills together. Audit `vp-production`, `vp-full-frame-quality`, `vp-research-architect`, `vp-scriptwriting`, `vp-flow-cdp` and their referenced style documents.
3. Update critique/style assertions that currently enforce a mascot or the old shot vocabulary. Preserve GPU, secrecy, directory, format and anti-duplication checks.
4. Add compatibility checks proving historical pins and cache identities remain replayable. No historical registry or saved revision is rewritten.

Exit: one consistent new contract, explicit compatibility behavior and no conflicting default character instruction.

### P2 — Make entities and references optional throughout production

1. Implement Section 5 in builders, validators, compiler, adapters and reference checkpoint orchestration.
2. Remove unconditional character reference generation/registration; generate only required continuity assets.
3. Implement style/Base/identity provenance and actual supported attachments across single and batch paths.
4. Ensure no-reference jobs, object-only full scenes, object variations and diagrams reach the provider without injected human instructions.

Exit: real compiled prompts and isolated transport tests demonstrate zero unsolicited entities and correct attachment handling.

### P3 — Repair semantic and pacing gates

1. Define structured source-to-visual bindings: named entities, action, relation, quantities and relevant context. Validate omissions and contradictions separately from literal word overlap.
2. Wire validation into production before provider submission. Missing narration/description is invalid or explicitly unsupported, never automatic success.
3. Reject the known false positives: 500-word draft versus spaceship travelling 500 km; 70 surveyed students versus 70 purple elephants. Also cover negation, reversed comparisons, incorrect units and legitimate bilingual paraphrases.
4. Do not market heuristic scores as measured semantic accuracy. Where a judgment cannot be established deterministically, produce an explicit review finding; auto mode stops clearly on an unresolved required gate.
5. Replace people/no-people quotas and blanket static-object bans with explanatory relevance, repetition and legibility checks. Retain meaningful continuity and timing checks.
6. Enforce short profile requirements at brief, content, audio and render boundaries. Do not stretch audio or add silence merely to reach the target.

Exit: bad semantic examples fail through the production entry point; useful static explanatory images and valid short scripts pass.

### P4 — Enable observable pool dispatch

1. Implement explicit policy and ownership rules from Section 6 across execution settings, flow management, image planning and bridge dispatch.
2. Replace whole-job profile filtering in pool mode with dependency-group ownership. Keep explicit single-profile mode functional.
3. Verify profile discovery, startup, health, leases, task grouping, cooldown, cancellation and teardown.
4. Add scheduling evidence and precise fallback reasons. Ensure transport fixtures cannot reach signed-in browsers through direct-CDP fallback.

Exit: isolated regression tests pass and a live two-profile test demonstrates overlapping independent requests with intact ownership and no duplicates.

### P5 — Run a small real-image style calibration

1. Author six original academic-domain test beats: isolated object, labelled comparison, grouping/relationship diagram, contextual human scene, nonhuman scene, and Base variation. Use the same narration where before/after comparison is meaningful.
2. Generate through the project Flow path with real attachments. Inspect binaries, labels, silhouettes, background treatment, human presence and reference provenance.
3. Evaluate against the user's samples: clear black outline, flat fills, appropriate background, simple explanatory composition, exact entities and labels, no unwanted identity.
4. Include a two-profile subset with two runnable independent groups; record actual dispatch overlap. Test configuration alone is not a pass.
5. Record output-specific corrections. Keep the sample small until visual acceptance is supported. If subjective style differences remain, present the concrete samples for feedback before full production.

Exit: calibration evidence demonstrates the intended drawing language and entity policy. Do not claim all future frames will pass based on this sample.

### P6 — Re-author and produce three comparable shorts

1. Create new authoring revisions or new comparison job IDs through supported commands. Use official migration/rollback only after checking execution authority and provenance; do not edit workflow JSON, DB rows or request states by hand.
2. Produce independent 5-scene scripts of 45–60 seconds for Impostor Paradox, Reviewer 2 and Collector's Fallacy, one core paradox each, within the existing channel pillar.
3. Re-verify source claims. Do not inherit unsupported neuroscience or percentage claims from the long drafts. Use approved titles, thumbnail text, localized hook and spoken-fact limits.
4. Build a beat/reference dependency plan from the actual short narration. Reuse old assets only if current content/style/reference identity and visual acceptance match.
5. Finish video 1 end-to-end as the integration pilot. Once accepted technically and visually, apply the verified path to videos 2 and 3; dispatch independent image groups across healthy profiles.
6. Generate VietNarrator audio at speed 1.0, align cue windows and subtitles, and render through Colab/approved Remotion entry points. Preserve headless EGL/NVENC and tile synchronization requirements.
7. Inspect complete MP4 playback, with extra attention to the opening, every labelled frame, transitions and reused Base chains. Use ffprobe for duration, streams, resolution and frame rate.

Exit: three new 1080x1920 MP4s, SRTs, matching revision manifests and a comparison report. All three have measured duration 45–60 seconds; required source/packaging/script checks pass.

### P7 — Conveyor, documentation and handoff

1. Run the 6-station conveyor after implementation, fixing actual failures. Expand test selection to include the new contract, compiler, optional-entity, scheduler and production-routing regressions.
2. Record test files, collected cases, AST totals and warnings separately. A passing selected suite is never described as the entire repository suite.
3. Run broader `sys/tests/` coverage in an isolated, transport-safe environment. Investigate failures; document environment dependencies explicitly.
4. Update PLAYBOOK with six-field entries only for reproduced and verified resolutions. Apply the skill extraction threshold where required.
5. Prepare a focused English PR using gh-axi and attach any created PR to the chat. Check CI against the exact pushed head; local certificate files do not substitute for remote green CI. Publishing/merging is outside this plan.
6. Deliver an evidence-linked before/after report with real output paths, remaining limitations, rollback instructions and no invented percentages.

Exit: reviewable change set, required CI green, reproducible evidence and complete deliverables. If an external gate is unavailable, identify the exact remaining gate rather than declare completion.

## 8. Validation matrix

| Test class | Required cases | Passing evidence |
| --- | --- | --- |
| Style/compiler | New pin; old pins; bold outline; white/contextual backgrounds; allowed labels | Compiled records, registry hashes, immutable old fixtures |
| Entities | Zero characters; explicit roles/counts; hands-only policy; object variation; unused declarations | Production validation and provider-bound prompt/attachment assertions |
| References | Style only; Base only; optional identity; changed hash; unsupported slot combination; cross-profile media | Verified attachments, fail-closed unsupported behavior, identity/cache invalidation |
| Semantics | Matching number/wrong meaning; reversed relation; missing entity; blank input; valid paraphrase | Gate called from production, meaningful failures and legitimate passes |
| Format | Wrong scene count; over/under duration; wrong speed; missing subtitles; valid short | Rejection before expensive generation plus measured audio/MP4 checks |
| Scheduling | Two independent groups; one chain; mixed chains; conflicting owners; no ready worker; intentional single mode | Correct ownership, bounded workers, explicit fallback, live overlap where feasible |
| Recovery | Timeout before send; ambiguous after send; generated before download; resume; stop; cooldown | No duplicate sends, collect-only recovery, valid journals and preserved completed assets |
| Lifecycle | Success, error and cancellation with pre-existing browsers | Exact spawned-resource teardown and preservation of user resources |
| Remote integration | Source packaging; audio cues; image paths; T4 render; current revision identity | Real remote WAV/MP4, ffprobe output, playback inspection and manifests |
| Reporting | References versus scene images; cached versus new; old versus new render; selected versus full tests | Counts recomputed from artifacts; no stale or inferred completion labels |

## 9. Release gates and rollback

- G0: baseline/recovery verified before new provider submissions.
- G1: style/entity contract and compatibility tests pass before calibration.
- G2: actual calibration images match the target sufficiently for production; subjective differences are visible to the user.
- G3: actual two-profile overlap demonstrated before claiming multi-profile execution. If only one account is healthy, report the capacity block and continue independent code work without a false claim.
- G4: first short passes complete playback and current-input checks before scaling to the remaining two.
- G5: all three shorts, required development gates and exact-head CI are complete before final certification.

Rollback is additive: retain the historical registries and default selection, use supported job migration rollback, and preserve new artifacts for inspection. Do not reset the worktree, delete user edits, mutate old journals or reuse foreign media IDs. Roll back the new pool policy to explicit single-profile mode if scheduling correctness fails; do not weaken ownership guards to increase throughput.

## 10. Progress record and completion rule

- [x] Create the remediation branch and record inherited changes.
- [x] Record the 11 supplied visual references and concrete diagnosed causes.
- [x] Write this implementation, validation, recovery and delivery plan.
- [ ] P0 baseline stabilization and orphan reconciliation.
- [ ] P1 new style contract and synchronized instructions.
- [ ] P2 optional entities and reference routing.
- [ ] P3 semantic/pacing/format production gates.
- [ ] P4 pool dispatch and ownership.
- [ ] P5 live style and concurrency calibration.
- [ ] P6 three verified short deliverables.
- [ ] P7 complete conveyor, CI and handoff.

Update each package with changed files, executed checks, real artifact paths, unresolved findings and the next action. Never mark the overall objective complete because only code tests or image reference registration passed.
