# Troubleshooting White Tile Drops & Frame Jitter in Remotion

## 1. Symptoms
- Rendered MP4 video exhibits white rectangular artifacts (white tiles) near the bottom or center of the frame (frequently in the bottom 1/5).
- Frame drops cause stick-figure sticker motions to stutter or break line-boil jitter rhythm.

---

## 2. Root Cause
- When Remotion captures frame-by-frame snapshots via Puppeteer/Playwright on headless GPU or hybrid GPU environments, Chromium reads pixels from the canvas surface before rasterization and compositing complete their draw cycle.

---

## 3. Proven Remedies

### 1. Enable Compositor Synchronization Flags
Mandatory flags:
- `--run-all-compositor-stages-before-draw`: Forces Chromium to finish all compositor pipeline stages before permitting pixel readback.
- `--disable-gpu-rasterization`: Forces Chromium to perform rasterization on the CPU compositor when GPU raster latency is asymmetric.

### 2. Fix Z-Index Layering for Captions and Stickers
Verify `sys/renderer/captions.mjs` and `sys/renderer/index.tsx`:
- `zIndex` of the caption container (`captions`) must be `30`.
- Sticker layers must have `zIndex` between `10` and `20`.
- Background plate must have `zIndex` of `1` with `objectFit: 'cover'`.

### 3. Never Enable Blanket Full-Frame `line_boil: true` on 1080p Raster Plates
- When `--disable-gpu-rasterization` is active (mandatory on headless Colab T4), SVG `<feTurbulence>` + `<feDisplacementMap scale={3}>` (`line_boil: true`) runs in **CPU software across 2,073,600 pixels per frame**, slowing 1080p rendering by **8x–10x** (12+ minutes for a 64s chapter) and pulling dashed black out-of-bounds pixels into the top/left borders at `scale = 1.0`.
- **Remedy**: Do **not** set `"line_boil": true` on full-screen `1920x1080` raster beats in `props.json`. Use camera motion effects (`zoom_in`, `zoom_out`, `punch_in`, `pan_left`, `pan_right`, `slide_left`, `shake`, `fade`, `hold`) for full-frame plates, and reserve `line_boil` / `boilJitter` for cut-out stickers (`scene.layers`).

### 4. Verification Test
Run the integrity test suite:
```bash
pytest sys/tests/test_renderer_tile_integrity.py
```
All assertions covering z-index ordering, Chrome flags, and flash prevention must PASS.
