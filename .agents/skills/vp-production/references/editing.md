# Timing, captions and output

Build timelines from real language-track WAVs. Interpolated anchors are estimates, not word alignment. Each cut/hold/diagram/reveal needs a semantic purpose; avoid fixed seconds per image or density quotas.

Language, aspect ratio, subtitles and track selection are independent. English outputs must render English narration/cues/timeline regardless of aspect ratio. Use one cue source for SRT and video, meaningful groups of at most two readable lines, no punctuation-only cue. Keep exact lesson spelling and enough reading time for each actual sentence.

Use supported camera/transition effects (`cut`, `hold`, `fade`, `slide_left`, `zoom_in`, `zoom_out`, `punch_in`, `pan_left`, `pan_right`, `shake`) according to render-capabilities.md; preserve teaching text and visual action under crop/zoom. No implicit Foley. Opening question and payoff must remain understandable in the sequence.

Prepare, render and encode on Colab. The machine only manages/collects important outputs. Inspect actual playback when available without treating that craft activity as a machine-review gate. Report files/timestamps and observed problems; do not claim learning/retention without audience data.

Layered scenes use `layers[].fx` (pop, pop_wobble, bounce, drop, slide_left, spin_grow) anchored to narration words; their one beat holds the background. Sticker matting and layer composition happen inside the Colab render request.

For multi-cue scenes and multi-chapter explainers, enforce **Cue-Window Allocation** (`[cue_i.start, cue_{i+1}.start)`):
- Anchor the first visual shot of every spoken cue to `cue_i.start` with `0.00s` drift (never scale only at the coarse scene boundary `SC01..SC30`, which causes cumulative mid-scene drift).
- Map shots 1:1 to spoken cues by semantic meaning in the target language script (`cue_shot_mapping_8ch.json` / `rebuild_option_b_templates.py`), re-ordering shots whenever translated or adapted clauses invert the original reference order.
- Subdivide any cue window longer than `3.80s` into semantic sub-beats so every image hold stays strictly within `1.5s–3.8s` (`<= 4.0s` hard ceiling), and verify rendered freshness (`mp4_mtime >= template_mtime`).
