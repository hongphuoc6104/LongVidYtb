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

- [colab-1792252056929833821.md](colab-1792252056929833821.md) — Colab TTS cần kiểm tra.
- [academic-q1-short-t1 — render](1792252056930097148-academic-q1-short-t1-render.md)
- [academic-paradox-q1-16x9 — images](1792253041978405817-academic-paradox-q1-16x9-images.md)

- [colab-1792252025942581851.md](colab-1792252025942581851.md) — Colab TTS cần kiểm tra.
- [full-frame-16x9-explainer — audio](1792252025942906021-full-frame-16x9-explainer-audio.md)

- [colab-1792252672239638737.md](colab-1792252672239638737.md) — Colab TTS cần kiểm tra.

- [colab-1792252672239883298.md](colab-1792252672239883298.md) — Colab TTS cần kiểm tra.

- [colab-1792252832784235580.md](colab-1792252832784235580.md) — Colab TTS cần kiểm tra.

- [colab-1792252832784785357.md](colab-1792252832784785357.md) — Colab TTS cần kiểm tra.

- [colab-1792252835534344093.md](colab-1792252835534344093.md) — Colab TTS cần kiểm tra.

- [colab-1792252835534524245.md](colab-1792252835534524245.md) — Colab TTS cần kiểm tra.

- [colab-1792252835534727875.md](colab-1792252835534727875.md) — Colab TTS cần kiểm tra.

- [colab-1792252859870631909.md](colab-1792252859870631909.md) — Colab TTS cần kiểm tra.

- [colab-1792252859870866205.md](colab-1792252859870866205.md) — Colab TTS cần kiểm tra.

- [colab-1792252859871208536.md](colab-1792252859871208536.md) — Colab TTS cần kiểm tra.

- [colab-1792252943327813668.md](colab-1792252943327813668.md) — Colab TTS cần kiểm tra.

- [colab-1792252943328129658.md](colab-1792252943328129658.md) — Colab TTS cần kiểm tra.

- [colab-1792252977243200395.md](colab-1792252977243200395.md) — Colab TTS cần kiểm tra.

- [colab-1792252977378159024.md](colab-1792252977378159024.md) — Colab TTS cần kiểm tra.

- [colab-1792253033051487768.md](colab-1792253033051487768.md) — Colab TTS cần kiểm tra.

- [colab-1792253033051930351.md](colab-1792253033051930351.md) — Colab TTS cần kiểm tra.
- [academic-paradox-q1-16x9 — audio](1792253197960648662-academic-paradox-q1-16x9-audio.md)
- [full-frame-16x9-explainer — audio](1792253227122824670-full-frame-16x9-explainer-audio.md)

- [colab-1792253651585045841.md](colab-1792253651585045841.md) — Colab TTS cần kiểm tra.

- [colab-1792253780294598292.md](colab-1792253780294598292.md) — Colab TTS cần kiểm tra.

- [colab-1792253780294828907.md](colab-1792253780294828907.md) — Colab TTS cần kiểm tra.

- [colab-1792253993838159400.md](colab-1792253993838159400.md) — Colab TTS cần kiểm tra.

- [colab-1792253994782399123.md](colab-1792253994782399123.md) — Colab TTS cần kiểm tra.

- [colab-1792253994925755950.md](colab-1792253994925755950.md) — Colab TTS cần kiểm tra.
- [academic-paradox-q1-16x9 — images](1792255000051562908-academic-paradox-q1-16x9-images.md)
- [academic-paradox-q1-16x9 — images](1792255186957991840-academic-paradox-q1-16x9-images.md)

- [colab-1792254137529024600.md](colab-1792254137529024600.md) — Colab TTS cần kiểm tra.
- [academic-q1-short-t2 — audio](1792254137529528362-academic-q1-short-t2-audio.md)

- [colab-1792254329856848887.md](colab-1792254329856848887.md) — Colab TTS cần kiểm tra.
- [academic-q1-short-t2 — audio](1792254329857068973-academic-q1-short-t2-audio.md)
- [academic-q1-short-t2 — images](1792254403599420516-academic-q1-short-t2-images.md)
- [academic-q1-short-t2 — images](1792254492066407467-academic-q1-short-t2-images.md)

- [colab-1792254736537953606.md](colab-1792254736537953606.md) — Colab TTS cần kiểm tra.
- [full-frame-16x9-001 — audio](1792254736538483803-full-frame-16x9-001-audio.md)
- [academic-q1-short-t2 — render](1792254870909663303-academic-q1-short-t2-render.md)

- [colab-1792255061750672681.md](colab-1792255061750672681.md) — Colab TTS cần kiểm tra.
- [academic-q1-short-t2 — render](1792255061751119087-academic-q1-short-t2-render.md)

- [colab-1792255183339311388.md](colab-1792255183339311388.md) — Colab TTS cần kiểm tra.
- [academic-q1-short-t2 — render](1792255183339709905-academic-q1-short-t2-render.md)

- [colab-1792255317083013947.md](colab-1792255317083013947.md) — Colab TTS cần kiểm tra.
- [academic-q1-short-t2 — render](1792255317083314441-academic-q1-short-t2-render.md)

- [colab-1792255597779969385.md](colab-1792255597779969385.md) — Colab TTS cần kiểm tra.
- [academic-paradox-q1-16x9 — render](1792255597780299473-academic-paradox-q1-16x9-render.md)

- [colab-1792255918795423647.md](colab-1792255918795423647.md) — Colab TTS cần kiểm tra.
- [academic-q1-short-t2 — render](1792255918795668768-academic-q1-short-t2-render.md)

- [colab-1792257001760310013.md](colab-1792257001760310013.md) — Colab TTS cần kiểm tra.
- [full-frame-16x9-001 — render](1792257001760594593-full-frame-16x9-001-render.md)

- [colab-1792262868163194746.md](colab-1792262868163194746.md) — Colab TTS cần kiểm tra.
- [full-frame-16x9-001 — render](1792262868163458794-full-frame-16x9-001-render.md)

- [colab-1792274051890696918.md](colab-1792274051890696918.md) — Colab TTS cần kiểm tra.
- [academic-q1-short-t1 — render](1792274051890961796-academic-q1-short-t1-render.md)

- [colab-1792274131068828139.md](colab-1792274131068828139.md) — Colab TTS cần kiểm tra.

- [colab-1792275397882056890.md](colab-1792275397882056890.md) — Colab TTS cần kiểm tra.
- [academic-q1-short-t1 — render](1792275397882530821-academic-q1-short-t1-render.md)
- [feynman-jargon-trap-9x16 — content](1792277102108965749-feynman-jargon-trap-9x16-content.md)
