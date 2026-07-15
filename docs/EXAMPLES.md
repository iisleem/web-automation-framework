# Runnable Web Examples

The `tests/examples/` folder contains small SauceDemo recipes that show how to use the framework
without reading the full smoke, regression, and e2e suites first.

## Run The Examples

Run the focused examples in Chromium and generate the default core product report:

```bash
python framework.py run --browser chromium -m examples --report-kind core --no-open-report
```

Equivalent direct pytest command:

```bash
pytest tests/examples --browser chromium --report-kind core --no-open-report
```

Run on a supported browser alias or channel:

```bash
python framework.py run --browser chrome -m examples --report-kind core --no-open-report
python framework.py run --browser safari -m examples --report-kind core --no-open-report
```

Generated report outputs:

```text
reports/automation-report/index.html
reports/automation-report/report-data.json
```

## Included Recipes

| Example | Demonstrates |
| --- | --- |
| `tests/examples/test_page_object_recipe.py` | Direct Page Object usage with fixtures, test data, actions, and assertions. |
| `tests/examples/test_flow_recipe.py` | Higher-level SauceDemo flow usage with reusable assertions. |

## When To Use These

Use these examples as a starting point for new product scenarios. Keep page locators in page objects,
compose repeated business actions in flows, and keep tests readable with clear setup, action, and
assertion steps.
