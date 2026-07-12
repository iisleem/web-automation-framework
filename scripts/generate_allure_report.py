from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from utils.report_generator import generate_html_report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a lightweight HTML report from Allure result files."
    )
    parser.add_argument(
        "--results",
        default="reports/allure-results",
        help="Path to Allure results directory.",
    )
    parser.add_argument(
        "--output",
        default="reports/allure-report",
        help="Path to generated HTML report directory.",
    )
    args = parser.parse_args()

    report_path = generate_html_report(Path(args.results), Path(args.output))
    print(f"Generated report: {report_path}")


if __name__ == "__main__":
    main()
