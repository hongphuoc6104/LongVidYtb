# Archetype 4 — 2D Doodle, AI Pragmatism & Systemic Explainability (`archetype_4_doodle_explainer`)

- **Member Channels (12 total — 6 VN / 6 EN):**
  - **VN:** `ai_binh_dan`, `la_ban_hoc_thuat`, `luat_doi_thuong`, `nao_luoi`, `thuong_cho_kheo`, `tui_tien`
  - **EN Twins:** `en_plain_sight_ai`, `en_first_principles`, `en_fine_print`, `en_lazy_brain`, `en_kindred_sketch`, `en_wallet_anatomy`
- **Visual & HUD Signature:**
  - Clean 2D Indie Doodle (`1.7.0 handdrawn_2d_explainer`) / flat vector (`#FFFFFF` / `#F8F0DC` canvas, `>= 60–75%` negative space, cobalt blue `(42, 108, 184, 245)` + amber `(245, 158, 11, 255)` banners) using 1 white circle-head stickman + 1 focal metaphor ([vp-visual-fx](../../../vp-visual-fx/references/full-frame-doodle-contract.md)).
  - **Viewing-Comfort Lock (`nao_luoi`, `en_lazy_brain`):** Force gentle motion + `soft_fade` (`0.24s`); block harsh flash/whip seams (`get_channel_motion_policy`).
- **Short V4 & Audio Defaults:**
  - `theme_id`: `curious_explainer_momentum` (`primary_bgm=bgm_curious_acoustic_loop.wav`, `vacuum_stem=clock_tick.wav`), nominal rate `1.16x`.
- **Per-Channel Playbooks:** Load `sys/channels/<channel_id>/playbook/{overview,content,visual,pacing}.md` or run `./vp playbook <channel_id>`.
