---
name: vp-visual-fx
description: "Visual grammar, 1.7.0 handdrawn_2d_explainer contracts, Two-Stage SceneMap planning, sharded 5-Niche FX warehouse (`sys/fx_warehouse/`), and bespoke-per-video synthesis."
---

# VP Visual Grammar & Motion FX Warehouse (`vp-visual-fx`)

Governs Video Pilot's visual continuity, `SceneMap` planning, sharded 30fps HUD/VFX/Audio warehouse (`sys/fx_warehouse/`), and bespoke per-video asset synthesis across all 5 Niche Archetypes ([vp-channel-registry](../vp-channel-registry/SKILL.md)).

## 1. Visual Contracts & Two-Stage `SceneMap`
- **Channel Visual Isolation:** Photorealistic, Noir Forensic, 3D Biomedical, Cinema 35mm, and GIS Map-Paper channels load their exact style grammar from `sys/channels/<channel_id>/playbook/visual.md`. Standard 2D channels lock to `1.7.0 handdrawn_2d_explainer` (`>= 60%` negative space, 1 stickman + 1 focal metaphor, full-frame `kind: "scene"`, zero `matte_sticker.py` cutouts) documented in [full-frame-doodle-contract.md](references/full-frame-doodle-contract.md).
- **Two-Stage `SceneMap` (`sys/flow_video/scene_map_planner.py`):**
  1. Plan Cast/Reference DAG (`reference_scene_ids`), `camera_move` (zero consecutive duplicates), and viewing-comfort policy (`get_channel_motion_policy`: forces `soft_fade 0.24s` on Group 4 Doodle `nao_luoi`/`en_lazy_brain` & Group 5 Mindful).
  2. Compile positive-framing prompts dynamically via `compile_scene_image_prompts()` (`allowed_text=None` unless declared on `1.7.0`).
- **T4 NVENC Only:** All video renders run on remote Colab Tesla T4 `FFmpeg h264_nvenc` (zero Remotion/Chromium/CPU); high-density `long_16x9` (240–350 frames) defaults to static Lanczos + `xfade=fade` unless `--fx-mode auto_niche|full_fx` is enabled.

## 2. Sharded FX & Audio Warehouse (`sys/fx_warehouse/`)
| Shard | Exported Scope |
|---|---|
| `archetypes.py` | 5 Niche Archetypes, `CHANNEL_ARCHETYPE_MAP`, comfort guardrails & bespoke policies |
| `camera_vfx.py` | 8 sub-pixel `float32` 2.5D camera curves + 7 GPU shaders + `register_bespoke_*` |
| `hud_widgets.py` | 14 30fps PIL RGBA HUD widgets + `build_bespoke_topic_hud_patch` |
| `audio_sfx_bgm.py` | 25 stereo 48kHz SFX stems + 5 BGM loops + `synthesize_bespoke_topic_sfx` |
| `selector.py` | Content-aware `auto_select_beat_fx`, `STATIC_CAMERA_HUDS`, comfort downgrades |
| `hud_forensic_v2.py` / `audio_suspense_v2.py` | 9 2K forensic HUD widgets + 4-act `-11.0 LUFS` suspense mixer |
| `pipeline_bridge.py` | Unified `--fx-mode` router (`static`, `auto_niche`, `full_fx`, `forensic_v2`) |

### Golden Rule of Non-Forced Selection & Universal Trigger Keywords
Never force an incompatible preset onto a topic (e.g., never force aviation CVR countdowns onto marine archaeology or kinetic slams onto Group 5 Mindful). Call `auto_select_beat_fx(...)`; when no catalog asset fits semantically, author `bespoke_hud_spec` / `bespoke_sfx_spec`.

| Keyword / Flag | Resolved `--fx-mode` | Behavior |
|---|---|---|
| `[PRO_FX]`, `auto_niche` | `auto_niche` | Shared spine branching cleanly to the channel's Niche Archetype + bespoke triggers |
| `[FULL_FX]`, `full_fx` | `full_fx` | Enables full 2.5D motion, 30fps HUD layer, GPU shaders & 48kHz SFX/BGM |
| `[BESPOKE_FX]`, `bespoke_fx` | `full_fx` (`force_bespoke=True`) | Synthesizes custom `bespoke_hud_spec` & `bespoke_sfx_spec` tailored to topic |
| `[FORENSIC_V2]` | `forensic_v2` | Forensic V2 30fps HUDs + 4-act suspense mix (downgraded on Group 5 Mindful) |
| `[STATIC_CLEAN]` | `static` | Locks static Lanczos + `xfade=fade` 2D framing |

## 3. References
- [Full-Frame 2D Doodle Contract (`1.7.0`)](references/full-frame-doodle-contract.md)
- [Sub-Warehouse Catalog (`camera_vfx`, `hud_widgets`, `audio_sfx_bgm`)](references/sub-warehouse-catalog.md)
- [Niche Archetype & Bespoke Synthesis Rules](references/niche-bespoke-synthesis-rules.md)
