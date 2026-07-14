from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys

from utils.allure_cli import get_or_install_allure_cli
from utils.config_reader import ConfigReader
from utils.logger import get_logger
from utils.report_opener import open_report
from utils.reporting import (
    VALID_REPORT_KINDS,
    build_web_report_metadata,
    configured_report_kind,
    finalize_web_report,
    primary_report_path,
)


PROJECT_ROOT = Path(__file__).resolve().parent
LOGGER = get_logger("framework-cli")
VALID_BROWSERS = {"chromium", "firefox", "webkit"}


class Doctor:
    def __init__(self) -> None:
        self.failed = 0
        self.warnings = 0

    def pass_(self, message: str) -> None:
        print(f"[PASS] {message}")

    def warn(self, message: str) -> None:
        self.warnings += 1
        print(f"[WARN] {message}")

    def fail(self, message: str) -> None:
        self.failed += 1
        print(f"[FAIL] {message}")

    def exit_code(self) -> int:
        return 1 if self.failed else 0


def main() -> int:
    parser = _build_parser()
    args, unknown_args = parser.parse_known_args()

    if args.command == "run":
        return _run_tests(args, unknown_args)
    if unknown_args:
        parser.error(f"Unknown arguments for '{args.command}': {' '.join(unknown_args)}")
    if args.command == "doctor":
        return _run_doctor(args)
    if args.command == "report":
        return _handle_report_command(args)
    if args.command == "helpers":
        return _open_helpers_catalog(args)

    parser.print_help()
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="framework.py",
        description="Unified CLI for the web automation framework.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run tests locally or as a browser matrix.")
    run_parser.add_argument("--env", default="qa", help="Environment from config/environments.yaml.")
    run_parser.add_argument("--base-url", help="Override the environment base URL.")
    run_parser.add_argument("--browser", choices=sorted(VALID_BROWSERS), help="Single browser for a normal pytest run.")
    run_parser.add_argument("--browsers", nargs="+", choices=sorted(VALID_BROWSERS), help="Run a browser matrix.")
    run_parser.add_argument("--browser-workers", type=int, help="Parallel browser suites for matrix execution.")
    run_parser.add_argument("--headed", action="store_true", help="Run browsers in headed mode.")
    run_parser.add_argument("-n", "--parallel", help="pytest-xdist worker count for test-case parallelism.")
    run_parser.add_argument("-m", "--markers", help="Raw pytest marker expression.")
    run_parser.add_argument("--smoke", action="store_true", help="Run smoke tests.")
    run_parser.add_argument("--regression", action="store_true", help="Run regression tests.")
    run_parser.add_argument("--e2e", action="store_true", help="Run e2e tests.")
    run_parser.add_argument("--negative", action="store_true", help="Run negative tests.")
    run_parser.add_argument("--helpers", action="store_true", help="Run helper simulation/unit tests.")
    run_parser.add_argument("--reruns", help="Retry failed tests.")
    run_parser.add_argument("--reruns-delay", help="Delay between retries.")
    run_parser.add_argument(
        "--run-reporting-demo", action="store_true", help="Include the intentionally failing reporting demo."
    )
    run_parser.add_argument(
        "--report-kind",
        choices=VALID_REPORT_KINDS,
        help="Post-run report kind: core, allure, both, or summary. Defaults to config/settings.yaml.",
    )
    run_parser.add_argument("--no-open-report", action="store_true", help="Do not open generated reports.")
    run_parser.add_argument("--no-generate-report", action="store_true", help="Do not generate a post-run report.")
    run_parser.add_argument("--matrix", action="store_true", help="Force browser matrix execution.")

    report_parser = subparsers.add_parser("report", help="Generate or open reports.")
    report_subparsers = report_parser.add_subparsers(dest="report_command", required=True)
    report_open = report_subparsers.add_parser("open", help="Open the latest generated report.")
    report_open.add_argument(
        "--type",
        choices=("auto", "matrix", "core", "allure", "summary"),
        default="auto",
        help="Report type to open.",
    )
    report_generate = report_subparsers.add_parser("generate", help="Generate a report from Allure results.")
    report_generate.add_argument("--results", default="reports/allure-results", help="Allure results directory.")
    report_generate.add_argument(
        "--output",
        help="Primary report output directory. Defaults to config/settings.yaml for the selected report kind.",
    )
    report_generate.add_argument(
        "--allure-output",
        help="Official Allure output directory when --report-kind is allure or both.",
    )
    report_generate.add_argument(
        "--summary-output",
        help="Summary report output directory when --report-kind is summary.",
    )
    report_generate.add_argument(
        "--report-kind",
        choices=VALID_REPORT_KINDS,
        help="Report kind to generate: core, allure, both, or summary. Defaults to config/settings.yaml.",
    )
    report_generate.add_argument("--no-open", action="store_true", help="Generate without opening the report.")

    helpers_parser = subparsers.add_parser("helpers", help="Open helper documentation.")
    helpers_parser.add_argument(
        "--guide",
        action="store_true",
        help="Print the Markdown helper guide path instead of opening the searchable catalog.",
    )

    doctor_parser = subparsers.add_parser("doctor", help="Check the local machine and project readiness.")
    doctor_parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as failures.",
    )
    doctor_parser.add_argument(
        "--install-allure",
        action="store_true",
        help="Install local Allure CLI if the allure command is missing.",
    )

    return parser


def _run_tests(args: argparse.Namespace, extra_pytest_args: list[str]) -> int:
    marker_expression = _resolve_marker_expression(args)
    browsers = _resolve_run_browsers(args)
    use_matrix = args.matrix or bool(args.browsers) or len(browsers) > 1

    if use_matrix:
        command = [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_browser_matrix.py"),
            "--env",
            args.env,
            "--browsers",
            *browsers,
        ]
        if args.browser_workers is not None:
            command.extend(["--browser-workers", str(args.browser_workers)])
        if args.base_url:
            command.extend(["--base-url", args.base_url])
        if marker_expression:
            command.extend(["-m", marker_expression])
        if args.headed:
            command.append("--headed")
        if args.parallel:
            command.extend(["-n", str(args.parallel)])
        if args.reruns:
            command.extend(["--reruns", str(args.reruns)])
        if args.reruns_delay:
            command.extend(["--reruns-delay", str(args.reruns_delay)])
        if args.run_reporting_demo:
            command.append("--run-reporting-demo")
        if args.no_open_report:
            command.append("--no-open-report")
        if args.no_generate_report:
            command.append("--no-generate-report")
        if args.report_kind:
            command.extend(["--report-kind", args.report_kind])
        command.extend(_normalize_passthrough_args(extra_pytest_args))
        return _run_command(command)

    command = [sys.executable, "-m", "pytest", "--env", args.env]
    if browsers:
        command.extend(["--browser", browsers[0]])
    if args.base_url:
        command.extend(["--base-url", args.base_url])
    if marker_expression:
        command.extend(["-m", marker_expression])
    if args.headed:
        command.append("--headed")
    if args.parallel:
        command.extend(["-n", str(args.parallel)])
    if args.reruns:
        command.extend(["--reruns", str(args.reruns)])
    if args.reruns_delay:
        command.extend(["--reruns-delay", str(args.reruns_delay)])
    if args.run_reporting_demo:
        command.append("--run-reporting-demo")
    if args.no_open_report:
        command.append("--no-open-report")
    if args.no_generate_report:
        command.append("--no-generate-report")
    if args.report_kind:
        command.extend(["--report-kind", args.report_kind])
    command.extend(_normalize_passthrough_args(extra_pytest_args))

    return _run_command(command)


def _resolve_marker_expression(args: argparse.Namespace) -> str | None:
    selected = [
        marker
        for marker, enabled in {
            "smoke": args.smoke,
            "regression": args.regression,
            "e2e": args.e2e,
            "negative": args.negative,
            "helpers": args.helpers,
        }.items()
        if enabled
    ]
    expressions = selected[:]
    if args.markers:
        expressions.append(f"({args.markers})" if " " in args.markers else args.markers)
    if not expressions:
        return None
    return " and ".join(expressions)


def _resolve_run_browsers(args: argparse.Namespace) -> list[str]:
    if args.browser and args.browsers:
        raise SystemExit("Use either --browser for a normal run or --browsers for a matrix run, not both.")
    if args.browsers:
        return args.browsers
    if args.browser:
        return [args.browser]
    if args.matrix:
        settings = ConfigReader(PROJECT_ROOT).read_settings()
        return settings.get("execution", {}).get("browsers", ["chromium"])
    return []


def _normalize_passthrough_args(args: list[str]) -> list[str]:
    if args and args[0] == "--":
        return args[1:]
    return args


def _handle_report_command(args: argparse.Namespace) -> int:
    if args.report_command == "open":
        report_path = _find_report(args.type)
        if not report_path:
            print("No report found. Run tests first or generate a report with: python framework.py report generate")
            return 1
        return 0 if _open_path(report_path) else 1

    results_dir = (PROJECT_ROOT / args.results).resolve()
    output_dir = (PROJECT_ROOT / args.output).resolve() if args.output else None
    allure_output_dir = (PROJECT_ROOT / args.allure_output).resolve() if args.allure_output else None
    summary_output_dir = (PROJECT_ROOT / args.summary_output).resolve() if args.summary_output else None
    result = _generate_report(
        results_dir,
        report_kind=args.report_kind,
        output_dir=output_dir,
        allure_output_dir=allure_output_dir,
        summary_output_dir=summary_output_dir,
    )
    report_path = primary_report_path(result)
    if not report_path:
        print("Report generation did not produce an index.html. Check logs for details.")
        return 1
    print(f"Generated report: {report_path}")
    if not args.no_open:
        _open_path(report_path)
    return 0


def _find_report(report_type: str) -> Path | None:
    candidates: list[Path] = []
    if report_type in {"auto", "matrix"}:
        candidates.append(PROJECT_ROOT / "reports" / "browser-matrix" / "index.html")
    if report_type in {"auto", "core"}:
        candidates.append(PROJECT_ROOT / "reports" / "automation-report" / "index.html")
    if report_type in {"auto", "summary"}:
        candidates.append(PROJECT_ROOT / "reports" / "summary-report" / "index.html")
    if report_type in {"auto", "allure"}:
        candidates.append(PROJECT_ROOT / "reports" / "allure-report" / "index.html")

    existing = [path for path in candidates if path.exists()]
    if not existing:
        return None
    return max(existing, key=lambda path: path.stat().st_mtime)


def _generate_report(
    results_dir: Path,
    *,
    report_kind: str | None = None,
    output_dir: Path | None = None,
    allure_output_dir: Path | None = None,
    summary_output_dir: Path | None = None,
):
    kind = configured_report_kind(PROJECT_ROOT, report_kind)
    metadata = build_web_report_metadata(PROJECT_ROOT)
    return finalize_web_report(
        project_root=PROJECT_ROOT,
        results_dir=results_dir,
        report_kind=kind,
        output_dir=output_dir,
        allure_output_dir=allure_output_dir,
        summary_output_dir=summary_output_dir,
        metadata=metadata,
        logger=LOGGER,
    )


def _open_helpers_catalog(args: argparse.Namespace) -> int:
    if args.guide:
        guide_path = PROJECT_ROOT / "docs" / "FRAMEWORK_HELPERS.md"
        print(guide_path)
        return 0 if guide_path.exists() else 1

    catalog_path = PROJECT_ROOT / "docs" / "helpers_catalog.html"
    if not catalog_path.exists():
        print(f"Helpers catalog not found: {catalog_path}")
        return 1
    return 0 if _open_path(catalog_path) else 1


def _run_doctor(args: argparse.Namespace) -> int:
    doctor = Doctor()
    print("Framework Doctor\n================")
    _check_python(doctor)
    _check_project_files(doctor)
    _check_yaml_config(doctor)
    _check_python_dependencies(doctor)
    _check_playwright_browsers(doctor)
    _check_allure(doctor, install=args.install_allure)
    _check_artifact_directories(doctor)
    _check_email_env(doctor)

    if args.strict and doctor.warnings:
        doctor.fail(f"Strict mode treats {doctor.warnings} warning(s) as failures.")

    print("\nSummary")
    print(f"Failures: {doctor.failed}")
    print(f"Warnings: {doctor.warnings}")
    if doctor.failed:
        print("Status: NOT READY")
    elif doctor.warnings:
        print("Status: READY WITH WARNINGS")
    else:
        print("Status: READY")
    return doctor.exit_code()


def _check_python(doctor: Doctor) -> None:
    version = sys.version_info
    if version >= (3, 10):
        doctor.pass_(f"Python {version.major}.{version.minor}.{version.micro}")
    else:
        doctor.fail(f"Python 3.10+ is required. Current: {version.major}.{version.minor}.{version.micro}")


def _check_project_files(doctor: Doctor) -> None:
    required_files = [
        "config/settings.yaml",
        "config/environments.yaml",
        "data/users.json",
        "data/checkout_data.json",
        "conftest.py",
        "pytest.ini",
        "requirements.txt",
        "scripts/run_browser_matrix.py",
        "docs/helpers_catalog.html",
        "docs/FRAMEWORK_HELPERS.md",
    ]
    for relative_path in required_files:
        path = PROJECT_ROOT / relative_path
        if path.exists():
            doctor.pass_(f"Found {relative_path}")
        else:
            doctor.fail(f"Missing {relative_path}")


def _check_yaml_config(doctor: Doctor) -> None:
    reader = ConfigReader(PROJECT_ROOT)
    try:
        settings = reader.read_settings()
        environments = reader.read_environments()
        configured_browsers = settings.get("execution", {}).get("browsers", [])
        invalid_browsers = [browser for browser in configured_browsers if browser not in VALID_BROWSERS]
        if invalid_browsers:
            doctor.fail(f"Invalid configured browser(s): {', '.join(invalid_browsers)}")
        else:
            doctor.pass_("settings.yaml is valid")
        if environments:
            doctor.pass_(f"environments.yaml has environments: {', '.join(sorted(environments))}")
        else:
            doctor.fail("environments.yaml has no environments")
    except Exception as error:
        doctor.fail(f"Could not read YAML config: {error}")


def _check_python_dependencies(doctor: Doctor) -> None:
    imports = {
        "pytest": "pytest",
        "playwright": "playwright",
        "pytest-playwright": "pytest_playwright",
        "allure-pytest": "allure_pytest",
        "yaml": "yaml",
        "requests": "requests",
        "pypdf": "pypdf",
    }
    for label, module_name in imports.items():
        if importlib.util.find_spec(module_name):
            doctor.pass_(f"Python dependency import works: {label}")
        else:
            doctor.fail(f"Missing Python dependency: {label}. Run pip install -r requirements.txt")


def _check_playwright_browsers(doctor: Doctor) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as error:
        doctor.fail(f"Could not import Playwright: {error}")
        return

    try:
        with sync_playwright() as playwright:
            for browser_name in sorted(VALID_BROWSERS):
                browser_type = getattr(playwright, browser_name)
                executable_path = Path(browser_type.executable_path)
                if executable_path.exists():
                    doctor.pass_(f"Playwright {browser_name} browser is installed")
                else:
                    doctor.fail(f"Playwright {browser_name} browser is missing. Run: playwright install")
    except Exception as error:
        doctor.fail(f"Could not inspect Playwright browsers: {error}")


def _check_allure(doctor: Doctor, install: bool) -> None:
    if shutil.which("allure"):
        doctor.pass_("Allure CLI is available on PATH")
        return
    if install:
        executable = get_or_install_allure_cli(PROJECT_ROOT, LOGGER)
        if executable:
            doctor.pass_(f"Local Allure CLI is installed: {executable}")
        else:
            doctor.warn("Allure CLI is unavailable. Core report generation still works.")
        return
    local_allure = PROJECT_ROOT / ".tools" / "allure"
    if local_allure.exists():
        doctor.pass_("Local Allure CLI cache exists under .tools/allure")
    else:
        doctor.warn("Allure CLI is not on PATH. Required only for --report-kind allure or both.")


def _check_artifact_directories(doctor: Doctor) -> None:
    for directory in ("reports", "screenshots", "videos", "traces"):
        path = PROJECT_ROOT / directory
        path.mkdir(parents=True, exist_ok=True)
        if os.access(path, os.W_OK):
            doctor.pass_(f"Artifact directory is writable: {directory}")
        else:
            doctor.fail(f"Artifact directory is not writable: {directory}")


def _check_email_env(doctor: Doctor) -> None:
    try:
        email_config = ConfigReader(PROJECT_ROOT).read_settings().get("email", {})
    except Exception:
        return
    username_env = email_config.get("username_env")
    password_env = email_config.get("password_env")
    missing = [env_name for env_name in (username_env, password_env) if env_name and not os.getenv(env_name)]
    if missing:
        doctor.warn(
            "Email helper env vars are not set: " + ", ".join(missing) + ". Required only for real IMAP/OTP scenarios."
        )
    else:
        doctor.pass_("Email helper environment variables are available or not required")


def _run_command(command: list[str]) -> int:
    print("$ " + " ".join(command), flush=True)
    completed = subprocess.run(command, cwd=PROJECT_ROOT)
    return completed.returncode


def _open_path(path: Path) -> bool:
    return open_report(path, LOGGER)


if __name__ == "__main__":
    raise SystemExit(main())
