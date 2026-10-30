"""Soft retention scorer for channel scripts (hook, open loop, beat density, closing).

Usage:
    python sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel nao_luoi

Scores are advisory (like ``script_cadence_checker.py``); they never block a job.
A script below ``REWRITE_THRESHOLD`` should get a rewritten hook (write 3 variants, keep the best).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from channels.registry import get_channel  # noqa: E402

SYLLABLES_PER_SECOND = 4.3
REWRITE_THRESHOLD = 60
HOOK_MAX_SYLLABLES = {"short_9x16": 18, "long_16x9": 24}

_CURIOSITY = re.compile(
    r"(?i)(\?|vì sao|tại sao|ủa|sự thật|bí mật|không ai|ít ai|sai|thật ra|điều gì|nếu bạn|đừng|\d)"
)
_DIRECT = re.compile(r"(?i)\b(bạn|mình|ta)\b")
_OPEN_LOOP = re.compile(
    r"(?i)(nhưng|thế nhưng|vậy mà|hóa ra|cuối video|lát nữa|điều bất ngờ|bí mật|câu trả lời|chuyện gì)"
)
_CLOSING = re.compile(r"(?i)(\?|bình luận|comment|phần 2|phần tiếp|theo dõi|lưu lại|tag|chia sẻ|bạn có)")
_SPLIT = re.compile(r"(?<=[.!?…])\s+")


def syllables(text: str) -> int:
    return len([w for w in re.split(r"\s+", text.strip()) if re.search(r"\w", w)])


def sentences(text: str) -> List[str]:
    return [s.strip() for s in _SPLIT.split(text.strip()) if s.strip()]


@dataclass
class HookScore:
    channel_id: str
    format_profile: str
    score: int
    hook: str
    hook_syllables: int
    estimated_seconds: float
    seconds_per_sentence: float
    checks: dict = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)

    @property
    def needs_rewrite(self) -> bool:
        return self.score < REWRITE_THRESHOLD


def score_script(narrations: Sequence[str], channel_id: str, format_profile: str = "short_9x16") -> HookScore:
    """Score scene narrations in order against the channel's format spec."""
    channel = get_channel(channel_id)
    spec = channel.spec_for(format_profile)
    text = " ".join(n.strip() for n in narrations if n and n.strip())
    sents = sentences(text)
    if not sents:
        raise ValueError("Script has no narration")
    hook = sents[0]
    hook_syl = syllables(hook)
    total_syl = syllables(text)
    seconds = round(total_syl / SYLLABLES_PER_SECOND, 1)
    sec_per_sentence = round(seconds / len(sents), 2)
    lo, hi = spec.duration_seconds
    beat_hi = spec.beat_interval_seconds[1]
    limit = HOOK_MAX_SYLLABLES.get(format_profile, 20)
    early = " ".join(sents[1:4])

    checks = {
        "hook_short": hook_syl <= limit,
        "hook_curiosity": bool(_CURIOSITY.search(hook)),
        "hook_direct": bool(_DIRECT.search(hook)),
        "open_loop": bool(_OPEN_LOOP.search(early) or "?" in early),
        "beat_density": sec_per_sentence <= beat_hi,
        "duration_fit": lo * 0.85 <= seconds <= hi * 1.15,
        "closing_cta": bool(_CLOSING.search(sents[-1])),
    }
    weights = {"hook_short": 20, "hook_curiosity": 20, "hook_direct": 10, "open_loop": 15,
               "beat_density": 15, "duration_fit": 10, "closing_cta": 10}
    score = sum(weights[k] for k, ok in checks.items() if ok)

    fixes = {
        "hook_short": f"Rút câu mở đầu xuống <= {limit} âm tiết (hiện {hook_syl}).",
        "hook_curiosity": "Câu mở đầu cần câu hỏi, con số hoặc sự thật ngược đời. Mẫu: " + channel.hook_formulas[0],
        "hook_direct": "Nói thẳng với người xem ('bạn') ngay câu đầu.",
        "open_loop": "Trong 3 câu tiếp theo, hứa một câu trả lời và trì hoãn nó ('Nhưng điều bất ngờ là...').",
        "beat_density": f"Mỗi câu trung bình {sec_per_sentence}s; tách câu để có nhịp mới mỗi <= {beat_hi:g}s.",
        "duration_fit": f"Ước lượng {seconds}s, mục tiêu {lo}-{hi}s cho {format_profile}.",
        "closing_cta": "Câu kết: " + spec.closing,
    }
    return HookScore(
        channel_id=channel.id,
        format_profile=format_profile,
        score=score,
        hook=hook,
        hook_syllables=hook_syl,
        estimated_seconds=seconds,
        seconds_per_sentence=sec_per_sentence,
        checks=checks,
        suggestions=[fixes[k] for k, ok in checks.items() if not ok],
    )


def score_content_file(path: Path, channel_id: str, format_profile: Optional[str] = None) -> HookScore:
    content = json.loads(Path(path).read_text(encoding="utf-8"))
    brief_path = Path(path).with_name("brief.json")
    fmt = format_profile
    if fmt is None and brief_path.exists():
        fmt = json.loads(brief_path.read_text(encoding="utf-8")).get("format_profile")
    narrations = [sc.get("narration", "") for sc in content.get("scenes", [])]
    return score_script(narrations, channel_id, fmt or "short_9x16")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content", required=True, type=Path)
    parser.add_argument("--channel", required=True)
    parser.add_argument("--format", dest="format_profile", default=None)
    args = parser.parse_args(argv)
    result = score_content_file(args.content, args.channel, args.format_profile)
    print(json.dumps(dict(asdict(result), needs_rewrite=result.needs_rewrite), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
