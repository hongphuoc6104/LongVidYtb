# Flow recovery and bounded load testing

Flow has two separate failure classes: a local connection/setup failure proven to
occur before sending, and a submitted, uncertain or provider-refused request.
Only an explicitly retryable, proven unsent failure may move to another worker.
Preserve request identities and collect in-flight results after a terminal error.

## Reproduction and measured scope

On 2026-10-18 an offline six-patch probe injected
`PUBLIC_ERROR_UNUSUAL_ACTIVITY` on every executor call. With one worker and a
0.1-second fixture cooldown, eager scheduling made six calls and took 2.502
seconds. This was a local control-flow experiment with zero provider requests.
It does not establish the Google account's current health or image throughput.

The dispatcher now maintains at most one scheduled patch per available worker.
After observing a terminal error it schedules no remaining patch, waits for
already-running work to finish, and retains collected results on their patches.
The error includes the original failure instead of only a generic batch error.

`test_flow_batch_stop.py` verifies six refusal/uncertainty categories, collection
after another worker fails, an unsent local contract failure, and 1,000 successful
offline requests without same-profile overlap. All requests use local callbacks;
there is no browser connection, generated image or provider credit charge.

## Fast recovery decisions

| Observed state | Action |
| --- | --- |
| Confirmed connection failure before dispatch | Repair the configured connection; allow only the explicitly retryable unsent remainder. |
| Image generated but not downloaded | Collect the original media; do not create a new request. |
| Timeout or disconnect after a possible send | Stop queued work, retain the owner and reconcile the original request. |
| Unusual activity, CAPTCHA, authentication or quota refusal | Stop queued work; resolve the provider message using normal account/browser controls. Do not rotate accounts or reissue the refused request automatically. |

Google's [Flow help](https://support.google.com/flow/answer/16353333?hl=en)
recommends retrying after a couple of minutes and disabling VPNs/proxies for an
Unusual Activity message. This does not guarantee a recovery deadline. Clearing
cookies is not evidence that a server-side refusal has been removed.

## Live acceptance still required

At inspection all six configured CDP ports were closed. The account registry
listed three profiles (one enabled), while generation configuration listed six
enabled profiles. Do not count these as verified signed-in accounts.
The browser tool returned `Local browser use is disabled in Work settings`.
Consequently no live image load test or cookie/reload recovery test was performed.

Once ordinary browser control is available, inspect the selected signed-in
profile and pending requests first. Use a small serial sample with a minimum
four-second gap, record each request/result/latency, and stop on the first
provider refusal. Avoid the legacy CAPTCHA interception path; do not change
verification actions or use cookie resets to circumvent a refusal.

## Project-only continuation

The user subsequently required project tools only, without Computer Use. Work
browser permissions are not a prerequisite for those project commands. The
earlier browser-tool limitation applies only to that separate tool route.

The expanded project suite initially found seven failures out of 84 tests. Old
trial/status fixtures did not close the direct fallback or external port probes.
One synthetic timeout case reached the live RPC and received parameter error
`[3]`, without a returned image; billing was not verified. This was unintended
test transport leakage, not a successful stress test. The fixtures now use
private Unix endpoints and assert on any external launch/direct dispatch.

At 17:11 on 2026-10-18, read-only production observation confirmed fresh real
images in adversarial-ai-9x16, with matching bytes/media sidecars and roughly
27–43 seconds per image in the latest sample. These were submissions by the
already-running production controller, not this test task. Its submitted
request and profile ownership prevent disruptive cleanup while it is running.

The cleanup utility rejects the active port 9225 because its CLI only accepts
9222/9223/9224. It also claims seven-day filtering but passes no time range and
prints a claim that abnormal-activity flags were eliminated without performing
a post-cleanup generation check. These are observed utility limitations, not
evidence that cookies caused or resolved a provider refusal.
