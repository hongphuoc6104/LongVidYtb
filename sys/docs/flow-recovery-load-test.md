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
