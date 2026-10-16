"""Fail-closed validation of actual GitHub Actions results for one revision."""
from __future__ import annotations


def validate_ci_runs(runs: object, head: str) -> bool:
    """Missing, truncated, pending, skipped or foreign-revision runs cannot certify CI."""
    return (
        isinstance(runs, list) and bool(runs)
        and all(isinstance(run, dict) and run.get('head_sha') == head
                and run.get('status') == 'completed' and run.get('conclusion') == 'success'
                and isinstance(run.get('id'), int) and isinstance(run.get('html_url'), str)
                for run in runs)
    )
