"""Immutable job configuration and per-revision runtime provenance."""
from __future__ import annotations

import copy
import hashlib
import json
import time
from pathlib import Path
from typing import Any


def job_config(pilot: Any, job: str | None = None) -> dict:
    """Use the accepted control snapshot; never merge new global defaults into a job."""
    if job is not None:
        from execution import is_job
        if is_job(pilot, job):
            return copy.deepcopy(pilot.payload(job, 'control'))
    path = Path(pilot.root) / 'config.json'
    return json.loads(path.read_text()) if path.is_file() else copy.deepcopy(getattr(pilot, 'cfg', {}) or {})


def source_receipt(root: Path, module: str, cfg: dict) -> dict:
    """Record actual implementation hashes without changing old job journals."""
    paths = set(root.glob('*.py'))
    for folder in ('content', 'scripts', 'tools', 'colab_bridge', 'flow_cdp', 'flow_prompts', 'renderer'):
        paths.update(p for p in (root / folder).rglob('*')
                     if p.is_file() and p.suffix in {'.py', '.mjs', '.tsx', '.ts', '.json'}
                     and '__pycache__' not in p.parts and 'node_modules' not in p.parts)
    sources = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}

    def stamp(value: Any) -> str:
        return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    return {'version': 1, 'module': module, 'started_at': time.time(),
            'source_sha256': stamp(sources), 'sources': sources, 'config_sha256': stamp(cfg),
            'quality_approval': False}
