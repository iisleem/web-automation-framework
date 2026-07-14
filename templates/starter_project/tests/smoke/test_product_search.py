import pytest

from flows.product_flow import search_for_product


@pytest.mark.smoke
def test_product_search(page, base_url):
    search_for_product(page, base_url, "sample product")
