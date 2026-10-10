# Similarity Comparison with Minh Quân Pro V4

Official sources retrieved on 2026-09-23:
- https://github.com/pnnbao97/VieNeu-TTS — V4 is proprietary to VieNeu; V3 Turbo is the open release. No other confirmed source distributes genuine V4 voice for free.
- https://docs.vieneu.io/vi/docs/sdk/voice-cloning/ — reference samples can bypass denoising if already clean.

This is AI audio synthesized locally via V3 Turbo, not V4. Preserves the legacy reference sample; does not confirm sample licensing via search results.

A: Denoised reference sample, temperature 0.8 (reproducibility control).
B: Non-denoised reference sample, temperature 0.8.
C: Non-denoised reference sample, temperature 0.65.

Each configuration includes a sentence matching source sample content (same) and a new Vietnamese–English sentence (mixed). Constant top_p 0.95, original speed, unchanged pitch, normalized to -23 LUFS with peak limiting. Compare A/B for denoising impact, B/C for temperature impact. Single synthesis per item; stability not yet proven. NumPy seeds do not guarantee every generator in the engine is deterministically fixed.

Not yet evaluated by listening; no claim of which sample is more similar. Listeners must rate timbre similarity independently from pronunciation accuracy. Production defaults remain unchanged.

Reproduction: Use `sys/.venv-tts/bin/python` to run `../refine.py` from project root with full path. Parameters and WAV hashes stored in `result.json`.
