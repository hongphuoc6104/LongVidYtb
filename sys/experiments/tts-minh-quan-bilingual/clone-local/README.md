# Local Clone from Minh Quân Pro V4 Sample

This is a user-requested experiment utilizing demo audio as reference for the installed
**VieNeu v3 Turbo ONNX FP32**. Does not download V4 models or call paid synthesis APIs.
Timbre quality and pronunciation accuracy have not been verified by auditory review.

Sources and checksums are located in `source.json`; usage rights are not independently verified.
Do not register as a global preset or edit project defaults.

Run from project root:

```bash
sys/.venv-tts/bin/python -B sys/experiments/tts-minh-quan-bilingual/clone-local/run_clone.py
```

`voice-profile.npz` stores speaker embeddings and reference codes for local reuse.
Load via `numpy.load(..., allow_pickle=False)` and pass a dictionary containing
`speaker_emb` and `codes` into the `voice` parameter of `tts.infer`.

`index.html` contains the source sample and three clone/preset pairs: Vietnamese, English, and Vietnamese–English.
`*-raw.wav` retains original outputs; remaining WAVs only adjust loudness without altering
pitch or speed. The source V4 sample is preserved for reference, potentially differing in loudness.
Existing generated samples are preserved on subsequent runs, without rerunning to cherry-pick outputs.

Do not treat valid files or successful model execution as proof of acceptable pronunciation.
