import pytest

from utils.helpers.notifications import (
    assert_notification_hidden,
    assert_notification_visible,
    dismiss_notification,
    notification_locator,
    wait_for_notification,
)


pytestmark = pytest.mark.helpers


class FakeLocator:
    def __init__(self, selector, text="", visible=True):
        self.selector = selector
        self.text = text
        self.visible = visible
        self.filters = []
        self.waits = []
        self.clicked = False

    def filter(self, **kwargs):
        self.filters.append(kwargs)
        return self

    def first(self):
        return self

    def wait_for(self, state, timeout):
        self.waits.append((state, timeout))
        if state == "visible":
            assert self.visible is True
        if state == "hidden":
            self.visible = False

    def inner_text(self):
        return self.text

    def click(self):
        self.clicked = True


class FakePage:
    def __init__(self):
        self.locators = {}

    def locator(self, selector):
        if selector not in self.locators:
            self.locators[selector] = FakeLocator(selector)
        return self.locators[selector]


def test_notification_locator_supports_text_filter():
    page = FakePage()

    locator = notification_locator(page, selector=".toast", text="Saved")

    assert locator.selector == ".toast"
    assert locator.filters == [{"has_text": "Saved"}]


def test_wait_for_notification_waits_until_visible():
    page = FakePage()
    page.locator(".toast").text = "Saved successfully"

    locator = wait_for_notification(page, selector=".toast", text="Saved", timeout_ms=3000)

    assert locator.waits == [("visible", 3000)]
    assert locator.filters == [{"has_text": "Saved"}]


def test_assert_notification_visible_supports_contains_and_exact():
    page = FakePage()
    page.locator(".toast").text = "Saved successfully"

    assert_notification_visible(page, "Saved", selector=".toast")
    assert_notification_visible(
        page,
        "Saved successfully",
        selector=".toast",
        contains=False,
    )


def test_assert_notification_visible_has_clear_failure_message():
    page = FakePage()
    page.locator(".toast").text = "Failed"

    with pytest.raises(AssertionError, match="Expected notification"):
        assert_notification_visible(
            page,
            "Saved",
            selector=".toast",
            contains=False,
        )


def test_assert_notification_hidden_waits_for_hidden_state():
    page = FakePage()

    assert_notification_hidden(page, selector=".toast", timeout_ms=2000)

    assert page.locator(".toast").waits == [("hidden", 2000)]
    assert page.locator(".toast").visible is False


def test_dismiss_notification_clicks_dismiss_and_waits_hidden():
    page = FakePage()

    dismiss_notification(
        page,
        dismiss_selector=".toast button",
        notification_selector=".toast",
        timeout_ms=1500,
    )

    assert page.locator(".toast button").clicked is True
    assert page.locator(".toast").waits == [("hidden", 1500)]
