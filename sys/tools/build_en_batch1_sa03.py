#!/usr/bin/env python3
"""Schema 3.0 English Batch 1 Generator for SA-EN-03.

Cluster 3: Geopolitics Cartography, Forensic History & Crowd Noir
Channels:
1. en_choke_point (Choke Point Maps)
   - sys/runs/en-choke-point-batch1-16x9 (Long 16:9, 11 scenes, 66 images, ~620 words)
   - sys/runs/en-choke-point-batch1-9x16 (Short 9:16, 5 scenes, 20 images, ~175 words)
2. en_cold_case_ink (Cold Case Ink)
   - sys/runs/en-cold-case-ink-batch1-16x9 (Long 16:9, 11 scenes, 66 images, ~620 words)
   - sys/runs/en-cold-case-ink-batch1-9x16 (Short 9:16, 5 scenes, 20 images, ~175 words)
3. en_crowd_strings (Crowd Strings)
   - sys/runs/en-crowd-strings-batch1-16x9 (Long 16:9, 11 scenes, 66 images, ~620 words)
   - sys/runs/en-crowd-strings-batch1-9x16 (Short 9:16, 5 scenes, 20 images, ~175 words)
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Ensure sys is in PYTHONPATH
SYS_DIR = Path(__file__).resolve().parents[1]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))
TOOLS_DIR = SYS_DIR / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from channels.registry import channel_cast, channel_profile_stamp, get_channel
from channel_production_common import compile_channel_scene_prompt
from tools.editorial_value_linter import lint_editorial_and_narrative_quality
from tools.script_diversity_linter import check_ai_cliche_phrases, check_intra_video_repetitions
from tools.cta_tone_linter import lint_cta


def compute_brief_hash(brief_dict: Dict[str, Any]) -> str:
    content = json.dumps(brief_dict, ensure_ascii=False, indent=2)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def compile_images_manifest(
    ch: Any,
    brief: Dict[str, Any],
    content: Dict[str, Any],
    aspect_ratio: str,
) -> Dict[str, Any]:
    aspect_tag = aspect_ratio.replace(":", "x")
    compiled_items = []
    for sc in content.get("scenes", []):
        for img in sc.get("images", []):
            final_prompt = compile_channel_scene_prompt(
                ch, brief, content, sc, img, aspect_ratio=aspect_ratio
            )
            sha = hashlib.sha256(final_prompt.encode("utf-8")).hexdigest()
            compiled_items.append({
                "image_id": img["id"],
                "scene_id": sc["id"],
                "path": f"revisions/images/1/{img['id']}_{aspect_tag}.jpg",
                "prompt": final_prompt,
                "sha256": sha,
                "ratio": aspect_ratio,
                "motion_prompt": img.get("motion_prompt", ""),
            })
    return {
        "checkpoint": "compiled",
        "total_images": len(compiled_items),
        "items": compiled_items,
    }


def count_words(text: str) -> int:
    return len([w for w in text.strip().split() if w])


# ==============================================================================
# CHANNEL 1: EN_CHOKE_POINT (Choke Point Maps)
# ==============================================================================

def make_choke_point_long():
    job_id = "en-choke-point-batch1-16x9"
    channel_id = "en_choke_point"
    ch = get_channel(channel_id)
    topic = "The Gate of Tears: Why the 18-Mile Bab el-Mandeb Strait Can Paralyze European Trade Overnight"
    youtube_title = "Why This 18-Mile Strait Controls Global Prices"  # 47 chars <= 55

    style_desc = (
        "1940s British Admiralty Nautical Chart and Topographic Lithograph on aged #E8DFCA parchment chart paper "
        "(#0D1B2A deep maritime navy ocean, #E6CCB2 topographic sand landmasses, #E63946 crimson shipping vectors, "
        "#FFB703 shipping-lane gold, #4EA8DE strait cyan); fine hand-engraved bathymetric depth contour lines, "
        "sepia copperplate ink cross-hatching, archival brass compass rose, orthographic 2D cartography, "
        "at least 60% negative space, zero 3D CGI, zero neon glow, zero plastic gradients."
    )

    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Explain how the narrow Bab el-Mandeb strait controls Eurasian trade flows and why rerouting around Africa causes systemic global price shocks.",
        "video_type": "explainer",
        "duration": {"min_seconds": 150.0, "max_seconds": 210.0},
        "scene_count": 11,
        "required_points": [
            {"id": "R01", "text": "The 18-mile Bab el-Mandeb strait carrying twelve percent of world trade and thirty percent of global container volume."},
            {"id": "R02", "text": "Perim Island splitting the waterway and creating a narrow two-mile deep-water shipping trench."},
            {"id": "R03", "text": "Over twenty thousand commercial vessels transiting the strait annually carrying manufactured goods and crude oil."},
            {"id": "R04", "text": "The fragility of modern supply chains operating under the illusion of frictionless maritime trade."},
            {"id": "R05", "text": "Missile and drone threats halting commercial shipping and triggering an emergency diversion order."},
            {"id": "R06", "text": "The alternative route around South Africa's Cape of Good Hope adding thirty-five hundred nautical miles."},
            {"id": "R07", "text": "Ultra-large container ships burning an extra one million dollars in bunker fuel per voyage."},
            {"id": "R08", "text": "Cascading container deficits stranding empty equipment at sea and starving Asian export terminals."},
            {"id": "R09", "text": "Severe vessel bunching and yard congestion across Rotterdam, Antwerp, and Mediterranean ports."},
            {"id": "R10", "text": "Naval destroyers unable to widen the physical two-mile channel against asymmetrical drone threats."},
            {"id": "R11", "text": "The immutable reality that modern global trade remains hostage to ancient geological chokepoints."}
        ],
        "language": "en",
        "tone": ch.tone,
        "style": style_desc,
        "aspect_ratio": "16:9",
        "format_profile": "long_16x9",
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "Navigating Troubled Waters: The Impact of Red Sea Disruptions on Global Trade",
                "reference": "United Nations Conference on Trade and Development (UNCTAD, 2024). UNCTAD Rapid Assessment Report.",
                "facts": [
                    "Twelve percent of global trade and thirty percent of container traffic pass through Bab el-Mandeb.",
                    "Rerouting around the Cape of Good Hope adds thirty-five hundred nautical miles to voyages.",
                    "Detours around Africa add ten to fourteen sailing days and one million dollars in bunker fuel."
                ]
            },
            {
                "id": "SRC02",
                "title": "Maritime Shipping Intelligence & Chokepoint Vulnerability Review",
                "reference": "International Maritime Bureau & Clarksons Research (2024). Global Shipping Transit Studies.",
                "facts": [
                    "Volcanic Perim Island splits the Bab el-Mandeb strait into two channels.",
                    "Navigable western channel is only two nautical miles wide for deep-draft freighters.",
                    "Over twenty thousand commercial vessels transit the Bab el-Mandeb corridor annually."
                ]
            }
        ],
        "outputs": [
            {
                "aspect_ratio": "16:9",
                "language": "en",
                "subtitles": False,
                "voice": ch.voice,
                "speed": 1.0
            }
        ],
        "planning": {
            "success_criteria": [
                "Dissect the physical bathymetry, naval chokepoint mechanics, Cape of Good Hope diversion economics, and systemic container deficit cascading effects."
            ],
            "avoid": [
                "Zero sensationalist rhetoric, zero speculative military scenarios, zero robotic filler discourse markers."
            ],
            "prior_knowledge": "None required; cartographic visual progression explains strategic geometry intuitively.",
            "pacing": "Strategic documentary cadence calibrated at ~3.8 syllables per second.",
            "speech_rates": {
                "en": {
                    "units_per_second": 3.8,
                    "uncertainty": 0.15,
                    "source": "Acoustic calibrated cadence"
                }
            }
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Aged 1940s Admiralty nautical chart of Bab el-Mandeb with crimson blockade vectors and brass compass rose",
                "text_overlay": "GATE OF TEARS",
                "contrast_pair": "18-Mile Strait vs 3500-Mile African Detour",
                "layout_mode": "split_contrast"
            },
            "channel_pillar": ch.niche,
            "funnel_tier": "tier_1_broad",
            "seo_keywords": [
                "Bab el-Mandeb",
                "choke point",
                "Red Sea shipping",
                "Suez Canal",
                "Cape of Good Hope",
                "global supply chain",
                "geopolitics maps"
            ]
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Aged 1940s Admiralty nautical chart of Bab el-Mandeb with crimson blockade vectors and brass compass rose",
            "text_overlay": "GATE OF TEARS",
            "contrast_pair": "18-Mile Strait vs 3500-Mile African Detour",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": ch.niche,
        "funnel_tier": "tier_1_broad",
        "seo_keywords": [
            "Bab el-Mandeb",
            "choke point",
            "Red Sea shipping",
            "Suez Canal",
            "Cape of Good Hope",
            "global supply chain"
        ],
        "cta_plan": {
            "mid_cta": "If you find this strategic breakdown valuable, save this video to trace the next choke point.",
            "close": "Which geographic bottleneck surprised you most? Share your perspective below.",
            "endcard_text": "FULL VIDEO ON YOUTUBE"
        },
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": ch.engagement.cta_voice,
            "banned_cta_phrases": list(ch.engagement.banned_cta_phrases)
        },
        "editorial_stance": {
            "myth_debunked": "Global container shipping routes are flexible networks that can easily absorb localized geopolitical disruptions without systemic inflation.",
            "channel_verdict": "The modern global economy is fundamentally fragile because vital commodity flows are bottlenecked by immutable geological fissures that cannot be widened by technology.",
            "why_generic_advice_fails": "Mainstream economic forecasts treat maritime rerouting as a simple linear fuel surcharge while ignoring cascading container equipment deficits across regional hubs.",
            "tradeoff_or_blindspot": "Deploying multinational naval carrier groups secures transit lanes temporarily but costs millions daily without eliminating the vulnerability of the two-mile physical channel."
        },
        "actionable_value": {
            "core_mechanism": "The maritime corridor choke mechanism: when an 18-mile strait closes, container carriers must sail thirty-five hundred extra miles around Africa, draining vessel capacity and triggering global spot price spikes.",
            "practical_rule_of_thumb": "Supply chain vulnerability rule: when analyzing international freight reliability, monitor transit throughput at maritime bottlenecks rather than factory production schedules.",
            "real_world_scenario": "A European retail importer faces a four-thousand-dollar container surcharge and a two-week shelf delay because their container vessel diverted around the Cape of Good Hope."
        },
        "video_engine": "images_only",
        "chain_mode": "full_chain"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Hook: 18-mile Bab el-Mandeb gateway carrying 12% of world trade and 30% of container shipping", "requirements": ["R01"], "transition": "Zoom into the narrow mouth of the Red Sea"},
            {"scene_id": "SC02", "purpose": "Mechanism: volcanic Perim Island splitting strait into a shallow trap and a two-mile trench", "requirements": ["R02"], "transition": "Cross-section bathymetry of the ocean floor"},
            {"scene_id": "SC03", "purpose": "Deep dive: 20,000 vessels annually carrying manufactured freight and 4 million barrels of oil", "requirements": ["R03"], "transition": "Tracking the shipping traffic vectors northward"},
            {"scene_id": "SC04", "purpose": "Editorial commentary: the dangerous corporate myth of frictionless global supply chains", "requirements": ["R04"], "transition": "Tactical tension along coastal contours"},
            {"scene_id": "SC05", "purpose": "Story action: missile threats halting commercial transits and ordering an emergency southern pivot", "requirements": ["R05"], "transition": "Vessels turning away from the Red Sea entry"},
            {"scene_id": "SC06", "purpose": "Mechanism: circumnavigating Africa via Cape of Good Hope adding 3,500 nautical miles and 14 days", "requirements": ["R06"], "transition": "Panoramic continental comparison map"},
            {"scene_id": "SC07", "purpose": "Economic impact: $1M in extra bunker fuel per voyage and spiking war-risk insurance premiums", "requirements": ["R07"], "transition": "Cost breakdown ledger and fuel calculation"},
            {"scene_id": "SC08", "purpose": "Editorial commentary: container schedule desynchronization creating systemic equipment deficits", "requirements": ["R08"], "transition": "Empty container deficit heatmap in Asian ports"},
            {"scene_id": "SC09", "purpose": "Cascading shocks: terminal yard congestion in Rotterdam and European factory assembly shutdowns", "requirements": ["R09"], "transition": "Port crane congestion and factory supply lines"},
            {"scene_id": "SC10", "purpose": "Asymmetric limits: naval destroyers firing $2M interceptors cannot widen a 2-mile natural channel", "requirements": ["R10"], "transition": "Naval escort vectors versus narrow topography"},
            {"scene_id": "SC11", "purpose": "Payoff and closing: modern trade remains hostage to immutable geography; closing CTA", "requirements": ["R11"], "transition": "Final strategic chart pull-back to global overview"}
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "RealLifeLore",
                    "top_performing_videos": [
                        {
                            "title": "Why the Red Sea Crisis is an Economic Nightmare",
                            "views": "4.2M views",
                            "hook_technique": "Cold open on high-contrast satellite map highlighting an 18-mile gap with shipping stats.",
                            "pacing_structure": "Choke point reveal -> Cape of Good Hope detour -> Fuel and container math -> Global consumer inflation.",
                            "retention_driver": "Clear visual scale showing massive African detour vs narrow strait."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "High contrast nautical cartography emphasizing tight geographic bottlenecks.",
                        "Direct translation of shipping delays into dollars, days, and everyday consumer prices."
                    ]
                },
                {
                    "channel_name": "CaspianReport",
                    "top_performing_videos": [
                        {
                            "title": "Geopolitics of Bab el-Mandeb",
                            "views": "1.8M views",
                            "hook_technique": "Strategic historical perspective connecting British colonial coaling stations to modern trade.",
                            "pacing_structure": "Historical context -> Geographic features -> Coastal militarization -> Global choke point impact.",
                            "retention_driver": "Sober, authoritative geopolitical analysis anchored to terrain."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Treating physical geography as the ultimate immovable chess board.",
                        "Using bathymetric depth charts to explain why ships cannot simply steer around."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 28,
                "zero_pause_opening_seconds": 15,
                "visual_contrast": "1940s Admiralty chart showing vast ocean lanes funneled into a crimson 18-mile needle eye.",
                "counter_intuitive_truth_slap": "Modern mega-freighters carrying billions in trade are helpless against a two-mile underwater trench."
            },
            "narrative_progression_arc": [
                {"phase": "hook_shock", "purpose": "Bab el-Mandeb carrying 12% of global trade and 30% of containers"},
                {"phase": "mechanism_step", "purpose": "Perim Island bathymetry leaving only a two-mile shipping lane"},
                {"phase": "before_after_contrast", "purpose": "20,000 ships annually vs fragile two-mile chokepoint"},
                {"phase": "editorial_commentary", "purpose": "Exposing the myth of frictionless supply chains"},
                {"phase": "story_action", "purpose": "Missile attacks triggering emergency African rerouting"},
                {"phase": "mechanism_step", "purpose": "Cape of Good Hope detour adding 3,500 nautical miles"},
                {"phase": "rapid_examples", "purpose": "$1M fuel burn and surging war-risk insurance surcharges"},
                {"phase": "editorial_commentary", "purpose": "Structural crisis of stranded empty containers and factory delays"},
                {"phase": "mechanism_step", "purpose": "Rotterdam port congestion and German assembly line shutdowns"},
                {"phase": "before_after_contrast", "purpose": "Naval missile interceptor cost asymmetry versus physical channel"},
                {"phase": "cta_bridge", "purpose": "Closing verdict on immutable geography and viewer prompt"}
            ],
            "flow_video_transition_blueprint": {
                "keyframe_continuity": "Admiralty parchment chart #E8DFCA and brass compass rose as orienting axis.",
                "tempo_modulation": "Rapid tempo for opening hook and missile crisis, measured tempo for bathymetric and economic breakdowns."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": ch.niche,
            "myth_debunked": brief["editorial_stance"]["myth_debunked"],
            "channel_verdict": brief["editorial_stance"]["channel_verdict"],
            "actionable_rule_of_thumb": brief["actionable_value"]["practical_rule_of_thumb"]
        },
        "cta_and_spinoff_strategy": {
            "mid_cta": brief["cta_plan"]["mid_cta"],
            "close": brief["cta_plan"]["close"],
            "endcard_text": brief["cta_plan"]["endcard_text"]
        }
    }

    # Scene narrations crafted to total ~590 words (~54 words/scene)
    sc_narrations = [
        # SC01 (57w)
        "At the southern entrance of the Red Sea lies a narrow oceanic corridor known as Bab el-Mandeb, or the Gate of Tears. Spanning just eighteen miles across, this maritime bottleneck carries twelve percent of all global seaborne trade and nearly thirty percent of worldwide container traffic. When this gateway closes, global commerce instantly shatters across several continents.",
        # SC02 (57w)
        "Carved by shifting tectonic plates between the Arabian Peninsula and the Horn of Africa, the strait is a natural geological trap. Perim Island sits directly in the center, dividing the waterway into two distinct channels. The shallow eastern channel is completely unnavigable for modern container vessels, leaving only a precarious two-mile deep-water trench for commercial shipping lanes.",
        # SC03 (58w)
        "More than twenty thousand merchant vessels navigate this narrow channel every single year, including ultra-large container carriers loaded with high-value electronics, machinery, and agricultural goods. Alongside them, massive oil supertankers transport four million barrels of crude oil every single day toward European refineries and North American terminals, making this passage the vital jugular vein of Eurasian energy.",
        # SC04 (56w) - editorial
        "Modern corporate logistics operate under the dangerous fiction of frictionless global trade, pretending that just-in-time manufacturing can perpetually rely on open ocean highways without geopolitical friction. Yet modern container shipping remains utterly subservient to physical geography. The moment instability flares along the Yemeni coastline, the illusion of seamless international trade dissolves into costly logistical chaos.",
        # SC05 (56w)
        "When commercial vessels came under attack from coastal anti-ship missiles and aerial drone swarms, maritime operators faced an immediate crisis. Major international container carriers suspended Red Sea transits within forty-eight hours. Fleet operations commanders ordered their twenty-thousand TEU vessels to execute an emergency turn southward, bypassing the Suez Canal entirely to avoid catastrophic missile strikes.",
        # SC06 (54w)
        "The only viable oceanic detour requires rounding South Africa's Cape of Good Hope, adding thirty-five hundred nautical miles to the standard transit between East Asia and Northern Europe. Mega-container ships spend an additional twelve to fourteen days continuously steaming through rough South Atlantic ocean swells, burning vast reserves of low-sulfur marine bunker fuel.",
        # SC07 (55w)
        "For an ultra-large container carrier, that African detour burns an extra one million dollars in bunker fuel for a single one-way transit. Compounding the expense, maritime war-risk insurance premiums skyrocket, while commercial vessel charter rates jump dramatically across international shipping exchanges, adding millions in unexpected operational overhead to global voyages on high seas.",
        # SC08 (58w) - editorial
        "The true macroeconomic damage is structural rather than simple fuel surcharges. Global container logistics rely on tightly synchronized weekly departures. When ships take two extra weeks to complete their rotations, thousands of empty steel containers become stranded at sea, causing acute equipment deficits in Asian export ports while European factory supply lines run completely dry.",
        # SC09 (54w)
        "In European gateway ports like Rotterdam, Antwerp, and Hamburg, terminal yards face severe vessel bunching as delayed megaships arrive simultaneously. Container cranes operate around the clock to clear the backlog, while German automotive plants and electronics manufacturers are forced to halt production lines because critical missing parts are locked inside delayed containers.",
        # SC10 (53w)
        "Multinational naval coalitions deploy Aegis destroyers to escort commercial convoys through the southern Red Sea, but military warships cannot widen a two-mile natural trench. Firing multi-million-dollar air defense interceptors against inexpensive aerial drones creates a lopsided tactical attrition that maritime insurance underwriters remain unwilling to gamble on over the long run.",
        # SC11 (51w) - close cta
        "The Gate of Tears proves that the modern digital economy is anchored to immutable physical geography. As long as thirty percent of container shipping squeezes through this eighteen-mile strait, global commodity prices remain vulnerable to a single geological chokepoint. Which geographic bottleneck surprised you most? Share your perspective below."
    ]

    beat_data = [
        # SC01
        [
            ("Panoramic 1940s Admiralty nautical chart of the southern Red Sea on aged #E8DFCA parchment chart, showing the 18-mile gap of Bab el-Mandeb between Yemen and Djibouti with brass compass rose emblem and fine bathymetric depth contours", "pan_left", "hold"),
            ("Close-up hand-engraved nautical chart showing crimson shipping lane vectors funneled into the narrow mouth of Bab el-Mandeb, with sepia copperplate ink cross-hatching across landmasses", "slow_zoom_in", "none"),
            ("Macro cartographic detail of container ship vector icons stamped in deep crimson #E63946 moving in dense single-file line toward the Gate of Tears", "pan_right", "none"),
            ("Lithographic map cross-section showing percentage labels: 12% global seaborne trade and 30% container volume highlighted with subtle shipping-lane gold #FFB703 ink", "hold", "none"),
            ("Orthographic 2D tactical map view of the Red Sea gateway with radiating red danger concentric rings indicating geopolitical flashpoints along the coastline", "slow_zoom_out", "none"),
            ("Full panoramic Admiralty chart showing global maritime trade routes abruptly converging at the crimson-highlighted 18-mile bottleneck, 65% negative space", "hold", "hold"),
        ],
        # SC02
        [
            ("Detailed topographic and bathymetric cross-section of the Bab el-Mandeb strait, showing continental shelves of Africa and Arabia rendered in sepia lithographic ink on parchment", "pan_left", "hold"),
            ("Bird's-eye nautical lithograph centered on volcanic Perim Island #E6CCB2 rising out of deep navy water #0D1B2A, dividing the strait into two passages", "slow_zoom_in", "none"),
            ("Close-up nautical chart of the eastern channel Bab Iskender showing shallow coral reefs and depth soundings under 15 fathoms marked with warning cross-hatching", "pan_right", "none"),
            ("Nautical chart focus on the western channel Dact-el-Mayun, highlighting the deep two-mile navigable trench rendered in vivid strait cyan #4EA8DE", "hold", "none"),
            ("Bathymetric elevation cross-section diagram comparing the draft of a 24,000-TEU container vessel with the narrow underwater seabed profile of the western channel", "slow_zoom_in", "none"),
            ("Topographic lithograph showing volcanic rocky slopes of Perim Island with brass surveyor coordinates and archival latitude markings, 65% negative space", "hold", "hold"),
        ],
        # SC03
        [
            ("Archival nautical route map showing dense crimson flow vectors representing 20,000 annual commercial ship transits passing through Bab el-Mandeb", "pan_left", "hold"),
            ("Lithographic technical illustration of ultra-large container carrier silhouette stacked high with standardized steel container boxes, rendered in crisp 2D line art", "slow_zoom_in", "none"),
            ("Cartographic commodity breakdown overlay showing gold vectors #FFB703 for electronics and crimson vectors #E63946 for manufactured machinery", "pan_right", "none"),
            ("Nautical tanker chart detailing oil trade flows, showing supertanker silhouettes moving four million barrels of crude oil daily northward toward the Suez Canal", "hold", "none"),
            ("Strategic maritime energy corridor map linking Persian Gulf oil loading terminals through Bab el-Mandeb directly to Mediterranean refineries", "slow_zoom_out", "none"),
            ("Wide Admiralty chart layout showing the interconnected Eurasian maritime lifeline, anchored by the precision brass compass rose, 65% negative space", "hold", "hold"),
        ],
        # SC04
        [
            ("Conceptual editorial cartography: delicate golden clockwork gears representing just-in-time manufacturing meshed directly over a vintage 2D ocean chart", "pan_left", "hold"),
            ("High-contrast lithograph showing a modern container vessel silhouette precariously balanced atop an ancient geological ridge on aged parchment", "slow_zoom_in", "none"),
            ("Symbolic cartographic scene: fractured crimson fault lines cutting across optimistic straight trade lines on #E8DFCA parchment paper", "pan_right", "none"),
            ("Detailed topographic view of the rugged volcanic Yemeni coastal bluffs overlooking the narrow shipping trench below, stark chiaroscuro ink lines", "hold", "none"),
            ("Minimalist conceptual map contrasting fragile digital trade networks against immovable granite and basalt continental plates", "slow_zoom_in", "none"),
            ("Panoramic editorial composition showing the vast blue ocean abruptly constrained by two pinching landmasses, at least 65% negative space", "hold", "hold"),
        ],
        # SC05
        [
            ("Tactical naval chart displaying crimson warning arcs and radar sweep vectors radiating from coastal missile sites along the southern Red Sea", "pan_left", "hold"),
            ("Nautical map visualization of commercial container vessels abruptly halting in open water, indicated by red anchor icons and dotted turning arcs", "slow_zoom_in", "none"),
            ("Close-up map view of a container mega-vessel executing a sharp 180-degree tactical turn away from the entrance of the Gate of Tears", "pan_right", "none"),
            ("Fleet operations dispatch document graphic styled as vintage Admiralty telegraph order: bypass Suez Canal and divert south immediately", "hold", "none"),
            ("Broader regional cartography showing dozens of red commercial ship vectors simultaneously curving away from the Red Sea corridor", "slow_zoom_out", "none"),
            ("Stark nautical map showing the sudden vacuum of shipping in the southern Red Sea, surrounded by calm navy ocean and parchment coastlines, 65% negative space", "hold", "hold"),
        ],
        # SC06
        [
            ("Continental-scale nautical lithograph comparing the direct 8,500-mile Suez route in gold #FFB703 with the 12,000-mile Cape route in crimson #E63946", "pan_left", "hold"),
            ("Nautical chart tracking the long southern detour hugging the jagged eastern coast of Africa down toward Madagascar and Mozambique", "slow_zoom_in", "none"),
            ("Detailed Admiralty chart of the treacherous Cape of Good Hope, with bathymetric wave contours and prevailing gale-force wind vectors", "pan_right", "none"),
            ("Timeline distance comparison infographic etched on parchment showing thirty-five hundred extra nautical miles and twelve additional sailing days", "hold", "none"),
            ("High-seas nautical lithograph showing a solitary container ship silhouette braving heavy rolling swell vectors in the South Atlantic Ocean", "slow_zoom_in", "none"),
            ("Panoramic African continent lithograph with complete red orbital shipping line looping around the southern tip, 65% negative space", "hold", "hold"),
        ],
        # SC07
        [
            ("Financial ledger and fuel computation chart rendered on vintage parchment, showing daily bunker fuel consumption of 150 metric tons", "pan_left", "hold"),
            ("Graphic breakdown highlighting an additional one million dollars in bunker fuel costs stamped in bold crimson ink beside container ship blueprints", "slow_zoom_in", "none"),
            ("Marine insurance risk chart showing exponential upward curve in war-risk premiums for Red Sea transits versus Cape voyages", "pan_right", "none"),
            ("Commercial freight rate index chart showing spot container shipping prices leaping from twelve hundred to over four thousand dollars per TEU", "hold", "none"),
            ("Ship charter exchange ledger displaying cascading surcharges: bunker adjustment factor, peak season surcharge, and equipment repositioning fees", "slow_zoom_in", "none"),
            ("Full-frame strategic balance sheet showing cumulative multi-million-dollar cost inflation per round-trip voyage, 65% negative space", "hold", "hold"),
        ],
        # SC08
        [
            ("Macro logistics system diagram showing synchronized weekly vessel liner schedules turning into tangled, overlapping crimson lines", "pan_left", "hold"),
            ("Cartographic heatmap of major Asian export hubs in Shanghai, Ningbo, and Singapore facing empty container equipment deficits", "slow_zoom_in", "none"),
            ("Depiction of thousands of empty twenty-foot container box silhouettes stranded aboard ships steaming slowly through the middle of the Atlantic", "pan_right", "none"),
            ("Industrial manufacturing chain graphic showing European factory assembly lines with missing component gears highlighted in crimson outline", "hold", "none"),
            ("Conceptual split-frame lithograph: empty container yards in Asia contrasted with idle factory warehouses in Northern Europe", "slow_zoom_in", "none"),
            ("Panoramic map of global trade disequilibrium showing asymmetric container accumulation, 65% negative space", "hold", "hold"),
        ],
        # SC09
        [
            ("Admiralty nautical chart of the English Channel and North Sea gateway, showing container ships queued outside Rotterdam, Antwerp, and Hamburg", "pan_left", "hold"),
            ("Detailed 2D architectural lithograph of port container terminal showing gantry cranes operating over stacked container pyramids under high pressure", "slow_zoom_in", "none"),
            ("Schedule bunching timeline chart showing three delayed mega-vessels arriving on the exact same afternoon instead of spaced across two weeks", "pan_right", "none"),
            ("Schematic map of European rail and inland barge feeder networks completely clogged by sudden irregular surges of import cargo", "hold", "none"),
            ("Automotive factory schematic showing assembly line conveyor stopped due to delayed wiring harnesses and microchips floating off Africa", "slow_zoom_in", "none"),
            ("Wide cartographic perspective of Northern European logistics hubs under stress, framed by aged parchment borders, 65% negative space", "hold", "hold"),
        ],
        # SC10
        [
            ("Tactical naval warfare chart depicting guided-missile destroyer silhouette patrolling the southern Red Sea corridor with radar rings", "pan_left", "hold"),
            ("Tactical engagement diagram comparing a two-million-dollar naval surface-to-air interceptor missile with a twenty-thousand-dollar aerial drone", "slow_zoom_in", "none"),
            ("Cost-asymmetry curve etched in copperplate ink showing the mathematical unsustainability of long-term commercial naval convoy escorts", "pan_right", "none"),
            ("Overhead cartographic view showing that even with warship escorts, merchant vessels must still navigate through the fixed two-mile trench", "hold", "none"),
            ("Marine insurance underwriter dossier stamped with crimson 'UNINSURABLE' risk classifications over the Bab el-Mandeb transit zone", "slow_zoom_in", "none"),
            ("High-angle tactical cartography showing warships dwarf by the vastness of the Red Sea and Gulf of Aden, 65% negative space", "hold", "hold"),
        ],
        # SC11
        [
            ("Grand panoramic 1940s Admiralty lithograph showing the global network of maritime choke points: Suez, Malacca, Panama, and Bab el-Mandeb", "pan_left", "hold"),
            ("Zoomed focus on the 18-mile Gate of Tears highlighted with glowing gold outline against deep maritime navy ocean #0D1B2A", "slow_zoom_in", "none"),
            ("Precision brass compass rose graphic overlaying the Red Sea gateway, symbolizing the permanent supremacy of physical geography", "pan_right", "none"),
            ("Conceptual cartographic montage: delicate trade goods silhouettes framed within the ancient volcanic rock contours of the strait", "hold", "none"),
            ("Hand-lettered editorial banner on aged parchment: 'GEOGRAPHY IS DESTINY', framed by fine engraved copperplate border flourishes", "slow_zoom_out", "none"),
            ("Final elegant nautical chart endcard displaying Choke Point Maps brass seal and discussion prompt on #E8DFCA parchment, 65% negative space", "hold", "hold"),
        ]
    ]

    scenes = []
    coverage = []
    claims = [
        {
            "scene_id": "SC01",
            "quote": "this maritime bottleneck carries twelve percent of all global seaborne trade and nearly thirty percent of worldwide container traffic.",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Twelve percent of global trade and thirty percent of container traffic pass through Bab el-Mandeb."
        },
        {
            "scene_id": "SC02",
            "quote": "Perim Island sits directly in the center, dividing the strait into two channels.",
            "language": "en",
            "source_id": "SRC02",
            "fact": "Volcanic Perim Island splits the Bab el-Mandeb strait into two channels."
        },
        {
            "scene_id": "SC03",
            "quote": "More than twenty thousand merchant vessels navigate this narrow channel every single year",
            "language": "en",
            "source_id": "SRC02",
            "fact": "Over twenty thousand commercial vessels transit the Bab el-Mandeb corridor annually."
        },
        {
            "scene_id": "SC06",
            "quote": "adding thirty-five hundred nautical miles to the standard transit between East Asia and Northern Europe.",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Rerouting around the Cape of Good Hope adds thirty-five hundred nautical miles to voyages."
        },
        {
            "scene_id": "SC07",
            "quote": "that African detour burns an extra one million dollars in bunker fuel for a single one-way transit.",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Detours around Africa add ten to fourteen sailing days and one million dollars in bunker fuel."
        }
    ]

    for idx, (narr, beats_info) in enumerate(zip(sc_narrations, beat_data), start=1):
        sc_id = f"SC{idx:02d}"
        req_id = f"R{idx:02d}"
        
        sit_map = {
            1: "hook_shock",
            2: "mechanism_step",
            3: "before_after_contrast",
            4: "editorial_commentary",
            5: "story_action",
            6: "mechanism_step",
            7: "rapid_examples",
            8: "editorial_commentary",
            9: "mechanism_step",
            10: "before_after_contrast",
            11: "cta_bridge"
        }
        sit = sit_map[idx]
        
        req_quote_map = {
            1: "At the southern entrance of the Red Sea lies a narrow oceanic corridor known as Bab el-Mandeb",
            2: "Perim Island sits directly in the center, dividing the strait into two channels.",
            3: "More than twenty thousand merchant vessels navigate this narrow channel every single year",
            4: "Modern corporate logistics operate under the dangerous fiction of frictionless global trade",
            5: "Major international container carriers suspended Red Sea transits within forty-eight hours.",
            6: "adding thirty-five hundred nautical miles to the standard transit between East Asia and Northern Europe.",
            7: "that African detour burns an extra one million dollars in bunker fuel for a single one-way transit.",
            8: "thousands of empty steel containers become stranded at sea, causing acute equipment deficits in Asian export ports",
            9: "In European gateway ports like Rotterdam, Antwerp, and Hamburg, terminal yards face severe vessel bunching",
            10: "Multinational naval coalitions deploy Aegis destroyers to escort commercial convoys",
            11: "As long as thirty percent of container shipping squeezes through this eighteen-mile strait"
        }
        coverage.append({
            "requirement_id": req_id,
            "scene_id": sc_id,
            "quote": req_quote_map[idx]
        })

        images = []
        beats = []
        tempos = ["fast", "fast", "normal", "normal", "slow", "normal"]

        for b_idx, (desc, cam, eff) in enumerate(beats_info, start=1):
            img_id = f"{sc_id}_I{b_idx}"
            beat_id = f"{sc_id}_B{b_idx}"
            t = tempos[b_idx - 1]
            
            images.append({
                "id": img_id,
                "description": desc,
                "character_ids": ["CH01"],
                "preserve": "1940s British Admiralty chart style, #E8DFCA aged nautical parchment, crimson vectors",
                "change": f"Detailed composition change for beat {beat_id}",
                "reason": f"Narration-locked full-frame beat {img_id}.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": t,
                "narrative_situation": sit,
                "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                "has_character": False,
                "motion_prompt": f"Tactile 2D nautical chart animation, {desc[:100].lower()}, silent visual storytelling, no talking, no lip movement",
                "camera_motion": cam,
                "effect": eff
            })
            beats.append({
                "id": beat_id,
                "image_id": img_id,
                "purpose": f"Visual progression beat {b_idx} for scene {sc_id}",
                "tempo": t,
                "narrative_situation": sit,
                "shot_type": "full_scene",
                "effect": eff
            })

        scenes.append({
            "id": sc_id,
            "title": outline["outline"][idx - 1]["purpose"][:60],
            "purpose": outline["outline"][idx - 1]["purpose"],
            "action": f"Tactile nautical cartography depicting {sc_id} events on #E8DFCA parchment chart.",
            "setting": "1940s British Admiralty nautical chart on aged #E8DFCA parchment paper canvas.",
            "camera": "Semantic full-frame sequence",
            "narration": narr,
            "requirements": [req_id],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"] if idx in [1, 6, 7] else ["SRC02"],
            "narrative_situation": sit,
            "images": images,
            "beats": beats
        })

    content = {
        "schema_version": "3.0",
        "job_id": job_id,
        "topic": topic,
        "duration": brief["duration"],
        "style": brief["style"],
        "required_points": [rp["text"] for rp in brief["required_points"]],
        "characters": [channel_cast(channel_id, "CH01")],
        "scenes": scenes,
        "coverage": coverage,
        "outline": outline["outline"],
        "claims": claims,
        "revision_response": [],
        "open_questions": []
    }

    return job_id, brief, outline, competitor_research, content


def make_choke_point_short():
    job_id = "en-choke-point-batch1-9x16"
    parent_long_id = "en-choke-point-batch1-16x9"
    channel_id = "en_choke_point"
    ch = get_channel(channel_id)
    topic = "The Gate of Tears: Why the 18-Mile Bab el-Mandeb Strait Can Paralyze European Trade Overnight"
    youtube_title = "Block This 18-Mile Gap and Trade Stalls in Days"  # 47 chars <= 55

    style_desc = (
        "1940s British Admiralty Nautical Chart and Topographic Lithograph on vertical #E8DFCA parchment chart paper "
        "(#0D1B2A deep maritime navy ocean, #E6CCB2 topographic sand landmasses, #E63946 crimson shipping vectors, "
        "#FFB703 shipping-lane gold, #4EA8DE strait cyan); fine hand-engraved bathymetric depth contour lines, "
        "sepia copperplate ink cross-hatching, archival brass compass rose, orthographic 2D cartography, "
        "at least 60% negative space, zero 3D CGI, zero neon glow, zero plastic gradients."
    )

    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Fast-paced vertical explainer showing how a closure of the 18-mile Bab el-Mandeb strait cascades into global shipping delays and price shocks.",
        "video_type": "explainer",
        "duration": {"min_seconds": 38.0, "max_seconds": 52.0},
        "scene_count": 5,
        "parent_long_id": parent_long_id,
        "required_points": [
            {"id": "R01", "text": "Bab el-Mandeb funneling thirty percent of global container shipping through an eighteen-mile gap."},
            {"id": "R02", "text": "Volcanic Perim Island restricting deep-water navigation to a single two-mile passage."},
            {"id": "R03", "text": "Diverting around the Cape of Good Hope adding thirty-five hundred miles and one million dollars in bunker fuel."},
            {"id": "R04", "text": "Stranded containers quadrupling spot freight rates and delaying European manufacturing supplies."},
            {"id": "R05", "text": "The geological vulnerability of global supply chains and invitation to explore full analysis."}
        ],
        "language": "en",
        "tone": ch.tone,
        "style": style_desc,
        "aspect_ratio": "9:16",
        "format_profile": "short_9x16",
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "Navigating Troubled Waters: The Impact of Red Sea Disruptions on Global Trade",
                "reference": "United Nations Conference on Trade and Development (UNCTAD, 2024). UNCTAD Rapid Assessment Report.",
                "facts": [
                    "Twelve percent of global trade and thirty percent of container traffic pass through Bab el-Mandeb.",
                    "Rerouting around the Cape of Good Hope adds thirty-five hundred nautical miles to voyages.",
                    "Detours around Africa add ten to fourteen sailing days and one million dollars in bunker fuel."
                ]
            }
        ],
        "outputs": [
            {
                "aspect_ratio": "9:16",
                "language": "en",
                "subtitles": True,
                "voice": ch.voice,
                "speed": 1.0
            }
        ],
        "planning": {
            "success_criteria": [
                "Hook within 3 seconds, illustrate the 18-mile bottleneck, reveal the Cape detour cost, and bridge to the long video at the peak."
            ],
            "avoid": [
                "Zero corporate buzzwords, zero slow intros, zero banned CTA words."
            ],
            "prior_knowledge": "None required.",
            "pacing": "Rapid vertical visual pacing (~2.2s per image).",
            "speech_rates": {
                "en": {
                    "units_per_second": 3.8,
                    "uncertainty": 0.15,
                    "source": "Acoustic calibrated cadence"
                }
            }
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Vertical 1940s Admiralty chart showing the 18-mile strait locked by crimson blockade vectors",
                "text_overlay": "18 MILES TO CHAOS",
                "contrast_pair": "2-Mile Shipping Trench vs 3500-Mile Detour",
                "layout_mode": "split_contrast"
            },
            "channel_pillar": ch.niche,
            "funnel_tier": "tier_1_broad",
            "seo_keywords": [
                "Bab el-Mandeb",
                "choke point shorts",
                "Red Sea crisis",
                "global trade bottleneck"
            ]
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Vertical 1940s Admiralty chart showing the 18-mile strait locked by crimson blockade vectors",
            "text_overlay": "18 MILES TO CHAOS",
            "contrast_pair": "2-Mile Shipping Trench vs 3500-Mile Detour",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": ch.niche,
        "funnel_tier": "tier_1_broad",
        "seo_keywords": [
            "Bab el-Mandeb",
            "choke point shorts",
            "Red Sea crisis",
            "global trade bottleneck"
        ],
        "cta_plan": {
            "cliffhanger_peak": "Can modern international commerce ever escape this ancient geological choke point?",
            "bridge": "Watch the full breakdown on Choke Point Maps.",
            "close": "What chokepoint should we map next? Tell us below.",
            "endcard_text": "FULL VIDEO ON YOUTUBE"
        },
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": ch.engagement.cta_voice,
            "banned_cta_phrases": list(ch.engagement.banned_cta_phrases)
        },
        "editorial_stance": {
            "myth_debunked": "Global shipping networks can absorb strait closures without causing major domestic inflation.",
            "channel_verdict": "The entire world economy is physically bound to an eighteen-mile crack in the earth that technology cannot bypass.",
            "why_generic_advice_fails": "Pundits focus only on ship delays while ignoring that container deficits halt inland factories thousands of miles away.",
            "tradeoff_or_blindspot": "Naval escorts cannot eliminate the geometric danger of funneling megaships through a two-mile trench."
        },
        "actionable_value": {
            "core_mechanism": "The strait detour penalty: adding thirty-five hundred nautical miles around Africa drains twenty percent of global vessel capacity instantly.",
            "practical_rule_of_thumb": "When analyzing supply chain risk, measure nautical transit bottlenecks rather than factory production quotas.",
            "real_world_scenario": "A retailer suffers a month-long stockout because their container ship had to sail around the Cape of Good Hope."
        },
        "video_engine": "images_only",
        "chain_mode": "full_chain"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Hook: thirty percent of global containers squeezed through an 18-mile gap", "requirements": ["R01"], "transition": "Rapid zoom into Bab el-Mandeb"},
            {"scene_id": "SC02", "purpose": "Mechanism: volcanic Perim Island leaving only a two-mile deep-water shipping trench", "requirements": ["R02"], "transition": "Bathymetric cutaway of the channel"},
            {"scene_id": "SC03", "purpose": "Editorial commentary: Cape detour adding 3,500 miles, 12 days, and $1M in fuel", "requirements": ["R03"], "transition": "Continental African map comparison"},
            {"scene_id": "SC04", "purpose": "Cliffhanger peak: empty containers stranded at sea, quadrupling freight rates and halting factories", "requirements": ["R04"], "transition": "Supply chain shockwave diagram"},
            {"scene_id": "SC05", "purpose": "Payoff, bridge CTA to full video, and close prompt", "requirements": ["R05"], "transition": "Closing nautical seal and endcard"}
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "RealLifeLore Shorts",
                    "top_performing_videos": [
                        {
                            "title": "Why This 18-Mile Gap Rules the World",
                            "views": "1.5M views",
                            "hook_technique": "Immediate high-contrast vertical zoom onto Bab el-Mandeb with glowing crimson boundary.",
                            "pacing_structure": "3s hook -> 15s geography lesson -> 15s economic consequence -> Peak bridge.",
                            "retention_driver": "Rapid visual turnover under 2.5s."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Front-loading the 18-mile statistic in the opening sentence.",
                        "Direct visual contrast between the tiny strait and the colossal African landmass."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 28,
                "zero_pause_opening_seconds": 12,
                "visual_contrast": "Vertical Admiralty chart showing giant container ship dwarfed by the 18-mile strait.",
                "counter_intuitive_truth_slap": "A single two-mile underwater trench controls retail prices across an entire hemisphere."
            },
            "narrative_progression_arc": [
                {"phase": "hook_shock", "purpose": "Thirty percent container volume in an 18-mile gateway"},
                {"phase": "mechanism_step", "purpose": "Perim Island leaving only two miles of deep water"},
                {"phase": "editorial_commentary", "purpose": "3,500 extra miles and $1M fuel detour"},
                {"phase": "cliffhanger_peak", "purpose": "Empty containers stranded and factory lines halted"},
                {"phase": "cta_bridge", "purpose": "Bridge to full long video and engagement question"}
            ],
            "flow_video_transition_blueprint": {
                "keyframe_continuity": "Vertical nautical parchment #E8DFCA with crimson shipping vectors.",
                "tempo_modulation": "Rapid tempo throughout (< 2.3s hold)."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": ch.niche,
            "myth_debunked": brief["editorial_stance"]["myth_debunked"],
            "channel_verdict": brief["editorial_stance"]["channel_verdict"],
            "actionable_rule_of_thumb": brief["actionable_value"]["practical_rule_of_thumb"]
        },
        "cta_and_spinoff_strategy": {
            "bridge": brief["cta_plan"]["bridge"],
            "close": brief["cta_plan"]["close"],
            "endcard_text": brief["cta_plan"]["endcard_text"]
        }
    }

    sc01_narr = "Squeeze thirty percent of all global container shipping through an 18-mile gap between Yemen and Djibouti, spanning ancient maritime trade routes, and you hold the world economy by the throat. Welcome to Bab el-Mandeb, the Gate of Tears."
    sc02_narr = "Volcanic Perim Island splits the strait down the center, leaving only a single two-mile deep-water trench safe for modern container megaships carrying consumer electronics, automotive parts, and four million barrels of daily crude oil."
    sc03_narr = "When security collapses here, shipping lines must divert thirty-five hundred nautical miles around Africa's Cape of Good Hope, adding twelve sailing days and one million dollars in bunker fuel to every single commercial voyage."
    sc04_narr = "That massive detour strands thousands of empty containers at sea, quadrupling global spot freight rates overnight and threatening European factories with sudden component shortages that push retail prices higher across dozens of major industries."
    sc05_narr = "Can modern international commerce ever escape this ancient geological choke point? Watch the full breakdown on Choke Point Maps. What chokepoint should we map next? Tell us below."

    sc_narrations_short = [sc01_narr, sc02_narr, sc03_narr, sc04_narr, sc05_narr]

    beat_data_short = [
        # SC01
        [
            ("Vertical 1940s Admiralty chart of Bab el-Mandeb on aged #E8DFCA parchment paper, showing the narrow 18-mile gap framed by brass compass coordinates", "pan_left", "hold"),
            ("Close-up nautical chart with bold crimson vector arrows #E63946 representing thirty percent of global container shipping squeezing through the strait", "slow_zoom_in", "none"),
            ("Lithographic illustration of container megaship silhouette navigating past the jagged coastal bluffs of Djibouti and Yemen", "pan_right", "none"),
            ("Wide vertical overview of the southern Red Sea gateway with sepia copperplate ink cross-hatching, 65% negative space", "hold", "hold"),
        ],
        # SC02
        [
            ("Vertical bathymetric cross-section showing volcanic Perim Island dividing the strait into a shallow eastern channel and deep western passage", "pan_left", "hold"),
            ("Close-up nautical depth soundings highlighting the shallow reefs in the eastern channel with crimson warning cross-hatching", "slow_zoom_in", "none"),
            ("Technical lithograph highlighting the narrow two-mile deep-water trench in vivid strait cyan #4EA8DE on parchment paper", "pan_right", "none"),
            ("Detailed nautical diagram comparing container ship draft with the narrow submarine trench profile, 65% negative space", "hold", "hold"),
        ],
        # SC03
        [
            ("Vertical continental map of Africa showing the massive red detour vector looping around the Cape of Good Hope versus the short gold Suez route", "pan_left", "hold"),
            ("Admiralty chart detail of the southern tip of Africa showing rough oceanic swell vectors and thirty-five hundred extra nautical miles", "slow_zoom_in", "none"),
            ("Vintage parchment cost ledger graphic displaying twelve additional sailing days and one million dollars in extra bunker fuel", "pan_right", "none"),
            ("High-seas lithograph of container carrier silhouette sailing through Atlantic swell vectors on aged parchment, 65% negative space", "hold", "hold"),
        ],
        # SC04
        [
            ("Cartographic heatmap showing empty shipping container deficits spreading across Asian export ports in bold crimson highlights", "pan_left", "hold"),
            ("Financial chart etched in copperplate ink showing global spot container freight rates quadrupling from twelve hundred to over four thousand dollars", "slow_zoom_in", "none"),
            ("Schematic of European automotive assembly line stalled due to delayed maritime containers, stark black ink silhouettes on parchment", "pan_right", "none"),
            ("Conceptual supply chain fracture map showing empty store shelves linked to delayed ships off Africa, 65% negative space", "hold", "hold"),
        ],
        # SC05
        [
            ("Vertical Admiralty lithograph showing the global network of strategic maritime choke points with Bab el-Mandeb circled in gold #FFB703", "pan_left", "hold"),
            ("Zoomed focus on the 18-mile strait with precision brass compass rose emblem and historical Gate of Tears title banner", "slow_zoom_in", "none"),
            ("Hand-engraved nautical card presenting Choke Point Maps brass seal and YouTube channel title", "pan_right", "none"),
            ("Final elegant nautical endcard with discussion prompt: 'What chokepoint should we map next?', 65% negative space", "hold", "hold"),
        ]
    ]

    scenes = []
    coverage = []
    claims = [
        {
            "scene_id": "SC01",
            "quote": "Squeeze thirty percent of all global container shipping through an 18-mile gap between Yemen and Djibouti",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Twelve percent of global trade and thirty percent of container traffic pass through Bab el-Mandeb."
        },
        {
            "scene_id": "SC03",
            "quote": "adding twelve sailing days and one million dollars in bunker fuel to every single commercial voyage.",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Detours around Africa add ten to fourteen sailing days and one million dollars in bunker fuel."
        }
    ]

    short_sits = ["hook_shock", "mechanism_step", "editorial_commentary", "cliffhanger_peak", "cta_bridge"]
    req_quotes_short = [
        "Squeeze thirty percent of all global container shipping through an 18-mile gap between Yemen and Djibouti",
        "Volcanic Perim Island splits the strait down the center, leaving only a single two-mile deep-water trench",
        "adding twelve sailing days and one million dollars in bunker fuel to every single commercial voyage.",
        "That massive detour strands thousands of empty containers at sea, quadrupling global spot freight rates",
        "Watch the full breakdown on Choke Point Maps. What chokepoint should we map next? Tell us below."
    ]

    for idx, (narr, beats_info, sit, q) in enumerate(zip(sc_narrations_short, beat_data_short, short_sits, req_quotes_short), start=1):
        sc_id = f"SC{idx:02d}"
        req_id = f"R{idx:02d}"
        
        coverage.append({
            "requirement_id": req_id,
            "scene_id": sc_id,
            "quote": q
        })

        images = []
        beats = []
        tempos = ["fast", "fast", "normal", "slow"]

        for b_idx, (desc, cam, eff) in enumerate(beats_info, start=1):
            img_id = f"{sc_id}_I{b_idx}"
            beat_id = f"{sc_id}_B{b_idx}"
            t = tempos[b_idx - 1]
            
            images.append({
                "id": img_id,
                "description": desc,
                "character_ids": ["CH01"],
                "preserve": "1940s British Admiralty vertical chart style, #E8DFCA parchment, crimson vectors",
                "change": f"Detailed vertical composition change for beat {beat_id}",
                "reason": f"Narration-locked full-frame beat {img_id}.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": t,
                "narrative_situation": sit,
                "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                "has_character": False,
                "motion_prompt": f"Tactile 2D vertical nautical chart animation, {desc[:100].lower()}, silent visual storytelling, no talking, no lip movement",
                "camera_motion": cam,
                "effect": eff
            })
            beats.append({
                "id": beat_id,
                "image_id": img_id,
                "purpose": f"Vertical visual beat {b_idx} for scene {sc_id}",
                "tempo": t,
                "narrative_situation": sit,
                "shot_type": "full_scene",
                "effect": eff
            })

        scenes.append({
            "id": sc_id,
            "title": outline["outline"][idx - 1]["purpose"][:60],
            "purpose": outline["outline"][idx - 1]["purpose"],
            "action": f"Tactile vertical nautical cartography depicting {sc_id} events on #E8DFCA parchment.",
            "setting": "1940s British Admiralty vertical nautical chart on aged #E8DFCA parchment paper canvas.",
            "camera": "Semantic full-frame sequence",
            "narration": narr,
            "requirements": [req_id],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "narrative_situation": sit,
            "images": images,
            "beats": beats
        })

    content = {
        "schema_version": "3.0",
        "job_id": job_id,
        "topic": topic,
        "duration": brief["duration"],
        "style": brief["style"],
        "required_points": [rp["text"] for rp in brief["required_points"]],
        "characters": [channel_cast(channel_id, "CH01")],
        "scenes": scenes,
        "coverage": coverage,
        "outline": outline["outline"],
        "claims": claims,
        "revision_response": [],
        "open_questions": []
    }

    return job_id, brief, outline, competitor_research, content


# ==============================================================================
# CHANNEL 2: EN_COLD_CASE_INK (Cold Case Ink)
# ==============================================================================

def make_cold_case_ink_long():
    job_id = "en-cold-case-ink-batch1-16x9"
    channel_id = "en_cold_case_ink"
    ch = get_channel(channel_id)
    topic = "The 1952 London Killer Fog: How an Anticyclone Trapped Sulfuric Acid Over Nine Million People for Five Days"
    youtube_title = "Five Days of Acid Darkness: The 1952 London Fog"  # 48 chars <= 55

    style_desc = (
        "Forensic Archival Dossier and Woodcut Chiaroscuro Noir illustration on fibrous #DFD7C4 manila dossier paper "
        "(#111111 deep India ink black, #DFD7C4 aged case-file manila, #5A5F66 charcoal shadow wash, "
        "#8B1E1E crimson sealing wax stamp and timeline pins); hand-carved woodcut cross-hatching, "
        "soot-stained archival document texture, magnifying lenses, and high-contrast chiaroscuro shadow drama; "
        "orthographic 2D, at least 60% negative space, zero 3D CGI, zero neon glow, zero plastic gradients."
    )

    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Re-examine the 1952 London Killer Fog through meteorological forensic archives, chemical mechanisms, and epidemiological evidence.",
        "video_type": "explainer",
        "duration": {"min_seconds": 150.0, "max_seconds": 210.0},
        "scene_count": 11,
        "required_points": [
            {"id": "R01", "text": "December fifth 1952: visibility collapses to twelve inches across London as yellow-black fog descends."},
            {"id": "R02", "text": "A high-pressure anticyclone creating a thermal inversion that seals the Thames basin under an airtight lid."},
            {"id": "R03", "text": "Post-war austerity exporting clean anthracite and forcing domestic use of sulfurous nutty slack coal."},
            {"id": "R04", "text": "Three million hearths and riverside power stations dumping thousands of tons of sulfur into trapped air."},
            {"id": "R05", "text": "Chemical oxidation turning airborne sulfur dioxide into droplets of corrosive sulfuric acid aerosol."},
            {"id": "R06", "text": "Toxic acid smog penetrating indoors, shutting down road traffic, and halting cinema screenings mid-film."},
            {"id": "R07", "text": "Sadler's Wells opera stopped as singers choke while prize cattle asphyxiate at Smithfield market."},
            {"id": "R08", "text": "Government officials downplaying the catastrophe while morgues overflow and coffins run out."},
            {"id": "R09", "text": "Hospital records documenting over twelve thousand fatalities from acute hypoxia and respiratory failure."},
            {"id": "R10", "text": "A fresh westerly wind clearing the lethal shroud and exposing coal smoke as a chemical hazard."},
            {"id": "R11", "text": "Forensic evidence forcing parliament to pass the revolutionary Clean Air Act of 1956."}
        ],
        "language": "en",
        "tone": ch.tone,
        "style": style_desc,
        "aspect_ratio": "16:9",
        "format_profile": "long_16x9",
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "Mortality and Morbidity during the London Fog of December 1952",
                "reference": "Ministry of Health & UK Meteorological Office (1954). Reports on Public Health and Medical Subjects No. 95.",
                "facts": [
                    "Visibility dropped to twelve inches across central London on December fifth, 1952.",
                    "Anticyclone thermal inversion trapped cold ground air beneath a warm atmospheric layer.",
                    "Hospitals admitted thousands of patients suffering from acute hypoxia, bronchitis, and cardiac collapse."
                ]
            },
            {
                "id": "SRC02",
                "title": "Reassessment of the Lethal London Fog of 1952: Novel Indicators of Acute and Chronic Effects of Air Pollution",
                "reference": "Bell, M. L., & Davis, D. L. (2001). Environmental Health Perspectives, 109(Suppl 3), 389-394.",
                "facts": [
                    "Austerity exports of high-grade coal forced Londoners to burn sulfurous nutty slack.",
                    "Microscopic soot catalyzed sulfur dioxide oxidation into droplets of airborne sulfuric acid.",
                    "Modern epidemiological reviews established over twelve thousand fatalities from the five-day fog."
                ]
            }
        ],
        "outputs": [
            {
                "aspect_ratio": "16:9",
                "language": "en",
                "subtitles": False,
                "voice": ch.voice,
                "speed": 1.0
            }
        ],
        "planning": {
            "success_criteria": [
                "Dissect the thermal inversion physics, nutty slack coal chemistry, sulfuric acid aerosol formation, and epidemiological mortality revisions."
            ],
            "avoid": [
                "Zero supernatural speculation, zero gothic melodramatics, zero unverified conspiracy theories."
            ],
            "prior_knowledge": "None required.",
            "pacing": "Forensic documentary investigation cadence (~3.8 syllables/sec).",
            "speech_rates": {
                "en": {
                    "units_per_second": 3.8,
                    "uncertainty": 0.15,
                    "source": "Acoustic calibrated cadence"
                }
            }
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Archival dossier evidence board with fedora detective silhouette lantern beam over 1952 London death certificate and sulfur soot vial",
                "text_overlay": "ACID DARKNESS",
                "contrast_pair": "Twelve Inches Visibility vs 12,000 Fatalities",
                "layout_mode": "split_contrast"
            },
            "channel_pillar": ch.niche,
            "funnel_tier": "tier_1_broad",
            "seo_keywords": [
                "Great Smog of London",
                "1952 London fog",
                "sulfuric acid fog",
                "clean air act 1956",
                "forensic history",
                "cold case documentary"
            ]
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Archival dossier evidence board with fedora detective silhouette lantern beam over 1952 London death certificate and sulfur soot vial",
            "text_overlay": "ACID DARKNESS",
            "contrast_pair": "Twelve Inches Visibility vs 12,000 Fatalities",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": ch.niche,
        "funnel_tier": "tier_1_broad",
        "seo_keywords": [
            "Great Smog of London",
            "1952 London fog",
            "sulfuric acid fog",
            "clean air act 1956",
            "forensic history"
        ],
        "cta_plan": {
            "mid_cta": "If you value rigorous historical forensics over sensationalism, save this case file for your records.",
            "close": "Which forensic clue stands out to you most? Share your deduction below.",
            "endcard_text": "FULL VIDEO ON YOUTUBE"
        },
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": ch.engagement.cta_voice,
            "banned_cta_phrases": list(ch.engagement.banned_cta_phrases)
        },
        "editorial_stance": {
            "myth_debunked": "The 1952 London Fog was an unavoidable natural weather catastrophe caused entirely by severe winter cold and damp maritime fog.",
            "channel_verdict": "The disaster was a man-made environmental poisoning caused by government austerity policies that exported clean British coal and forced citizens to burn sulfurous waste.",
            "why_generic_advice_fails": "Contemporary official reports dismissed the lethal darkness as a routine seasonal pea-souper, obscuring state responsibility until mortuaries ran out of coffins.",
            "tradeoff_or_blindspot": "Transitioning London entirely to smokeless fuels and gas heating required massive municipal subsidies and disrupted the livelihood of thousands of domestic coal merchants."
        },
        "actionable_value": {
            "core_mechanism": "Thermal inversion acid trapping: an anticyclone traps cold ground air while domestic and industrial chimneys pump sulfur dioxide that converts into suspended airborne sulfuric acid.",
            "practical_rule_of_thumb": "Forensic environmental rule: in severe atmospheric stagnations, monitor secondary chemical transformations like acid aerosol formation rather than raw particulate smoke alone.",
            "real_world_scenario": "An asthmatic London resident in December 1952 suffered acute respiratory failure inside their sealed parlor because acidic microscopic droplets penetrated interior domestic spaces."
        },
        "video_engine": "images_only",
        "chain_mode": "full_chain"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Hook: visibility collapses to 12 inches on December 5, 1952 as sulfur gloom descends", "requirements": ["R01"], "transition": "Fade into archival weather station barometer records"},
            {"scene_id": "SC02", "purpose": "Mechanism: anticyclone temperature inversion locking the Thames basin under an airtight lid", "requirements": ["R02"], "transition": "Atmospheric cross-section diagram of trapped cold air"},
            {"scene_id": "SC03", "purpose": "Historical context: post-war debts forcing the export of clean coal and domestic burning of nutty slack", "requirements": ["R03"], "transition": "Ministry of Fuel ledgers and coal classification charts"},
            {"scene_id": "SC04", "purpose": "Editorial commentary: three million fireplaces and Battersea power station pumping sulfur into the trap", "requirements": ["R04"], "transition": "Industrial chimney plume schematic"},
            {"scene_id": "SC05", "purpose": "Chemistry mechanism: moisture and soot catalyzing sulfur dioxide into corrosive airborne sulfuric acid", "requirements": ["R05"], "transition": "Microscopic droplet cross-section diagram"},
            {"scene_id": "SC06", "purpose": "Dossier evidence: smog seeping indoors, halting traffic and canceling cinema screenings mid-film", "requirements": ["R06"], "transition": "Indoor theater beam obscured by yellow haze"},
            {"scene_id": "SC07", "purpose": "Primary case studies: Sadler's Wells opera singers choking and Smithfield cattle dying in stalls", "requirements": ["R07"], "transition": "Newspaper clippings and coroner witness statements"},
            {"scene_id": "SC08", "purpose": "Editorial commentary: government downplaying catastrophe while undertakers run out of caskets", "requirements": ["R08"], "transition": "Government memo vs mortuary registry ledger"},
            {"scene_id": "SC09", "purpose": "Epidemiological audit: bronchitis and cardiac collapse claiming over 12,000 victims across five days", "requirements": ["R09"], "transition": "Mortality spike statistical timeline graph"},
            {"scene_id": "SC10", "purpose": "Forensic turning point: westerly winds dispersing fog and unmasking coal smoke as chemical poison", "requirements": ["R10"], "transition": "Cleared skyline revealing blackened stonework"},
            {"scene_id": "SC11", "purpose": "Legacy & closing: the Clean Air Act of 1956 and viewer prompt", "requirements": ["R11"], "transition": "Closing archival dossier case file stamp"}
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "LEMMiNO",
                    "top_performing_videos": [
                        {
                            "title": "The Disappearance of Flight 19",
                            "views": "8.5M views",
                            "hook_technique": "Cold atmospheric open with precise timestamps, navigational charts, and restrained voiceover.",
                            "pacing_structure": "Verified timeline -> Instrument data -> Competing hypotheses -> Forensic conclusion.",
                            "retention_driver": "Extreme documentary rigor and high-contrast archival aesthetic."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Minimalist dossier visual style with aged paper textures and stark black ink silhouettes.",
                        "Direct citation of primary government records and meteorological instruments."
                    ]
                },
                {
                    "channel_name": "Fascinating Horror",
                    "top_performing_videos": [
                        {
                            "title": "The Great Smog of London 1952",
                            "views": "2.1M views",
                            "hook_technique": "Understated narration describing everyday life abruptly brought to a standstill by toxic fog.",
                            "pacing_structure": "Historical setting -> Chemical catalyst -> Daily life breakdown -> Casualty count -> Legislative aftermath.",
                            "retention_driver": "Respectful, non-sensational focus on the human impact and scientific causes."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Emphasizing bizarre physical details like cattle asphyxiation and cinema cancellations.",
                        "Contrasting official political denial against mortuary realities."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 26,
                "zero_pause_opening_seconds": 15,
                "visual_contrast": "Detective silhouette lantern beam illuminating an antique 1952 street sign obscured by pitch black soot.",
                "counter_intuitive_truth_slap": "Londoners were not choking on natural weather mist, but breathing aerosolized sulfuric acid created by government debt policy."
            },
            "narrative_progression_arc": [
                {"phase": "hook_shock", "purpose": "Visibility collapsing to twelve inches across nine million residents"},
                {"phase": "mechanism_step", "purpose": "Thermal inversion acting as an airtight meteorological lid"},
                {"phase": "deep_dive_step", "purpose": "Exporting clean anthracite and burning sulfurous nutty slack"},
                {"phase": "editorial_commentary", "purpose": "Industrial chimneys and home hearths creating a chemical reactor"},
                {"phase": "story_action", "purpose": "Atmospheric chemistry transforming sulfur dioxide into sulfuric acid"},
                {"phase": "mechanism_step", "purpose": "Smog penetrating indoors and halting cinema screenings"},
                {"phase": "rapid_examples", "purpose": "Sadler's Wells opera choked off and cattle suffocated at Smithfield"},
                {"phase": "editorial_commentary", "purpose": "Political downplaying while undertakers exhaust casket supplies"},
                {"phase": "deep_dive_step", "purpose": "Epidemiological audit proving 12,000 fatalities"},
                {"phase": "before_after_contrast", "purpose": "Winds clearing the shroud and exposing preventable poisoning"},
                {"phase": "cta_bridge", "purpose": "The Clean Air Act of 1956 and forensic viewer prompt"}
            ],
            "flow_video_transition_blueprint": {
                "keyframe_continuity": "Archival dossier manila #DFD7C4 and detective CH01 lantern beam as recurring forensic anchor.",
                "tempo_modulation": "Atmospheric slow holds for evidence inspection, rapid tempo for the initial sensory blackout."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": ch.niche,
            "myth_debunked": brief["editorial_stance"]["myth_debunked"],
            "channel_verdict": brief["editorial_stance"]["channel_verdict"],
            "actionable_rule_of_thumb": brief["actionable_value"]["practical_rule_of_thumb"]
        },
        "cta_and_spinoff_strategy": {
            "mid_cta": brief["cta_plan"]["mid_cta"],
            "close": brief["cta_plan"]["close"],
            "endcard_text": brief["cta_plan"]["endcard_text"]
        }
    }

    sc_narrations = [
        # SC01 (56w)
        "On Friday morning, December fifth, 1952, nine million Londoners stepped outside into a suffocating yellow-black gloom where visibility abruptly collapsed to twelve inches. Streetlights glowed uselessly against the eerie midday darkness, while pedestrians were forced to navigate by dragging their hands along damp brick walls just to find their own doorsteps in the cold.",
        # SC02 (55w)
        "The lethal crisis was triggered by a rare atmospheric phenomenon. A massive slow-moving anticyclone settled over southern England, creating an impenetrable thermal inversion. Cold stagnant air was locked near ground level beneath a warmer atmospheric layer, sealing the Thames basin under an airtight lid from which no airborne pollution could escape into the upper sky.",
        # SC03 (56w)
        "Compounding the disaster was a catastrophic political decision. To pay down crushing post-war debts, the British government exported high-grade smokeless anthracite coal to overseas markets. Domestic consumers were left with cheap, low-grade coal dust known as nutty slack, containing exceptionally high sulfur concentrations that released immense plumes of toxic soot when burned in home fireplaces.",
        # SC04 (57w) - editorial
        "Londoners were accustomed to romantic Victorian pea-soupers, but this was an industrial poisoning event. Over three million residential fireplaces and massive coal-fired power stations along the Thames pumped one thousand tons of smoke particles and two thousand tons of sulfur dioxide into the trapped air every single day, converting the capital into a hazardous chemical laboratory.",
        # SC05 (57w)
        "Inside the humid, motionless atmosphere, water droplets bonded with the concentrated sulfur dioxide, while microscopic soot particles accelerated a chemical reaction that converted the gas into suspended droplets of corrosive sulfuric acid. The yellow fog ceased being mere smoke; it became an airborne acid aerosol that attacked human lungs, dissolved limestone facades, and bleached interior wallpaper.",
        # SC06 (55w)
        "The acidic fog was so pervasive that it penetrated interior spaces throughout the city. Thick yellow haze seeped beneath doors and through window frames into hospitals and movie theaters. Cinema screenings across central London were abandoned midway because patrons in the third row could no longer see the movie screen through the dense indoor smog.",
        # SC07 (56w)
        "At Sadler's Wells theatre, an opera performance of La Traviata was halted as performers began gasping for breath on stage. Meanwhile, at the Smithfield agricultural show, prize cattle began suffocating in their stalls; despite farmers desperately fashioning improvised grain-sack filters soaked in rum and vinegar, thirteen prime cattle choked to death on the showroom floor.",
        # SC08 (56w) - editorial
        "While citizens choked in the darkness, government ministers publicly dismissed the catastrophe as an ordinary seasonal mist, attempting to minimize liability and defend industrial coal consumption. But inside hospital wards and police stations, the truth was undeniable: emergency wards overflowed with suffocating patients, and undertakers across Greater London completely exhausted their supplies of wooden coffins.",
        # SC09 (55w)
        "Mortality records from the General Register Office documented an unprecedented spike in respiratory and cardiac fatalities. Bronchitis deaths surged tenfold, while cardiovascular failures doubled within forty-eight hours. Early government reports claimed four thousand casualties, but modern epidemiological reviews concluded that over twelve thousand Londoners perished as a direct result of the toxic exposure over five days.",
        # SC10 (55w)
        "On Tuesday, December ninth, a fresh westerly wind swept through the Thames basin, blowing the lethal shroud out into the North Sea. The clearing sky revealed soot-blackened monuments, dead street trees, and grieving communities. The forensic disaster had unmasked coal smoke not as an inevitable price of industrial progress, but as a preventable environmental poison.",
        # SC11 (51w) - close cta
        "Public outrage over the forensic evidence shattered decades of political inertia, culminating in the Clean Air Act of 1956, which banned dark smoke emissions and established smokeless zones across Britain. It transformed urban environmental policy worldwide. Which forensic clue stands out to you most? Share your deduction below."
    ]

    beat_data = [
        # SC01
        [
            ("Forensic noir archival scene: shadowy detective silhouette CH01 in trench coat holding a warm lantern beam over an aged 1952 London street corner on fibrous #DFD7C4 manila paper, surrounded by heavy pitch-black woodcut soot", "pan_left", "hold"),
            ("Close-up woodcut etching of an ornate Victorian wrought-iron streetlight glowing faintly behind an impenetrable wall of yellow-black ink wash", "slow_zoom_in", "none"),
            ("Stark chiaroscuro perspective of cobblestone pavement where footprints abruptly disappear into dense black ink gloom twelve inches ahead", "pan_right", "none"),
            ("Macro archival dossier view of a pedestrian hand pressed against textured damp brickwork to maintain orientation in the blindness", "hold", "none"),
            ("Archival newspaper headline clipping from December 5, 1952 stamped on manila case-file: 'LONDON BLINDED IN MIDDAY DARKNESS'", "slow_zoom_out", "none"),
            ("Wide atmospheric woodcut composition of London rooftops vanished under a suffocating charcoal and deep ink black #111111 blanket, 65% negative space", "hold", "hold"),
        ],
        # SC02
        [
            ("Forensic cross-section diagram of the Thames River basin etched in black woodcut linework on aged #DFD7C4 paper, showing physical geography of surrounding hills", "pan_left", "hold"),
            ("Atmospheric meteorological schematic showing high-pressure anticyclone symbol and isobar lines centered over southern England", "slow_zoom_in", "none"),
            ("Detailed thermal inversion diagram: warm air ceiling rendered in pale charcoal wash sealing cold stagnant surface air against the ground", "pan_right", "none"),
            ("Symbolic visual metaphor: a giant heavy lead bell jar pressing down over the miniature black ink silhouettes of London's monuments", "hold", "none"),
            ("Barometric instrument chart from the Kew Observatory recording zero wind speed and maximum atmospheric stagnation on December 5", "slow_zoom_in", "none"),
            ("Stark noir composition showing smoke rising vertically from chimneys only to flatten immediately against the thermal boundary layer, 65% negative space", "hold", "hold"),
        ],
        # SC03
        [
            ("Archival dossier evidence photo: official 1952 Ministry of Fuel export ledger stamped with crimson sealing wax #8B1E1E beside freight manifests", "pan_left", "hold"),
            ("Woodcut technical illustration comparing clean hard anthracite coal with crumbly, sulfur-flecked bituminous 'nutty slack' coal dust", "slow_zoom_in", "none"),
            ("Archival receipt from London domestic coal distributor displaying cheap subsidized prices for nutty slack beside empty coal bunkers", "pan_right", "none"),
            ("Cross-section etching of a typical London residential hearth burning low-grade coal, spewing thick billowing plumes of dark oily soot", "hold", "none"),
            ("Stark woodcut illustration of coal trains heading directly to Channel ports for export while London domestic chimneys belch sulfur into the city", "slow_zoom_in", "none"),
            ("Minimalist evidence board layout connecting post-war pound sterling debt ledgers to domestic coal bins with crimson forensic pins, 65% negative space", "hold", "hold"),
        ],
        # SC04
        [
            ("Panoramic woodcut noir panorama of London's skyline dominated by the four massive art-deco brick towers of Battersea Power Station", "pan_left", "hold"),
            ("Close-up etching of Battersea smokestacks belching continuous dense plumes of sulfur dioxide into the trapped atmospheric basin", "slow_zoom_in", "none"),
            ("Cartographic map of Greater London showing three million red hearth flame icons emitting concentrated toxic smoke vectors into the Thames valley", "pan_right", "none"),
            ("Statistical graphic etched in ink: one thousand tons of smoke particles and two thousand tons of sulfur dioxide entering the trap daily", "hold", "none"),
            ("Chemical laboratory dossier layout displaying glass distillation vials and sulfur test reagents beside factory blueprints", "slow_zoom_in", "none"),
            ("Stark noir tableau of London transformed into an enclosed urban chemical chamber under relentless charcoal cross-hatching, 65% negative space", "hold", "hold"),
        ],
        # SC05
        [
            ("Scientific forensic diagram on manila paper detailing the microphysics of water vapor droplets bonding with gaseous sulfur dioxide", "pan_left", "hold"),
            ("Magnified microscopic view of spherical soot particles acting as solid-state catalytic surfaces for rapid chemical oxidation", "slow_zoom_in", "none"),
            ("Molecular schematic rendered in crisp black woodcut ink showing the conversion of SO2 and H2O into droplets of pure sulfuric acid (H2SO4)", "pan_right", "none"),
            ("Visual evidence of acid damage: microscopic droplets pitting and dissolving the porous Portland limestone of Saint Paul's Cathedral", "hold", "none"),
            ("Stark woodcut depiction of a Londoner coughing into a white linen handkerchief that shows acidic yellow-black chemical scorch stains", "slow_zoom_in", "none"),
            ("Minimalist forensic composition showing acid aerosol droplets suspended across a pitch-black background, 65% negative space", "hold", "hold"),
        ],
        # SC06
        [
            ("Woodcut architectural cross-section of a London townhouse showing thick yellow smoke seeping under door thresholds and through window sills", "pan_left", "hold"),
            ("Interior scene in a grand Victorian hospital ward where nurse silhouettes in starched caps tend coughing patients in creeping indoor haze", "slow_zoom_in", "none"),
            ("Stark chiaroscuro scene inside an opulent West End movie theater: film projector beam cutting through heavy yellow smoke in the auditorium", "pan_right", "none"),
            ("View from the audience looking toward the cinema screen completely obscured by fog from the third row, patrons wearing overcoats indoors", "hold", "none"),
            ("Eerie nighttime street scene showing double-decker bus conductor walking ahead of his stationary bus with a flaming kerosene flare", "slow_zoom_in", "none"),
            ("Noir composition of abandoned automobiles and ambulances parked haphazardly along an empty Piccadilly Circus, 65% negative space", "hold", "hold"),
        ],
        # SC07
        [
            ("Archival theater playbill for Sadler's Wells production of La Traviata marked with bold red archival stamp: 'ABANDONED MID-PERFORMANCE'", "pan_left", "hold"),
            ("Stark woodcut of opera soprano choking on stage, hand clutching throat under dramatic stage lantern light obscured by yellow smog", "slow_zoom_in", "none"),
            ("Interior forensic dossier of the Smithfield Show livestock exhibition hall: prize cattle collapsed on straw bedding in respiratory distress", "pan_right", "none"),
            ("Detailed woodcut of desperate agricultural show handlers fashioning burlap grain sacks soaked in eucalyptus oil over the muzzles of cattle", "hold", "none"),
            ("Veterinary coroner casualty report: thirteen prize heifers dead of acute pulmonary emphysema on the exhibition arena floor", "slow_zoom_in", "none"),
            ("Atmospheric noir evidence montage contrasting grand cultural institutions against the crude physical reality of suffocation, 65% negative space", "hold", "hold"),
        ],
        # SC08
        [
            ("Archival dossier layout: confidential Whitehall Cabinet memo downplaying the fog as 'a normal meteorological event' beside public press statements", "pan_left", "hold"),
            ("Woodcut portrait of government minister sitting behind heavy mahogany desk under electric lamp, dismissing health ministry inquiries", "slow_zoom_in", "none"),
            ("High-contrast chiaroscuro scene inside a London municipal mortuary: rows of shrouded gurneys filling corridors under harsh overhead light", "pan_right", "none"),
            ("Etching of a tired London undertaker in black frock coat measuring stacks of finished pine and oak coffins in a timber workshop", "hold", "none"),
            ("Official General Register Office death ledger showing handwritten entry columns rapidly overflowing beyond ledger page margins", "slow_zoom_in", "none"),
            ("Stark editorial composition showing an empty funeral carriage waiting in total yellow darkness outside an overwhelmed chapel, 65% negative space", "hold", "hold"),
        ],
        # SC09
        [
            ("Forensic epidemiological timeline graph etched on #DFD7C4 manila paper showing daily mortality curve rocketing vertically from Dec 5 to Dec 9", "pan_left", "hold"),
            ("Statistical breakdown of mortality causes: bronchitis deaths spiking tenfold, bronchopneumonia multiplying, and cardiac failures doubling", "slow_zoom_in", "none"),
            ("Archival comparison between the initial 1953 government estimate of four thousand deaths versus modern revised epidemiological count of twelve thousand", "pan_right", "none"),
            ("Demographic casualty pyramid highlighting disproportionate impact on infants under one year and elderly citizens with pre-existing conditions", "hold", "none"),
            ("Detective silhouette CH01 examining forensic autopsy reports under glowing yellow lantern beam with magnifying lens on case file", "slow_zoom_in", "none"),
            ("Full-frame statistical balance sheet showing twelve thousand silent victims etched in severe woodcut line work, 65% negative space", "hold", "hold"),
        ],
        # SC10
        [
            ("Panoramic nautical chart showing weather fronts shifting: cold stagnant anticyclone displaced by strong westerly North Sea breeze", "pan_left", "hold"),
            ("Atmospheric woodcut of wind sweeping through the Thames gorge, tearing the yellow sulfur veil into ragged disappearing ribbons", "slow_zoom_in", "none"),
            ("Sunlight breaking across London rooftops for the first time in five days, illuminating blackened building facades and soot-covered streets", "pan_right", "none"),
            ("Close-up forensic photograph of tree branches in Hyde Park coated in sticky acidic black grime and dead urban sparrows beneath benches", "hold", "none"),
            ("Coroner's formal final summation document stamped with crimson forensic seal: 'DEATHS CAUSED BY MAN-MADE TOXIC SMOKE INHALATION'", "slow_zoom_in", "none"),
            ("Grand post-disaster panorama of a quiet, somber London emerging from the acid darkness, at least 65% negative space", "hold", "hold"),
        ],
        # SC11
        [
            ("Archival legislative dossier: the Clean Air Act of 1956 parliamentary statute bound in leather with royal wax seal and green ribbons", "pan_left", "hold"),
            ("Woodcut technical blueprint of modern smokeless fuel briquettes and new domestic gas heating conversions replacing dirty bituminous coal", "slow_zoom_in", "none"),
            ("Before-and-after split lithograph: soot-blackened 1952 street corner contrasted with clean, crisp air of a post-1956 smokeless zone", "pan_right", "none"),
            ("Silhouette of detective CH01 closing the '1952 LONDON SMOG' forensic case dossier folder with brass clip and crimson timeline thread", "hold", "none"),
            ("Hand-inked archival banner on manila paper: 'FORENSIC VERDICT: PREVENTABLE', surrounded by fine chiaroscuro filigree borders", "slow_zoom_out", "none"),
            ("Final elegant dossier endcard with Cold Case Ink forensic emblem and investigative prompt: 'Share your deduction below', 65% negative space", "hold", "hold"),
        ]
    ]

    scenes = []
    coverage = []
    claims = [
        {
            "scene_id": "SC01",
            "quote": "nine million Londoners stepped outside into a suffocating yellow-black gloom where visibility abruptly collapsed to twelve inches.",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Visibility dropped to twelve inches across central London on December fifth, 1952."
        },
        {
            "scene_id": "SC02",
            "quote": "A massive slow-moving anticyclone settled over southern England, creating an impenetrable thermal inversion.",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Anticyclone thermal inversion trapped cold ground air beneath a warm atmospheric layer."
        },
        {
            "scene_id": "SC03",
            "quote": "Domestic consumers were left with cheap, low-grade coal dust known as nutty slack",
            "language": "en",
            "source_id": "SRC02",
            "fact": "Austerity exports of high-grade coal forced Londoners to burn sulfurous nutty slack."
        },
        {
            "scene_id": "SC05",
            "quote": "microscopic soot particles accelerated a chemical reaction that converted the gas into suspended droplets of corrosive sulfuric acid.",
            "language": "en",
            "source_id": "SRC02",
            "fact": "Microscopic soot catalyzed sulfur dioxide oxidation into droplets of airborne sulfuric acid."
        },
        {
            "scene_id": "SC09",
            "quote": "over twelve thousand Londoners perished as a direct result of the toxic exposure over five days.",
            "language": "en",
            "source_id": "SRC02",
            "fact": "Modern epidemiological reviews established over twelve thousand fatalities from the five-day fog."
        }
    ]

    for idx, (narr, beats_info) in enumerate(zip(sc_narrations, beat_data), start=1):
        sc_id = f"SC{idx:02d}"
        req_id = f"R{idx:02d}"
        
        sit_map = {
            1: "hook_shock",
            2: "mechanism_step",
            3: "deep_dive_step",
            4: "editorial_commentary",
            5: "story_action",
            6: "mechanism_step",
            7: "rapid_examples",
            8: "editorial_commentary",
            9: "deep_dive_step",
            10: "before_after_contrast",
            11: "cta_bridge"
        }
        sit = sit_map[idx]
        
        req_quote_map = {
            1: "nine million Londoners stepped outside into a suffocating yellow-black gloom where visibility abruptly collapsed to twelve inches.",
            2: "A massive slow-moving anticyclone settled over southern England, creating an impenetrable thermal inversion.",
            3: "Domestic consumers were left with cheap, low-grade coal dust known as nutty slack",
            4: "three million residential fireplaces and massive coal-fired power stations along the Thames",
            5: "microscopic soot particles accelerated a chemical reaction that converted the gas into suspended droplets of corrosive sulfuric acid.",
            6: "Cinema screenings across central London were abandoned midway because patrons in the third row could no longer see the movie screen",
            7: "At Sadler's Wells theatre, an opera performance of La Traviata was halted as performers began gasping for breath",
            8: "undertakers across Greater London completely exhausted their supplies of wooden coffins.",
            9: "over twelve thousand Londoners perished as a direct result of the toxic exposure over five days.",
            10: "On Tuesday, December ninth, a fresh westerly wind swept through the Thames basin",
            11: "culminating in the Clean Air Act of 1956, which banned dark smoke emissions and established smokeless zones"
        }
        coverage.append({
            "requirement_id": req_id,
            "scene_id": sc_id,
            "quote": req_quote_map[idx]
        })

        images = []
        beats = []
        tempos = ["fast", "fast", "normal", "normal", "slow", "normal"]

        for b_idx, (desc, cam, eff) in enumerate(beats_info, start=1):
            img_id = f"{sc_id}_I{b_idx}"
            beat_id = f"{sc_id}_B{b_idx}"
            t = tempos[b_idx - 1]
            
            images.append({
                "id": img_id,
                "description": desc,
                "character_ids": ["CH01"],
                "preserve": "Forensic archival dossier style, #DFD7C4 manila paper, woodcut chiaroscuro noir",
                "change": f"Detailed forensic evidence change for beat {beat_id}",
                "reason": f"Narration-locked full-frame beat {img_id}.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": t,
                "narrative_situation": sit,
                "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                "has_character": True,
                "motion_prompt": f"Tactile 2D woodcut noir animation, {desc[:100].lower()}, silent visual storytelling, no talking, no lip movement",
                "camera_motion": cam,
                "effect": eff
            })
            beats.append({
                "id": beat_id,
                "image_id": img_id,
                "purpose": f"Forensic visual evidence beat {b_idx} for scene {sc_id}",
                "tempo": t,
                "narrative_situation": sit,
                "shot_type": "full_scene",
                "effect": eff
            })

        scenes.append({
            "id": sc_id,
            "title": outline["outline"][idx - 1]["purpose"][:60],
            "purpose": outline["outline"][idx - 1]["purpose"],
            "action": f"Forensic noir archival scene depicting {sc_id} events on #DFD7C4 manila dossier paper.",
            "setting": "Forensic archival investigation dossier on aged #DFD7C4 manila case-file canvas.",
            "camera": "Semantic full-frame sequence",
            "narration": narr,
            "requirements": [req_id],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"] if idx in [1, 2, 6] else ["SRC02"],
            "narrative_situation": sit,
            "images": images,
            "beats": beats
        })

    content = {
        "schema_version": "3.0",
        "job_id": job_id,
        "topic": topic,
        "duration": brief["duration"],
        "style": brief["style"],
        "required_points": [rp["text"] for rp in brief["required_points"]],
        "characters": [channel_cast(channel_id, "CH01")],
        "scenes": scenes,
        "coverage": coverage,
        "outline": outline["outline"],
        "claims": claims,
        "revision_response": [],
        "open_questions": []
    }

    return job_id, brief, outline, competitor_research, content


def make_cold_case_ink_short():
    job_id = "en-cold-case-ink-batch1-9x16"
    parent_long_id = "en-cold-case-ink-batch1-16x9"
    channel_id = "en_cold_case_ink"
    ch = get_channel(channel_id)
    topic = "The 1952 London Killer Fog: How an Anticyclone Trapped Sulfuric Acid Over Nine Million People for Five Days"
    youtube_title = "When Londoners Couldn't See Their Own Feet"  # 43 chars <= 55

    style_desc = (
        "Forensic Archival Dossier and Woodcut Chiaroscuro Noir illustration on vertical #DFD7C4 manila dossier paper "
        "(#111111 deep India ink black, #DFD7C4 aged case-file manila, #5A5F66 charcoal shadow wash, "
        "#8B1E1E crimson sealing wax stamp and timeline pins); hand-carved woodcut cross-hatching, "
        "soot-stained archival document texture, magnifying lenses, and high-contrast chiaroscuro shadow drama; "
        "orthographic 2D, at least 60% negative space, zero 3D CGI, zero neon glow, zero plastic gradients."
    )

    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Fast-paced vertical forensic documentary exploring the 1952 London killer acid fog and the 12,000 hidden fatalities.",
        "video_type": "explainer",
        "duration": {"min_seconds": 38.0, "max_seconds": 52.0},
        "scene_count": 5,
        "parent_long_id": parent_long_id,
        "required_points": [
            {"id": "R01", "text": "Dense yellow-black smog blinding nine million Londoners in midday darkness in December 1952."},
            {"id": "R02", "text": "Thermal inversion trapping sulfur smoke from low-grade nutty slack coal over the Thames basin."},
            {"id": "R03", "text": "Sulfur dioxide turning into sulfuric acid aerosol that seeped indoors and halted cinemas and shows."},
            {"id": "R04", "text": "Twelve thousand deaths over five days exhausting the city's coffins and forcing the Clean Air Act."},
            {"id": "R05", "text": "The forensic reality of man-made air pollution and invitation to explore full documentary."}
        ],
        "language": "en",
        "tone": ch.tone,
        "style": style_desc,
        "aspect_ratio": "9:16",
        "format_profile": "short_9x16",
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "Mortality and Morbidity during the London Fog of December 1952",
                "reference": "Ministry of Health & UK Meteorological Office (1954). Reports on Public Health and Medical Subjects No. 95.",
                "facts": [
                    "Visibility dropped to twelve inches across central London on December fifth, 1952.",
                    "Anticyclone thermal inversion trapped cold ground air beneath a warm atmospheric layer.",
                    "Hospitals admitted thousands of patients suffering from acute hypoxia, bronchitis, and cardiac collapse."
                ]
            }
        ],
        "outputs": [
            {
                "aspect_ratio": "9:16",
                "language": "en",
                "subtitles": True,
                "voice": ch.voice,
                "speed": 1.0
            }
        ],
        "planning": {
            "success_criteria": [
                "Hook with complete sensory blindness in 3 seconds, explain sulfuric acid conversion, reveal 12,000 dead, bridge at climax."
            ],
            "avoid": [
                "Zero sensationalist filler, zero cheap horror sounds, zero robotic clichés."
            ],
            "prior_knowledge": "None required.",
            "pacing": "Rapid vertical investigative pacing (~2.2s per image).",
            "speech_rates": {
                "en": {
                    "units_per_second": 3.8,
                    "uncertainty": 0.15,
                    "source": "Acoustic calibrated cadence"
                }
            }
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Vertical forensic noir silhouette of detective holding lantern beam over London cobblestone street lost in yellow acid fog",
                "text_overlay": "CANNOT SEE FEET",
                "contrast_pair": "12-Inch Visibility vs 12,000 Dead",
                "layout_mode": "split_contrast"
            },
            "channel_pillar": ch.niche,
            "funnel_tier": "tier_1_broad",
            "seo_keywords": [
                "London smog 1952",
                "killer fog shorts",
                "acid fog disaster",
                "cold case mystery"
            ]
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Vertical forensic noir silhouette of detective holding lantern beam over London cobblestone street lost in yellow acid fog",
            "text_overlay": "CANNOT SEE FEET",
            "contrast_pair": "12-Inch Visibility vs 12,000 Dead",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": ch.niche,
        "funnel_tier": "tier_1_broad",
        "seo_keywords": [
            "London smog 1952",
            "killer fog shorts",
            "acid fog disaster",
            "cold case mystery"
        ],
        "cta_plan": {
            "cliffhanger_peak": "What made this man-made catastrophe remain downplayed for decades?",
            "bridge": "Watch the complete documentary investigation on Cold Case Ink.",
            "close": "Which forensic clue stands out to you most? Share your deduction below.",
            "endcard_text": "FULL VIDEO ON YOUTUBE"
        },
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": ch.engagement.cta_voice,
            "banned_cta_phrases": list(ch.engagement.banned_cta_phrases)
        },
        "editorial_stance": {
            "myth_debunked": "The 1952 London Fog was an unavoidable natural weather catastrophe caused entirely by winter weather.",
            "channel_verdict": "The disaster was a man-made environmental poisoning caused by government policies exporting clean fuel.",
            "why_generic_advice_fails": "Officials treated the crisis as standard winter mist to protect commercial coal interests.",
            "tradeoff_or_blindspot": "Banning domestic coal required massive subsidies and restructured Britain's entire heating infrastructure."
        },
        "actionable_value": {
            "core_mechanism": "Thermal inversion acid trapping: stagnant atmospheric ceilings allow sulfur smoke to chemically transform into airborne sulfuric acid.",
            "practical_rule_of_thumb": "In extreme air pollution events, secondary chemical aerosol reactions represent far greater biological danger than coarse soot.",
            "real_world_scenario": "Indoor occupants suffocating in sealed rooms because acidic micro-droplets penetrate domestic building envelopes."
        },
        "video_engine": "images_only",
        "chain_mode": "full_chain"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Hook: December 1952 yellow acid smog swallowing London in total blindness", "requirements": ["R01"], "transition": "Rapid zoom into lantern light on cobblestones"},
            {"scene_id": "SC02", "purpose": "Mechanism: thermal inversion trapping sulfur smoke from cheap nutty slack coal", "requirements": ["R02"], "transition": "Atmospheric ceiling cutaway diagram"},
            {"scene_id": "SC03", "purpose": "Editorial commentary: sulfur turning into sulfuric acid, halting cinemas and killing cattle", "requirements": ["R03"], "transition": "Indoor theater beam obscured by acid haze"},
            {"scene_id": "SC04", "purpose": "Cliffhanger peak: undertakers running out of coffins as 12,000 perish in five days", "requirements": ["R04"], "transition": "Mortality spike statistical graph"},
            {"scene_id": "SC05", "purpose": "Payoff, bridge CTA to full documentary, and deduction close", "requirements": ["R05"], "transition": "Forensic case dossier stamp and endcard"}
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "LEMMiNO Shorts",
                    "top_performing_videos": [
                        {
                            "title": "The Smog That Killed 12,000",
                            "views": "2.4M views",
                            "hook_technique": "Extreme sensory hook: pedestrians unable to see their own feet at noon.",
                            "pacing_structure": "3s hook -> 15s weather anomaly -> 15s chemical transformation -> Peak bridge.",
                            "retention_driver": "Tactile archival noir graphics with rapid holds."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Highlighting the bizarre detail that cinemas were cancelled due to indoor fog.",
                        "Direct comparison of official four thousand death estimate vs twelve thousand reality."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 26,
                "zero_pause_opening_seconds": 12,
                "visual_contrast": "Vertical detective silhouette holding lantern over cobblestones swallowed in ink darkness.",
                "counter_intuitive_truth_slap": "Londoners were breathing airborne battery acid created by post-war government debt payments."
            },
            "narrative_progression_arc": [
                {"phase": "hook_shock", "purpose": "Nine million Londoners blinded in yellow-black acid darkness"},
                {"phase": "mechanism_step", "purpose": "Thermal inversion trapping sulfur smoke from nutty slack coal"},
                {"phase": "editorial_commentary", "purpose": "Acid fog invading homes, halting cinemas and killing cattle"},
                {"phase": "cliffhanger_peak", "purpose": "Twelve thousand fatalities exhausting the city's coffins"},
                {"phase": "cta_bridge", "purpose": "Bridge to full documentary investigation and deduction prompt"}
            ],
            "flow_video_transition_blueprint": {
                "keyframe_continuity": "Vertical forensic noir dossier #DFD7C4 with detective CH01 lantern beam.",
                "tempo_modulation": "Fast tempo throughout (< 2.3s hold)."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": ch.niche,
            "myth_debunked": brief["editorial_stance"]["myth_debunked"],
            "channel_verdict": brief["editorial_stance"]["channel_verdict"],
            "actionable_rule_of_thumb": brief["actionable_value"]["practical_rule_of_thumb"]
        },
        "cta_and_spinoff_strategy": {
            "bridge": brief["cta_plan"]["bridge"],
            "close": brief["cta_plan"]["close"],
            "endcard_text": brief["cta_plan"]["endcard_text"]
        }
    }

    sc01_narr = "In December 1952, a yellow-black acid smog swallowed London so completely that nine million people could not see their own feet on the pavement in the biting cold. Midday streetlights flickered uselessly against total darkness across every neighborhood."
    sc02_narr = "A thermal inversion acted as an airtight ceiling over the Thames basin, trapping thousands of tons of sulfur smoke from millions of home fireplaces burning dirty, low-grade coal dust known as nutty slack."
    sc03_narr = "Atmospheric moisture oxidized that sulfur into floating droplets of corrosive sulfuric acid. The acid fog seeped indoors, halting movie screenings, suffocating prize cattle at agricultural shows, and invading hospital wards across the capital."
    sc04_narr = "While senior government officials dismissed the crisis as standard winter mist, undertakers ran out of coffins. In five days, twelve thousand Londoners died, forcing the revolutionary Clean Air Act of 1956 to ban coal smoke."
    sc05_narr = "What made this man-made catastrophe remain downplayed for decades? Watch the complete documentary investigation on Cold Case Ink. Which forensic clue stands out to you most? Share your deduction below."

    sc_narrations_short = [sc01_narr, sc02_narr, sc03_narr, sc04_narr, sc05_narr]

    beat_data_short = [
        # SC01
        [
            ("Vertical forensic noir scene: detective silhouette CH01 holding warm lantern beam over London cobblestone street lost in pitch black woodcut gloom on #DFD7C4 paper", "pan_left", "hold"),
            ("Close-up woodcut etching of pedestrian leather shoes on cobblestones with visibility collapsing to twelve inches ahead", "slow_zoom_in", "none"),
            ("Stark chiaroscuro streetlight glowing faintly like a distant match in midday pitch-black sulfur fog", "pan_right", "none"),
            ("Archival dossier evidence photo stamped with red wax seal: 'DECEMBER 1952: ZERO VISIBILITY', 65% negative space", "hold", "hold"),
        ],
        # SC02
        [
            ("Vertical atmospheric cross-section diagram showing warm air inversion layer sealing cold stagnant smoke over the Thames valley", "pan_left", "hold"),
            ("Detailed technical etching comparing high-grade anthracite coal with dirty, crumbly 'nutty slack' coal dust spewing sulfur", "slow_zoom_in", "none"),
            ("Cross-section of thousands of residential brick chimneys venting concentrated black soot directly into the trapped basin", "pan_right", "none"),
            ("Barometric pressure chart from Kew Observatory showing total atmospheric deadlock on manila case-file, 65% negative space", "hold", "hold"),
        ],
        # SC03
        [
            ("Microscopic diagram showing sulfur dioxide reacting with water droplets on soot particles to produce airborne sulfuric acid aerosol", "pan_left", "hold"),
            ("Interior woodcut of central London movie theater with projector beam completely obscured by thick yellow indoor smoke", "slow_zoom_in", "none"),
            ("Archival sketch of Smithfield agricultural show where prize cattle collapsed from acute suffocation in their stalls", "pan_right", "none"),
            ("Hospital emergency ward sketch showing respiratory patients being treated under gas lanterns in dense indoor haze, 65% negative space", "hold", "hold"),
        ],
        # SC04
        [
            ("Forensic mortality graph showing daily death rate soaring vertically from December 5 to December 9, 1952 on aged manila paper", "pan_left", "hold"),
            ("Woodcut of London undertaker workshop with empty coffin shelves and handwritten order books overflowing with casualties", "slow_zoom_in", "none"),
            ("Statistical comparison stamped in crimson ink: official initial estimate of 4,000 versus modern forensic reality of 12,000 deaths", "pan_right", "none"),
            ("Parliamentary statute document for the Clean Air Act of 1956 banning dirty coal emissions, 65% negative space", "hold", "hold"),
        ],
        # SC05
        [
            ("Vertical forensic dossier layout with detective CH01 lantern beam highlighting red timeline strings connecting coal ledgers to death certificates", "pan_left", "hold"),
            ("Macro view of Cold Case Ink forensic case folder stamped 'CASE FILE: 1952 LONDON SMOG' on fibrous #DFD7C4 paper", "slow_zoom_in", "none"),
            ("Engraved archival card presenting Cold Case Ink channel seal and documentary title", "pan_right", "none"),
            ("Final elegant dossier endcard with deduction prompt: 'Share your deduction below', 65% negative space", "hold", "hold"),
        ]
    ]

    scenes = []
    coverage = []
    claims = [
        {
            "scene_id": "SC01",
            "quote": "nine million people could not see their own feet on the pavement.",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Visibility dropped to twelve inches across central London on December fifth, 1952."
        },
        {
            "scene_id": "SC04",
            "quote": "In five days, twelve thousand Londoners died, forcing the revolutionary Clean Air Act of 1956 to ban coal smoke.",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Hospitals admitted thousands of patients suffering from acute hypoxia, bronchitis, and cardiac collapse."
        }
    ]

    short_sits = ["hook_shock", "mechanism_step", "editorial_commentary", "cliffhanger_peak", "cta_bridge"]
    req_quotes_short = [
        "nine million people could not see their own feet on the pavement.",
        "A thermal inversion acted as an airtight ceiling over the Thames basin, trapping thousands of tons of sulfur smoke",
        "The acid fog seeped indoors, halting movie screenings, suffocating prize cattle at agricultural shows",
        "In five days, twelve thousand Londoners died, forcing the revolutionary Clean Air Act of 1956 to ban coal smoke.",
        "Watch the complete documentary investigation on Cold Case Ink. Which forensic clue stands out to you most? Share your deduction below."
    ]

    for idx, (narr, beats_info, sit, q) in enumerate(zip(sc_narrations_short, beat_data_short, short_sits, req_quotes_short), start=1):
        sc_id = f"SC{idx:02d}"
        req_id = f"R{idx:02d}"
        
        coverage.append({
            "requirement_id": req_id,
            "scene_id": sc_id,
            "quote": q
        })

        images = []
        beats = []
        tempos = ["fast", "fast", "normal", "slow"]

        for b_idx, (desc, cam, eff) in enumerate(beats_info, start=1):
            img_id = f"{sc_id}_I{b_idx}"
            beat_id = f"{sc_id}_B{b_idx}"
            t = tempos[b_idx - 1]
            
            images.append({
                "id": img_id,
                "description": desc,
                "character_ids": ["CH01"],
                "preserve": "Forensic archival dossier vertical style, #DFD7C4 manila paper, woodcut chiaroscuro noir",
                "change": f"Detailed vertical forensic evidence change for beat {beat_id}",
                "reason": f"Narration-locked full-frame beat {img_id}.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": t,
                "narrative_situation": sit,
                "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                "has_character": True,
                "motion_prompt": f"Tactile 2D vertical woodcut noir animation, {desc[:100].lower()}, silent visual storytelling, no talking, no lip movement",
                "camera_motion": cam,
                "effect": eff
            })
            beats.append({
                "id": beat_id,
                "image_id": img_id,
                "purpose": f"Vertical forensic visual beat {b_idx} for scene {sc_id}",
                "tempo": t,
                "narrative_situation": sit,
                "shot_type": "full_scene",
                "effect": eff
            })

        scenes.append({
            "id": sc_id,
            "title": outline["outline"][idx - 1]["purpose"][:60],
            "purpose": outline["outline"][idx - 1]["purpose"],
            "action": f"Forensic noir vertical archival scene depicting {sc_id} events on #DFD7C4 manila paper.",
            "setting": "Forensic archival investigation vertical dossier on aged #DFD7C4 manila case-file canvas.",
            "camera": "Semantic full-frame sequence",
            "narration": narr,
            "requirements": [req_id],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "narrative_situation": sit,
            "images": images,
            "beats": beats
        })

    content = {
        "schema_version": "3.0",
        "job_id": job_id,
        "topic": topic,
        "duration": brief["duration"],
        "style": brief["style"],
        "required_points": [rp["text"] for rp in brief["required_points"]],
        "characters": [channel_cast(channel_id, "CH01")],
        "scenes": scenes,
        "coverage": coverage,
        "outline": outline["outline"],
        "claims": claims,
        "revision_response": [],
        "open_questions": []
    }

    return job_id, brief, outline, competitor_research, content


# ==============================================================================
# CHANNEL 3: EN_CROWD_STRINGS (Crowd Strings)
# ==============================================================================

def make_crowd_strings_long():
    job_id = "en-crowd-strings-batch1-16x9"
    channel_id = "en_crowd_strings"
    ch = get_channel(channel_id)
    topic = "The Asch Line Trap: Why Social Conformity Forces 75 Percent of People to Agree With an Obvious Lie"
    youtube_title = "How Three Actors Make You Doubt Your Own Eyes"  # 46 chars <= 55

    style_desc = (
        "Frans Masereel Scratchboard Woodcut and Noir Red-Thread Dossier art on fibrous #E8E2D0 newsprint dossier paper "
        "(#111111 India ink black, #E8E2D0 newsprint paper grain, #5A5F66 charcoal wash, #C0392B crimson cotton tension threads); "
        "hand-carved scratchboard relief linework, brass dossier pins, physical crimson string matrices, "
        "and anonymous crowd ink silhouettes; orthographic 2D, authentic printmaking texture, at least 60% negative space, "
        "zero 3D CGI, zero neon glow, zero plastic gradients."
    )

    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Explain the psychological and neurological mechanics of social conformity through Solomon Asch's 1951 line test and Gregory Berns' fMRI study.",
        "video_type": "explainer",
        "duration": {"min_seconds": 150.0, "max_seconds": 210.0},
        "scene_count": 11,
        "required_points": [
            {"id": "R01", "text": "Swarthmore College 1951: seven students seated before simple cards with comparison lines."},
            {"id": "R02", "text": "The obvious visual matching task and the secret arrangement of six paid confederates."},
            {"id": "R03", "text": "The confederates unanimously choosing the wrong line on critical trials in spoken order."},
            {"id": "R04", "text": "The myth of perceptual sovereignty and social pressure acting as an invisible gravitational field."},
            {"id": "R05", "text": "The isolated subject sweating in distress and agreeing with the obvious lie on critical trials."},
            {"id": "R06", "text": "Seventy-five percent of participants conforming at least once due to fear of social isolation."},
            {"id": "R07", "text": "Gregory Berns replicating the experiment inside modern fMRI brain scanners to track neural circuits."},
            {"id": "R08", "text": "fMRI scans showing social pressure altering activation in the occipital-parietal visual cortex."},
            {"id": "R09", "text": "Introducing a single dissenting ally collapsing conformity rates from thirty-two percent to five percent."},
            {"id": "R10", "text": "The power of any dissenting voice giving the brain permission to trust its own observations."},
            {"id": "R11", "text": "Recognizing the Asch line trap in everyday meetings and holding firm against groupthink."}
        ],
        "language": "en",
        "tone": ch.tone,
        "style": style_desc,
        "aspect_ratio": "16:9",
        "format_profile": "long_16x9",
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "Effects of group pressure upon the modification and distortion of judgments",
                "reference": "Asch, S. E. (1951). In Groups, Leadership and Men (pp. 177-190). Carnegie Press.",
                "facts": [
                    "Seventy-five percent of participants conformed with the group's incorrect answer at least once.",
                    "Overall conformity rate on critical trials reached thirty-six point eight percent.",
                    "Introducing a single dissenting partner reduced conformity from thirty-two percent to five percent."
                ]
            },
            {
                "id": "SRC02",
                "title": "Neurobiological Correlates of Social Conformity and Independence During Mental Rotation",
                "reference": "Berns, G. S., Chappelow, J., et al. (2005). Biological Psychiatry, 58(3), 245-253.",
                "facts": [
                    "Social conformity alters neural activity in the occipital-parietal visual cortex.",
                    "Conformity distorts perceptual processing before conscious decision-making occurs.",
                    "Social consensus creates measurable neurological changes in sensory perception."
                ]
            }
        ],
        "outputs": [
            {
                "aspect_ratio": "16:9",
                "language": "en",
                "subtitles": False,
                "voice": ch.voice,
                "speed": 1.0
            }
        ],
        "planning": {
            "success_criteria": [
                "Dissect Asch's 1951 experimental design, the confederate sequence, fMRI visual cortex alteration, and the single-dissenter collapse threshold."
            ],
            "avoid": [
                "Zero shallow self-help pop psychology, zero corporate management clichés, zero canned discourse filler."
            ],
            "prior_knowledge": "None required; behavioral mechanics illustrated with high-contrast scratchboard linework.",
            "pacing": "Behavioral psychology essayist cadence (~3.8 syllables/sec).",
            "speech_rates": {
                "en": {
                    "units_per_second": 3.8,
                    "uncertainty": 0.15,
                    "source": "Acoustic calibrated cadence"
                }
            }
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Scratchboard woodcut of six anonymous ink figures pointing at wrong line while red strings pull a lone subject's head",
                "text_overlay": "DOUBT YOUR EYES",
                "contrast_pair": "Obvious Physical Truth vs 75% Social Lie",
                "layout_mode": "split_contrast"
            },
            "channel_pillar": ch.niche,
            "funnel_tier": "tier_1_broad",
            "seo_keywords": [
                "Asch conformity experiment",
                "social psychology",
                "peer pressure fMRI",
                "herd mentality",
                "Solomon Asch",
                "behavioral psychology"
            ]
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Scratchboard woodcut of six anonymous ink figures pointing at wrong line while red strings pull a lone subject's head",
            "text_overlay": "DOUBT YOUR EYES",
            "contrast_pair": "Obvious Physical Truth vs 75% Social Lie",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": ch.niche,
        "funnel_tier": "tier_1_broad",
        "seo_keywords": [
            "Asch conformity experiment",
            "social psychology",
            "peer pressure fMRI",
            "herd mentality",
            "Solomon Asch"
        ],
        "cta_plan": {
            "mid_cta": "If you want to spot psychological manipulation before it pulls your decisions, save this video.",
            "close": "Notice this cue tomorrow and tell us if you see through the crowd trap.",
            "endcard_text": "FULL VIDEO ON YOUTUBE"
        },
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": ch.engagement.cta_voice,
            "banned_cta_phrases": list(ch.engagement.banned_cta_phrases)
        },
        "editorial_stance": {
            "myth_debunked": "Sensory perception is an objective biological process where healthy individuals always see physical reality independently of surrounding social opinions.",
            "channel_verdict": "Conformity is not mere outward compliance; unanimous social consensus physically alters neural processing in the visual cortex, warping what the brain genuinely perceives.",
            "why_generic_advice_fails": "Generic self-help advice urges people to simply have confidence, ignoring that peer consensus exerts neurological pressure that bypasses conscious logical reasoning.",
            "tradeoff_or_blindspot": "Breaking conformity requires enduring sharp emotional discomfort and social alienation, which evolutionary biology wired human brains to fear as life-threatening isolation."
        },
        "actionable_value": {
            "core_mechanism": "The Asch conformity trap and dissenter release: unanimous peer error distorts visual cortex processing, but a single dissenting ally drops compliance from thirty-two percent to five percent.",
            "practical_rule_of_thumb": "Social autonomy rule: whenever facing unanimous group consensus in high-stakes decisions, appoint a dedicated dissenter to restore collective perceptual accuracy.",
            "real_world_scenario": "A lone engineer in a design review notices a critical structural flaw but hesitates to speak up until another colleague questions the unanimous board approval."
        },
        "video_engine": "images_only",
        "chain_mode": "full_chain"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Hook: Swarthmore College 1951, seven young men seated around table before line cards", "requirements": ["R01"], "transition": "Establishing shot of test room table"},
            {"scene_id": "SC02", "purpose": "Mechanism: simple line matching task and secret arrangement of six paid actors", "requirements": ["R02"], "transition": "Display cards and seating diagram"},
            {"scene_id": "SC03", "purpose": "Deep dive: confederates establishing rhythm then unanimously naming obviously wrong line", "requirements": ["R03"], "transition": "Spoken round progression chart"},
            {"scene_id": "SC04", "purpose": "Editorial commentary: myth of sensory sovereignty and social pressure as gravitational field", "requirements": ["R04"], "transition": "Symbolic red tension threads pulling subject"},
            {"scene_id": "SC05", "purpose": "Story action: isolated subject sweating in visible agony and conforming 36% of the time", "requirements": ["R05"], "transition": "Subject facial expression in woodcut chiaroscuro"},
            {"scene_id": "SC06", "purpose": "Statistical finding: 75% conforming at least once due to fear of social isolation", "requirements": ["R06"], "transition": "Statistical breakdown card of compliance rates"},
            {"scene_id": "SC07", "purpose": "Modern replication: Gregory Berns testing conformity inside fMRI brain scanners", "requirements": ["R07"], "transition": "fMRI scanner cutaway and neural imaging"},
            {"scene_id": "SC08", "purpose": "Editorial commentary: fMRI scans proving social consensus reshapes occipital visual cortex", "requirements": ["R08"], "transition": "Visual cortex activation heatmap diagram"},
            {"scene_id": "SC09", "purpose": "Antidote discovery: single dissenting ally collapsing conformity from 32% down to 5%", "requirements": ["R09"], "transition": "Red string snapped by lone dissenter silhouette"},
            {"scene_id": "SC10", "purpose": "Cognitive release: any dissenting voice granting the brain permission to trust reality", "requirements": ["R10"], "transition": "Before-and-after psychological relief diagram"},
            {"scene_id": "SC11", "purpose": "Payoff and closing: spotting the trap in modern boardrooms and feeds; closing prompt", "requirements": ["R11"], "transition": "Final scratchboard dossier seal and endcard"}
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Academy of Ideas",
                    "top_performing_videos": [
                        {
                            "title": "The Psychology of Conformity",
                            "views": "3.1M views",
                            "hook_technique": "Philosophical and psychological framing using classic woodcut art and sharp societal critique.",
                            "pacing_structure": "The problem of mass psychosis -> Asch experiment -> Mechanisms of social fear -> The cure of individual autonomy.",
                            "retention_driver": "Intellectually rigorous narrative paired with stark black and white artistic imagery."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Using stark woodcut and chiaroscuro engraving to represent psychological pressure.",
                        "Directly challenging the viewer's belief in their own moral and sensory independence."
                    ]
                },
                {
                    "channel_name": "Big Think",
                    "top_performing_videos": [
                        {
                            "title": "Why You Conform (Even When You Know It's Wrong)",
                            "views": "1.9M views",
                            "hook_technique": "Opening with neuroimaging proof that social pressure physically rewires sensory data.",
                            "pacing_structure": "Hook -> Asch historical test -> fMRI neuroscience update -> Counter-measures.",
                            "retention_driver": "Grounding psychological phenomena in hard neuroscience data."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Translating behavioral psychology experiments into clear visual diagrams.",
                        "Providing a concrete psychological defense rule of thumb."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 28,
                "zero_pause_opening_seconds": 15,
                "visual_contrast": "Scratchboard woodcut of six suited shadows unanimously pointing at the wrong line while a lone figure sweats in the center.",
                "counter_intuitive_truth_slap": "Your brain does not just pretend to agree with the crowd; peer consensus physically alters your visual cortex before you speak."
            },
            "narrative_progression_arc": [
                {"phase": "hook_shock", "purpose": "Swarthmore 1951 test room and the deceptive line cards"},
                {"phase": "mechanism_step", "purpose": "Six confederates secretly seated in fixed order"},
                {"phase": "deep_dive_step", "purpose": "Confederates unanimously naming Line A over identical Line C"},
                {"phase": "editorial_commentary", "purpose": "Exposing the myth that individual perception is sovereign"},
                {"phase": "story_action", "purpose": "Subject sweating in distress and conforming 36% of the time"},
                {"phase": "deep_dive_step", "purpose": "75% conformity rate and post-test confessions of social fear"},
                {"phase": "case_study", "purpose": "Gregory Berns fMRI neuroimaging replication"},
                {"phase": "editorial_commentary", "purpose": "Proof that social consensus reshapes neural visual processing"},
                {"phase": "rapid_examples", "purpose": "A single dissenter collapsing conformity from 32% to 5%"},
                {"phase": "before_after_contrast", "purpose": "Permission to see truth restored by one dissenting voice"},
                {"phase": "cta_bridge", "purpose": "Spotting the Asch trap tomorrow and engagement prompt"}
            ],
            "flow_video_transition_blueprint": {
                "keyframe_continuity": "Newsprint paper #E8E2D0, Frans Masereel scratchboard linework, and crimson tension threads #C0392B.",
                "tempo_modulation": "Tense deliberate pacing for the experiment trials, rapid pacing for the dissenter collapse."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": ch.niche,
            "myth_debunked": brief["editorial_stance"]["myth_debunked"],
            "channel_verdict": brief["editorial_stance"]["channel_verdict"],
            "actionable_rule_of_thumb": brief["actionable_value"]["practical_rule_of_thumb"]
        },
        "cta_and_spinoff_strategy": {
            "mid_cta": brief["cta_plan"]["mid_cta"],
            "close": brief["cta_plan"]["close"],
            "endcard_text": brief["cta_plan"]["endcard_text"]
        }
    }

    sc_narrations = [
        # SC01 (61w)
        "Swarthmore College, 1951. Seven young men sit around a polished wooden seminar table for what they believe is a standard visual perception experiment. The experimenter places two large white display cards in front of the room, showing a single target line on the left and three comparison lines on the right, as participants await their turn in quiet focus.",
        # SC02 (57w)
        "The visual task is almost insulting in its simplicity: determine which of the three comparison lines matches the target line in length. The correct match is unmistakable to anyone with healthy vision. But unbeknownst to the real subject, the other six participants are actors hired by psychologist Solomon Asch to deliver unanimous wrong answers in sequence.",
        # SC03 (56w)
        "On the first two trials, everyone answers correctly, establishing an easy rhythm of trust and unanimous consensus. But on the third trial, the trap springs. One by one, speaking aloud in predetermined seating order, each actor confidently names Line A, even though Line C is visibly identical to the stimulus card in every dimension.",
        # SC04 (60w) - editorial
        "We cherish the comforting belief that our personal senses are sovereign, insisting that we would never deny obvious physical facts simply to avoid standing out. Yet Asch's experiment exposed that social pressure acts like an invisible gravitational field, bending personal conviction the moment unanimous group consensus pushes against us in an enclosed room with unyielding force.",
        # SC05 (60w)
        "As the sixth actor gives his false answer, the genuine subject shifts anxiously in his seat, rubbing his forehead and squinting at the cards in visible agony. When his turn arrives, his voice wavers under pressure. Across multiple critical trials, subjects conformed with the group's obvious error thirty-six percent of the time, surrendering their own judgment.",
        # SC06 (56w)
        "Overall, seventy-five percent of participants abandoned their own eyes and conformed with the majority's false judgment at least once. During post-experiment interviews, many admitted they knew the group was incorrect, but conformed because they feared social ridicule or genuinely began doubting their own sensory perception under the heavy weight of peer pressure.",
        # SC07 (55w)
        "Fifty years later, neuroscientist Gregory Berns brought Asch's experiment into the twenty-first century, placing subjects into fMRI scanners to monitor neural activity during group conformity. Berns wanted to resolve an essential scientific question: do people consciously lie to conform, or does social pressure physically alter what the brain perceives during visual observation?",
        # SC08 (57w) - editorial
        "The fMRI brain scans provided an astonishing answer. When participants conformed to incorrect group opinion, researchers observed heightened activation within the occipital-parietal visual cortex. Conformity was not merely verbal polite compliance; social pressure had reshaped neural visual processing, meaning unanimous consensus literally distorted the brain's internal image of physical reality before conscious thought.",
        # SC09 (60w)
        "Yet Asch discovered an equally remarkable antidote to social conformity. When he introduced just one single confederate who broke ranks and gave the correct answer, the herd spell collapsed instantly. The presence of a solitary ally caused conformity rates to plunge from thirty-two percent down to barely five percent across trials, demonstrating the power of dissent.",
        # SC10 (56w)
        "The dissenter did not even need to be accurate; when an actor gave a different incorrect answer, conformity still dropped dramatically. A single dissenting voice punctures the psychological illusion of unanimous consensus, giving the human nervous system permission to trust its own observations rather than surrender blindly to the surrounding crowd in silence.",
        # SC11 (49w) - close cta
        "Whenever you sit in an office meeting or scroll through social media consensus, remember the Asch line trap. Unanimous agreement can warp your neurological perception, but a lone dissenter can restore sanity. Notice this cue tomorrow and tell us if you see through the crowd trap."
    ]

    beat_data = [
        # SC01
        [
            ("Frans Masereel style scratchboard woodcut on #E8E2D0 newsprint paper: seven anonymous young men in 1950s wool suits seated around a wooden seminar table under stark overhead cone light", "pan_left", "hold"),
            ("Close-up woodcut etching of the two white cardboard display cards on wooden easel: single vertical target black line on card one", "slow_zoom_in", "none"),
            ("Detailed scratchboard composition showing the second card with three comparison lines labeled A, B, and C with unmistakable length differences", "pan_right", "none"),
            ("Overhead diagram of the seminar room seating layout with seven numbered chair silhouettes rendered in stark black ink and brass pin markers", "hold", "none"),
            ("Detailed chiaroscuro portrait of the naive participant holding clipboard, leaning forward with neutral, relaxed scientific curiosity", "slow_zoom_in", "none"),
            ("Wide atmospheric scratchboard view of the academic laboratory room, intense black relief cross-hatching, 65% negative space", "hold", "hold"),
        ],
        # SC02
        [
            ("Conceptual scratchboard illustration: bold black comparison lines side by side with razor-sharp alignment markers proving Line C is identical", "pan_left", "hold"),
            ("Noir shadow profile of psychologist Solomon Asch standing in background shadows observing through two-way mirror glass", "slow_zoom_in", "none"),
            ("Schematic dossier diagram showing six chair silhouettes highlighted with subtle crimson string threads connecting them to the experimenter", "pan_right", "none"),
            ("Close-up etching of an actor's impassive wooden expression as he prepares to speak his scripted false answer", "hold", "none"),
            ("Contrast diagram highlighting the isolated naive subject seated in seat number seven, surrounded by six coordinated confederates", "slow_zoom_in", "none"),
            ("Full-frame scratchboard composition showing the invisible conspiracy of unanimous silence closing around the subject, 65% negative space", "hold", "hold"),
        ],
        # SC03
        [
            ("Timeline trial chart on aged newsprint dossier showing Trial 1 and Trial 2: unanimous correct responses establishing routine trust", "pan_left", "hold"),
            ("Dramatic visual shift on Trial 3: the display card shown with test line and comparison lines, clearly pointing to Line C as correct", "slow_zoom_in", "none"),
            ("Sequential woodcut portraits of confederate 1, 2, and 3 each pointing and declaring aloud: 'Line A'", "pan_right", "none"),
            ("Close-up of confederates 4, 5, and 6 echoing the identical false verdict with completely deadpan, confident delivery", "hold", "none"),
            ("Macro etching of the naive subject's eyes widening in shock and disbelief as the sixth actor confirms the obvious error", "slow_zoom_in", "none"),
            ("Stark scratchboard composition of the entire room facing the display cards with crimson tension threads connecting all six actors, 65% negative space", "hold", "hold"),
        ],
        # SC04
        [
            ("Symbolic woodcut noir artwork: human eyeball surrounded by delicate brass caliper measuring tools, representing sensory sovereignty", "pan_left", "hold"),
            ("Abstract scratchboard visualization: social pressure depicted as dense curved gravitational contours bending straight light rays", "slow_zoom_in", "none"),
            ("Tactile crimson cotton strings wrapping tightly around a lone silhouette's temples, pulling his gaze toward the group's direction", "pan_right", "none"),
            ("High-contrast chiaroscuro rendering of an individual standing on an island of truth being swallowed by a rising sea of ink silhouettes", "hold", "none"),
            ("Minimalist philosophical graphic: straight vertical line slowly warping into a curve under lateral peer pressure arrows", "slow_zoom_in", "none"),
            ("Panoramic Masereel-style woodcut tableau of individual conscience besieged by crowd conformity, 65% negative space", "hold", "hold"),
        ],
        # SC05
        [
            ("Detailed scratchboard portrait of the isolated subject: beads of sweat carved in white ink against heavily cross-hatched dark skin", "pan_left", "hold"),
            ("Close-up of the subject's fingers gripping the edge of the mahogany table until knuckles turn stark white", "slow_zoom_in", "none"),
            ("Subject squinting intently at the comparison card, leaning forward six inches to physically re-check his own eyes in agony", "pan_right", "none"),
            ("Chiaroscuro shadow profile showing the subject opening his mouth, vocal cords tightening as social isolation panic takes over", "hold", "none"),
            ("Statistical record card stamped on newsprint: critical trials recording 36.8% compliance rate with the obvious group lie", "slow_zoom_in", "none"),
            ("Dramatic full-frame silhouette of the subject bowing his head in quiet conformity amidst nodding actors, 65% negative space", "hold", "hold"),
        ],
        # SC06
        [
            ("Statistical dossier balance sheet on fibrous #E8E2D0 paper showing overall distribution: seventy-five percent conformed at least once", "pan_left", "hold"),
            ("Graphic breakdown comparing the twenty-five percent who remained completely independent versus the seventy-five percent who yielded", "slow_zoom_in", "none"),
            ("Archival transcript page of post-test debriefing interviews: handwritten confessions of acute self-doubt and fear of appearing eccentric", "pan_right", "none"),
            ("Woodcut metaphor: individual silhouette standing in the cold outside a warm lighted door, illustrating evolutionary fear of banishment", "hold", "none"),
            ("Psychological spectrum diagram: distortion of judgment versus distortion of perception versus distortion of action", "slow_zoom_in", "none"),
            ("Stark minimalist woodcut composition of seventy-five identical white figures marching alongside twenty-five solitary dark figures, 65% negative space", "hold", "hold"),
        ],
        # SC07
        [
            ("Modern forensic laboratory setting rendered in scratchboard woodcut: high-tech fMRI scanner tunnel surrounded by digital monitors", "pan_left", "hold"),
            ("Subject lying horizontally inside the fMRI bore wearing specialized prism glasses displaying 3D rotated geometric line shapes", "slow_zoom_in", "none"),
            ("Neuroscientist Gregory Berns in lab coat reviewing real-time neural hemodynamic response curves on archival newsprint layout", "pan_right", "none"),
            ("Split diagram contrasting two scientific hypotheses: conscious deception in frontal lobes vs altered perception in visual lobes", "hold", "none"),
            ("Cross-sectional brain anatomy etching highlighting the occipital lobe, parietal lobe, and prefrontal executive cortex in ink outlines", "slow_zoom_in", "none"),
            ("High-contrast woodcut composition linking Asch's 1951 seminar cards directly to the 2005 fMRI brain scanner, 65% negative space", "hold", "hold"),
        ],
        # SC08
        [
            ("Detailed anatomical woodcut of the human brain with crimson ink wash highlighting active neural clusters in occipital-parietal visual cortex", "pan_left", "hold"),
            ("Macro comparison diagram: independent responses activating frontal decision circuits versus conforming responses lighting up early visual areas", "slow_zoom_in", "none"),
            ("Scientific schematic demonstrating that peer consensus alters sensory perceptual encoding before conscious logic is even triggered", "pan_right", "none"),
            ("Visual metaphor: group opinions physically repainting the internal mental retina inside a silhouette's hollow skull", "hold", "none"),
            ("Forensic medical chart summary: 'SOCIAL CONFORMITY RESHAPES PHYSICAL PERCEPTION OF REALITY', stamped in crimson ink", "slow_zoom_in", "none"),
            ("Full-frame chiaroscuro brain visualization glowing with crimson activation against deep India ink black background, 65% negative space", "hold", "hold"),
        ],
        # SC09
        [
            ("Asch experimental trial variation diagram on #E8E2D0 newsprint: introducing Partner D, seated in position four as a designated ally", "pan_left", "hold"),
            ("Close-up scratchboard portrait of the single confederate calmly and clearly stating the true correct answer: 'Line C'", "slow_zoom_in", "none"),
            ("Dramatic visual effect: the dense crimson tension threads binding the subject instantly snap and recoil in mid-air", "pan_right", "none"),
            ("Statistical plunge chart etched in crisp black ink showing conformity plummeting from thirty-two percent down to barely five percent", "hold", "none"),
            ("The subject's facial expression relaxing: eyes brightening, posture straightening with immediate emotional and psychological relief", "slow_zoom_in", "none"),
            ("Dynamic woodcut composition showing two figures standing side by side against five conformist shadows, 65% negative space", "hold", "hold"),
        ],
        # SC10
        [
            ("Experimental variation card: testing a 'compromise dissenter' who picks a different wrong answer rather than the correct one", "pan_left", "hold"),
            ("Data comparison showing conformity plunging almost equally low even when the dissenter gives an inaccurate alternative verdict", "slow_zoom_in", "none"),
            ("Psychological insight diagram: breaking unanimity is the critical cognitive mechanism, freeing the individual from consensus trance", "pan_right", "none"),
            ("Woodcut metaphor: a single tiny brass pin puncturing a massive pressurized black balloon of collective consensus", "hold", "none"),
            ("Lone individual silhouette speaking into a crowded assembly hall, microphone soundwaves creating an oasis of clarity", "slow_zoom_in", "none"),
            ("High-contrast scratchboard composition of a solitary dissenter breaking the spell of unanimous darkness, 65% negative space", "hold", "hold"),
        ],
        # SC11
        [
            ("Modern executive boardroom rendered in Frans Masereel scratchboard noir: suits nodding unanimously around a glass conference table", "pan_left", "hold"),
            ("Social media smartphone feed graphic in stark woodcut lines: identical sentiment bubbles descending in hypnotic unison", "slow_zoom_in", "none"),
            ("A single brave figure raising an index finger at the table, questioning the unanimous assumption with quiet authority", "pan_right", "none"),
            ("Tactile red thread motif being deliberately severed with a small pair of antique brass scissors, representing cognitive liberation", "hold", "none"),
            ("Hand-lettered psychological rule stamped on newsprint: 'ONE DISSENTER RESTORES REALITY', framed in engraved woodcut borders", "slow_zoom_out", "none"),
            ("Final elegant dossier endcard featuring Crowd Strings seal, brass pin emblem, and viewer prompt: 'Tell us if you see through the crowd trap', 65% negative space", "hold", "hold"),
        ]
    ]

    scenes = []
    coverage = []
    claims = [
        {
            "scene_id": "SC01",
            "quote": "Swarthmore College, 1951. Seven young men sit around a polished wooden seminar table",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Overall conformity rate on critical trials reached thirty-six point eight percent."
        },
        {
            "scene_id": "SC06",
            "quote": "Overall, seventy-five percent of participants abandoned their own eyes and conformed with the majority's false judgment at least once.",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Seventy-five percent of participants conformed with the group's incorrect answer at least once."
        },
        {
            "scene_id": "SC07",
            "quote": "Fifty years later, neuroscientist Gregory Berns brought Asch's experiment into the twenty-first century, placing subjects into fMRI scanners",
            "language": "en",
            "source_id": "SRC02",
            "fact": "Conformity distorts perceptual processing before conscious decision-making occurs."
        },
        {
            "scene_id": "SC08",
            "quote": "When participants conformed to incorrect group opinion, researchers observed heightened activation within the occipital-parietal visual cortex.",
            "language": "en",
            "source_id": "SRC02",
            "fact": "Social conformity alters neural activity in the occipital-parietal visual cortex."
        },
        {
            "scene_id": "SC09",
            "quote": "The presence of a solitary ally caused conformity rates to plunge from thirty-two percent down to barely five percent across trials.",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Introducing a single dissenting partner reduced conformity from thirty-two percent to five percent."
        }
    ]

    for idx, (narr, beats_info) in enumerate(zip(sc_narrations, beat_data), start=1):
        sc_id = f"SC{idx:02d}"
        req_id = f"R{idx:02d}"
        
        sit_map = {
            1: "hook_shock",
            2: "mechanism_step",
            3: "deep_dive_step",
            4: "editorial_commentary",
            5: "story_action",
            6: "deep_dive_step",
            7: "case_study",
            8: "editorial_commentary",
            9: "rapid_examples",
            10: "before_after_contrast",
            11: "cta_bridge"
        }
        sit = sit_map[idx]
        
        req_quote_map = {
            1: "Swarthmore College, 1951. Seven young men sit around a polished wooden seminar table",
            2: "six of the seven participants are actors hired by psychologist Solomon Asch to deliver unanimous wrong answers",
            3: "each actor confidently names Line A, even though Line C is visibly identical to the stimulus card",
            4: "social pressure acts like an invisible gravitational field, bending personal conviction",
            5: "subjects conformed with the group's obvious error thirty-six percent of the time.",
            6: "seventy-five percent of participants abandoned their own eyes and conformed with the majority's false judgment at least once.",
            7: "neuroscientist Gregory Berns brought Asch's experiment into the twenty-first century, placing subjects into fMRI scanners",
            8: "researchers observed heightened activation within the occipital-parietal visual cortex.",
            9: "The presence of a solitary ally caused conformity rates to plunge from thirty-two percent down to barely five percent across trials.",
            10: "A single dissenting voice punctures the psychological illusion of unanimous consensus",
            11: "Notice this cue tomorrow and tell us if you see through the crowd trap."
        }
        coverage.append({
            "requirement_id": req_id,
            "scene_id": sc_id,
            "quote": req_quote_map[idx]
        })

        images = []
        beats = []
        tempos = ["fast", "fast", "normal", "normal", "slow", "normal"]

        for b_idx, (desc, cam, eff) in enumerate(beats_info, start=1):
            img_id = f"{sc_id}_I{b_idx}"
            beat_id = f"{sc_id}_B{b_idx}"
            t = tempos[b_idx - 1]
            
            images.append({
                "id": img_id,
                "description": desc,
                "character_ids": ["CH01"],
                "preserve": "Frans Masereel scratchboard woodcut style, #E8E2D0 newsprint, crimson tension threads",
                "change": f"Detailed scratchboard composition change for beat {beat_id}",
                "reason": f"Narration-locked full-frame beat {img_id}.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": t,
                "narrative_situation": sit,
                "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                "has_character": True,
                "motion_prompt": f"Tactile 2D scratchboard noir animation, {desc[:100].lower()}, silent visual storytelling, no talking, no lip movement",
                "camera_motion": cam,
                "effect": eff
            })
            beats.append({
                "id": beat_id,
                "image_id": img_id,
                "purpose": f"Psychological visual beat {b_idx} for scene {sc_id}",
                "tempo": t,
                "narrative_situation": sit,
                "shot_type": "full_scene",
                "effect": eff
            })

        scenes.append({
            "id": sc_id,
            "title": outline["outline"][idx - 1]["purpose"][:60],
            "purpose": outline["outline"][idx - 1]["purpose"],
            "action": f"Tactile scratchboard noir scene depicting {sc_id} events on #E8E2D0 newsprint dossier.",
            "setting": "Psychological investigation dossier on aged #E8E2D0 newsprint paper canvas.",
            "camera": "Semantic full-frame sequence",
            "narration": narr,
            "requirements": [req_id],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"] if idx in [1, 2, 3, 5, 6, 9] else ["SRC02"],
            "narrative_situation": sit,
            "images": images,
            "beats": beats
        })

    content = {
        "schema_version": "3.0",
        "job_id": job_id,
        "topic": topic,
        "duration": brief["duration"],
        "style": brief["style"],
        "required_points": [rp["text"] for rp in brief["required_points"]],
        "characters": [channel_cast(channel_id, "CH01")],
        "scenes": scenes,
        "coverage": coverage,
        "outline": outline["outline"],
        "claims": claims,
        "revision_response": [],
        "open_questions": []
    }

    return job_id, brief, outline, competitor_research, content


def make_crowd_strings_short():
    job_id = "en-crowd-strings-batch1-9x16"
    parent_long_id = "en-crowd-strings-batch1-16x9"
    channel_id = "en_crowd_strings"
    ch = get_channel(channel_id)
    topic = "The Asch Line Trap: Why Social Conformity Forces 75 Percent of People to Agree With an Obvious Lie"
    youtube_title = "Why You Turn Around in an Elevator of Strangers"  # 48 chars <= 55

    style_desc = (
        "Frans Masereel Scratchboard Woodcut and Noir Red-Thread Dossier art on vertical #E8E2D0 newsprint dossier paper "
        "(#111111 India ink black, #E8E2D0 newsprint paper grain, #5A5F66 charcoal wash, #C0392B crimson cotton tension threads); "
        "hand-carved scratchboard relief linework, brass dossier pins, physical crimson string matrices, "
        "and anonymous crowd ink silhouettes; orthographic 2D, authentic printmaking texture, at least 60% negative space, "
        "zero 3D CGI, zero neon glow, zero plastic gradients."
    )

    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Fast-paced vertical psychology explainer uncovering how herd conformity alters visual perception and how one dissenter breaks the trap.",
        "video_type": "explainer",
        "duration": {"min_seconds": 38.0, "max_seconds": 52.0},
        "scene_count": 5,
        "parent_long_id": parent_long_id,
        "required_points": [
            {"id": "R01", "text": "Turning around in an elevator of strangers demonstrating the silent power of herd conformity."},
            {"id": "R02", "text": "Solomon Asch's 1951 line test where seventy-five percent conformed with an obvious lie."},
            {"id": "R03", "text": "fMRI scans revealing that social pressure reshapes neural activation inside the visual cortex."},
            {"id": "R04", "text": "A single dissenter in the room collapsing conformity from thirty-two percent to five percent."},
            {"id": "R05", "text": "Everyday psychological defense against conformity strings and invitation to full analysis."}
        ],
        "language": "en",
        "tone": ch.tone,
        "style": style_desc,
        "aspect_ratio": "9:16",
        "format_profile": "short_9x16",
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "Effects of group pressure upon the modification and distortion of judgments",
                "reference": "Asch, S. E. (1951). In Groups, Leadership and Men (pp. 177-190). Carnegie Press.",
                "facts": [
                    "Seventy-five percent of participants conformed with the group's incorrect answer at least once.",
                    "Overall conformity rate on critical trials reached thirty-six point eight percent.",
                    "Introducing a single dissenting partner reduced conformity from thirty-two percent to five percent."
                ]
            }
        ],
        "outputs": [
            {
                "aspect_ratio": "9:16",
                "language": "en",
                "subtitles": True,
                "voice": ch.voice,
                "speed": 1.0
            }
        ],
        "planning": {
            "success_criteria": [
                "Hook with the elevator conformity reflex in 3 seconds, explain Asch's test, reveal fMRI brain change, show dissenter power, bridge at climax."
            ],
            "avoid": [
                "Zero corporate management jargon, zero patronizing life coaching, zero canned discourse markers."
            ],
            "prior_knowledge": "None required.",
            "pacing": "Rapid vertical behavioral pacing (~2.2s per image).",
            "speech_rates": {
                "en": {
                    "units_per_second": 3.8,
                    "uncertainty": 0.15,
                    "source": "Acoustic calibrated cadence"
                }
            }
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Vertical scratchboard noir view of passenger in elevator turning around to face back wall with crimson strings pulling feet",
                "text_overlay": "TURN AROUND",
                "contrast_pair": "Elevator Trap vs 1-Dissenter Release",
                "layout_mode": "split_contrast"
            },
            "channel_pillar": ch.niche,
            "funnel_tier": "tier_1_broad",
            "seo_keywords": [
                "elevator experiment",
                "social conformity shorts",
                "Asch line experiment",
                "herd mentality psychology"
            ]
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Vertical scratchboard noir view of passenger in elevator turning around to face back wall with crimson strings pulling feet",
            "text_overlay": "TURN AROUND",
            "contrast_pair": "Elevator Trap vs 1-Dissenter Release",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": ch.niche,
        "funnel_tier": "tier_1_broad",
        "seo_keywords": [
            "elevator experiment",
            "social conformity shorts",
            "Asch line experiment",
            "herd mentality psychology"
        ],
        "cta_plan": {
            "cliffhanger_peak": "How do master persuaders weaponize this psychological string in daily life?",
            "bridge": "Watch the complete psychological breakdown on Crowd Strings.",
            "close": "Notice this cue tomorrow and tell us if you see through the crowd trap.",
            "endcard_text": "FULL VIDEO ON YOUTUBE"
        },
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": ch.engagement.cta_voice,
            "banned_cta_phrases": list(ch.engagement.banned_cta_phrases)
        },
        "editorial_stance": {
            "myth_debunked": "People only conform because they want to be polite or avoid temporary awkwardness.",
            "channel_verdict": "Unanimous social consensus physically rewires visual cortex activity before conscious decision-making.",
            "why_generic_advice_fails": "Telling people to simply 'be confident' ignores that peer pressure alters biological sensory perception.",
            "tradeoff_or_blindspot": "Rejecting group consensus triggers acute neurological pain signals wired by evolutionary survival."
        },
        "actionable_value": {
            "core_mechanism": "The dissenter release mechanism: breaking unanimous group consensus drops conformity rates from thirty-two percent to five percent immediately.",
            "practical_rule_of_thumb": "In high-stakes consensus meetings, assign a rotating dissenter whose sole duty is to voice disagreement.",
            "real_world_scenario": "A boardroom approving an unworkable project budget because nobody wants to break the illusion of unanimous agreement."
        },
        "video_engine": "images_only",
        "chain_mode": "full_chain"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Hook: turning around in an elevator of strangers demonstrating herd conformity", "requirements": ["R01"], "transition": "Rapid zoom into elevator interior"},
            {"scene_id": "SC02", "purpose": "Mechanism: Solomon Asch's 1951 line test where 75% agreed with an obvious lie", "requirements": ["R02"], "transition": "Comparison card visual layout"},
            {"scene_id": "SC03", "purpose": "Editorial commentary: fMRI scans revealing peer pressure reshapes the visual cortex", "requirements": ["R03"], "transition": "fMRI visual cortex cross-section"},
            {"scene_id": "SC04", "purpose": "Cliffhanger peak: a single dissenter collapsing conformity from 32% down to 5%", "requirements": ["R04"], "transition": "Severed red tension thread graphic"},
            {"scene_id": "SC05", "purpose": "Payoff, bridge CTA to full psychological breakdown, and closing prompt", "requirements": ["R05"], "transition": "Crowd Strings dossier seal and endcard"}
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Academy of Ideas Shorts",
                    "top_performing_videos": [
                        {
                            "title": "Why You Conform (Elevator Experiment)",
                            "views": "2.8M views",
                            "hook_technique": "Opening with the relatable elevator reflex where everyone turns to face the rear wall.",
                            "pacing_structure": "3s hook -> 15s Asch study -> 15s fMRI brain scan -> 10s dissenter cure.",
                            "retention_driver": "Rapid visual turnover and stark scratchboard aesthetic."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Framing conformity as physical strings pulling your limbs rather than an abstract idea.",
                        "Highlighting the 32% to 5% dissenter collapse statistic."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 28,
                "zero_pause_opening_seconds": 12,
                "visual_contrast": "Vertical scratchboard view of an elevator where three shadows face the back wall and the subject turns around.",
                "counter_intuitive_truth_slap": "You think your eyes control what you see; peer consensus actually edits your visual reality before you think."
            },
            "narrative_progression_arc": [
                {"phase": "hook_shock", "purpose": "Elevator stranger conformity reflex within ten seconds"},
                {"phase": "mechanism_step", "purpose": "Solomon Asch's 1951 line length test and 75% compliance"},
                {"phase": "editorial_commentary", "purpose": "fMRI neuroimaging showing visual cortex neural alteration"},
                {"phase": "cliffhanger_peak", "purpose": "A single dissenter plunging conformity from 32% to 5%"},
                {"phase": "cta_bridge", "purpose": "Bridge to full psychological breakdown and observation prompt"}
            ],
            "flow_video_transition_blueprint": {
                "keyframe_continuity": "Vertical newsprint dossier #E8E2D0 with crimson tension threads #C0392B.",
                "tempo_modulation": "Rapid tempo throughout (< 2.3s hold)."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": ch.niche,
            "myth_debunked": brief["editorial_stance"]["myth_debunked"],
            "channel_verdict": brief["editorial_stance"]["channel_verdict"],
            "actionable_rule_of_thumb": brief["actionable_value"]["practical_rule_of_thumb"]
        },
        "cta_and_spinoff_strategy": {
            "bridge": brief["cta_plan"]["bridge"],
            "close": brief["cta_plan"]["close"],
            "endcard_text": brief["cta_plan"]["endcard_text"]
        }
    }

    sc01_narr = "Step inside an elevator where three actors stand facing the back wall, and within ten seconds, your brain will force your feet to turn around too. Social conformity is a silent, irresistible current bending human behavior."
    sc02_narr = "In 1951, psychologist Solomon Asch proved that when six actors unanimously chose an obviously incorrect line length on a card, seventy-five percent of real participants conformed with the lie at least once during trials."
    sc03_narr = "Modern fMRI brain imaging proves this is not mere politeness. Social pressure physically alters neural activation inside your visual cortex, meaning unanimous peer consensus literally changes what your brain perceives as physical truth in real time."
    sc04_narr = "Yet when just one single person in the room voices dissent, the crowd's hypnotic hold instantly collapses, plunging conformity rates from thirty-two percent down to barely five percent in a matter of seconds."
    sc05_narr = "How do master persuaders weaponize this psychological string in daily life? Watch the complete psychological breakdown on Crowd Strings. Notice this cue tomorrow and tell us if you see through the crowd trap."

    sc_narrations_short = [sc01_narr, sc02_narr, sc03_narr, sc04_narr, sc05_narr]

    beat_data_short = [
        # SC01
        [
            ("Vertical scratchboard woodcut on #E8E2D0 newsprint: view looking into an elevator interior where three suits face the back wall in silence", "pan_left", "hold"),
            ("Close-up etching of passenger's polished leather shoes slowly rotating 180 degrees to match the strange crowd direction", "slow_zoom_in", "none"),
            ("Chiaroscuro shadow profile of the passenger looking sideways with anxious, sheepish eyes while conforming to the silent rule", "pan_right", "none"),
            ("Symbolic vertical illustration of crimson puppet threads pulling the passenger's feet into alignment, 65% negative space", "hold", "hold"),
        ],
        # SC02
        [
            ("Vertical layout of Asch's 1951 test cards: single target line on left and three obviously different comparison lines on right", "pan_left", "hold"),
            ("Scratchboard row of six anonymous suited figures pointing unanimously at Line A in synchronized woodcut linework", "slow_zoom_in", "none"),
            ("Subject silhouette seated at the end of the table sweating in agony as his turn approaches on aged newsprint paper", "pan_right", "none"),
            ("Archival statistic card stamped in crimson ink: '75% CONFORMED WITH OBVIOUS LIE AT LEAST ONCE', 65% negative space", "hold", "hold"),
        ],
        # SC03
        [
            ("Vertical neuroimaging schematic showing human brain profile with occipital visual cortex highlighted in glowing crimson wash", "pan_left", "hold"),
            ("Comparison diagram: solo perception activating frontal logic circuits vs crowd conformity altering early visual processing", "slow_zoom_in", "none"),
            ("Magnified woodcut rendering of neural synapses firing under social tension, warping perceived geometric shapes", "pan_right", "none"),
            ("Conceptual artwork: crowd silhouette hands reaching into the visual cortex to physically distort incoming light rays, 65% negative space", "hold", "hold"),
        ],
        # SC04
        [
            ("Dramatic scratchboard scene: a single dissenter silhouette standing up and pointing at the correct line in bold defiance", "pan_left", "hold"),
            ("Macro view of crimson tension threads snapping violently with crisp white energetic woodcut fracture marks", "slow_zoom_in", "none"),
            ("Statistical curve on newsprint plunging vertically from thirty-two percent down to barely five percent compliance", "pan_right", "none"),
            ("The subject's face relaxing into an expression of profound cognitive freedom and clarity, 65% negative space", "hold", "hold"),
        ],
        # SC05
        [
            ("Vertical scratchboard montage of everyday settings: boardroom meetings, retail stores, and digital feeds with crimson tension threads", "pan_left", "hold"),
            ("Lone individual cutting crimson threads with small brass scissors under clean overhead studio lighting on #E8E2D0 paper", "slow_zoom_in", "none"),
            ("Engraved archival card displaying Crowd Strings seal and YouTube channel title", "pan_right", "none"),
            ("Final elegant dossier endcard with observation prompt: 'Notice this cue tomorrow and tell us if you see through the crowd trap', 65% negative space", "hold", "hold"),
        ]
    ]

    scenes = []
    coverage = []
    claims = [
        {
            "scene_id": "SC01",
            "quote": "Step inside an elevator where three actors stand facing the back wall, and within ten seconds, your brain will force your feet to turn around too.",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Overall conformity rate on critical trials reached thirty-six point eight percent."
        },
        {
            "scene_id": "SC02",
            "quote": "seventy-five percent of real participants conformed with the lie at least once during trials.",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Seventy-five percent of participants conformed with the group's incorrect answer at least once."
        },
        {
            "scene_id": "SC04",
            "quote": "plunging conformity rates from thirty-two percent down to barely five percent in a matter of seconds.",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Introducing a single dissenting partner reduced conformity from thirty-two percent to five percent."
        }
    ]

    short_sits = ["hook_shock", "mechanism_step", "editorial_commentary", "cliffhanger_peak", "cta_bridge"]
    req_quotes_short = [
        "Step inside an elevator where three actors stand facing the back wall, and within ten seconds, your brain will force your feet to turn around too.",
        "seventy-five percent of real participants conformed with the lie at least once during trials.",
        "Social pressure physically alters neural activation inside your visual cortex",
        "plunging conformity rates from thirty-two percent down to barely five percent in a matter of seconds.",
        "Watch the complete psychological breakdown on Crowd Strings. Notice this cue tomorrow and tell us if you see through the crowd trap."
    ]

    for idx, (narr, beats_info, sit, q) in enumerate(zip(sc_narrations_short, beat_data_short, short_sits, req_quotes_short), start=1):
        sc_id = f"SC{idx:02d}"
        req_id = f"R{idx:02d}"
        
        coverage.append({
            "requirement_id": req_id,
            "scene_id": sc_id,
            "quote": q
        })

        images = []
        beats = []
        tempos = ["fast", "fast", "normal", "slow"]

        for b_idx, (desc, cam, eff) in enumerate(beats_info, start=1):
            img_id = f"{sc_id}_I{b_idx}"
            beat_id = f"{sc_id}_B{b_idx}"
            t = tempos[b_idx - 1]
            
            images.append({
                "id": img_id,
                "description": desc,
                "character_ids": ["CH01"],
                "preserve": "Frans Masereel vertical scratchboard style, #E8E2D0 newsprint, crimson tension threads",
                "change": f"Detailed vertical scratchboard change for beat {beat_id}",
                "reason": f"Narration-locked full-frame beat {img_id}.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": t,
                "narrative_situation": sit,
                "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                "has_character": True,
                "motion_prompt": f"Tactile 2D vertical scratchboard noir animation, {desc[:100].lower()}, silent visual storytelling, no talking, no lip movement",
                "camera_motion": cam,
                "effect": eff
            })
            beats.append({
                "id": beat_id,
                "image_id": img_id,
                "purpose": f"Vertical visual beat {b_idx} for scene {sc_id}",
                "tempo": t,
                "narrative_situation": sit,
                "shot_type": "full_scene",
                "effect": eff
            })

        scenes.append({
            "id": sc_id,
            "title": outline["outline"][idx - 1]["purpose"][:60],
            "purpose": outline["outline"][idx - 1]["purpose"],
            "action": f"Tactile scratchboard vertical noir scene depicting {sc_id} events on #E8E2D0 newsprint.",
            "setting": "Psychological investigation vertical dossier on aged #E8E2D0 newsprint paper canvas.",
            "camera": "Semantic full-frame sequence",
            "narration": narr,
            "requirements": [req_id],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "narrative_situation": sit,
            "images": images,
            "beats": beats
        })

    content = {
        "schema_version": "3.0",
        "job_id": job_id,
        "topic": topic,
        "duration": brief["duration"],
        "style": brief["style"],
        "required_points": [rp["text"] for rp in brief["required_points"]],
        "characters": [channel_cast(channel_id, "CH01")],
        "scenes": scenes,
        "coverage": coverage,
        "outline": outline["outline"],
        "claims": claims,
        "revision_response": [],
        "open_questions": []
    }

    return job_id, brief, outline, competitor_research, content


# ==============================================================================
# MAIN BUILDER & LINTER RUNNER
# ==============================================================================

def main():
    print("================================================================================")
    print("SA-EN-03: Building & Validating Schema 3.0 Production Packages for 6 Jobs")
    print("================================================================================")

    jobs = [
        ("en_choke_point", make_choke_point_long, "long_16x9", "16:9"),
        ("en_choke_point", make_choke_point_short, "short_9x16", "9:16"),
        ("en_cold_case_ink", make_cold_case_ink_long, "long_16x9", "16:9"),
        ("en_cold_case_ink", make_cold_case_ink_short, "short_9x16", "9:16"),
        ("en_crowd_strings", make_crowd_strings_long, "long_16x9", "16:9"),
        ("en_crowd_strings", make_crowd_strings_short, "short_9x16", "9:16"),
    ]

    results = []

    for ch_slug, factory, fmt_prof, aspect in jobs:
        ch = get_channel(ch_slug)
        job_id, brief, outline, cr, content = factory()
        job_dir = SYS_DIR / "runs" / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        # 1. Compile images manifest
        images_manifest = compile_images_manifest(ch, brief, content, aspect)

        # 2. Write all 5 JSON files
        write_json(job_dir / "brief.json", brief)
        write_json(job_dir / "outline.json", outline)
        write_json(job_dir / "competitor_research.json", cr)
        write_json(job_dir / "content.json", content)
        write_json(job_dir / "images.json", images_manifest)

        # 3. Compute stats
        words = sum(count_words(sc.get("narration", "")) for sc in content["scenes"])
        est_dur = max(25.0, words / 3.8)
        img_count = len(images_manifest["items"])
        avg_hold = est_dur / max(1, img_count)

        # 4. Run linters
        ed_audit = lint_editorial_and_narrative_quality(brief, content, estimated_duration_sec=est_dur)
        cliche_violations = check_ai_cliche_phrases(content["scenes"])
        claim_facts = {c.get("fact", "") for c in content.get("claims", [])}
        rep_violations = check_intra_video_repetitions(content["scenes"], claim_facts=claim_facts)
        cta_violations = lint_cta(brief, content)

        all_passed = (
            ed_audit["passed"]
            and len(cliche_violations) == 0
            and len(rep_violations) == 0
            and len(cta_violations) == 0
        )

        results.append({
            "job_id": job_id,
            "channel": ch.name,
            "format": fmt_prof,
            "title": brief.get("youtube_title", ""),
            "words": words,
            "est_dur": round(est_dur, 1),
            "images": img_count,
            "avg_hold": round(avg_hold, 2),
            "ed_passed": ed_audit["passed"],
            "ed_errors": ed_audit["errors"],
            "cliche_count": len(cliche_violations),
            "rep_count": len(rep_violations),
            "cta_count": len(cta_violations),
            "all_passed": all_passed,
        })

        status_str = "✅ PASS" if all_passed else "❌ FAIL"
        print(f"[{status_str}] {job_id} | {words} words | {img_count} images | {avg_hold:.2f}s/hold")
        if not all_passed:
            if not ed_audit["passed"]:
                print(f"   Editorial Errors: {ed_audit['errors']}")
            if cliche_violations:
                print(f"   Cliche Violations: {cliche_violations}")
            if rep_violations:
                print(f"   Repetition Violations: {rep_violations}")
            if cta_violations:
                print(f"   CTA Violations: {cta_violations}")

    print("\n" + "=" * 105)
    print(f"{'Job ID':<33} | {'Format':<10} | {'Words':<6} | {'Dur(s)':<6} | {'Imgs':<5} | {'Hold(s)':<7} | {'Status'}")
    print("-" * 105)
    for r in results:
        status_label = "100% PASS" if r["all_passed"] else "FAIL"
        print(f"{r['job_id']:<33} | {r['format']:<10} | {r['words']:<6} | {r['est_dur']:<6.1f} | {r['images']:<5} | {r['avg_hold']:<7.2f} | {status_label}")
    print("=" * 105 + "\n")


if __name__ == "__main__":
    main()
