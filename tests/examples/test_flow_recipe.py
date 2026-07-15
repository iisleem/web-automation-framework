import pytest

from flows.saucedemo import add_product_and_open_cart
from utils.assertions import assert_equal, assert_true


pytestmark = pytest.mark.examples


def test_flow_helper_adds_product_and_opens_cart(page, base_url, users):
    product_name = "Sauce Labs Bike Light"

    cart_page = add_product_and_open_cart(
        page=page,
        base_url=base_url,
        user=users["standard_user"],
        product_name=product_name,
    )

    assert_equal(cart_page.get_item_count(), 1, "Cart should contain one product")
    assert_true(cart_page.is_product_in_cart(product_name), "Flow helper should leave the product in cart")
