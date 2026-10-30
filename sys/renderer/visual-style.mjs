// Keep original illustration colors for the light 2D profile; preserve legacy grading.
export function vignetteBackground(props = {}) {
  if (props.hide_overlays || String(props.visual_style_profile || '').startsWith('ch_') || props.visual_style_profile === 'soft_pastel_2d' || props.visual_style_profile === 'earth_toned_2d' || props.visual_style_profile === 'handdrawn_2d_explainer') return null;
  return props.modern_style
    ? 'radial-gradient(circle at 50% 45%, rgba(0,0,0,0) 65%, rgba(15,23,42,0.22) 100%)'
    : 'radial-gradient(circle at 50% 45%, rgba(0,0,0,0) 60%, rgba(0,0,0,0.42) 100%)';
}
