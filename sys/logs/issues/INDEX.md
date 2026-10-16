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
- [academic-detective-9x16-001 — images](1791855778262068904-academic-detective-9x16-001-images.md)
- [academic-detective-9x16-001 — images](1791855832631763485-academic-detective-9x16-001-images.md)
- [academic-detective-9x16-001 — images](1791856506549260469-academic-detective-9x16-001-images.md)
- [academic-detective-9x16-001 — images](1791857265486599976-academic-detective-9x16-001-images.md)
- [academic-detective-9x16-001 — images](1791857430988310265-academic-detective-9x16-001-images.md)

- [colab-1791857531929922446.md](colab-1791857531929922446.md) — Colab TTS cần kiểm tra.
- [academic-detective-9x16-001 — render](1791857531930254692-academic-detective-9x16-001-render.md)

- [colab-1791857570303681985.md](colab-1791857570303681985.md) — Colab TTS cần kiểm tra.

- [colab-1791857580577755022.md](colab-1791857580577755022.md) — Colab TTS cần kiểm tra.

- [colab-1791857772373505704.md](colab-1791857772373505704.md) — Colab TTS cần kiểm tra.
- [academic-detective-9x16-001 — render](1791857772373771105-academic-detective-9x16-001-render.md)

- [colab-1791858013173224428.md](colab-1791858013173224428.md) — Colab TTS cần kiểm tra.
- [academic-detective-9x16-001 — render](1791858013173735289-academic-detective-9x16-001-render.md)



- [colab-1791867208573731323.md](colab-1791867208573731323.md) — Colab TTS cần kiểm tra.
- [attention-architect-16x9-001 — audio](1791867208574085350-attention-architect-16x9-001-audio.md)
- [attention-architect-16x9-001 — images](1791868022626088593-attention-architect-16x9-001-images.md)
- [attention-architect-16x9-001 — images](1791868316529125173-attention-architect-16x9-001-images.md)
- [attention-architect-16x9-001 — images](1791868538073801136-attention-architect-16x9-001-images.md)

- [colab-1791869199968810514.md](colab-1791869199968810514.md) — Colab TTS cần kiểm tra.
- [attention-architect-16x9-001 — render](1791869199969371332-attention-architect-16x9-001-render.md)

- [colab-1792092071643397637.md](colab-1792092071643397637.md) — Colab TTS cần kiểm tra.
- [academic-research-paradox-16x9-13m — audio](1792092071643728895-academic-research-paradox-16x9-13m-audio.md)
- [academic-research-paradox-16x9-13m — images](1792092439778141157-academic-research-paradox-16x9-13m-images.md)
- [academic-research-paradox-16x9-13m — images](1792093162977397304-academic-research-paradox-16x9-13m-images.md)
- [academic-research-paradox-16x9-13m — images](1792093671674156964-academic-research-paradox-16x9-13m-images.md)
- [academic-research-paradox-16x9-13m — images](1792094805975879628-academic-research-paradox-16x9-13m-images.md)
- [academic-research-paradox-16x9-13m — images](1792095300922428310-academic-research-paradox-16x9-13m-images.md)
- [academic-research-paradox-16x9-13m — images](1792095645105889311-academic-research-paradox-16x9-13m-images.md)
- [academic-research-paradox-16x9-13m — images](1792096346016532400-academic-research-paradox-16x9-13m-images.md)
- [academic-research-paradox-16x9-13m — images](1792096802675221004-academic-research-paradox-16x9-13m-images.md)
- [academic-research-paradox-16x9-13m — images](1792097408290966545-academic-research-paradox-16x9-13m-images.md)
- [academic-research-paradox-16x9-13m — images](1792097933116655394-academic-research-paradox-16x9-13m-images.md)
- [academic-research-paradox-16x9-13m — images](1792098158227869286-academic-research-paradox-16x9-13m-images.md)

- [colab-1792098649023812170.md](colab-1792098649023812170.md) — Colab TTS cần kiểm tra.
- [academic-research-paradox-16x9-13m — render](1792098649024113905-academic-research-paradox-16x9-13m-render.md)

- [colab-1792098725558574943.md](colab-1792098725558574943.md) — Colab TTS cần kiểm tra.
