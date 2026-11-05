"""Style v2 90-image dataset generator for 18 English channels.
Mini 20s story arc: Beat 1 (Hook) -> Beats 2-4 (Mechanism) -> Beat 5 (Payoff).
Strictly adheres to style_v2_spec.md.
"""
import json
from pathlib import Path

CHANNELS_DATA = [
    {
        "channel": "en-first-principles",
        "number": 1,
        "style_vi": "Mực tối giản & mảng màu phẳng trên giấy kem ấm (Veritasium/Primer)",
        "palette": "#F4EFE4 bg, #2B2B2B line, #E07A3F accent, #9BA88D",
        "topic": "Tsiolkovsky Rocket Equation & Multistage staging breakdown",
        "beats": [
            {
                "beat": 1,
                "role": "hook",
                "prompt": "Vertical 9:16 full-bleed minimalist ink line art on warm cream paper #F4EFE4. A slender multistage rocket stands upright drawn with clean dark lines #2B2B2B. Only the tiny top nosecone is highlighted in warm terracotta #E07A3F, with muted sage #9BA88D accents. Over 65% negative space, lower 30% completely uncluttered, zero text, zero numbers, zero blueprint lines."
            },
            {
                "beat": 2,
                "role": "mechanism_friction",
                "prompt": "Vertical 9:16 full-bleed minimalist ink line art on warm cream paper #F4EFE4. Architectural cross-section of an empty hollow rocket fuel tank in crisp charcoal lines #2B2B2B. Heavy terracotta downward resistance vectors #E07A3F show parasitic dead weight, with sage #9BA88D accents. Over 65% calm negative space, lower 30% empty, zero text, zero letters, zero blue."
            },
            {
                "beat": 3,
                "role": "mechanism_turn",
                "prompt": "Vertical 9:16 full-bleed minimalist ink line art on warm cream paper #F4EFE4. The massive lower booster stage cleanly detaches downward in ghosted charcoal lines #2B2B2B, with vibrant terracotta release sparks #E07A3F at the separation plane. Sage green guidelines #9BA88D, over 65% negative space, lower 30% clean, zero text, zero grids, zero blue."
            },
            {
                "beat": 4,
                "role": "mechanism_surge",
                "prompt": "Vertical 9:16 full-bleed minimalist ink line art on warm cream paper #F4EFE4. The lightweight upper stage rocket accelerates rapidly upward along a curve drawn in dark ink #2B2B2B. A clean solid terracotta exhaust flame #E07A3F propels the sleek vehicle with sage #9BA88D accents. Over 65% negative space, lower 30% empty, zero text, zero letters."
            },
            {
                "beat": 5,
                "role": "payoff",
                "prompt": "Vertical 9:16 full-bleed minimalist ink line art on warm cream paper #F4EFE4. A delicate mechanical balance scale in clean charcoal lines #2B2B2B: discarded heavy booster tanks sink below while a tiny terracotta capsule #E07A3F ascends freely into orbital space with sage #9BA88D accents. Over 70% negative space, lower 30% clean, zero text, zero numbers."
            }
        ]
    },
    {
        "channel": "en-scale-and-bone",
        "number": 2,
        "style_vi": "Minh họa động vật học bột màu gouache trên giấy kem (PBS Eons/BBC Earth)",
        "palette": "#F2EBDD bg, #4A6B53 moss green, #C86D51 terracotta, #3A2E25 dark bark",
        "topic": "Komodo Dragon hatchling climbing trees to escape cannibalistic adults",
        "beats": [
            {
                "beat": 1,
                "role": "hook",
                "prompt": "Vertical 9:16 full-bleed naturalist gouache illustration on warm cream #F2EBDD. A tiny, vulnerable Komodo dragon hatchling with mottled terracotta #C86D51 scales pauses beside a moss-covered root #4A6B53 with deep bark shadows #3A2E25. Over 65% calm negative space, soft brushwork, lower 30% simple, zero text, zero letters, zero grids, zero human elements."
            },
            {
                "beat": 2,
                "role": "mechanism_friction",
                "prompt": "Vertical 9:16 full-bleed naturalist gouache illustration on warm cream #F2EBDD. A shadowy massive adult Komodo dragon head in deep bark brown #3A2E25 prowls across the forest floor below, framed by muted moss green #4A6B53 and earthy terracotta #C86D51. Menacing profile, over 65% calm negative space, lower 30% empty, zero text, zero HUD, zero blue."
            },
            {
                "beat": 3,
                "role": "mechanism_turn",
                "prompt": "Vertical 9:16 full-bleed naturalist gouache illustration on warm cream #F2EBDD. Macro perspective of the tiny hatchling's sharp curved claws gripping vertical tree bark #3A2E25, scrambling vigorously upward away from danger, with terracotta skin highlights #C86D51 and moss #4A6B53. Over 65% calm negative space, lower 30% clean, zero text, zero letters, zero blue."
            },
            {
                "beat": 4,
                "role": "mechanism_surge",
                "prompt": "Vertical 9:16 full-bleed naturalist gouache illustration on warm cream #F2EBDD. High in the canopy, the small Komodo juvenile rests securely on a horizontal mossy tree branch #4A6B53 with warm terracotta belly scales #C86D51 overlooking the distant ground #3A2E25. Over 65% calm negative space, lower 30% simple, zero text, zero numbers, zero blue."
            },
            {
                "beat": 5,
                "role": "payoff",
                "prompt": "Vertical 9:16 full-bleed naturalist gouache illustration on warm cream #F2EBDD. An ancient towering rainforest tree rendered in deep brown gouache #3A2E25 with lush moss patches #4A6B53, cradling one solitary tiny hatchling #C86D51 safe in high foliage. Serene natural sanctuary, over 70% calm negative space, lower 30% empty, zero text, zero letters."
            }
        ]
    },
    {
        "channel": "en-pocket-cosmos",
        "number": 3,
        "style_vi": "Vũ trụ tối giản, hư vô đen ấm với thiên thể phát sáng đơn độc (melodysheep/Kurzgesagt)",
        "palette": "#0E0B0A warm black void, #F2A541 golden amber, #F6E7CB soft cream glow, #B5523B deep ember",
        "topic": "Photon sphere and light bending at black hole event horizon",
        "beats": [
            {
                "beat": 1,
                "role": "hook",
                "prompt": "Vertical 9:16 full-bleed minimal cosmic illustration on deep warm-black void #0E0B0A. A pure dark spherical silhouette sits centered, encircled by a razor-thin radiant amber ring #F2A541 with soft cream luminescence #F6E7CB and subtle ember accents #B5523B. Over 70% calm negative space, lower 30% dark and empty, zero blue, zero text, zero grids, zero HUD."
            },
            {
                "beat": 2,
                "role": "mechanism_friction",
                "prompt": "Vertical 9:16 full-bleed minimal cosmic illustration on deep warm-black void #0E0B0A. A solitary beam of golden light #F2A541 enters from the side, bending into an acute gravitational curve around a massive dark spherical shadow with ember edges #B5523B and cream haze #F6E7CB. Over 70% negative space, lower 30% empty, zero text, zero grids, zero blue."
            },
            {
                "beat": 3,
                "role": "mechanism_turn",
                "prompt": "Vertical 9:16 full-bleed minimal cosmic illustration on deep warm-black void #0E0B0A. At the photon sphere boundary, a stream of golden amber light #F2A541 loops into a perfect glowing circular orbit around the central black void, shining with cream luminescence #F6E7CB and ember glow #B5523B. Over 70% negative space, lower 30% dark, zero text, zero blue."
            },
            {
                "beat": 4,
                "role": "mechanism_surge",
                "prompt": "Vertical 9:16 full-bleed minimal cosmic illustration on deep warm-black void #0E0B0A. The trapped circulating photon stream glows intensely in radiant amber #F2A541 and soft cream light #F6E7CB, carving a razor-sharp halo around the pitch-black event horizon with ember warmth #B5523B. Over 70% negative space, lower 30% clean, zero text, zero HUD, zero blue."
            },
            {
                "beat": 5,
                "role": "payoff",
                "prompt": "Vertical 9:16 full-bleed minimal cosmic illustration on deep warm-black void #0E0B0A. Sublime cosmic halo metaphor: a single pure circular crown of warm amber light #F2A541 floating in eternal equilibrium around a silent dark sphere, with gentle cream aura #F6E7CB and ember rim #B5523B. Over 75% calm negative darkness, lower 30% empty, zero text, zero blue."
            }
        ]
    },
    {
        "channel": "en-deep-time-strata",
        "number": 4,
        "style_vi": "Mặt cắt địa chất hội họa, tông màu đất ấm ít lớp (History of the Earth/PBS Eons)",
        "palette": "#E9DCC3 cream parchment, #C68B59 terracotta sandstone, #7A4E2D deep canyon brown, #D9A05B dry ochre salt",
        "topic": "Messinian Salinity Crisis when the Mediterranean became a dry salt desert",
        "beats": [
            {
                "beat": 1,
                "role": "hook",
                "prompt": "Vertical 9:16 full-bleed painterly geological cross-section on pale cream stone #E9DCC3. A vast cracked desert basin canyon carved from terracotta sandstone #C68B59 and deep brown strata #7A4E2D with dry ochre salt crystals #D9A05B. Broad brushstrokes, over 65% calm negative space, lower 30% clean, zero text, zero numbers, zero grids, zero blue ocean."
            },
            {
                "beat": 2,
                "role": "mechanism_friction",
                "prompt": "Vertical 9:16 full-bleed painterly geological landscape on pale cream stone #E9DCC3. Massive tectonic mountain barrier rising in deep brown #7A4E2D and terracotta #C68B59, sealing off a dry canyon threshold dusted with ochre mineral salt #D9A05B. Over 65% calm negative space, lower 30% empty, zero text, zero letters, zero grids, zero blue water."
            },
            {
                "beat": 3,
                "role": "mechanism_turn",
                "prompt": "Vertical 9:16 full-bleed painterly geological view on pale cream stone #E9DCC3. Endless geometric polygonal salt flats crusting across a sunken desert valley floor in shimmering ochre #D9A05B and terracotta sandstone #C68B59 with brown fissures #7A4E2D. Over 65% calm negative space, lower 30% simple, zero text, zero labels, zero grids, zero blue."
            },
            {
                "beat": 4,
                "role": "mechanism_surge",
                "prompt": "Vertical 9:16 full-bleed painterly geological cross-section on pale cream stone #E9DCC3. A colossal natural rock dam breaching in deep canyon brown #7A4E2D as a majestic torrent of water floods the terracotta valley #C68B59 with ochre spray #D9A05B. Over 65% calm negative space, lower 30% clean, zero text, zero letters, zero neon."
            },
            {
                "beat": 5,
                "role": "payoff",
                "prompt": "Vertical 9:16 full-bleed painterly geological cross-section on pale cream stone #E9DCC3. Minimal stratified earth profile showing thick ancient banded layers of ochre salt #D9A05B, terracotta sandstone #C68B59, and deep brown bedrock #7A4E2D. Calm timeless geological strata, over 70% calm negative space, lower 30% empty, zero text, zero numbers."
            }
        ]
    },
    {
        "channel": "en-inside-vessel",
        "number": 5,
        "style_vi": "Render 3D y khoa mềm mại & tinh gọn trên nền san hô kem ấm (Nucleus/Kurzgesagt)",
        "palette": "#F6E6DC warm coral cream bg, #D9534F ruby crimson, #F2B5A0 peach organelle, #6B2E2E deep garnet",
        "topic": "Cardiac muscle mitochondria density and zero lactic acid fatigue",
        "beats": [
            {
                "beat": 1,
                "role": "hook",
                "prompt": "Vertical 9:16 full-bleed soft clean 3D cellular render on warm coral cream #F6E6DC. A single stylized cardiac muscle fiber floats gracefully with soft ruby crimson #D9534F and peach #F2B5A0 tones with deep garnet accents #6B2E2E. Smooth matte surfaces, studio lighting, over 65% calm negative space, lower 30% empty, zero text, zero labels, zero blue."
            },
            {
                "beat": 2,
                "role": "mechanism_friction",
                "prompt": "Vertical 9:16 full-bleed soft clean 3D cellular render on warm coral cream #F6E6DC. A cross-section cutaway of a heart muscle cell revealing hundreds of smooth, densely packed oval mitochondria in peach #F2B5A0 and ruby crimson #D9534F with deep garnet borders #6B2E2E. Over 65% calm negative space, lower 30% clean, zero text, zero labels, zero blue."
            },
            {
                "beat": 3,
                "role": "mechanism_turn",
                "prompt": "Vertical 9:16 full-bleed soft clean 3D cellular render on warm coral cream #F6E6DC. Macro view of a single pill-shaped mitochondrion glowing with gentle peach warmth #F2B5A0, with folded inner cristae membranes in ruby crimson #D9534F and garnet #6B2E2E. Over 65% calm negative space, lower 30% empty, zero text, zero letters, zero blue."
            },
            {
                "beat": 4,
                "role": "mechanism_surge",
                "prompt": "Vertical 9:16 full-bleed soft clean 3D cellular render on warm coral cream #F6E6DC. Interlocking myocardial muscle bands contracting in smooth harmony in ruby crimson #D9534F, powered by golden energy channels in peach #F2B5A0 and garnet #6B2E2E without fatigue crystals. Over 65% calm negative space, lower 30% clean, zero text, zero blue."
            },
            {
                "beat": 5,
                "role": "payoff",
                "prompt": "Vertical 9:16 full-bleed soft clean 3D cellular render on warm coral cream #F6E6DC. An elegant minimalist infinity loop sculpture formed of stylized cardiac muscle tissue in ruby crimson #D9534F with peach accents #F2B5A0 and garnet shadow #6B2E2E. Symbol of tireless rhythm, over 70% calm negative space, lower 30% empty, zero text, zero blue."
            }
        ]
    },
    {
        "channel": "en-macro-gears",
        "number": 6,
        "style_vi": "Sa bàn isometric đất sét & giấy trên nền cát ấm (Practical Engineering/Visual Capitalist)",
        "palette": "#EFE6D6 warm sand bg, #D97706 warm ochre orange, #5E6B5B slate sage, #3A3530 dark charcoal clay",
        "topic": "How standardized shipping containers collapsed freight costs by 90%",
        "beats": [
            {
                "beat": 1,
                "role": "hook",
                "prompt": "Vertical 9:16 full-bleed isometric clay diorama on warm sand background #EFE6D6. A solitary stack of irregular wooden crates and barrels modeled in matte clay tones with slate sage #5E6B5B and charcoal #3A3530 accents. Soft studio lighting, over 65% calm negative space, lower 30% clean, zero text, zero letters, zero blueprint lines, zero neon."
            },
            {
                "beat": 2,
                "role": "mechanism_friction",
                "prompt": "Vertical 9:16 full-bleed isometric clay diorama on warm sand background #EFE6D6. A single corrugated steel shipping container in bold warm ochre orange #D97706, perfectly rectangular and modular with slate sage corners #5E6B5B and charcoal shadow #3A3530. Over 65% calm negative space, lower 30% empty, zero text, zero logos, zero blue."
            },
            {
                "beat": 3,
                "role": "mechanism_turn",
                "prompt": "Vertical 9:16 full-bleed isometric clay diorama on warm sand background #EFE6D6. Three identical modular containers in ochre orange #D97706 and slate sage #5E6B5B clicking together with miniature twist-locks into a compact block on charcoal base #3A3530. Over 65% calm negative space, lower 30% clean, zero text, zero numbers, zero blue."
            },
            {
                "beat": 4,
                "role": "mechanism_surge",
                "prompt": "Vertical 9:16 full-bleed isometric clay diorama on warm sand background #EFE6D6. A minimalist stylized gantry crane in slate sage #5E6B5B lifting a single ochre container #D97706 in one smooth mechanical motion above a charcoal rail track #3A3530. Over 65% calm negative space, lower 30% simple, zero text, zero letters, zero blue."
            },
            {
                "beat": 5,
                "role": "payoff",
                "prompt": "Vertical 9:16 full-bleed isometric clay diorama on warm sand background #EFE6D6. Minimal mechanical balance scale: a chaotic pile of loose barrels tipping up while a single compact ochre container #D97706 rests solidly on the lower pan with sage accents #5E6B5B and charcoal #3A3530. Over 70% negative space, lower 30% empty, zero text, zero blue."
            }
        ]
    },
    {
        "channel": "en-fine-print",
        "number": 7,
        "style_vi": "In ấn risograph 3 màu trên giấy kem (LegalEagle/CNBC)",
        "palette": "#F5EFE6 cream paper, #E63946 bold scarlet ink, #2B2B2B charcoal ink, #F2C14E warm amber",
        "topic": "Buried background data mining terms in consumer service agreements",
        "beats": [
            {
                "beat": 1,
                "role": "hook",
                "prompt": "Vertical 9:16 full-bleed 3-color risograph print on warm cream paper #F5EFE6. A single elegant legal scroll stands vertically with crisp charcoal linework #2B2B2B and a bold scarlet wax seal #E63946 with warm amber accents #F2C14E. Tactile grain, over 65% calm negative space, lower 30% completely uncluttered, zero text, zero readable words, zero blue."
            },
            {
                "beat": 2,
                "role": "mechanism_friction",
                "prompt": "Vertical 9:16 full-bleed 3-color risograph print on warm cream paper #F5EFE6. A classic brass magnifying glass with warm amber frame #F2C14E hovering over a contract page, casting a bold scarlet shadow #E63946 over charcoal lines #2B2B2B. Over 65% calm negative space, lower 30% empty, zero text, zero letters, zero blue."
            },
            {
                "beat": 3,
                "role": "mechanism_turn",
                "prompt": "Vertical 9:16 full-bleed 3-color risograph print on warm cream paper #F5EFE6. A heavy iron padlock in dark charcoal #2B2B2B snapping shut around a scarlet ribbon #E63946 with a warm amber keyhole #F2C14E, sealing away consumer rights. Over 65% calm negative space, lower 30% clean, zero text, zero letters, zero blue."
            },
            {
                "beat": 4,
                "role": "mechanism_surge",
                "prompt": "Vertical 9:16 full-bleed 3-color risograph print on warm cream paper #F5EFE6. A stylized balance scale in dark charcoal #2B2B2B: an oversized scarlet corporate stamp #E63946 heavily outweighs a fragile amber quill pen #F2C14E on the cream sheet. Over 65% calm negative space, lower 30% simple, zero text, zero words, zero blue."
            },
            {
                "beat": 5,
                "role": "payoff",
                "prompt": "Vertical 9:16 full-bleed 3-color risograph print on warm cream paper #F5EFE6. A single clean scarlet judge gavel #E63946 resting horizontally upon a round charcoal sound block #2B2B2B with subtle warm amber grain #F2C14E. Minimalist judicial stillness, over 70% calm negative space, lower 30% empty, zero text, zero letters, zero blue."
            }
        ]
    },
    {
        "channel": "en-crowd-strings",
        "number": 8,
        "style_vi": "Bóng khắc gỗ linocut thưa thớt trên giấy ngà, điểm nhấn đỏ (Academy of Ideas/Fern)",
        "palette": "#F4EEDB ivory paper, #111111 relief block black, #C0392B bold crimson accent",
        "topic": "Conformity and normative social influence in group decisions",
        "beats": [
            {
                "beat": 1,
                "role": "hook",
                "prompt": "Vertical 9:16 full-bleed bold linocut relief print on textured ivory paper #F4EEDB. A sparse row of identical stark black mannequin silhouettes #111111, with exactly one figure highlighted by a crimson shadow #C0392B. Sharp woodblock gouge textures, over 65% calm negative space, lower 30% completely empty, zero text, zero letters, zero blue, zero faces."
            },
            {
                "beat": 2,
                "role": "mechanism_friction",
                "prompt": "Vertical 9:16 full-bleed bold linocut relief print on textured ivory paper #F4EEDB. Three vertical black comparison bars #111111 of clearly unequal heights, with a single deceptive crimson horizontal guideline #C0392B forcing false equality. Sharp gouged edges, over 65% calm negative space, lower 30% clean, zero text, zero numbers, zero blue."
            },
            {
                "beat": 3,
                "role": "mechanism_turn",
                "prompt": "Vertical 9:16 full-bleed bold linocut relief print on textured ivory paper #F4EEDB. Minimalist marionette puppet strings in vibrant crimson #C0392B connecting a row of stylized black wooden head silhouettes #111111, exerting invisible social pressure. Over 65% calm negative space, lower 30% empty, zero text, zero letters, zero hands, zero blue."
            },
            {
                "beat": 4,
                "role": "mechanism_surge",
                "prompt": "Vertical 9:16 full-bleed bold linocut relief print on textured ivory paper #F4EEDB. A single lone black figure silhouette #111111 wavering under the tension of a crimson elastic cord #C0392B before turning to align with the crowd. Dramatic relief contrast, over 65% calm negative space, lower 30% clean, zero text, zero faces, zero blue."
            },
            {
                "beat": 5,
                "role": "payoff",
                "prompt": "Vertical 9:16 full-bleed bold linocut relief print on textured ivory paper #F4EEDB. A single solitary crimson origami bird #C0392B breaking free upward into empty space above a quiet row of black shadow heads #111111. Poetic independence, over 70% calm negative space, lower 30% empty, zero text, zero words, zero blue."
            }
        ]
    },
    {
        "channel": "en-cold-case-ink",
        "number": 9,
        "style_vi": "Sa bàn thu nhỏ u tối, ánh đèn vàng ấm, than chì & nâu đỏ (LEMMiNO)",
        "palette": "#14110F charcoal black void, #FFB703 warm amber lamplight, #5A4A3F deep sepia, #D9C7A7 parchment cream",
        "topic": "Tamam Shud mystery and the cipher torn from a rare Rubaiyat book",
        "beats": [
            {
                "beat": 1,
                "role": "hook",
                "prompt": "Vertical 9:16 full-bleed moody miniature diorama in deep charcoal sepia #14110F. A vintage wooden park bench sits illuminated by a single warm amber conical lamplight #FFB703, revealing rich sepia shadows #5A4A3F and parchment tones #D9C7A7. Cinematic tenebrism, over 65% calm negative space, lower 30% dark and empty, zero blue fog, zero text, zero faces."
            },
            {
                "beat": 2,
                "role": "mechanism_friction",
                "prompt": "Vertical 9:16 full-bleed moody miniature diorama in deep charcoal sepia #14110F. Macro still life of a single torn scrap of aged parchment #D9C7A7 hidden inside a dark tweed pocket seam with sepia folds #5A4A3F, bathed in golden amber light #FFB703. Over 65% calm negative space, lower 30% empty, zero text, zero readable letters, zero blue."
            },
            {
                "beat": 3,
                "role": "mechanism_turn",
                "prompt": "Vertical 9:16 full-bleed moody miniature diorama in deep charcoal sepia #14110F. An antique leather-bound poetry book in dark sepia #5A4A3F lying open on a wooden surface under warm amber lamplight #FFB703, showing where a final page was excised. Over 65% calm negative space, lower 30% clean, zero text, zero letters, zero blue."
            },
            {
                "beat": 4,
                "role": "mechanism_surge",
                "prompt": "Vertical 9:16 full-bleed moody miniature diorama in deep charcoal sepia #14110F. A vintage heavy black rotary telephone handset resting beside a cryptic handwritten cipher parchment #D9C7A7 in warm amber lamplight #FFB703 with sepia shadows #5A4A3F. Over 65% calm negative space, lower 30% simple, zero readable text, zero faces, zero blue."
            },
            {
                "beat": 5,
                "role": "payoff",
                "prompt": "Vertical 9:16 full-bleed moody miniature diorama in deep charcoal sepia #14110F. An empty desolate sandy beach shoreline at midnight bathed in a solitary golden amber lighthouse beam #FFB703, with quiet sepia dunes #5A4A3F and parchment foam #D9C7A7. Timeless enigma, over 70% calm dark negative space, lower 30% empty, zero text, zero blue."
            }
        ]
    },
    {
        "channel": "en-choke-point",
        "number": 10,
        "style_vi": "Bản đồ nổi giấy gân dập, tông da thuộc & đất, một lộ trình đỏ (Johnny Harris/RealLifeLore)",
        "palette": "#EADFC8 parchment beige, #A8B58F muted olive terrain, #C9A27E sandstone ridge, #C0392B crimson shipping route",
        "topic": "Strait of Hormuz chokepoint and global oil transit vulnerability",
        "beats": [
            {
                "beat": 1,
                "role": "hook",
                "prompt": "Vertical 9:16 full-bleed textured paper relief map on aged parchment #EADFC8. Two sculpted sandstone ridges #C9A27E and muted olive coastlines #A8B58F pinch together, separated by calm parchment water with one thin crimson route #C0392B. Elegant tactile shadows, over 65% calm negative space, lower 30% clean, zero text, zero labels, zero grids, zero blue."
            },
            {
                "beat": 2,
                "role": "mechanism_friction",
                "prompt": "Vertical 9:16 full-bleed textured paper relief map on aged parchment #EADFC8. Close-up of the narrow two-mile sea gap between steep sandstone bluffs #C9A27E and olive hills #A8B58F, traversed by a solitary dotted crimson shipping corridor #C0392B. Over 65% calm negative space, lower 30% empty, zero text, zero country names, zero grids, zero blue."
            },
            {
                "beat": 3,
                "role": "mechanism_turn",
                "prompt": "Vertical 9:16 full-bleed textured paper relief map on aged parchment #EADFC8. Stylized triangular paper watchtowers in sandstone #C9A27E guarding the jagged northern coastline with olive contours #A8B58F overlooking a single crimson sea route #C0392B. Tactile paper shadows, over 65% calm negative space, lower 30% clean, zero text, zero letters, zero blue."
            },
            {
                "beat": 4,
                "role": "mechanism_surge",
                "prompt": "Vertical 9:16 full-bleed textured paper relief map on aged parchment #EADFC8. A miniature stylized paper supertanker hull navigating the narrowest throat of water between sculpted cliffs #C9A27E along the crimson line #C0392B with olive shoreline #A8B58F. Over 65% calm negative space, lower 30% simple, zero text, zero labels, zero blue."
            },
            {
                "beat": 5,
                "role": "payoff",
                "prompt": "Vertical 9:16 full-bleed textured paper relief map on aged parchment #EADFC8. Macro view of a single red wax seal and knotted crimson thread #C0392B binding together two parchment landmasses #C9A27E and #A8B58F. Global chokepoint metaphor, over 70% calm negative space, lower 30% empty, zero text, zero letters, zero blue."
            }
        ]
    },
    {
        "channel": "en-root-and-canopy",
        "number": 11,
        "style_vi": "Màu nước thực vật học thưa thớt trên giấy kem (BBC Earth/In Defense of Plants)",
        "palette": "#F5EFE1 cream wash, #3F5E38 deep forest green, #5C4033 earthy bark brown, #D4A373 warm golden amber sap",
        "topic": "Mycorrhizal fungal networks sharing carbon and warnings between mother trees and saplings",
        "beats": [
            {
                "beat": 1,
                "role": "hook",
                "prompt": "Vertical 9:16 full-bleed sparse botanical watercolor on textured cream paper #F5EFE1. An ancient mother oak tree rendered with organic forest green foliage #3F5E38 and earthy bark #5C4033 with warm amber sap highlights #D4A373. Soft water blooms, over 65% calm negative space, lower 30% completely uncluttered, zero text, zero letters, zero blue, zero human figures."
            },
            {
                "beat": 2,
                "role": "mechanism_friction",
                "prompt": "Vertical 9:16 full-bleed sparse botanical watercolor on textured cream paper #F5EFE1. Delicate subterranean root system spreading underground in earthy brown #5C4033, entwined with fine golden amber fungal filaments #D4A373 and soft forest green moss #3F5E38. Over 65% calm negative space, lower 30% empty, zero text, zero letters, zero blue."
            },
            {
                "beat": 3,
                "role": "mechanism_turn",
                "prompt": "Vertical 9:16 full-bleed sparse botanical watercolor on textured cream paper #F5EFE1. Luminous droplets of amber sap #D4A373 traveling like organic light pulses along slender fungal threads between tree roots in brown #5C4033 and green #3F5E38. Over 65% calm negative space, lower 30% clean, zero text, zero letters, zero blue."
            },
            {
                "beat": 4,
                "role": "mechanism_surge",
                "prompt": "Vertical 9:16 full-bleed sparse botanical watercolor on textured cream paper #F5EFE1. A tender young sapling sprouting into life with vivid forest green leaves #3F5E38, nurtured by golden amber fungal strands #D4A373 reaching its tiny brown root #5C4033. Over 65% calm negative space, lower 30% simple, zero text, zero words, zero blue."
            },
            {
                "beat": 5,
                "role": "payoff",
                "prompt": "Vertical 9:16 full-bleed sparse botanical watercolor on textured cream paper #F5EFE1. Two trees of different heights in forest green #3F5E38 and bark brown #5C4033, connected beneath the cream ground by an elegant golden network loop #D4A373. Symbiotic harmony, over 70% calm negative space, lower 30% empty, zero text, zero blue."
            }
        ]
    },
    {
        "channel": "en-spawn-to-apex",
        "number": 12,
        "style_vi": "Nhiếp ảnh macro tự nhiên, bokeh ấm xanh rêu & hổ phách (Deep Look)",
        "palette": "#2E3B22 dark moss green, #A3B565 bright olive green, #F59E0B golden amber, #EDE3C8 soft cream highlight",
        "topic": "Dragonfly hunting success rate of 95% using predictive interception",
        "beats": [
            {
                "beat": 1,
                "role": "hook",
                "prompt": "Vertical 9:16 full-bleed natural macro photography with soft moss green background #2E3B22. A dragonfly head in razor-sharp focus showing iridescent olive facets #A3B565 and glowing golden amber reflections #F59E0B on a cream perch #EDE3C8. Soft shallow depth of field, over 65% calm negative space, lower 30% clean, zero text, zero graphics, zero blue."
            },
            {
                "beat": 2,
                "role": "mechanism_friction",
                "prompt": "Vertical 9:16 full-bleed natural macro photography with deep moss green bokeh #2E3B22. A tiny gnat in mid-flight with a subtle natural sunlight trail in golden amber #F59E0B and olive leaf reflections #A3B565 with cream highlight #EDE3C8. Over 65% calm negative space, lower 30% empty, zero text, zero hud overlays, zero blue."
            },
            {
                "beat": 3,
                "role": "mechanism_turn",
                "prompt": "Vertical 9:16 full-bleed natural macro photography with dark moss bokeh #2E3B22. The dragonfly launching from a reed with transparent wings glistening in golden amber light #F59E0B, angling its body along a predictive interception trajectory with olive highlights #A3B565. Over 65% calm negative space, lower 30% clean, zero text, zero blue."
            },
            {
                "beat": 4,
                "role": "mechanism_surge",
                "prompt": "Vertical 9:16 full-bleed natural macro photography with dark moss green bokeh #2E3B22. The apex predator's spiny olive legs #A3B565 snapping shut in mid-air to capture prey, bathed in dramatic golden amber side sunlight #F59E0B and cream glint #EDE3C8. Over 65% calm negative space, lower 30% simple, zero text, zero graphics, zero blue."
            },
            {
                "beat": 5,
                "role": "payoff",
                "prompt": "Vertical 9:16 full-bleed natural macro photography with soft moss green blur #2E3B22. The dragonfly resting poised on a solitary vertical cream reed #EDE3C8, with amber veined wings #F59E0B catching morning rays and bright olive thorax #A3B565. Sovereign predator stillness, over 70% negative space, lower 30% empty, zero text, zero blue."
            }
        ]
    },
    {
        "channel": "en-second-arrow",
        "number": 13,
        "style_vi": "Điêu khắc đá cẩm thạch, chiaroscuro ấm trên nền đen than chì (Daily Stoic)",
        "palette": "#0F0E0D charcoal black void, #EAE8E3 antique Carrara marble, #C9A96E warm golden amber light",
        "topic": "How reacting with anger or self-pity creates the second, unnecessary arrow of suffering",
        "beats": [
            {
                "beat": 1,
                "role": "hook",
                "prompt": "Vertical 9:16 full-bleed classical marble sculpture illustration on deep charcoal void #0F0E0D. A stoic Roman marble bust carved from antique Carrara stone #EAE8E3 is struck in the shoulder by a simple wooden arrow, bathed in directional golden light #C9A96E. Intense chiaroscuro, over 70% negative black space, lower 30% empty, zero text, zero blue, zero panic."
            },
            {
                "beat": 2,
                "role": "mechanism_friction",
                "prompt": "Vertical 9:16 full-bleed classical marble sculpture illustration on deep charcoal void #0F0E0D. Dramatic chiaroscuro close-up: from the distorted jagged shadow of the marble statue #EAE8E3 emerges a menacing second splintered arrow aimed at its own chest, lit by golden amber rays #C9A96E. Over 70% negative black space, lower 30% empty, zero text, zero blue."
            },
            {
                "beat": 3,
                "role": "mechanism_turn",
                "prompt": "Vertical 9:16 full-bleed classical marble sculpture illustration on deep charcoal void #0F0E0D. Profile of the Roman marble philosopher head #EAE8E3 showing absolute serene composure in warm golden chiaroscuro light #C9A96E, while the illusory shadowy storm of arrows dissolves into darkness. Over 70% negative space, lower 30% clean, zero text, zero blue."
            },
            {
                "beat": 4,
                "role": "mechanism_surge",
                "prompt": "Vertical 9:16 full-bleed classical marble sculpture illustration on deep charcoal void #0F0E0D. A powerful chiseled marble forearm #EAE8E3 reaches into the warm golden beam #C9A96E, effortlessly catching the incoming second arrow in mid-flight before it strikes. Sovereign composure, over 70% negative black space, lower 30% simple, zero text, zero blue."
            },
            {
                "beat": 5,
                "role": "payoff",
                "prompt": "Vertical 9:16 full-bleed classical marble sculpture illustration on deep charcoal void #0F0E0D. A flawless polished marble sphere #EAE8E3 resting peacefully on a stone pedestal in a solitary warm amber spotlight #C9A96E, while broken arrows lie harmlessly around it. Stoic equanimity, over 75% negative black space, lower 30% empty, zero text, zero blue."
            }
        ]
    },
    {
        "channel": "en-bamboo-marble",
        "number": 14,
        "style_vi": "Tranh khắc gỗ ukiyo-e trên giấy washi, phong cách thưa thớt (Philosophies for Life)",
        "palette": "#F2EBD9 warm washi paper, #2D5A3A bamboo green, #8B6F47 driftwood brown, #C99E32 muted gold, #3E4E59 subtle indigo accent",
        "topic": "Chuang Tzu parable of the empty boat and letting go of anger",
        "beats": [
            {
                "beat": 1,
                "role": "hook",
                "prompt": "Vertical 9:16 full-bleed sparse ukiyo-e woodblock print on warm fibrous washi paper #F2EBD9. A solitary rustic wooden rowboat #8B6F47 drifts through gentle mist with subtle bamboo green #2D5A3A and muted gold #C99E32 accents. Minimalist woodcut lines, over 70% calm negative space, lower 30% completely empty, zero text, zero letters, zero busy waves, zero blue."
            },
            {
                "beat": 2,
                "role": "mechanism_friction",
                "prompt": "Vertical 9:16 full-bleed sparse ukiyo-e woodblock print on warm fibrous washi paper #F2EBD9. Two wooden boats in driftwood brown #8B6F47 colliding softly in foggy water, with delicate ripples and muted gold accents #C99E32 and faint indigo shadow #3E4E59. Over 70% calm negative space, lower 30% empty, zero text, zero letters, zero blue."
            },
            {
                "beat": 3,
                "role": "mechanism_turn",
                "prompt": "Vertical 9:16 full-bleed sparse ukiyo-e woodblock print on warm fibrous washi paper #F2EBD9. A close view of the colliding boat in brown #8B6F47, revealing completely empty wooden benches, no oarsman inside, with bamboo green accents #2D5A3A and muted gold #C99E32. Over 70% calm negative space, lower 30% clean, zero text, zero letters, zero blue."
            },
            {
                "beat": 4,
                "role": "mechanism_surge",
                "prompt": "Vertical 9:16 full-bleed sparse ukiyo-e woodblock print on warm fibrous washi paper #F2EBD9. A stylized Eastern sage silhouette in bamboo green robes #2D5A3A bowing toward the empty boat with quiet realization, touched by muted gold mist #C99E32. Over 70% calm negative space, lower 30% simple, zero text, zero words, zero blue."
            },
            {
                "beat": 5,
                "role": "payoff",
                "prompt": "Vertical 9:16 full-bleed sparse ukiyo-e woodblock print on warm fibrous washi paper #F2EBD9. A single slender bamboo stalk in deep green #2D5A3A bending gracefully over still water, with muted gold reflections #C99E32 and brown bank #8B6F47. Serene non-resistance, over 75% calm negative space, lower 30% empty, zero text, zero blue."
            }
        ]
    },
    {
        "channel": "en-kindred-sketch",
        "number": 15,
        "style_vi": "Tranh bột màu gouache biên tập ấm áp trên giấy kem (School of Life)",
        "palette": "#F5EFEB soft warm cream, #C8644A terracotta coral, #D4A359 warm ochre, #4A6B5D muted sage",
        "topic": "Attachment theory: how intimacy triggers fear of engulfment in avoidant partners",
        "beats": [
            {
                "beat": 1,
                "role": "hook",
                "prompt": "Vertical 9:16 full-bleed warm editorial gouache illustration on soft cream #F5EFEB. A stylized solitary figure in muted sage #4A6B5D sits quietly beside a terracotta coral chair #C8644A with warm ochre highlights #D4A359. Gentle painterly textures, over 65% calm negative space, lower 30% clean, zero text, zero words, zero blue, stylized featureless face."
            },
            {
                "beat": 2,
                "role": "mechanism_friction",
                "prompt": "Vertical 9:16 full-bleed warm editorial gouache illustration on soft cream #F5EFEB. A warm ochre thread #D4A359 reaches gently toward a solitary figure, while a delicate terracotta bell jar #C8644A lowers to shelter them, with sage accents #4A6B5D. Over 65% calm negative space, lower 30% empty, zero text, zero letters, zero blue."
            },
            {
                "beat": 3,
                "role": "mechanism_turn",
                "prompt": "Vertical 9:16 full-bleed warm editorial gouache illustration on soft cream #F5EFEB. A stylized wooden birdcage in warm ochre #D4A359 resting on a table with its door swung wide open, revealing a peaceful terracotta flower inside #C8644A with sage leaves #4A6B5D. Over 65% calm negative space, lower 30% clean, zero text, zero blue."
            },
            {
                "beat": 4,
                "role": "mechanism_surge",
                "prompt": "Vertical 9:16 full-bleed warm editorial gouache illustration on soft cream #F5EFEB. The protective glass bell jar gracefully dissolving into floating sage leaves #4A6B5D as warm ochre sunlight #D4A359 warms the terracotta figure #C8644A in open air. Over 65% calm negative space, lower 30% simple, zero text, zero words, zero blue."
            },
            {
                "beat": 5,
                "role": "payoff",
                "prompt": "Vertical 9:16 full-bleed warm editorial gouache illustration on soft cream #F5EFEB. Two stylized minimalist figures in sage #4A6B5D and terracotta #C8644A standing side by side in generous space, connected by a shared warm ochre shadow #D4A359 on the floor. Autonomous connection, over 70% negative space, lower 30% empty, zero text, zero blue."
            }
        ]
    },
    {
        "channel": "en-lazy-brain",
        "number": 16,
        "style_vi": "Nguệch ngoạc bút dạ trên sổ phác thảo trắng ngà, nét tối giản (Better Than Yesterday/After Skool)",
        "palette": "#FAF7F0 sketchbook off-white, #222222 charcoal marker ink, #F2A541 warm marigold yellow, #E76F51 terracotta marker",
        "topic": "Variable reward schedule and dopamine spikes during infinite feed scrolling",
        "beats": [
            {
                "beat": 1,
                "role": "hook",
                "prompt": "Vertical 9:16 full-bleed playful felt-tip marker doodle on off-white sketchbook paper #FAF7F0. A simple minimalist smartphone outline drawn in loose charcoal marker #222222 with three warm marigold yellow rays #F2A541 and terracotta accents #E76F51. Bold expressive strokes, over 65% calm negative space, lower 30% empty, zero text, zero letters, zero grids, zero blue."
            },
            {
                "beat": 2,
                "role": "mechanism_friction",
                "prompt": "Vertical 9:16 full-bleed playful felt-tip marker doodle on off-white sketchbook paper #FAF7F0. A stylized brain silhouette drawn in loose charcoal marker #222222 functioning like a three-reel slot machine with bold marigold #F2A541 and terracotta icons #E76F51. Over 65% calm negative space, lower 30% clean, zero text, zero numbers, zero blue."
            },
            {
                "beat": 3,
                "role": "mechanism_turn",
                "prompt": "Vertical 9:16 full-bleed playful felt-tip marker doodle on off-white sketchbook paper #FAF7F0. A dynamic line graph sketched in loose charcoal #222222 showing a dramatic spike drawn with bright marigold #F2A541 and terracotta marker #E76F51 before dropping flat. Over 65% calm negative space, lower 30% empty, zero text, zero letters, zero blue."
            },
            {
                "beat": 4,
                "role": "mechanism_surge",
                "prompt": "Vertical 9:16 full-bleed playful felt-tip marker doodle on off-white sketchbook paper #FAF7F0. An infinite vertical ribbon drawn in charcoal ink #222222 scrolling downward like paper tape, dotted with marigold sparks #F2A541 and terracotta #E76F51. Over 65% calm negative space, lower 30% simple, zero text, zero letters, zero blue."
            },
            {
                "beat": 5,
                "role": "payoff",
                "prompt": "Vertical 9:16 full-bleed playful felt-tip marker doodle on off-white sketchbook paper #FAF7F0. A single closed sketchbook resting beside a steaming ceramic coffee mug drawn in simple charcoal marker #222222 with warm marigold steam #F2A541 and terracotta shadow #E76F51. Calm offline peace, over 70% negative space, lower 30% empty, zero text, zero blue."
            }
        ]
    },
    {
        "channel": "en-career-leverage",
        "number": 17,
        "style_vi": "Nhiếp ảnh tĩnh vật biên tập, gỗ sồi ấm & đồng thau, ánh sáng ban ngày (HBR/WSJ)",
        "palette": "#EDE4D3 linen cream, #2C1D11 dark walnut wood, #D4A017 polished brass, #8A6E4B warm leather tan",
        "topic": "The Competence Penalty: Why top performers get trapped in tactical execution instead of being promoted",
        "beats": [
            {
                "beat": 1,
                "role": "hook",
                "prompt": "Vertical 9:16 full-bleed editorial still-life photography on cream linen #EDE4D3. A polished brass chess knight #D4A017 rests on a dark walnut wood pedestal #2C1D11 beside warm leather tan bookbinding #8A6E4B. Soft natural side daylight, shallow depth of field, over 65% calm negative space, lower 30% clean, zero text, zero letters, zero blue."
            },
            {
                "beat": 2,
                "role": "mechanism_friction",
                "prompt": "Vertical 9:16 full-bleed editorial still-life photography on cream linen #EDE4D3. A delicate brass gear assembly #D4A017 bound tightly by leather cords #8A6E4B to a heavy dark walnut wooden block #2C1D11, locked in place. Soft daylight, over 65% calm negative space, lower 30% empty, zero text, zero letters, zero blue."
            },
            {
                "beat": 3,
                "role": "mechanism_turn",
                "prompt": "Vertical 9:16 full-bleed editorial still-life photography on cream linen #EDE4D3. A miniature dark walnut ladder #2C1D11 leaning against an open door, with lower rungs crowded while the top brass rung #D4A017 catches pure sunlight with leather tan accents #8A6E4B. Over 65% calm negative space, lower 30% clean, zero text, zero blue."
            },
            {
                "beat": 4,
                "role": "mechanism_surge",
                "prompt": "Vertical 9:16 full-bleed editorial still-life photography on cream linen #EDE4D3. A solid brass key #D4A017 resting beside a set of tall double doors carved from dark walnut #2C1D11 opening toward soft morning daylight with leather tan threshold #8A6E4B. Over 65% calm negative space, lower 30% simple, zero text, zero blue."
            },
            {
                "beat": 5,
                "role": "payoff",
                "prompt": "Vertical 9:16 full-bleed editorial still-life photography on cream linen #EDE4D3. A solitary vintage brass nautical compass #D4A017 resting centered on an immaculate dark walnut tabletop #2C1D11 with warm leather accents #8A6E4B. Strategic clarity and sovereign direction, over 70% negative space, lower 30% empty, zero text, zero blue."
            }
        ]
    },
    {
        "channel": "en-wallet-anatomy",
        "number": 18,
        "style_vi": "Tranh cắt giấy xếp lớp trên bìa cứng ngà (PBS Two Cents)",
        "palette": "#FAF6E9 ivory cardstock, #2E7D32 forest green paper, #D97706 warm amber paper, #722F37 burgundy wine paper",
        "topic": "Why Restaurants Put Their Highest Markups on the Second-Cheapest Wine",
        "beats": [
            {
                "beat": 1,
                "role": "hook",
                "prompt": "Vertical 9:16 full-bleed layered paper-cut illustration on ivory cardstock #FAF6E9. Three silhouetted paper bottles with crisp drop shadows: two forest green #2E7D32 and one prominent burgundy paper bottle #722F37 with warm amber accents #D97706. Tactile layered paper craft, over 65% calm negative space, lower 30% clean, zero text, zero numbers, zero blue."
            },
            {
                "beat": 2,
                "role": "mechanism_friction",
                "prompt": "Vertical 9:16 full-bleed layered paper-cut illustration on ivory cardstock #FAF6E9. A stylized layered paper restaurant menu folding open, with a warm amber paper beam #D97706 spotlighting a burgundy paper bottle silhouette #722F37 against forest green layers #2E7D32. Over 65% calm negative space, lower 30% empty, zero text, zero numbers, zero blue."
            },
            {
                "beat": 3,
                "role": "mechanism_turn",
                "prompt": "Vertical 9:16 full-bleed layered paper-cut illustration on ivory cardstock #FAF6E9. A delicate paper-cut balance scale where a tiny burgundy wine bottle #722F37 heavily outweighs a giant stack of golden amber paper coins #D97706 with forest green accents #2E7D32. Over 65% calm negative space, lower 30% clean, zero text, zero blue."
            },
            {
                "beat": 4,
                "role": "mechanism_surge",
                "prompt": "Vertical 9:16 full-bleed layered paper-cut illustration on ivory cardstock #FAF6E9. A stylized paper bottle with its cork popping in crisp relief, spraying droplets of warm amber paper #D97706 and rich burgundy wine droplets #722F37 over green #2E7D32. Over 65% calm negative space, lower 30% simple, zero text, zero letters, zero blue."
            },
            {
                "beat": 5,
                "role": "payoff",
                "prompt": "Vertical 9:16 full-bleed layered paper-cut illustration on ivory cardstock #FAF6E9. A single elegant paper-cut wine goblet casting a crisp burgundy paper shadow #722F37 beside a single green grapevine leaf #2E7D32 and amber drop #D97706. Refined consumer wisdom, over 70% calm negative space, lower 30% empty, zero text, zero blue."
            }
        ]
    }
]

def verify_and_save_prompts():
    for ch_data in CHANNELS_DATA:
        ch = ch_data["channel"]
        run_dir = Path("sys/runs") / f"{ch}-style-v2"
        images_dir = run_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        
        # Save prompts.json
        prompts_file = run_dir / "prompts.json"
        prompts_file.write_text(json.dumps(ch_data, ensure_ascii=False, indent=2))
        
        for b in ch_data["beats"]:
            p = b["prompt"]
            words = p.split()
            assert len(words) <= 70, f"{ch} beat {b['beat']} prompt has {len(words)} words > 70: {p}"
            # Check for hex colors
            assert "#" in p, f"{ch} beat {b['beat']} missing hex color: {p}"
            # Check for forbidden keywords
            for forbidden in ["blue", "navy", "teal", "grid", "graph paper", "hud", "neon"]:
                # Note: "zero blue" is allowed
                if forbidden in p.lower() and f"zero {forbidden}" not in p.lower() and f"no {forbidden}" not in p.lower():
                    print(f"WARNING: forbidden keyword '{forbidden}' in {ch} beat {b['beat']}: {p}")

    print("All 18 channels and 90 prompts verified and written to prompts.json!")

if __name__ == "__main__":
    verify_and_save_prompts()
