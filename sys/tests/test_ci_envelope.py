"""CI machine evidence remains independent of the CLI's display format."""
import base64
import json

import pytest
from conveyor.ci_evidence import decode_ci_runs, validate_ci_runs


def test_ci_envelope_preserves_all_runs_and_rejects_incomplete_or_foreign_results():
    runs = [{'id': 1, 'head_sha': 'current', 'status': 'completed', 'conclusion': 'success',
             'html_url': 'https://example.test/run/1'}]
    payload = base64.b64encode(json.dumps(runs).encode()).decode()
    decoded = decode_ci_runs(payload)
    assert decoded == runs
    assert validate_ci_runs(decoded, 'current')
    assert not validate_ci_runs(decoded, 'different')
    assert not validate_ci_runs([*decoded, {**decoded[0], 'id': 2, 'status': 'in_progress'}], 'current')
    assert not validate_ci_runs([], 'current')
    with pytest.raises(ValueError):
        decode_ci_runs('runs[1]{id,status}: 1,completed')
