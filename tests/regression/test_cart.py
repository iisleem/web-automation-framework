import pytest

from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils.assertions import assert_equal, assert_true


PRODUCT_NAME = "Sauce Labs Backpack"


@pytest.mark.regression
def test_add_product_to_cart(page, base_url, users):
    login_page = LoginPage(page)
    inventory_page = InventoryPage(page)

    login_page.open(base_url)
    login_page.login(**users["standard_user"])
    inventory_page.add_product_to_cart(PRODUCT_NAME)

    assert_equal(inventory_page.get_cart_count(), 1, "Cart badge should show one item")


@pytest.mark.regression
def test_remove_product_from_cart(page, base_url, users):
    login_page = LoginPage(page)
    inventory_page = InventoryPage(page)
    cart_page = CartPage(page)

    login_page.open(base_url)
    login_page.login(**users["standard_user"])
    inventory_page.add_product_to_cart(PRODUCT_NAME)
    inventory_page.open_cart()

    assert_true(cart_page.is_product_in_cart(PRODUCT_NAME), "Product should be in cart")
    cart_page.remove_product(PRODUCT_NAME)

    assert_equal(cart_page.get_item_count(), 0, "Cart should be empty after removal")
