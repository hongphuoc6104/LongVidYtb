# Archetype 5 — Mindful Living, Philosophy & Parables (`archetype_5_mindful_healing`)

- **Member Channels (5 core members across VN/EN):**
  - **VN:** `loi_sang_soi`, `minh_triet_song`, `tam_tinh_dem`
  - **EN Twins:** `en_second_arrow`, `en_bamboo_marble`, `en_parable_lamp`
- **Visual & HUD Signature:**
  - Warm calm sanctuary cinema / poetic brushwork / parchment stillness (muted sandalwood gold `(148, 116, 68, 245)` + parchment cream `(232, 200, 142, 255)`).
  - **Strict Comfort Downgrade (`disallowed_vfx`):** Block ALL kinetic slams, strobe flashes, radar pings, whip cuts, `forensic_v2` HUDs, and `white_flash`/`edge_pass` seams (`get_channel_motion_policy` locks `soft_fade` `0.24s`).
- **Short V4 & Audio Defaults:**
  - `theme_id`: `zen_reflective_swell` (`primary_bgm=bgm_zen_night_healing.wav`, `vacuum_stem=singing_bowl_zen.wav`), calm reflective rate `1.04x`.
- **Per-Channel Playbooks:** Load `sys/channels/<channel_id>/playbook/{overview,content,visual,pacing}.md` or run `./vp playbook <channel_id>`.
