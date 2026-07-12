import pytest

from utils.helpers.performance import (
    assert_no_slow_resources,
    assert_page_load_under,
    assert_resource_count_under,
    get_navigation_timing,
    get_resource_summary,
    get_resource_timings,
)


pytestmark = pytest.mark.helpers


class FakePage:
    def __init__(self):
        self.navigation_timing = {
            "startTime": 0,
            "domContentLoadedEventEnd": 450,
            "loadEventEnd": 900,
            "responseEnd": 300,
            "duration": 900,
        }
        self.resources = [
            {
                "name": "https://example.test/app.js",
                "initiatorType": "script",
                "duration": 120,
                "transferSize": 1000,
            },
            {
                "name": "https://example.test/logo.png",
                "initiatorType": "img",
                "duration": 80,
                "transferSize": 500,
            },
        ]

    def evaluate(self, script):
        if "navigation" in script:
            return self.navigation_timing
        if "resource" in script:
            return self.resources
        raise AssertionError(f"Unexpected script: {script}")


def test_navigation_and_resource_helpers_return_browser_timings():
    page = FakePage()

    assert get_navigation_timing(page)["loadEventEnd"] == 900
    assert get_resource_timings(page) == page.resources
    assert get_resource_summary(page) == {
        "count": 2,
        "total_transfer_size": 1500,
        "by_type": {"script": 1, "img": 1},
    }


def test_performance_assertions_pass_for_thresholds():
    page = FakePage()

    assert_page_load_under(page, 1000)
    assert_no_slow_resources(page, 150)
    assert_resource_count_under(page, 1, resource_type="img")


def test_performance_assertions_report_failures():
    page = FakePage()

    with pytest.raises(AssertionError, match="page performance metric"):
        assert_page_load_under(page, 100)

    with pytest.raises(AssertionError, match="slower than"):
        assert_no_slow_resources(page, 100)

    with pytest.raises(AssertionError, match="resource count"):
        assert_resource_count_under(page, 1)


def test_slow_resource_assertion_supports_ignored_patterns():
    page = FakePage()

    assert_no_slow_resources(
        page,
        100,
        ignored_url_patterns=["*app.js"],
    )
