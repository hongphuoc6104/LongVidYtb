# Minh Quân Pro Experiment — Vietnamese & American English

Standalone experiment testbed, retaining **VieNeu v3 Turbo / ONNX FP32 / Minh Quân Pro**. Does not modify
production configuration, installed dependencies, approved scripts, or job data. Variations of
`I` and `<en>…</en>` apply only to marked English sections within the test suite.

## Listening and Evaluation

Open `artifacts/index.html` directly or view the local server via the `serve` command.
Select sentences, listen to samples A/B/C, score them, log errors with timestamps, and download the review JSON.
Labels A/B/C are randomized per sentence; they do not consistently map to a specific
configuration. The evaluation page never auto-fills scores or fakes listening verification.

Human raters evaluating English must distinguish American phonemes, stress, and rhythm. Without
qualified listening evaluation, the status remains **unrated**, rather than pass or
fail. Evaluation ballots do not constitute Pilot production media approval decisions.

## Execution from Project Root

```bash
sys/.venv-tts/bin/python -B sys/experiments/tts-minh-quan-bilingual/lab.py prepare
sys/.venv-tts/bin/python -B sys/experiments/tts-minh-quan-bilingual/lab.py run A
sys/.venv-tts/bin/python -B sys/experiments/tts-minh-quan-bilingual/lab.py serve --port 8768
```

The server binds strictly to `127.0.0.1`. Never downloads or updates models or invokes paid APIs.
If the model is not found in cache, it halts to report missing environment dependencies.

After receiving genuine evaluation ballots:

```bash
sys/.venv-tts/bin/python -B sys/experiments/tts-minh-quan-bilingual/lab.py review A --file /path/to/evaluation-minh-quan-A.json
sys/.venv-tts/bin/python -B sys/experiments/tts-minh-quan-bilingual/lab.py run B
```

Proceed sequentially through `A → B → C-speed → C-split → D → E → final`.
Each round only executes when valid ballots exist from the prior round. Never auto-select via phonemes or
durations. Re-running the command resumes interrupted runs; `--limit 1` can be used
to test a single sample first. Imported reviews are never overwritten.

| Round | Variants | Scope |
|---|---|---|
| A | Baseline / Standard English orthography / English tags | 13 items with English × 3, plus 8 Vietnamese control sentences: 47 WAVs |
| B | Baseline / Punctuation preservation | 21 items + 2 short question samples, 2 takes per item |
| C-speed | 0.92 / 0.96 / 1.00 | 21 items, speeds share source WAV |
| C-split | Full scene / Per sentence / Language boundary split | 21 items + single word `wake`, phrase `get up` |
| D | Temperature 0.65 / 0.50 / 0.80 | 8 hardest items from C-split ballots, 3 independent runs per config |
| E | Volume leveling / Production EQ and limiter | 8 hard items, sharing source WAV per pair |
| final | Selected configuration | 8 retained items + 5 live scenes |

Prioritize configurations with fewer severe errors, followed by higher average score. If error rates
are identical and score delta ≤ 0.1/5, retain the minimal-change option (baseline,
0.92, full scene, temperature 0.65, or volume leveling only). Winning a round
does not mean passing final criteria.

## Data and Experiment Governance

- `corpus.json`: 16 core items, 5 scenes from `vocab-wake-004`, 8 retained items from
  `vocab-wake-up-003`, 4 diagnostic items. Stores verbatim sentences, English span positions,
  revision paths, scene IDs, and content checksums. The 8 retained items are not
  synthesized before the final round; they are domain-relevant but not representative of all vocabulary.
- `frozen.json`: Checksums for sentence sets and immutable control files.
- `environment.json`: Package versions, loaded model/codec hashes, trial codes, and voice profile.
- `history/`: Exact copies of revision 2 production WAVs with legacy requests and metadata.
- `cache/<hash>/`: Source float WAVs, read units, input logs,
  normalized sentences, phonemes, seeds, and pauses. Never trims head/tail of source WAVs.
- `rounds/<round>/`: Locked plans, test WAVs, measurement results, processing logs, and listening pages.
- `reviews/`, `decisions/`: Original evaluation ballots and trial configuration decisions.

New WAVs are standalone trial clips, not claiming bit-for-bit recreation of the full production
concatenation pipeline. Historical WAVs serve as authentic control references. Seeds are tied to sentences and runs;
seeds differ across the three runs in D, but are held constant when comparing other variables. Does not guarantee
bit-identical outputs across different hardware or runtime versions.

Punctuation preservation monkey-patches functions strictly within the test process, always restored after
invocation. Never modifies `site-packages`. Numbers and abbreviations remain normalized. Emotion
tags are not used in this trial. Existing silences are measured before padding; never
adds full pause duration to WAVs already containing silence.

Reference listening loudness is **−23 LUFS**, tolerance within 0.5 LUFS. Post-processing branch E
applies production EQ, −14 LUFS normalization, and −1.5 dB limiter, then attenuates playback
to −23 LUFS for fair comparison. Never dynamically compresses only the control sample to make it louder.
Speed adjustments occur post-source synthesis, matching current implementation.

## Verification and Conclusion

```bash
sys/.venv-tts/bin/python -B -m unittest discover -s sys/experiments/tts-minh-quan-bilingual -p 'test_*.py' -v
sys/.venv-tts/bin/python -B sys/experiments/tts-minh-quan-bilingual/audit.py
```

Pass criteria: No omitted/inserted/repeated words, no tone-induced semantic errors, no mispronounced
phonemes or misplaced stress on target words; all criteria averages ≥ 4/5, no score < 3/5;
simultaneously passing across all three runs of config D and final test set. Identity retention as
Minh Quân Pro is rated independently. Acoustic measurements do not prove initial/final consonants are not swallowed.

No unbounded automated repair loops. Tools run once through the sequence above. If specific
defects remain after the final round, hand off evidence and consider at most one tracked
remediation pass, without overwriting past reports. Never auto-integrate into production.
