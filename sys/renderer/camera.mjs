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
      const isCrop = Boolean(beat.focus?.scale && Number(beat.focus.scale) > 1.0);
      const wasCrop = Boolean(previous?.focus?.scale && Number(previous.focus.scale) > 1.0);
      const continues = previous && (beat.shot_type === 'variation' || (beat.src && beat.src === previous.src)) && (!isCrop && !wasCrop);
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
      const isCrop = Boolean(anchor.focus?.scale && Number(anchor.focus.scale) > 1.0);
      let cropScale = isCrop ? Math.min(1.6, Math.max(1.0, Number(anchor.focus.scale))) : null;
      // Unknown legacy effects and lateral sweeps are steady in calm playback.
      // Keep the semantic selector available for authoring and contract checks.
      const explicit = anchor.camera_motion || anchor.effect || (typeof anchor.camera === 'object' ? anchor.camera?.motion : undefined);
      const hasIntent = (explicit && !['auto', 'cut', 'fade', 'draw_on', 'line_boil'].includes(explicit)) ||
        anchor.camera_intent || scene.camera_intent || scene.camera;
      const requested = hasIntent ? selectSemanticCameraEffect(anchor, scene, group.first) : 'hold';
      const inward = ['zoom_in', 'push_in', 'punch_in', 'drift_diag_in'].includes(requested);
      const outward = ['zoom_out', 'pull_back', 'drift_diag_out'].includes(requested);
      const locked = isCrop || beats.slice(group.first, group.last + 1).some((beat) =>
        ['hold', 'static'].includes(beat.camera_motion || beat.effect) ||
        Boolean(beat.emphasis_text) ||
        Boolean(beat.is_endcard) ||
        ['white_card', 'white_isolated', 'macro_prop'].includes(beat.shot_type));
      const absoluteStart = Number(scene.start || 0) + start;
      const moving = !locked && (inward || outward) && duration >= CALM_MIN_MOTION_SECONDS && absoluteStart >= nextMotionAt;
      // smoothstep's peak derivative is 1.5. Include overscan in the speed budget.
      let amplitude = moving ? Math.min(CALM_MAX_ZOOM, CALM_MAX_ZOOM_PER_SEC * duration / (1.5 * BASE_OVERSCAN)) : 0;
      let focusX = 50;
      let focusY = 42;
      if (cropScale) {
        let effectiveCropScale = cropScale;
        let rawX = anchor.focus?.x ?? 0.5;
        let rawY = anchor.focus?.y ?? 0.42;

        const hasLettering = Boolean(
          anchor.emphasis_text ||
          anchor.lettering_bbox ||
          (anchor.visible_text && anchor.visible_text.length)
        );
        const letteringYMax = anchor.lettering_bbox ? anchor.lettering_bbox[3] : 0.14;

        // 1. Lettering safety: must fully CONTAIN or fully EXCLUDE (zero partial cut)
        if (hasLettering) {
          let S = effectiveCropScale * BASE_OVERSCAN;
          let invS = 1.0 / S;
          let vy1 = rawY * (1.0 - invS);

          // Partial overlap check: if top edge cuts into lettering [0, letteringYMax]
          if (vy1 < letteringYMax + 0.015) {
            // Attempt 1: Adjust crop downwards to safely EXCLUDE lettering
            const neededY = (letteringYMax + 0.015) / Math.max(0.01, 1.0 - invS);
            if (neededY <= 0.85) {
              rawY = Math.max(rawY, neededY);
            } else if (effectiveCropScale <= 1.25) {
              // Attempt 2: Contain lettering if zoom is modest
              effectiveCropScale = Math.min(1.15, effectiveCropScale);
              S = effectiveCropScale * BASE_OVERSCAN;
              rawX = 0.5;
              rawY = 0.5 / S;
            } else {
              // Attempt 3: Degrade gracefully to full image with push-in
              effectiveCropScale = null;
            }
          }
        }

        // 2. Primary-subject head safety: never partially intersect head bbox
        if (effectiveCropScale) {
          const hasChar = ['full_scene', 'variation', 'character'].includes(anchor.shot_type) || Boolean(anchor.head_bbox);
          if (hasChar) {
            let hx1 = 0.32, hy1 = 0.18, hx2 = 0.68, hy2 = 0.45;
            if (anchor.head_bbox && Array.isArray(anchor.head_bbox) && anchor.head_bbox.length === 4) {
              [hx1, hy1, hx2, hy2] = anchor.head_bbox;
            } else if (rawX > 0.60) {
              hx1 = 0.55; hx2 = 0.95;
            } else if (rawX < 0.40) {
              hx1 = 0.05; hx2 = 0.45;
            }

            const S = effectiveCropScale * BASE_OVERSCAN;
            const invS = 1.0 / S;
            const vx1 = rawX * (1.0 - invS);
            const vx2 = rawX + (1.0 - rawX) * invS;
            const vy1 = rawY * (1.0 - invS);
            const vy2 = rawY + (1.0 - rawY) * invS;

            const interX = Math.max(vx1, hx1) < Math.min(vx2, hx2);
            const interY = Math.max(vy1, hy1) < Math.min(vy2, hy2);
            const contains = (vx1 <= hx1 + 1e-4) && (vy1 <= hy1 + 1e-4) && (vx2 >= hx2 - 1e-4) && (vy2 >= hy2 - 1e-4);

            if (interX && interY && !contains) {
              // Partial intersection cuts character head! Fall back to centered, less-zoomed crop
              rawX = 0.5;
              effectiveCropScale = Math.min(1.15, effectiveCropScale);
              const testS = effectiveCropScale * BASE_OVERSCAN;
              const testInvS = 1.0 / testS;
              const testVx1 = rawX * (1.0 - testInvS);
              const testVx2 = rawX + (1.0 - rawX) * testInvS;
              const testVy1 = rawY * (1.0 - testInvS);
              const testVy2 = rawY + (1.0 - rawY) * testInvS;
              const testInterX = Math.max(testVx1, hx1) < Math.min(testVx2, hx2);
              const testInterY = Math.max(testVy1, hy1) < Math.min(testVy2, hy2);
              const testContains = (testVx1 <= hx1 + 1e-4) && (testVy1 <= hy1 + 1e-4) && (testVx2 >= hx2 - 1e-4) && (testVy2 >= hy2 - 1e-4);

              if (testInterX && testInterY && !testContains) {
                // If still slicing head, degrade gracefully to full image
                effectiveCropScale = null;
              }
            }
          }
        }

        if (effectiveCropScale) {
          const S = effectiveCropScale * BASE_OVERSCAN;
          const halfSpan = 0.5 / S;
          const minCenter = halfSpan;
          const maxCenter = Math.max(minCenter, 1.0 - halfSpan);
          focusX = Math.min(maxCenter, Math.max(minCenter, rawX)) * 100;
          focusY = Math.min(maxCenter, Math.max(minCenter, rawY)) * 100;
          cropScale = effectiveCropScale;
        } else {
          // Graceful degradation: full image with push-in
          cropScale = null;
          focusX = 50;
          focusY = 42;
        }
      } else {
        const hasLettering = Boolean(
          anchor.emphasis_text ||
          anchor.lettering_bbox ||
          (anchor.visible_text && anchor.visible_text.length) ||
          beats.slice(group.first, group.last + 1).some((b) => Boolean(b.emphasis_text))
        );
        let rawX = anchor.focus?.x ?? 0.5;
        let rawY = anchor.focus?.y ?? 0.42;

        if (hasLettering) {
          // Rule: Lettering must be fully contained without clipping the top or side edges.
          // Anchor focusY to top (0%) so vy1 = 0 and lettering top is never cropped by BASE_OVERSCAN.
          // Move pivot toward lettering and cap zoom amplitude so edges stay within frame.
          focusY = 0;
          if (anchor.lettering_bbox && Array.isArray(anchor.lettering_bbox) && anchor.lettering_bbox.length === 4) {
            const [lx1, , lx2] = anchor.lettering_bbox;
            if (lx2 > 0.95 && lx1 > 0.04) {
              focusX = 55;
            } else if (lx1 < 0.05 && lx2 < 0.96) {
              focusX = 45;
            } else {
              focusX = 50;
            }
          } else {
            focusX = (rawX >= 0.55) ? 55 : (rawX <= 0.45 ? 45 : 50);
          }
          amplitude = Math.min(amplitude, 0.005);
        } else {
          focusX = Math.min(65, Math.max(35, rawX * 100));
          focusY = Math.min(58, Math.max(35, rawY * 100));
        }
      }
      const camera = {
        start, end, amplitude, outward: outward && moving, shotType: anchor.shot_type,
        cropScale,
        focusX,
        focusY,
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
  if (camera.cropScale) {
    return {
      scale: camera.cropScale * BASE_OVERSCAN,
      focusX: camera.focusX,
      focusY: camera.focusY,
    };
  }
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

