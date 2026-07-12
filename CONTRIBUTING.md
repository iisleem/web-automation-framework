# Contributing

Thanks for helping improve this framework.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
playwright install
python framework.py doctor
```

## Before Opening A Pull Request

Run the focused checks first:

```bash
python -m pytest -m helpers --no-generate-report
python -m pytest --collect-only -q --no-generate-report
python framework.py doctor
```

For behavior changes, also run:

```bash
python -m pytest --no-generate-report --no-open-report
```

## Contribution Guidelines

- Keep locators inside Page Objects, not test files.
- Keep helper functions small, explicit, and documented.
- Add tests for new helpers or framework behavior.
- Do not commit secrets, `.env` files, auth storage state, reports, videos, screenshots, or traces.
- Update `README.md`, `docs/FRAMEWORK_HELPERS.md`, and `docs/helpers_catalog.html` when user-facing behavior changes.
