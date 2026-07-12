# Framework Helpers Catalog

Reusable helpers for common web automation tasks. Each helper is designed to be small, explicit, and safe to use in tests without hiding real product issues.

## Search

Open this file in a browser or editor and use search for helper names, tags, or categories. For a browser-native searchable catalog, open:

```text
docs/helpers_catalog.html
```

## Helper Index

| Helper | Category | Tags | Description |
| --- | --- | --- | --- |
| `EmailOtpHelper.get_latest_otp` | Email | otp, imap, email, verification | Reads the latest OTP from an email that matches sender and/or subject filters. |
| `EmailOtpHelper.wait_for_otp` | Email | otp, wait, polling, email | Polls email until an OTP arrives or timeout is reached. |
| `ImapEmailClient.find_latest_email` | Email | imap, inbox, email | Reads latest email by sender and/or subject. |
| `wait_until` | Wait | polling, retry, timeout | Repeats a condition until it returns a truthy value or times out. |
| `extract_otp` | Text | otp, regex, parsing | Extracts the first OTP-like value from text. |
| `extract_first_match` | Text | regex, parsing | Extracts the first regex match or first capture group. |
| `extract_numbers` | Text | numbers, parsing | Returns all numeric groups from text. |
| `normalize_text` | Text | cleanup, string | Collapses repeated whitespace for stable text comparisons. |
| `random_email` | Data | test data, email, random | Generates unique email addresses for test data. |
| `random_username` | Data | test data, user, random | Generates random usernames. |
| `random_phone` | Data | test data, phone, random | Generates random phone numbers. |
| `unique_id` | Data | id, unique, random | Generates short unique IDs with a prefix. |
| `timestamped_value` | Data | timestamp, unique | Generates timestamped values for stable uniqueness. |
| `wait_for_file` | Files | download, file, wait | Waits for a file matching a glob pattern. |
| `assert_file_exists` | Files | file, assertion | Asserts that a path exists and is a file. |
| `assert_file_extension` | Files | file, extension, assertion | Asserts file extension. |
| `cleanup_directory` | Files | cleanup, download | Recreates an empty directory. |
| `save_storage_state` | Browser | session, cookies, storage | Saves Playwright browser storage state. |
| `read_storage_state` | Browser | session, json | Reads saved Playwright storage state. |
| `clear_browser_storage` | Browser | cookies, local storage, session | Clears local storage, session storage, and cookies. |
| `set_local_storage_item` | Browser | local storage | Sets a local storage item. |
| `get_local_storage_item` | Browser | local storage | Reads a local storage item. |
| `create_authenticated_state`, `new_context_with_storage` | Auth | auth, session, storage state | Creates and reuses authenticated browser storage state. |
| `assert_storage_state_has_cookies`, `assert_storage_state_has_origin` | Auth | auth, assertion, cookies | Validates saved authenticated session state. |
| `ApiClient` | API | api, setup, cleanup | Lightweight API client for setup, cleanup, and hybrid UI/API tests. |
| `assert_status_code` | API | api, assertion | Asserts API response status code. |
| `assert_json_field` | API | api, json, assertion | Asserts nested JSON response fields. |
| `today`, `tomorrow`, `yesterday` | Date/Time | date, timezone | Returns relative dates, optionally timezone-aware. |
| `add_days`, `format_date`, `parse_date` | Date/Time | date, formatting | Date arithmetic, formatting, and parsing helpers. |
| `build_url` | URL | query, navigation | Builds a URL with path and query parameters. |
| `parse_query_params`, `get_query_param` | URL | query, assertion | Reads query parameters from URLs. |
| `assert_url_contains_param` | URL | query, assertion | Asserts a URL contains a query parameter and optional value. |
| `remove_query_param` | URL | query, cleanup | Removes a query parameter from a URL. |
| `require_env`, `optional_env` | Environment | env, secrets | Reads required or optional environment variables. |
| `validate_required_envs` | Environment | env, validation | Validates a list of required environment variables. |
| `mask_secret` | Environment | secrets, logging | Masks secret values for safer logging. |
| `read_csv_file`, `assert_csv_headers`, `assert_csv_row_count` | Files | csv, validation | Reads and validates CSV files. |
| `read_json_file`, `assert_json_file_field` | Files | json, validation | Reads and validates JSON files. |
| `normalize_table_rows`, `find_row_by_cell_text` | Table | table, grid | Normalizes table rows and finds a row by text. |
| `assert_table_contains_row`, `assert_column_sorted` | Table | table, assertion | Validates table content and sorting. |
| `extract_table_rows` | Table | playwright, table | Extracts rows from a Playwright table locator. |
| `wait_for_response`, `assert_response_status` | Network | response, api, wait | Waits for matching Playwright network responses and validates status. |
| `start_failed_request_tracking`, `assert_no_failed_requests` | Network | requestfailed, monitoring | Tracks failed browser requests and asserts the page had no unexpected failures. |
| `block_resources`, `mock_response` | Network | route, mock, performance | Blocks resource types or mocks browser network responses. |
| `wait_for_download`, `save_download` | File Transfer | download, export | Waits for Playwright downloads and saves them to a controlled directory. |
| `assert_download_filename`, `assert_download_extension` | File Transfer | download, assertion | Validates downloaded filenames and extensions. |
| `create_upload_file`, `set_input_files` | File Transfer | upload, file input | Creates upload fixtures and sets files on page or locator inputs. |
| `step`, `attach_json`, `attach_text`, `attach_file` | Allure Debug | allure, attachment, reporting | Adds reusable Allure steps and attachments. |
| `attach_page_url`, `attach_html_snapshot` | Allure Debug | page, html, debug | Attaches current page URL and HTML snapshot for debugging. |
| `start_console_tracking`, `assert_no_console_errors` | Console | console, pageerror, debug | Tracks browser console warnings/errors and page errors. |
| `filter_console_entries` | Console | console, filtering | Filters captured console entries by level or text. |
| `fill_form`, `FormField` | Forms | form, input, checkbox, select | Fills forms from simple maps or explicit field definitions. |
| `clear_fields`, `assert_field_value`, `assert_validation_message` | Forms | form, assertion, validation | Clears fields and validates field values or messages. |
| `press_key`, `tab_to_next`, `shift_tab_to_previous` | Keyboard | keyboard, focus, accessibility | Sends keyboard actions for focus and accessibility workflows. |
| `focus_element`, `assert_focused`, `assert_focus_order` | Keyboard | focus, tab order, assertion | Focuses elements and validates keyboard tab order. |
| `get_active_element_text`, `assert_active_element_text` | Keyboard | active element, assertion | Reads and validates the currently focused element text. |
| `CleanupRegistry`, `assert_cleanup_success` | Cleanup | cleanup, teardown, test data | Registers cleanup actions and validates teardown results. |
| `wait_for_notification`, `assert_notification_visible` | Notifications | toast, snackbar, alert | Waits for and validates toast, alert, snackbar, or notification UI. |
| `assert_notification_hidden`, `dismiss_notification` | Notifications | dismiss, hidden, toast | Dismisses notifications and validates they disappear. |
| `SoftAssert`, `soft_assert` | Assertions | soft assertion, grouped failures | Collects assertion failures and reports them together at the end. |
| `get_cookie`, `set_cookie`, `delete_cookie` | Cookies | cookie, session | Reads, creates, and deletes browser cookies. |
| `assert_cookie_exists`, `assert_cookie_value` | Cookies | cookie, assertion | Validates cookie existence, value, and attributes. |
| `copy_cookies` | Cookies | session, reuse | Copies cookies between Playwright contexts or pages. |
| `assert_page_title`, `assert_html_lang` | Accessibility | a11y, title, lang | Runs lightweight accessibility smoke checks for title and document language. |
| `assert_heading_visible`, `assert_images_have_alt_text` | Accessibility | a11y, heading, alt text | Validates headings and image alt text. |
| `assert_element_accessible_name` | Accessibility | a11y, accessible name | Checks elements are reachable by role and accessible name. |
| `capture_page_screenshot`, `capture_element_screenshot` | Visual | screenshot, allure | Captures page or element screenshots with optional masks and Allure attachment. |
| `assert_screenshot_matches_baseline` | Visual | baseline, comparison | Compares screenshots with byte-level baselines or updates baselines. |
| `login_as`, `add_product_and_open_cart` | SauceDemo Flows | business flow, login, cart | Reusable SauceDemo login and cart business flows. |
| `checkout_product`, `start_checkout_for_product` | SauceDemo Flows | business flow, checkout | Reusable SauceDemo checkout flows. |

## Email OTP Helpers

### Configuration

Email configuration lives in `config/settings.yaml`:

```yaml
email:
  provider: imap
  host: imap.gmail.com
  port: 993
  use_ssl: true
  username_env: TEST_EMAIL_USERNAME
  password_env: TEST_EMAIL_PASSWORD
  mailbox: INBOX
  default_otp_regex: "\\b\\d{4,8}\\b"
```

Set credentials through environment variables:

```bash
export TEST_EMAIL_USERNAME="automation@example.com"
export TEST_EMAIL_PASSWORD="app-password-or-secret"
```

Never hardcode email passwords in repository files.

### `EmailOtpHelper.get_latest_otp`

Gets the latest OTP from the newest matching email.

```python
def test_otp(email_otp_helper):
    otp = email_otp_helper.get_latest_otp(
        sender="no-reply@example.com",
        subject_contains="Verification Code",
        regex=r"\\b\\d{6}\\b",
    )

    assert otp is not None
```

### `EmailOtpHelper.wait_for_otp`

Polls email until an OTP is found.

```python
def test_wait_for_otp(email_otp_helper):
    otp = email_otp_helper.wait_for_otp(
        sender="security@example.com",
        subject_contains="Your login code",
        regex=r"\\b\\d{6}\\b",
        timeout_seconds=60,
        interval_seconds=5,
    )

    assert len(otp) == 6
```

### Direct Client Usage

```python
def test_latest_email(email_client):
    message = email_client.find_latest_email(
        sender="billing@example.com",
        subject_contains="Invoice",
    )

    assert message is not None
    assert "Invoice" in message.subject
```

## Wait Helpers

### `wait_until`

Use when a non-Playwright system needs polling, such as email, files, APIs, async jobs, or database state.

```python
from utils.helpers.wait import wait_until


token = wait_until(
    lambda: get_token_if_ready(),
    timeout_seconds=30,
    interval_seconds=2,
    failure_message="Token was not generated.",
)
```

Do not use this for normal browser element waits. Prefer Playwright locators and `expect()` for UI waits.

## Text Helpers

### `extract_otp`

```python
from utils.helpers.text import extract_otp


otp = extract_otp("Your verification code is 482913")
assert otp == "482913"
```

### `extract_first_match`

```python
from utils.helpers.text import extract_first_match


order_id = extract_first_match("Order ID: ORD-12345", r"Order ID: ([A-Z]+-\\d+)")
assert order_id == "ORD-12345"
```

### `extract_numbers`

```python
from utils.helpers.text import extract_numbers


numbers = extract_numbers("Total: $42. Tax: $3")
assert numbers == ["42", "3"]
```

### `normalize_text`

```python
from utils.helpers.text import normalize_text


assert normalize_text("Hello   automation\nteam") == "Hello automation team"
```

## Test Data Generators

Use these helpers when tests need unique but readable values.

```python
from utils.helpers.data import (
    random_email,
    random_phone,
    random_username,
    timestamped_value,
    unique_id,
)


email = random_email(domain="example.test", prefix="qa")
username = random_username(prefix="qa")
phone = random_phone(country_code="+962", digits=9)
order_id = unique_id("order")
run_name = timestamped_value("run")
```

## File Helpers

Useful for download flows and generated-file validations.

```python
from utils.helpers.files import (
    assert_file_exists,
    assert_file_extension,
    cleanup_directory,
    wait_for_file,
)


cleanup_directory("downloads")
downloaded_file = wait_for_file("downloads", pattern="*.pdf", timeout_seconds=30)
assert_file_exists(downloaded_file)
assert_file_extension(downloaded_file, "pdf")
```

## File Transfer Helpers

Use these helpers for browser download and upload scenarios.

```python
from utils.helpers.file_transfer import (
    assert_download_extension,
    assert_download_filename,
    assert_file_contains,
    create_upload_file,
    set_input_files,
    wait_for_download,
)


download_path = wait_for_download(
    page,
    lambda: page.get_by_role("button", name="Export").click(),
    downloads_dir="downloads",
)
assert_download_filename(download_path, "orders.csv")
assert_download_extension(download_path, ".csv")
assert_file_contains(download_path, "order_id")

upload_path = create_upload_file("uploads", "profile.txt", "Automation profile")
set_input_files(page, "input[type=file]", upload_path)
```

Use locator-based upload when the test already has a file input locator:

```python
file_input = page.locator("[data-test='document-upload']")
set_input_files(file_input, upload_path)
```

## Browser Storage Helpers

Use these helpers to save and reuse authenticated sessions, manage local storage, or clean browser state.

```python
from utils.helpers.browser import (
    clear_browser_storage,
    get_local_storage_item,
    save_storage_state,
    set_local_storage_item,
)


save_storage_state(page, "data/auth_state.json")
set_local_storage_item(page, "featureFlag", "enabled")
assert get_local_storage_item(page, "featureFlag") == "enabled"
clear_browser_storage(page)
```

Playwright can reuse a saved storage state:

```python
context = browser.new_context(storage_state="data/auth_state.json")
```

## Auth Session Helpers

Use auth session helpers when a suite should log in once, save Playwright storage state, and reuse that state in later tests.

```python
from utils.helpers.auth import (
    assert_storage_state_has_cookies,
    create_authenticated_state,
    new_context_with_storage,
)


state_path = create_authenticated_state(
    page,
    "data/auth/standard_user.json",
    login_action=lambda page: login_page.login(
        users["standard_user"]["username"],
        users["standard_user"]["password"],
    ),
    verify_action=lambda page: inventory_page.assert_products_page_loaded(),
)

assert_storage_state_has_cookies(state_path)

context = new_context_with_storage(
    browser,
    state_path,
    viewport={"width": 1280, "height": 720},
)
authenticated_page = context.new_page()
```

For shared suites, keep storage state files out of git if they contain live session cookies.

## Cookie Helpers

Use cookie helpers for session assertions, feature flags, and copying state between contexts.

```python
from utils.helpers.cookies import (
    assert_cookie_attribute,
    assert_cookie_exists,
    assert_cookie_value,
    copy_cookies,
    delete_cookie,
    set_cookie,
)


set_cookie(
    page,
    name="feature_flag",
    value="checkout_v2",
    url="https://www.saucedemo.com/",
)
assert_cookie_exists(page, "feature_flag")
assert_cookie_value(page, "feature_flag", "checkout_v2")
assert_cookie_attribute(page, "feature_flag", "sameSite", "Lax")
delete_cookie(page, "feature_flag")
```

Copy cookies from one context to another:

```python
copy_cookies(source_page, target_context)
```

## API Helpers

Use API helpers for test setup, cleanup, and hybrid UI/API scenarios.

```python
from utils.helpers.api import ApiClient, assert_json_field, assert_status_code


api = ApiClient(
    base_url="https://api.example.com",
    default_headers={"Authorization": "Bearer token"},
)

response = api.get("/users/1")
assert_status_code(response, 200)
assert_json_field(response, "user.name", "Alex")
```

## Network Helpers

Use network helpers when the UI flow must wait for a backend response, validate browser-side API behavior, monitor failed requests, or stub expensive resources.

```python
from utils.helpers.network import (
    assert_no_failed_requests,
    assert_response_json_field,
    assert_response_status,
    block_resources,
    mock_response,
    start_failed_request_tracking,
    wait_for_response,
)


tracker = start_failed_request_tracking(
    page,
    ignored_url_patterns=["*analytics*", "*fonts*"],
)

response = wait_for_response(
    page,
    url_contains="/api/orders",
    status=201,
    method="POST",
    trigger=lambda: page.get_by_role("button", name="Submit").click(),
)
assert_response_status(response, 201)
assert_response_json_field(response, "order.status", "created")
tracker.assert_no_failures()
```

Block nonessential resources to speed up tests:

```python
block_resources(page, resource_types=("image", "font", "media"))
```

Mock a browser network response:

```python
mock_response(
    page,
    "**/api/feature-flags",
    body='{"checkoutV2": true}',
)
```

## Allure Debug Helpers

Use these helpers to make reports richer without duplicating attachment code in every test.

```python
from utils.helpers.allure_debug import (
    attach_html_snapshot,
    attach_json,
    attach_page_url,
    attach_text,
    step,
)


with step("Create order through UI"):
    checkout_page.finish_order()

attach_json({"order_id": "ORD-123"}, name="created order")
attach_text("Useful debug note", name="debug note")
attach_page_url(page)
attach_html_snapshot(page)
```

Attach an existing file:

```python
from utils.helpers.allure_debug import attach_file


attach_file("downloads/orders.csv", name="exported orders")
```

## Console Helpers

Use console helpers to catch hidden frontend problems during UI tests.

```python
from utils.helpers.console import start_console_tracking


tracker = start_console_tracking(
    page,
    ignored_text_patterns=["*ResizeObserver*"],
)

page.goto(base_url)
# test actions...
tracker.assert_no_errors()
```

Filter captured entries when a test wants to assert a specific message:

```python
from utils.helpers.console import filter_console_entries


api_errors = filter_console_entries(
    tracker.entries,
    levels=("error",),
    text_contains="/api/orders",
)
```

## Form Helpers

Use form helpers for common input, checkbox, select, upload, and validation flows.

```python
from utils.helpers.forms import (
    FormField,
    assert_field_value,
    assert_validation_message,
    fill_form,
    submit_and_wait_for_url,
)


fill_form(
    page,
    {
        "[data-test='firstName']": "Alex",
        "[data-test='lastName']": "Tester",
    },
)

fill_form(
    page,
    [
        FormField("[data-test='acceptTerms']", True, "checkbox"),
        FormField("[data-test='country']", "JO", "select"),
    ],
)

assert_field_value(page, "[data-test='firstName']", "Alex")
submit_and_wait_for_url(page, "[data-test='submit']", "/complete")
```

Validation example:

```python
assert_validation_message(
    page,
    "[data-test='error']",
    "First name is required",
)
```

## Keyboard And Focus Helpers

Use keyboard helpers for accessibility checks, keyboard-only flows, and focus assertions.

```python
from utils.helpers.keyboard import (
    assert_active_element_text,
    assert_focus_order,
    assert_focused,
    focus_element,
    press_key,
    tab_to_next,
)


focus_element(page, "[data-test='username']")
assert_focused(page, "[data-test='username']")

press_key(page, "Enter")
tab_to_next(page)

assert_focus_order(
    page,
    [
        "[data-test='username']",
        "[data-test='password']",
        "[data-test='login-button']",
    ],
)
assert_active_element_text(page, "Login")
```

Use Playwright locator assertions for normal visibility/clickability checks. Use these helpers when the scenario specifically cares about keyboard behavior or focused elements.

## Cleanup Registry Helpers

Use cleanup registry helpers when a test creates external data and needs reliable teardown steps.

```python
from utils.helpers.cleanup import CleanupRegistry, assert_cleanup_success


cleanup = CleanupRegistry()

order = api.create_order()
cleanup.add("delete order", api.delete_order, order["id"])

user = api.create_user()
cleanup.add("delete user", api.delete_user, user["id"])

try:
    run_ui_scenario(user, order)
finally:
    results = cleanup.run_all()
    assert_cleanup_success(results)
```

Cleanup actions run in reverse order by default. That is useful when a test creates parent/child data and child resources should be removed before parent resources.

## Notification Helpers

Use notification helpers for toast, snackbar, alert, and status-message workflows.

```python
from utils.helpers.notifications import (
    assert_notification_hidden,
    assert_notification_visible,
    dismiss_notification,
)


page.get_by_role("button", name="Save").click()
assert_notification_visible(page, "Saved successfully")

dismiss_notification(
    page,
    dismiss_selector="[data-test='toast-close']",
    notification_selector="[data-test='toast']",
)
assert_notification_hidden(page, selector="[data-test='toast']")
```

The default selector covers common toast, alert, snackbar, and notification patterns. Pass a project-specific selector when the app has stable `data-test` attributes.

## Soft Assertion Helpers

Use soft assertions when one test should collect several related validation failures before failing.

```python
from utils.helpers.soft_assertions import soft_assert


softly = soft_assert()

softly.assert_equal(summary.total, "$39.98", "Cart total mismatch")
softly.assert_contains(summary.customer_name, "Alex")
softly.assert_true(summary.confirm_button_enabled, "Confirm button should be enabled")

softly.assert_all()
```

Use hard assertions for critical preconditions where the rest of the test cannot continue safely.

## Accessibility Smoke Helpers

These helpers are lightweight smoke checks. They do not replace a full accessibility scanner, but they catch common issues quickly.

```python
from utils.helpers.accessibility import (
    assert_element_accessible_name,
    assert_heading_visible,
    assert_html_lang,
    assert_images_have_alt_text,
    assert_minimum_heading_count,
    assert_page_title,
)


assert_page_title(page, "Swag Labs")
assert_html_lang(page, "en")
assert_heading_visible(page, "Products", level=1)
assert_minimum_heading_count(page, 1)
assert_images_have_alt_text(page)
assert_element_accessible_name(page, "button", "Add to cart")
```

## Visual Helpers

Use visual helpers to capture screenshots consistently and compare them to simple byte-level baselines.

```python
from utils.helpers.visual import (
    assert_screenshot_created,
    assert_screenshot_matches_baseline,
    capture_element_screenshot,
    capture_page_screenshot,
    screenshot_path,
)


path = screenshot_path("screenshots/visual", "checkout_complete_chromium")
capture_page_screenshot(
    page,
    path,
    full_page=True,
    mask=[page.locator("[data-test='dynamic-banner']")],
    attach_to_allure=True,
)
assert_screenshot_created(path)
assert_screenshot_matches_baseline(
    path,
    "screenshots/baselines/checkout_complete_chromium.png",
)
```

Element screenshot example:

```python
capture_element_screenshot(
    page.locator("[data-test='inventory-list']"),
    "screenshots/visual/inventory_list.png",
)
```

The baseline comparison is intentionally simple and dependency-free. For advanced visual diffing, add a dedicated image comparison library and keep the helper API stable.

## SauceDemo Business Flows

Business flows live under `flows/` because they are product-specific. Keep reusable technical helpers under `utils/helpers/`, and keep application workflow shortcuts under `flows/`.

```python
from flows.saucedemo import checkout_product, login_as


inventory_page = login_as(page, base_url, users["standard_user"])

checkout_page = checkout_product(
    page,
    base_url,
    users["standard_user"],
    "Sauce Labs Bike Light",
    checkout_data["valid_customer"],
)
```

Available SauceDemo flows:

- `login_as`
- `add_product_and_open_cart`
- `start_checkout_for_product`
- `submit_checkout_information`
- `checkout_product`

## Date / Time Helpers

```python
from utils.helpers.date_time import add_days, format_date, parse_date, today, tomorrow


current = today("UTC")
next_week = add_days(current, 7)
assert format_date(next_week) == format_date(parse_date(format_date(next_week)))
assert tomorrow("UTC") == add_days(current, 1)
```

## URL Helpers

```python
from utils.helpers.url import build_url, assert_url_contains_param, get_query_param


url = build_url("https://example.com", "search", {"q": "automation", "page": 1})
assert_url_contains_param(url, "q", "automation")
assert get_query_param(url, "page") == "1"
```

## Environment / Secrets Helpers

```python
from utils.helpers.env import mask_secret, require_env, validate_required_envs


token = require_env("API_TOKEN")
print(mask_secret(token))
validate_required_envs(["API_TOKEN", "TEST_EMAIL_USERNAME"])
```

## CSV / JSON Validation Helpers

```python
from utils.helpers.files import (
    assert_csv_headers,
    assert_csv_row_count,
    assert_json_file_field,
    read_csv_file,
)


rows = read_csv_file("downloads/users.csv")
assert_csv_headers("downloads/users.csv", ["id", "name"])
assert_csv_row_count("downloads/users.csv", 10)
assert_json_file_field("downloads/user.json", "user.name", "Alex")
```

## Table Helpers

Use table helpers for admin grids, reports, product tables, and dashboards.

```python
from utils.helpers.table import (
    assert_column_sorted,
    assert_table_contains_row,
    extract_table_rows,
)


rows = extract_table_rows(page.locator("table"))
assert_table_contains_row(rows, ["Sauce Labs Backpack", "$29.99"])
assert_column_sorted(rows[1:], column_index=0)
```

## Design Rules For New Helpers

- Keep helpers small and focused.
- Do not hardcode credentials or environment-specific secrets.
- Prefer config and environment variables for integrations.
- Return useful values instead of asserting inside helpers, unless the helper is explicitly an assertion helper.
- Raise clear errors with enough context.
- Document every new helper in this file.
- Add a simple example for each helper.
- Keep business-domain helpers separate from low-level utilities when the library grows.
