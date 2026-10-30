export const PORTRAIT_CAPTION_ACTIVE_COLOR = '#FBBF24';

/** Profile 07: centered white text with an amber spoken-word accent. */
export function captionStyle(width = 1080, height = 1920) {
  const portrait = height >= width;
  const scale = width / (portrait ? 1080 : 1920);
  return {
    position: 'absolute',
    zIndex: 30,
    bottom: Math.round((portrait ? 400 : 85) * scale),
    left: '50%',
    transform: 'translateX(-50%)',
    width: Math.round((portrait ? 820 : 1400) * scale),
    maxWidth: '92%',
    whiteSpace: 'pre-line',
    overflowWrap: 'normal',
    fontFamily: 'Arial, sans-serif',
    fontSize: Math.round((portrait ? 48 : 38) * scale),
    fontWeight: 800,
    lineHeight: 1.28,
    textAlign: 'center',
    padding: portrait ? '0px' : `${Math.round(14 * scale)}px ${Math.round(24 * scale)}px`,
    boxSizing: 'border-box',
    borderRadius: Math.round(20 * scale),
    color: '#ffffff',
    background: 'transparent',
    border: 'none',
    boxShadow: 'none',
    ...(portrait ? {WebkitTextStroke: `${1.5 * scale}px #111827`, paintOrder: 'stroke fill'} : {}),
    textShadow: portrait ? '0 2px 4px rgba(0,0,0,0.8)' : '0 2px 8px rgba(0,0,0,0.95), 0 0 3px #000'
  };
}

/**
 * Show compact groups using measured word starts, preserving every cue token.
 * Missing or mismatched alignment keeps the complete cue without guessed timing.
 * @param {{text: string, start: number, end: number}} cue
 * @param {{word: string, start: number, end: number}[]} words
 * @param {number} time
 * @returns {{text: string, active: boolean}[]}
 */
export function portraitCaptionTokens(cue, words, time) {
  if (!cue.text.trim()) return [];
  const tokens = karaokeTokens(cue, words, time);
  const aligned = words.filter(word => word.start >= cue.start - 0.02 && word.start < cue.end);
  if (aligned.length !== tokens.length || aligned.some((word, i) =>
    word.word !== tokens[i].text || !Number.isFinite(word.start) ||
    !Number.isFinite(word.end) || word.end <= word.start ||
    (i > 0 && word.start < aligned[i - 1].end))) return tokens;
  /** @type {number[]} */
  const starts = [0];
  let count = 0;
  let chars = 0;
  tokens.forEach((token, index) => {
    if (count && (count >= 6 || chars + 1 + token.text.length > 28 ||
      /[.!?;,:…]$/u.test(tokens[index - 1].text))) {
      starts.push(index);
      count = 0;
      chars = 0;
    }
    chars += (count ? 1 : 0) + token.text.length;
    count += 1;
  });
  let group = 0;
  starts.forEach((index, position) => {
    if (time >= aligned[index].start) group = position;
  });
  return tokens.slice(starts[group], starts[group + 1] ?? tokens.length);
}

export function captionMaxHeight(width = 1080, height = 1920) {
  const s = captionStyle(width, height);
  const verticalPadding = Number.parseFloat(s.padding) * 2;
  return Math.ceil(s.fontSize * s.lineHeight * 2 + verticalPadding + 12);
}

/** Single-word kinetic pop for 9:16 portrait video (Alternating Red #FF3B30 and Yellow #FFE600) */
export function portraitKineticWord(cue, words, time) {
  if (!cue || !cue.text.trim()) return null;
  const cleanCueWords = (words || []).filter(w => w.start >= cue.start - 0.05 && w.start < cue.end + 0.05);
  if (cleanCueWords.length === 0) {
    const tokens = cue.text.trim().split(/\s+/u);
    const duration = Math.max(0.1, cue.end - cue.start);
    const progress = Math.min(1.0, Math.max(0.0, (time - cue.start) / duration));
    const idx = Math.min(tokens.length - 1, Math.floor(progress * tokens.length));
    return {
      text: tokens[idx],
      index: idx,
      color: idx % 2 === 0 ? '#FF3B30' : '#FFE600'
    };
  }

  const activeIdx = cleanCueWords.findIndex(w => w.start <= time && time < w.end);
  if (activeIdx !== -1) {
    const w = cleanCueWords[activeIdx];
    return {
      text: w.word,
      index: activeIdx,
      color: activeIdx % 2 === 0 ? '#FF3B30' : '#FFE600'
    };
  }

  const pastWords = cleanCueWords.filter(w => w.end <= time);
  if (pastWords.length > 0) {
    const lastWord = pastWords[pastWords.length - 1];
    if (time - lastWord.end < 0.25) {
      const idx = cleanCueWords.indexOf(lastWord);
      return {
        text: lastWord.word,
        index: idx,
        color: idx % 2 === 0 ? '#FF3B30' : '#FFE600'
      };
    }
  }

  return null;
}

/** Profile for 2x scale kinetic portrait typography with heavy black stroke and shadow */
export function portraitKineticCaptionStyle(width = 1080, height = 1920) {
  const scale = width / 1080;
  return {
    position: 'absolute',
    zIndex: 30,
    bottom: Math.round(400 * scale),
    left: '50%',
    transform: 'translateX(-50%)',
    width: '100%',
    textAlign: 'center',
    fontFamily: 'Arial, sans-serif',
    fontSize: Math.round(100 * scale),
    fontWeight: 900,
    lineHeight: 1.1,
    boxSizing: 'border-box',
    background: 'transparent',
    border: 'none',
    boxShadow: 'none',
    WebkitTextStroke: `${Math.round(6 * scale)}px #000000`,
    paintOrder: 'stroke fill',
    textShadow: '0 6px 16px rgba(0,0,0,0.95), 0 0 4px #000000'
  };
}


/** Match by position and time, so repeated Vietnamese words highlight separately. */
export function karaokeTokens(cue, words, time) {
  const tokens = cue.text.trim().split(/\s+/u);
  const candidates = words.filter(word => word.start >= cue.start - 0.02 && word.start < cue.end);
  if (candidates.length !== tokens.length || candidates.some((word, i) => word.word !== tokens[i])) {
    return tokens.map(text => ({text, active: false}));
  }
  return candidates.map(word => ({text: word.word, active: word.start <= time && time < word.end}));
}
