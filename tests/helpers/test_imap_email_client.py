import os

import pytest

from utils.helpers.email.imap_email_client import ImapEmailClient


pytestmark = pytest.mark.helpers


def test_imap_client_reads_credentials_from_environment(monkeypatch):
    monkeypatch.setenv("TEST_EMAIL_USERNAME", "automation@example.com")
    monkeypatch.setenv("TEST_EMAIL_PASSWORD", "secret")

    client = ImapEmailClient(
        host="imap.example.com",
        username_env="TEST_EMAIL_USERNAME",
        password_env="TEST_EMAIL_PASSWORD",
    )

    assert client.username == "automation@example.com"
    assert client.password == "secret"


def test_imap_client_raises_clear_error_when_username_env_missing(monkeypatch):
    monkeypatch.delenv("MISSING_EMAIL_USERNAME", raising=False)

    with pytest.raises(ValueError, match="MISSING_EMAIL_USERNAME"):
        ImapEmailClient(
            host="imap.example.com",
            username_env="MISSING_EMAIL_USERNAME",
            password="secret",
        )


def test_imap_client_from_config_uses_expected_values(monkeypatch):
    monkeypatch.setenv("TEST_EMAIL_USERNAME", "automation@example.com")
    monkeypatch.setenv("TEST_EMAIL_PASSWORD", "secret")

    client = ImapEmailClient.from_config(
        {
            "host": "imap.example.com",
            "port": 1993,
            "use_ssl": True,
            "username_env": "TEST_EMAIL_USERNAME",
            "password_env": "TEST_EMAIL_PASSWORD",
        }
    )

    assert client.host == "imap.example.com"
    assert client.port == 1993
    assert client.use_ssl is True
    assert client.username == os.getenv("TEST_EMAIL_USERNAME")
