#!/usr/bin/env python3
"""Fact Grounding Linter (4th Mandatory Script Linter for Video Pilot).

Validates spoken narration against `fact_vault.json` across all repo script schemas:
  1. Report-Only Leakage Gate: blocks claims flagged `report-only` without user approval.
  2. Quantitative Number Grounding: checks concrete numbers/years/metrics against `verified_facts`.
  3. Domain Safety Guard: blocks ungrounded medical cure, legal guarantee, and financial return promises.
  4. Source Attribution Report: prints verified `sources_used` and YouTube source block.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from tools.notebooklm_vault import format_youtube_sources_block  # noqa: E402

_PAUSE_TAG_RE = re.compile(r"\[pause:[^\]]+\]", re.IGNORECASE)
_NUMBER_RE = re.compile(r"(?<![A-Za-zÀ-ỹ])\d+(?:[.,]\d+)?(?![A-Za-zÀ-ỹ])")
_STOPWORDS = frozenset({
    "của", "và", "là", "trong", "cho", "với", "những", "này", "được", "một", "các",
    "nhưng", "khi", "nếu", "để", "từ", "vào", "lại", "rất", "chỉ", "hơn", "nhất",
    "that", "this", "with", "from", "have", "they", "were", "when", "only", "into",
})

_DOMAIN_SAFETY_RULES: dict[str, list[tuple[re.Pattern[str], str]]] = {
    "co_the_ke": [
        (re.compile(r"\b(?:chữa\s+khỏi\s+hoàn\s+toàn|chữa\s+dứt\s+điểm|thay\s+thế\s+thuốc|đặc\s+trị\s+bách\s+bệnh)\b", re.I),
         "MEDICAL_CLAIM_FORBIDDEN: ungrounded cure/treatment claim on co_the_ke"),
    ],
    "en_inside_vessel": [
        (re.compile(r"\b(?:guaranteed\s+cure|cures\s+permanently|replaces\s+medication)\b", re.I),
         "MEDICAL_CLAIM_FORBIDDEN: ungrounded cure/treatment claim on en_inside_vessel"),
    ],
    "luat_doi_thuong": [
        (re.compile(r"\b(?:chắc\s+chắn\s+thắng\s+kiện\s+100%|cam\s+kết\s+thắng\s+kiện|bảo\s+đảm\s+được\s+bồi\s+thường\s+tuyệt\s+đối)\b", re.I),
         "LEGAL_GUARANTEE_FORBIDDEN: guaranteed litigation outcome on luat_doi_thuong"),
    ],
    "en_fine_print": [
        (re.compile(r"\b(?:guaranteed\s+to\s+win\s+in\s+court|100%\s+legal\s+victory)\b", re.I),
         "LEGAL_GUARANTEE_FORBIDDEN: guaranteed litigation outcome on en_fine_print"),
    ],
    "tui_tien": [
        (re.compile(r"\b(?:cam\s+kết\s+lợi\s+nhuận|chắc\s+chắn\s+lãi|làm\s+giàu\s+không\s+rủi\s+ro)\b", re.I),
         "FINANCIAL_GUARANTEE_FORBIDDEN: guaranteed investment return on tui_tien"),
    ],
    "en_wallet_anatomy": [
        (re.compile(r"\b(?:guaranteed\s+returns?|risk-free\s+profit)\b", re.I),
         "FINANCIAL_GUARANTEE_FORBIDDEN: guaranteed investment return on en_wallet_anatomy"),
    ],
}


def extract_narration_units(content: dict[str, Any]) -> list[dict[str, str]]:
    """Extract ordered `{id, text}` narration units from any Video Pilot script schema."""
    units: list[dict[str, str]] = []

    for idx, ch in enumerate(content.get("chapters") or [], start=1):
        for b_idx, beat in enumerate(ch.get("beats") or [], start=1):
            txt = str(beat.get("narration") or beat.get("text") or "").strip()
            if txt:
                units.append({"id": str(beat.get("id") or beat.get("beat_id") or f"CH{idx}_B{b_idx}"), "text": txt})

    for idx, sc in enumerate(content.get("scenes") or [], start=1):
        txt = str(sc.get("narration") or sc.get("dialogue") or sc.get("text") or "").strip()
        if txt:
            units.append({"id": str(sc.get("id") or f"SC{idx:02d}"), "text": txt})

    for key in ("beats", "visual_states", "segments"):
        for idx, item in enumerate(content.get(key) or [], start=1):
            if not isinstance(item, dict):
                continue
            txt = str(item.get("narration") or item.get("text") or "").strip()
            if txt:
                units.append({"id": str(item.get("id") or item.get("beat_id") or f"{key}_{idx}"), "text": txt})

    return units


def _normalize_num(tok: str) -> str:
    return tok.replace(",", ".").rstrip(".")


def _is_trivial_ordinal(num_str: str, full_text: str, pos: int) -> bool:
    """Ignore trivial small rhetorical counts/ordinals (e.g. '1', '2', '3') unless part of units."""
    try:
        val = float(num_str)
    except ValueError:
        return True
    if val in (1.0, 2.0, 3.0) and "." not in num_str:
        after = full_text[pos : pos + 20].lower()
        if not re.match(r"^\s*(?:%|phần trăm|kg|km|mét|triệu|tỷ|tỉ|độ|giờ|năm|tháng|usd|\$)", after):
            return True
    return False


def _build_verified_corpus(vault: dict[str, Any]) -> tuple[str, set[str]]:
    parts: list[str] = []
    for item in vault.get("verified_facts") or []:
        if str(item.get("status") or "").lower() == "report-only":
            continue
        for k in ("claim_vi", "claim_en", "claim_text", "exact_number"):
            val = str(item.get(k) or "").strip()
            if val:
                parts.append(val)
    for k in ("surprising_hook_fact", "mechanism_plain_vi", "visual_appearance_notes"):
        val = str(vault.get(k) or "").strip()
        if val:
            parts.append(val)
    for lst_k in ("analogies", "vietnam_micro_bridges", "spoken_numbers_vi"):
        for v in vault.get(lst_k) or []:
            parts.append(str(v))

    corpus = " \n ".join(parts)
    nums = {_normalize_num(m.group(0)) for m in _NUMBER_RE.finditer(corpus)}
    return corpus, nums


def lint_fact_grounding(
    content: dict[str, Any],
    vault: dict[str, Any],
    channel_id: str | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    """Validate script narration against a verified `FactVault`."""
    errors: list[str] = []
    warnings: list[str] = []

    ch = channel_id or str(content.get("channel_id") or vault.get("channel_id") or "").strip()
    units = extract_narration_units(content)
    if not units:
        errors.append("EMPTY_SCRIPT: no narration text found in content/script JSON")

    verified_corpus, verified_nums = _build_verified_corpus(vault)
    verified_corpus_lower = verified_corpus.lower()

    # 1. Report-Only Leakage Gate
    skipped_report_only = 0
    for ro in vault.get("report_only_claims") or []:
        if ro.get("user_approved") is True:
            continue
        skipped_report_only += 1
        ro_text = str(ro.get("claim_vi") or ro.get("claim_en") or ro.get("claim_text") or "").strip()
        ro_nums = {
            _normalize_num(m.group(0))
            for m in _NUMBER_RE.finditer(ro_text)
            if _normalize_num(m.group(0)) not in verified_nums
        }
        ro_tokens = [
            w for w in re.findall(r"[a-zA-ZÀ-ỹ0-9_-]{4,}", ro_text.lower())
            if w not in _STOPWORDS and w not in verified_corpus_lower
        ]

        for u in units:
            clean_u = _PAUSE_TAG_RE.sub(" ", u["text"])
            u_lower = clean_u.lower()
            u_nums = {_normalize_num(m.group(0)) for m in _NUMBER_RE.finditer(clean_u)}
            leaked_nums = ro_nums & u_nums
            matched_tokens = [t for t in ro_tokens if re.search(rf"\b{re.escape(t)}\b", u_lower)]
            if leaked_nums or len(matched_tokens) >= 3:
                errors.append(
                    f"REPORT_ONLY_LEAKAGE[{u['id']}]: unverified report-only claim leaked into narration "
                    f"(nums={sorted(leaked_nums)}, terms={matched_tokens[:4]})"
                )

    # 2. Quantitative Number Grounding
    ungrounded_numbers: list[dict[str, str]] = []
    for u in units:
        clean_u = _PAUSE_TAG_RE.sub(" ", u["text"])
        for m in _NUMBER_RE.finditer(clean_u):
            norm = _normalize_num(m.group(0))
            if _is_trivial_ordinal(norm, clean_u, m.end()):
                continue
            if norm not in verified_nums:
                ungrounded_numbers.append({"unit": u["id"], "number": norm, "context": clean_u[:80]})

    if ungrounded_numbers:
        msg = (
            f"UNGROUNDED_NUMBERS: {len(ungrounded_numbers)} concrete numeric claim(s) absent from FactVault "
            + ", ".join(f"{x['unit']}:{x['number']}" for x in ungrounded_numbers[:6])
        )
        if strict:
            errors.append(msg)
        else:
            warnings.append(msg)

    # 3. Domain Safety Guard
    for pat, err_msg in _DOMAIN_SAFETY_RULES.get(ch, []):
        for u in units:
            if pat.search(u["text"]):
                errors.append(f"{err_msg} (at {u['id']})")

    sources_used: list[str] = []
    for item in vault.get("verified_facts") or []:
        if str(item.get("status") or "").lower() == "report-only":
            continue
        src = str(item.get("source_name") or "").strip()
        if src and src not in sources_used:
            sources_used.append(src)

    return {
        "valid": len(errors) == 0,
        "channel_id": ch,
        "strict": strict,
        "errors": errors,
        "warnings": warnings,
        "checked_units": len(units),
        "ungrounded_numbers": ungrounded_numbers,
        "skipped_report_only_count": skipped_report_only,
        "sources_used": sources_used,
        "youtube_sources_block": format_youtube_sources_block(vault),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Video Pilot Fact Grounding Linter")
    p.add_argument("--content", required=True, help="Path to content.json / script JSON")
    p.add_argument("--vault", required=True, help="Path to fact_vault.json")
    p.add_argument("--channel", default="", help="Channel ID override")
    p.add_argument("--strict", action="store_true", help="Fail on any ungrounded quantitative numbers")
    p.add_argument("--json", action="store_true", help="Print JSON output")
    args = p.parse_args(argv)

    content = json.loads(Path(args.content).read_text(encoding="utf-8"))
    vault = json.loads(Path(args.vault).read_text(encoding="utf-8"))
    res = lint_fact_grounding(content, vault, channel_id=args.channel or None, strict=args.strict)

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        status = "PASS" if res["valid"] else "FAIL"
        print(f"[fact_grounding_linter] {status} | units={res['checked_units']} | sources={len(res['sources_used'])}")
        for e in res["errors"]:
            print(f"  ERROR: {e}")
        for w in res["warnings"]:
            print(f"  WARN: {w}")
    return 0 if res["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
