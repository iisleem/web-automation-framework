from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.first_name_input = self.locator_with_fallbacks(
            "first name input",
            "[data-test='firstName']",
            "#first-name",
            "input[name='firstName']",
        )
        self.last_name_input = self.locator_with_fallbacks(
            "last name input",
            "[data-test='lastName']",
            "#last-name",
            "input[name='lastName']",
        )
        self.postal_code_input = self.locator_with_fallbacks(
            "postal code input",
            "[data-test='postalCode']",
            "#postal-code",
            "input[name='postalCode']",
        )
        self.continue_button = self.locator_with_fallbacks(
            "continue checkout button",
            "[data-test='continue']",
            "#continue",
            "input[type='submit']",
        )
        self.finish_button = self.locator_with_fallbacks(
            "finish checkout button",
            "[data-test='finish']",
            "#finish",
            "button:has-text('Finish')",
        )
        self.error_banner = self.locator_with_fallbacks(
            "checkout error banner",
            "[data-test='error']",
            ".error-message-container",
            "h3:has-text('Error:')",
        )
        self.complete_header = self.locator_with_fallbacks(
            "checkout complete header",
            "[data-test='complete-header']",
            ".complete-header",
            "h2:has-text('Thank you')",
        )
        self.summary_total = self.locator_with_fallbacks(
            "checkout summary total",
            "[data-test='total-label']",
            ".summary_total_label",
        )

    def fill_information(
        self,
        first_name: str,
        last_name: str,
        postal_code: str,
    ) -> None:
        self.fill(self.first_name_input, first_name, "first name")
        self.fill(self.last_name_input, last_name, "last name")
        self.fill(self.postal_code_input, postal_code, "postal code")

    def continue_to_overview(self) -> None:
        self.click(self.continue_button, "continue checkout")

    def finish_order(self) -> None:
        self.click(self.finish_button, "finish checkout")

    def get_error_message(self) -> str:
        return self.text(self.error_banner, "checkout error message")

    def get_complete_message(self) -> str:
        return self.text(self.complete_header, "checkout complete message")

    def is_overview_displayed(self) -> bool:
        expect(self.resolve(self.summary_total)).to_be_visible()
        return True
