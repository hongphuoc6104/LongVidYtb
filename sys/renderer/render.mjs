import {bundle} from '@remotion/bundler';
import {openBrowser, selectComposition, renderMedia, renderStill} from '@remotion/renderer';
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import os, {cpus} from 'node:os';
import {fileURLToPath} from 'node:url';
import {outputPlans, renderConcurrency, runParallelPool} from './outputs.mjs';
import {captionStyle, captionMaxHeight} from './captions.mjs';
import {generateSrt} from './srt.mjs';

if (!process.argv[2] || process.argv[2] === '--help' || process.argv[2] === '-h') {
  console.log('Usage: node sys/renderer/render.mjs <work_dir>');
  console.log('Strict I/O contract: renders video.mp4, subtitles.srt, layout.json, stills & thumbnails');
  process.exit(process.argv[2] ? 0 : 1);
}

const dir = path.resolve(process.argv[2]);
const propsPath = path.join(dir, 'props.json');
if (!fs.existsSync(propsPath)) {
  console.error(`Error: props.json not found in ${dir}`);
  process.exit(1);
}

const props = JSON.parse(fs.readFileSync(propsPath, 'utf8'));
const publicDir = path.join(dir, 'public');
if (!fs.existsSync(publicDir)) {
  fs.mkdirSync(publicDir, {recursive: true});
}

// Generate native subtitles.srt directly from props.cues if available
const srtCues = props.cues || props.tracks?.[props.primary_language || 'vi']?.cues;
if (Array.isArray(srtCues)) {
  const srtContent = generateSrt(srtCues);
  fs.writeFileSync(path.join(dir, 'subtitles.srt'), srtContent, 'utf8');
}

const plans = outputPlans(props, fs.existsSync(path.join(publicDir, 'narration_en.wav')));
const url = await bundle({
  entryPoint: fileURLToPath(new URL('./index.tsx', import.meta.url)),
  publicDir: path.join(dir, 'public')
});
function resolveChromePath() {
  if (process.env.VP_CHROME_PATH && fs.existsSync(process.env.VP_CHROME_PATH)) {
    return process.env.VP_CHROME_PATH;
  }
  try {
    const pwPath = chromium.executablePath();
    if (fs.existsSync(pwPath)) return pwPath;
  } catch {}
  for (const p of ['/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser']) {
    if (fs.existsSync(p)) return p;
  }
  return chromium.executablePath();
}

const hasNvidiaEgl = fs.existsSync('/usr/lib64-nvidia/libEGL_nvidia.so.0');
if (hasNvidiaEgl) {
  try {
    const vendorDir = '/usr/share/glvnd/egl_vendor.d';
    fs.mkdirSync(vendorDir, {recursive: true});
    const nvidiaIcd = path.join(vendorDir, '10_nvidia.json');
    if (!fs.existsSync(nvidiaIcd)) {
      fs.writeFileSync(nvidiaIcd, JSON.stringify({
        file_format_version: '1.0.0',
        ICD: {library_path: '/usr/lib64-nvidia/libEGL_nvidia.so.0'}
      }, null, 2));
    }
    process.env.LD_LIBRARY_PATH = `/usr/lib64-nvidia:${process.env.LD_LIBRARY_PATH || ''}`;
  } catch {}
}

function wrapChromeExecutable(rawPath) {
  if (rawPath.endsWith('-wrapper.sh')) return rawPath;
  const wrapperDir = path.join(os.tmpdir(), 'vp-chrome');
  fs.mkdirSync(wrapperDir, {recursive: true});
  const wrapper = path.join(wrapperDir, `chrome-wrapper-${process.pid}.sh`);
  const content = `#!/usr/bin/env bash
if [ -f "/usr/lib64-nvidia/libEGL_nvidia.so.0" ]; then
  export LD_LIBRARY_PATH="/usr/lib64-nvidia:\${LD_LIBRARY_PATH}"
  exec "${rawPath}" \\
    --no-sandbox \\
    --disable-dev-shm-usage \\
    --use-gl=angle \\
    --use-angle=gl-egl \\
    --enable-gpu \\
    --enable-gpu-rasterization \\
    --enable-zero-copy \\
    --ignore-gpu-blocklist \\
    --run-all-compositor-stages-before-draw \\
    --disable-checker-imaging \\
    --disable-new-content-rendering-timeout \\
    "$@"
else
  exec "${rawPath}" \\
    --no-sandbox \\
    --disable-dev-shm-usage \\
    --run-all-compositor-stages-before-draw \\
    --disable-checker-imaging \\
    --disable-new-content-rendering-timeout \\
    --disable-gpu-rasterization \\
    --enable-gpu \\
    --ignore-gpu-blocklist \\
    "$@"
fi
`;
  fs.writeFileSync(wrapper, content, {mode: 0o755});
  return wrapper;
}

const rawChromePath = resolveChromePath();
const chromePath = wrapChromeExecutable(rawChromePath);

process.on('exit', () => {
  try {
    if (fs.existsSync(chromePath) && chromePath.includes('chrome-wrapper-')) {
      fs.unlinkSync(chromePath);
    }
  } catch {}
});

process.env.DISABLE_FROM_SURFACE = 'true';

const effectiveConcurrency = renderConcurrency(props.render_concurrency, cpus().length, hasNvidiaEgl);

// Step 1: Run Batch DOM Caption Safety Check and close Playwright BEFORE opening Remotion browser
const captionPlans = plans.filter(plan => !plan.props.hideSubtitles);
let failures = [];
let checked = 0;
if (captionPlans.length) {
  const pw = await chromium.launch({executablePath: chromePath, headless: true});
  try {
    for (const plan of captionPlans) {
      const checkWidth = plan.props.width;
      const checkHeight = plan.props.height;
      const page = await pw.newPage({viewport: {width: checkWidth, height: checkHeight}});
      try {
        await page.setContent('<div id="subtitle"></div>');
        const style = captionStyle(checkWidth, checkHeight);
        const maxHeight = captionMaxHeight(checkWidth, checkHeight);
        const cues = Array.isArray(plan.props.cues) ? plan.props.cues : [];
        const res = await page.evaluate(({cuesList, styleObj, w, h, maxH, file, language}) => {
          const e = document.querySelector('#subtitle');
          for (const [key, value] of Object.entries(styleObj)) {
            e.style[key] = typeof value === 'number' && !['fontWeight', 'lineHeight', 'zIndex'].includes(key) ? `${value}px` : String(value);
          }
          const badList = [];
          for (const cue of cuesList) {
            e.textContent = cue.text;
            const r = e.getBoundingClientRect();
            const isOverflow = r.left < 0 || r.right > w || r.top < 0 || r.bottom > h || r.height > maxH || e.scrollWidth > e.clientWidth;
            if (isOverflow) {
              badList.push({file, language, text: cue.text, errors: ['subtitle']});
            }
          }
          return {checkedCount: cuesList.length, badList};
        }, {cuesList: cues, styleObj: style, w: checkWidth, h: checkHeight, maxH: maxHeight, file: plan.file, language: plan.props.language});
        checked += res.checkedCount;
        if (res.badList.length) failures.push(...res.badList);
      } finally {
        await page.close();
      }
    }
  } finally {
    await pw.close();
  }
}

const layoutResult = {
  passed: !failures.length,
  applies: captionPlans.length > 0,
  checked_cues: checked,
  concurrency: effectiveConcurrency,
  execution_mode: 'multi_threaded_batch',
  method: 'actual requested language/aspect caption styles; two lines; no quality approval',
  failures
};

fs.writeFileSync(path.join(dir, 'layout.json'), JSON.stringify(layoutResult, null, 2));

if (layoutResult.failures.length) throw Error('Text overflow');

// Step 2: Open Remotion browser after Playwright has cleanly exited
const browser = await openBrowser('chrome', {
  browserExecutable: chromePath,
  chromiumOptions: {
    ...(hasNvidiaEgl ? {gl: 'angle-egl'} : {}),
    args: [
      '--no-sandbox',
      '--disable-dev-shm-usage',
      '--run-all-compositor-stages-before-draw',
      '--disable-checker-imaging',
      '--disable-new-content-rendering-timeout',
      ...(hasNvidiaEgl ? [
        '--use-gl=angle',
        '--use-angle=gl-egl',
        '--enable-gpu-rasterization',
        '--enable-zero-copy'
      ] : [
        '--disable-gpu-rasterization'
      ]),
      '--enable-gpu',
      '--ignore-gpu-blocklist'
    ]
  }
});

try {
  // Render representative stills on the shared browser instance
  const compStills = await selectComposition({
    serveUrl: url,
    id: 'Pilot',
    inputProps: plans[0].props,
    puppeteerInstance: browser
  });

  const stillsFps = compStills.fps || 30;
  for (const scene of plans[0].props.scenes) {
    let targetFrame = 0;
    if (scene.start !== undefined && scene.end !== undefined) {
      targetFrame = Math.round(((scene.start + scene.end) / 2) * stillsFps);
    } else if (scene.startFrame !== undefined) {
      const dur = scene.durationInFrames ?? (scene.endFrame !== undefined ? scene.endFrame - scene.startFrame : 0);
      targetFrame = Math.round(scene.startFrame + dur / 2);
    } else if (scene.start !== undefined) {
      targetFrame = Math.round(scene.start * stillsFps);
    }
    targetFrame = Math.max(0, Math.min(compStills.durationInFrames - 1, targetFrame));

    await renderStill({
      serveUrl: url,
      composition: compStills,
      inputProps: plans[0].props,
      puppeteerInstance: browser,
      frame: targetFrame,
      output: path.join(dir, scene.id + '.png')
    });
  }

  // Render thumbnail and cover stills if thumbnail_spec is provided
  if (props.thumbnail_spec) {
    const spec = props.thumbnail_spec;
    const thumbText = spec.title || spec.text_overlay || spec.text || '';
    const thumbBadge = spec.badge || '';
    const thumbImage = spec.image || plans[0]?.props?.scenes?.[0]?.image || plans[0]?.props?.scenes?.[0]?.images?.[0]?.src || '';

    if (props.omni_platform && spec.text_overlay) {
      const text = spec.text_overlay;
      if (text !== text.toUpperCase() || text.trim().split(/\s+/u).length < 2 || text.trim().split(/\s+/u).length > 4) {
        throw Error('Invalid thumbnail text: 2–4 uppercase words required');
      }
    }

    const ratio = props.aspect_ratio || '9:16';
    const targets = [];
    if (ratio === '16:9' || ratio === 'dual' || props.omni_platform) {
      targets.push([1920, 1080, 'thumbnail_youtube_16x9.png']);
    }
    if (ratio === '9:16' || ratio === 'dual' || props.omni_platform) {
      targets.push([1080, 1920, 'cover_tiktok_reels_9x16.png']);
    }

    for (const [width, height, file] of targets) {
      const inputProps = {
        width,
        height,
        text: thumbText,
        title: spec.title || thumbText,
        badge: thumbBadge,
        image: thumbImage
      };
      const composition = await selectComposition({
        serveUrl: url,
        id: 'Thumbnail',
        inputProps,
        puppeteerInstance: browser
      });
      await renderStill({
        serveUrl: url,
        composition,
        inputProps,
        puppeteerInstance: browser,
        frame: 0,
        output: path.join(dir, file)
      });
    }
  }

  for (const plan of plans) {
    const composition = await selectComposition({serveUrl: url, id: 'Pilot', inputProps: plan.props, puppeteerInstance: browser});
    await renderMedia({
      serveUrl: url,
      composition,
      inputProps: plan.props,
      puppeteerInstance: browser,
      codec: 'h264',
      hardwareAcceleration: 'if-possible',
      videoBitrate: '6M',
      audioCodec: 'aac',
      concurrency: Math.min(effectiveConcurrency, Math.max(1, cpus().length)),
      outputLocation: path.join(dir, plan.file),
      onProgress: ({renderedFrames}) => {
        if (renderedFrames % 150 === 0) {
          console.log(`Render progress: ${renderedFrames}/${composition.durationInFrames} frames`);
        }
      }
    });
  }
  if (plans[0].file !== 'video.mp4') fs.copyFileSync(path.join(dir, plans[0].file), path.join(dir, 'video.mp4'));

  const ratio = props.aspect_ratio || '9:16';
  if (ratio === '16:9' && !fs.existsSync(path.join(dir, 'video_16x9.mp4')) && fs.existsSync(path.join(dir, 'video.mp4'))) {
    fs.copyFileSync(path.join(dir, 'video.mp4'), path.join(dir, 'video_16x9.mp4'));
  }
  if (ratio === '9:16' && !fs.existsSync(path.join(dir, 'video_9x16.mp4')) && fs.existsSync(path.join(dir, 'video.mp4'))) {
    fs.copyFileSync(path.join(dir, 'video.mp4'), path.join(dir, 'video_9x16.mp4'));
  }

} finally {
  await browser.close({silent: true});
}
