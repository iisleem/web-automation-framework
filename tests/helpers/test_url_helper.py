import pytest

from utils.helpers.url import (
    assert_url_contains_param,
    build_url,
    get_query_param,
    parse_query_params,
    remove_query_param,
)


pytestmark = pytest.mark.helpers


def test_build_url_with_query_params():
    url = build_url(
        "https://example.com",
        "search",
        {"q": "automation", "page": 2},
    )

    assert url == "https://example.com/search?q=automation&page=2"


def test_parse_and_get_query_params():
    url = "https://example.com/search?q=automation&page=2&page=3"

    assert parse_query_params(url) == {"q": ["automation"], "page": ["2", "3"]}
    assert get_query_param(url, "q") == "automation"


def test_assert_url_contains_param_passes_for_expected_value():
    assert_url_contains_param("https://example.com/search?q=automation", "q", "automation")


def test_assert_url_contains_param_fails_for_missing_param():
    with pytest.raises(AssertionError, match="query parameter"):
        assert_url_contains_param("https://example.com/search", "q")


def test_remove_query_param():
    result = remove_query_param("https://example.com/search?q=automation&page=2", "q")

    assert result == "https://example.com/search?page=2"
