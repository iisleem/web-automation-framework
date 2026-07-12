import pytest

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils.assertions import assert_list_sorted


@pytest.mark.regression
@pytest.mark.parametrize(
    ("sort_option", "field", "reverse"),
    [
        ("az", "name", False),
        ("za", "name", True),
        ("lohi", "price", False),
        ("hilo", "price", True),
    ],
)
def test_sort_products_by_name_and_price(page, base_url, users, sort_option, field, reverse):
    login_page = LoginPage(page)
    inventory_page = InventoryPage(page)

    login_page.open(base_url)
    login_page.login(**users["standard_user"])
    inventory_page.sort_products(sort_option)

    values = (
        inventory_page.get_product_names()
        if field == "name"
        else inventory_page.get_product_prices()
    )
    assert_list_sorted(values, reverse=reverse)
