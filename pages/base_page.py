from pathlib import Path

import allure
from playwright.sync_api import Error, Locator, Page, TimeoutError, expect

from utils.config_reader import ConfigReader
from utils.logger import get_logger
from utils.runtime_healing import attempt_runtime_healing, runtime_healing_settings
from utils.self_healing import LocatorCandidate


LOGGER = get_logger("self-healing")


class HealingLocator:
    def __init__(
        self,
        page: Page,
        description: str,
        candidates: list[LocatorCandidate],
        enabled: bool,
        timeout_ms: int,
    ) -> None:
        self.page = page
        self.description = description
        self.candidates = candidates
        self.enabled = enabled
        self.timeout_ms = timeout_ms

    def resolve(self) -> Locator:
        primary = self.page.locator(self.candidates[0].selector)
        if not self.enabled or len(self.candidates) == 1:
            return primary

        for index, candidate in enumerate(self.candidates):
            locator = self.page.locator(candidate.selector)
            try:
                locator.first.wait_for(state="attached", timeout=self.timeout_ms)
                if index > 0:
                    _log_healing_event(self.description, self.candidates[0], candidate)
                return locator
            except (TimeoutError, Error):
                continue

        return primary

    def __getattr__(self, name: str):
        return getattr(self.resolve(), name)


class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self._settings = ConfigReader(self.project_path()).read_settings()
        self._self_healing_config = self._settings.get("self_healing", {})
        self._runtime_healing = runtime_healing_settings(self._settings, self.project_path())

    def goto(self, url: str) -> None:
        with allure.step(f"Open URL: {url}"):
            self.page.goto(url)

    def click(self, locator: Locator | HealingLocator, description: str) -> None:
        with allure.step(f"Click {description}"):
            self._run_locator_action(
                locator,
                description,
                "click",
                lambda resolved: resolved.click(),
            )

    def fill(self, locator: Locator | HealingLocator, value: str, description: str) -> None:
        with allure.step(f"Fill {description}"):
            self._run_locator_action(
                locator,
                description,
                "fill",
                lambda resolved: resolved.fill(value),
            )

    def text(self, locator: Locator | HealingLocator, description: str) -> str:
        with allure.step(f"Read text from {description}"):
            return self._run_locator_action(
                locator,
                description,
                "text",
                lambda resolved: resolved.inner_text(),
            )

    def select(self, locator: Locator | HealingLocator, value: str, description: str) -> None:
        with allure.step(f"Select {description}: {value}"):
            self._run_locator_action(
                locator,
                description,
                "select",
                lambda resolved: resolved.select_option(value),
            )

    def expect_visible(self, locator: Locator | HealingLocator, description: str) -> None:
        with allure.step(f"Verify {description} is visible"):
            self._run_locator_action(
                locator,
                description,
                "expect_visible",
                lambda resolved: expect(resolved).to_be_visible(),
            )

    def locator(self, selector: str, description: str) -> Locator:
        return self.page.locator(selector)

    def locator_with_fallbacks(
        self,
        description: str,
        primary_selector: str,
        *fallback_selectors: str | LocatorCandidate,
    ) -> HealingLocator:
        candidates = [
            LocatorCandidate(primary_selector, f"{description} primary locator"),
            *[
                fallback
                if isinstance(fallback, LocatorCandidate)
                else LocatorCandidate(fallback, f"{description} fallback locator")
                for fallback in fallback_selectors
            ],
        ]
        return HealingLocator(
            self.page,
            description,
            candidates,
            self._is_self_healing_enabled(),
            self._self_healing_timeout_ms(),
        )

    def resolve(self, locator: Locator | HealingLocator) -> Locator:
        if isinstance(locator, HealingLocator):
            return locator.resolve()
        return locator

    def _run_locator_action(
        self,
        locator: Locator | HealingLocator,
        description: str,
        action: str,
        runner,
    ):
        try:
            return runner(self.resolve(locator))
        except Exception as error:
            if not isinstance(locator, HealingLocator):
                raise
            return attempt_runtime_healing(
                page=self.page,
                description=description,
                primary=locator.candidates[0],
                action=action,
                action_runner=runner,
                settings=self._runtime_healing,
                original_error=error,
            )

    def _resolve_locator(
        self,
        description: str,
        candidates: list[LocatorCandidate],
    ) -> Locator:
        primary = self.page.locator(candidates[0].selector)
        if not self._is_self_healing_enabled() or len(candidates) == 1:
            return primary

        timeout_ms = self._self_healing_timeout_ms()
        for index, candidate in enumerate(candidates):
            locator = self.page.locator(candidate.selector)
            try:
                locator.first.wait_for(state="attached", timeout=timeout_ms)
                if index > 0:
                    _log_healing_event(description, candidates[0], candidate)
                return locator
            except (TimeoutError, Error):
                continue

        return primary

    def attach_screenshot(self, name: str) -> None:
        screenshot = self.page.screenshot(full_page=True)
        allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)

    @staticmethod
    def normalize_url(base_url: str, path: str = "") -> str:
        return f"{base_url.rstrip('/')}/{path.lstrip('/')}"

    @staticmethod
    def project_path(*parts: str) -> Path:
        return Path(__file__).resolve().parents[1].joinpath(*parts)

    def _is_self_healing_enabled(self) -> bool:
        return bool(self._self_healing_config.get("enabled", False))

    def _self_healing_timeout_ms(self) -> int:
        return int(self._self_healing_config.get("timeout_ms", 1500))


def _log_healing_event(
    description: str,
    primary: LocatorCandidate,
    healed: LocatorCandidate,
) -> None:
    message = (
        f"Self-healing locator used for '{description}'. "
        f"Primary failed: {primary.selector}. Healed with: {healed.selector}"
    )
    LOGGER.warning(message)
    with allure.step(message):
        allure.attach(
            f"Description: {description}\n"
            f"Primary: {primary.selector}\n"
            f"Fallback: {healed.selector}\n"
            f"Fallback description: {healed.description}",
            name="self-healing locator event",
            attachment_type=allure.attachment_type.TEXT,
        )
