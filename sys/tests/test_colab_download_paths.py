"""Path fallback must not multiply timeout/recovery attempts or hide provider errors."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from colab_bridge.client import Client, ColabError


def client() -> Client:
    value = Client.__new__(Client)
    value.session = "fixture-session"
    value.account = None
    value.binary = "/bin/true"
    return value


def test_absolute_download_succeeds_without_fallback() -> None:
    value = client()
    with patch.object(value, "call", return_value="") as call:
        value._download_archive("/content/job", Path("output.zip"), timeout=180)
    assert call.call_count == 1
    assert call.call_args.args[3] == "/content/job/output.zip"


def test_confirmed_missing_file_retries_relative_path_once() -> None:
    value = client()
    with patch.object(value, "call", side_effect=[ColabError("COLAB_REMOTE_PATH_NOT_FOUND: source"), ""]) as call:
        value._download_archive("/content/job", Path("output.zip"), timeout=300)
    assert [entry.args[3] for entry in call.call_args_list] == ["/content/job/output.zip", "job/output.zip"]
    assert all(entry.kwargs["timeout"] == 300 for entry in call.call_args_list)


@pytest.mark.parametrize("error", ["COLAB_TIMEOUT", "COLAB_PROVIDER_BLOCKED", "download unavailable", "COLAB_SESSION_NOT_FOUND"])
def test_unknown_or_provider_failure_is_not_retried(error: str) -> None:
    value = client()
    with patch.object(value, "call", side_effect=ColabError(error)) as call:
        with pytest.raises(ColabError, match=error):
            value._download_archive("/content/job", Path("output.zip"), timeout=180)
    assert call.call_count == 1


def test_path_outside_content_has_no_relative_fallback() -> None:
    value = client()
    with patch.object(value, "call", side_effect=ColabError("COLAB_REMOTE_PATH_NOT_FOUND: source")) as call:
        with pytest.raises(ColabError, match="REMOTE_PATH_NOT_FOUND"):
            value._download_archive("/remote/job", Path("output.zip"), timeout=180)
    assert call.call_count == 1


def test_transport_classifies_file_errors_without_copying_cli_output() -> None:
    value = client()
    response = SimpleNamespace(returncode=1, stdout="", stderr="No such file or directory: private-path")
    with patch("colab_bridge.client.subprocess.run", return_value=response):
        with pytest.raises(ColabError, match="COLAB_REMOTE_PATH_NOT_FOUND") as error:
            value.call("download", "-s", value.session, "/content/job/output.zip", "output.zip")
    assert "private-path" not in str(error.value)
