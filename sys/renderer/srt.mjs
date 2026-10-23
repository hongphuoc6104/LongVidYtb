/**
 * Standalone Native SRT Subtitle Generator.
 * Converts timeline subtitle cues directly into standard SubRip (.srt) format.
 */

/**
 * Formats seconds into SRT timestamp format: HH:MM:SS,mmm
 * @param {number} seconds
 * @returns {string}
 */
export function formatSrtTimestamp(seconds) {
  const num = Number(seconds);
  const totalMs = Math.max(0, Math.round((Number.isFinite(num) ? num : 0) * 1000));
  const ms = totalMs % 1000;
  const totalSec = Math.floor(totalMs / 1000);
  const s = totalSec % 60;
  const totalMin = Math.floor(totalSec / 60);
  const m = totalMin % 60;
  const h = Math.floor(totalMin / 60);

  const pad = (n, len = 2) => String(n).padStart(len, '0');
  return `${pad(h)}:${pad(m)}:${pad(s)},${pad(ms, 3)}`;
}

/**
 * Generates standard SRT content from an array of subtitle cues.
 * Each cue must have {start: number, end: number, text: string}.
 *
 * Example output:
 * 1
 * 00:00:00,000 --> 00:00:02,500
 * Xin chào đây là bản dựng video độc lập.
 *
 * @param {Array<{start?: number, end?: number, text?: string}>} cues
 * @returns {string}
 */
export function generateSrt(cues) {
  if (!Array.isArray(cues) || cues.length === 0) {
    return '';
  }

  const entries = [];
  let index = 1;

  for (const cue of cues) {
    if (!cue || typeof cue !== 'object') continue;
    const start = formatSrtTimestamp(cue.start);
    const end = formatSrtTimestamp(cue.end);
    const text = String(cue.text || '').trim();
    if (!text) continue;

    entries.push(`${index}\n${start} --> ${end}\n${text}\n`);
    index++;
  }

  return entries.length > 0 ? entries.join('\n') : '';
}
