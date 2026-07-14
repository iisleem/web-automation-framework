## What Changed

- 

## Why

- 

## Validation

- [ ] `python -m compileall -q framework.py conftest.py pages flows utils scripts tests`
- [ ] `python -m ruff check .`
- [ ] `python framework.py run --helpers --no-open-report --no-generate-report`
- [ ] `python framework.py run --smoke --browser chromium --report-kind core --no-open-report`
- [ ] Browser matrix was run where relevant: `python scripts/run_browser_matrix.py --browsers chromium --env qa -m smoke --report-kind core --no-open-report`
- [ ] Report generation was checked where relevant: `python framework.py report generate --report-kind both --no-open`

## Setup, Secrets, Reports, And CI Impact

- [ ] New setup steps or environment variables are documented, or this PR does not change setup.
- [ ] New secrets are documented as placeholders only, or this PR does not require secrets.
- [ ] Report output behavior is documented, or this PR does not affect reporting.
- [ ] CI impact is documented, or this PR does not affect CI.

## Notes

- 
