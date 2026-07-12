# Security Policy

## Secrets

Do not commit passwords, API tokens, email app passwords, `.env` files, Playwright storage state, or generated reports.

Email and OTP helpers must read credentials from environment variables:

```bash
export TEST_EMAIL_USERNAME="qa.automation@example.com"
export TEST_EMAIL_PASSWORD="app-password-or-provider-secret"
```

## Reporting A Vulnerability

Please open a private security advisory or contact the repository owner through GitHub. Include a clear description, reproduction steps, and any relevant logs with secrets removed.
