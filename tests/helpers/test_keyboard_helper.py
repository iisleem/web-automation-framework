import pytest

from utils.helpers.keyboard import (
    assert_active_element_text,
    assert_focus_order,
    assert_focused,
    focus_element,
    press_key,
    shift_tab_to_previous,
    tab_to_next,
)


pytestmark = pytest.mark.helpers


class FakeKeyboard:
    def __init__(self, page):
        self.page = page
        self.presses = []

    def press(self, key):
        self.presses.append(key)
        if key == "Tab":
            self.page.move_focus(1)
        if key == "Shift+Tab":
            self.page.move_focus(-1)


class FakeLocator:
    def __init__(self, page, selector):
        self.page = page
        self.selector = selector

    def focus(self):
        self.page.active_selector = self.selector

    def evaluate(self, script):
        if "document.activeElement" in script:
            return self.page.active_selector == self.selector
        raise AssertionError(f"Unexpected script: {script}")


class FakePage:
    def __init__(self, focus_order=None):
        self.focus_order = focus_order or []
        self.active_selector = None
        self.active_text = ""
        self.keyboard = FakeKeyboard(self)

    def locator(self, selector):
        return FakeLocator(self, selector)

    def evaluate(self, script):
        if "document.activeElement" in script:
            return self.active_text
        raise AssertionError(f"Unexpected script: {script}")

    def move_focus(self, step):
        if not self.focus_order:
            return
        if self.active_selector not in self.focus_order:
            self.active_selector = self.focus_order[0 if step > 0 else -1]
            return
        current_index = self.focus_order.index(self.active_selector)
        next_index = (current_index + step) % len(self.focus_order)
        self.active_selector = self.focus_order[next_index]


def test_press_key_supports_repeat_count():
    page = FakePage()

    press_key(page, "Enter", times=3)

    assert page.keyboard.presses == ["Enter", "Enter", "Enter"]


def test_press_key_rejects_invalid_repeat_count():
    with pytest.raises(AssertionError, match="Expected times"):
        press_key(FakePage(), "Enter", times=0)


def test_tab_helpers_move_focus_forward_and_backward():
    page = FakePage(["#first", "#second", "#third"])

    tab_to_next(page, times=2)
    assert page.active_selector == "#second"

    shift_tab_to_previous(page)
    assert page.active_selector == "#first"


def test_focus_element_and_assert_focused():
    page = FakePage()

    locator = focus_element(page, "#email")

    assert locator.selector == "#email"
    assert_focused(page, "#email")


def test_assert_focused_has_clear_failure_message():
    page = FakePage()
    page.active_selector = "#password"

    with pytest.raises(AssertionError, match="Expected element"):
        assert_focused(page, "#email")


def test_assert_focus_order_tabs_through_selectors():
    page = FakePage(["#username", "#password", "#submit"])

    assert_focus_order(page, ["#username", "#password", "#submit"])

    assert page.keyboard.presses == ["Tab", "Tab", "Tab"]


def test_assert_focus_order_rejects_empty_selector_list():
    with pytest.raises(AssertionError, match="cannot be empty"):
        assert_focus_order(FakePage(), [])


def test_active_element_text_assertion_supports_contains_and_exact():
    page = FakePage()
    page.active_text = "Submit order"

    assert_active_element_text(page, "Submit")
    assert_active_element_text(page, "Submit order", contains=False)


def test_active_element_text_assertion_has_clear_failure_message():
    page = FakePage()
    page.active_text = "Cancel"

    with pytest.raises(AssertionError, match="Expected active element text"):
        assert_active_element_text(page, "Submit")
