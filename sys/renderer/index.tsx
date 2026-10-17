import {selectSemanticCameraEffect, overscanScale, BASE_OVERSCAN} from './camera.mjs';
import {Thumbnail} from './thumbnail';
import React, {useLayoutEffect} from 'react';
import {karaokeTokens, captionStyle, captionMaxHeight} from './captions.mjs';
import {BRAND_LOGO_DATA_URI} from './brand_logo';
import {
  AbsoluteFill,
  Audio,
  Sequence,
  Composition,
  Easing,
  Img,
  Video as RemotionVideo,
  interpolate,
  registerRoot,
  spring,
  staticFile,
  useCurrentFrame
} from 'remotion';

// Multi-harmonic deterministic noise for organic handheld camera vibration
export function organicNoise(time: number, seed: number = 0): number {
  const o1 = Math.sin(time * 19.3 + seed * 1.7);
  const o2 = Math.sin(time * 38.7 + seed * 3.1) * 0.5;
  const o3 = Math.sin(time * 73.1 + seed * 5.9) * 0.25;
  return (o1 + o2 + o3) / 1.75;
}

// Deterministic line-boil pseudo-random jitter for hand-drawn stick figure vitality
export function boilJitter(frame: number, seed: number = 0): number {
  const step = Math.floor(frame / 4);
  const r = Math.sin(step * 12.9898 + seed * 78.233) * 43758.5453;
  return r - Math.floor(r) - 0.5;
}

export {selectSemanticCameraEffect} from './camera.mjs';

// Dynamic voice-guided BGM sidechain ducking envelope (swells in pauses, ducks during speech)
export function computeDynamicBgmVolume(
  t: number,
  cues: any[],
  baseVolume: number = 0.12,
  duckedVolume: number = 0.075,
  swellVolume: number = 0.19
): number {
  if (!Array.isArray(cues) || cues.length === 0) return baseVolume;
  const attack = 0.22;  // 220ms smooth duck before/into speech
  const release = 0.45; // 450ms warm swell into narrative pause
  let speechWeight = 0;
  for (const c of cues) {
    const start = Number(c.start ?? 0);
    const end = Number(c.end ?? 0);
    if (t >= start && t <= end) {
      speechWeight = 1;
      break;
    }
    if (t >= start - attack && t < start) {
      speechWeight = Math.max(speechWeight, (t - (start - attack)) / attack);
    } else if (t > end && t <= end + release) {
      speechWeight = Math.max(speechWeight, 1 - (t - end) / release);
    }
  }
  return swellVolume - speechWeight * (swellVolume - duckedVolume);
}

function renderHighlightedText(text: string, targetWord?: string, modern = false) {
  if (!text) return null;
  const cleanTarget = targetWord ? targetWord.toLowerCase().trim() : '';

  // Tách từ theo khoảng trắng và các dấu ngắt câu
  const parts = text.split(/(\s+|[.,!?:;"“”]+)/);
  return parts.map((part, i) => {
    const cleanPart = part.toLowerCase().replace(/[^a-z0-9-]/g, '');
    const isTarget = cleanTarget && cleanPart === cleanTarget;
    const isEnglishKeyword = !modern && /^[A-Z][a-zA-Z0-9-]*$/.test(part) && part.length > 1;

    if (isTarget || isEnglishKeyword) {
      return (
        <span
          key={i}
          style={{
            color: '#FACC15', // Vibrant Yellow highlight
            fontWeight: 900,
            textShadow: '0 0 16px rgba(250, 204, 21, 0.7), 0 2px 4px rgba(0, 0, 0, 0.95)',
            display: 'inline-block',
            letterSpacing: '0.02em',
          }}
        >
          {part}
        </span>
      );
    }
    return <span key={i}>{part}</span>;
  });
}

const DISABLE_SUBTITLES = false;

const Video: React.FC<any> = (p) => {
  const frame = useCurrentFrame();
  const fps = p.fps || 30;
  const t = frame / fps;
  const width = p.width || 1080;
  const height = p.height || 1920;
  const duration = p.duration || 30;

  useLayoutEffect(() => {
    for (const element of document.querySelectorAll<HTMLElement>('[data-check]')) {
      if (
        element.scrollWidth > element.clientWidth ||
        (element.dataset.check === 'subtitle' &&
          element.offsetHeight > captionMaxHeight(width, height))
      ) {
        throw new Error('Actual render text overflow: ' + element.textContent);
      }
    }
  }, [frame, width, height]);

  // Support J-Cut / L-Cut visual boundary offset (visual leads or lags audio cut slightly)
  const scene =
    p.scenes.find((s: any) => {
      const jlOffset = Number(s.j_l_cut_offset ?? (p.enable_jl_cut ? -0.18 : 0));
      return t >= Math.max(0, s.start + jlOffset) && t < s.end + jlOffset;
    }) ||
    p.scenes.find((s: any) => t >= s.start && t < s.end) ||
    p.scenes[p.scenes.length - 1] ||
    {start: 0, end: 1, image: '', title: ''};

  const cue = (p.cues || []).find((c: any) => t >= c.start && t < c.end);
  const imageList = scene.images || [{src: scene.image, at: 0, effect: 'auto'}];
  const relative = t - scene.start;

  let active = 0;
  for (let i = 0; i < imageList.length; i++) {
    if (relative >= imageList[i].at) active = i;
  }
  const beat = imageList[active] || {src: scene.image, at: 0, effect: 'auto'};
  const currentImageSrc = beat?.src || scene.image;
  const nextAt = imageList[active + 1]?.at ?? (scene.end - scene.start);
  const beatDuration = Math.max(0.001, nextAt - beat.at);
  const progress = Math.max(0, Math.min(1, (relative - beat.at) / beatDuration));
  const transition = Math.max(0, Math.min(1, (relative - beat.at) / Math.min(0.3, beatDuration / 2)));
  // Smooth 85ms flipbook micro-dissolve for in-place variation shots
  const isVariationCut = active > 0 && beat.shot_type === 'variation' && beat.effect !== 'slide_left';
  const variationCrossfade = isVariationCut
    ? Math.max(0, Math.min(1, (relative - beat.at) / Math.min(0.085, beatDuration / 3)))
    : 1;

  // Motion Engine with Spring Physics, Bezier Easing & Dynamic Motion Blur
  let scale = 1;
  let translateX = 0;
  let translateY = 0;
  let motionBlurX = 0;
  const effect = selectSemanticCameraEffect(beat, scene, active);

  // Asymmetric organic ease curve (fast eye-catch, gentle cinematic settle)
  const smoothProgress = interpolate(progress, [0, 1], [0, 1], {
    easing: Easing.bezier(0.33, 1, 0.68, 1.0)
  });

  if (effect === 'punch_in') {
    // Spring physics with snappy elasticity and gentle settle
    const punchFrame = Math.round((relative - beat.at) * fps);
    const punchSpring = spring({
      frame: Math.max(0, punchFrame),
      fps,
      config: { damping: 12, mass: 0.5, stiffness: 120 }
    });
    scale = interpolate(punchSpring, [0, 1], [1.22, 1.08]);
  } else if (effect === 'zoom_in') {
    scale = 1 + 0.08 * smoothProgress;
  } else if (effect === 'zoom_out') {
    scale = 1.08 - 0.08 * smoothProgress;
  } else if (effect === 'pan_left') {
    scale = 1.06;
    translateX = (0.5 - smoothProgress) * 3;
  } else if (effect === 'pan_right') {
    scale = 1.06;
    translateX = (smoothProgress - 0.5) * 3;
  } else if (effect === 'shake') {
    scale = 1.06; // Đệm phóng to 6% để triệt tiêu viền đen khi rung chấn màn hình (14px shake)
  } else if (effect === 'slide_left') {
    // Bezier deceleration curve for natural slide momentum
    const slideEase = interpolate(transition, [0, 1], [0, 1], {
      easing: Easing.bezier(0.16, 1, 0.3, 1)
    });
    translateX = (1 - slideEase) * 100;
    // Whip Pan: Optical directional motion blur peaks at the fastest motion point
    if (transition > 0 && transition < 1) {
      motionBlurX = Math.sin(transition * Math.PI) * 18;
    }
  } else if (!p.modern_style && effect !== 'hold') {
    // AUTO KEN BURNS (Chu kỳ chuyển động camera êm ái chống nhàm chán)
    const cycle = active % 4;
    if (cycle === 0) {
      scale = 1.0 + 0.06 * smoothProgress; // Smooth zoom in
    } else if (cycle === 1) {
      scale = 1.05;
      translateX = (smoothProgress - 0.5) * 2.5; // Smooth pan right
    } else if (cycle === 2) {
      scale = 1.06 - 0.06 * smoothProgress; // Smooth zoom out
    } else {
      scale = 1.05;
      translateX = (0.5 - smoothProgress) * 2.5; // Smooth pan left
    }
  }

  // Overscan applies after every motion branch; 4.5% zoom crops ~2.15% per edge.
  // This is a framing margin, not proof that a provider watermark is removed.
  scale = overscanScale(scale);

  // Organic Camera Shake + Subtle Handheld Micro-Breathing (GPU transform only, zero overlay clutter)
  let shakeX = 0;
  let shakeY = 0;
  let microRot = 0;
  if (effect === 'shake' || (effect === 'punch_in' && (relative - beat.at) < 0.28)) {
    const shakeTime = relative - beat.at;
    const decay = Math.max(0, 1 - shakeTime / 0.28);
    shakeX = organicNoise(shakeTime * 1.5, 1.2) * 14 * decay;
    shakeY = organicNoise(shakeTime * 1.5, 4.7) * 12 * decay;
  } else if (effect !== 'hold') {
    shakeX = organicNoise(t * 0.14, active + 1.1) * 3.2;
    shakeY = organicNoise(t * 0.14, active + 3.7) * 2.4;
    microRot = organicNoise(t * 0.11, active + 7.3) * 0.18;
  }

  const opacity = beat.effect === 'fade' ? transition : variationCrossfade;
  // Clamp focal center to safe central viewport so model coordinate guesses never zoom into blank corners
  const focusX = Math.min(65, Math.max(35, (beat.focus?.x ?? 0.5) * 100));
  const focusY = Math.min(58, Math.max(35, (beat.focus?.y ?? 0.42) * 100));
  const editorial = p.reframe_mode && height > width && !['macro_prop', 'white_card', 'white_isolated'].includes(beat.shot_type);
  const editorialScale = 1 + (scale / BASE_OVERSCAN - 1) * 0.65;
  const isVideoAsset = currentImageSrc && (currentImageSrc.endsWith('.mp4') || currentImageSrc.endsWith('.webm'));

  // Procedural Line Boiling (opt-in only for isolated assets; disabled on full-bleed 1080p)
  const isLineBoil = Boolean(beat.line_boil || beat.effect === 'line_boil' || p.line_boil);
  const boilFps = 10;
  const boilIndex = Math.floor((frame / fps) * boilFps) % 4;
  const lineBoilFilter = isLineBoil ? `url(#line-boil-${boilIndex})` : '';

  // Stroke Draw-on restricted to white_card shots when explicitly requested
  const isDrawOn = Boolean((beat.draw_on || beat.effect === 'draw_on') && beat.shot_type === 'white_card');
  const drawDuration = beat.draw_duration || 1.3;
  const drawProgress = isDrawOn ? Math.min(1, Math.max(0, (relative - beat.at) / drawDuration)) : 1;
  const drawEase = interpolate(drawProgress, [0, 1], [0, 1], {
    easing: Easing.bezier(0.2, 0.8, 0.35, 1.0)
  });

  const drawMask = isDrawOn && drawEase < 1
    ? `linear-gradient(135deg, rgba(0,0,0,1) 0%, rgba(0,0,0,1) ${drawEase * 105}%, rgba(0,0,0,0) ${drawEase * 105 + 12}%)`
    : undefined;

  const combinedFilter = [
    motionBlurX > 0.5 ? `blur(${motionBlurX.toFixed(1)}px)` : '',
    lineBoilFilter
  ].filter(Boolean).join(' ') || undefined;

  return (
    <AbsoluteFill style={{background: editorial ? '#0F172A' : p.modern_style ? '#F8FAFC' : '#090D16', fontFamily: 'Arial, sans-serif', color: 'white', width, height, overflow: 'hidden'}}>
      {/* Procedural Line Boiling SVG Displacement Filters */}
      <svg style={{position: 'absolute', width: 0, height: 0, pointerEvents: 'none'}}>
        <defs>
          {[0, 1, 2, 3].map((seedIndex) => (
            <filter
              id={`line-boil-${seedIndex}`}
              key={seedIndex}
              x="-5%"
              y="-5%"
              width="110%"
              height="110%"
            >
              <feTurbulence
                type="fractalNoise"
                baseFrequency="0.04"
                numOctaves={2}
                result="noise"
                seed={seedIndex * 37 + 13}
              />
              <feDisplacementMap
                in="SourceGraphic"
                in2="noise"
                scale={3}
                xChannelSelector="R"
                yChannelSelector="G"
              />
            </filter>
          ))}
        </defs>
      </svg>

      {/* Legacy renderer compatibility only; standard content validation rejects scene.layers. */}
      {scene.layers && scene.layers.length > 0 ? (
        <AbsoluteFill style={{zIndex: 5}}>
          {scene.layers.map((l: any, idx: number) => {
            const lStart = l.start ?? 0;
            const lEnd = l.end ?? (scene.end - scene.start);
            if (relative < lStart || relative > lEnd) return null;
            const tau = relative - lStart;
            const lf = Math.round(tau * fps);

            if (l.bg || l.kind === 'background') {
              const bgScale = 1.08 - (0.02 * relative) / Math.max(1, scene.end - scene.start);
              const flash =
                l.fx === 'bg_flash'
                  ? interpolate(tau, [0, 0.25], [0.25, 0], {extrapolateRight: 'clamp'})
                  : 0;
              return (
                <AbsoluteFill key={l.id || `bg-${idx}`} style={{zIndex: l.z ?? 1}}>
                  <Img
                    src={staticFile(l.src)}
                    decoding="sync"
                    style={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover',
                      transform: `scale(${bgScale}) translateX(${Math.sin(relative / 2) * 1}%)`,
                    }}
                  />
                  {flash > 0 && (
                    <AbsoluteFill style={{background: 'white', opacity: flash, pointerEvents: 'none'}} />
                  )}
                </AbsoluteFill>
              );
            }

            // Sticker layer with Spring physics, multi-harmonic organic breathing, and smooth motion
            let s = 1 + 0.014 * organicNoise(relative * 0.22, idx + 1.5);
            let dx = 0;
            let dy = 0;
            let rot = 0;

            const sp = spring({
              frame: lf,
              fps,
              config: {damping: 9, stiffness: 160, mass: 0.6}
            });

            if (['pop', 'pop_wobble', 'bounce'].includes(l.fx)) s *= sp;
            if (l.fx === 'pop_wobble') rot += 10 * Math.sin(9 * tau) * Math.exp(-2 * tau);
            if (l.fx === 'bounce') dy -= 90 * Math.abs(Math.sin(5 * tau)) * Math.exp(-1.6 * tau);
            if (l.fx === 'drop') {
              dy -= tau < 0.3 ? height * 0.6 * (1 - tau / 0.3) ** 2 : 40 * Math.exp(-8 * (tau - 0.3)) * Math.abs(Math.sin(20 * (tau - 0.3)));
            }
            if (l.fx === 'slide_left') dx -= tau < 0.35 ? width * (1 - tau / 0.35) ** 3 : 0;
            if (l.fx === 'spin_grow') {
              s = Math.min(1, 0.15 + tau / 0.5);
              rot = -2.2 * relative * 57.3;
            }
            if (l.exitFx === 'suck' && relative > lEnd - 0.45) {
              const k = (relative - (lEnd - 0.45)) / 0.45;
              s *= Math.max(0.02, 1 - k);
              dx -= k * ((l.x ?? 0.5) - 0.5) * width;
              rot += k * 360;
            }
            if (l.shakeAt !== undefined && relative >= l.shakeAt && relative <= l.shakeAt + 0.6) {
              dx += 18 * Math.sin(70 * (relative - l.shakeAt)) * Math.exp(-4 * (relative - l.shakeAt));
            }

            const layerWidth = (l.w ?? 0.5) * width;
            return (
              <div
                key={l.id || `stk-${idx}`}
                style={{
                  position: 'absolute',
                  zIndex: l.z ?? 5,
                  left: (l.x ?? 0.5) * width - layerWidth / 2 + dx,
                  top: (l.y ?? 0.5) * height + dy,
                  width: layerWidth,
                  transform: `translateY(-50%) scale(${s}) rotate(${rot}deg)`,
                  transformOrigin: '50% 50%',
                  pointerEvents: 'none',
                }}
              >
                <Img src={staticFile(l.src)} decoding="sync" style={{width: '100%', display: 'block'}} />
              </div>
            );
          })}
        </AbsoluteFill>
      ) : (
        <>
          {/* Background layer transition (supports fade, slide_left, and 85ms flipbook variation cross-dissolve) */}
          {active > 0 && ((['fade', 'slide_left'].includes(beat.effect) && transition < 1) || (isVariationCut && variationCrossfade < 1)) && (
            <Img
              src={staticFile(imageList[active - 1].src)}
              decoding="sync"
              style={{
                position: 'absolute',
                width: '100%',
                height: '100%',
                objectFit: editorial ? 'contain' : 'cover',
                objectPosition: `${focusX}% ${focusY}%`,
                ...(editorial ? {top: '25%', height: '48%', borderRadius: 24} : {}),
                transform: `translate(calc(${translateX}% + ${shakeX}px), calc(${translateY}% + ${shakeY}px)) scale(${editorial ? editorialScale : scale}) rotate(${microRot.toFixed(3)}deg)`,
                transformOrigin: `${focusX}% ${focusY}%`,
              }}
            />
          )}

          {/* Main Visual Layer: Image with Ken Burns + Handheld Micro-Motion or Video Clip */}
          {currentImageSrc && (
            isVideoAsset ? (
              <RemotionVideo
                src={staticFile(currentImageSrc)}
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'contain',
                  opacity
                }}
              />
            ) : (
              <Img
                src={staticFile(currentImageSrc)}
                decoding="sync"
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: editorial ? 'contain' : 'cover',
                  objectPosition: `${focusX}% ${focusY}%`,
                  ...(editorial ? {position: 'absolute', top: '25%', height: '48%', borderRadius: 24, boxShadow: '0 12px 32px #0008'} : {}),
                  transform: `translate(calc(${translateX}% + ${shakeX}px), calc(${translateY}% + ${shakeY}px)) scale(${editorial ? editorialScale : scale}) rotate(${microRot.toFixed(3)}deg)`,
                  transformOrigin: `${focusX}% ${focusY}%`,
                  opacity,
                  filter: combinedFilter,
                  WebkitMaskImage: drawMask,
                  maskImage: drawMask,
                }}
              />
            )
          )}
        </>
      )}

      {editorial && p.hook_title && <div style={{position: 'absolute', top: 230, left: 56, width: 820, fontSize: 58, fontWeight: 900, textAlign: 'center', color: '#FACC15'}}>{p.hook_title}</div>}
      {p.cover_text && t < (p.cover_duration || 0) && <Thumbnail image={scene.image} text={p.cover_text} width={width} height={height} />}

      {/* Interactive Practice Indicator: Đếm nhịp luyện nói tự động đồng bộ theo Cue */}
      {!p.modern_style && cue && (cue.practice || cue.text?.includes('Cùng nhắc lại nhé')) && (() => {
        const pDur = cue.end - cue.start;
        const pRel = t - cue.start;
        const pProgress = Math.max(0, Math.min(1, pRel / pDur));
        if (pProgress < 0.4) return null;
        const countProgress = (pProgress - 0.4) / 0.6;
        const countText = countProgress < 0.33 ? '3...' : countProgress < 0.66 ? '2...' : '1... 🎙️';
        return (
          <div
            style={{
              position: 'absolute',
              bottom: height >= width ? 510 : 180,
              left: '50%',
              transform: 'translateX(-50%)',
              background: 'rgba(15, 23, 42, 0.94)',
              border: '2px dashed #FACC15',
              borderRadius: 30,
              padding: '10px 24px',
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              zIndex: 25,
              boxShadow: '0 8px 24px rgba(250, 204, 21, 0.35)'
            }}
          >
            <span style={{fontSize: 32}}>🗣️</span>
            <span style={{fontSize: 26, fontWeight: 800, color: '#FACC15'}}>
              Luyện nói: {countText}
            </span>
          </div>
        );
      })()}

      {/* Cinematic Overlays: Vignette & Subtle Film Grain */}
      {!p.hide_overlays && (
        <>
          {/* 1. Vignette (Darkened edges to guide focus towards center) */}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              pointerEvents: 'none',
              background: p.modern_style
                ? 'radial-gradient(circle at 50% 45%, rgba(0,0,0,0) 65%, rgba(15,23,42,0.22) 100%)'
                : 'radial-gradient(circle at 50% 45%, rgba(0,0,0,0) 60%, rgba(0,0,0,0.42) 100%)',
              zIndex: 12
            }}
          />

          {/* 2. Film Grain texture via inline SVG Filter overlay (opt-in to avoid full-screen feTurbulence overhead) */}
          {p.enable_film_grain && (
            <div
              style={{
                position: 'absolute',
                inset: 0,
                pointerEvents: 'none',
                opacity: 0.035,
                mixBlendMode: 'overlay',
                backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
                zIndex: 13
              }}
            />
          )}
        </>
      )}

      {/* Subtitles (Phụ đề động bắt mắt) */}
      {!DISABLE_SUBTITLES && !p.hideSubtitles && cue && (() => {
        const lineText = cue.text;
        const targetWord = p.target_word;
        return (
          <div data-check="subtitle" style={{...captionStyle(width, height), zIndex: 30} as React.CSSProperties}>
            {height > width && p.words?.length ? karaokeTokens(cue, p.words, t).map((token: any, index: number) => <span key={index} style={{color: token.active ? '#FACC15' : 'white', display: 'inline-block', transform: token.active ? 'scale(1.06)' : undefined, marginRight: '0.25em'}}>{token.text}</span>) : renderHighlightedText(lineText, targetWord, p.modern_style)}
          </div>
        );
      })()}

      {/* Subtle Progress Bar (Thanh thời gian mỏng phát sáng ở đáy) */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          height: 6,
          width: `${Math.min(100, Math.max(0, (t / duration) * 100))}%`,
          background: 'linear-gradient(90deg, #38BDF8, #FACC15)',
          boxShadow: '0 0 10px rgba(56, 189, 248, 0.8)',
          zIndex: 20
        }}
      />

      {/* Brand Channel Logo / Watermark Cover (Hiển thị cố định từ đầu đến cuối video) */}
      {!p.hide_logo && (() => {
        const isHorizontal = width >= height;
        const logoSize = isHorizontal ? Math.round(width * (108 / 1920)) : Math.round(width * (100 / 1080));
        const logoRight = isHorizontal ? Math.round(width * (23 / 1920)) : Math.round(width * (32 / 1080));
        const logoBottom = isHorizontal ? Math.round(height * (38 / 1080)) : Math.round(height * (50 / 1920));
        const logoRadius = Math.round(logoSize * (16 / 108));
        return (
          <div
            style={{
              position: 'absolute',
              right: logoRight,
              bottom: isHorizontal ? logoBottom : undefined,
              top: isHorizontal ? undefined : Math.round(height * (120 / 1920)),
              width: logoSize,
              height: logoSize,
              borderRadius: logoRadius,
              overflow: 'hidden',
              zIndex: 40,
              boxShadow: '0 2px 10px rgba(0, 0, 0, 0.22)',
              pointerEvents: 'none',
            }}
          >
            <Img
              src={p.brandLogoSrc ? staticFile(p.brandLogoSrc) : BRAND_LOGO_DATA_URI}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                display: 'block',
              }}
            />
          </div>
        );
      })()}

      {(p.sfx_events || []).map((event: any, index: number) => <Sequence key={index} from={Math.round(event.at * fps)} durationInFrames={Math.round(.3 * fps)}><Audio src={staticFile(event.src)} volume={0.5} /></Sequence>)}
      {/* Audio Mixer: Voice narration */}
      <Audio src={staticFile(p.audioSrc || 'narration.wav')} volume={1} />

      {/* Audio Mixer: Background Music (BGM) with Dynamic Voice-Activated Ducking */}
      {p.bgmSrc && (
        <Audio
          src={staticFile(p.bgmSrc)}
          volume={(f) =>
            computeDynamicBgmVolume(
              f / fps,
              p.cues || [],
              p.bgmVolume ?? 0.12,
              p.bgmDuckedVolume ?? 0.075,
              p.bgmSwellVolume ?? 0.19
            )
          }
          loop
        />
      )}
    </AbsoluteFill>
  );
};

registerRoot(() => (
  <>
  <Composition
    id="Pilot"
    component={Video}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={1800}
    defaultProps={{scenes: [], cues: []}}
    calculateMetadata={({props}: any) => {
      const isHorizontal = props.aspect_ratio === '16:9' || props.width === 1920;
      return {
        width: props.width || (isHorizontal ? 1920 : 1080),
        height: props.height || (isHorizontal ? 1080 : 1920),
        durationInFrames: Math.ceil((props.duration || 30) * (props.fps || 30))
      };
    }}
  />
  <Composition id="Thumbnail" component={Thumbnail} width={1920} height={1080} fps={30} durationInFrames={1} defaultProps={{image: "", text: ""}} calculateMetadata={({props}: any) => ({width: props.width || 1920, height: props.height || 1080})} />
  </>
));
