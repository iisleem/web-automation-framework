import pytest

from utils.helpers.visual import (
    assert_screenshot_created,
    assert_screenshot_matches_baseline,
    capture_element_screenshot,
    capture_page_screenshot,
    screenshot_path,
)


pytestmark = pytest.mark.helpers


class FakePage:
    def __init__(self):
        self.calls = []

    def screenshot(self, **kwargs):
        self.calls.append(kwargs)
        with open(kwargs["path"], "wb") as file:
            file.write(b"fake-page-png")


class FakeLocator:
    def __init__(self):
        self.calls = []

    def screenshot(self, **kwargs):
        self.calls.append(kwargs)
        with open(kwargs["path"], "wb") as file:
            file.write(b"fake-element-png")


def test_capture_page_screenshot_writes_file_and_passes_options(tmp_path):
    page = FakePage()
    output_path = tmp_path / "screens" / "home.png"

    result = capture_page_screenshot(
        page,
        output_path,
        full_page=False,
        mask=["dynamic"],
    )

    assert result == output_path
    assert output_path.read_bytes() == b"fake-page-png"
    assert page.calls == [{"path": str(output_path), "full_page": False, "mask": ["dynamic"]}]


def test_capture_element_screenshot_writes_file(tmp_path):
    locator = FakeLocator()
    output_path = tmp_path / "element.png"

    result = capture_element_screenshot(locator, output_path)

    assert result == output_path
    assert output_path.read_bytes() == b"fake-element-png"


def test_assert_screenshot_matches_baseline_creates_missing_baseline(tmp_path):
    actual = tmp_path / "actual.png"
    baseline = tmp_path / "baseline" / "home.png"
    actual.write_bytes(b"same")

    result = assert_screenshot_matches_baseline(actual, baseline)

    assert result == baseline
    assert baseline.read_bytes() == b"same"


def test_assert_screenshot_matches_baseline_detects_difference(tmp_path):
    actual = tmp_path / "actual.png"
    baseline = tmp_path / "baseline.png"
    actual.write_bytes(b"actual")
    baseline.write_bytes(b"baseline")

    with pytest.raises(AssertionError, match="Screenshot does not match baseline"):
        assert_screenshot_matches_baseline(actual, baseline)


def test_assert_screenshot_created_requires_non_empty_file(tmp_path):
    screenshot = tmp_path / "screen.png"
    screenshot.write_bytes(b"png")

    assert assert_screenshot_created(screenshot) == screenshot


def test_screenshot_path_sanitizes_name():
    assert screenshot_path("screens", "checkout complete / chrome").as_posix() == (
        "screens/checkout_complete___chrome.png"
    )
