# Remote Audio Delivery & Cadence Standards

Voice/reference/rate come from the current brief, with request provenance. Synthesized audio must adhere to the vocal persona matrix and pacing standards documented in [voice-cadence-pacing.md](../../vp-channel-patterns/references/voice-cadence-pacing.md) and [vp-scriptwriting](../../vp-scriptwriting/SKILL.md).

## 1. Format-aware pause policy

Explicit-output jobs with `tts_pause_policy: format_v1` use the defaults in
`sys/format_profiles.py`: short/regular sentences are 0.16/0.22 s for short_9x16
and 0.20/0.28 s for long_16x9; scene/video tails are 0.30/0.15 s and 0.40/0.25 s.
SC01 sentence gaps are shorter (0.12/0.16 s short; 0.16/0.20 s long). No explicit
tags are allowed in SC01. Profile selection follows each language's outputs;
a shared-language dual track uses long timing. Reused excerpts keep source timing.

Explicit `[pause:...]` tags retain their exact duration, including terminal tags;
they replace automatic defaults. Learner holds use max, not additive padding.
Suggested authored pivots are 0.45 s short / 0.60 s long, never an automatic remap
of an existing 900 ms tag. No pause is required just because the picture changes.
Ordinary commas stay inside an utterance; only sentences over 180 characters may
be split at clause punctuation. Preserve model-internal natural timing.

See [implementation and acceptance plan](../../../../sys/docs/narration-pause-implementation-plan.md)
and `sys/tools/preview_narration_pauses.py` for exact boundary budgets. Saved
WAVs/requests are immutable; regenerate audio, SRT and timelines together.
Legacy routing/selector keeps 0.50 s sentences, 0.70 s scenes, 0.35 s final tail.

## 2. Boundary trimming, prosody guards and timing evidence

The Colab worker (`sys/colab_bridge/worker.py`) strips inter-letter hyphens (`vi-đê-ô` -> `vi đê ô`) before `OmniVoice` BPE tokenization, strips isolated leading reference-prompt bursts (`<= 240 ms` followed by `>= 120 ms` quiet gap `< 0.011` RMS), preserves soft trailing nasal codas (`>= 0.006` within `90 ms`), trims each utterance to 25 ms lead / 30 ms trail with an 8 ms fade, and auto-retries single-item (`batch_size=1`) when `_utterance_acoustic_score` detects internal silence holes (`> 380 ms`) or syllable-rate collapse. These buffers add about 55 ms to a join; they are separate from the inserted pause. Request `pause_plan` proves planned silence only; PCM and direct listening to `narration.wav` are mandatory to verify output timing, clean utterance starts/endings, and perceived naturalness. Legacy cadence duration formulas remain approximate, not `format_v1` budgets.

## 3. Dynamic Pacing & Voice Matrix
- **Hook & Empathy (Phase 1):** ~4.2–4.4 syl/s (Vietnamese) / ~145–150 wpm (English).
- **Causal Evidence & Mechanism (Phase 2):** ~4.0 syl/s (Vietnamese) / ~135–140 wpm (English).
- **Philosophical Payoff (Phase 3):** ~3.6–3.8 syl/s (Vietnamese) / ~120–125 wpm (English).
- **Default Canonical Voice (`sys/config.json`):** Both Vietnamese (`vi`) and English (`en`) use `VietNarrator` (`assets/voices/viet_narrator/profile.json`, canonical speed `1.00`, contract range `[0.90, 1.15]`, with scene-level `tone` multipliers `0.98`, `1.02`, `0.92`). Shared settings: `num_step: 32`, `batch_size: 4`, `audio_processing.VOICE_CHAIN` (`highpass 80Hz`, `-2dB@250Hz`, `+3.5dB@3.2kHz`, de-esser, 2-stage `acompressor`), `-11.0 LUFS`, `-1.0 dBTP`, `48kHz` Mono PCM16 via `kjanh/KhanhTTS-OmniVoice` on Colab T4. Honor explicit brief voice/rate choices. No local TTS fallback.

## 4. Remote Delivery & Audio Invariants
Specify intent and pronunciation risks as craft notes. Only `learner_pause_seconds` has the existing scene-tail hold behavior; intent notes do not guarantee emotion and images do not demonstrate moving lips. Practice holds only when requested/useful, with question/model at the scene boundary and feedback after.

Use actual measured WAV duration, content boundary and pauses for timeline. Technical format/silence/provenance checks do not certify stress, accent or naturalness. When listening is unavailable, report that limit; do not invoke a mandatory reviewer in auto.

Keep synthesis on Colab; missing T4/model/reference is a capability issue, not permission for local fallback. No forced Foley/music, a universal solo persona or rate from the skill. SFX/mixing requires an implemented supported contract. Collect existing remote request on the same account/session before retrying; release dedicated VM after durable collection.

Layer anchors are interpolated inside the real audio chunks; keep narration quotes exact so anchors resolve.
