import pytest

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils.assertions import assert_equal


@pytest.mark.regression
@pytest.mark.reporting_demo
def test_intentional_failure_generates_artifacts(page, base_url, users):
    login_page = LoginPage(page)
    inventory_page = InventoryPage(page)

    login_page.open(base_url)
    login_page.login(**users["standard_user"])
    inventory_page.add_product_to_cart("Sauce Labs Backpack")

    assert_equal(
        inventory_page.get_cart_count(),
        99,
        "Intentional failure: cart count is expected to be wrong",
    )
