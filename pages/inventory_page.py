from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage


class InventoryPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.title = self.locator_with_fallbacks(
            "inventory title",
            "[data-test='title']",
            ".title",
            "span:has-text('Products')",
        )
        self.inventory_items = self.locator_with_fallbacks(
            "inventory items",
            "[data-test='inventory-item']",
            ".inventory_item",
        )
        self.cart_link = self.locator_with_fallbacks(
            "shopping cart link",
            "[data-test='shopping-cart-link']",
            ".shopping_cart_link",
        )
        self.cart_badge = self.locator_with_fallbacks(
            "shopping cart badge",
            "[data-test='shopping-cart-badge']",
            ".shopping_cart_badge",
        )
        self.sort_dropdown = self.locator_with_fallbacks(
            "product sort dropdown",
            "[data-test='product-sort-container']",
            ".product_sort_container",
            "select",
        )
        self.product_names = self.locator_with_fallbacks(
            "product names",
            "[data-test='inventory-item-name']",
            ".inventory_item_name",
        )
        self.product_prices = self.locator_with_fallbacks(
            "product prices",
            "[data-test='inventory-item-price']",
            ".inventory_item_price",
        )

    def is_loaded(self) -> bool:
        expect(self.resolve(self.title)).to_have_text("Products")
        return True

    def add_product_to_cart(self, product_name: str) -> None:
        item = self._product_item(product_name)
        self.click(item.get_by_role("button", name="Add to cart"), f"Add {product_name}")

    def remove_product_from_cart(self, product_name: str) -> None:
        item = self._product_item(product_name)
        self.click(item.get_by_role("button", name="Remove"), f"Remove {product_name}")

    def open_cart(self) -> None:
        self.click(self.cart_link, "shopping cart")

    def get_cart_count(self) -> int:
        if not self.cart_badge.is_visible():
            return 0
        return int(self.cart_badge.inner_text())

    def sort_products(self, option_value: str) -> None:
        self.select(self.sort_dropdown, option_value, "product sort option")

    def get_product_names(self) -> list[str]:
        return self.product_names.all_inner_texts()

    def get_product_prices(self) -> list[float]:
        prices = self.product_prices.all_inner_texts()
        return [float(price.replace("$", "")) for price in prices]

    def _product_item(self, product_name: str) -> Locator:
        return self.inventory_items.filter(has_text=product_name)
