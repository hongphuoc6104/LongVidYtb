#!/usr/bin/env python3
"""Video Pilot — Multi-T4 Pool Dispatcher for Vietnamese Long Explainer Voices.

Synthesizes Studio V3 Human Voices across Colab accounts (account-05, account-06, account-07, account-08)
in parallel, ensuring 100% throughput across the remaining 18 channels.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

TOOL_DIR = Path(__file__).resolve().parent
SYS_DIR = TOOL_DIR.parent
ROOT_DIR = SYS_DIR.parent

for _p in (str(ROOT_DIR), str(SYS_DIR), str(TOOL_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tools.synthesize_vn_long_omnivoice import resolve_channel_ids, synthesize_long_channel

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("dispatch_vn_long_voices_pool")

POOL_ACCOUNTS: List[Tuple[str, str]] = [
    ("account-07", "vp-long-batch-07"),
    ("account-08", "vp-long-batch-08"),
    ("account-05", "vp-vn-long-1794089419"),
    ("account-06", "vp-ho-so-ky-la-long"),
]

VN_18_CHANNELS = [
    "banh-rang",
    "luat-doi-thuong",
    "la-ban-hoc-thuat",
    "luat-ngam",
    "ua-sao-vay",
    "dia-com",
    "vu-tru-ti-hon",
    "chanh-niem-ke",
    "minh-triet-song",
    "co-the-ke",
    "su-ke-lai",
    "ban-do-quyen-luc",
    "loi-sang-soi",
    "nao-luoi",
    "thuong-cho-kheo",
    "nghe-song-sot",
    "ai-binh-dan",
    "tam-tinh-dem",
]


def process_channel_job(channel_slug: str, account_info: Tuple[str, str]) -> Dict[str, Any]:
    account, session = account_info
    ch_id, clean_slug = resolve_channel_ids(channel_slug)
    logger.info(f"[{account}:{session}] Starting synthesis for {clean_slug}...")
    
    spec_p = SYS_DIR / f"channels/vn_rebuilt_style_specs/{clean_slug}/{clean_slug}_long_master_spec.json"
    out_dir = ROOT_DIR / f"video/vn_pilot_{ch_id}_long"
    
    t0 = time.time()
    try:
        mastered_wav = synthesize_long_channel(
            channel_arg=ch_id,
            spec_path_arg=str(spec_p),
            out_dir_arg=str(out_dir),
            account=account,
            session=session,
            batch_size=8,
            num_step=32,
        )
        elapsed = time.time() - t0
        logger.info(f"[{account}] Successfully synthesized {clean_slug} in {elapsed:.2f}s -> {mastered_wav}")
        return {
            "channel_slug": clean_slug,
            "account": account,
            "status": "success",
            "elapsed_sec": round(elapsed, 2),
            "wav_path": str(mastered_wav),
        }
    except Exception as e:
        elapsed = time.time() - t0
        logger.error(f"[{account}] Failed {clean_slug} after {elapsed:.2f}s: {e}", exc_info=True)
        return {
            "channel_slug": clean_slug,
            "account": account,
            "status": "error",
            "error": str(e),
            "elapsed_sec": round(elapsed, 2),
        }


def run_pool_dispatch(channels: List[str], pool: List[Tuple[str, str]] = POOL_ACCOUNTS) -> List[Dict[str, Any]]:
    logger.info(f"=== Dispatching {len(channels)} channels across {len(pool)} Colab T4 GPU accounts ===")
    results = []
    
    # We maintain an available worker queue
    import queue
    worker_q = queue.Queue()
    for item in pool:
        worker_q.put(item)
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(pool)) as executor:
        futures = {}
        for ch in channels:
            account_info = worker_q.get()
            fut = executor.submit(process_channel_job, ch, account_info)
            futures[fut] = account_info
            
            # When any future finishes, return its worker to the queue and submit the next
            if len(futures) >= len(pool):
                done, _ = concurrent.futures.wait(futures.keys(), return_when=concurrent.futures.FIRST_COMPLETED)
                for d in done:
                    acc_info = futures.pop(d)
                    worker_q.put(acc_info)
                    res = d.result()
                    results.append(res)
                    
        # Wait for remaining
        for fut in concurrent.futures.as_completed(futures.keys()):
            res = fut.result()
            results.append(res)
            
    logger.info(f"=== Pool Dispatch Complete: {len(results)} jobs finished ===")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pool Dispatcher for VN Long Voices")
    parser.add_argument("--channels", nargs="*", default=VN_18_CHANNELS, help="List of channels or default 18")
    parser.add_argument("--accounts", nargs="*", default=["account-07", "account-08"], help="Colab accounts to use")
    args = parser.parse_args()
    
    active_pool = [p for p in POOL_ACCOUNTS if p[0] in args.accounts]
    run_pool_dispatch(args.channels, active_pool)
