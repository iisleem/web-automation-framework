from __future__ import annotations

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class ProductPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.heading = self.locator_with_fallbacks(
            "product page heading",
            "[data-test='product-heading']",
            "h1",
        )
        self.search_input = self.locator_with_fallbacks(
            "product search input",
            "[data-test='product-search']",
            "input[name='search']",
        )
        self.result_title = self.locator_with_fallbacks(
            "product result title",
            "[data-test='product-result-title']",
            ".product-result-title",
        )

    def open(self, base_url: str) -> None:
        self.goto(f"{base_url.rstrip('/')}/products")

    def search(self, search_term: str) -> None:
        self.fill(self.search_input, search_term, "product search")

    def assert_loaded(self) -> None:
        expect(self.resolve(self.heading)).to_be_visible()

    def assert_result_visible(self, expected_text: str) -> None:
        expect(self.resolve(self.result_title)).to_contain_text(expected_text)
