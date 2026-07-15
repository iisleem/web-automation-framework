# Web Feature Parity Notes

The web automation framework is the baseline for the automation framework family. It defines the
default user experience for CLI commands, pytest markers, reporting, helper documentation, browser
matrix execution, and practical runnable samples. Shared behavior should move to `automation-core`
when it is environment-neutral; browser-specific behavior stays in this repository.

## Web Baseline Capabilities

| Capability | Web status | Notes |
| --- | --- | --- |
| Unified CLI | Supported | `framework.py` handles doctor checks, test runs, reports, helper docs, and browser matrix runs. |
| Pytest execution | Supported | Markers, pytest-xdist workers, pytest reruns, and passthrough pytest args are supported. |
| Page Object Model | Supported | Page objects live under `pages/`; tests keep locators out of test files. |
| SauceDemo sample | Supported | Smoke, regression, and e2e tests demonstrate login, cart, sorting, checkout, negative validation, and reporting artifacts. |
| Browser selection | Supported | Chromium, Firefox, WebKit, Google Chrome channel, Microsoft Edge channel, and Safari-engine/WebKit aliases are supported through Playwright. |
| Browser matrix | Supported | `scripts/run_browser_matrix.py` runs one suite per browser and builds `reports/browser-matrix/index.html`. |
| Runtime auto-healing | Supported | Disabled by default; web discovers Playwright candidates and automation-core evaluates decisions. |
| Reports | Supported | Core product report is the default at `reports/automation-report/index.html`. |
| Official Allure | Optional | Use `--report-kind allure` or `--report-kind both` when official Allure HTML is needed. |
| Failure artifacts | Supported | Failed tests capture screenshots, Playwright traces, videos, and Allure attachments. |
| Helper catalog | Supported | `docs/FRAMEWORK_HELPERS.md` and `docs/helpers_catalog.html` document reusable web automation helpers. |
| Starter template | Supported | GitHub template repository plus `templates/starter_project/` for product-specific pages, flows, tests, and config. |

## Reporting Modes

Every pytest run writes raw Allure result files to `reports/allure-results/`. The post-run reporting
flow calls `automation_core.reporting.finalize_allure_reporting(...)` through the web adapter in
`utils/reporting.py`.

| Report kind | Primary output | Notes |
| --- | --- | --- |
| `core` | `reports/automation-report/index.html` | Default and recommended product report. |
| `allure` | `reports/allure-report/index.html` | Official Allure report only. |
| `both` | Core report plus official Allure output | Core remains primary; official Allure failures are warnings when core succeeds. |
| `summary` | `reports/summary-report/index.html` | Lightweight HTML summary. |

## Web-Only Ownership

| Area | Why it stays in web |
| --- | --- |
| Playwright browsers, contexts, pages, traces, videos, screenshots | Browser/runtime-specific implementation. |
| Page objects and SauceDemo UI flows | Product-specific web demo behavior. |
| Browser matrix execution | Cross-browser web concern; mobile/API use their own matrix dimensions. |
| Browser storage, cookies, console, network, form, table, keyboard, visual, accessibility helpers | These depend on Playwright page/locator/browser concepts. |

## Shared/Core Ownership

| Area | Direction |
| --- | --- |
| Product report models and generation | Owned by `automation-core`; web passes serializable web metadata through `utils/reporting.py`. |
| Neutral config, logging, reporting utilities, polling, text, data, file, env, cleanup, and soft assertion concepts | Web keeps compatibility import paths while delegating shared behavior to `automation-core`. |
| Framework-specific adapters | Stay in this repo when they depend on Playwright or browser concepts. |

## Self-Healing And Auto-Healing

Conservative self-healing currently means engineer-defined primary locators with ordered fallback
selectors in page objects.

Runtime auto-healing is supported through the web adapter and `automation-core` healing models. It is
disabled by default. `suggest` mode records ranked candidates only, while `apply` mode can use a
candidate after core approval and web safety checks. Candidate discovery stays in web because it
depends on Playwright pages and browser DOM signals.

## Maintainer Rule

When adding a feature to this repository:

1. Keep browser-specific behavior in web.
2. Move environment-neutral behavior to `automation-core` when it applies to more than one framework.
3. Keep CLI/reporting/docs patterns aligned with mobile and API unless the target environment requires a difference.
4. Document intentional parity differences here.
