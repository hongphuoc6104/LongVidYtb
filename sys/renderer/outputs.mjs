/** One source of truth for language, timeline, multi-threading and output dimensions. */
export function renderConcurrency(requested, cores, hasGpuEgl = false) {
  const envVal = Number.parseInt(process.env.VP_RENDER_CONCURRENCY || '', 10);
  if (Number.isInteger(envVal) && envVal > 0) {
    return Math.min(envVal, 16);
  }
  const available = Number.isInteger(cores) && cores > 0 ? cores : 4;
  // On Colab T4 (typically 2 vCPUs + NVIDIA T4 16GB GPU) or when requested explicitly,
  // ensure multi-threaded execution is not bottlenecked to 2 vCPUs.
  const effectivePool = hasGpuEgl ? Math.max(available, 6) : Math.max(available, 4);
  if (Number.isInteger(requested) && requested > 0) {
    return Math.min(requested, Math.max(effectivePool, requested));
  }
  return Math.min(Math.max(4, effectivePool), 8);
}

export async function runParallelPool(items, concurrency, taskFn) {
  const list = Array.from(items || []);
  if (!list.length) return [];
  const workers = Math.max(1, Math.min(Number(concurrency) || 4, list.length));
  const results = new Array(list.length);
  let cursor = 0;
  async function worker() {
    while (cursor < list.length) {
      const idx = cursor++;
      results[idx] = await taskFn(list[idx], idx);
    }
  }
  await Promise.all(Array.from({length: workers}, () => worker()));
  return results;
}

function normalizeScenes(scenes, fps = 30) {
  if (!Array.isArray(scenes)) return scenes;
  return scenes.map((s) => {
    if (!s || typeof s !== 'object') return s;
    const scene = {...s};
    if (scene.start === undefined && scene.startFrame !== undefined) {
      scene.start = scene.startFrame / fps;
    }
    if (scene.end === undefined) {
      if (scene.durationInFrames !== undefined) {
        scene.end = (scene.start ?? 0) + scene.durationInFrames / fps;
      } else if (scene.endFrame !== undefined) {
        scene.end = scene.endFrame / fps;
      }
    }
    return scene;
  });
}

export function outputPlans(props, hasEnglish) {
  const ratio = props.aspect_ratio || '9:16';
  if (!['9:16', '16:9', 'dual'].includes(ratio)) throw Error('Unsupported output aspect ratio');
  const fps = props.fps || 30;

  if (props.outputs) {
    const expected = ratio === 'dual' ? ['9:16', '16:9'] : [ratio];
    if (!Array.isArray(props.outputs) || props.outputs.length !== expected.length) throw Error('Explicit output contract required');
    const plans = props.outputs.map((plan, i) => {
      if (plan.aspect_ratio !== expected[i] || !['vi', 'en'].includes(plan.language) || typeof plan.subtitles !== 'boolean') throw Error('Invalid output contract');
      let track = props.tracks?.[plan.language];
      if (!track && props.primary_language === plan.language) {
        track = {
          audioSrc: props.audioSrc || 'narration.wav',
          duration: props.duration || (props.durationInFrames ? props.durationInFrames / fps : 30),
          scenesByAspect: props.scenes_by_aspect || {[expected[0]]: props.scenes},
          cues: props.cues
        };
      }
      const rawScenes = track?.scenesByAspect?.[plan.aspect_ratio];
      if (!track?.audioSrc || !Number.isFinite(track.duration) || track.duration <= 0 || !Array.isArray(rawScenes) || !rawScenes.length) throw Error('Missing language track/timeline for requested aspect');
      if (plan.subtitles && !Array.isArray(track.cues)) throw Error('Missing captions for requested language');
      const vertical = plan.aspect_ratio === '9:16';
      const scenes = normalizeScenes(rawScenes, fps);
      return {
        file: ratio === 'dual' ? `video_${vertical ? '9x16' : '16x9'}.mp4` : 'video.mp4',
        props: {
          ...props,
          scenes,
          duration: track.duration,
          cues: track.cues || [],
          width: vertical ? 1080 : 1920,
          height: vertical ? 1920 : 1080,
          words: track.words || [],
          hideSubtitles: !plan.subtitles,
          audioSrc: track.audioSrc,
          language: plan.language
        }
      };
    });
    if (props.omni_platform) {
      const main = plans.find(plan => plan.props.width === 1920);
      if (!main) throw Error('Omni-platform requires a landscape master');
      plans.push({file: 'video_youtube_16x9.mp4', props: {...main.props, hideSubtitles: true}});
      plans.push({file: 'video_facebook_16x9.mp4', props: {...main.props, hideSubtitles: false}});
      for (const short of props.short_deliveries || []) plans.push({file: short.file, props: {...props, ...short.props, sfx_events: [{at: 0, src: 'pop_clean.wav'}]}});
    }
    return plans;
  }

  // Standalone mode without explicit outputs[]
  if (props.en_scenes && !hasEnglish) {
    throw Error('English track and timeline required');
  }
  const rawScenes16x9 = props.en_scenes || props.scenes_by_aspect?.['16:9'] || props.scenes;
  const duration16x9 = props.en_duration || props.duration || (props.durationInFrames ? props.durationInFrames / fps : 30);
  const audioSrc16x9 = (props.en_scenes && hasEnglish) ? 'narration_en.wav' : (props.audioSrc || 'narration.wav');

  const rawScenes9x16 = props.scenes_by_aspect?.['9:16'] || props.scenes;
  const duration9x16 = props.duration || (props.durationInFrames ? props.durationInFrames / fps : 30);
  const audioSrc9x16 = props.audioSrc || 'narration.wav';

  if (ratio === '16:9' && (!rawScenes16x9 || !rawScenes16x9.length)) {
    throw Error('Missing scenes for 16:9 aspect ratio');
  }
  if (ratio === '9:16' && (!rawScenes9x16 || !rawScenes9x16.length)) {
    throw Error('Missing scenes for 9:16 aspect ratio');
  }
  if (ratio === 'dual' && (!rawScenes9x16?.length || !rawScenes16x9?.length)) {
    throw Error('Scenes required for both aspects in dual mode');
  }

  const verticalScenes = normalizeScenes(rawScenes9x16, fps);
  const horizontalScenes = normalizeScenes(rawScenes16x9, fps);

  const vertical = {
    ...props,
    scenes: verticalScenes,
    duration: duration9x16,
    width: 1080,
    height: 1920,
    hideSubtitles: props.hideSubtitles ?? false,
    audioSrc: audioSrc9x16
  };
  const horizontal = {
    ...props,
    scenes: horizontalScenes,
    duration: duration16x9,
    width: 1920,
    height: 1080,
    hideSubtitles: props.hideSubtitles ?? true,
    audioSrc: audioSrc16x9
  };

  return ratio === 'dual'
    ? [{file: 'video_9x16.mp4', props: vertical}, {file: 'video_16x9.mp4', props: horizontal}]
    : [{file: 'video.mp4', props: ratio === '16:9' ? horizontal : vertical}];
}
