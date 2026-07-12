import pytest

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils.assertions import assert_contains, assert_true


@pytest.mark.smoke
def test_valid_login(page, base_url, users):
    login_page = LoginPage(page)
    inventory_page = InventoryPage(page)

    login_page.open(base_url)
    login_page.login(**users["standard_user"])

    assert_true(inventory_page.is_loaded(), "Standard user should land on inventory page")


@pytest.mark.smoke
@pytest.mark.negative
def test_invalid_login_shows_error(page, base_url, users):
    login_page = LoginPage(page)

    login_page.open(base_url)
    login_page.login(
        users["invalid_user"]["username"],
        users["invalid_user"]["password"],
    )

    assert_true(login_page.is_error_visible(), "Invalid login error should be visible")
    assert_contains(
        login_page.get_error_message(),
        users["invalid_user"]["expected_error"],
    )


@pytest.mark.smoke
@pytest.mark.negative
def test_locked_out_user_login_shows_error(page, base_url, users):
    login_page = LoginPage(page)

    login_page.open(base_url)
    login_page.login(
        users["locked_out_user"]["username"],
        users["locked_out_user"]["password"],
    )

    assert_true(login_page.is_error_visible(), "Locked-out user error should be visible")
    assert_contains(
        login_page.get_error_message(),
        users["locked_out_user"]["expected_error"],
    )
