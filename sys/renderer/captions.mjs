export function captionStyle(width = 1080, height = 1920) {
  const portrait = height >= width;
  const scale = width / (portrait ? 1080 : 1920);
  return {
    position: 'absolute',
    zIndex: 30,
    bottom: Math.round((portrait ? 400 : 85) * scale),
    left: portrait ? Math.round(56 * scale) : '50%',
    transform: portrait ? undefined : 'translateX(-50%)',
    width: Math.round((portrait ? 820 : 1400) * scale),
    maxWidth: '92%',
    whiteSpace: 'pre-line',
    overflowWrap: 'normal',
    fontFamily: 'Arial, sans-serif',
    fontSize: Math.round((portrait ? 48 : 38) * scale),
    fontWeight: 800,
    lineHeight: 1.28,
    textAlign: 'center',
    padding: `${Math.round(14 * scale)}px ${Math.round(24 * scale)}px`,
    boxSizing: 'border-box',
    borderRadius: Math.round(20 * scale),
    color: '#ffffff',
    background: portrait ? 'rgba(15, 23, 42, 0.88)' : 'transparent',
    border: portrait ? '2px solid rgba(56, 189, 248, 0.45)' : 'none',
    boxShadow: portrait ? '0 8px 24px rgba(0, 0, 0, 0.4)' : 'none',
    textShadow: '0 2px 8px rgba(0,0,0,0.95), 0 0 3px #000'
  };
}

export function captionMaxHeight(width = 1080, height = 1920) {
  const s = captionStyle(width, height);
  const verticalPadding = Number.parseFloat(s.padding) * 2;
  return Math.ceil(s.fontSize * s.lineHeight * 2 + verticalPadding + 12);
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
