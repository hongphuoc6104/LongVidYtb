# Flow submission safety and offline verification

- The engine owns request journals and budget transitions. Transport code must never rewrite a journal because a download is missing or an exception occurred.
- Distinguish a connection failure before dispatch from a failure after an attempted socket/provider send. Error wording such as “socket” does not prove non-submission.
- Unknown, partial, generated-but-uncollected and provider-blocked requests keep their owning account/session. Collect or reconcile the original request. Do not rotate accounts or automatically reissue a refused RPC.
- Worker failover requires both explicit evidence that the remaining request was never sent and an explicitly retryable pre-send error. Contract/auth/quota/bot/CAPTCHA refusals stop dependent work.
- In a mixed batch, one unsent patch cannot reclassify submitted or collected patches. Retain partial output and refuse blanket resubmission.
- Profile availability respects enabled candidates; an entirely disabled pool returns immediately. Quota accounting rejects duplicate request identities across operation/alias boundaries.
- Offline tests close both socket and direct-CDP branches and verify journal bytes stay intact. They prove control flow, not real provider output quality.
- Test references: `test_repository_checkpoint.py`, `test_flow_prompt_integration.py`, `test_multi_profile_manager.py` and `test_account_management.py`.
