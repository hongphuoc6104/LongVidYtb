"""Local account profiles; isolated OAuth, sessions, pool selection and history."""
import argparse
import fcntl
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

STORE = Path.home() / '.config/video-pilot/colab'
VALID_ROLES = ('any', 'tts', 'render')


def folder(name: str) -> Path:
    if not re.fullmatch('[a-z0-9][a-z0-9_-]{0,47}', str(name)):
        raise ValueError('Invalid account ID')
    return STORE / 'profiles' / name


def registry() -> dict[str, Any]:
    path = STORE / 'accounts.json'
    return json.loads(path.read_text()) if path.exists() else {'preferred': None, 'accounts': []}


def save(data: dict[str, Any]) -> None:
    STORE.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(STORE, 0o700)
    path = STORE / 'accounts.json'
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=2) + '\n')
    os.chmod(tmp, 0o600)
    tmp.replace(path)


def add(name: str, source: Path | None = None, role: str = 'any') -> None:
    if role not in VALID_ROLES:
        raise ValueError(f'Invalid role {role!r}; expected one of {VALID_ROLES}')
    data = registry()
    dest = folder(name)
    if dest.exists():
        raise ValueError('Account already exists; refusing to overwrite')
    if source and not (source / 'token.json').is_file():
        raise ValueError('No logged-in account')
    dest.mkdir(parents=True, mode=0o700)
    if source:
        for filename in ['token.json', 'sessions.json']:
            src = source / filename
            if src.is_file():
                shutil.copyfile(src, dest / filename)
                os.chmod(dest / filename, 0o600)
    entry: dict[str, Any] = {'id': name, 'enabled': True}
    if role != 'any':
        entry['role'] = role
    data['accounts'].append(entry)
    if data['preferred'] is None:
        data['preferred'] = name
    save(data)


def set_enabled(name: str, enabled: bool) -> dict[str, Any]:
    """Enable or disable an account profile in the pool registry."""
    folder(name)
    data = registry()
    target = next((x for x in data['accounts'] if x['id'] == name), None)
    if not target:
        raise ValueError(f'Unknown account: {name}')
    target['enabled'] = bool(enabled)
    if not enabled and data.get('preferred') == name:
        replacement = next(
            (x['id'] for x in data['accounts'] if x.get('enabled', True) and x['id'] != name),
            None,
        )
        if replacement:
            data['preferred'] = replacement
    elif enabled and data.get('preferred') is None:
        data['preferred'] = name
    save(data)
    return dict(target, preferred=(data.get('preferred') == name))


def set_role(name: str, role: str) -> dict[str, Any]:
    """Assign a workload role ('any', 'tts', or 'render') to an account profile."""
    folder(name)
    if role not in VALID_ROLES:
        raise ValueError(f'Invalid role {role!r}; expected one of {VALID_ROLES}')
    data = registry()
    target = next((x for x in data['accounts'] if x['id'] == name), None)
    if not target:
        raise ValueError(f'Unknown account: {name}')
    target['role'] = role
    save(data)
    return dict(target)


def remove(name: str, *, delete_files: bool = False) -> dict[str, Any]:
    """Remove an account from the registry (and optionally its profile folder if not busy)."""
    dest = folder(name)
    if is_session_busy(name):
        raise ValueError(f'Account {name} has an active busy session lock; stop/release before removing')
    data = registry()
    before = len(data['accounts'])
    data['accounts'] = [x for x in data['accounts'] if x['id'] != name]
    if len(data['accounts']) == before and not dest.exists():
        raise ValueError(f'Unknown account: {name}')
    if data.get('preferred') == name:
        data['preferred'] = next(
            (x['id'] for x in data['accounts'] if x.get('enabled', True)),
            data['accounts'][0]['id'] if data['accounts'] else None,
        )
    save(data)
    if delete_files and dest.exists():
        shutil.rmtree(dest)
    return {'removed': name, 'preferred': data.get('preferred')}


def is_session_busy(
    name: str,
    session: str = 'video-pilot-tts',
    *,
    lock_dir: Path | None = None,
) -> bool:
    """Return True if another process holds the local session execution lock."""
    try:
        from .protocol import stamp
    except (ImportError, ValueError):
        try:
            from protocol import stamp
        except ImportError:
            from sys.colab_bridge.protocol import stamp
    base = Path(lock_dir) if lock_dir is not None else (Path.home() / '.cache/video-pilot-colab')
    lock_path = base / (stamp([name, session]) + '.lock')
    if not lock_path.is_file():
        return False
    with lock_path.open('a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        else:
            fcntl.flock(handle, fcntl.LOCK_UN)
            return False


def local_sessions(name: str) -> list[str]:
    """Return session names currently recorded in the account's local sessions.json."""
    sess_file = folder(name) / 'sessions.json'
    if not sess_file.is_file():
        return []
    try:
        raw = json.loads(sess_file.read_text())
        if isinstance(raw, dict):
            return [k for k, v in raw.items() if isinstance(v, dict) and v.get('endpoint')]
    except (OSError, ValueError):
        pass
    return []


def has_external_session(name: str, allowed_prefixes: tuple[str, ...] = ('video-pilot',)) -> bool:
    """Return True if account has active sessions belonging to other external projects."""
    sess_names = local_sessions(name)
    for s in sess_names:
        if not any(s.startswith(p) for p in allowed_prefixes):
            return True
    return False


def select(
    name: str = 'auto',
    *,
    session: str = 'video-pilot-tts',
    role: str | None = None,
    exclude: set[str] | list[str] | tuple[str, ...] | None = None,
    prefer_idle: bool = False,
    lock_dir: Path | None = None,
) -> str:
    """Select an authenticated enabled account profile.

    - 'auto': selects preferred account first, then any enabled authenticated account.
    - 'auto-idle' (or prefer_idle=True): selects an enabled authenticated account whose
      target session is NOT currently locked by another process, enabling concurrent T4 usage.
    - explicit '<account-id>': selects that exact account if enabled and authenticated.
    """
    if role is not None and role not in VALID_ROLES:
        raise ValueError(f'Invalid role {role!r}; expected one of {VALID_ROLES}')
    data = registry()
    excluded = set(exclude or ())
    entries = list(data['accounts'])
    if name not in ('auto', 'auto-idle'):
        entries = [x for x in entries if x['id'] == name]
    else:
        if name == 'auto-idle':
            prefer_idle = True
        entries = sorted(
            entries,
            key=lambda x: (
                is_session_busy(x['id'], session, lock_dir=lock_dir) if prefer_idle else False,
                x['id'] != data['preferred'],
            ),
        )
    for item in entries:
        acc_id = item['id']
        if acc_id in excluded or not item.get('enabled', True):
            continue
        acc_role = item.get('role', 'any')
        if role and role != 'any' and acc_role not in ('any', role):
            continue
        # Protect accounts running external projects (e.g. histology, training notebooks)
        if has_external_session(acc_id):
            continue
        if (folder(acc_id) / 'token.json').is_file():
            if name == 'auto-idle' and is_session_busy(acc_id, session, lock_dir=lock_dir):
                continue
            return acc_id
    raise ValueError('COLAB_LOGIN_REQUIRED: no authenticated account profile')


def select_pool(
    *,
    max_accounts: int | None = None,
    session: str = 'video-pilot-tts',
    role: str | None = None,
    include_busy: bool = False,
    lock_dir: Path | None = None,
) -> list[str]:
    """Return ordered list of authenticated, enabled accounts for parallel Multi-T4 execution."""
    if role is not None and role not in VALID_ROLES:
        raise ValueError(f'Invalid role {role!r}; expected one of {VALID_ROLES}')
    data = registry()
    entries = sorted(
        data['accounts'],
        key=lambda x: (
            is_session_busy(x['id'], session, lock_dir=lock_dir),
            x['id'] != data.get('preferred'),
        ),
    )
    selected: list[str] = []
    for item in entries:
        acc_id = item['id']
        if not item.get('enabled', True):
            continue
        acc_role = item.get('role', 'any')
        if role and role != 'any' and acc_role not in ('any', role):
            continue
        # Protect accounts running external projects
        if has_external_session(acc_id):
            continue
        if not (folder(acc_id) / 'token.json').is_file():
            continue
        if not include_busy and is_session_busy(acc_id, session, lock_dir=lock_dir):
            continue
        selected.append(acc_id)
        if max_accounts is not None and max_accounts > 0 and len(selected) >= max_accounts:
            break
    return selected


def command(binary: str | Path, name: str, args: list[str] | tuple[str, ...]) -> list[str]:
    first = Path(binary).read_text().splitlines()[0]
    if not first.startswith('#!/') or ' ' in first[2:]:
        raise ValueError('Unsupported colab launcher')
    return [first[2:], str(Path(__file__).with_name('account_cli.py')), str(folder(name)), *args]


def assignment_state(binary: str | Path, name: str, session: str, timeout: int = 45) -> dict[str, Any]:
    """Read-only exact-account server probe using the installed official runtime."""
    argv = command(binary, name, ())
    helper = Path(__file__).with_name('assignment_probe.py')
    try:
        result = subprocess.run(
            [argv[0], str(helper), str(folder(name)), session],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode:
            return {'verified': False, 'reason': 'helper_failed', 'error_type': 'ProcessExit'}
        data = json.loads(result.stdout)
        if not isinstance(data, dict):
            raise ValueError('Invalid observation')
        return data
    except subprocess.TimeoutExpired:
        return {'verified': False, 'reason': 'network_unknown', 'error_type': 'TimeoutExpired'}
    except (OSError, ValueError):
        return {'verified': False, 'reason': 'helper_unavailable', 'error_type': 'InvalidObservation'}


def status_all(
    *,
    session: str = 'video-pilot-tts',
    probe_server: bool = False,
    binary: str | Path | None = None,
    lock_dir: Path | None = None,
) -> dict[str, Any]:
    """Inspect all registered Colab accounts, local session locks, and optional live server assignments."""
    d = registry()
    resolved_bin = binary or shutil.which('colab') or str(Path.home() / '.local/bin/colab')
    items: list[dict[str, Any]] = []
    for x in d['accounts']:
        acc_id = x['id']
        auth = (folder(acc_id) / 'token.json').is_file()
        busy = is_session_busy(acc_id, session, lock_dir=lock_dir)
        sessions = local_sessions(acc_id)
        info: dict[str, Any] = {
            'id': acc_id,
            'enabled': bool(x.get('enabled', True)),
            'role': x.get('role', 'any'),
            'preferred': acc_id == d.get('preferred'),
            'authenticated': auth,
            'session_busy': busy,
            'local_sessions': sessions,
        }
        if probe_server and auth and Path(resolved_bin).is_file():
            info['server_assignment'] = assignment_state(resolved_bin, acc_id, session)
        items.append(info)
    return {
        'store': str(STORE),
        'preferred': d.get('preferred'),
        'total_accounts': len(items),
        'ready_for_pool': sum(1 for i in items if i['enabled'] and i['authenticated'] and not i['session_busy']),
        'accounts': items,
    }


def main() -> None:
    actions = [
        'list', 'import-current', 'login', 'prefer', 'run', 'login-many',
        'enable', 'disable', 'role', 'remove', 'status-all', 'select-idle', 'pool',
    ]
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=actions)
    p.add_argument('account', nargs='?', default='auto')
    p.add_argument('args', nargs=argparse.REMAINDER)
    a = p.parse_args()
    if a.action == 'login-many':
        binary = shutil.which('colab') or str(Path.home() / '.local/bin/colab')
        while True:
            d = registry()
            used = {x['id'] for x in d['accounts']}
            n = 1
            while f'account-{n:02d}' in used:
                n += 1
            name = f'account-{n:02d}'
            add(name)
            print(f'\nĐăng nhập {name}: mở liên kết Google, chọn tài khoản khác, dán mã vào terminal này.', flush=True)
            result = subprocess.run(command(binary, name, ['sessions']))
            if result.returncode or not (folder(name) / 'token.json').is_file():
                print('Đăng nhập chưa hoàn tất. Dừng để giữ nguyên trạng thái.')
                return
            print(f'Đã lưu {name}.', flush=True)
            if input('Thêm tài khoản nữa? [y/N]: ').strip().lower() not in ('y', 'yes', 'c', 'có'):
                return
    if a.action == 'list':
        d = registry()
        print(json.dumps({
            'store': str(STORE),
            'preferred': d['preferred'],
            'accounts': [
                dict(
                    x,
                    role=x.get('role', 'any'),
                    authenticated=(folder(x['id']) / 'token.json').is_file(),
                    session_busy=is_session_busy(x['id']),
                )
                for x in d['accounts']
            ],
        }, indent=2))
        return
    if a.action == 'status-all':
        probe = '--probe' in a.args or (a.account == '--probe')
        print(json.dumps(status_all(probe_server=probe), indent=2))
        return
    if a.action == 'select-idle':
        role = a.args[0] if a.args else (a.account if a.account in VALID_ROLES else None)
        print(select('auto-idle', role=role))
        return
    if a.action == 'pool':
        role = a.account if a.account in VALID_ROLES else None
        print(json.dumps({'pool': select_pool(role=role)}, indent=2))
        return
    if a.action in ('enable', 'disable'):
        if a.account == 'auto':
            p.error('Specify account ID')
        print(json.dumps(set_enabled(a.account, a.action == 'enable'), indent=2))
        return
    if a.action == 'role':
        if a.account == 'auto' or not a.args:
            p.error('Specify account ID and role (any, tts, render)')
        print(json.dumps(set_role(a.account, a.args[0]), indent=2))
        return
    if a.action == 'remove':
        if a.account == 'auto':
            p.error('Specify account ID')
        delete_files = '--purge' in a.args
        print(json.dumps(remove(a.account, delete_files=delete_files), indent=2))
        return
    if a.action == 'import-current':
        add(a.account, Path.home() / '.config/colab-cli')
        print(a.account)
        return
    if a.action == 'prefer':
        name = select(a.account)
        d = registry()
        d['preferred'] = name
        save(d)
        print(name)
        return
    if a.action == 'login':
        if a.account == 'auto':
            p.error('Specify account ID')
        if not folder(a.account).exists():
            add(a.account)
        name = a.account
        args = ['sessions']
    else:
        name = select(a.account)
        args = a.args
        if args[:1] == ['--']:
            args = args[1:]
        if not args:
            p.error('Specify a Colab command')
    binary = shutil.which('colab') or str(Path.home() / '.local/bin/colab')
    raise SystemExit(subprocess.run(command(binary, name, args)).returncode)


if __name__ == '__main__':
    try:
        main()
    except ValueError as ex:
        print(str(ex), file=sys.stderr)
        raise SystemExit(2) from ex

