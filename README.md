# Web Automation Framework User Guide

[![Python Playwright Tests](https://github.com/iisleem/web-automation-framework/actions/workflows/playwright-tests.yml/badge.svg)](https://github.com/iisleem/web-automation-framework/actions/workflows/playwright-tests.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/playwright-python-2EAD33.svg)](https://playwright.dev/python/)
[![Pytest](https://img.shields.io/badge/tested%20with-pytest-0A9EDC.svg)](https://pytest.org/)
[![Reports](https://img.shields.io/badge/reports-Core%20Product%20%2B%20Allure-2EAD33.svg)](https://github.com/iisleem/automation-core)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Python web automation framework built with Playwright, Pytest, pytest-playwright, Page Object Model, automation-core product reporting, optional official Allure reporting, retry support, parallel execution, and GitHub Actions CI.

The included demo application is [SauceDemo](https://www.saucedemo.com/).

## What This Framework Gives You

- Clean Page Object Model with locators kept out of test files
- Pytest fixtures for browser, context, page, config, users, and checkout data
- Unified framework CLI for health checks, test execution, reports, and helper docs
- CLI support for browser, headed/headless mode, environment, base URL, markers, retries, and parallel execution
- Settings-driven browser matrix execution with a main dashboard and drill-down browser reports
- Automatic post-run automation-core product report generation from Allure result files
- Optional official Allure HTML report generation with local CLI install when requested
- Report kind selection: `core`, `allure`, `both`, or `summary`
- Automatic local report opening after test runs, skipped safely in CI/server environments
- Optional self-healing locators and disabled-by-default runtime auto-healing audit/apply modes
- Screenshots, videos, and Playwright traces on failed tests
- Reusable helper library for OTP email, polling, text extraction, and common automation utilities
- JSON test data files for users and checkout data
- YAML environment and framework settings
- Reusable assertions, logging, config reader, data reader, and screenshot helper
- Smoke, regression, e2e, negative, and reporting demo markers
- GitHub Actions workflow for CI

## Project Structure

```text
web-automation-framework/
├── config/
│   ├── settings.yaml              # Timeouts, viewport, artifact folders, retry defaults
│   └── environments.yaml          # Environment names and base URLs
├── data/
│   ├── users.json                 # SauceDemo users
│   └── checkout_data.json         # Checkout form data
├── pages/
│   ├── base_page.py               # Shared page actions
│   ├── login_page.py              # Login page object
│   ├── inventory_page.py          # Products page object
│   ├── cart_page.py               # Cart page object
│   └── checkout_page.py           # Checkout page object
├── flows/
│   └── saucedemo/                 # Reusable SauceDemo business flows
├── tests/
│   ├── smoke/                     # Fast critical tests
│   ├── regression/                # Feature regression tests
│   └── e2e/                       # End-to-end user journeys
├── utils/
│   ├── allure_cli.py              # Auto-installs/locates Allure CLI when official Allure is requested
│   ├── assertions.py              # Reusable assertion helpers
│   ├── config_reader.py           # YAML config reader
│   ├── data_reader.py             # JSON data reader
│   ├── helpers/                   # Reusable automation helper library
│   ├── logger.py                  # Framework logger
│   ├── report_generator.py        # Compatibility wrapper over automation-core report helpers
│   ├── reporting.py               # Web adapter for automation-core reporting
│   ├── runtime_healing.py         # Web adapter for runtime locator healing
│   ├── self_healing.py            # Self-healing locator data model
│   └── screenshot_helper.py       # Screenshot helper
├── scripts/
│   ├── generate_allure_report.py  # Manual report generation helper
│   └── run_browser_matrix.py      # Browser matrix runner and dashboard builder
├── docs/
│   ├── FRAMEWORK_HELPERS.md       # Helper usage guide
│   ├── FEATURE_PARITY.md          # Web baseline and cross-framework parity notes
│   ├── WALKTHROUGH.md             # First-run walkthrough with local report screenshots
│   ├── assets/walkthrough/        # Walkthrough screenshots captured from sample runs
│   └── helpers_catalog.html       # Searchable helper catalog
├── templates/
│   └── starter_project/           # Copyable product suite starter
├── reports/                       # Allure results, automation reports, matrix reports, logs
├── screenshots/                   # Failure screenshots
├── videos/                        # Failure videos
├── traces/                        # Failure Playwright traces
├── .github/workflows/
│   └── playwright-tests.yml       # GitHub Actions pipeline
├── .env.example                   # Safe optional environment variable placeholders
├── conftest.py                    # Pytest hooks and fixtures
├── framework.py                   # Unified framework CLI
├── pyproject.toml                 # Ruff lint configuration
├── pytest.ini                     # Pytest config, markers, Allure results path
├── requirements.txt               # Python dependencies
└── .gitignore
```

## Starter Template

This repository is marked as a GitHub template repository. Use it when starting a new
product-specific web automation suite, then replace the SauceDemo example layers with the
application pages, flows, data, and tests for your product.

A small copyable starter is available under `templates/starter_project/`. It shows the expected
shape for product-owned page objects, flows, tests, and environment configuration without copying
framework internals.

For the shared family guidance behind this layout, see
[Automation Framework Template Strategy](https://github.com/iisleem/automation-core/blob/main/docs/template_strategy.md).

For a first-run guide with screenshots from the sample reports, see
[Web Framework Walkthrough](docs/WALKTHROUGH.md).

## Quick Start

```bash
cd web-automation-framework
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
playwright install
python framework.py doctor
python framework.py run
```

Optional integrations such as email OTP helpers use environment variables. Start from the safe placeholder file when needed:

```bash
cp .env.example .env
```

On Linux CI or a fresh Linux machine, install browser system dependencies:

```bash
playwright install --with-deps
```

## Unified Framework CLI

The easiest entry point is `framework.py`. It wraps the common framework workflows while still allowing direct `pytest` commands whenever you need them.

Check whether the machine is ready:

```bash
python framework.py doctor
```

Run the default green suite:

```bash
python framework.py run
```

Run smoke tests:

```bash
python framework.py run --smoke
```

Run one browser:

```bash
python framework.py run --browser chromium
```

Run headed:

```bash
python framework.py run --headed --browser chromium
```

Run a browser matrix:

```bash
python framework.py run --browsers chromium firefox webkit chrome safari
```

Run browsers in parallel and tests in parallel inside each browser:

```bash
python framework.py run --browsers chromium firefox webkit chrome safari --browser-workers 3 --parallel 2
```

Open the latest report:

```bash
python framework.py report open
```

Generate a report from existing Allure results:

```bash
python framework.py report generate
python framework.py report generate --report-kind both
```

Open the searchable helper catalog:

```bash
python framework.py helpers
```

Print the helper guide path:

```bash
python framework.py helpers --guide
```

Doctor checks include:

- Python version
- Required project files
- YAML config validity
- Python dependency imports
- Playwright browser binaries
- Optional Allure CLI availability
- Writable artifact folders
- Optional email/OTP environment variables

Use strict mode when warnings should fail setup validation:

```bash
python framework.py doctor --strict
```

The default core product report does not require the Allure CLI. If you want official Allure reports with `--report-kind allure` or `--report-kind both`, the framework can auto-install Allure CLI locally. You can also ask doctor to install it early:

```bash
python framework.py doctor --install-allure
```

## Daily Test Commands

Run the default green suite:

```bash
python framework.py run
pytest
```

Run smoke tests:

```bash
python framework.py run --smoke
pytest -m smoke
```

Run regression tests:

```bash
pytest -m regression
```

Run e2e tests:

```bash
pytest -m e2e
```

Run negative tests:

```bash
pytest -m negative
```

Run tests in headed mode:

```bash
python framework.py run --headed
pytest --headed
```

Run a specific browser:

```bash
python framework.py run --browser chromium
python framework.py run --browser chrome
python framework.py run --browser safari
pytest --browser chromium
pytest --browser firefox
pytest --browser webkit
pytest --browser chromium --browser-channel chrome
```

Run the browser matrix from `config/settings.yaml`:

```bash
python framework.py run --matrix
python scripts/run_browser_matrix.py
```

Run a selected browser matrix:

```bash
python framework.py run --browsers chromium chrome safari
python scripts/run_browser_matrix.py --browsers chromium chrome safari
```

Run smoke tests in headed Chromium:

```bash
python framework.py run --smoke --browser chromium --headed
pytest -m smoke --browser chromium --headed
```

Run in parallel:

```bash
python framework.py run --parallel 2
pytest -n 2
```

Retry failures:

```bash
python framework.py run --reruns 2 --reruns-delay 1
pytest --reruns 2 --reruns-delay 1
```

Run one test file:

```bash
pytest tests/smoke/test_login.py
```

Run one test case:

```bash
pytest tests/smoke/test_login.py::test_valid_login
```

Run helper unit tests:

```bash
python framework.py run --helpers --no-generate-report
pytest tests/helpers --no-generate-report
pytest -m helpers --no-generate-report
```

## Pytest CLI Options

| Option | Example | Purpose |
| --- | --- | --- |
| `--env` | `pytest --env qa` | Select an environment from `config/environments.yaml` |
| `--base-url` | `pytest --base-url https://www.saucedemo.com/` | Override the environment base URL |
| `--browser` | `pytest --browser chromium` | Select Playwright engines: `chromium`, `firefox`, or `webkit` |
| `--headed` | `pytest --headed` | Run with visible browser UI |
| `-m` | `pytest -m smoke` | Select tests by marker |
| `-n` | `pytest -n 2` | Run tests in parallel with pytest-xdist |
| `--reruns` | `pytest --reruns 2` | Retry failed tests |
| `--reruns-delay` | `pytest --reruns 2 --reruns-delay 1` | Wait between retries |
| `--run-reporting-demo` | `pytest --run-reporting-demo -m reporting_demo` | Include the intentionally failing reporting demo |
| `--report-kind` | `pytest --report-kind both` | Generate `core`, `allure`, `both`, or `summary` post-run report |
| `--no-open-report` | `pytest --no-open-report` | Generate report but do not open browser |
| `--no-generate-report` | `pytest --no-generate-report` | Disable post-run report generation |

## Unified CLI Options

| Command | Example | Purpose |
| --- | --- | --- |
| `doctor` | `python framework.py doctor` | Validate local setup and project readiness |
| `doctor --strict` | `python framework.py doctor --strict` | Fail when warnings exist |
| `doctor --install-allure` | `python framework.py doctor --install-allure` | Preinstall local Allure CLI if needed |
| `run` | `python framework.py run` | Run the default pytest suite |
| `run --smoke` | `python framework.py run --smoke` | Run smoke tests |
| `run --regression` | `python framework.py run --regression` | Run regression tests |
| `run --e2e` | `python framework.py run --e2e` | Run e2e tests |
| `run --negative` | `python framework.py run --negative` | Run negative tests |
| `run --helpers` | `python framework.py run --helpers --no-generate-report` | Run helper simulation/unit tests |
| `run --browser` | `python framework.py run --browser chrome` | Run a normal pytest session in one browser |
| `run --browsers` | `python framework.py run --browsers chromium chrome safari` | Run browser matrix execution |
| `run --browser-workers` | `python framework.py run --browsers chromium firefox --browser-workers 2` | Run browser suites in parallel |
| `run --parallel` | `python framework.py run --parallel 4` | Run test cases in parallel using pytest-xdist |
| `run --markers` | `python framework.py run --markers "smoke and not flaky"` | Use a raw pytest marker expression |
| `run --headed` | `python framework.py run --headed` | Run with visible browser UI |
| `run --reruns` | `python framework.py run --reruns 2 --reruns-delay 1` | Retry failed tests |
| `run --run-reporting-demo` | `python framework.py run --run-reporting-demo --markers reporting_demo` | Include intentional failure demo |
| `run --report-kind` | `python framework.py run --report-kind both` | Generate `core`, `allure`, `both`, or `summary` post-run report |
| `report open` | `python framework.py report open` | Open latest matrix, core, summary, or Allure report |
| `report generate` | `python framework.py report generate` | Generate report from existing Allure results |
| `report generate --report-kind` | `python framework.py report generate --report-kind allure` | Generate a specific report kind from existing results |
| `helpers` | `python framework.py helpers` | Open searchable helper catalog |
| `helpers --guide` | `python framework.py helpers --guide` | Print Markdown helper guide path |

You can pass extra pytest arguments after `--`:

```bash
python framework.py run --smoke -- --maxfail=1 -k valid_login
```

## Browser Matrix Execution

The framework supports two cross-browser execution styles.

Framework CLI browser names:

| Name | Playwright runtime | Notes |
| --- | --- | --- |
| `chromium` | `--browser chromium` | Bundled Playwright Chromium browser. |
| `firefox` | `--browser firefox` | Bundled Playwright Firefox browser. |
| `webkit` | `--browser webkit` | Bundled Playwright WebKit browser. |
| `chrome` | `--browser chromium --browser-channel chrome` | Real Google Chrome channel. Install with `python -m playwright install chrome` if missing. |
| `msedge` | `--browser chromium --browser-channel msedge` | Real Microsoft Edge channel. Install with `python -m playwright install msedge` if missing. |
| `safari` | `--browser webkit` | Safari-engine/WebKit coverage. Playwright does not launch `Safari.app` directly. |

`chromium` is the bundled Playwright browser. `chrome` is the installed Google Chrome channel
driven through Playwright. The framework uses Playwright `--browser-channel`; it does not call
system browser CLIs directly.

Pytest native multi-browser execution:

```bash
pytest -m smoke --browser chromium --browser firefox --browser webkit
pytest -m smoke --browser chromium --browser-channel chrome
```

This runs all selected browsers in one pytest session and produces one combined report.

Recommended browser matrix execution:

```bash
python framework.py run --matrix
python scripts/run_browser_matrix.py
```

This reads browsers from `config/settings.yaml`:

```yaml
execution:
  browsers:
    - chromium
    - firefox
    - webkit
    - chrome
    - msedge
    - safari
  browser_workers: 1
```

The matrix runner executes pytest once per browser, then creates:

```text
reports/browser-matrix/index.html                 # Main dashboard
reports/browser-matrix/reports/chromium/          # Chromium drill-down report
reports/browser-matrix/reports/firefox/           # Firefox drill-down report
reports/browser-matrix/reports/webkit/            # WebKit drill-down report
reports/browser-matrix/reports/chrome/            # Google Chrome channel drill-down report
reports/browser-matrix/reports/msedge/            # Microsoft Edge channel drill-down report
reports/browser-matrix/reports/safari/            # Safari-engine/WebKit drill-down report
reports/browser-matrix/results/chromium/          # Chromium Allure results
reports/browser-matrix/results/firefox/           # Firefox Allure results
reports/browser-matrix/results/webkit/            # WebKit Allure results
reports/browser-matrix/results/chrome/            # Google Chrome channel Allure results
reports/browser-matrix/results/msedge/            # Microsoft Edge channel Allure results
reports/browser-matrix/results/safari/            # Safari-engine/WebKit Allure results
reports/browser-matrix/logs/chromium.log          # Chromium pytest output
reports/browser-matrix/logs/firefox.log           # Firefox pytest output
reports/browser-matrix/logs/webkit.log            # WebKit pytest output
reports/browser-matrix/logs/chrome.log            # Google Chrome channel pytest output
reports/browser-matrix/logs/msedge.log            # Microsoft Edge channel pytest output
reports/browser-matrix/logs/safari.log            # Safari-engine/WebKit pytest output
```

The main dashboard is the entry point. It shows:

- Browser-level status
- Total tests per browser
- Passed, failed, broken, and skipped counts
- Pass rate
- Duration
- Attention-needed summary
- Links to each browser's detailed drill-down report
- Links to each browser's execution log

By default, the browser drill-down links under `reports/browser-matrix/reports/<browser>/index.html` are automation-core product reports. Use `--report-kind allure` for official Allure drill-down reports, or `--report-kind both` to generate both core and official Allure outputs.

The matrix command returns a non-zero exit code if any browser run fails, so CI can fail correctly while still keeping the dashboard and browser reports available as artifacts.

Browser matrix runs can also execute browsers in parallel. Configure it in `settings.yaml`:

```yaml
execution:
  browser_workers: 3
```

Or override it from the command line:

```bash
python scripts/run_browser_matrix.py --browser-workers 3
python framework.py run --browsers chromium firefox webkit chrome safari --browser-workers 3
```

Select the matrix report kind:

```bash
python framework.py run --browsers chromium firefox --report-kind core
python framework.py run --browsers chromium firefox --report-kind both
python scripts/run_browser_matrix.py --browsers chromium firefox --report-kind allure
```

Parallel execution has two levels:

- Test-case level parallelism: `-n 4` runs test cases in parallel inside each browser using pytest-xdist.
- Browser-level parallelism: `--browser-workers 3` runs browser suites in parallel.

Warning: these levels multiply. This command can create up to 12 concurrent test workers:

```bash
python scripts/run_browser_matrix.py --browser-workers 3 -n 4
python framework.py run --browsers chromium firefox webkit --browser-workers 3 --parallel 4
```

Start conservatively, then increase based on machine or CI runner capacity.

Browser matrix options:

| Option | Example | Purpose |
| --- | --- | --- |
| `--browsers` | `python scripts/run_browser_matrix.py --browsers chromium chrome safari` | Override configured browser list |
| `--env` | `python scripts/run_browser_matrix.py --env qa` | Select environment |
| `--base-url` | `python scripts/run_browser_matrix.py --base-url https://www.saucedemo.com/` | Override base URL for every browser run |
| `-m`, `--markers` | `python scripts/run_browser_matrix.py -m smoke` | Run marker subset |
| `--headed` | `python scripts/run_browser_matrix.py --headed` | Run headed browsers |
| `-n`, `--parallel-workers` | `python scripts/run_browser_matrix.py -n 2` | Run each browser's tests in parallel |
| `--browser-workers` | `python scripts/run_browser_matrix.py --browser-workers 3` | Run browsers in parallel |
| `--reruns` | `python scripts/run_browser_matrix.py --reruns 2` | Retry failures per browser |
| `--reruns-delay` | `python scripts/run_browser_matrix.py --reruns 2 --reruns-delay 1` | Delay between retries |
| `--run-reporting-demo` | `python scripts/run_browser_matrix.py --run-reporting-demo -m reporting_demo` | Include intentional failure demo |
| `--no-open-report` | `python scripts/run_browser_matrix.py --no-open-report` | Generate dashboard without opening browser |
| `--no-generate-report` | `python scripts/run_browser_matrix.py --no-generate-report` | Run browser matrix without generating reports |

Examples:

```bash
python scripts/run_browser_matrix.py -m smoke --no-open-report
python framework.py run --browsers chromium firefox webkit --smoke --no-open-report
python framework.py run --smoke --browser chrome --no-open-report
python framework.py run --smoke --browser safari --no-open-report
python scripts/run_browser_matrix.py --browsers chromium chrome safari -m smoke --no-open-report
python scripts/run_browser_matrix.py --browsers chromium firefox -m regression -n 2 --reruns 2
python framework.py run --browsers chromium firefox --regression --parallel 2 --reruns 2
python scripts/run_browser_matrix.py --browsers chromium firefox webkit --browser-workers 3 -m smoke
python framework.py run --browsers chromium firefox webkit --browser-workers 3 --smoke
python scripts/run_browser_matrix.py --browsers chromium --env staging --headed
python framework.py run --browsers chromium --env staging --headed
```

## Marker Reference

| Marker | Purpose | Example |
| --- | --- | --- |
| `smoke` | Critical fast confidence tests | `pytest -m smoke` |
| `regression` | Broader product behavior coverage | `pytest -m regression` |
| `e2e` | Full user journeys | `pytest -m e2e` |
| `negative` | Validation and error scenarios | `pytest -m negative` |
| `reporting_demo` | Intentional failure for artifacts/reporting | `pytest --run-reporting-demo -m reporting_demo` |
| `flaky` | Marker available for retry-oriented tests | `pytest -m flaky --reruns 2` |
| `helpers` | Unit-style helper library tests | `pytest -m helpers --no-generate-report` |

The `reporting_demo` test is skipped by default so local and CI runs stay green.

## Reporting Behavior

Every pytest run writes raw Allure results to:

```text
reports/allure-results/
```

At the end of the test session, the framework automatically generates:

```text
reports/automation-report/index.html
```

This is the default automation-core product report and it is the report opened locally after a run.

Report generation flow:

1. Pytest writes raw Allure result files to `reports/allure-results/`.
2. The web adapter calls `automation_core.reporting.finalize_allure_reporting(...)`.
3. By default, `report_kind=core` generates `reports/automation-report/index.html`.
4. If the run is local, the framework opens the core report in the default browser.
5. If the run is in CI/server mode or browser opening fails, the framework logs a note and does not fail a successful test run.

Supported report kinds:

| Kind | Output | Purpose |
| --- | --- | --- |
| `core` | `reports/automation-report/index.html` | Default product report and recommended local/CI artifact |
| `allure` | `reports/allure-report/index.html` | Official Allure HTML report only |
| `both` | Core report plus official Allure report | Recommended when a team wants the product dashboard and Allure drill-downs |
| `summary` | `reports/summary-report/index.html` | Lightweight summary report |

Configure the default in `config/settings.yaml`:

```yaml
reporting:
  report_kind: core
  core_report_dir: reports/automation-report
  allure_report_dir: reports/allure-report
  summary_report_dir: reports/summary-report
```

Override it per run:

```bash
python framework.py run --report-kind core
python framework.py run --report-kind both
pytest --report-kind allure
```

Generate report but do not open it:

```bash
python framework.py run --no-open-report
pytest --no-open-report
```

Skip report generation:

```bash
python framework.py run --no-generate-report
pytest --no-generate-report
```

Generate a report manually from existing results:

```bash
python framework.py report generate
python framework.py report generate --report-kind both
python scripts/generate_allure_report.py --report-kind core
```

Open the latest report:

```bash
python framework.py report open
python framework.py report open --type matrix
python framework.py report open --type core
python framework.py report open --type summary
python framework.py report open --type allure
```

Official Allure is optional. If `--report-kind allure` or `--report-kind both` is selected and the `allure` command is missing, the framework attempts to install a local Allure CLI under `.tools/`. If official Allure still cannot run while `report_kind=both`, the core report remains successful and the framework logs a warning instead of failing an otherwise successful test run.

Important: official Allure reports can show permanent `Loading...` when opened directly with `file://`. Open them through the framework CLI:

```bash
python framework.py report open --type allure
```

If you want to run official Allure manually:

```bash
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

## Failure Artifacts

On failed tests, the framework captures:

- Full-page screenshot in `screenshots/`
- Playwright trace zip in `traces/`
- Browser video in `videos/`
- Attachments in the Allure result

Run the intentional failure demo:

```bash
python framework.py run --run-reporting-demo --markers reporting_demo --no-open-report
pytest --run-reporting-demo -m reporting_demo --no-open-report
```

Open a trace:

```bash
playwright show-trace traces/<trace-file>.zip
```

Passed-test videos are deleted automatically so `videos/` only keeps useful failure evidence.

## Demo Test Coverage

| Scenario | Test |
| --- | --- |
| Valid login | `tests/smoke/test_login.py::test_valid_login` |
| Invalid login | `tests/smoke/test_login.py::test_invalid_login_shows_error` |
| Locked-out user login | `tests/smoke/test_login.py::test_locked_out_user_login_shows_error` |
| Add product to cart | `tests/regression/test_cart.py::test_add_product_to_cart` |
| Remove product from cart | `tests/regression/test_cart.py::test_remove_product_from_cart` |
| Sort products by price/name | `tests/regression/test_sorting.py` |
| Complete checkout flow | `tests/e2e/test_checkout.py::test_complete_checkout_flow` |
| Negative checkout validation | `tests/e2e/test_checkout.py::test_checkout_requires_first_name` |
| Failure reporting demo | `tests/regression/test_reporting_demo.py::test_intentional_failure_generates_artifacts` |

## Feature Examples

Run by environment:

```bash
python framework.py run --env qa
python framework.py run --env staging
python framework.py run --env prod
pytest --env qa
pytest --env staging
pytest --env prod
```

Run with a temporary base URL override:

```bash
python framework.py run --base-url https://www.saucedemo.com/ --smoke
pytest --base-url https://www.saucedemo.com/ -m smoke
```

Run cross-browser smoke tests in one combined pytest report:

```bash
pytest -m smoke --browser chromium --browser firefox --browser webkit
```

Run cross-browser smoke tests with the main matrix dashboard:

```bash
python framework.py run --browsers chromium firefox webkit --smoke --no-open-report
python scripts/run_browser_matrix.py -m smoke --no-open-report
```

Run regression tests in parallel with retries and no browser auto-open:

```bash
python framework.py run --regression --parallel 2 --reruns 2 --reruns-delay 1 --no-open-report
pytest -m regression -n 2 --reruns 2 --reruns-delay 1 --no-open-report
```

Run e2e tests headed for debugging:

```bash
python framework.py run --e2e --headed --browser chromium
pytest -m e2e --headed --browser chromium
```

Run only checkout tests:

```bash
pytest tests/e2e/test_checkout.py
```

Run reporting demo and generate failure artifacts:

```bash
python framework.py run --run-reporting-demo --markers reporting_demo --no-open-report
pytest --run-reporting-demo -m reporting_demo --no-open-report
```

Generate report from previous results without running tests:

```bash
python framework.py report generate
python scripts/generate_allure_report.py --report-kind core
```

## Framework Helpers

The framework includes reusable helpers for common automation tasks so engineers do not need to
rebuild the same utilities in every project. Environment-neutral helpers such as config, logging,
data generation, files, polling, text extraction, date/time, secrets, cleanup, soft assertions, and
report utilities are compatibility wrappers over `automation-core`; web-specific helpers remain in
this repository.

Helper documentation:

- [Framework Helpers Guide](docs/FRAMEWORK_HELPERS.md)
- [Searchable Helpers Catalog](docs/helpers_catalog.html)
- [Feature Parity Notes](docs/FEATURE_PARITY.md)
- [Web Framework Walkthrough](docs/WALKTHROUGH.md)

Open the searchable catalog from the CLI:

```bash
python framework.py helpers
```

Helper configuration at a glance:

| Helper area | Extra setup needed? | Notes |
| --- | --- | --- |
| Email OTP | Yes | Set `TEST_EMAIL_USERNAME` and `TEST_EMAIL_PASSWORD` as environment variables. Use a test mailbox or app password, never a real password in code. |
| API | Usually yes | Pass the target API base URL and headers/tokens from config or environment variables. |
| Database | Project-specific | The built-in helper works with DB-API connections. SQLite works out of the box; PostgreSQL/MySQL projects should add the driver they use and pass a connection object. |
| Auth/session | No global setup | Saves Playwright storage state to a file. Keep live auth state under ignored paths such as `data/auth/`. |
| PDF | No | `pypdf` is installed through `requirements.txt`. Scanned image PDFs need OCR, which is intentionally out of scope. |
| Security smoke | No | Tune expected headers/cookie names per application because demo or lower environments may not use production headers. |
| Performance smoke | No | Tune timing/resource thresholds per environment; CI runners can be slower than local machines. |
| i18n | No | Pass expected locale/language selectors from the application under test. |
| Browser/file/network/form/table/helpers | No | Use directly from `utils.helpers.*` with Playwright pages, locators, files, or response objects. |

Current helper categories:

- Email OTP helpers using IMAP
- Polling and retry helpers
- Text extraction helpers
- Test data generators
- File and download helpers
- File transfer helpers for browser downloads/uploads
- CSV/JSON structured file validation helpers
- Browser storage/session helpers
- Auth/session helpers for saving and reusing logged-in Playwright storage state
- Cookie helpers for session assertions, feature flags, and context reuse
- API helpers for setup, cleanup, and hybrid UI/API tests
- Database helpers for setup, cleanup, and DB-backed assertions
- Network helpers for responses, failed requests, mocks, and blocked resources
- Security smoke helpers for headers, cookies, storage, and secret-leak checks
- Performance smoke helpers for navigation timing and resource thresholds
- Date/time helpers
- URL/query parameter helpers
- PDF helpers for downloaded document validation
- i18n helpers for locale, direction, translation-key, and language-switch checks
- Environment/secrets helpers
- Table/grid helpers
- Allure/debug helpers for reusable steps and attachments
- Console helpers for browser warnings/errors and page errors
- Form helpers for input, checkbox, select, upload, and validation flows
- Keyboard/focus helpers for tab order, active element, and keyboard accessibility checks
- Cleanup registry helpers for API setup data, teardown steps, and post-test resource cleanup
- Notification helpers for toast, snackbar, alert, and status-message checks
- Soft assertion helpers for grouped validation failures
- Accessibility smoke helpers for title, language, headings, alt text, and accessible names
- Visual helpers for screenshots, baselines, masks, and Allure attachments
- SauceDemo business flow helpers for login, cart, and checkout flows

Helper tests live under:

```text
tests/helpers/
```

Run them with:

```bash
python framework.py run --helpers --no-generate-report
pytest tests/helpers --no-generate-report
pytest -m helpers --no-generate-report
```

Example OTP usage:

OTP email helpers require a dedicated test mailbox or provider mailbox configured through environment variables. Do not put email passwords in repository files. For Gmail, use an App Password for the test mailbox instead of the real account password.

```bash
export TEST_EMAIL_USERNAME="qa.automation@example.com"
export TEST_EMAIL_PASSWORD="app-password-or-provider-secret"
```

```python
def test_login_with_email_code(email_otp_helper):
    otp = email_otp_helper.wait_for_otp(
        sender="security@example.com",
        subject_contains="Your login code",
        regex=r"\\b\\d{6}\\b",
        timeout_seconds=60,
        interval_seconds=5,
    )

    assert len(otp) == 6
```

Example polling usage:

```python
from utils.helpers.wait import wait_until


job_id = wait_until(
    lambda: get_job_id_if_ready(),
    timeout_seconds=30,
    interval_seconds=2,
)
```

Example text extraction:

```python
from utils.helpers.text import extract_otp


otp = extract_otp("Your verification code is 482913")
```

## Self-Healing And Runtime Auto-Healing

The framework supports two conservative locator recovery layers.

Engineer-defined self-healing means a Page Object can define a primary selector and one or more
fallback selectors. If the primary selector is not attached to the DOM, the framework tries the
fallback selectors in order.

Runtime auto-healing is separate and disabled by default. When enabled, it runs only after the
original Playwright action fails. `suggest` mode records ranked candidates without applying them.
`apply` mode uses a candidate only when automation-core returns `APPLIED` and the web adapter safety
checks pass.

Both layers are configured in:

```text
config/settings.yaml
```

```yaml
self_healing:
  enabled: true
  timeout_ms: 1500

runtime_healing:
  mode: disabled
  min_score: 0.78
  ambiguity_delta: 0.05
  max_candidates: 10
  allowed_actions:
    - click
    - fill
    - select
    - text
    - expect_visible
  allow_patterns: []
  deny_patterns: []
  audit_path: reports/healing/events.jsonl
```

Example Page Object usage:

```python
self.login_button = self.locator_with_fallbacks(
    "login button",
    "[data-test='login-button']",
    "#login-button",
    "input[type='submit']",
)
```

When an engineer-defined fallback is used, the framework:

- Logs a warning
- Adds an Allure step
- Attaches the primary and fallback selector details to the Allure result

When runtime auto-healing is attempted, the framework:

- Logs the attempt and decision
- Writes a JSONL audit event under `reports/healing/`
- Attaches the event to Allure
- Enriches the core product report with healing metadata

Runtime candidate discovery is web-owned and Playwright-based. It looks at stable element signals
such as `data-test`, `data-testid`, `id`, `name`, `aria-label`, role, and nearby text. Full DOM XPath
is not used as a primary signal.

Disable all locator recovery beyond the original locator:

```yaml
self_healing:
  enabled: false
  timeout_ms: 1500

runtime_healing:
  mode: disabled
```

## Working With Test Data

Users are stored in:

```text
data/users.json
```

Checkout data is stored in:

```text
data/checkout_data.json
```

The fixtures `users` and `checkout_data` load this data once per test session. Example:

```python
def test_valid_login(page, base_url, users):
    login_page = LoginPage(page)
    login_page.open(base_url)
    login_page.login(**users["standard_user"])
```

## Working With Environments

Environment URLs live in:

```text
config/environments.yaml
```

Example:

```yaml
qa:
  base_url: "https://www.saucedemo.com/"
```

Run against an environment:

```bash
python framework.py run --env qa
pytest --env qa
```

SauceDemo exposes one public demo URL, so `qa`, `staging`, and `prod` currently point to the same application.

## Writing New Tests

Follow these rules:

- Keep locators inside `pages/`, not inside test files.
- Add page-specific actions to the relevant Page Object.
- Use `utils/assertions.py` for clear assertion steps.
- Use test data from `data/` when values are reusable.
- Add a marker such as `smoke`, `regression`, `e2e`, or `negative`.
- Keep tests readable as business flows.

Example pattern:

```python
import pytest

from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from utils.assertions import assert_true


@pytest.mark.smoke
def test_user_can_open_inventory(page, base_url, users):
    login_page = LoginPage(page)
    inventory_page = InventoryPage(page)

    login_page.open(base_url)
    login_page.login(**users["standard_user"])

    assert_true(inventory_page.is_loaded(), "Inventory page should be loaded")
```

## Page Object Guidelines

Good Page Object usage:

- Define locators in `__init__`.
- Use `locator_with_fallbacks()` for important elements that have stable alternative selectors.
- Expose business actions such as `login`, `add_product_to_cart`, and `finish_order`.
- Use stable SauceDemo `data-test` selectors where available.
- Use Playwright `expect()` inside page readiness checks when waiting is needed.

Avoid:

- Locators directly inside tests
- Sleeps or fixed waits
- Assertions hidden inside low-level click/fill helpers
- Broad fallback selectors that might match the wrong element
- Test data hardcoded repeatedly across many tests

## CI/CD

The GitHub Actions workflow is:

```text
.github/workflows/playwright-tests.yml
```

The pipeline:

1. Checks out the repository.
2. Sets up Python 3.12.
3. Installs dependencies from `requirements.txt`.
4. Installs Playwright browsers with system dependencies.
5. Runs `ruff check .` for syntax/import lint coverage.
6. Runs `ruff format --check .` to enforce consistent formatting.
7. Runs the browser matrix runner in parallel with Chromium.
8. Skips the intentional reporting demo by default.
9. Generates the browser matrix dashboard and browser drill-down report.
10. Uploads reports, screenshots, videos, and traces as artifacts.

## Troubleshooting

If browsers are missing:

```bash
python framework.py doctor
playwright install
```

If Linux dependencies are missing:

```bash
playwright install --with-deps
```

If you want to regenerate the report without rerunning tests:

```bash
python framework.py report generate
python scripts/generate_allure_report.py --report-kind core
```

If official Allure cannot run while using `--report-kind both`, the framework keeps the core product report and logs a warning.

If you need parallel execution, prefer the supported commands:

```bash
pytest -n 4
python framework.py run --browsers chromium firefox webkit --browser-workers 3
```

Avoid starting multiple independent `pytest` commands at the same time against the same `reports/allure-results` directory. Each pytest session cleans that directory before writing Allure results, so separate concurrent sessions can race with each other.

If a test fails, inspect:

```text
screenshots/
videos/
traces/
reports/automation-report/index.html
reports/allure-report/index.html  # only when generated with --report-kind allure or both
```

## Notes

- The framework is intentionally beginner-friendly but keeps production-style boundaries.
- Normal `pytest` runs stay green because the reporting demo is skipped by default.
- Use `--run-reporting-demo -m reporting_demo` when you specifically want to demonstrate screenshots, videos, traces, and failed-test reporting.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
