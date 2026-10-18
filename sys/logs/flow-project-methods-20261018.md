# Project-only Flow recovery verification — 2026-10-18

## Scope

User instruction: use only the project's tools; do not use Computer Use. Work browser permissions are not a prerequisite for this route. No Computer Use call was made in this continuation. Existing production requests, account ownership and cookies were retained.

## Results

- Initial expanded Python suite: 77 passed, 7 failed in 41.34 seconds.
- Corrected Python suite: all 84 passed in 10.38 seconds.
- Project Node suites: all 42 passed.
- Isolated development conveyor: 309 tests and 16 subtests passed, documentation and static checks passed. CI certification is recorded separately below when complete.

The seven failures exposed legacy trial/status fixtures which replaced only the socket sender. They now use private local Unix endpoints, disable observations of real CDP ports, and fail immediately if a direct send/browser launch is attempted. They still exercise the real bridge, budget/ownership and timeout logic.

One initial timeout fixture unexpectedly reached the real provider RPC and received parameter error [3], with no returned image. Provider billing was not checked. This is recorded as unintended transport leakage, not as successful live load testing. No further live send was made by the corrected fixtures.

## Method coverage

| Existing project method | Executed evidence | Result / limit |
| --- | --- | --- |
| Bounded queue / stop after refusal | test_flow_batch_stop, saved before/after stress reports | One call after first refusal, even with 1,000 queued patches; remainder unchanged. Offline. |
| Proven-unsent transport failover | test_multi_profile_manager | Only explicitly retryable unsent work moves; completed items retained. Offline. |
| Ownership / quota / CAPTCHA / ambiguous send | test_flow_profile_trial, test_account_management | Pool stops; owner and budget remain; no automatic resend. Offline. |
| Status reconnect / timeout classification | test_flow_status | Read-only failures stay unsent; post-send uncertainty stays ambiguous. Offline. |
| References and partial result mapping | test_flow_reference_binding, test_flow_prompt_integration | Source media IDs and request mapping retained. Offline. |
| Reload after interrupted submission | test-attempt-store, test-session | Interrupted send becomes unknown; reissue forbidden. Offline, not a reload of production. |
| Download retry / existing image collection | test-attempt-store, test-queue-runner | Known media retained after collection failure; no generation resend. Offline. |
| Profile startup/locks | test_flow_accounts, test_flow_lease_manager | Temporary fixture directories and real file-lock contracts. Not a production restart. |
| Cookie/site-data/cache cleanup plus page reload | Actual cleaner CLI with --port 9225 | Rejected by CLI (only 9222/9223/9224 accepted). No data was cleared. The active production owner also prevents disruptive cleanup. |
| Seven-day cleanup claim | Source inspection of cleaner | No time-range filter exists. Its success message does not verify provider recovery. |
| Legacy CAPTCHA interception | Source inspection only | Not executed as a recovery test; interception is not an accepted way to resolve provider verification. |

## Live production observation

At 2026-10-18T17:17:17.809143+07:00, a read-only 15-minute sample of the independently running adversarial-ai-9x16 production controller shows 25 downloaded images and 1 pending request, with 0 journal errors. All downloaded images passed binary verification, hash comparison and provider-media-ID checks. Observed latency: 26.65–45.85 seconds, median 33.38 seconds. These images were not submitted by this test task. This sample does not establish the error cannot recur under different load.

Profile 1 on port 9225 is active. The registry lists three profiles (one enabled), while generation config lists six enabled profiles. Metadata and an open port do not establish provider authentication. The exact profile is still owned by production, so reset/cache/cookie tests against it have not been performed. No production job was stopped to make this test possible.

## Review

PR: https://github.com/hongphuoc6104/LongVidYtb/pull/4 . Fixture fixes are applied to the primary workspace while retaining unrelated changes. Production engine code and journals were not changed in this continuation.

## Final certification

All six stations passed for commit 549fc0cd5fd61c32ad8ec43c93cc3a86009675a1. Actual successful CI runs: 39118624678, 39118622715. Certificate: /home/hongphuoc6104/.codex/worktrees/colab-runtime-manager/flowkit-video-pipeline/sys/logs/proofs/green_certified_20261018_171812.json. PR #4 remains a draft, unmerged.
