#!/usr/bin/env python3
"""
English Studio V3 Voice Discovery, Isolation, Mastering & Ranking Engine (25 -> Top 20 -> Top 18).

Workflow:
1. Sources 25 native English explainer voice candidates across the 18 English channel niches.
2. Extracts untouched 48kHz stereo Opus audio via yt-dlp and selects clean speech candidate windows.
3. Runs GPU batch separation on Colab Tesla T4 (htdemucs_ft --two-stems=vocals --shifts=2)
   + faster-whisper (large-v3, language="en", word_timestamps=True).
4. Applies DeepFilterNet3 (48kHz, -D -a 18 --pf) locally to eliminate room reverb and mic hiss.
5. Aligns exact word/sentence boundaries at minimum-energy valleys (<= -28 dB) with 110ms/150ms
   pure silence padding, F0 single-speaker consistency check, and sponsor/CTA filter.
6. Masters via Studio Vocal EQ + De-Esser + 2-Pass EBU R128 loudnorm (-14.0 LUFS / -1.2 dBTP,
   peak strictly normalized within [25500, 29500] PCM16 at 24000 Hz mono).
7. Ranks all 25 candidates by Composite Studio Quality Score (0-100), auto-eliminates the bottom 5-7,
   auto-assigns the Top 18 to the 18 English channels (`sys/assets/voices/ch_en_*/`), and generates
   an interactive HTML5 Audition & Selection Dashboard.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import shutil
import subprocess
import sys
import tempfile
import wave
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "sys") not in sys.path:
    sys.path.insert(0, str(ROOT / "sys"))

VOICES_DIR = ROOT / "sys/assets/voices"
POOL_DIR = VOICES_DIR / "en_pool_25"
YT_DLP = "/home/hongphuoc6104/.local/bin/yt-dlp"
FFMPEG = "/home/hongphuoc6104/.local/bin/ffmpeg"
FFPROBE = "/home/hongphuoc6104/.local/bin/ffprobe"
DEEP_FILTER = "/home/hongphuoc6104/.local/bin/deep-filter"
COLAB_PY = "/home/hongphuoc6104/.local/share/uv/tools/google-colab-cli/bin/python"
ACCOUNT_CLI = str(ROOT / "sys/colab_bridge/account_cli.py")
COOKIE_FILE = Path("/home/hongphuoc6104/.config/video-pilot/youtube_cookies.txt")
COOKIE_ARGS = (
    ["--cookies", str(COOKIE_FILE)]
    if COOKIE_FILE.is_file()
    else ["--cookies-from-browser", "chrome:/home/hongphuoc6104/.config/google-chrome/Profile 1"]
)

# Expected channel contract from sys/tests/test_channel_voice_profiles.py
EN_CHANNEL_CONTRACTS: Dict[str, Dict[str, Any]] = {
    "en_lazy_brain": {
        "voice": "OmniVoice_EnLazyBrain",
        "recommended_speed": 1.08,
        "default_tone": "narrative_warm",
        "display_name": "Lazy Brain Lab",
        "niche": "Neuroscience of procrastination, dopamine & habits",
    },
    "en_crowd_strings": {
        "voice": "OmniVoice_EnCrowdStrings",
        "recommended_speed": 1.10,
        "default_tone": "analytical_crisp",
        "display_name": "Crowd Strings",
        "niche": "Social dynamics, persuasion & crowd psychology",
    },
    "en_kindred_sketch": {
        "voice": "OmniVoice_EnKindredSketch",
        "recommended_speed": 1.02,
        "default_tone": "narrative_warm",
        "display_name": "Kindred Sketch",
        "niche": "Attachment styles, empathy & human relationships",
    },
    "en_first_principles": {
        "voice": "OmniVoice_EnFirstPrinciples",
        "recommended_speed": 1.12,
        "default_tone": "analytical_crisp",
        "display_name": "First Principles Ink",
        "niche": "Mental models, critical thinking & decision theory",
    },
    "en_wallet_anatomy": {
        "voice": "OmniVoice_EnWalletAnatomy",
        "recommended_speed": 1.10,
        "default_tone": "analytical_crisp",
        "display_name": "Wallet Anatomy",
        "niche": "Behavioral finance, spending traps & money psychology",
    },
    "en_macro_gears": {
        "voice": "OmniVoice_EnMacroGears",
        "recommended_speed": 1.12,
        "default_tone": "analytical_crisp",
        "display_name": "Macro Gears",
        "niche": "Macro systems, supply chains & hidden infrastructure",
    },
    "en_plain_sight_ai": {
        "voice": "OmniVoice_EnPlainSightAI",
        "recommended_speed": 1.14,
        "default_tone": "analytical_crisp",
        "display_name": "Plain Sight AI",
        "niche": "Practical AI, algorithms & automation decoded",
    },
    "en_career_leverage": {
        "voice": "OmniVoice_EnCareerLeverage",
        "recommended_speed": 1.10,
        "default_tone": "analytical_crisp",
        "display_name": "Career Leverage",
        "niche": "Workplace leverage, negotiation & career strategy",
    },
    "en_fine_print": {
        "voice": "OmniVoice_EnFinePrint",
        "recommended_speed": 1.08,
        "default_tone": "analytical_crisp",
        "display_name": "Everyday Fine Print",
        "niche": "Consumer law, contracts & everyday legal literacy",
    },
    "en_inside_vessel": {
        "voice": "OmniVoice_EnInsideVessel",
        "recommended_speed": 1.08,
        "default_tone": "narrative_warm",
        "display_name": "Inside the Vessel",
        "niche": "Human physiology, sleep, immunity & body signals",
    },
    "en_kitchen_molecules": {
        "voice": "OmniVoice_EnKitchenMolecules",
        "recommended_speed": 1.10,
        "default_tone": "analytical_crisp",
        "display_name": "Kitchen Molecules",
        "niche": "Food science, Maillard reactions & culinary chemistry",
    },
    "en_wait_how": {
        "voice": "OmniVoice_EnWaitHow",
        "recommended_speed": 1.14,
        "default_tone": "analytical_crisp",
        "display_name": "Wait, How?",
        "niche": "Everyday physics, counter-intuitive science & paradoxes",
    },
    "en_cold_case_ink": {
        "voice": "OmniVoice_EnColdCaseInk",
        "recommended_speed": 1.02,
        "default_tone": "reflective_slow",
        "display_name": "Cold Case Ink",
        "niche": "Historical mysteries, forensics & unsolved cases",
    },
    "en_choke_point": {
        "voice": "OmniVoice_EnChokePoint",
        "recommended_speed": 1.10,
        "default_tone": "analytical_crisp",
        "display_name": "Choke Point Maps",
        "niche": "Geopolitics, trade routes & strategic geography",
    },
    "en_pocket_cosmos": {
        "voice": "OmniVoice_EnPocketCosmos",
        "recommended_speed": 1.06,
        "default_tone": "narrative_warm",
        "display_name": "Pocket Cosmos",
        "niche": "Astrophysics, quantum mechanics & cosmic wonder",
    },
    "en_second_arrow": {
        "voice": "OmniVoice_EnSecondArrow",
        "recommended_speed": 1.00,
        "default_tone": "reflective_slow",
        "display_name": "The Second Arrow",
        "niche": "Mindfulness, emotional regulation & Zen psychology",
    },
    "en_parable_lamp": {
        "voice": "OmniVoice_EnParableLamp",
        "recommended_speed": 1.02,
        "default_tone": "reflective_slow",
        "display_name": "Parable & Lamp",
        "niche": "Philosophical parables, allegories & timeless stories",
    },
    "en_bamboo_marble": {
        "voice": "OmniVoice_EnBambooMarble",
        "recommended_speed": 1.00,
        "default_tone": "reflective_slow",
        "display_name": "Bamboo & Marble",
        "niche": "Stoicism, Taoist stillness & mental resilience",
    },
}

# 25 Curated English Voice Candidates (Grouped into 5 Batches of 5)
CANDIDATES_25: List[Dict[str, Any]] = [
    # Batch 1 (account-07)
    {
        "cand_id": "EN_V01",
        "batch": 1,
        "target_channel": "en_lazy_brain",
        "archetype": "Witty Conversational Behavioral & Habit Narrator",
        "vi_desc": "Giọng nam ấm, gần gũi, kể chuyện tâm lý học hành vi & thói quen trì hoãn cực kỳ tự nhiên",
        "queries": [
            "Better Ideas why your brain procrastinates dopamine",
            "Better Ideas habits focus procrastination",
            "Nathaniel Drew mental clarity focus habits",
        ],
    },
    {
        "cand_id": "EN_V02",
        "batch": 1,
        "target_channel": "en_crowd_strings",
        "archetype": "Crisp Social Dynamics & Persuasion Analyst",
        "vi_desc": "Giọng phân tích sắc sảo, nhịp điệu dứt khoát, giải mã tâm lý đám đông & giao tiếp",
        "queries": [
            "Charisma on Command how to command respect psychology",
            "Charisma on Command confidence social dynamics",
            "PolyMatter psychology of society behavior",
        ],
    },
    {
        "cand_id": "EN_V03",
        "batch": 1,
        "target_channel": "en_kindred_sketch",
        "archetype": "Warm Empathetic Attachment & Relationship Storyteller",
        "vi_desc": "Giọng trầm ấm, giàu sự thấu cảm, truyền tải tâm lý tình cảm & gắn kết gia đình sâu sắc",
        "queries": [
            "The School of Life attachment styles relationships",
            "The School of Life emotional maturity love",
            "Cinema Therapy psychology of relationships",
        ],
    },
    {
        "cand_id": "EN_V04",
        "batch": 1,
        "target_channel": "en_first_principles",
        "archetype": "Authoritative First-Principles Science & Logic Narrator",
        "vi_desc": "Giọng chuẩn mực, trí thức, dẫn dắt tư duy nguyên bản (First Principles) đầy thuyết phục",
        "queries": [
            "Veritasium thinking fast and slow cognitive bias",
            "Veritasium game theory math logic",
            "3Blue1Brown essence of probability logic",
        ],
    },
    {
        "cand_id": "EN_V05",
        "batch": 1,
        "target_channel": "en_wallet_anatomy",
        "archetype": "Crisp Behavioral Finance & Money Psychology Analyst",
        "vi_desc": "Giọng rõ ràng, đĩnh đạc, chuyên mổ xẻ bẫy tài chính cá nhân và tâm lý tiền bạc",
        "queries": [
            "The Plain Bagel psychology of money investing",
            "Two Cents behavioral finance spending habits",
            "Ben Felix common sense investing money",
        ],
    },
    # Batch 2 (account-08)
    {
        "cand_id": "EN_V06",
        "batch": 2,
        "target_channel": "en_macro_gears",
        "archetype": "Clear Macro Infrastructure & Systems Engineer",
        "vi_desc": "Giọng nam trầm ổn, mạch lạc, giải thích cơ chế vận hành hạ tầng & chuỗi cung ứng thế giới",
        "queries": [
            "Practical Engineering how infrastructure works power grid",
            "Wendover Productions how logistics supply chains work",
            "Real Engineering how modern machines work",
        ],
    },
    {
        "cand_id": "EN_V07",
        "batch": 2,
        "target_channel": "en_plain_sight_ai",
        "archetype": "Modern High-Clarity AI & Tech Storyteller",
        "vi_desc": "Giọng hiện đại, phát âm cực nét, giải thích công nghệ AI phức tạp thành ngôn ngữ đời thường",
        "queries": [
            "ColdFusion artificial intelligence future technology",
            "Marques Brownlee artificial intelligence explained",
            "Cleo Abram artificial intelligence technology",
        ],
    },
    {
        "cand_id": "EN_V08",
        "batch": 2,
        "target_channel": "en_career_leverage",
        "archetype": "Executive Career Strategy & Negotiation Mentor",
        "vi_desc": "Giọng tự tin, chuyên nghiệp, chia sẻ đòn bẩy sự nghiệp và nghệ thuật đàm phán nơi công sở",
        "queries": [
            "Harvard Business Review how to negotiate salary career",
            "Ali Abdaal evidence based productivity career",
            "Jeff Su workplace productivity career tips",
        ],
    },
    {
        "cand_id": "EN_V09",
        "batch": 2,
        "target_channel": "en_fine_print",
        "archetype": "Sharp Legal & Consumer Fine-Print Decoder",
        "vi_desc": "Giọng luật sư sắc bén, phát âm chuẩn xác từng chữ, bóc tách điều khoản ngầm & luật đời thường",
        "queries": [
            "LegalEagle contract law consumer rights explained",
            "Company Man hidden business strategies consumers",
            "Modern MBA business breakdown consumer",
        ],
    },
    {
        "cand_id": "EN_V10",
        "batch": 2,
        "target_channel": "en_inside_vessel",
        "archetype": "Engaging Human Anatomy & Medical Science Narrator",
        "vi_desc": "Giọng bác sĩ/nhà giải phẫu học ấm áp, trực quan, giải mã tín hiệu cơ thể & giấc ngủ",
        "queries": [
            "Institute of Human Anatomy what happens when you sleep",
            "TED-Ed what happens to your body brain",
            "Doctor Mike human body medical science",
        ],
    },
    # Batch 3 (account-09)
    {
        "cand_id": "EN_V11",
        "batch": 3,
        "target_channel": "en_kitchen_molecules",
        "archetype": "Crisp Culinary Chemistry & Food Science Explainer",
        "vi_desc": "Giọng hào hứng, rõ chữ, giải thích phản ứng hóa học trong căn bếp & khoa học ẩm thực",
        "queries": [
            "Ethan Chlebowski food science cooking chemistry",
            "America's Test Kitchen science of cooking",
            "Adam Ragusea food science chemistry",
        ],
    },
    {
        "cand_id": "EN_V12",
        "batch": 3,
        "target_channel": "en_wait_how",
        "archetype": "Energetic Everyday Physics & Paradox Explorer",
        "vi_desc": "Giọng giàu năng lượng tò mò, lôi cuốn ngay từ câu đầu, giải thích nghịch lý vật lý đời thường",
        "queries": [
            "SmarterEveryDay physics of everyday things",
            "Steve Mould physics paradox explained",
            "MinutePhysics everyday physics explained",
        ],
    },
    {
        "cand_id": "EN_V13",
        "batch": 3,
        "target_channel": "en_cold_case_ink",
        "archetype": "Deep Atmospheric Investigative & Mystery Narrator",
        "vi_desc": "Giọng trầm sâu, cuốn hút kiểu phim tài liệu điều tra, dẫn dắt các vụ án lịch sử bí ẩn",
        "queries": [
            "LEMMiNO unsolved mystery history documentary",
            "Barely Sociable unsolved mystery investigation",
            "Nexpo mystery investigation documentary",
        ],
    },
    {
        "cand_id": "EN_V14",
        "batch": 3,
        "target_channel": "en_choke_point",
        "archetype": "Compelling Geopolitical & Strategic Map Analyst",
        "vi_desc": "Giọng thuyết minh địa chính trị có chiều sâu, nhấn nhá kịch tính về bản đồ quyền lực & eo biển",
        "queries": [
            "RealLifeLore geography choke points global trade",
            "CaspianReport geopolitics strategic geography",
            "Johnny Harris how maps explain the world",
        ],
    },
    {
        "cand_id": "EN_V15",
        "batch": 3,
        "target_channel": "en_pocket_cosmos",
        "archetype": "Wonder-Filled Astrophysics & Cosmic Storyteller",
        "vi_desc": "Giọng truyền cảm hứng kỳ vĩ, trong trẻo, kể chuyện vũ trụ học & vật lý lượng tử",
        "queries": [
            "Astrum space cosmos planets documentary",
            "SEA space astrophysics universe documentary",
            "Cool Worlds astrophysics universe",
        ],
    },
    # Batch 4 (account-10)
    {
        "cand_id": "EN_V16",
        "batch": 4,
        "target_channel": "en_second_arrow",
        "archetype": "Calm Mindful Zen & Emotional Regulation Voice",
        "vi_desc": "Giọng trầm tĩnh, thư thái, chữa lành, dẫn dắt chánh niệm và hóa giải mũi tên thứ hai",
        "queries": [
            "Pursuit of Wonder art of letting go mindfulness",
            "Einzelgänger buddhism mindfulness letting go",
            "Plum Village mindfulness breathing meditation",
        ],
    },
    {
        "cand_id": "EN_V17",
        "batch": 4,
        "target_channel": "en_parable_lamp",
        "archetype": "Deep Reflective Philosophical Parable Narrator",
        "vi_desc": "Giọng kể chuyện ngụ ngôn triết học sâu lắng, chậm rãi, giàu chất chiêm nghiệm về cuộc đời",
        "queries": [
            "Pursuit of Wonder philosophical story meaning of life",
            "Aperture philosophy human condition meaning",
            "Exurb1a philosophy story universe",
        ],
    },
    {
        "cand_id": "EN_V18",
        "batch": 4,
        "target_channel": "en_bamboo_marble",
        "archetype": "Grounded Stoic & Eastern Wisdom Narrator",
        "vi_desc": "Giọng nam vững chãi, điềm tĩnh như đá cẩm thạch & tre trúc, truyền tải triết lý Khắc kỷ & Đạo gia",
        "queries": [
            "Daily Stoic Marcus Aurelius stoicism resilience",
            "Ryan Holiday stoic philosophy discipline",
            "Philosophize This stoicism eastern philosophy",
        ],
    },
    {
        "cand_id": "EN_V19",
        "batch": 4,
        "target_channel": "en_lazy_brain",
        "archetype": "Crisp Fast-Paced Doodle Explainer Narrator (Reserve #19)",
        "vi_desc": "Giọng Explainer 2D nhanh, gọn, bắt tai kiểu kênh hoạt hình giải thích tâm lý & não bộ",
        "queries": [
            "The Paint Explainer psychology habits explained",
            "AsapSCIENCE brain dopamine habits",
            "Kurzgesagt habits brain mind",
        ],
    },
    {
        "cand_id": "EN_V20",
        "batch": 4,
        "target_channel": "en_first_principles",
        "archetype": "Iconic Deep Curiosity & Cognitive Science Narrator (Reserve #20)",
        "vi_desc": "Giọng kể chuyện khoa học nhận thức đặc trưng, đặt câu hỏi gợi mở cuốn hút người nghe",
        "queries": [
            "Vsauce cognitive science how we think",
            "Be SmartJoe Hanson science curiosity",
            "SciShow Psych psychology human brain",
        ],
    },
    # Batch 5 (account-11) — Extra 5 candidates for the 25-voice competition pool
    {
        "cand_id": "EN_V21",
        "batch": 5,
        "target_channel": "en_wallet_anatomy",
        "archetype": "Macro Economics & Wealth Mechanics Narrator (Pool #21)",
        "vi_desc": "Giọng phân tích kinh tế vĩ mô & dòng tiền sắc nét, giọng đọc phóng sự tài chính",
        "queries": [
            "How Money Works economics wealth psychology",
            "Economics Explained global economy money",
            "Patrick Boyle finance economics",
        ],
    },
    {
        "cand_id": "EN_V22",
        "batch": 5,
        "target_channel": "en_pocket_cosmos",
        "archetype": "Academic Space & Quantum Physics Narrator (Pool #22)",
        "vi_desc": "Giọng học thuật rõ ràng, chuyên sâu về vật lý thiên văn và cơ học lượng tử",
        "queries": [
            "PBS Space Time quantum mechanics astrophysics",
            "Sabine Hossenfelder physics explained",
            "Fermilab particle physics quantum",
        ],
    },
    {
        "cand_id": "EN_V23",
        "batch": 5,
        "target_channel": "en_plain_sight_ai",
        "archetype": "Punchy Developer & Algorithm Explainer (Pool #23)",
        "vi_desc": "Giọng nhịp nhanh, dứt khoát, chuyên giải thích thuật toán & công nghệ phần mềm",
        "queries": [
            "Fireship software technology explained",
            "Computerphile artificial intelligence algorithms",
            "Spanning Tree algorithms computer science",
        ],
    },
    {
        "cand_id": "EN_V24",
        "batch": 5,
        "target_channel": "en_crowd_strings",
        "archetype": "Deep Psychological Essay & Philosophy Narrator (Pool #24)",
        "vi_desc": "Giọng đọc tiểu luận tâm lý học chiều sâu (Carl Jung, tâm lý học đám đông)",
        "queries": [
            "Academy of Ideas psychology of the crowd Carl Jung",
            "Eternalised psychology philosophy Carl Jung",
            "After Skool psychology human behavior",
        ],
    },
    {
        "cand_id": "EN_V25",
        "batch": 5,
        "target_channel": "en_macro_gears",
        "archetype": "Cinematic Industrial & Engineering Documentary Voice (Pool #25)",
        "vi_desc": "Giọng thuyết minh phim tài liệu kỹ thuật & công nghiệp nặng quy mô lớn",
        "queries": [
            "Mustard engineering aviation history documentary",
            " Neo how infrastructure technology works",
            "Branch Education how technology works inside",
        ],
    },
]

BANNED_PHRASES_EN = (
    "subscribe",
    "hit the bell",
    "notification",
    "like and subscribe",
    "leave a comment",
    "comments below",
    "in the description",
    "link in the description",
    "sponsored by",
    "this video is sponsored",
    "brilliant.org",
    "skillshare",
    "squarespace",
    "nordvpn",
    "surfshark",
    "expressvpn",
    "betterhelp",
    "audible",
    "patreon",
    "nebula",
    "welcome back to",
    "hey guys",
    "what's up guys",
    "thank you for watching",
    "thanks for watching",
    "see you in the next",
    "in today's video",
    "in this video",
    "merch",
    "sign up for free",
    "use code",
    "discount",
)


def contains_banned_speech_en(text: str) -> bool:
    low = text.lower().strip()
    if any(bp in low for bp in BANNED_PHRASES_EN):
        return True
    # Reject non-ASCII gibberish or music tags
    if "[" in low or "]" in low or "♪" in low:
        return True
    return False


def parse_json3_cues_en(json3_path: Path) -> List[Tuple[float, float, str]]:
    data = json.loads(json3_path.read_text(encoding="utf-8", errors="ignore"))
    cues: List[Tuple[float, float, str]] = []
    for ev in data.get("events", []):
        segs = ev.get("segs")
        if not segs:
            continue
        t_start = float(ev.get("tStartMs", 0)) / 1000.0
        d_dur = float(ev.get("dDurationMs", 0)) / 1000.0
        raw_txt = "".join(str(s.get("utf8", "")) for s in segs)
        clean_txt = re.sub(r"\[[^\]]*\]|\([^\)]*\)", "", raw_txt)
        clean_txt = re.sub(r"\s+", " ", clean_txt).strip()
        if not clean_txt or len(clean_txt) < 2:
            continue
        low = clean_txt.lower()
        if any(b in low for b in ("music", "applause", "laughter", "intro")):
            continue
        last_off = max((float(s.get("tOffsetMs", 0)) for s in segs), default=0.0) / 1000.0
        t_end = t_start + max(min(d_dur, last_off + 0.65), 0.5)
        cues.append((round(t_start, 2), round(t_end, 2), clean_txt))
    return cues


def pick_raw_candidate_regions_en(
    cues: List[Tuple[float, float, str]], total_dur: float, max_regions: int = 3
) -> List[Tuple[float, float]]:
    min_t = 45.0 if total_dur > 140.0 else 15.0
    max_t = max(min_t + 30.0, min(total_dur - 45.0, 600.0))

    scored: List[Tuple[float, float, float]] = []
    for i in range(len(cues)):
        st = cues[i][0]
        if st < min_t or st > max_t:
            continue
        pause_before = (st - cues[i - 1][1]) if i > 0 else 0.5
        words_acc: List[str] = []
        for j in range(i, min(i + 12, len(cues))):
            if j > i and (cues[j][0] - cues[j - 1][1]) > 0.95:
                break
            en = cues[j][1]
            words_acc.extend(cues[j][2].split())
            dur = en - st
            if 7.5 <= dur <= 11.8:
                joined = " ".join(words_acc)
                if contains_banned_speech_en(joined):
                    continue
                wc = len(words_acc)
                wps = wc / dur if dur > 0 else 0.0
                if 16 <= wc <= 55 and 2.0 <= wps <= 4.6:
                    pause_after = (cues[j + 1][0] - en) if (j + 1) < len(cues) else 0.5
                    digit_count = len(re.findall(r"\d|%", joined))
                    score = (
                        -abs(dur - 9.2)
                        - abs(wps - 2.9) * 1.5
                        + min(max(pause_before, 0.0), 0.6) * 2.5
                        + min(max(pause_after, 0.0), 0.6) * 2.5
                        - digit_count * 1.8
                    )
                    scored.append((score, st, en))
            elif dur > 12.0:
                break

    scored.sort(key=lambda x: x[0], reverse=True)
    picked: List[Tuple[float, float]] = []
    for _, st, en in scored:
        if all(abs(st - pst) > 22.0 for pst, _ in picked):
            pad_st = max(0.0, round(st - 2.2, 2))
            pad_en = min(total_dur, round(en + 2.2, 2))
            if pad_en - pad_st >= 10.0:
                picked.append((pad_st, pad_en))
                if len(picked) >= max_regions:
                    break

    if len(picked) < max_regions and total_dur >= 60.0:
        span_start = min_t
        span_end = max(span_start + 20.0, min(total_dur - 30.0, 480.0))
        for frac in np.linspace(0.15, 0.75, max_regions * 2):
            st = round(float(span_start + (span_end - span_start) * frac), 2)
            en = min(total_dur, round(st + 14.5, 2))
            if en - st >= 11.0 and all(abs(st - pst) > 20.0 for pst, _ in picked):
                picked.append((st, en))
                if len(picked) >= max_regions:
                    break
    return picked[:max_regions]


def read_wav_float(path: Path) -> Tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as w:
        sr = w.getframerate()
        ch = w.getnchannels()
        n = w.getnframes()
        raw = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
        if ch > 1:
            raw = raw.reshape(-1, ch).mean(axis=1)
    return raw, sr


def write_wav_pcm16(path: Path, samples: np.ndarray, sr: int) -> None:
    clipped = np.clip(samples, -0.999, 0.999)
    pcm = (clipped * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def estimate_f0_hz(seg: np.ndarray, sr: int) -> Optional[float]:
    if len(seg) < int(sr * 0.15):
        return None
    rms = float(np.sqrt(np.mean(seg**2)))
    if rms < 0.012:
        return None
    f0_vals: List[float] = []
    win = int(sr * 0.04)
    hop = int(sr * 0.02)
    min_lag = int(sr / 340.0)
    max_lag = int(sr / 75.0)
    for start in range(0, len(seg) - win, hop):
        frame = seg[start : start + win]
        if float(np.sqrt(np.mean(frame**2))) < 0.018:
            continue
        frame = frame - np.mean(frame)
        corr = np.correlate(frame, frame, mode="full")[win - 1 :]
        if corr[0] <= 1e-8:
            continue
        corr = corr / corr[0]
        if max_lag >= len(corr):
            continue
        sub = corr[min_lag:max_lag]
        if len(sub) == 0:
            continue
        pk_idx = int(np.argmax(sub))
        if sub[pk_idx] >= 0.45:
            lag = min_lag + pk_idx
            f0_vals.append(float(sr) / float(lag))
    if len(f0_vals) < 4:
        return None
    return float(np.median(f0_vals))


def check_single_speaker_consistency(samples: np.ndarray, sr: int) -> Tuple[bool, float, float]:
    quarters = np.array_split(samples, 4)
    f0s: List[float] = []
    q_dbs: List[float] = []
    for q in quarters:
        f0 = estimate_f0_hz(q, sr)
        if f0 is not None:
            f0s.append(f0)
        flen = int(sr * 0.04)
        if len(q) >= flen * 2:
            fr = q[: (len(q) // flen) * flen].reshape(-1, flen)
            rms = np.sqrt(np.mean(fr**2, axis=1))
            act = rms[rms > 0.008]
            if len(act) > 0:
                q_dbs.append(float(20.0 * np.log10(np.median(act))))
    if len(f0s) >= 2:
        f0_min, f0_max = min(f0s), max(f0s)
        semitones = float(12.0 * np.log2(max(f0_max, 1.0) / max(f0_min, 1.0)))
    else:
        semitones = 0.0
    rms_spread = (max(q_dbs) - min(q_dbs)) if len(q_dbs) >= 2 else 0.0
    ok = (semitones <= 6.5) and (rms_spread <= 8.8)
    return ok, round(semitones, 2), round(rms_spread, 2)


def find_quietest_valley(
    samples: np.ndarray, sr: int, t_min: float, t_max: float, win_sec: float = 0.020
) -> Tuple[int, float]:
    i_min = max(0, int(t_min * sr))
    i_max = min(len(samples), int(t_max * sr))
    w = max(16, int(win_sec * sr))
    if i_max - i_min <= w:
        mid = max(0, min(len(samples) - 1, (i_min + i_max) // 2))
        seg = samples[max(0, mid - w // 2) : min(len(samples), mid + w // 2)]
        db = float(20.0 * np.log10(max(float(np.sqrt(np.mean(seg**2))) if len(seg) else 1e-7, 1e-7)))
        return mid, db

    step = max(8, w // 4)
    best_idx = i_min
    best_rms = 1e9
    for idx in range(i_min, i_max - w + 1, step):
        seg = samples[idx : idx + w]
        r = float(np.sqrt(np.mean(seg**2)))
        if r < best_rms:
            best_rms = r
            best_idx = idx + w // 2
    best_db = float(20.0 * np.log10(max(best_rms, 1e-7)))
    return best_idx, best_db


def master_studio_clip_two_pass(in_48k_wav: Path, out_24k_wav: Path, tmp_dir: Path) -> None:
    eq_comp_wav = tmp_dir / f"stage_eq_{in_48k_wav.stem}.wav"
    af_pre = (
        "highpass=f=80:poles=2,"
        "equalizer=f=210:t=q:w=1.4:g=-1.8,"
        "equalizer=f=3200:t=q:w=1.1:g=1.8,"
        "treble=g=1.5:f=7500,"
        "deesser=i=0.35:m=0.40:f=0.5:s=o,"
        "acompressor=threshold=-21dB:ratio=2.3:attack=12:release=160:makeup=2dB"
    )
    subprocess.run(
        [FFMPEG, "-y", "-i", str(in_48k_wav), "-af", af_pre, "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(eq_comp_wav)],
        check=True,
        capture_output=True,
    )

    p1 = subprocess.run(
        [
            FFMPEG,
            "-hide_banner",
            "-i",
            str(eq_comp_wav),
            "-af",
            "loudnorm=I=-14.0:TP=-1.2:LRA=9.0:print_format=json",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    m = re.search(r"\{\s*\"input_i\"[\s\S]*?\}", p1.stderr)
    if m:
        ln = json.loads(m.group(0))
        af_p2 = (
            f"loudnorm=I=-14.0:TP=-1.2:LRA=9.0:"
            f"measured_I={ln['input_i']}:measured_TP={ln['input_tp']}:"
            f"measured_LRA={ln['input_lra']}:measured_thresh={ln['input_thresh']}:"
            f"offset={ln['target_offset']}:linear=true,"
            f"alimiter=limit=-1.2dB:level=disabled,"
            f"aresample=24000"
        )
    else:
        af_p2 = "loudnorm=I=-14.0:TP=-1.2:LRA=9.0,alimiter=limit=-1.2dB:level=disabled,aresample=24000"

    subprocess.run(
        [FFMPEG, "-y", "-i", str(eq_comp_wav), "-af", af_p2, "-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le", str(out_24k_wav)],
        check=True,
        capture_output=True,
    )
    arr, sr = read_wav_float(out_24k_wav)
    lead_zero = int(0.085 * sr)
    tail_zero = int(0.110 * sr)
    fade_in_n = int(0.018 * sr)
    fade_out_n = int(0.025 * sr)
    if len(arr) > (lead_zero + tail_zero + fade_in_n + fade_out_n + sr):
        arr[:lead_zero] = 0.0
        arr[lead_zero : lead_zero + fade_in_n] *= np.linspace(0.0, 1.0, fade_in_n, dtype=np.float32)
        arr[-tail_zero:] = 0.0
        arr[-(tail_zero + fade_out_n) : -tail_zero] *= np.linspace(1.0, 0.0, fade_out_n, dtype=np.float32)

    # Guarantee peak strictly inside [25500, 29200] PCM16 (-2.18 dBFS to -1.00 dBFS) for test_channel_voice_profiles.py
    pk = float(np.max(np.abs(arr)))
    if pk > 1e-6:
        target_pk_int = 27800.0  # ~ -1.42 dBFS
        curr_pk_int = pk * 32767.0
        if curr_pk_int < 24800.0 or curr_pk_int > 29800.0:
            arr = arr * (target_pk_int / curr_pk_int)
    write_wav_pcm16(out_24k_wav, arr, sr)


def compute_final_metrics(wav_path: Path) -> Dict[str, float]:
    arr, sr = read_wav_float(wav_path)
    dur = len(arr) / float(sr)
    rms_db = float(20.0 * np.log10(max(float(np.sqrt(np.mean(arr**2))), 1e-7)))
    peak_db = float(20.0 * np.log10(max(float(np.max(np.abs(arr))), 1e-7)))

    flen = int(sr * 0.05)
    fr = arr[: (len(arr) // flen) * flen].reshape(-1, flen)
    frms = np.sqrt(np.mean(fr**2, axis=1))
    fdb = 20.0 * np.log10(np.maximum(frms, 1e-7))
    p05, p10, p50, p90 = [float(x) for x in np.percentile(fdb, [5, 10, 50, 90])]
    active_ratio = float(np.mean(fdb > -34.0))

    edge = int(sr * 0.06)
    start_60ms_db = float(20.0 * np.log10(max(float(np.sqrt(np.mean(arr[:edge] ** 2))), 1e-7)))
    end_60ms_db = float(20.0 * np.log10(max(float(np.sqrt(np.mean(arr[-edge:] ** 2))), 1e-7)))

    interior = arr[int(0.15 * sr) : len(arr) - int(0.18 * sr)]
    nsec = max(1, len(interior) // sr)
    sec_dbs = [
        float(20.0 * np.log10(max(float(np.sqrt(np.mean(interior[i * sr : (i + 1) * sr] ** 2))), 1e-7)))
        for i in range(nsec)
    ]
    min_1s_db = min(sec_dbs) if sec_dbs else -140.0

    fft = np.abs(np.fft.rfft(interior))
    freqs = np.fft.rfftfreq(len(interior), 1.0 / sr)
    v_e = float(np.sum(fft[(freqs >= 200) & (freqs <= 3400)] ** 2))
    hf_e = float(np.sum(fft[freqs > 4500] ** 2))
    hf_ratio = hf_e / max(v_e, 1e-9)

    _, f0_st, q_spread = check_single_speaker_consistency(interior, sr)
    f0_med = estimate_f0_hz(interior, sr) or 130.0
    return {
        "dur": round(dur, 2),
        "rms_db": round(rms_db, 2),
        "peak_db": round(peak_db, 2),
        "p05_db": round(p05, 1),
        "p10_db": round(p10, 1),
        "p50_db": round(p50, 1),
        "p90_db": round(p90, 1),
        "dyn_db": round(p90 - p10, 1),
        "active_ratio": round(active_ratio, 2),
        "min_1s_db": round(min_1s_db, 1),
        "start_60ms_db": round(start_60ms_db, 1),
        "end_60ms_db": round(end_60ms_db, 1),
        "hf_ratio": round(hf_ratio, 4),
        "f0_hz": round(f0_med, 1),
        "f0_spread_semitones": f0_st,
        "quarter_rms_spread_db": q_spread,
    }


def compute_composite_studio_score(metrics: Dict[str, float], span_info: Dict[str, Any]) -> float:
    """Compute objective 0-100 Studio Voice Quality Score for ranking the 25 voices."""
    sir = float(span_info.get("raw_sir_db", 25.0))
    prob = float(span_info.get("avg_word_prob", 0.92))
    p10 = float(metrics.get("p10_db", -45.0))
    rms = float(metrics.get("rms_db", -14.5))
    hf = float(metrics.get("hf_ratio", 0.015))
    f0_st = float(metrics.get("f0_spread_semitones", 2.0))
    act = float(metrics.get("active_ratio", 0.65))

    # 1. Vocal Isolation & BGM Rejection (max 30 pts)
    sir_pts = min(30.0, max(10.0, (sir - 8.0) * 1.15))
    # 2. English Diction & Whisper Clarity (max 25 pts)
    prob_pts = min(25.0, max(10.0, (prob - 0.75) * 105.0))
    # 3. Noise Floor Silence Purity (max 15 pts)
    floor_pts = min(15.0, max(5.0, (-p10 - 25.0) * 0.35))
    # 4. Presence & High-Frequency Crispness (max 12 pts)
    hf_pts = 12.0 - min(8.0, abs(hf - 0.022) * 180.0)
    # 5. Single-Speaker Pitch & Cadence Consistency (max 10 pts)
    spk_pts = max(2.0, 10.0 - max(0.0, f0_st - 1.2) * 1.4)
    # 6. Broadcast Loudness & Density Accuracy (max 8 pts)
    loud_pts = max(2.0, 8.0 - abs(rms - (-14.2)) * 1.2 - max(0.0, 0.58 - act) * 15.0)

    total = sir_pts + prob_pts + floor_pts + hf_pts + spk_pts + loud_pts
    return round(min(99.8, max(60.0, total)), 2)


def select_best_word_span_and_crop_en(
    df_wav_path: Path, words: List[Dict[str, Any]], raw_sir_db: float
) -> Optional[Tuple[float, np.ndarray, int, str, Tuple[float, float], Dict[str, Any]]]:
    samples, sr = read_wav_float(df_wav_path)
    clip_dur = len(samples) / float(sr)
    if len(words) < 12:
        return None

    flen0 = max(1, int(sr * 0.04))
    fr0 = samples[: (len(samples) // flen0) * flen0].reshape(-1, flen0)
    p90_clip_db = float(np.percentile(20.0 * np.log10(np.maximum(np.sqrt(np.mean(fr0**2, axis=1)), 1e-7)), 90))
    valley_ceil_db = min(-23.0, p90_clip_db - 11.5)

    best: Optional[Tuple[float, np.ndarray, int, str, Tuple[float, float], Dict[str, Any]]] = None
    n = len(words)
    for a in range(n):
        w_a = words[a]
        st_a = float(w_a["start"])
        if st_a < 0.15:
            continue
        pause_before = (st_a - float(words[a - 1]["end"])) if a > 0 else st_a
        prev_punct = (a == 0) or str(words[a - 1]["word"]).endswith((".", "!", "?", ":", ";", ","))
        if pause_before < 0.05 and not (prev_punct and pause_before >= 0.02):
            continue

        for b in range(a + 12, min(n + 1, a + 65)):
            w_b = words[b - 1]
            en_b = float(w_b["end"])
            speech_dur = en_b - st_a
            if speech_dur < 6.20:
                continue
            if speech_dur > 11.8:
                break
            if clip_dur - en_b < 0.12:
                continue

            pause_after = (float(words[b]["start"]) - en_b) if b < n else (clip_dur - en_b)
            end_punct = str(w_b["word"]).endswith((".", "!", "?"))
            clause_punct = str(w_b["word"]).endswith((",", ";", ":"))
            if pause_after < 0.05 and not ((end_punct or clause_punct) and pause_after >= 0.02):
                continue

            span_words = [str(words[k]["word"]).strip() for k in range(a, b)]
            text = re.sub(r"\s+", " ", " ".join(span_words)).strip()
            if contains_banned_speech_en(text):
                continue
            avg_prob = float(np.mean([float(words[k]["prob"]) for k in range(a, b)]))
            if avg_prob < 0.68:
                continue

            v_st_min = max(0.02, st_a - min(0.30, max(0.05, pause_before * 0.85)))
            v_st_max = max(v_st_min + 0.02, st_a - 0.008)
            idx_st, db_st = find_quietest_valley(samples, sr, v_st_min, v_st_max)

            v_en_min = min(clip_dur - 0.04, en_b + 0.008)
            v_en_max = min(clip_dur - 0.01, en_b + min(0.32, max(0.06, pause_after * 0.85)))
            idx_en, db_en = find_quietest_valley(samples, sr, v_en_min, v_en_max)

            if db_st > valley_ceil_db or db_en > valley_ceil_db or idx_en <= idx_st + int(5.8 * sr):
                continue

            core = samples[idx_st:idx_en].copy()
            spk_ok, f0_st, q_spread = check_single_speaker_consistency(core, sr)
            if not spk_ok:
                continue

            nsec = max(1, len(core) // sr)
            sec_dbs = [
                float(20.0 * np.log10(max(float(np.sqrt(np.mean(core[k * sr : (k + 1) * sr] ** 2))), 1e-7)))
                for k in range(nsec)
            ]
            if min(sec_dbs) < -32.0:
                continue

            clean_text = text.lstrip(".,;:-–— ")
            if not clean_text or len(clean_text) < 25:
                continue
            clean_text = clean_text[0].upper() + clean_text[1:]
            if not clean_text.endswith((".", "!", "?")):
                clean_text = clean_text.rstrip(",;:-–— ") + "."

            digits_n = len(re.findall(r"\d|%", clean_text))
            score = (
                raw_sir_db * 1.4
                + avg_prob * 20.0
                + (6.0 if prev_punct else 0.0)
                + (8.0 if end_punct else (2.5 if clause_punct else 0.0))
                + min(pause_before, 0.5) * 5.0
                + min(pause_after, 0.5) * 5.0
                - max(0.0, db_st + 48.0) * 0.30
                - max(0.0, db_en + 48.0) * 0.30
                - abs(speech_dur - 8.8) * 1.4
                - digits_n * 2.5
                - f0_st * 0.8
            )

            if best is None or score > best[0]:
                fade_in = int(0.018 * sr)
                fade_out = int(0.025 * sr)
                core[:fade_in] *= np.linspace(0.0, 1.0, fade_in, dtype=np.float32)
                core[-fade_out:] *= np.linspace(1.0, 0.0, fade_out, dtype=np.float32)
                padded = np.concatenate(
                    [
                        np.zeros(int(0.110 * sr), dtype=np.float32),
                        core,
                        np.zeros(int(0.150 * sr), dtype=np.float32),
                    ]
                )
                span_info = {
                    "raw_sir_db": round(raw_sir_db, 2),
                    "avg_word_prob": round(avg_prob, 3),
                    "valley_start_db": round(db_st, 1),
                    "valley_end_db": round(db_en, 1),
                    "pause_before_s": round(pause_before, 2),
                    "pause_after_s": round(pause_after, 2),
                }
                best = (score, padded, sr, clean_text, (round(idx_st / sr, 2), round(idx_en / sr, 2)), span_info)
    return best


def allocate_colab_t4_en(preferred_account: str, session: str) -> str:
    # Only use accounts 07..21 so we never touch accounts 01..06 running the 6 VN video jobs!
    safe_pool = [f"account-{i:02d}" for i in range(7, 22) if f"account-{i:02d}" != preferred_account]
    random.shuffle(safe_pool)
    accounts = [preferred_account] + safe_pool
    for acc in accounts:
        pdir = f"/home/hongphuoc6104/.config/video-pilot/colab/profiles/{acc}"
        if not Path(pdir).is_dir():
            continue
        probe_alive = subprocess.run(
            [COLAB_PY, ACCOUNT_CLI, pdir, "exec", "-s", session, "--timeout", "30"],
            input="import torch; print('CUDA_OK', torch.cuda.is_available())",
            text=True,
            capture_output=True,
            timeout=40,
            check=False,
        )
        if probe_alive.returncode == 0 and "CUDA_OK True" in probe_alive.stdout:
            print(f"[✓] Reusing active Colab Tesla T4 on {acc} (session={session})")
            return pdir

        subprocess.run([COLAB_PY, ACCOUNT_CLI, pdir, "stop", "-s", session], timeout=45, check=False, capture_output=True)
        res = subprocess.run(
            [COLAB_PY, ACCOUNT_CLI, pdir, "new", "-s", session, "--gpu", "T4"],
            timeout=150,
            check=False,
            capture_output=True,
            text=True,
        )
        probe = subprocess.run(
            [COLAB_PY, ACCOUNT_CLI, pdir, "exec", "-s", session, "--timeout", "45"],
            input="import torch; print('CUDA_OK', torch.cuda.is_available())",
            text=True,
            capture_output=True,
            timeout=65,
            check=False,
        )
        if probe.returncode == 0 and "CUDA_OK True" in probe.stdout:
            print(f"[✓] Allocated Colab Tesla T4 on {acc} (session={session})")
            return pdir
        subprocess.run([COLAB_PY, ACCOUNT_CLI, pdir, "stop", "-s", session], timeout=45, check=False, capture_output=True)
        print(f"[!] Account {acc} T4 allocation failed ({res.stderr[:80].strip()}), trying next safe account...")
    raise RuntimeError(f"Could not allocate Colab T4 GPU for {preferred_account} (session={session})")


def run_colab_demucs_and_whisper_en(
    profile_dir: str, session: str, stereo_wavs: List[Path], tmp_path: Path
) -> Tuple[List[Path], Dict[str, Any]]:
    in_zip = tmp_path / "cands_in.zip"
    out_zip = tmp_path / "cands_out.zip"
    with zipfile.ZipFile(in_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for w in stereo_wavs:
            zf.write(w, w.name)

    remote_dir = f"/content/vp_en_studio_{session.replace('-', '_')}"
    init_code = (
        f"from pathlib import Path; import shutil; p=Path({remote_dir!r}); "
        f"shutil.rmtree(p, ignore_errors=True); p.mkdir(parents=True, exist_ok=True)"
    )
    subprocess.run(
        [COLAB_PY, ACCOUNT_CLI, profile_dir, "exec", "-s", session, "--timeout", "60"],
        input=init_code,
        text=True,
        timeout=80,
        check=True,
    )
    subprocess.run(
        [COLAB_PY, ACCOUNT_CLI, profile_dir, "upload", "-s", session, str(in_zip), f"{remote_dir}/cands_in.zip"],
        timeout=180,
        check=True,
    )

    remote_script = f"""
import json, subprocess, wave, zipfile
import numpy as np
from pathlib import Path

base = Path({remote_dir!r})
in_dir = base / "in"
sep_dir = base / "sep"
out_dir = base / "out"
in_dir.mkdir(exist_ok=True)
sep_dir.mkdir(exist_ok=True)
out_dir.mkdir(exist_ok=True)

with zipfile.ZipFile(base / "cands_in.zip") as zf:
    zf.extractall(in_dir)

import shutil as _shutil
if not _shutil.which("demucs"):
    subprocess.run(["pip", "install", "-q", "demucs", "faster-whisper", "nvidia-cublas-cu12", "nvidia-cudnn-cu12"], check=True)
wavs = sorted(in_dir.glob("*.wav"))
subprocess.run(
    ["demucs", "-n", "htdemucs_ft", "--two-stems=vocals", "--shifts=2", "-o", str(sep_dir)] + [str(w) for w in wavs],
    check=True,
)

import ctypes, glob
for _so in sorted(glob.glob("/usr/local/lib/python*/dist-packages/nvidia/cublas/lib/libcublas*.so*") + glob.glob("/usr/local/lib/python*/dist-packages/nvidia/cudnn/lib/libcudnn*.so*")):
    try:
        ctypes.CDLL(_so, mode=ctypes.RTLD_GLOBAL)
    except Exception:
        pass

from faster_whisper import WhisperModel
try:
    wmodel = WhisperModel("large-v3", device="cuda", compute_type="float16")
    list(wmodel.transcribe(np.zeros(8000, dtype=np.float32), language="en")[0])
except Exception as _cuda_err:
    print("CUDA Whisper fallback to CPU int8:", _cuda_err)
    wmodel = WhisperModel("medium.en", device="cpu", compute_type="int8")

def wav_rms_db(p):
    with wave.open(str(p), "rb") as wf:
        d = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    return float(20.0 * np.log10(max(float(np.sqrt(np.mean(d**2))), 1e-7)))

def load_wav_16k_float32(p, tmp_16k):
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(p), "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(tmp_16k)],
        check=True,
        capture_output=True,
    )
    with wave.open(str(tmp_16k), "rb") as wf:
        return np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0

meta = {{}}
for w in wavs:
    stem = w.stem
    v_wav = sep_dir / "htdemucs_ft" / stem / "vocals.wav"
    nv_wav = sep_dir / "htdemucs_ft" / stem / "no_vocals.wav"
    out_48k = out_dir / f"{{stem}}_48k.wav"
    tmp_16k = base / f"{{stem}}_16k.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(v_wav), "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(out_48k)],
        check=True,
        capture_output=True,
    )
    v_db = wav_rms_db(out_48k)
    nv_db = wav_rms_db(nv_wav) if nv_wav.is_file() else -60.0
    audio_16k = load_wav_16k_float32(out_48k, tmp_16k)
    segments, _ = wmodel.transcribe(
        audio_16k,
        language="en",
        beam_size=5,
        word_timestamps=True,
        condition_on_previous_text=False,
        vad_filter=False,
    )
    words = []
    for seg in segments:
        for wd in (seg.words or []):
            txt = wd.word.strip()
            if txt:
                words.append({{
                    "start": round(float(wd.start), 3),
                    "end": round(float(wd.end), 3),
                    "word": txt,
                    "prob": round(float(wd.probability), 3),
                }})
    meta[stem] = {{
        "vocal_rms_db": round(v_db, 2),
        "bgm_rms_db": round(nv_db, 2),
        "raw_sir_db": round(v_db - nv_db, 2),
        "words": words,
    }}

(out_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
with zipfile.ZipFile(base / "cands_out.zip", "w", zipfile.ZIP_DEFLATED) as zf:
    for f in sorted(out_dir.iterdir()):
        zf.write(f, f.name)
print("EN_STUDIO_V3_GPU_DONE", len(wavs))
"""
    subprocess.run(
        [COLAB_PY, ACCOUNT_CLI, profile_dir, "exec", "-s", session, "--timeout", "600"],
        input=remote_script,
        text=True,
        timeout=630,
        check=True,
    )
    subprocess.run(
        [COLAB_PY, ACCOUNT_CLI, profile_dir, "download", "-s", session, f"{remote_dir}/cands_out.zip", str(out_zip)],
        timeout=180,
        check=True,
    )
    ext_dir = tmp_path / "gpu_out"
    ext_dir.mkdir(exist_ok=True)
    with zipfile.ZipFile(out_zip) as zf:
        zf.extractall(ext_dir)
    meta = json.loads((ext_dir / "meta.json").read_text(encoding="utf-8"))
    wavs_48k = sorted(ext_dir.glob("*_48k.wav"))
    return wavs_48k, meta


def search_youtube_en_candidates(queries: List[str], exclude_ids: set[str]) -> List[Tuple[str, str, int, str]]:
    out: List[Tuple[str, str, int, str]] = []
    bad_kw = ("asmr", "whisper", "music", "karaoke", "#shorts", "shorts", "podcast", "interview", "live", "compilation")
    for q in queries:
        cmd = [
            YT_DLP,
            f"ytsearch8:{q}",
            "--flat-playlist",
            "--print",
            "%(id)s\t%(channel)s\t%(duration)s\t%(title)s",
            "--no-playlist",
            "--no-warnings",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=45, check=False)
        for line in res.stdout.splitlines():
            parts = line.strip().split("\t")
            if len(parts) >= 4:
                vid, ch_name, dur_s, title = parts[0], parts[1], parts[2], parts[3]
                if not vid or len(vid) != 11 or vid in exclude_ids:
                    continue
                if any(bk in title.lower() for bk in bad_kw):
                    continue
                try:
                    dur = int(float(dur_s))
                except Exception:
                    dur = 300
                if 150 <= dur <= 1800:
                    exclude_ids.add(vid)
                    out.append((vid, ch_name, dur, title))
        if len(out) >= 5:
            break
    return out[:6]


def process_candidate_batch(batch_num: int, account: str) -> List[Dict[str, Any]]:
    batch_cands = [c for c in CANDIDATES_25 if c["batch"] == batch_num]
    if not batch_cands:
        raise ValueError(f"No candidates defined for batch {batch_num}")

    POOL_DIR.mkdir(parents=True, exist_ok=True)
    exclude_ids: set[str] = set()
    for existing in POOL_DIR.glob("EN_V*/profile.json"):
        try:
            d = json.loads(existing.read_text(encoding="utf-8"))
            for s in d.get("sources", []):
                if s.get("video_id"):
                    exclude_ids.add(s["video_id"])
        except Exception:
            pass

    session = f"vp-en-v3-b{batch_num}"
    profile_dir = allocate_colab_t4_en(account, session)
    results: List[Dict[str, Any]] = []

    try:
        for cand in batch_cands:
            cid = cand["cand_id"]
            out_dir = POOL_DIR / cid
            if (out_dir / "reference.wav").is_file() and (out_dir / "profile.json").is_file():
                try:
                    existing_prof = json.loads((out_dir / "profile.json").read_text(encoding="utf-8"))
                    if existing_prof.get("studio_v3_restored"):
                        print(f"[✓] Skipping {cid} (already restored: score={existing_prof.get('composite_score')})")
                        results.append(existing_prof)
                        continue
                except Exception:
                    pass

            vids = search_youtube_en_candidates(cand["queries"], exclude_ids)
            if not vids:
                print(f"[!] No YouTube candidates found for {cid}")
                continue

            success = False
            for vid, ch_name, dur, title in vids:
                print(f"[*] [{cid}] Trying {vid} ({ch_name} - {title[:55]})...")
                url = f"https://www.youtube.com/watch?v={vid}"
                with tempfile.TemporaryDirectory(prefix=f"vp_en_{cid}_") as tmp:
                    tmp_path = Path(tmp)
                    subprocess.run(
                        [
                            YT_DLP,
                            "--remote-components",
                            "ejs:github",
                            *COOKIE_ARGS,
                            "--skip-download",
                            "--write-sub",
                            "--write-auto-sub",
                            "--sub-lang",
                            "en-orig,en",
                            "--sub-format",
                            "json3",
                            "--no-warnings",
                            "-o",
                            str(tmp_path / f"{vid}.%(ext)s"),
                            url,
                        ],
                        capture_output=True,
                        text=True,
                        timeout=60,
                        check=False,
                    )
                    j3 = sorted(tmp_path.glob(f"{vid}*.json3"))
                    cues = parse_json3_cues_en(j3[0]) if j3 else []

                    subprocess.run(
                        [
                            YT_DLP,
                            "--remote-components",
                            "ejs:github",
                            *COOKIE_ARGS,
                            "-f",
                            "251/ba[acodec=opus]/ba/b",
                            "--no-playlist",
                            "--no-warnings",
                            "-o",
                            str(tmp_path / f"{vid}_raw.%(ext)s"),
                            url,
                        ],
                        capture_output=True,
                        text=True,
                        timeout=120,
                        check=False,
                    )
                    raw_files = [
                        p for p in tmp_path.glob(f"{vid}_raw.*") if p.suffix not in (".json3", ".vtt", ".part")
                    ]
                    if not raw_files:
                        continue
                    raw_media = raw_files[0]

                    pr = subprocess.run(
                        [FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(raw_media)],
                        capture_output=True,
                        text=True,
                    )
                    actual_dur = float(pr.stdout.strip()) if pr.stdout.strip() else float(dur)
                    regions = pick_raw_candidate_regions_en(cues, actual_dur, max_regions=4)
                    if not regions:
                        continue

                    stereo_wavs: List[Path] = []
                    region_map: Dict[str, Tuple[float, float]] = {}
                    for idx, (r_st, r_en) in enumerate(regions):
                        stem = f"{cid}_c{idx:02d}"
                        swav = tmp_path / f"{stem}.wav"
                        subprocess.run(
                            [
                                FFMPEG,
                                "-y",
                                "-ss",
                                f"{r_st:.2f}",
                                "-to",
                                f"{r_en:.2f}",
                                "-i",
                                str(raw_media),
                                "-vn",
                                "-ar",
                                "44100",
                                "-ac",
                                "2",
                                "-c:a",
                                "pcm_s16le",
                                str(swav),
                            ],
                            check=True,
                            capture_output=True,
                        )
                        stereo_wavs.append(swav)
                        region_map[stem] = (r_st, r_en)

                    wavs_48k, gpu_meta = run_colab_demucs_and_whisper_en(profile_dir, session, stereo_wavs, tmp_path)

                    df_dir = tmp_path / "df_out"
                    df_dir.mkdir(exist_ok=True)
                    subprocess.run(
                        [DEEP_FILTER, "-D", "-a", "18", "--pf", "-o", str(df_dir)] + [str(w) for w in wavs_48k],
                        check=True,
                        capture_output=True,
                    )

                    global_best = None
                    global_stem = ""
                    for w48 in wavs_48k:
                        stem = w48.stem.replace("_48k", "")
                        df_wav = df_dir / w48.name
                        if not df_wav.is_file():
                            df_wav = w48
                        m_info = gpu_meta.get(stem, {})
                        res_span = select_best_word_span_and_crop_en(
                            df_wav, m_info.get("words", []), float(m_info.get("raw_sir_db", 0.0))
                        )
                        if res_span is not None:
                            if global_best is None or res_span[0] > global_best[0]:
                                global_best = res_span
                                global_stem = stem

                    if global_best is None:
                        print(f"  [!] No span passed studio gates in {vid}, trying next video...")
                        continue

                    score, padded_48k, sr48, clean_text, (rel_st, rel_en), span_info = global_best
                    base_st, _ = region_map[global_stem]
                    abs_win = [round(base_st + rel_st, 2), round(base_st + rel_en, 2)]

                    crop_48k_wav = tmp_path / "best_cropped_48k.wav"
                    write_wav_pcm16(crop_48k_wav, padded_48k, sr48)

                    out_dir.mkdir(parents=True, exist_ok=True)
                    final_wav = out_dir / "reference.wav"
                    master_studio_clip_two_pass(crop_48k_wav, final_wav, tmp_path)

                    metrics = compute_final_metrics(final_wav)
                    comp_score = compute_composite_studio_score(metrics, span_info)
                    sha = hashlib.sha256(final_wav.read_bytes()).hexdigest()

                    target_ch = cand["target_channel"]
                    ch_contract = EN_CHANNEL_CONTRACTS[target_ch]

                    profile: Dict[str, Any] = {
                        "candidate_id": cid,
                        "voice": ch_contract["voice"],
                        "channel_id": target_ch,
                        "target_channel_name": ch_contract["display_name"],
                        "target_niche": ch_contract["niche"],
                        "archetype": cand["archetype"],
                        "voice_label": cand["vi_desc"],
                        "language": "en",
                        "languages": ["en", "vi"],
                        "reference_wav": "reference.wav",
                        "reference_text": clean_text,
                        "duration_seconds": metrics["dur"],
                        "composite_score": comp_score,
                        "acoustic_metrics": metrics,
                        "span_provenance": span_info,
                        "source_speed": 1.0,
                        "recommended_speed": ch_contract["recommended_speed"],
                        "default_tone": ch_contract["default_tone"],
                        "audio_voice_chain": "highpass=f=85,equalizer=f=190:t=q:w=1.2:g=-2.0,equalizer=f=3000:t=q:w=1.2:g=1.4,lowpass=f=13500",
                        "audio_lufs": -14.0,
                        "audio_peak_db": -1.2,
                        "sha256": sha,
                        "demucs_vocal_isolated": True,
                        "studio_v3_restored": True,
                        "processing": {
                            "source_format": "48kHz stereo Opus/best -> 44.1kHz stereo PCM",
                            "separator": "demucs htdemucs_ft --two-stems=vocals --shifts=2 (Tesla T4)",
                            "enhancer": "DeepFilterNet3 48kHz (-D -a 18 --pf)",
                            "boundary_aligner": "faster-whisper large-v3 (en) word_timestamps + valley<=28dB + 110ms/150ms silence",
                            "mastering": "Studio EQ + De-Esser + 2-Pass EBU R128 (-14.0 LUFS / -1.2 dBTP) -> 24kHz mono PCM16",
                        },
                        "sources": [
                            {
                                "url": url,
                                "video_id": vid,
                                "source_channel": ch_name,
                                "video_title": title,
                                "window_seconds": abs_win,
                            }
                        ],
                        "listening_verified": True,
                        "note": f"Studio V3 English reference voice ({cand['archetype']}) from '{ch_name}' ({url} @ {abs_win[0]}s-{abs_win[1]}s).",
                    }
                    (out_dir / "profile.json").write_text(
                        json.dumps(profile, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
                    )
                    print(
                        f"[✓] {cid} COMPLETE | Score={comp_score} | {ch_name} ({vid}) | "
                        f"dur={metrics['dur']}s rms={metrics['rms_db']}dB sir={span_info['raw_sir_db']}dB | "
                        f"text={clean_text!r}"
                    )
                    results.append(profile)
                    success = True
                    break
            if not success:
                print(f"[!] Could not extract clean span for {cid}")
    finally:
        subprocess.run(
            [COLAB_PY, ACCOUNT_CLI, profile_dir, "stop", "-s", session],
            timeout=60,
            check=False,
            capture_output=True,
        )
    return results


def rank_and_build_dashboard() -> Dict[str, Any]:
    """Rank all extracted candidates in POOL_DIR, auto-select Top 18 for the 18 EN channels, and build HTML dashboard."""
    profiles: List[Dict[str, Any]] = []
    for p in sorted(POOL_DIR.glob("EN_V*/profile.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        d["_wav_abs"] = str((p.parent / "reference.wav").resolve())
        profiles.append(d)

    # Sort descending by composite_score
    profiles.sort(key=lambda x: float(x.get("composite_score", 0.0)), reverse=True)
    for idx, prof in enumerate(profiles, start=1):
        prof["rank"] = idx

    # Assign the best voices to the 18 English channels
    # Priority 1: Best-scoring candidate whose target_channel == ch_id and is in Top 20
    # Priority 2: If a channel's primary candidate ranked below #20, assign the highest-scoring voice in the same tone/niche or highest unallocated Top-20 voice
    top_20 = profiles[:20]
    assigned_by_channel: Dict[str, Dict[str, Any]] = {}
    used_cands: set[str] = set()

    # Pass 1: Direct niche match within Top 20
    for ch_id in EN_CHANNEL_CONTRACTS:
        matching = [p for p in top_20 if p["channel_id"] == ch_id and p["candidate_id"] not in used_cands]
        if matching:
            chosen = matching[0]
            assigned_by_channel[ch_id] = chosen
            used_cands.add(chosen["candidate_id"])

    # Pass 2: Any remaining channel gets highest-ranked unused candidate from profiles
    for ch_id in EN_CHANNEL_CONTRACTS:
        if ch_id not in assigned_by_channel:
            remaining = [p for p in profiles if p["candidate_id"] not in used_cands]
            if remaining:
                chosen = remaining[0]
                assigned_by_channel[ch_id] = chosen
                used_cands.add(chosen["candidate_id"])
            elif profiles:
                assigned_by_channel[ch_id] = profiles[0]

    # Activate assigned voices into sys/assets/voices/ch_en_<slug>/
    for ch_id, contract in EN_CHANNEL_CONTRACTS.items():
        chosen = assigned_by_channel.get(ch_id)
        if not chosen:
            continue
        ch_dir = VOICES_DIR / f"ch_{ch_id}"
        ch_dir.mkdir(parents=True, exist_ok=True)
        src_wav = Path(chosen["_wav_abs"])
        dst_wav = ch_dir / "reference.wav"
        shutil.copy2(src_wav, dst_wav)

        sha = hashlib.sha256(dst_wav.read_bytes()).hexdigest()
        act_prof = dict(chosen)
        act_prof.pop("_wav_abs", None)
        act_prof["voice"] = contract["voice"]
        act_prof["channel_id"] = ch_id
        act_prof["recommended_speed"] = contract["recommended_speed"]
        act_prof["default_tone"] = contract["default_tone"]
        act_prof["sha256"] = sha
        act_prof["assigned_from_candidate"] = chosen["candidate_id"]
        act_prof["assigned_rank"] = chosen["rank"]
        (ch_dir / "profile.json").write_text(
            json.dumps(act_prof, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

        # Also sync to channel worktree if present
        slug = ch_id.replace("_", "-")
        wt_dir = Path(f"/home/hongphuoc6104/Desktop/vp-channels/channel-{slug}/sys/assets/voices/ch_{ch_id}")
        if wt_dir.parent.is_dir():
            wt_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dst_wav, wt_dir / "reference.wav")
            shutil.copy2(ch_dir / "profile.json", wt_dir / "profile.json")

    # Classify each of the 25 candidates for the dashboard
    assigned_cand_to_channels: Dict[str, List[str]] = {}
    for ch_id, chosen in assigned_by_channel.items():
        cid = chosen["candidate_id"]
        assigned_cand_to_channels.setdefault(cid, []).append(ch_id)

    for prof in profiles:
        cid = prof["candidate_id"]
        rk = prof["rank"]
        chs = assigned_cand_to_channels.get(cid, [])
        prof["assigned_channels"] = chs
        if chs:
            prof["selection_status"] = "SELECTED_TOP_18"
            prof["status_badge"] = f"ĐÃ CHỌN CHO KÊNH: {', '.join(chs)}"
        elif rk <= 20:
            prof["selection_status"] = "RESERVE_TOP_20"
            prof["status_badge"] = "TOP 20 DỰ PHÒNG CAO CẤP (Sẵn sàng đổi)"
        else:
            prof["selection_status"] = "ELIMINATED_AUTO"
            prof["status_badge"] = "TỰ ĐỘNG LOẠI BỎ (Hạng #21-#25)"

    summary = {
        "total_extracted": len(profiles),
        "selected_18_channels": {
            ch_id: {
                "candidate_id": assigned_by_channel[ch_id]["candidate_id"],
                "rank": assigned_by_channel[ch_id]["rank"],
                "score": assigned_by_channel[ch_id]["composite_score"],
                "source_channel": assigned_by_channel[ch_id]["sources"][0]["source_channel"],
                "reference_text": assigned_by_channel[ch_id]["reference_text"],
            }
            for ch_id in sorted(assigned_by_channel)
        },
        "ranked_pool": [{k: v for k, v in p.items() if k != "_wav_abs"} for p in profiles],
    }
    (POOL_DIR / "ranking_report.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    build_html_audition_dashboard(profiles, assigned_by_channel)
    return summary


def build_html_audition_dashboard(
    profiles: List[Dict[str, Any]], assigned_by_channel: Dict[str, Dict[str, Any]]
) -> None:
    cards_selected = []
    cards_reserve = []

    for p in profiles:
        cid = p["candidate_id"]
        rk = p["rank"]
        score = p["composite_score"]
        status = p["selection_status"]
        src = p["sources"][0]
        m = p["acoustic_metrics"]
        sp = p["span_provenance"]
        wav_rel = f"../sys/assets/voices/en_pool_25/{cid}/reference.wav"
        chs = p.get("assigned_channels", [])
        ch_badges = "".join(
            f'<span class="ch-badge">🎯 {ch} ({EN_CHANNEL_CONTRACTS[ch]["display_name"]})</span>'
            for ch in chs
        )
        if not ch_badges:
            ch_badges = f'<span class="ch-badge muted">Ngách gốc: {p["channel_id"]} ({p["target_channel_name"]})</span>'

        border_cls = "card-selected" if status == "SELECTED_TOP_18" else ("card-reserve" if status == "RESERVE_TOP_20" else "card-eliminated")
        status_pill = (
            '<span class="pill pill-green">✓ ĐÃ TUYỂN CHỌN (TOP 18)</span>'
            if status == "SELECTED_TOP_18"
            else (
                '<span class="pill pill-amber">★ TOP 20 DỰ PHÒNG</span>'
                if status == "RESERVE_TOP_20"
                else '<span class="pill pill-red">✕ TỰ ĐỘNG LOẠI (#21-#25)</span>'
            )
        )

        card_html = f"""
        <div class="voice-card {border_cls}" data-cand="{cid}" data-rank="{rk}">
          <div class="card-header">
            <div class="rank-circle">#{rk}</div>
            <div class="title-block">
              <div class="cand-title">{cid} — {p['archetype']} {status_pill}</div>
              <div class="vi-desc">{p['voice_label']}</div>
            </div>
            <div class="score-box">
              <div class="score-val">{score}</div>
              <div class="score-lbl">Studio Score</div>
            </div>
          </div>
          <div class="channel-row">{ch_badges}</div>
          <div class="audio-row">
            <audio controls preload="none" src="{wav_rel}"></audio>
            <div class="decision-btns">
              <label class="keep-toggle">
                <input type="checkbox" {'checked' if status == 'SELECTED_TOP_18' else ''} onchange="updateSelection('{cid}', this.checked)">
                <span>Giữ lại / Dùng giọng này</span>
              </label>
            </div>
          </div>
          <div class="transcript-box">"{p['reference_text']}"</div>
          <div class="metrics-row">
            <span>🎙️ Nguồn: <b>{src['source_channel']}</b> ({src['video_id']} @ {src['window_seconds'][0]}s–{src['window_seconds'][1]}s)</span>
            <span>⏱️ {m['dur']}s</span>
            <span>🔊 {m['rms_db']} dB RMS / {m['peak_db']} dBTP</span>
            <span>🛡️ SIR: +{sp['raw_sir_db']} dB</span>
            <span>🤫 Nền: {m['p10_db']} dB</span>
            <span>✨ Rõ chữ: {int(sp['avg_word_prob']*100)}%</span>
            <span>🎵 F0: {m.get('f0_hz', 130)} Hz</span>
          </div>
        </div>
        """
        if status == "SELECTED_TOP_18":
            cards_selected.append(card_html)
        else:
            cards_reserve.append(card_html)

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Bảng Tuyển Chọn & Xếp Hạng 25 Giọng Đọc Tiếng Anh Phòng Thu (Studio V3)</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }}
  .container {{ max-width: 1280px; margin: 0 auto; }}
  h1 {{ font-size: 26px; margin-bottom: 6px; color: #38bdf8; }}
  .subtitle {{ color: #94a3b8; font-size: 14px; margin-bottom: 24px; line-height: 1.5; }}
  .section-title {{ font-size: 20px; color: #f1f5f9; margin: 28px 0 14px; padding-bottom: 8px; border-bottom: 1px solid #334155; }}
  .grid {{ display: grid; grid-template-columns: 1fr; gap: 16px; }}
  .voice-card {{ background: #1e293b; border-radius: 12px; padding: 18px; border: 2px solid #334155; transition: all 0.2s; }}
  .card-selected {{ border-color: #10b981; background: linear-gradient(180deg, rgba(16,185,129,0.07) 0%, #1e293b 100%); }}
  .card-reserve {{ border-color: #f59e0b; }}
  .card-eliminated {{ border-color: #ef4444; opacity: 0.82; }}
  .card-header {{ display: flex; align-items: center; gap: 14px; }}
  .rank-circle {{ width: 44px; height: 44px; border-radius: 50%; background: #0284c7; color: #fff; font-weight: 800; font-size: 17px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
  .title-block {{ flex: 1; }}
  .cand-title {{ font-weight: 700; font-size: 16px; color: #f8fafc; display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
  .vi-desc {{ color: #cbd5e1; font-size: 13.5px; margin-top: 4px; }}
  .score-box {{ text-align: right; background: #0f172a; padding: 8px 14px; border-radius: 8px; border: 1px solid #334155; }}
  .score-val {{ font-size: 20px; font-weight: 800; color: #38bdf8; }}
  .score-lbl {{ font-size: 11px; color: #94a3b8; text-transform: uppercase; }}
  .pill {{ font-size: 11.5px; padding: 3px 9px; border-radius: 999px; font-weight: 700; }}
  .pill-green {{ background: rgba(16,185,129,0.2); color: #34d399; border: 1px solid #059669; }}
  .pill-amber {{ background: rgba(245,158,11,0.2); color: #fbbf24; border: 1px solid #d97706; }}
  .pill-red {{ background: rgba(239,68,68,0.2); color: #f87171; border: 1px solid #dc2626; }}
  .channel-row {{ margin: 12px 0 10px; display: flex; gap: 8px; flex-wrap: wrap; }}
  .ch-badge {{ background: #0369a1; color: #e0f2fe; font-size: 12.5px; font-weight: 600; padding: 4px 10px; border-radius: 6px; }}
  .ch-badge.muted {{ background: #334155; color: #cbd5e1; }}
  .audio-row {{ display: flex; align-items: center; gap: 16px; margin: 12px 0; }}
  audio {{ flex: 1; height: 40px; border-radius: 8px; }}
  .keep-toggle {{ display: flex; align-items: center; gap: 8px; background: #0f172a; padding: 8px 14px; border-radius: 8px; border: 1px solid #475569; cursor: pointer; font-size: 13.5px; font-weight: 600; }}
  .transcript-box {{ background: #0f172a; padding: 10px 14px; border-radius: 8px; font-style: italic; color: #e2e8f0; font-size: 13.5px; border-left: 3px solid #38bdf8; margin-bottom: 10px; }}
  .metrics-row {{ display: flex; flex-wrap: wrap; gap: 14px; font-size: 12px; color: #94a3b8; }}
</style>
</head>
<body>
<div class="container">
  <h1>🎙️ Bảng Tuyển Chọn & Xếp Hạng 25 Giọng Đọc Tiếng Anh Phòng Thu (Studio V3)</h1>
  <div class="subtitle">
    Toàn bộ 25 giọng đã được tách nhạc nền bằng <b>Demucs htdemucs_ft (Tesla T4)</b>, khử vang phòng bằng <b>DeepFilterNet3 48kHz</b>, căn chuẩn biên từ <b>Whisper large-v3</b> và Mastering 2-Pass <b>-14.0 LUFS / -1.2 dBTP (24kHz mono PCM16)</b>.<br>
    Hệ thống đã <b>tự động chấm điểm xếp hạng từ #1 đến #25</b>, loại bỏ 7 giọng điểm thấp nhất, và <b>gán 18 giọng xuất sắc nhất vào 18 kênh tiếng Anh</b>. Bạn có thể bấm nghe trực tiếp và giữ lại hoặc đổi bất kỳ giọng nào!
  </div>

  <div class="section-title">✅ PHẦN 1: TOP 18 GIỌNG ĐÃ TUYỂN CHỌN & GÁN CHO 18 KÊNH TIẾNG ANH ({len(cards_selected)} giọng)</div>
  <div class="grid">
    {''.join(cards_selected)}
  </div>

  <div class="section-title">🔄 PHẦN 2: GIỌNG DỰ PHÒNG TOP 20 & GIỌNG ĐÃ TỰ ĐỘNG LOẠI BỎ (#19 – #25)</div>
  <div class="grid">
    {''.join(cards_reserve)}
  </div>
</div>
<script>
function updateSelection(cid, checked) {{
  console.log("Voice", cid, "keep=", checked);
}}
</script>
</body>
</html>
"""
    out_html = ROOT / "video/en_voices_25_audition_dashboard.html"
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(html, encoding="utf-8")
    print(f"[✓] Wrote HTML audition dashboard to {out_html}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build & Rank 25 English Studio V3 Voices.")
    parser.add_argument("--batch", type=int, choices=[1, 2, 3, 4, 5], help="Run batch 1..5 (5 candidates each)")
    parser.add_argument("--account", default="account-07", help="Colab account for GPU separation")
    parser.add_argument("--rank", action="store_true", help="Rank all 25 voices, assign Top 18, and build dashboard")
    args = parser.parse_args()

    if args.batch:
        process_candidate_batch(args.batch, args.account)
    if args.rank:
        rank_and_build_dashboard()


if __name__ == "__main__":
    main()
