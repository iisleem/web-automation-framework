import pytest

from flows.saucedemo import saucedemo_flows


pytestmark = pytest.mark.helpers


class FakeLoginPage:
    events = []

    def __init__(self, page):
        self.page = page

    def open(self, base_url):
        self.events.append(("open", base_url))

    def login(self, username, password):
        self.events.append(("login", username, password))


class FakeInventoryPage:
    events = []

    def __init__(self, page):
        self.page = page

    def is_loaded(self):
        self.events.append(("inventory_loaded",))
        return True

    def add_product_to_cart(self, product_name):
        self.events.append(("add_product", product_name))

    def open_cart(self):
        self.events.append(("open_cart",))


class FakeCartPage:
    events = []

    def __init__(self, page):
        self.page = page

    def checkout(self):
        self.events.append(("checkout",))


class FakeCheckoutPage:
    events = []

    def __init__(self, page):
        self.page = page

    def fill_information(self, first_name, last_name, postal_code):
        self.events.append(("fill_information", first_name, last_name, postal_code))

    def continue_to_overview(self):
        self.events.append(("continue_to_overview",))

    def is_overview_displayed(self):
        self.events.append(("overview_displayed",))
        return True

    def finish_order(self):
        self.events.append(("finish_order",))


@pytest.fixture(autouse=True)
def patch_pages(monkeypatch):
    for fake_class in (FakeLoginPage, FakeInventoryPage, FakeCartPage, FakeCheckoutPage):
        fake_class.events = []

    monkeypatch.setattr(saucedemo_flows, "LoginPage", FakeLoginPage)
    monkeypatch.setattr(saucedemo_flows, "InventoryPage", FakeInventoryPage)
    monkeypatch.setattr(saucedemo_flows, "CartPage", FakeCartPage)
    monkeypatch.setattr(saucedemo_flows, "CheckoutPage", FakeCheckoutPage)


def test_login_as_opens_url_and_logs_in():
    inventory_page = saucedemo_flows.login_as(
        page="page",
        base_url="https://www.saucedemo.com/",
        user={"username": "standard_user", "password": "secret_sauce"},
    )

    assert isinstance(inventory_page, FakeInventoryPage)
    assert FakeLoginPage.events == [
        ("open", "https://www.saucedemo.com/"),
        ("login", "standard_user", "secret_sauce"),
    ]
    assert FakeInventoryPage.events == [("inventory_loaded",)]


def test_add_product_and_open_cart_returns_cart_page():
    cart_page = saucedemo_flows.add_product_and_open_cart(
        page="page",
        base_url="https://www.saucedemo.com/",
        user={"username": "standard_user", "password": "secret_sauce"},
        product_name="Sauce Labs Backpack",
    )

    assert isinstance(cart_page, FakeCartPage)
    assert ("add_product", "Sauce Labs Backpack") in FakeInventoryPage.events
    assert ("open_cart",) in FakeInventoryPage.events


def test_start_checkout_for_product_clicks_checkout():
    checkout_page = saucedemo_flows.start_checkout_for_product(
        page="page",
        base_url="https://www.saucedemo.com/",
        user={"username": "standard_user", "password": "secret_sauce"},
        product_name="Sauce Labs Backpack",
    )

    assert isinstance(checkout_page, FakeCheckoutPage)
    assert FakeCartPage.events == [("checkout",)]


def test_submit_checkout_information_fills_customer_data():
    checkout_page = FakeCheckoutPage("page")

    result = saucedemo_flows.submit_checkout_information(
        checkout_page,
        {"first_name": "Alex", "last_name": "Morgan", "postal_code": "10001"},
    )

    assert result == checkout_page
    assert FakeCheckoutPage.events == [
        ("fill_information", "Alex", "Morgan", "10001"),
        ("continue_to_overview",),
    ]


def test_checkout_product_completes_order():
    checkout_page = saucedemo_flows.checkout_product(
        page="page",
        base_url="https://www.saucedemo.com/",
        user={"username": "standard_user", "password": "secret_sauce"},
        product_name="Sauce Labs Bike Light",
        customer={"first_name": "Alex", "last_name": "Morgan", "postal_code": "10001"},
    )

    assert isinstance(checkout_page, FakeCheckoutPage)
    assert ("overview_displayed",) in FakeCheckoutPage.events
    assert ("finish_order",) in FakeCheckoutPage.events
