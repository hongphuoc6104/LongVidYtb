"""Explicit profile policy and dependency validation for Flow production."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def profile_path(profile: dict[str, Any]) -> Path:
    return (Path(profile['user_data_dir']).expanduser() / profile['directory']).resolve()


def authorized_profiles(
    profiles: list[dict[str, Any]], session: dict[str, Any], accounts: list[dict[str, Any]], policy: str,
) -> list[dict[str, Any]]:
    """Configuration is inventory, never authorization to use an account."""
    if policy not in {'pool', 'single_profile'}:
        raise ValueError('FLOW_DISPATCH_POLICY: expected pool or single_profile')
    allowed = set(session.get('pool', []))
    paths = {
        (Path(a['metadata_root']).expanduser() / a['profile']).resolve(): a['id']
        for a in accounts if a.get('service') == 'flow' and a['id'] in allowed
    }
    binding = session.get('runtime_bindings', {}).get('flow', {})
    bound = binding.get('target', {}).get('profile_path')
    result = [dict(p, account=paths[profile_path(p)]) for p in profiles
              if p.get('enabled', True) and profile_path(p) in paths]
    if policy == 'single_profile':
        if bound:
            result = [p for p in result if profile_path(p) == Path(bound).expanduser().resolve()]
        else:
            selected = session.get('defaults', {}).get('flow')
            result = [p for p in result if p['account'] == selected]
    if not result:
        raise ValueError('FLOW_AUTHORIZED_POOL_EMPTY: select a verified authorized profile')
    return result


def job_profiles(p: Any, job: str) -> tuple[str, list[dict[str, Any]]]:
    from account_catalog import discover
    from execution import settings

    from pilot import read

    frozen = p.payload(job, 'control')
    # Old jobs remain single-profile until an official new job/migration opts in.
    policy = frozen.get('flow_dispatch_policy', 'single_profile')
    profiles = read(p.root / 'config.json').get('flow_cdp_profiles', [])
    return policy, authorized_profiles(
        profiles, settings(p, job)['management_session'], discover(system_root=p.root)['accounts'], policy,
    )


def validate_dependencies(units: list[dict[str, Any]]) -> int:
    """Return runnable root count; reject cycles/missing parents before workers start."""
    by_id = {unit['id']: unit for unit in units}
    if len(by_id) != len(units):
        raise ValueError('FLOW_DEPENDENCY_DUPLICATE: duplicate image IDs')
    complete: set[str] = set()

    def visit(key: str, path: set[str]) -> None:
        if key in complete:
            return
        if key in path:
            raise ValueError('FLOW_DEPENDENCY_CYCLE: ' + key)
        parent = by_id[key].get('based_on')
        if parent:
            if parent not in by_id:
                raise ValueError('FLOW_DEPENDENCY_MISSING: ' + parent)
            visit(parent, path | {key})
            if by_id[parent].get('ratio') != by_id[key].get('ratio'):
                raise ValueError('FLOW_DEPENDENCY_RATIO: Base and variation ratios differ')
        complete.add(key)

    for key in by_id:
        visit(key, set())
    return sum(not unit.get('based_on') for unit in units)
