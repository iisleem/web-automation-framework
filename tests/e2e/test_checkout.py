import pytest

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils.assertions import assert_contains, assert_true


PRODUCT_NAME = "Sauce Labs Bike Light"


@pytest.mark.e2e
def test_complete_checkout_flow(page, base_url, users, checkout_data):
    login_page = LoginPage(page)
    inventory_page = InventoryPage(page)
    cart_page = CartPage(page)
    checkout_page = CheckoutPage(page)
    customer = checkout_data["valid_customer"]

    login_page.open(base_url)
    login_page.login(**users["standard_user"])
    inventory_page.add_product_to_cart(PRODUCT_NAME)
    inventory_page.open_cart()
    cart_page.checkout()
    checkout_page.fill_information(
        customer["first_name"],
        customer["last_name"],
        customer["postal_code"],
    )
    checkout_page.continue_to_overview()

    assert_true(checkout_page.is_overview_displayed(), "Checkout overview should be visible")

    checkout_page.finish_order()

    assert_contains(checkout_page.get_complete_message(), "Thank you for your order!")


@pytest.mark.e2e
@pytest.mark.negative
def test_checkout_requires_first_name(page, base_url, users, checkout_data):
    login_page = LoginPage(page)
    inventory_page = InventoryPage(page)
    cart_page = CartPage(page)
    checkout_page = CheckoutPage(page)
    customer = checkout_data["missing_first_name"]

    login_page.open(base_url)
    login_page.login(**users["standard_user"])
    inventory_page.add_product_to_cart(PRODUCT_NAME)
    inventory_page.open_cart()
    cart_page.checkout()
    checkout_page.fill_information(
        customer["first_name"],
        customer["last_name"],
        customer["postal_code"],
    )
    checkout_page.continue_to_overview()

    assert_contains(checkout_page.get_error_message(), customer["expected_error"])
