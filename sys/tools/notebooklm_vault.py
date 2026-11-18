#!/usr/bin/env python3
"""Hybrid Dual-Mode NotebookLM 3-Vault Engine for Video Pilot (38 VN/EN Channels).

Provides:
- Canonical schemas & validation for `FactVault` and `PatternBrief`
- Bilingual NotebookLM Markdown -> `fact_vault.json` parser with `"report-only"` quarantine
- Dynamic Master Prompt renderer tailored across all 38 channels / 5 niche archetypes
- Exports to `vp-research-architect` (`brief.sources[]`), YouTube `"Nguồn tham khảo"` blocks,
  and `chanh_niem_ke` V5.0 `episode_manifest.json` seed metadata
- `NotebookLMBridge` supporting optional `nlm`/`notebooklm-py` CLI, Chrome CDP pool plan
  (obeying `.agents/rules/gpu-headless-chrome.md`), and zero-dependency Web UI import/fallback.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from fx_warehouse.archetypes import (  # noqa: E402
    ARCHETYPE_PROFILES,
    CHANNEL_BESPOKE_RULES,
    get_channel_archetype,
)

ARCHETYPE_SOURCE_PRIORITIES: dict[str, dict[str, str]] = {
    "archetype_1_forensic_noir": {
        "vi": "Hồ sơ điều tra chính thức (NTSB, AAIB, cục hàng hải), báo cáo điều tra tai nạn, nghiên cứu tâm lý xã hội học peer-reviewed (APA, HBR) và báo cáo nhân sự/thị trường lao động",
        "en": "Official inquiry dockets (NTSB, AAIB, maritime safety boards), peer-reviewed behavioral psychology studies (APA, HBR), and labor/industry reports",
    },
    "archetype_2_geopolitics_history": {
        "vi": "Dữ liệu USGS, EIA, UN Comtrade, IMF, World Bank, báo cáo thảm họa chính thức (IAEA, CSB, WHO), chính sử (Đại Việt Sử Ký Toàn Thư) và địa lý quân sự học thuật",
        "en": "USGS, EIA, UN Comtrade, IMF, World Bank datasets, official disaster reports (IAEA, CSB, WHO), and peer-reviewed historical/geopolitical monographs",
    },
    "archetype_3_science_xray": {
        "vi": "NIH, PubMed, WHO, AHA, CDC, Nature, NASA, ESA, Bộ Y Tế Việt Nam, sách giáo khoa hóa học thực phẩm & vật lý thực nghiệm",
        "en": "NIH, PubMed, WHO, AHA, CDC, Nature, NASA, ESA, and peer-reviewed physics/biology/food-chemistry journals",
    },
    "archetype_4_doodle_explainer": {
        "vi": "Văn bản luật Việt Nam hiện hành (Bộ luật Lao động 2019, Bộ luật Dân sự 2015, Luật Nhà ở), biểu thuế/lãi suất ngân hàng chính thức, tài liệu khoa học hành vi (APA, Gottman), tài liệu kỹ thuật AI chính thức",
        "en": "Statutory codes & consumer protection filings (FTC, CFPB), peer-reviewed cognitive/relationship science (APA, Gottman), financial filings, and official technical docs",
    },
    "archetype_5_mindful_healing": {
        "vi": "Bản dịch kinh điển (Đạo Đức Kinh, Trang Tử, Marcus Aurelius Meditations, Seneca), bình chú lịch sử-phê bình uy tín và nghiên cứu tâm lý học chánh niệm",
        "en": "Primary classical translations (Tao Te Ching, Zhuangzi, Marcus Aurelius Meditations, Seneca), historical-critical commentaries, and mindfulness psychology papers",
    },
}

_CHANNEL_SPECIFIC_SOURCES: dict[str, str] = {
    "co_the_ke": "NIH, PubMed, WHO, AHA, CDC, Nature, Harvard Health, Matthew Walker, Bộ Y Tế Việt Nam",
    "luat_doi_thuong": "Bộ luật Lao động 2019, Bộ luật Dân sự 2015, Luật Nhà ở 2023, Nghị định hướng dẫn chính phủ, Thư Viện Pháp Luật",
    "ho_so_ky_la": "NTSB, AAIB, BEA, ICAO, báo cáo điều tra hàng hải/y khoa pháp y và hồ sơ lưu trữ báo chí điều tra",
    "chanh_niem_ke": "IAEA, US CSB, WHO, USGS, báo cáo kỹ thuật sụp đổ hạ tầng & bản đồ tọa độ địa lý chính xác",
    "su_ke_lai": "Đại Việt Sử Ký Toàn Thư, Khâm Định Việt Sử Thông Giám Cương Mục, chính sử đối chiếu và nghiên cứu địa hình quân sự",
    "ban_do_quyen_luc": "EIA, USGS, UN Comtrade, CSIS, Lloyd's List, dữ liệu vận tải biển & bán dẫn",
    "tui_tien": "Báo cáo thường niên doanh nghiệp, Ngân hàng Nhà nước, Tổng cục Thuế, Luật Thuế TNCN, nghiên cứu kinh tế hành vi",
}

_METRIC_RE = re.compile(
    r"(?<!\w)(?:\d{1,4}(?:[.,]\d+)?\s*(?:%|phần trăm|percent|kg|g|mg|mcg|km|m|mét|mm|cm|lít|ml|"
    r"giờ|phút|giây|ngày|tháng|năm|tuổi|nghìn|triệu|tỷ|tỉ|người|triệu đồng|nghìn đồng|đồng|usd|\$|"
    r"độ c|°c|psi|feet|ft|hz|mw|gw|rem|sv|msv|bar|atm|rpm|cal|kcal|tonnes?|tons?)\b|\b(?:1[0-9]{3}|20[0-9]{2})\b)",
    re.IGNORECASE,
)

_COORDINATE_RE = re.compile(
    r"(-?\d{1,3}\.\d+)\s*,\s*(-?\d{1,3}\.\d+)"
)


def _infer_channel_meta(channel_id: str) -> dict[str, Any]:
    """Resolve language, display name, niche, and archetype safely without crashing on unknown IDs."""
    arch_id = get_channel_archetype(channel_id)
    arch = ARCHETYPE_PROFILES.get(arch_id, ARCHETYPE_PROFILES["archetype_1_forensic_noir"])
    lang = "en" if channel_id.startswith("en_") else "vi"
    name = channel_id
    niche = CHANNEL_BESPOKE_RULES.get(channel_id, {}).get("focus") or arch["label"]
    try:
        from channels.registry import get_channel  # local import keeps tool lightweight
        ch = get_channel(channel_id)
        if ch:
            name = ch.name
            niche = ch.niche or niche
            lang = getattr(ch, "language", lang) or lang
    except Exception:
        pass
    return {
        "channel_id": channel_id,
        "display_name": name,
        "niche": niche,
        "language": lang,
        "archetype_id": arch_id,
        "archetype_label": arch["label"],
    }


def _clean_line(line: str) -> str:
    return re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", line).strip()


def _extract_source_bracket(text: str) -> tuple[str, str]:
    """Extract trailing `[Source Name]` citation if present."""
    m = re.search(r"\[([^\[\]]{2,90})\]\s*\.?$", text.strip())
    if m:
        src = m.group(1).strip()
        cleaned = (text[: m.start()].rstrip(" .;-:") + ".").strip()
        if cleaned == ".":
            cleaned = text.strip()
        return cleaned, src
    return text.strip(), ""


def _extract_exact_number(text: str) -> str:
    m = _METRIC_RE.search(text)
    if m:
        return m.group(0).strip()
    m2 = re.search(r"\b\d+(?:[.,]\d+)?\b", text)
    return m2.group(0) if m2 else ""


def parse_notebooklm_markdown_to_fact_vault(
    md_text: str,
    topic: str,
    channel_id: str,
    format_profile: str = "short_9x16",
    audience: str = "",
    source_mode: str = "web_import",
) -> dict[str, Any]:
    """Parse NotebookLM Markdown Research Notes into canonical `fact_vault.json`."""
    meta = _infer_channel_meta(channel_id)
    lang = meta["language"]
    if not audience:
        audience = (
            "Khán giả Việt Nam tò mò từ 22-44 tuổi thích giải thích cơ chế dễ hiểu"
            if lang == "vi"
            else "Curious English-speaking adults seeking clear source-backed explanations"
        )

    sections: dict[str, list[str]] = {}
    current_sec = "general"
    for raw_line in (md_text or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        sec_m = re.match(r"^(?:#{1,4}\s*)?(?:Section\s*)?(\d+)[.:)]\s*(.+)$", line, re.IGNORECASE)
        if not sec_m and re.match(r"^#{1,4}\s+[A-Za-zÀ-ỹ]", line):
            heading = re.sub(r"^#{1,4}\s+", "", line).strip().lower()
            current_sec = heading
            sections.setdefault(current_sec, [])
            continue
        if sec_m:
            num = sec_m.group(1)
            heading = sec_m.group(2).strip().lower()
            current_sec = f"{num}:{heading}"
            sections.setdefault(current_sec, [])
            continue
        sections.setdefault(current_sec, []).append(line)

    def _find_section_lines(*keywords: str, default_prefix: str | None = None) -> list[str]:
        out: list[str] = []
        for k, lines in sections.items():
            kl = k.lower()
            if (default_prefix and kl.startswith(default_prefix)) or any(kw in kl for kw in keywords):
                out.extend(lines)
        return out

    verified_facts: list[dict[str, Any]] = []
    report_only_claims: list[dict[str, Any]] = []

    fact_lines = _find_section_lines("key fact", "sự kiện", "dữ kiện", default_prefix="1:")
    if not fact_lines:
        fact_lines = sections.get("general", [])

    for idx, raw in enumerate(fact_lines, start=1):
        cleaned = _clean_line(raw)
        if not cleaned:
            continue
        is_report_only = bool(re.search(r"\breport[- ]only\b|\bchỉ có trong báo cáo\b", cleaned, re.IGNORECASE))
        claim_body, src = _extract_source_bracket(re.sub(r"\(?\breport[- ]only\b\)?", "", cleaned, flags=re.IGNORECASE).strip())
        exact_num = _extract_exact_number(claim_body)
        entry = {
            "id": f"F{idx:02d}",
            "claim_vi": claim_body if lang == "vi" else "",
            "claim_en": claim_body if lang == "en" else "",
            "claim_text": claim_body,
            "exact_number": exact_num,
            "source_name": src or ("report-only" if is_report_only else "NotebookLM Imported Source"),
            "status": "report-only" if is_report_only else "verified",
            "user_approved": False,
        }
        if is_report_only:
            report_only_claims.append(entry)
        else:
            verified_facts.append(entry)

    hook_lines = _find_section_lines("surprising", "nghịch lý", "gây sốc", "hook", default_prefix="2:")
    mech_lines = _find_section_lines("how it works", "mechanism", "cơ chế", default_prefix="3:")
    bridge_lines = _find_section_lines("analogy", "analogies", "micro-bridge", "quy đổi", "ví von", "đời thường", default_prefix="4:")
    visual_lines = _find_section_lines("what it looks like", "visual", "hình ảnh", "bối cảnh", default_prefix="5:")
    miscon_lines = _find_section_lines("misconception", "hiểu nhầm", "hiểu lầm", default_prefix="6:")
    glossary_lines = _find_section_lines("spoken number", "pronunciation", "glossary", "phát âm", "phiên âm", default_prefix="7:")
    conflict_lines = _find_section_lines("conflict", "gap", "report-only", "mâu thuẫn", "thiếu hụt", default_prefix="8:")
    gis_lines = _find_section_lines("coordinate", "tọa độ", "gis", "chronological", default_prefix="9:")

    for raw in conflict_lines:
        cleaned = _clean_line(raw)
        if re.search(r"\breport[- ]only\b|\bchỉ có trong báo cáo\b", cleaned, re.IGNORECASE):
            claim_body, src = _extract_source_bracket(re.sub(r"\(?\breport[- ]only\b\)?", "", cleaned, flags=re.IGNORECASE).strip())
            report_only_claims.append({
                "id": f"RO{len(report_only_claims) + 1:02d}",
                "claim_vi": claim_body if lang == "vi" else "",
                "claim_en": claim_body if lang == "en" else "",
                "claim_text": claim_body,
                "exact_number": _extract_exact_number(claim_body),
                "source_name": src or "report-only",
                "status": "report-only",
                "user_approved": False,
            })

    analogies: list[str] = []
    vietnam_micro_bridges: list[str] = []
    for raw in bridge_lines:
        c = _clean_line(raw)
        if not c:
            continue
        if re.search(r"việt nam|hà nội|sài gòn|tp\.?hcm|vnđ|nghìn đồng|bát phở|xe máy|căn hộ", c, re.IGNORECASE):
            vietnam_micro_bridges.append(c)
        else:
            analogies.append(c)
    if not vietnam_micro_bridges and analogies and lang == "vi":
        vietnam_micro_bridges = analogies[:1]

    pronunciation_glossary: dict[str, str] = {}
    spoken_numbers_vi: list[str] = []
    for raw in glossary_lines:
        c = _clean_line(raw)
        if "->" in c:
            left, right = [p.strip().strip("\"'") for p in c.split("->", 1)]
            if left and right:
                pronunciation_glossary[left] = right
        elif ":" in c and not c.lower().startswith("http"):
            left, right = [p.strip().strip("\"'") for p in c.split(":", 1)]
            if left and right and len(left) <= 32:
                pronunciation_glossary[left] = right
        if c:
            spoken_numbers_vi.append(c)

    misconception = _clean_line(miscon_lines[0]) if miscon_lines else ""
    correction = " ".join(_clean_line(x) for x in miscon_lines[1:]) if len(miscon_lines) > 1 else misconception

    pin_coordinates: list[dict[str, Any]] = []
    for raw in gis_lines:
        c = _clean_line(raw)
        cm = _COORDINATE_RE.search(c)
        if cm:
            pin_coordinates.append({
                "label": re.sub(r"[:(\[]?\s*-?\d{1,3}\.\d+\s*,\s*-?\d{1,3}\.\d+.*", "", c).strip() or "Site",
                "lon": float(cm.group(1)),
                "lat": float(cm.group(2)),
            })

    return {
        "schema_version": "1.0",
        "topic": topic,
        "channel_id": channel_id,
        "language": lang,
        "format_profile": format_profile,
        "audience": audience,
        "research_mode": "deep_research" if format_profile == "long_16x9" else "fast_research",
        "source_mode": source_mode,
        "verified_facts": verified_facts,
        "report_only_claims": report_only_claims,
        "surprising_hook_fact": " ".join(_clean_line(x) for x in hook_lines).strip(),
        "mechanism_plain_vi": " ".join(_clean_line(x) for x in mech_lines).strip(),
        "analogies": analogies,
        "vietnam_micro_bridges": vietnam_micro_bridges,
        "visual_appearance_notes": " ".join(_clean_line(x) for x in visual_lines).strip(),
        "misconception_and_correction": {
            "misconception": misconception,
            "correction": correction,
        },
        "conflicts_or_gaps": [_clean_line(x) for x in conflict_lines if not re.search(r"\breport[- ]only\b", x, re.IGNORECASE)],
        "spoken_numbers_vi": spoken_numbers_vi,
        "pronunciation_glossary": pronunciation_glossary,
        "chronicle_gis_anchors": {
            "pin_coordinates": pin_coordinates,
            "timeline_notes": [_clean_line(x) for x in gis_lines if not _COORDINATE_RE.search(x)],
        },
    }


def validate_fact_vault(vault: dict[str, Any], min_verified_facts: int | None = None) -> dict[str, Any]:
    """Validate canonical `FactVault`, quarantining any report-only claims."""
    errors: list[str] = []
    warnings: list[str] = []

    topic = str(vault.get("topic") or "").strip()
    channel_id = str(vault.get("channel_id") or "").strip()
    fmt = str(vault.get("format_profile") or "short_9x16").strip()
    lang = str(vault.get("language") or ("en" if channel_id.startswith("en_") else "vi")).strip()

    if not topic:
        errors.append("MISSING_TOPIC: FactVault requires non-empty 'topic'")
    if not channel_id:
        errors.append("MISSING_CHANNEL_ID: FactVault requires 'channel_id'")

    req_facts = min_verified_facts if min_verified_facts is not None else (8 if fmt == "long_16x9" else 4)
    verified = list(vault.get("verified_facts") or [])
    report_only = list(vault.get("report_only_claims") or [])

    clean_verified: list[dict[str, Any]] = []
    for i, item in enumerate(verified):
        status = str(item.get("status") or "verified").lower()
        src = str(item.get("source_name") or "").strip()
        claim = str(item.get("claim_vi") or item.get("claim_en") or item.get("claim_text") or "").strip()
        if status == "report-only" or src.lower() == "report-only":
            errors.append(f"REPORT_ONLY_IN_VERIFIED: item[{i}] ({claim[:48]}) must sit in report_only_claims, not verified_facts")
            continue
        if not claim:
            errors.append(f"EMPTY_CLAIM: verified_facts[{i}] has empty claim text")
            continue
        if not src:
            errors.append(f"MISSING_SOURCE_NAME: verified_facts[{i}] ({claim[:48]}) has no source_name")
            continue
        clean_verified.append(item)

    if len(clean_verified) < req_facts:
        errors.append(
            f"INSUFFICIENT_VERIFIED_FACTS: found {len(clean_verified)} verified facts, need >= {req_facts} for {fmt}"
        )

    if not str(vault.get("surprising_hook_fact") or "").strip():
        warnings.append("MISSING_SURPRISING_HOOK_FACT: populate 'surprising_hook_fact' for stronger Cold Open")
    if not str(vault.get("mechanism_plain_vi") or "").strip():
        warnings.append("MISSING_MECHANISM_PLAIN: populate 'mechanism_plain_vi' for conversational clarity")

    if lang == "vi" and not (vault.get("vietnam_micro_bridges") or []):
        warnings.append("MISSING_VN_MICRO_BRIDGES: VN channels should include >= 1 'vietnam_micro_bridges' item for 60s localization")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "verified_fact_count": len(clean_verified),
        "report_only_count": len(report_only),
        "required_min_facts": req_facts,
    }


def export_research_architect_sources(vault: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert verified FactVault items into `vp-research-architect` `brief.sources[]` entries."""
    by_source: dict[str, list[str]] = {}
    for item in vault.get("verified_facts") or []:
        if str(item.get("status") or "").lower() == "report-only":
            continue
        src = str(item.get("source_name") or "").strip()
        claim = str(item.get("claim_vi") or item.get("claim_en") or item.get("claim_text") or "").strip()
        if src and claim:
            by_source.setdefault(src, []).append(claim)
    return [
        {"title": src, "reference": src, "facts": claims}
        for src, claims in by_source.items()
    ]


def format_youtube_sources_block(vault: dict[str, Any], language: str | None = None) -> str:
    """Format verified source attribution lines for YouTube descriptions (never includes report-only)."""
    lang = language or str(vault.get("language") or "vi")
    seen: list[str] = []
    for item in vault.get("verified_facts") or []:
        if str(item.get("status") or "").lower() == "report-only":
            continue
        src = str(item.get("source_name") or "").strip()
        if src and src.lower() != "report-only" and src not in seen:
            seen.append(src)
    header = "Nguồn tham khảo:" if lang == "vi" else "Sources:"
    if not seen:
        return f"{header}\n- (Đang cập nhật nguồn sơ cấp)" if lang == "vi" else f"{header}\n- (Primary sources pending)"
    return header + "\n" + "\n".join(f"- {s}" for s in seen)


def export_chanh_niem_ke_manifest_seed(vault: dict[str, Any]) -> dict[str, Any]:
    """Extract `chanh_niem_ke` V5.0 `episode_manifest.json` seed fields from a FactVault."""
    anchors = vault.get("chronicle_gis_anchors") or {}
    return {
        "topic": vault.get("topic", ""),
        "pin_coordinates": list(anchors.get("pin_coordinates") or []),
        "timeline_notes": list(anchors.get("timeline_notes") or []),
        "pronunciation_glossary": dict(vault.get("pronunciation_glossary") or {}),
        "vietnam_micro_bridges": list(vault.get("vietnam_micro_bridges") or []),
        "verified_facts_summary": [
            {
                "id": f.get("id"),
                "fact": f.get("claim_vi") or f.get("claim_text"),
                "exact_number": f.get("exact_number", ""),
                "source": f.get("source_name", ""),
            }
            for f in (vault.get("verified_facts") or [])
            if str(f.get("status") or "").lower() != "report-only"
        ],
    }


def render_channel_master_prompts(
    channel_id: str,
    topic: str,
    format_profile: str = "long_16x9",
    audience: str = "",
) -> dict[str, str]:
    """Render ready-to-paste Notebook 1, 2 & 3 Master Prompts tailored to channel & format."""
    meta = _infer_channel_meta(channel_id)
    lang = meta["language"]
    arch_id = meta["archetype_id"]
    if not audience:
        audience = (
            "Khán giả Việt Nam 22-44 tuổi thích giải mã bản chất dễ hiểu"
            if lang == "vi"
            else "Curious English-speaking adults seeking clear source-backed explainers"
        )
    rec_sources = _CHANNEL_SPECIFIC_SOURCES.get(
        channel_id,
        ARCHETYPE_SOURCE_PRIORITIES.get(arch_id, ARCHETYPE_SOURCE_PRIORITIES["archetype_1_forensic_noir"])[lang],
    )
    research_mode = "Deep Research" if format_profile == "long_16x9" else "Fast Research"
    fact_range = "12-22" if format_profile == "long_16x9" else "4-7"
    lang_label = "Vietnamese" if lang == "vi" else "English"

    nb1_prompt = (
        f"You are a retention analyst for {lang_label} "
        f"{'long-form documentaries' if format_profile == 'long_16x9' else 'vertical shorts'} "
        f"({meta['display_name']}, niche: {meta['niche']}). Use ONLY the sources in this notebook. "
        "Study narrative structure ONLY — NEVER quote or reuse phrasing.\n"
        f"Extract: (1) Top 4 hook formulas (first sentence <= {'24' if format_profile == 'long_16x9' else '18'} syllables), "
        "(2) Beat/chapter pacing map"
        + (" with 60-90s Retention Resets" if format_profile == "long_16x9" else " across 12-18 beats")
        + ", (3) Top 5 retention techniques, (4) Natural closing CTA + Short-to-Long bridge rules (zero like/share/subscribe), "
        "(5) Forbidden AI-translationese markers."
    )

    nb2_prompt = (
        "You are a prompting-technique analyst. Use ONLY official Google Flow documentation in this notebook "
        "(Nano Banana 2.1 BELUGA, Omni 1.2 Flash macaron_cookie, Veo 3.1 Lite). "
        "Output: (1) Positive-framing image prompt order, (2) Reference image line wording, "
        "(3) Veo 3.1 Lite 10-credit Seam prompt template (70-100w, surface anti-symbol guard) vs "
        "Omni 1.2 Flash Frame-Link template (40-70w), (4) Avoid retiring Veo 3.1 Fast/Quality & Omni 1.1 (Dec 5, 2026) and retired Veo Extend."
    )

    nb3_step1 = (
        f"[Run {research_mode} in NotebookLM]\n"
        f"TOPIC: {topic}\n"
        f"CHANNEL: {channel_id} ({meta['niche']})\n"
        f"FORMAT: {format_profile}\n"
        f"AUDIENCE: {audience}\n"
        f"Find authoritative primary sources in: {rec_sources}. "
        "Prioritize exact numbers, units, dates, causal mechanisms, and physical visual appearance."
    )

    extra_cnk = (
        "\n9. Chronicle GIS Anchors: geographic [lon, lat] coordinates and chronological causal steps."
        if channel_id == "chanh_niem_ke"
        else ""
    )
    nb3_step2 = (
        f"TOPIC: {topic}\nCHANNEL: {channel_id} | FORMAT: {format_profile} | AUDIENCE: {audience}\n"
        "Use ONLY original sources imported in this notebook. Claims only in a summary report without primary-source confirmation MUST be labeled \"report-only\".\n"
        "Output Markdown sections:\n"
        f"1. Key facts ({fact_range}): exact number, unit, date, and [Source Name] in brackets.\n"
        "2. Most surprising hook fact and why viewers assume the opposite.\n"
        "3. How it works (step-by-step causal mechanism in plain spoken Vietnamese).\n"
        "4. Analogies & Vietnam Micro-Bridges (2-3 concrete comparisons for everyday VN viewers).\n"
        "5. Visual appearance notes (colors, shapes, scale, setting; zero text in frame).\n"
        "6. Common misconception and correction.\n"
        "7. Spoken numbers & Pronunciation Glossary (e.g. AZ-5 -> A Zét năm).\n"
        f"8. Report-only claims & Conflicts/Gaps.{extra_cnk}"
    )

    return {
        "channel_id": channel_id,
        "archetype_id": arch_id,
        "format_profile": format_profile,
        "recommended_sources": rec_sources,
        "notebook_1_pattern_prompt": nb1_prompt,
        "notebook_2_flow_rules_prompt": nb2_prompt,
        "notebook_3_research_box": nb3_step1,
        "notebook_3_chat_prompt": nb3_step2,
    }


class NotebookLMBridge:
    """Hybrid Dual-Mode connector: CLI (`nlm`/`notebooklm-py`) + Chrome CDP pool plan + Web UI fallback."""

    NOTEBOOKLM_URL = "https://notebooklm.google.com/"

    @staticmethod
    def detect_capabilities() -> dict[str, Any]:
        """Inspect available automation bridges read-only (never launches Chrome)."""
        has_nlm_cli = shutil.which("nlm") is not None
        has_notebooklm_py = importlib.util.find_spec("notebooklm") is not None
        cdp_profiles: list[dict[str, Any]] = []
        try:
            from flow_cdp.accounts import default_profiles
            cdp_profiles = [
                {"id": p.get("id"), "port": p.get("port"), "directory": p.get("directory"), "enabled": bool(p.get("enabled", True))}
                for p in default_profiles()
                if p.get("enabled", True)
            ]
        except Exception:
            cdp_profiles = []

        return {
            "cli_available": has_nlm_cli or has_notebooklm_py,
            "has_nlm_cli": has_nlm_cli,
            "has_notebooklm_py": has_notebooklm_py,
            "cdp_profiles_count": len(cdp_profiles),
            "cdp_profile_sample": cdp_profiles[:5],
            "web_import_available": True,
            "offline_fallback_available": True,
            "recommended_mode": (
                "nlm_cli"
                if has_nlm_cli
                else ("notebooklm_py" if has_notebooklm_py else ("chrome_cdp_or_web_import" if cdp_profiles else "web_import"))
            ),
        }

    @staticmethod
    def build_cdp_notebooklm_launch_plan(profile_id: str | None = None) -> dict[str, Any]:
        """Build a GPU-compliant Chrome CDP launch command using `flow_cdp` pool config."""
        from flow_cdp.accounts import default_profiles, detect_chrome_binary
        from flow_cdp.resource_locks import build_optimized_chrome_launch

        profiles = [p for p in default_profiles() if p.get("enabled", True)]
        if not profiles:
            raise RuntimeError("No enabled Chrome profiles found in flow_cdp.accounts.default_profiles()")

        chosen = profiles[0]
        if profile_id:
            matches = [p for p in profiles if p.get("id") == profile_id]
            if not matches:
                raise ValueError(f"Profile {profile_id!r} not found in flow_cdp profiles")
            chosen = matches[0]

        cmd = build_optimized_chrome_launch(
            chrome_bin=detect_chrome_binary(),
            port=int(chosen["port"]),
            user_data_dir=str(chosen["user_data_dir"]),
            profile_dir=str(chosen["directory"]),
            url=NotebookLMBridge.NOTEBOOKLM_URL,
            headless=True,
        )
        return {
            "profile_id": chosen["id"],
            "port": int(chosen["port"]),
            "url": NotebookLMBridge.NOTEBOOKLM_URL,
            "gpu_rule": ".agents/rules/gpu-headless-chrome.md",
            "command": cmd,
        }

    @staticmethod
    def fetch_via_cli(notebook_id: str, prompt: str, timeout_sec: int = 90) -> str:
        """Query an existing NotebookLM notebook via `nlm` CLI if installed."""
        nlm_bin = shutil.which("nlm")
        if not nlm_bin:
            raise RuntimeError(
                "`nlm` CLI is not installed. Use Web UI + `notebooklm_vault.py import-notes` or install notebooklm-mcp-cli."
            )
        proc = subprocess.run(
            [nlm_bin, "notebook", "query", notebook_id, prompt],
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"nlm query failed ({proc.returncode}): {proc.stderr.strip()}")
        return proc.stdout.strip()


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Video Pilot NotebookLM 3-Vault CLI")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("bridge-status", help="Inspect available NotebookLM automation bridges (read-only)")

    rp = sub.add_parser("render-prompts", help="Render channel-tailored Notebook 1/2/3 Master Prompts")
    rp.add_argument("--channel", required=True)
    rp.add_argument("--topic", required=True)
    rp.add_argument("--format", default="long_16x9", choices=["short_9x16", "long_16x9"])
    rp.add_argument("--audience", default="")
    rp.add_argument("--json", action="store_true")

    imp = sub.add_parser("import-notes", help="Parse NotebookLM Markdown notes into validated fact_vault.json")
    imp.add_argument("--channel", required=True)
    imp.add_argument("--topic", required=True)
    imp.add_argument("--format", default="short_9x16", choices=["short_9x16", "long_16x9"])
    imp.add_argument("--audience", default="")
    imp.add_argument("--input", required=True, help="Markdown notes file exported from NotebookLM")
    imp.add_argument("--output", required=True, help="Destination fact_vault.json path")

    val = sub.add_parser("validate", help="Validate an existing fact_vault.json")
    val.add_argument("--vault", required=True)
    val.add_argument("--min-facts", type=int, default=None)

    exp = sub.add_parser("export-sources", help="Export brief.sources JSON and YouTube description source block")
    exp.add_argument("--vault", required=True)
    exp.add_argument("--json", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    if args.command == "bridge-status":
        print(json.dumps(NotebookLMBridge.detect_capabilities(), ensure_ascii=False, indent=2))
        return 0

    if args.command == "render-prompts":
        prompts = render_channel_master_prompts(args.channel, args.topic, args.format, args.audience)
        if args.json:
            print(json.dumps(prompts, ensure_ascii=False, indent=2))
        else:
            for k, v in prompts.items():
                print(f"=== {k} ===\n{v}\n")
        return 0

    if args.command == "import-notes":
        md_text = Path(args.input).read_text(encoding="utf-8")
        vault = parse_notebooklm_markdown_to_fact_vault(
            md_text=md_text,
            topic=args.topic,
            channel_id=args.channel,
            format_profile=args.format,
            audience=args.audience,
        )
        res = validate_fact_vault(vault)
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(vault, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"output": str(out_p), "validation": res}, ensure_ascii=False, indent=2))
        return 0 if res["valid"] else 1

    if args.command == "validate":
        vault = json.loads(Path(args.vault).read_text(encoding="utf-8"))
        res = validate_fact_vault(vault, min_verified_facts=args.min_facts)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0 if res["valid"] else 1

    if args.command == "export-sources":
        vault = json.loads(Path(args.vault).read_text(encoding="utf-8"))
        payload = {
            "brief_sources": export_research_architect_sources(vault),
            "youtube_sources_block": format_youtube_sources_block(vault),
        }
        if vault.get("channel_id") == "chanh_niem_ke":
            payload["chanh_niem_ke_manifest_seed"] = export_chanh_niem_ke_manifest_seed(vault)
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(payload["youtube_sources_block"])
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
