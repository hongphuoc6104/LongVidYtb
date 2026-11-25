# 02 — Zero-Box Typography & Visual Commentary Forensics

> **Thread 1B** | V12 Cinema Research | 2026-11-25

## 1. User Defect Diagnosis

The user identified **3 exact defect patterns** that make our videos look "AI edit":

| Screenshot | Defect | Source Code | Root Cause |
|---|---|---|---|
| `media_…43560abb.png` | Dark pill bar: "NỬA ĐÊM 06/08/1442 \| 48 GIỜ BÙNG BÍT TIN DỮ" | `render_prestige_dateline_png` (L321-346) | `rgba(0,0,0,0.7)` rectangle + gold separator line |
| `media_…b4602a02.png` | Gold-bordered VS plaque: "ĐÚNG 10 NGÀY [VS] TRU DI 3 HỌ" | `render_v7_stat_versus_png` (L512-599) | Dark box + gold border + red VS badge |
| `media_…ec18d5fd.png` | Dark pill bar: "THÁNG 07/1464 · QUANG THUẬN 6 \| 22 NĂM RỬA OAN" | `render_prestige_dateline_png` (L321-346) | Same dark pill + gold dot separator |

> [!CAUTION]
> **Every `ImageDraw.rectangle(fill=(0,0,0,alpha))` and `ImageDraw.rounded_rectangle()` used as text background MUST be deleted.** This is the single root cause of the "AI edit" look.

---

## 2. Channels Studied & Evidence

| Channel | Videos Analyzed | Key Typography Insight |
|---|---|---|
| **Johnny Harris** | "Real Reason Putin Invaded Ukraine" (If61baWF4GE), "Modern Middle East" (bLOEhycMG78), "Is Fascism Back?" (GV8KGcFqeLc), "Egypt River Army" (20CgG5pUv9Q) | **Map IS the analysis** — color-coded territory fills + tiny clean labels at centroids. Zero dark overlays. |
| **Fern** | NATO's Plan If Russia Attacks (5.12M views) | **Giant 3D boxless text** in physical space ("HOW WOULD A WAR..."). Fleet icon arrays as data viz. Dark-map clean sans-serif labels. |
| **Cleo Abram** | "The Sun Is Weirder Than You Think" (10M views) | **Giant cinema text** ("INTO THE") floating in space. Scale comparison IS the data. Expert lower thirds are minimal name+title only. |
| **Epic History TV** | The First Crusade (774K) | **Period-appropriate serif labels** directly on parchment maps. Empire names ARE the map labels. |
| **SandRhoman** | Why Knights Lost to Mercenaries (259K) | **Title text in smoke/cloud negative space**. Character comparison via illustrated panels, not text cards. |
| **Yarnhub** | When Tigers and Joseph Stalin Clashed (5.49M) | **"JULY 22, 1944 / MALINAVA, LATVIA"** — white Futura upper-left, zero box. Vehicle specs as small lower-left text overlay. |
| **The Operations Room** | Pearl Harbor 3/3 (454K) | Animated map arrows ARE the narrative. Tiny place-name labels on terrain. Zero HUD overlay. |

### Contact Sheets Saved

- `Screenshot: /home/hongphuoc6104/.gemini/antigravity/brain/49525582-f331-4a05-9640-f0d1fdf6d0b9/jh_editorial_body_typography.png | JH Putin/Ukraine clean map labels no boxes`
- `Screenshot: /home/hongphuoc6104/.gemini/antigravity/brain/49525582-f331-4a05-9640-f0d1fdf6d0b9/cleo_abram_editorial_typography.png | Cleo Abram giant boxless cinema text`
- `Screenshot: /home/hongphuoc6104/.gemini/antigravity/brain/49525582-f331-4a05-9640-f0d1fdf6d0b9/jh_editorial_typography_contact_sheet.png | JH Putin/Ukraine full intro montage`

---

## 3. The Four Zero-Box Typography Patterns

### Pattern A — Dates & Locations (Yarnhub/Fern Dateline)

**What top channels do:** Simple white bold text pinned to upper-left corner. 1px drop shadow for legibility. That's it.

```
BEFORE (our defect):  [█████ NỬA ĐÊM 06/08/1442 | 48 GIỜ BÙNG BÍT TIN DỮ █████]
                       ↑ dark rectangle               ↑ gold separator

AFTER (zero-box):     NỬA ĐÊM 1442
                      ↑ white text, subtle shadow, upper-left, NO RECTANGLE
```

**FFmpeg Implementation:**
```bash
drawtext=text='NỬA ĐÊM 1442':\
  fontfile=/path/to/Inter-Bold.ttf:\
  fontsize=42:\
  fontcolor=white:\
  shadowcolor=black@0.6:shadowx=2:shadowy=2:\
  x=w*0.05:y=h*0.05:\
  enable='between(t,0,4)'
```

**PIL Implementation:**
```python
# Shadow pass
draw.text((x+2, y+2), "NỬA ĐÊM 1442", fill=(0,0,0,153), font=font)
# Main pass  
draw.text((x, y), "NỬA ĐÊM 1442", fill=(255,255,255,255), font=font)
# NO ImageDraw.rectangle() — NEVER
```

**Rules:**
- Max **5 words** per dateline
- Max **2 lines** (date on line 1, location on line 2)
- Font: **Inter Bold 36-42px** (16:9) / **48-56px** (9:16)
- Duration: **3.0-4.5s** (fade in 0.3s → hold → fade out 0.5s)

---

### Pattern B — Statistical Contrasts (Anti-VS)

> [!IMPORTANT]
> **NEVER render a VS badge, comparison card, or side-by-side dark box again.** Use these 3 techniques instead:

#### B1: Split-Screen Visual Proof
Hard vertical split of two actual images. Each half has 1-3 word label in its own negative space.

```bash
# FFmpeg: split + label each half
[0:v]crop=iw/2:ih:0:0,drawtext=text='10 NGÀY':fontsize=96:x=(w-tw)/2:y=h*0.45:fontcolor=white:shadowcolor=black@0.6:shadowx=3:shadowy=3[left];
[0:v]crop=iw/2:ih:iw/2:0,drawtext=text='3 HỌ':fontsize=96:x=(w-tw)/2:y=h*0.45:fontcolor=white:shadowcolor=black@0.6:shadowx=3:shadowy=3[right];
[left][right]hstack
```

#### B2: Giant Number Kinetic Reveal
Show statistic as a **giant number** (40-60% canvas height) in vast negative space. Sequential reveal: first number → pause → second number.

```bash
# FFmpeg: giant sequential numbers
drawtext=text='10':fontsize=360:fontcolor=white:x=(w-tw)/2:y=(h-th)/2:\
  shadowcolor=black@0.5:shadowx=4:shadowy=4:\
  enable='between(t,0,2.5)',\
drawtext=text='3':fontsize=360:fontcolor=white:x=(w-tw)/2:y=(h-th)/2:\
  shadowcolor=black@0.5:shadowx=4:shadowy=4:\
  enable='between(t,3,5.5)'
```

#### B3: Color Territory Fill Contrast
Like Johnny Harris: map coloring IS the data. Red fill expands = one side gains. Blue fills in = other side responds. No text card needed.

---

### Pattern C — Historical Documents, Quotes & Evidence

#### C1: Parchment Full-Frame Quote
Cut to a **full-frame aged paper** background. Quote in period serif font. This is a SCENE CUT, not an overlay.

```python
# BELUGA prompt for background
"aged Vietnamese rice paper texture, warm sepia tones, hand-drawn ink calligraphy strokes, 
 soft natural light from left, 60% negative space, hand-drawn 2D style"

# PIL
bg = Image.open("parchment_bg.png")  # BELUGA-generated
draw = ImageDraw.Draw(bg)
font_quote = ImageFont.truetype("CrimsonText-Italic.ttf", 56)
font_attr = ImageFont.truetype("Inter-Regular.ttf", 24)
draw.text((x, y), '"Lê Lợi thương dân..."', fill=(44,24,16), font=font_quote)
draw.text((x_attr, y_attr), "— Đại Việt Sử Ký Toàn Thư", fill=(107,91,74), font=font_attr)
# NO RECTANGLE BEHIND THE TEXT
```

#### C2: Dark Tabletop Evidence Shot
Full-frame cut to dark wood surface with document/artifact lit by warm light. Text floats in dark negative space.

#### C3: Cinema Quote Overlay (Giant Sparse)
1-3 word excerpt at **120-180px** over very dark footage (brightness ≈ 0.15-0.25).

```bash
# FFmpeg: dim footage + giant text
eq=brightness=-0.6,\
drawtext=text='TRU DI':fontsize=180:fontcolor=white:\
  x=(w-tw)/2:y=h*0.4:\
  shadowcolor=black@0.7:shadowx=4:shadowy=4
```

---

### Pattern D — Visual Commentary & Analytical Cutaways

| Format | When to Use | Implementation |
|---|---|---|
| **D1: Giant 1-3 Word Cinema Type** | Chapter transitions, date reveals, dramatic verdicts | 96-180px white text in negative space, subtle shadow |
| **D2: Split-Screen Before/After** | Cause/effect, two-side conflicts | `crop` + `hstack` + labels |
| **D3: Progressive Evidence Highlight** | Analyzing documents, pointing out details | Vignette spotlight + small annotation |
| **D4: Territory Fill Map** | Geopolitics, empire expansion, alliances | PIL polygon fill with centroid labels |
| **D5: Dark-Tabletop Evidence Rig** | Historical documents, decrees, source quotes | BELUGA full-frame + floating text in negative space |

---

## 4. Colab T4 NVENC Implementation

### Text Rendering Pipeline

```
PIL pre-render → transparent PNG → FFmpeg overlay filter → h264_nvenc
```

**Why PIL + FFmpeg overlay (not drawtext alone):**
- PIL gives kerning control, multi-line layout, Vietnamese diacritics quality
- FFmpeg `overlay` filter respects PNG alpha natively
- `h264_nvenc` on T4 handles overlay compositing at real-time speed

### FFmpeg Overlay Command Template
```bash
ffmpeg -hwaccel cuda -i input.mp4 -i text_overlay.png \
  -filter_complex "[0:v][1:v]overlay=x=X:y=Y:\
    enable='between(t,T_START,T_END)':\
    alpha='if(lt(t-T_START,0.4),(t-T_START)/0.4,\
           if(gt(t-T_START,DUR-0.5),(DUR-(t-T_START))/0.5,1))'" \
  -c:v h264_nvenc -preset p4 -rc vbr -cq 23 \
  -c:a copy output.mp4
```

### Anti-Patterns to DELETE from Codebase

| File | Lines | What to Remove |
|---|---|---|
| `render_single_pass.py` | L321-346 | `render_prestige_dateline_png` dark rectangle |
| `render_single_pass.py` | L512-599 | `render_v7_stat_versus_png` VS plaque |
| `render_single_pass.py` | L450-509 | `render_v7_hook_headline_png` dark box |
| `hud_widgets.py` | L77-438 | All `_draw_pill`, `_draw_card_shell` |
| `hud_forensic_v2.py` | L288-306, L402-430, L1338-1342 | `_draw_pill`, `_draw_card_shell`, rect scrim |
| `history_styles_10x10.py` | L1744-1967, L2786-3133 | Short boxed stamps/cards |

> [!TIP]
> The existing `_render_long_zero_box_hud` at `history_styles_10x10.py:L3136-3217` is already a good starting point — extend this pattern to ALL text rendering.

---

## 5. Universal Zero-Box Rules

1. **Max 3 words** for any text that appears ON footage (not full-frame cutaways)
2. **Shadow only** — `2-4px offset, rgba(0,0,0,0.5-0.7)` — never a background rectangle
3. **Negative space placement** — text goes where the frame is darkest/emptiest (sky, water, shadow)
4. **Full-frame for dense text** — anything >5 words gets its own full-frame cutaway (parchment, tabletop, dark slate)
5. **Font stack**: Inter Bold/Black (data), Crimson Text Italic (quotes), Montserrat Black (impact numbers)
6. **Never** render: rectangles, pills, borders, separator lines, gold accents, VS badges, comparison cards
