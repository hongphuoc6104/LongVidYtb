# Pacing & Script Rules — Sử Kể Lại (v3)

Reference contract for zero-filler Vietnamese spoken narration, clause-level sub-beat splitting (`Long 16:9`), and `12`-beat `Short 9:16` spin-off arcs.

## 1. Zero-Filler 12-Sentence-Per-Chapter Structure (`Long 16:9`)

Every `long_16x9` episode is locked to:
- **`10` Chapters × `12` Core Sentences = `120` Core Sentences** total.
- **Zero Filler**: Every sentence must advance a concrete historical event, tactical mechanism, geographical constraint, causal consequence, or human stake. Cut throat-clearing intros ("Trong video hôm nay..."), repetitive summaries, and generic adjectives.
- **Spoken Cadence**: Write short, natural Vietnamese spoken sentences calibrated for `VietNarrator_su_ke_lai` at `1.30x` (`speaking_rate=1.30`) with `0.06s` inter-beat gaps and `0.18s` chapter gaps, targeting **`~9m15s–9m45s`** total runtime.
- **Chapter Hook & Payoff**:
  - Sentence 1 of Chapter 1 opens immediately with a counter-intuitive historical stake or visceral tactical problem (no channel intro).
  - Sentence 12 of each chapter bridges directly into the next chapter's escalation.

## 2. Two-Clause Sentence Rule (Eliminating Visual Drag)

Each of the `120` spoken sentences is split at its natural **clause boundary** (comma, conjunction, or cause-effect pivot) into **two visual sub-beats**, yielding **`240` BELUGA `1920x1080` frames** (average **`~2.30s–2.40s/image`**) connected by `xfade=fade:duration=0.18`:

| Sub-beat | Duration Share | Camera Role (from 5-Shot Matrix) | Visual Purpose |
| :--- | :--- | :--- | :--- |
| **Sub-beat A** | **`48%`** | **Wide Establishing** or **Medium OTS** (or Atmospheric Landscape) | Establishes the spatial/tactical context of the opening clause |
| **Sub-beat B** | **`52%`** | **Tight Action Macro** or **Low-Angle Hero** | Punches in on the physical detail, weapon, terrain hazard, or human reaction in the second clause |

### Split Example
- **Spoken Sentence**: *"Khi thủy triều bắt đầu rút xuống lòng sông Bạch Đằng, hàng nghìn cọc gỗ lim bịt sắt mới lộ mũi nhọn dưới làn nước đục."*
- **Sub-beat A (`48%`)**: Wide Establishing across the receding muddy tide of the Bạch Đằng estuary at dusk, dark wooden war junks drifting in the current.
- **Sub-beat B (`52%`)**: Tight Action Macro just above the swirling brown waterline as sharpened, charred ironwood stake tips emerge from the ebbing current.

## 3. Short 9:16 Narrative Arcs (Mode A 12-Beat & Mode B 20-Beat V3)

### Mode A — Standalone Long Spin-Off (`short_9x16`, `~48–58s`)
Standalone `short_9x16` spin-offs (`parent_long_id` linked, Dual-Model `veo_3_1_lite` Seam + `omni_flash` Frame-Link) follow a compressed `12`-beat arc:

1. **Beats 1–2 (`0–8s`) — Counter-Intuitive Hook**: Immediate historical paradox or fatal tactical miscalculation in beat 1 (`<= 18` syllables, zero pause).
2. **Beats 3–5 (`8–22s`) — Terrain & Constraint**: Visualizes the exact physical bottleneck (river tide, mountain pass, supply line, armor/weapon mismatch).
3. **Beats 6–9 (`22–40s`) — Tactical Turn & Climax**: Step-by-step execution of the ambush, counter-strike, or engineered trap.
4. **Beats 10–12 (`40–58s`, last 15%) — Consequence, Close CTA & Channel Bridge**: Lands the decisive historical outcome and delivers a natural close CTA + bridge to the full `parent_long_id` episode on **Sử Kể Lại** (never "like/share/subscribe").

### Mode B — Serialized Heroic Short (`serialized_detail_short`, `20` beats, `~105–118s`, `< 125s`, `4 chunks × 5 beats`)
For multi-phase campaigns designed as **"nghe để học cái hay như xem phim"**, lock each serialized episode (`Tập 1 -> Tập 2 -> Tập 3`) to **`20` beats (`~105–118s`, `< 125s`, `4` chunks × `5` beats)**. Ground 100% in primary chronicles (`vp-notebooklm-vault`; quarantine `dã sử / tương truyền` in `report_only_claims`).
- **100% 35mm Live-Action Epic & Screen Text Law**: CẤM sa bàn đất sét/bùn gỗ (`tactical_sand_table`) hoặc bản đồ ký hiệu không chú thích; diễn giải mưu lược qua toàn cảnh rộng/trên cao dễ hiểu ngay (biển đuốc vây thành, kỵ binh phục kích mưa đêm, đại quân áp sát, voi chiến, cờ bay rạng đông). Banner chữ chỉ dùng `heroic_banner` (`anchor_y=150`, `<= 4` từ viết HOA, `NotoSans-Bold.ttf` viền đen dày, **`font_size >= VietSub >= 132px`** trên `1440x2560`, mục tiêu `136px`; CẤM hộp telemetry nhiều dòng, kicker hoặc subline nhỏ).

#### 5-Act Heroic Cinema + Analysis Arc (`B00–B19`)
1. **Hồi 1 (`B00–B03`, Chunk 1) — Thế cờ sinh tử & nghịch lý chiến lược**: `B00` Hook `<= 18` syllables (**zero `[pause:...]`**), đặt ngay thế hiểm nghèo và câu hỏi chiến lược.
2. **Hồi 2–3 (`B04–B10`, Chunks 1–3) — Giải phẫu mưu lược & cái giá nếu sai 1 bước**: Toàn cảnh 35mm dễ hiểu ngay tức thì làm rõ bẫy chiến thuật & cơ chế tâm lý khiến địch mắc sai lầm (`--visual-mode hybrid_2k` có thể pin `12` beat động `flow_video` + `8` beat toàn cảnh/chân dung `2k_native_kenburns` qua `asset_mode_override`).
3. **Hồi 4 (`B11–B15`, Chunks 3–4) — Nén căng thẳng → `[pause:450–650ms]` + `silence_vacuum` tim đập → Cao trào bùng nổ**: Câu ngắn dồn dập (`urgent_escalation`), ngắt bằng **`[pause:450–650ms]`** trên khoảng lặng `silence_vacuum` tim đập, rồi bùng nổ (`climax_heroic` + `braaam` + `taiko` + kèn đồng D-major).
4. **Hồi 5 (`B16–B19`, Chunk 4, final 15% `< 125s`) — Đúc kết bài học hào khí + Nút thắt Tập 2/3 & Channel Bridge**: Rút ra bài học tư duy & tự hào dân tộc (`reflective_lesson`), mở nút thắt Tập kế tiếp trên **Sử Kể Lại** + `parent_long_id` (`bridge <= 22` syl, `close <= 24` syl, combined outro `<= 38` syl, zero *"like/share/subscribe"*).

#### 6 `delivery_mode` Vocal Profiles (`sys/voice_prosody.py`)
OmniVoice clones emotion from reference audio without ElevenLabs inline emotion tags; pair `[pause:Xms]` silence splicing (`split_text_with_pauses()`) with per-beat `delivery_mode`:

| `delivery_mode` | Narrative Placement | Vocal Character & Pacing Role |
|---|---|---|
| `tense_whisper` | Hồi 1 covert setup & Hồi 4 pre-ambush breath | Hushed, close-mic tension before contact or inside night reconnaissance |
| `narrative_cinema` | Hồi 1–2 human stakes & transition beats | Warm, grounded docudrama storyteller baseline |
| `tactical_breakdown` | Hồi 2–3 wide 35mm tactical & failure-mode cuts | Crisp analytical clarity explaining *"why this worked"* and *"where 1 slip fails"* |
| `urgent_escalation` | Hồi 4 pre-climax rapid short clauses | Tightening cadence and rising urgency leading into `[pause:450–650ms]` |
| `climax_heroic` | Hồi 4 post-vacuum turning-point eruption | High-authority resonant peak over `braaam` + `taiko` + D-major brass |
| `reflective_lesson` | Hồi 5 strategic takeaway & Tập 2/3 cliffhanger | Measured, thoughtful cadence landing the human lesson and channel bridge |

#### `heroic_vietnam_epic` Audio & Single-Pass 4-GPU Render (`sys/short_engine/`)
- **Epic 5-Act Audio (`sys/short_engine/audio_epic.py`)**: Normalize utterances to **`-14.0 LUFS` BEFORE `micro_gain_db`** so whisper-to-heroic contrast survives; score **5-Act `heroic_vietnam_epic`** (trống trận, ngũ cung Việt Nam, pre-climax `silence_vacuum` + heartbeat aligned to `[pause:450–650ms]`, Act 4 `braaam` + `taiko` + kèn đồng D-major, master **`-11.0 LUFS / -1.0 dBTP`**).
- **Single-Pass 4-GPU Render (`sys/short_engine/render_single_pass.py`)**: Default `--render-mode single_pass` (`<= 15 phút` E2E, `~8–12 phút` target) splits `4` chunks (`0` overhang), runs `slice_ass_for_window()`, encodes 4 complete 2K chunks in parallel on Colab T4 (`-bf 0 -g 30 -b:v 10M -preset p4`, `flags=bicubic` + `unsharp=3:3:0.45:3:3:0.25`), and joins locally in `<2s` lossless (`ffmpeg -f concat -c:v copy -c:a copy`); `--render-mode two_pass` stays available for compatibility. Always clean up with `unassign_server=True` and abort failover after `2` consecutive `COLAB_EXEC_UNCONFIRMED`.
