from __future__ import annotations

from typing import Any

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


def login_as(
    page: Any,
    base_url: str,
    user: dict[str, str],
) -> InventoryPage:
    login_page = LoginPage(page)
    inventory_page = InventoryPage(page)

    login_page.open(base_url)
    login_page.login(user["username"], user["password"])
    inventory_page.is_loaded()
    return inventory_page


def add_product_and_open_cart(
    page: Any,
    base_url: str,
    user: dict[str, str],
    product_name: str,
) -> CartPage:
    inventory_page = login_as(page, base_url, user)
    inventory_page.add_product_to_cart(product_name)
    inventory_page.open_cart()
    return CartPage(page)


def start_checkout_for_product(
    page: Any,
    base_url: str,
    user: dict[str, str],
    product_name: str,
) -> CheckoutPage:
    cart_page = add_product_and_open_cart(page, base_url, user, product_name)
    cart_page.checkout()
    return CheckoutPage(page)


def submit_checkout_information(
    checkout_page: CheckoutPage,
    customer: dict[str, str],
) -> CheckoutPage:
    checkout_page.fill_information(
        customer["first_name"],
        customer["last_name"],
        customer["postal_code"],
    )
    checkout_page.continue_to_overview()
    return checkout_page


def checkout_product(
    page: Any,
    base_url: str,
    user: dict[str, str],
    product_name: str,
    customer: dict[str, str],
) -> CheckoutPage:
    checkout_page = start_checkout_for_product(page, base_url, user, product_name)
    submit_checkout_information(checkout_page, customer)
    checkout_page.is_overview_displayed()
    checkout_page.finish_order()
    return checkout_page
