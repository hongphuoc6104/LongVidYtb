# Repository checkpoint — 2026-10-18

Scope: the user explicitly requested all repository changes, including the previously reviewed light 2D image work, production source packages, scripts, diagnostics, Flow runtime changes and the later Colab scheduling/health work.

## Included source

- Light 2D stick-figure registry 1.4.0, authoring defaults, remote style propagation and regression tests.
- Collector's Fallacy, Adversarial AI and Reviewer 2/Nobel source blueprints; updated Feynman spin-off source packages and builders.
- Thumbnail authoring utilities, script updates and text incident/diagnostic records.
- Flow request-budget enforcement, enabled-profile leasing and conservative submission ownership across transport failures.
- Colab identity-based execution claims, bounded health observations, explicit credential renewal, pool selection and dashboard status. Duplicate profile aliases share an execution lock; pending requests retain their original owner.
- Broader offline source/transport/render tests and GitHub Actions verification.

## Review fixes

The review found and corrected transport code that could rewrite an unresolved Flow request as unsent, fail over an ambiguous submission, or repeat a provider-refused RPC. Error text is no longer accepted as proof of non-submission. Partial batches retain their original ownership and require reconciliation. Explicitly bound jobs dispatch only on their exact profile with serial ownership.

Pacing smoothing now changes interpolated fallback estimates only, retaining their original estimates. Measured acoustic anchors remain authoritative and conflicting holds stay visible to validation. The body minimum is 0.83 seconds.

Source builders default to blueprint destinations and reject initialized live jobs. Production tests read versioned blueprint sources. Genuine thumbnail/MP4 existence checks are separately marked media acceptance and use an explicit local media root; they are not replaced by fixture media or claimed as CI render evidence.

## Verification

Offline verification exercises source factories, prompt compatibility, provider boundaries, ambiguous/partial submissions, exact-profile dispatch, disabled pools, batch budgets, Colab identity contention, pending-owner recovery, dashboard health, measured timing and remote render packaging.

The genuine local Collector thumbnail/MP4 checks passed using existing deliverables. This checkpoint does not regenerate media, allocate a GPU or claim a new rendered video. Pre-commit verification passed 347 tests and 8 subtests; the two genuine local media checks passed separately. Conveyor and GitHub Actions evidence for the exact published commit is retained in local proof logs.

## Local-only records

Five runtime-state JSON files found alongside a Reviewer blueprint remain local: brief-current, execution-control, integrity, integrity-meta and workflow. Per-machine Colab account-audit/activation/lock/cleanup JSON also remains local. Ignore rules prevent accidentally publishing these operational records in future source checkpoints.

Authentication, account ledgers, live job journals, cached models, generated images/audio/video and other ignored media are preserved on the machine. Text issue records and reproducible source packages are included in Git.

The existing feature branch and PR #2 now include this repository-wide checkpoint. Its title and description identify the expanded final scope.
