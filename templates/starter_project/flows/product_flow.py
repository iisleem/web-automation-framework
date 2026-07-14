from __future__ import annotations

from typing import Any

from pages.product_page import ProductPage


def search_for_product(page: Any, base_url: str, search_term: str) -> ProductPage:
    product_page = ProductPage(page)
    product_page.open(base_url)
    product_page.assert_loaded()
    product_page.search(search_term)
    product_page.assert_result_visible(search_term)
    return product_page
