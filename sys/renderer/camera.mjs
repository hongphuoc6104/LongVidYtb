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

export function cameraVariation(sceneId, beatIndex) {
  const id = String(sceneId || 'SC01');
  const idx = Math.max(0, Number(beatIndex) || 0);
  const r1 = hash01(`${id}:${idx}:zoom`);
  const r2 = hash01(`${id}:${idx}:pan`);
  const r3 = hash01(`${id}:${idx}:ease`);
  const r4 = hash01(`${id}:${idx}:dir`);

  // zoomAmp: 0.04 .. 0.09 (4% to 9% organic zoom)
  const zoomAmp = 0.04 + r1 * 0.05;

  // panAmp: 1.5 .. 3.5 (% of frame translation)
  const panAmp = 1.5 + r2 * 2.0;

  // Symmetric & organic easing bezier control points
  const EASING_CURVES = [
    [0.42, 0.0, 0.58, 1.0],   // Gentle symmetric ease-in-out
    [0.37, 0.0, 0.63, 1.0],   // Crisper cinematic ease-in-out
    [0.45, 0.05, 0.55, 0.95], // Cushioned settle
    [0.25, 0.1, 0.25, 1.0],   // Gradual cinematic decelerate
  ];
  const easing = EASING_CURVES[Math.floor(r3 * EASING_CURVES.length)];

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
  const explicit = beat?.camera_motion || beat?.effect;
  if (explicit && !['auto', 'cut', 'fade'].includes(explicit)) return explicit;
  const intent = String(beat?.camera_intent || scene?.camera_intent || scene?.camera || '').toLowerCase();
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

