# Format-aware narration pauses — implementation and acceptance plan

Date: 2026-10-18. Policy: `format_v1`. Status: implemented; perceptual acceptance pending.

## 1. Problem and measured baseline

The previous explicit-output pipeline reads `tts_pause` (0.50 s per sentence,
0.70 s per intermediate scene, 0.35 s at the end). Configuration fields
`tts_calibrated_pauses` and `audio_trim_silence` were not consumed by that path.
The worker already trims utterances independently with 25 ms lead, 30 ms trail
and an 8 ms fade. Boundary buffers add approximately 55 ms between utterances.

Inspection of existing audio revisions in the source checkout found:

| Job | WAV duration | Inserted boundary silence | Share |
| --- | ---: | ---: | ---: |
| academic-q1-short-t1, audio/2 | 48.00 s | 6.55 s | 13.6% |
| academic-q1-short-t2, audio/3 | 50.82 s | 7.05 s | 13.9% |
| academic-q1-short-t3, audio/1 | 48.76 s | 6.55 s | 13.4% |
| full-frame-16x9-001, audio/3 | 375.91 s | 70.95 s | 18.9% |

These are source-WAV/request measurements, not YouTube retention observations.
The long video's SC01 has 4.70 s of inserted sentence/scene silence. Its internal
low-level intervals were 0.124–0.475 s at -35 dB with a 120 ms minimum detector
window; low amplitude is not necessarily complete silence or an unwanted pause.

## 2. Default policy (additional silence, in seconds)

The single source of truth is `PROFILES[*].narration_pauses` in
`sys/format_profiles.py`. Do not copy editable defaults into config or prompts.

| Boundary | short_9x16 | long_16x9 |
| --- | ---: | ---: |
| Sentence with fewer than 8 whitespace tokens | 0.16 | 0.20 |
| Other sentence | 0.22 | 0.28 |
| SC01 short sentence | 0.12 | 0.16 |
| SC01 other sentence | 0.16 | 0.20 |
| Minor clause, only when splitting an utterance over 180 characters | 0.12 | 0.16 |
| Intermediate scene | 0.30 | 0.40 |
| Final video tail | 0.15 | 0.25 |
| Suggested authored pivot, advisory only | 0.45 | 0.60 |

These are initial engineering settings for listening trials, not scientifically
validated optima for Vietnamese videos. Whitespace tokens are an approximate
Vietnamese syllable proxy, not an English syllable counter. All of SC01 receives
the opening rule; this is a scene contract, not a measured 15-second cutoff.

Do not infer a major conceptual transition from an image cut, keywords, tone,
chapter number or a random duration. Authors can use an explicit pause at the
end of a scene for a substantial transition (short: 0.40–0.50 s; long: 0.60–0.80 s).
Visual edits can occur during continuous speech.

## 3. Boundary precedence and integrity

1. Split at sentence ends, preserving closing quotation marks and transcript text.
2. Split very long sentences at existing clause punctuation; ordinary commas
   remain inside an utterance and receive model-controlled natural timing.
3. An explicit `[pause:450ms]` or `[pause:0.45s]` replaces that boundary's default.
   Preserve existing 800/900 ms tags exactly; never silently shorten authored tags.
4. Preserve terminal tags too. Adjacent tags add, with a maximum of 8 s.
   Invalid, nonfinite, leading or malformed tags fail with a clear error.
5. The last chunk uses the scene/video tail instead of a second sentence pause.
   A terminal explicit tag replaces this default. `learner_pause_seconds` remains
   a minimum hold: use max(resolved tail, requested hold), never add both.
6. Reject explicit tags in SC01, retaining short automatic sentence breaths.
7. Keep VietNarrator, nominal speed 1.0, existing tone multipliers, internal TTS
   pauses, boundary trimming and mastering unchanged.

## 4. Routing, request identity and compatibility

- `sys/config.json` selects `tts_pause_policy: format_v1` for explicit-output jobs.
- Missing selector or `legacy` keeps the former path. Jobs without outputs[] keep
  legacy adapter behavior. Legacy `tts_pause` remains available for rollback.
- Resolve a profile from outputs belonging to each language, independently of
  which language is primary. English portrait gets short pauses too.
- A language reused by both aspects has one shared WAV and uses long-form pauses.
  Reused omni-platform excerpts keep that source timing. A standalone short can
  receive independent short timing through a separate explicit-output job.
- Apply sentence segmentation and exact pauses to secondary languages as well.
  Existing secondary-segment assembly supports this without a new worker import.
- Include `pause_plan.version`, per-language profile, each boundary/reason and total
  boundary silence in the hashed request. Changed pauses invalidate assembled
  request caches; unchanged utterances can still reuse their waveform cache.
- `inserted_seconds` counts planned boundary silence only. It excludes natural
  intra-utterance pauses, 25/30 ms buffers and bilingual span gaps (currently 0.18 s).
- Preserve all saved requests, revisions, approval journals, WAVs and MP4s.
  Regenerate through normal revision/invalidation commands; never edit snapshots.

## 5. Work breakdown and delivery state

| Step | Work | State |
| --- | --- | --- |
| 1 | Inspect current request/WAV timing and identify inactive config | Done |
| 2 | Add format-profile defaults and typed boundary planner | Done |
| 3 | Route primary/secondary languages and record request provenance | Done |
| 4 | Add read-only budget preview and automatic regression coverage | Done |
| 5 | Update skills, playbook and this implementation plan | Done |
| 6 | Run focused tests, AST integrity, conveyor, lint and CI evidence | See verification report |
| 7 | Produce a short and long sample on Colab and listen in context | Pending media acceptance |
| 8 | Adopt revised scripts for new work based on listening/retention | Pending evidence |

The desktop does not synthesize speech or render video during contract tests.
Synthetic-model PCM tests prove silence assembly and manifest timing, not voice
naturalness. No GPU allocation or regeneration of existing production jobs is
required to implement this policy.

## 6. Preview and automated acceptance

```bash
python3 sys/tools/preview_narration_pauses.py \
  --brief sys/runs/<job>/brief-current.json \
  --content sys/runs/<job>/revisions/content/<revision>/content.json \
  --out sys/reports/<job>-pause-preview.json

python3 -m pytest sys/tests/test_narration_pauses.py \
  sys/tests/test_colab_worker.py sys/tests/test_colab_tts.py \
  sys/tests/test_human_naturalness_upgrades.py
./pipeline run
```

Preview does not modify job state or contact providers. It is an exact boundary
budget for format_v1, not an estimate of the model's speaking duration. Legacy
cadence and story-planning duration heuristics remain approximate; their hardcoded
historical tail/commas must not be mistaken for this policy's runtime budget.

Regression criteria: format selection, short/regular/opening sentences, quoted
punctuation, long-clause splits, exact and adjacent tags, terminal tags, SC01
rejection, finite/range validation, learner-hold max semantics, dual shared tracks,
secondary-language tone/retakes, request identity, PCM sample counts and manifest
content boundaries. Run existing full-frame/format/render checks unchanged.

## 7. Real-media trial and rollout

1. Pick one new 45–60 s standalone short and one long explainer. Keep the same
   authored text, voice, seed, tone and images for a controlled comparison.
2. Preserve the baseline revision; generate a new audio revision via pilot/Colab.
3. Listen to the hook, an ordinary transition, a dense explanation and the ending.
   Check sentence joins, final consonants, breath room and intentional pivots.
4. Compare measured inserted silence with pause_plan, and check internal silence
   separately. Do not automatically delete low-amplitude phonemes or breaths.
5. Regenerate SRT and visual timelines from the new WAV; render remotely and verify
   stream/duration contracts with ffprobe. Check anchors/captions at every join.
6. Shortening silence can take a short below 45 s. If the job explicitly requires
   45–60 s, revise useful content; do not pad silence or change speed to fill time.
   Likewise preserve explicit duration requirements for long jobs.
7. A previous coarse projection suggested roughly 30 s saved on the existing long
   video and 3–4 s on shorts. These are not measured new outputs; actual results
   depend on short-sentence classification, SC01 and retained explicit tags.
8. Release any newly created Colab/Chrome resources after durable collection.
9. For published trials, compare similar topics/lengths using retention around
   actual joins and Shorts stayed-to-watch; do not attribute changes to pauses alone.

### Dry-run against existing source scripts

The read-only preview retains existing explicit 900 ms tags. It reports these
new boundary budgets, without creating any new WAV:

| Job | Previous inserted silence | format_v1 planned silence |
| --- | ---: | ---: |
| academic-q1-short-t1 | 6.55 s | 3.29 s |
| academic-q1-short-t2 | 7.05 s | 3.51 s |
| academic-q1-short-t3 | 6.55 s | 3.29 s |
| full-frame-16x9-001 | 70.95 s | 30.31 s |

SC01 planned silence in the long script drops from 4.70 s to 1.30 s. Assuming
identical utterance audio, the long track would be about 335.27 s (5:35), and the
first short about 44.74 s. These are projections, not regenerated media. The
short therefore needs a content revision if the 45-second floor is required.

## 8. Rollback

Set `tts_pause_policy` to `legacy` before the next audio submission, then use the
normal pipeline revision flow. Restore an already approved artifact by selecting
its existing revision through supported commands. Do not rewrite its request hash,
DB, WAV, captions or render manifest. Rollback never disables worker-side trimming.
