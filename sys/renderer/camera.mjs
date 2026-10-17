// Semantic camera movement selector & Weyl Golden-Ratio Non-Repeating Cinematic Vector Engine
const PHI_1 = 0.6180339887498949; // Conjugate golden ratio
const PHI_2 = 0.7548776662466927; // Plastic constant R2_1
const PHI_3 = 0.5698402909980532; // Plastic constant R2_2

function fract(x) {
  return x - Math.floor(x);
}

function hashSceneIdentity(scene, beatIndex = 0) {
  const raw = `${scene?.id || 'SC01'}:${scene?.title || ''}:${Math.round((scene?.start || 0) * 10)}:${beatIndex}`;
  let h = 2166136261;
  for (let i = 0; i < raw.length; i++) {
    h ^= raw.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return Math.abs(h >>> 0);
}

export function selectSemanticCameraEffect(beat, scene, beatIndex = 0) {
  const explicit = beat?.camera_motion || beat?.effect;
  if (beat?.shot_type === 'white_card') return 'hold';
  if (explicit && !['auto', 'cut', 'fade'].includes(explicit)) return explicit;
  const intent = String(beat?.camera_intent || scene?.camera_intent || scene?.camera || '').toLowerCase();
  const desc = String(beat?.description || scene?.action || scene?.purpose || '').toLowerCase();

  if (intent.includes('hold') || desc.includes('diagram') || desc.includes('sơ đồ')) return 'hold';
  if (intent.includes('reveal') || intent.includes('shock') || desc.includes('bất ngờ') || desc.includes('giật mình')) return 'punch_in';
  if (intent.includes('establish') || intent.includes('wide') || desc.includes('toàn cảnh') || desc.includes('rộng')) return 'zoom_out';
  if (intent.includes('detail') || intent.includes('focus') || intent.includes('tension') || desc.includes('cận cảnh') || desc.includes('tập trung')) return 'zoom_in';
  if (intent.includes('pan_left') || intent.includes('contrast') || desc.includes('đối lập')) return 'pan_left';
  if (intent.includes('pan_right') || desc.includes('dòng thời gian') || desc.includes('hành trình')) return 'pan_right';

  // Strip numeric suffix from scene.id so incrementing SC01->SC02 (+1) never cancels out beatIndex*3 (+3) mod 4
  const prefixSeed = String(scene?.id || 'SC').replace(/\d+/g, '').split('').reduce((acc, ch) => acc + ch.charCodeAt(0), 0);
  const pool = ['zoom_in', 'pan_right', 'zoom_out', 'pan_left'];
  const prevIdx = beatIndex > 0 ? ((prefixSeed + (beatIndex - 1) * 3) % pool.length) : -1;
  let chosenIdx = (prefixSeed + beatIndex * 3) % pool.length;
  if (chosenIdx === prevIdx) {
    chosenIdx = (chosenIdx + 1) % pool.length;
  }
  return pool[chosenIdx];
}

/**
 * Determines whether two adjacent beats in a scene share the same continuous room/camera anchor group.
 * - Variations (`shot_type === 'variation'` or `based_on`) and consecutive full-scene beats stay in one unbroken glide.
 * - Concept diagrams (`white_card` / `hold`) and standalone optical lens cuts (`macro_prop`, `white_isolated`) start a clean group.
 */
export function isContinuousCameraBeat(prevBeat, currBeat) {
  if (!prevBeat || !currBeat) return false;
  if (currBeat.effect === 'slide_left' || currBeat.effect === 'fade') return false;

  const prevMotion = prevBeat.camera_motion || prevBeat.effect;
  const currMotion = currBeat.camera_motion || currBeat.effect;
  const prevIsHold = prevBeat.shot_type === 'white_card' || prevMotion === 'hold';
  const currIsHold = currBeat.shot_type === 'white_card' || currMotion === 'hold';
  if (prevIsHold || currIsHold) return false;

  if (currBeat.shot_type === 'variation' || Boolean(currBeat.based_on)) {
    return true;
  }

  const isolatedTypes = ['macro_prop', 'white_isolated'];
  if (isolatedTypes.includes(currBeat.shot_type) || isolatedTypes.includes(prevBeat.shot_type)) {
    return false;
  }

  return true;
}

/**
 * Resolves the continuous Anchor Group [startIndex..endIndex] and time window [startAt..endAt]
 * for any beat index inside a scene.
 */
export function resolveCameraAnchorGroup(imageList, activeIndex = 0, sceneSpan = 12.0) {
  const list = Array.isArray(imageList) && imageList.length > 0 ? imageList : [{ at: 0, effect: 'auto' }];
  const idx = Math.max(0, Math.min(list.length - 1, activeIndex));

  let startIndex = idx;
  while (startIndex > 0 && isContinuousCameraBeat(list[startIndex - 1], list[startIndex])) {
    startIndex--;
  }

  let endIndex = idx;
  while (endIndex + 1 < list.length && isContinuousCameraBeat(list[endIndex], list[endIndex + 1])) {
    endIndex++;
  }

  let groupIndex = 0;
  for (let i = 1; i <= startIndex; i++) {
    if (!isContinuousCameraBeat(list[i - 1], list[i])) {
      groupIndex++;
    }
  }

  const startAt = Number(list[startIndex]?.at ?? 0);
  const endAt = endIndex + 1 < list.length ? Number(list[endIndex + 1]?.at ?? sceneSpan) : Number(sceneSpan);
  const span = Math.max(0.001, endAt - startAt);

  return {
    startIndex,
    endIndex,
    startAt,
    endAt,
    span,
    groupIndex,
    anchorBeat: list[startIndex] || list[idx],
  };
}

/**
 * Resolves aspect-aware safe focal coordinates (focusX, focusY in percentages):
 * - Prioritizes beat.focus when explicitly authored (!== 0.5), then anchorBeat.focus, then aspect optical center.
 * - 16:9 Landscape: clamped to X [35%..65%], Y [35%..58%] with default optical center Y = 44%.
 * - 9:16 Portrait:  clamped to X [35%..65%], Y [35%..48%] with default optical center Y = 40% (clears bottom 18% Karaoke zone).
 */
export function resolveBeatFocus(beat, anchorBeat = null, isPortrait = false) {
  const defaultY = isPortrait ? 0.40 : 0.44;
  const maxY = isPortrait ? 48 : 58;

  const beatX = beat?.focus?.x;
  const anchorX = anchorBeat?.focus?.x;
  const rawX =
    typeof beatX === 'number' && Math.abs(beatX - 0.5) > 1e-4
      ? beatX
      : typeof anchorX === 'number' && Math.abs(anchorX - 0.5) > 1e-4
      ? anchorX
      : typeof beatX === 'number'
      ? beatX
      : 0.5;

  const beatY = beat?.focus?.y;
  const anchorY = anchorBeat?.focus?.y;
  const rawY =
    typeof beatY === 'number' && Math.abs(beatY - 0.5) > 1e-4
      ? beatY
      : typeof anchorY === 'number' && Math.abs(anchorY - 0.5) > 1e-4
      ? anchorY
      : defaultY;

  const focusX = Number(Math.min(65, Math.max(35, rawX * 100)).toFixed(2));
  const focusY = Number(Math.min(maxY, Math.max(35, rawY * 100)).toFixed(2));
  return { focusX, focusY };
}

/**
 * Generates a continuous, non-repeating 3-DOF cinematic camera trajectory (scaleStart, scaleEnd,
 * txStart, txEnd, tyStart, tyEnd, bezier) constrained by documentary film grammar.
 * Uses Weyl low-discrepancy irrational sequences coupled with scene duration and narrative tone.
 */
export function computeCinematicCameraVector(effect, scene, sceneIndex = 0, isPortrait = false, groupIndex = 0, spanOverride = null) {
  const seed = hashSceneIdentity(scene, sceneIndex) + (sceneIndex + 1) * 131 + (isPortrait ? 7919 : 0) + groupIndex * 3571;
  // Low-discrepancy quasi-random tuple in [0, 1)^3 that never repeats across scenes
  const u1 = fract(seed * PHI_1);
  const u2 = fract(seed * PHI_2);
  const u3 = fract(seed * PHI_3);

  const refDuration = isPortrait ? 6.0 : 12.0;
  const rawSpan = spanOverride !== null && spanOverride !== undefined
    ? Number(spanOverride)
    : Number((scene?.end ?? refDuration) - (scene?.start ?? 0));
  const sceneSpan = Math.max(2.0, rawSpan || refDuration);
  // Velocity-normalized duration factor adapted automatically for 16:9 long-form (12s ref) vs 9:16 Shorts (6s ref)
  const durationFactor = Math.min(1.22, Math.max(0.78, Math.sqrt(sceneSpan / refDuration)));

  const tone = String(scene?.tone || 'narrative_warm').toLowerCase();
  const toneFactor =
    tone === 'reflective_slow' ? 0.78 :
    tone === 'analytical_crisp' ? 1.08 :
    0.95;

  const amp = durationFactor * toneFactor;
  // Adaptive ease-in-out bezier control points within smooth fluid-head tripod bounds
  const c1x = Number((0.35 + 0.08 * u3).toFixed(3));
  const c2x = Number((0.58 + 0.08 * (1 - u3)).toFixed(3));

  // Aspect-aware spatial bounds: narrow 9:16 screens tighten horizontal swing (0.68x) to keep subjects centered
  const horizScale = isPortrait ? 0.68 : 1.0;
  const vertScale = isPortrait ? 1.12 : 1.0;

  // Diagonal micro-drift angle so zooms/pans never move on a robotic 1D rail
  const angle = u2 * Math.PI * 2;
  const driftX = Number((Math.cos(angle) * (0.28 + 0.26 * u1) * amp * horizScale).toFixed(4));
  const driftY = Number((Math.sin(angle) * (0.20 + 0.18 * u1) * amp * vertScale).toFixed(4));

  const zoomDelta = Number(((0.034 + 0.018 * u1) * amp * (isPortrait ? 1.06 : 1.0)).toFixed(4));
  const panSpan = Number(((1.05 + 0.55 * u1) * amp * horizScale).toFixed(4));
  const panZoomDelta = Number(((0.014 + 0.012 * u2) * amp).toFixed(4));

  if (effect === 'hold') {
    return {
      scaleStart: 1.0,
      scaleEnd: 1.0,
      txStart: 0.0,
      txEnd: 0.0,
      tyStart: 0.0,
      tyEnd: 0.0,
      bezier: [c1x, 0.0, c2x, 1.0],
    };
  }

  if (effect === 'zoom_out') {
    return {
      scaleStart: Number((1.0 + zoomDelta).toFixed(4)),
      scaleEnd: 1.0,
      txStart: driftX,
      txEnd: Number((-driftX * 0.5).toFixed(4)),
      tyStart: driftY,
      tyEnd: Number((-driftY * 0.5).toFixed(4)),
      bezier: [c1x, 0.0, c2x, 1.0],
    };
  }

  if (effect === 'pan_left') {
    const startScale = u3 > 0.5 ? 1.028 : Number((1.028 + panZoomDelta).toFixed(4));
    const endScale = u3 > 0.5 ? Number((1.028 + panZoomDelta).toFixed(4)) : 1.028;
    return {
      scaleStart: startScale,
      scaleEnd: endScale,
      txStart: Number((panSpan * 0.5).toFixed(4)),
      txEnd: Number((-panSpan * 0.5).toFixed(4)),
      tyStart: Number((-driftY * 0.6).toFixed(4)),
      tyEnd: Number((driftY * 0.6).toFixed(4)),
      bezier: [c1x, 0.0, c2x, 1.0],
    };
  }

  if (effect === 'pan_right') {
    const startScale = u3 > 0.5 ? 1.028 : Number((1.028 + panZoomDelta).toFixed(4));
    const endScale = u3 > 0.5 ? Number((1.028 + panZoomDelta).toFixed(4)) : 1.028;
    return {
      scaleStart: startScale,
      scaleEnd: endScale,
      txStart: Number((-panSpan * 0.5).toFixed(4)),
      txEnd: Number((panSpan * 0.5).toFixed(4)),
      tyStart: Number((driftY * 0.6).toFixed(4)),
      tyEnd: Number((-driftY * 0.6).toFixed(4)),
      bezier: [c1x, 0.0, c2x, 1.0],
    };
  }

  // Default: zoom_in / punch_in coupled with diagonal 2D drift
  return {
    scaleStart: 1.0,
    scaleEnd: Number((1.0 + zoomDelta).toFixed(4)),
    txStart: Number((-driftX * 0.5).toFixed(4)),
    txEnd: driftX,
    tyStart: Number((-driftY * 0.5).toFixed(4)),
    tyEnd: driftY,
    bezier: [c1x, 0.0, c2x, 1.0],
  };
}

export const BASE_OVERSCAN = 1.045;

export function overscanScale(scale) {
  return Math.max(1, scale) * BASE_OVERSCAN;
}
