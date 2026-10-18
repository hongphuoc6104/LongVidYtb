"""Credential renewal is opt-in and persists privately, without allocation or OAuth UI."""
import hashlib
import json
import types
from unittest.mock import patch

from colab_bridge.assignment_probe import probe
from dashboard.data import Dashboard


def test_expired_credentials_are_observation_only_unless_refresh_is_requested(tmp_path):
    credentials = types.SimpleNamespace(valid=False, refresh_token='fixture-private-refresh')
    refreshed = []

    def refresh(request):
        refreshed.append(request)
        credentials.valid = True

    credentials.refresh = refresh
    credentials.to_json = lambda: json.dumps({'token': 'fixture-private-token'})

    class Credential:
        @staticmethod
        def from_authorized_user_file(path):
            return credentials

    class Session:
        def __init__(self, cred, max_refresh_attempts):
            self.cred = cred

        def get(self, url, **kwargs):
            return types.SimpleNamespace(status_code=200, json=lambda: {'email': 'fixture@example.test', 'email_verified': True})

    class Client:
        def __init__(self, *args):
            pass

        def list_assignments(self):
            return []

    modules = {
        'google': types.ModuleType('google'), 'google.oauth2': types.ModuleType('google.oauth2'),
        'google.oauth2.credentials': types.SimpleNamespace(Credentials=Credential),
        'google.auth': types.ModuleType('google.auth'), 'google.auth.transport': types.ModuleType('google.auth.transport'),
        'google.auth.transport.requests': types.SimpleNamespace(AuthorizedSession=Session, Request=object),
        'colab_cli.common': types.SimpleNamespace(Client=Client, Prod=object),
    }
    with patch.dict('sys.modules', modules):
        assert probe(tmp_path, 'tts')['reason'] == 'refresh_required'
        assert not refreshed
        assert not (tmp_path/'token.json').exists()
        report = probe(tmp_path, 'tts', refresh_auth=True)
    assert len(refreshed) == 1
    assert report['verified'] is True
    assert report['identity'] == 'google:'+hashlib.sha256(b'fixture@example.test').hexdigest()
    assert (tmp_path/'token.json').stat().st_mode & 0o777 == 0o600
    assert 'fixture-private' not in json.dumps(report)


def test_dashboard_reads_cached_health_without_contacting_provider(tmp_path):
    home = tmp_path/'home'
    registry = home/'.config/video-pilot/colab/accounts.json'
    registry.parent.mkdir(parents=True)
    registry.write_text('{"accounts":[{"id":"one"}]}')
    app = Dashboard(tmp_path/'system', home=home)
    health = app.budgets.path.parent/'colab-health.json'
    health.parent.mkdir(parents=True)
    health.write_text(json.dumps({'checked_at': 100, 'verified_identities': 1, 'accounts': [
        {'id': 'one', 'state': 't4_ready', 'duplicate_of': 'two'}]}))
    with patch('colab_bridge.health.audit', side_effect=AssertionError('GET must not contact provider')):
        state = app.snapshot()
    account = state['inventory']['accounts'][0]
    assert state['inventory']['colab_health']['verified_identities'] == 1
    assert account['runtime_health']['duplicate_of'] == 'two'
    assert account['capability']['state'] == 't4_ready'


def test_dashboard_audit_action_runs_in_background_and_refresh_is_explicit(tmp_path):
    app = Dashboard(tmp_path/'system', home=tmp_path)
    with patch('pathlib.Path.home', return_value=tmp_path), \
         patch.object(app, 'start_operation', side_effect=lambda scope, action, task: task()), \
         patch('colab_bridge.health.audit', return_value={'fixture': True}) as audit:
        assert app.mutate('audit-colab-pool', {}) == {'fixture': True}
        assert audit.call_args.kwargs['refresh_auth'] is False
        app.mutate('audit-colab-pool', {'refresh_auth': True})
        assert audit.call_args.kwargs['refresh_auth'] is True
