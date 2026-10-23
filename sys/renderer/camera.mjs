// Semantic camera movement selector & organic non-repeating motion variations

export function hash01(str) {
  let h = 2166136261 >>> 0;
  const s = String(str);
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619) >>> 0;
  }
  return (h >>> 0) / 4294967296;
}

const MOTION_POOL = [
  'zoom_in',
  'pan_right',
  'zoom_out',
  'pan_left',
  'drift_diag_in',
  'pan_right',
  'drift_diag_out',
  'pan_left',
  'zoom_in',
  'zoom_out',
  'pan_down',
  'pan_up',
];

function isZoomInFamily(e) {
  return e === 'zoom_in' || e === 'drift_diag_in';
}

function isZoomOutFamily(e) {
  return e === 'zoom_out' || e === 'drift_diag_out';
}

function isVerticalFamily(e) {
  return e === 'pan_up' || e === 'pan_down';
}

export function resolveFallbackCameraSequence(sceneId, totalBeats = 24) {
  const id = String(sceneId || 'SC01');
  const sequence = [];
  for (let i = 0; i < totalBeats; i++) {
    const recent = sequence.slice(Math.max(0, sequence.length - 3));
    const lastEffect = sequence.length > 0 ? sequence[sequence.length - 1] : null;

    let candidates = MOTION_POOL.filter((eff) => {
      if (recent.includes(eff)) return false;
      if (lastEffect) {
        if (isZoomInFamily(lastEffect) && isZoomInFamily(eff)) return false;
        if (isZoomOutFamily(lastEffect) && isZoomOutFamily(eff)) return false;
        if (isVerticalFamily(lastEffect) && isVerticalFamily(eff)) return false;
      }
      return true;
    });

    if (candidates.length === 0) {
      candidates = MOTION_POOL.filter((eff) => eff !== lastEffect);
    }
    if (candidates.length === 0) candidates = MOTION_POOL;

    const roll = hash01(`${id}:cam_seq:${i}`);
    const chosenIdx = Math.floor(roll * candidates.length);
    sequence.push(candidates[chosenIdx]);
  }
  return sequence;
}

// Max camera speeds. Short beats (0.8-3.8s) with fixed amplitudes produced
// 3-10x faster motion than long beats, perceived as constant jumping.
export const MAX_ZOOM_PER_SEC = 0.02; // 2% scale per second
export const MAX_PAN_PER_SEC = 0.8; // 0.8% of frame per second (~15px/s at 1080p)

export function cameraVariation(sceneId, beatIndex, beatDuration = Infinity) {
  const id = String(sceneId || 'SC01');
  const idx = Math.max(0, Number(beatIndex) || 0);
  const dur = Math.max(0.1, Number(beatDuration) || Infinity);
  const r1 = hash01(`${id}:${idx}:zoom`);
  const r2 = hash01(`${id}:${idx}:pan`);
  const r4 = hash01(`${id}:${idx}:dir`);

  // zoomAmp: 0.03 .. 0.05, velocity-capped by beat duration
  const zoomAmp = Math.min(0.03 + r1 * 0.02, MAX_ZOOM_PER_SEC * dur);

  // panAmp: 1.0 .. 2.0 (% of frame), velocity-capped by beat duration
  const panAmp = Math.min(1.0 + r2 * 1.0, MAX_PAN_PER_SEC * dur);

  // Linear (constant velocity): ease-in-out on sub-4s beats doubles peak speed
  // and creates an accelerate/stop pump at every cut.
  const easing = [0.0, 0.0, 1.0, 1.0];

  // dirSign: -1 or 1 for subtle diagonal axis flip
  const dirSign = r4 < 0.5 ? -1 : 1;

  return {
    zoomAmp,
    panAmp,
    easing,
    dirSign,
  };
}

export function selectSemanticCameraEffect(beat, scene, beatIndex = 0) {
  const explicit = beat?.camera_motion || beat?.effect || (typeof beat?.camera === 'object' ? beat?.camera?.motion : undefined);
  if (explicit && !['auto', 'cut', 'fade'].includes(explicit)) return explicit;
  const cameraVal = typeof scene?.camera === 'object' ? (scene?.camera?.motion || '') : (scene?.camera || '');
  const intent = String(beat?.camera_intent || scene?.camera_intent || cameraVal || '').toLowerCase();
  const desc = String(beat?.description || scene?.action || scene?.purpose || '').toLowerCase();

  if (intent.includes('hold') || desc.includes('diagram') || desc.includes('sơ đồ')) return 'hold';
  if (intent.includes('reveal') || intent.includes('shock') || desc.includes('bất ngờ') || desc.includes('giật mình')) return 'punch_in';
  if (intent.includes('establish') || intent.includes('wide') || desc.includes('toàn cảnh') || desc.includes('rộng')) return 'zoom_out';
  if (intent.includes('detail') || intent.includes('focus') || intent.includes('tension') || desc.includes('cận cảnh') || desc.includes('tập trung')) return 'zoom_in';
  if (intent.includes('pan_left') || intent.includes('contrast') || desc.includes('đối lập')) return 'pan_left';
  if (intent.includes('pan_right') || desc.includes('dòng thời gian') || desc.includes('hành trình')) return 'pan_right';

  const sceneId = String(scene?.id || 'SC01');
  const idx = Math.max(0, Number(beatIndex) || 0);
  const seq = resolveFallbackCameraSequence(sceneId, idx + 1);
  return seq[idx];
}

export const BASE_OVERSCAN = 1.045;

export function overscanScale(scale) {
  return Math.max(1, scale) * BASE_OVERSCAN;
}

// Playback comfort is independent of authored camera-intent diversity. A fast
// image edit is not an instruction to restart the camera or change its axis.
export const CALM_MIN_MOTION_SECONDS = 2.4;
export const CALM_MAX_ZOOM = 0.015;
export const CALM_MAX_ZOOM_PER_SEC = 0.004;
export const CALM_REST_SECONDS = 4;

/** @param {object[]} scenes @returns {object[][]} Per-beat, scene-relative camera groups. */
export function buildCalmCameraPlan(scenes) {
  let nextMotionAt = -Infinity;
  return scenes.map((scene) => {
    const beats = scene.images?.length ? scene.images : [{src: scene.image, at: 0}];
    const groups = [];
    for (let i = 0; i < beats.length; i++) {
      const beat = beats[i];
      const previous = beats[i - 1];
      const continues = previous && (beat.shot_type === 'variation' || (beat.src && beat.src === previous.src));
      if (continues) {
        groups[groups.length - 1].last = i;
      } else {
        groups.push({first: i, last: i});
      }
    }

    const plan = [];
    for (const group of groups) {
      const anchor = beats[group.first];
      const start = Number(anchor.at) || 0;
      const end = Number(beats[group.last + 1]?.at ?? (scene.end - scene.start));
      const duration = Math.max(0, end - start);
      // Unknown legacy effects and lateral sweeps are steady in calm playback.
      // Keep the semantic selector available for authoring and contract checks.
      const explicit = anchor.camera_motion || anchor.effect || (typeof anchor.camera === 'object' ? anchor.camera?.motion : undefined);
      const hasIntent = (explicit && !['auto', 'cut', 'fade', 'draw_on', 'line_boil'].includes(explicit)) ||
        anchor.camera_intent || scene.camera_intent || scene.camera;
      const requested = hasIntent ? selectSemanticCameraEffect(anchor, scene, group.first) : 'hold';
      const inward = ['zoom_in', 'push_in', 'punch_in', 'drift_diag_in'].includes(requested);
      const outward = ['zoom_out', 'pull_back', 'drift_diag_out'].includes(requested);
      const locked = beats.slice(group.first, group.last + 1).some((beat) =>
        ['hold', 'static'].includes(beat.camera_motion || beat.effect) ||
        ['white_card', 'white_isolated', 'macro_prop'].includes(beat.shot_type));
      const absoluteStart = Number(scene.start || 0) + start;
      const moving = !locked && (inward || outward) && duration >= CALM_MIN_MOTION_SECONDS && absoluteStart >= nextMotionAt;
      // smoothstep's peak derivative is 1.5. Include overscan in the speed budget.
      const amplitude = moving ? Math.min(CALM_MAX_ZOOM, CALM_MAX_ZOOM_PER_SEC * duration / (1.5 * BASE_OVERSCAN)) : 0;
      const camera = {
        start, end, amplitude, outward: outward && moving, shotType: anchor.shot_type,
        focusX: Math.min(65, Math.max(35, (anchor.focus?.x ?? 0.5) * 100)),
        focusY: Math.min(58, Math.max(35, (anchor.focus?.y ?? 0.42) * 100)),
      };
      if (moving) nextMotionAt = Number(scene.start || 0) + end + CALM_REST_SECONDS;
      for (let i = group.first; i <= group.last; i++) plan[i] = camera;
    }
    return plan;
  });
}

/** @param {object | undefined} camera @param {number} relative */
export function calmCameraFrame(camera, relative) {
  if (!camera) return {scale: BASE_OVERSCAN, focusX: 50, focusY: 42};
  const duration = camera.end - camera.start;
  const progress = duration > 0 ? Math.max(0, Math.min(1, (relative - camera.start) / duration)) : 0;
  const eased = progress * progress * (3 - 2 * progress);
  return {
    scale: overscanScale(1 + camera.amplitude * (camera.outward ? 1 - eased : eased)),
    focusX: camera.focusX,
    focusY: camera.focusY,
  };
}

/** @param {{scale: number, focusX: number, focusY: number}} camera @param {boolean} editorial */
export function calmCameraStyle(camera, editorial = false) {
  const scale = editorial ? 1 + (camera.scale / BASE_OVERSCAN - 1) * 0.65 : camera.scale;
  return {
    objectPosition: `${camera.focusX}% ${camera.focusY}%`,
    transformOrigin: `${camera.focusX}% ${camera.focusY}%`,
    transform: `translate3d(0, 0, 0) scale(${scale})`,
    willChange: 'transform',
    backfaceVisibility: 'hidden',
  };
}

