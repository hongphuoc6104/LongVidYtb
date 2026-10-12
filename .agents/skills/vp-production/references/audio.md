# Remote Audio Delivery & Cadence Standards

Voice/reference/rate come from the current brief, with request provenance. Synthesized audio must adhere to the vocal persona matrix and pacing standards documented in [voice-cadence-pacing.md](../../vp-channel-patterns/references/voice-cadence-pacing.md) and [vp-scriptwriting](../../vp-scriptwriting/SKILL.md).

## 1. Acoustic Constants & Tail Buffer Compensation
The synthesis engine (`sys/adapters.py`) automatically appends trailing silence gaps:
- **Intermediate scene boundary:** $P_{\text{tail}} = 0.70\text{s}$ (`DEFAULT_PAUSE['para']`).
- **Final scene boundary:** $P_{\text{tail}} = 0.35\text{s}$ (`DEFAULT_PAUSE['tail']`).
- **Comma / minor clause pause:** $P_{\text{comma}} = 0.30\text{s}$ (`DEFAULT_PAUSE['minor']`).
- **Dramatic pause markers:** Intentional suspense breaks written as `[pause:900ms]` (0.8s–1.2s) must be preserved in narration text and accounted for in timeline budgets.

## 2. OmniVoice Boundary Silence Trimming & Calibrated Pauses (ERR-20261011-02)
To eliminate double-padding stutter and unnatural acoustic gaps:
- **Automatic boundary trimming (`_trim_silence`):** OmniVoice generates internal leading (`50–180ms`) and trailing (`180–420ms`) silence. The worker trims leading silence to 25ms and trailing silence to 30ms with an 8ms linear fade ramp before saving/stitching.
- **Calibrated sentence pauses:**
  - Short sentences (`< 8` words): `0.20s` pause (total acoustic gap ~0.25s).
  - Standard sentences: `0.28s` pause (total acoustic gap ~0.33s).
  - Dramatic pivots (`[pause:...]`): `0.48s` pause (total acoustic gap ~0.53s).

All script lines must be pre-validated with `sys/tools/script_cadence_checker.py` to ensure the measured/predicted audio duration aligns with scene budgets within $\pm 0.3\text{s}$ (`<= 0.25s` physical drift between final rendered MP4 and WAV).

## 3. Dynamic Pacing & Voice Matrix
- **Hook & Empathy (Phase 1):** ~4.2 syl/s (Vietnamese) / ~145–150 wpm (English).
- **Causal Evidence & Mechanism (Phase 2):** ~4.0 syl/s (Vietnamese) / ~135–140 wpm (English).
- **Philosophical Payoff (Phase 3):** ~3.6–3.8 syl/s (Vietnamese) / ~120–125 wpm (English).
- **Canonical Voice (`sys/config.json`):** `Adam` (`assets/voices/adam/profile.json`, `speed: 1.22`, `num_step: 32`, `batch_size: 4`, `-14.0 LUFS`, `-1.5 dBTP`, `48kHz` Mono PCM16) for all outputs (`vi` and `en`) via `kjanh/KhanhTTS-OmniVoice` on Colab T4. No local TTS fallback.

## 4. Remote Delivery & Audio Invariants
Specify intent and pronunciation risks as craft notes. Only `learner_pause_seconds` has the existing scene-tail hold behavior; intent notes do not guarantee emotion and images do not demonstrate moving lips. Practice holds only when requested/useful, with question/model at the scene boundary and feedback after.

Use actual measured WAV duration, content boundary and pauses for timeline. Technical format/silence/provenance checks do not certify stress, accent or naturalness. When listening is unavailable, report that limit; do not invoke a mandatory reviewer in auto.

Keep synthesis on Colab; missing T4/model/reference is a capability issue, not permission for local fallback. No forced Foley/music, a universal solo persona or rate from the skill. SFX/mixing requires an implemented supported contract. Collect existing remote request on the same account/session before retrying; release dedicated VM after durable collection.

Layer anchors are interpolated inside the real audio chunks; keep narration quotes exact so anchors resolve.
