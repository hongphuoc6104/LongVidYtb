# Issue Index & Proven Remedies

List of technical issues recorded during pipeline operation:

| Date Recorded | Subsystem / Job ID | Symptom Summary | Proven Remedy ("What Worked to Fix Bugs") |
|---|---|---|---|
| 2026-10-06 | Renderer / Colab Headless | White tile drops / Frame drops on headless Colab T4 | Wrap Chrome via executable shell wrapper + flags `--run-all-compositor-stages-before-draw --disable-gpu-rasterization` + `DISABLE_FROM_SURFACE='true'`. |
| 2026-10-08 | Flow CDP / Network | Timeout > 120s or Chrome extension disconnected | Add 4.0s delay between requests to avoid bot rate limits; verify port `8100` daemon and active Extension tab. |
| 2026-10-09 | Flow CDP / Multi-Profile & `BELUGA` ([log](20261009-ancient-humans-ch1-flow-cdp-multiprofile-beluga.md)) | `NANO_BANANA_2_1` wire mismatch, cross-profile `based_on` `media_id` error, `PUBLIC_ERROR_UNUSUAL_ACTIVITY` on tab reload | Map `NANO_BANANA_2_1` $\to$ `"BELUGA"` (`slot12` UUID on fresh gen); isolate per-profile slots & route `based_on` chains to same `profile_index`; wrap `executeWithPristine` with `Object.assign` neuter; use in-place backoff instead of tab reload. |
| 2026-10-09 | Renderer / Colab T4 Slowdown ([log](20261009-ancient-humans-ch1-colab-render-lineboil-slowdown.md)) | Upload fails when Colab session expires; 64s chapter takes >12m to render with dashed black border teeth | Auto-bootstrap `video-pilot-tts` T4 session & `/content/render-runtime`; never enable blanket `"line_boil": true` (SVG `<feTurbulence>`) on full-screen `1920x1080` raster plates under `--disable-gpu-rasterization`. |


- [colab-1791726905772317884.md](colab-1791726905772317884.md) — Colab TTS cần kiểm tra.

- [colab-1791726940787501565.md](colab-1791726940787501565.md) — Colab TTS cần kiểm tra.

- [colab-1791727082877599957.md](colab-1791727082877599957.md) — Colab TTS cần kiểm tra.

- [colab-1791727123668963406.md](colab-1791727123668963406.md) — Colab TTS cần kiểm tra.

- [colab-1791818378068968011.md](colab-1791818378068968011.md) — Colab TTS cần kiểm tra.
- [academic-detective-9x16-001 — audio](1791818378069316937-academic-detective-9x16-001-audio.md)
- [academic-detective-9x16-001 — images](1791818660042404310-academic-detective-9x16-001-images.md)
