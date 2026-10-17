# Issue Index & Proven Remedies

List of technical issues recorded during pipeline operation:

| Date Recorded | Subsystem / Job ID | Symptom Summary | Proven Remedy ("What Worked to Fix Bugs") |
|---|---|---|---|
| 2026-10-06 | Renderer / Colab Headless | White tile drops / Frame drops on headless Colab T4 | Wrap Chrome via executable shell wrapper + flags `--run-all-compositor-stages-before-draw --disable-gpu-rasterization` + `DISABLE_FROM_SURFACE='true'`. |
| 2026-10-08 | Flow CDP / Network | Timeout > 120s or Chrome extension disconnected | Add 4.0s delay between requests to avoid bot rate limits; verify port `8100` daemon and active Extension tab. |
| 2026-10-09 | Flow CDP / Multi-Profile & `BELUGA` ([log](20261009-ancient-humans-ch1-flow-cdp-multiprofile-beluga.md)) | `NANO_BANANA_2_1` wire mismatch, cross-profile `based_on` `media_id` error, `PUBLIC_ERROR_UNUSUAL_ACTIVITY` on tab reload | Map `NANO_BANANA_2_1` $\to$ `"BELUGA"` (`slot12` UUID on fresh gen); isolate per-profile slots & route `based_on` chains to same `profile_index`; wrap `executeWithPristine` with `Object.assign` neuter; use in-place backoff instead of tab reload. |
| 2026-10-09 | Renderer / Colab T4 Slowdown ([log](20261009-ancient-humans-ch1-colab-render-lineboil-slowdown.md)) | Upload fails when Colab session expires; 64s chapter takes >12m to render with dashed black border teeth | Auto-bootstrap `video-pilot-tts` T4 session & `/content/render-runtime`; never enable blanket `"line_boil": true` (SVG `<feTurbulence>`) on full-screen `1920x1080` raster plates under `--disable-gpu-rasterization`. |
| 2026-10-16 | Flow CDP / Browser Lease ([log](20261016-flow-cdp-sequential-profile-close.md)) | Mass launch of 10 Chrome profiles exhausts RAM; bound Flow jobs lose production identity under concurrency | Open and close profiles sequentially during login (`sequential_close`); propagate `jobId` separately from `testCase` and serialize requests when bound to a fixed profile. |
- [academic-q1-short-t1 — audio](1792249626389072818-academic-q1-short-t1-audio.md)
- [academic-q1-short-t1 — images](1792249729112722896-academic-q1-short-t1-images.md)
- [academic-q1-short-t1 — images](1792249834170276261-academic-q1-short-t1-images.md)
- [academic-q1-short-t1 — images](1792249940864787856-academic-q1-short-t1-images.md)
- [academic-q1-short-t1 — images](1792250347571860480-academic-q1-short-t1-images.md)
- [academic-q1-short-t1 — images](1792250504898058376-academic-q1-short-t1-images.md)
