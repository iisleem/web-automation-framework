import allure
from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.username_input = self.locator_with_fallbacks(
            "username input",
            "[data-test='username']",
            "#user-name",
            "input[name='user-name']",
        )
        self.password_input = self.locator_with_fallbacks(
            "password input",
            "[data-test='password']",
            "#password",
            "input[name='password']",
        )
        self.login_button = self.locator_with_fallbacks(
            "login button",
            "[data-test='login-button']",
            "#login-button",
            "input[type='submit']",
        )
        self.error_banner = self.locator_with_fallbacks(
            "login error banner",
            "[data-test='error']",
            ".error-message-container",
            "h3:has-text('Epic sadface')",
        )

    def open(self, base_url: str) -> None:
        self.goto(base_url)

    def login(self, username: str, password: str) -> None:
        with allure.step(f"Log in as {username}"):
            self.fill(self.username_input, username, "username")
            self.fill(self.password_input, password, "password")
            self.click(self.login_button, "login button")

    def get_error_message(self) -> str:
        return self.text(self.error_banner, "login error message")

    def is_error_visible(self) -> bool:
        error_banner = self.resolve(self.error_banner)
        expect(error_banner).to_be_visible()
        return error_banner.is_visible()
