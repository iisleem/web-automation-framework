from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class CartPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.cart_items = self.locator_with_fallbacks(
            "cart items",
            "[data-test='inventory-item']",
            ".cart_item",
        )
        self.checkout_button = self.locator_with_fallbacks(
            "checkout button",
            "[data-test='checkout']",
            "#checkout",
            "button:has-text('Checkout')",
        )
        self.continue_shopping_button = self.locator_with_fallbacks(
            "continue shopping button",
            "[data-test='continue-shopping']",
            "#continue-shopping",
            "button:has-text('Continue Shopping')",
        )

    def remove_product(self, product_name: str) -> None:
        item = self._cart_item(product_name)
        self.click(item.get_by_role("button", name="Remove"), f"Remove {product_name}")

    def checkout(self) -> None:
        self.click(self.checkout_button, "checkout button")

    def continue_shopping(self) -> None:
        self.click(self.continue_shopping_button, "continue shopping button")

    def is_product_in_cart(self, product_name: str) -> bool:
        return self._cart_item(product_name).count() > 0

    def get_item_count(self) -> int:
        return self.cart_items.count()

    def _cart_item(self, product_name: str) -> Locator:
        return self.cart_items.filter(has_text=product_name)
