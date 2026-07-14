from __future__ import annotations

from automation_core.reporting.generator import (
    generate_browser_matrix_dashboard as generate_browser_matrix_dashboard,
    generate_html_report as generate_html_report,
    read_allure_results as read_allure_results,
    summarize_results as summarize_results,
)


STATUS_ORDER = {"failed": 0, "broken": 1, "skipped": 2, "passed": 3}
