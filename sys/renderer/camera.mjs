// Semantic camera movement selector (eliminates mechanical active % 4 cycling)
export function selectSemanticCameraEffect(beat, scene, beatIndex) {
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

  // Non-repeating golden-ratio sequence seeded by scene ID + beatIndex so no two adjacent shots repeat
  const sceneSeed = String(scene?.id || 'SC01').split('').reduce((acc, ch) => acc + ch.charCodeAt(0), 0);
  const pool = ['zoom_in', 'pan_right', 'zoom_out', 'pan_left'];
  const prevIdx = beatIndex > 0 ? ((sceneSeed + (beatIndex - 1) * 3) % pool.length) : -1;
  let chosenIdx = (sceneSeed + beatIndex * 3) % pool.length;
  if (chosenIdx === prevIdx) {
    chosenIdx = (chosenIdx + 1) % pool.length;
  }
  return pool[chosenIdx];
}


export const BASE_OVERSCAN = 1.045;

export function overscanScale(scale) {
  return Math.max(1, scale) * BASE_OVERSCAN;
}
