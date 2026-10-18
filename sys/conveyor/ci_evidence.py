"""Fail-closed validation of actual GitHub Actions results for one revision."""
from __future__ import annotations

import base64
import json


def decode_ci_runs(payload: str) -> object:
    """Decode explicit jq @base64 output without depending on TOON formatting."""
    if not isinstance(payload, str) or len(payload) > 1_000_000:
        raise ValueError('Invalid CI evidence envelope')
    return json.loads(base64.b64decode(payload.strip(), validate=True))


def validate_ci_runs(runs: object, head: str) -> bool:
    """Missing, truncated, pending, skipped or foreign-revision runs cannot certify CI."""
    return (
        isinstance(runs, list) and bool(runs)
        and all(isinstance(run, dict) and run.get('head_sha') == head
                and run.get('status') == 'completed' and run.get('conclusion') == 'success'
                and isinstance(run.get('id'), int) and isinstance(run.get('html_url'), str)
                for run in runs)
    )
