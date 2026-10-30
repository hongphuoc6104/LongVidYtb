"""Channel experiment scoring from exported TikTok / YouTube Studio metrics.

CSV columns (header required; extra columns ignored, missing numeric = 0):
    channel_id, platform, video_id, format, views, avg_watch_pct, completion_pct,
    shares, new_followers, ctr_pct

Usage:
    python sys/analytics/channel_metrics.py sys/channels/metrics.csv

Decision rule (from the 8-channel plan):
- scale:   any short >= 5,000 views, or median short completion >= 40%,
           or long with ctr >= 4% and avg_watch >= 35%
- iterate: some signal (median short views >= 500 or any long ctr >= 2.5%)
- kill:    otherwise, once the channel has >= MIN_VIDEOS videos
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

MIN_VIDEOS = 6
VIRAL_SHORT_VIEWS = 5000
SCALE_COMPLETION = 40.0
SCALE_LONG_CTR = 4.0
SCALE_LONG_WATCH = 35.0
ITERATE_SHORT_VIEWS = 500
ITERATE_LONG_CTR = 2.5

_NUMERIC = ("views", "avg_watch_pct", "completion_pct", "shares", "new_followers", "ctr_pct")


@dataclass
class VideoMetric:
    channel_id: str
    platform: str
    video_id: str
    format: str
    views: float = 0
    avg_watch_pct: float = 0
    completion_pct: float = 0
    shares: float = 0
    new_followers: float = 0
    ctr_pct: float = 0

    @property
    def is_short(self) -> bool:
        return self.format.startswith("short")


@dataclass
class ChannelVerdict:
    channel_id: str
    videos: int
    shorts: int
    longs: int
    median_short_views: float
    max_short_views: float
    median_short_completion: float
    best_long_ctr: float
    best_long_watch: float
    follows_per_video: float
    decision: str
    reason: str


def _num(value: Optional[str]) -> float:
    try:
        return float(str(value).replace(",", "").replace("%", "").strip() or 0)
    except ValueError:
        return 0.0


def load_metrics(path: Path) -> List[VideoMetric]:
    with Path(path).open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for row in rows:
        if not (row.get("channel_id") or "").strip():
            continue
        out.append(VideoMetric(
            channel_id=row["channel_id"].strip(),
            platform=(row.get("platform") or "").strip(),
            video_id=(row.get("video_id") or "").strip(),
            format=(row.get("format") or "short_9x16").strip(),
            **{k: _num(row.get(k)) for k in _NUMERIC},
        ))
    return out


def _median(values: Iterable[float]) -> float:
    vals = list(values)
    return float(statistics.median(vals)) if vals else 0.0


def judge(channel_id: str, metrics: Sequence[VideoMetric]) -> ChannelVerdict:
    shorts = [m for m in metrics if m.is_short]
    longs = [m for m in metrics if not m.is_short]
    med_views = _median(m.views for m in shorts)
    max_views = max((m.views for m in shorts), default=0.0)
    med_completion = _median(m.completion_pct for m in shorts)
    best_ctr = max((m.ctr_pct for m in longs), default=0.0)
    best_watch = max((m.avg_watch_pct for m in longs), default=0.0)
    strong_long = any(m.ctr_pct >= SCALE_LONG_CTR and m.avg_watch_pct >= SCALE_LONG_WATCH for m in longs)
    follows = sum(m.new_followers for m in metrics) / len(metrics) if metrics else 0.0

    if max_views >= VIRAL_SHORT_VIEWS or (shorts and med_completion >= SCALE_COMPLETION) or strong_long:
        decision, reason = "scale", "Có tín hiệu thắng: tăng lên 3-5 short/ngày và giữ 1 long/tuần."
    elif med_views >= ITERATE_SHORT_VIEWS or best_ctr >= ITERATE_LONG_CTR:
        decision, reason = "iterate", "Có tín hiệu yếu: đổi câu mở đầu / góc chủ đề, giữ ngách."
    elif len(metrics) < MIN_VIDEOS:
        decision, reason = "collect", f"Chưa đủ dữ liệu (< {MIN_VIDEOS} video)."
    else:
        decision, reason = "kill", "Không có tín hiệu sau đủ video: dừng hoặc đổi ngách."
    return ChannelVerdict(
        channel_id=channel_id, videos=len(metrics), shorts=len(shorts), longs=len(longs),
        median_short_views=med_views, max_short_views=max_views, median_short_completion=med_completion,
        best_long_ctr=best_ctr, best_long_watch=best_watch, follows_per_video=round(follows, 2),
        decision=decision, reason=reason,
    )


def judge_all(metrics: Sequence[VideoMetric]) -> List[ChannelVerdict]:
    grouped: Dict[str, List[VideoMetric]] = {}
    for m in metrics:
        grouped.setdefault(m.channel_id, []).append(m)
    order = {"scale": 0, "iterate": 1, "collect": 2, "kill": 3}
    verdicts = [judge(cid, ms) for cid, ms in grouped.items()]
    return sorted(verdicts, key=lambda v: (order[v.decision], -v.max_short_views))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    args = parser.parse_args(argv)
    verdicts = judge_all(load_metrics(args.csv))
    print(json.dumps([asdict(v) for v in verdicts], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
