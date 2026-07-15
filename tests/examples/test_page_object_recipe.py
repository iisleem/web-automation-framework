import pytest

from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils.assertions import assert_equal, assert_true


pytestmark = pytest.mark.examples


def test_page_object_login_adds_product_to_cart(page, base_url, users):
    user = users["standard_user"]
    product_name = "Sauce Labs Backpack"

    login_page = LoginPage(page)
    inventory_page = InventoryPage(page)
    cart_page = CartPage(page)

    login_page.open(base_url)
    login_page.login(user["username"], user["password"])

    assert_true(inventory_page.is_loaded(), "Inventory page should load after login")

    inventory_page.add_product_to_cart(product_name)
    assert_equal(inventory_page.get_cart_count(), 1, "Cart badge should show one item")

    inventory_page.open_cart()
    assert_true(cart_page.is_product_in_cart(product_name), "Selected product should appear in the cart")
