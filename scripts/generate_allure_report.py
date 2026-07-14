from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from utils.reporting import (
    VALID_REPORT_KINDS,
    finalize_web_report,
    primary_report_path,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate framework reports from Allure result files."
    )
    parser.add_argument(
        "--results",
        default="reports/allure-results",
        help="Path to Allure results directory.",
    )
    parser.add_argument(
        "--output",
        default="reports/automation-report",
        help="Path to generated core report directory.",
    )
    parser.add_argument(
        "--allure-output",
        default="reports/allure-report",
        help="Path to generated official Allure report directory.",
    )
    parser.add_argument(
        "--summary-output",
        default="reports/summary-report",
        help="Path to generated summary report directory.",
    )
    parser.add_argument(
        "--report-kind",
        choices=VALID_REPORT_KINDS,
        default="core",
        help="Report kind to generate: core, allure, both, or summary.",
    )
    args = parser.parse_args()

    result = finalize_web_report(
        project_root=PROJECT_ROOT,
        results_dir=(PROJECT_ROOT / args.results).resolve(),
        report_kind=args.report_kind,
        output_dir=(PROJECT_ROOT / args.output).resolve(),
        allure_output_dir=(PROJECT_ROOT / args.allure_output).resolve(),
        summary_output_dir=(PROJECT_ROOT / args.summary_output).resolve(),
    )
    report_path = primary_report_path(result)
    if not report_path:
        raise SystemExit("Report generation did not produce an index.html.")
    print(f"Generated report: {report_path}")


if __name__ == "__main__":
    main()
