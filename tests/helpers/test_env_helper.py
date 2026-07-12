import pytest

from utils.helpers.env import (
    mask_secret,
    optional_env,
    require_env,
    validate_required_envs,
)


pytestmark = pytest.mark.helpers


def test_require_env_returns_value(monkeypatch):
    monkeypatch.setenv("API_TOKEN", "secret")

    assert require_env("API_TOKEN") == "secret"


def test_require_env_raises_clear_error(monkeypatch):
    monkeypatch.delenv("MISSING_TOKEN", raising=False)

    with pytest.raises(EnvironmentError, match="MISSING_TOKEN"):
        require_env("MISSING_TOKEN")


def test_optional_env_returns_default(monkeypatch):
    monkeypatch.delenv("OPTIONAL_TOKEN", raising=False)

    assert optional_env("OPTIONAL_TOKEN", "fallback") == "fallback"


def test_validate_required_envs_returns_name_value_map(monkeypatch):
    monkeypatch.setenv("TOKEN_A", "a")
    monkeypatch.setenv("TOKEN_B", "b")

    assert validate_required_envs(["TOKEN_A", "TOKEN_B"]) == {
        "TOKEN_A": "a",
        "TOKEN_B": "b",
    }


def test_mask_secret_keeps_last_visible_chars():
    assert mask_secret("abcdef", visible_chars=2) == "****ef"
    assert mask_secret("abcdef", visible_chars=0) == "******"


def test_mask_secret_rejects_negative_visible_chars():
    with pytest.raises(ValueError, match="visible_chars"):
        mask_secret("secret", visible_chars=-1)
