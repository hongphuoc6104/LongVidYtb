# Flow load and recovery test, 2026-10-18

Live acceptance: blocked, no provider generation requests sent by this task and no images created. The browser tool reported Local browser use is disabled in Work settings; all six configured CDP ports were closed when inspected. The account registry lists three profiles (only profile_1 enabled), while sys/config.json lists six enabled profiles. Neither listing establishes current provider authentication. No cookie clearing, page reset, CAPTCHA interception or account rotation was executed.

## Reproduced local defect

The six-patch offline refusal probe invoked all six executor callbacks despite the first PUBLIC_ERROR_UNUSUAL_ACTIVITY. With a 0.1-second fixture cooldown the old code took 2.502 seconds. Bounded scheduling stops after the first error; the identical six-patch probe invokes one callback in 0.001287 seconds and preserves five unstarted patches. At 100 and 1,000 queued patches, it still invokes just one callback. These timings measure local scheduling only, with zero live provider requests.

## Change and verification

Applied the dispatcher correction to the current workspace, preserving existing changes and production job journals. The dispatcher retains completed in-flight outputs, leaves the unsent remainder untouched, includes the first failure in the batch error, and limits failover to explicitly retryable proven-unsent errors.

Nine new offline regressions cover six provider/uncertainty messages, in-flight collection, a 1,000-request success load without profile overlap, and local contract rejection. The focused dispatcher/lease suite passes 26 tests in the current workspace. The isolated development conveyor passes 295 tests and 16 subtests, documentation and static checks. PR: https://github.com/hongphuoc6104/LongVidYtb/pull/4, stacked on PR #3.

## Normal recovery

Repair a known unsent connection/setup error before continuing the unsent remainder. Collect an existing generated image instead of generating it again. For an uncertain send, keep the original request/account and reconcile it. For Unusual Activity, stop the queue; Google Flow Help recommends waiting a couple of minutes and disabling VPNs/proxies: https://support.google.com/flow/answer/16353333?hl=en . This is guidance, not proof of recovery. Cookie deletion has not been tested and is not a demonstrated cure.

Next live acceptance requires normal browser access and a selected authenticated profile without unresolved requests: a small serial sample, at least four seconds between requests, saved media IDs/latencies, and a stop at the first provider refusal.

## Final CI evidence

All six development stations are certified for commit 7c017ec39a02e9dae61cdcaa505fd05cfb4944b3. Both GitHub Actions runs passed: 39116005432, 39115994778. Certificate: /home/hongphuoc6104/.codex/worktrees/colab-runtime-manager/flowkit-video-pipeline/sys/logs/proofs/green_certified_20261018_163743.json. The PR remains a draft and has not been merged.
