# Layer breakdown

For each scene, list: setting → background; actors/props that *change* during narration → stickers.

| Narration fragment | Visual event | Layer |
|---|---|---|
| "The emperor yawns" | emperor appears, sleepy | sticker `emperor_sleepy`, fx `pop`, anchor "emperor" |
| "when a goose bursts in" | goose slides in | sticker `goose`, fx `slide_left`, anchor "goose" |
| "and bites his beard" | emperor shakes | `shake_anchor` "bites" on emperor layer |
| "50.000 năm trước... cây đàn guitar" | time marker / prop pops on exact phrase | sticker `prehistoric_totem` @ "50.000 năm trước", sticker `guitar` @ "cây đàn guitar" |

Rules
- **See-Say Sync**: Every concrete object/prop (e.g. "cây đàn guitar"), figure, or time/number milestone (e.g. "50.000 năm trước") spoken in narration must trigger a matching sticker (`layers[].anchor`) or scene beat (`beats[].anchor`) on that exact phrase (prioritize top ≤4 new stickers/scene per `LAYER_QUOTA` + reuse).
- Background never contains figures; describe depth and open floor space.
- Sticker = one figure OR one prop, full body, centred, explicit pose/expression/costume. No scenery, no ground.
- Visible text only through `visible_text` (e.g. a sign); keep it short.
- A new pose = a new sticker; same pose in a later scene = reuse.
- Every sticker must be used by at least one layer (`LAYER_UNUSED`).
- First layer usually anchors on the scene's first word so the frame is never empty.
