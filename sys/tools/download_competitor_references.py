#!/usr/bin/env python3
"""Download real competitor reference video thumbnails for Video Pilot channels.

Usage:
    python sys/tools/download_competitor_references.py --channel en-first-principles
    python sys/tools/download_competitor_references.py --all
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("download_competitor_refs")

REFS_DIR = Path("/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f/competitor_refs")

CHANNEL_COMPETITORS: Dict[str, Dict[str, Any]] = {
    "en-root-and-canopy": {
        "niche": "Botany & Forest Science",
        "competitors": {
            "crime_pays_botany": "https://www.youtube.com/@CrimePaysButBotanyDoesnt/videos",
            "bbc_earth": "https://www.youtube.com/@bbcearth/videos",
            "mossy_earth": "https://www.youtube.com/@MossyEarth/videos",
            "in_defense_of_plants": "https://www.youtube.com/@InDefenseofPlants/videos",
        },
    },
    "en-scale-and-bone": {
        "niche": "Zoology & Animal Evolution",
        "competitors": {
            "tierzoo": "https://www.youtube.com/@TierZoo/videos",
            "moth_light_media": "https://www.youtube.com/@MothLightMedia/videos",
            "pbs_eons": "https://www.youtube.com/@eons/videos",
            "casual_geographic": "https://www.youtube.com/@mancrackermedia/videos",
        },
    },
    "en-spawn-to-apex": {
        "niche": "Insect Metamorphosis & Biology",
        "competitors": {
            "deep_look": "https://www.youtube.com/@DeepLookPBS/videos",
            "microcosmos": "https://www.youtube.com/@journeytomicro/videos",
            "ant_lab": "https://www.youtube.com/@AntLab/videos",
            "real_science": "https://www.youtube.com/@realscience/videos",
        },
    },
    "en-second-arrow": {
        "niche": "Stoicism & Zen Philosophy",
        "competitors": {
            "daily_stoic": "https://www.youtube.com/@DailyStoic/videos",
            "einzelganger": "https://www.youtube.com/@Einzelganger/videos",
            "pursuit_of_wonder": "https://www.youtube.com/@PursuitofWonder/videos",
            "sprouts": "https://www.youtube.com/@SproutsSchools/videos",
        },
    },
    "en-bamboo-marble": {
        "niche": "Eastern Philosophy & Life Lessons",
        "competitors": {
            "sisyphus55": "https://www.youtube.com/@Sisyphus55/videos",
            "aperture": "https://www.youtube.com/@ApertureThinking/videos",
            "philosophies_for_life": "https://www.youtube.com/@PhilosophiesforLife/videos",
            "art_of_improvement": "https://www.youtube.com/@TheArtofImprovement/videos",
        },
    },
    "en-kindred-sketch": {
        "niche": "Empathy, Relationships & Attachment",
        "competitors": {
            "school_of_life": "https://www.youtube.com/@theschooloflifetv/videos",
            "psych2go": "https://www.youtube.com/@Psych2go/videos",
            "cinema_therapy": "https://www.youtube.com/@CinemaTherapyShow/videos",
            "heidi_priebe": "https://www.youtube.com/@HeidiPriebe1/videos",
        },
    },
    "en-lazy-brain": {
        "niche": "Neuroscience of Habits & Focus",
        "competitors": {
            "better_than_yesterday": "https://www.youtube.com/@BetterThanYesterday/videos",
            "sprouts": "https://www.youtube.com/@SproutsSchools/videos",
            "minutephysics": "https://www.youtube.com/@minutephysics/videos",
            "improvement_pill": "https://www.youtube.com/@ImprovementPill/videos",
        },
    },
    "en-first-principles": {
        "niche": "Mental Models & Physics Paradoxes",
        "competitors": {
            "veritasium": "https://www.youtube.com/@veritasium/videos",
            "primer": "https://www.youtube.com/@PrimerBlobs/videos",
            "3blue1brown": "https://www.youtube.com/@3blue1brown/videos",
            "polymatter": "https://www.youtube.com/@PolyMatter/videos",
        },
    },
    "en-career-leverage": {
        "niche": "Workplace Leverage & Negotiation",
        "competitors": {
            "hbr": "https://www.youtube.com/@harvardbusinessreview/videos",
            "wsj_explains": "https://www.youtube.com/@wsj/videos",
            "modern_wisdom": "https://www.youtube.com/@ModernWisdomPodcast/videos",
            "alex_hormozi": "https://www.youtube.com/@AlexHormozi/videos",
        },
    },
    "en-pocket-cosmos": {
        "niche": "Astrophysics & Space Exploration",
        "competitors": {
            "kurzgesagt": "https://www.youtube.com/@kurzgesagt/videos",
            "sea": "https://www.youtube.com/@SEAspace/videos",
            "melodysheep": "https://www.youtube.com/@melodysheep/videos",
            "astrum": "https://www.youtube.com/@astrumspace/videos",
        },
    },
    "en-deep-time-strata": {
        "niche": "Geology & Deep Earth History",
        "competitors": {
            "pbs_eons": "https://www.youtube.com/@eons/videos",
            "history_of_the_earth": "https://www.youtube.com/@HistoryoftheEarth/videos",
            "ben_g_thomas": "https://www.youtube.com/@BenGThomas/videos",
            "stefan_milo": "https://www.youtube.com/@StefanMilo/videos",
        },
    },
    "en-inside-vessel": {
        "niche": "Human Physiology & Medicine",
        "competitors": {
            "kurzgesagt": "https://www.youtube.com/@kurzgesagt/videos",
            "institute_human_anatomy": "https://www.youtube.com/@TheAnatomyLab/videos",
            "nucleus_medical": "https://www.youtube.com/@NucleusMedicalMedia/videos",
            "hashem_alghaili": "https://www.youtube.com/@HashemAlghailiScience/videos",
        },
    },
    "en-macro-gears": {
        "niche": "Macroeconomics & Industrial Chains",
        "competitors": {
            "economics_explained": "https://www.youtube.com/@EconomicsExplained/videos",
            "wendover": "https://www.youtube.com/@Wendoverproductions/videos",
            "practical_engineering": "https://www.youtube.com/@PracticalEngineeringChannel/videos",
            "visual_capitalist": "https://www.youtube.com/@VisualCapitalist/videos",
        },
    },
    "en-wallet-anatomy": {
        "niche": "Behavioral Pricing & Personal Finance",
        "competitors": {
            "two_cents": "https://www.youtube.com/@TwoCentsPBS/videos",
            "graham_stephan": "https://www.youtube.com/@GrahamStephan/videos",
            "humphrey_yang": "https://www.youtube.com/@HumphreyTalks/videos",
            "financial_diet": "https://www.youtube.com/@thefinancialdiet/videos",
        },
    },
    "en-fine-print": {
        "niche": "Consumer Law & Hidden Contracts",
        "competitors": {
            "legaleagle": "https://www.youtube.com/@LegalEagle/videos",
            "steve_lehto": "https://www.youtube.com/@stevelehto/videos",
            "cnbc_make_it": "https://www.youtube.com/@CNBCmakeit/videos",
            "clearvalue_tax": "https://www.youtube.com/@ClearValueTax/videos",
        },
    },
    "en-crowd-strings": {
        "niche": "Mass Psychology & Social Influence",
        "competitors": {
            "academy_of_ideas": "https://www.youtube.com/@AcademyofIdeas/videos",
            "moon": "https://www.youtube.com/@Moon-Real/videos",
            "fern": "https://www.youtube.com/@Fern-TV/videos",
            "vox": "https://www.youtube.com/@Vox/videos",
        },
    },
    "en-cold-case-ink": {
        "niche": "Forensic Mysteries & Unsolved Archives",
        "competitors": {
            "lemmino": "https://www.youtube.com/@LEMMiNO/videos",
            "bedtime_stories": "https://www.youtube.com/@BedtimeStories/videos",
            "thoughty2": "https://www.youtube.com/@Thoughty2/videos",
            "johnny_harris": "https://www.youtube.com/@johnnyharris/videos",
        },
    },
    "en-choke-point": {
        "niche": "Maritime Geopolitics & Bottlenecks",
        "competitors": {
            "reallifelore": "https://www.youtube.com/@RealLifeLore/videos",
            "caspian_report": "https://www.youtube.com/@CaspianReport/videos",
            "johnny_harris": "https://www.youtube.com/@johnnyharris/videos",
            "polymatter": "https://www.youtube.com/@PolyMatter/videos",
        },
    },
}


def download_refs_for_channel(channel_slug: str) -> List[Path]:
    spec = CHANNEL_COMPETITORS.get(channel_slug)
    if not spec:
        raise ValueError(f"Unknown channel: {channel_slug}")

    chan_out = REFS_DIR / channel_slug
    chan_out.mkdir(parents=True, exist_ok=True)

    downloaded: List[Path] = []
    logger.info(f"[*] Downloading real competitor thumbnails for {channel_slug} ({spec['niche']})...")

    for comp_name, url in spec["competitors"].items():
        cmd = [
            "yt-dlp",
            "--playlist-items", "1",
            "--write-thumbnail",
            "--skip-download",
            "-o", f"{chan_out}/{comp_name}_%(id)s.%(ext)s",
            url,
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=25, text=True)
            logger.info(f"  [+] {comp_name} downloaded successfully.")
        except Exception as e:
            logger.warning(f"  [-] {comp_name} download error: {e}")

    for f in chan_out.glob("*.*"):
        if f.suffix.lower() in [".webp", ".jpg", ".jpeg", ".png"]:
            downloaded.append(f)

    logger.info(f"[✓] {channel_slug}: Found {len(downloaded)} competitor reference images.")
    return downloaded


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", help="Channel slug")
    parser.add_argument("--all", action="store_true", help="Download for all 18 channels")
    args = parser.parse_args()

    if args.channel:
        download_refs_for_channel(args.channel)
    elif args.all:
        for ch in CHANNEL_COMPETITORS:
            try:
                download_refs_for_channel(ch)
            except Exception as e:
                logger.error(f"Error {ch}: {e}")


if __name__ == "__main__":
    main()
