from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import shutil
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from utils.config_reader import ConfigReader
from utils.logger import get_logger
from utils.report_opener import open_report
from utils.report_generator import (
    generate_browser_matrix_dashboard,
    read_allure_results,
    summarize_results,
)
from utils.reporting import (
    VALID_REPORT_KINDS,
    build_web_report_metadata,
    configured_report_kind,
    finalize_web_report,
    primary_report_path,
)


LOGGER = get_logger("browser-matrix")
VALID_BROWSERS = {"chromium", "firefox", "webkit"}


def main() -> int:
    args, extra_pytest_args = _parse_args()
    settings = ConfigReader(PROJECT_ROOT).read_settings()
    browsers = _resolve_browsers(args.browsers, settings)
    browser_workers = _resolve_browser_workers(
        args.browser_workers,
        settings,
        len(browsers),
    )
    _warn_about_nested_parallelism(browser_workers, args.parallel_workers)

    matrix_dir = PROJECT_ROOT / "reports" / "browser-matrix"
    results_root = matrix_dir / "results"
    reports_root = matrix_dir / "reports"
    logs_root = matrix_dir / "logs"
    matrix_dir.mkdir(parents=True, exist_ok=True)
    for run_root in (results_root, logs_root):
        if run_root.exists():
            shutil.rmtree(run_root)
        run_root.mkdir(parents=True, exist_ok=True)
    if not args.no_generate_report:
        if reports_root.exists():
            shutil.rmtree(reports_root)
        reports_root.mkdir(parents=True, exist_ok=True)
        legacy_official_reports_root = matrix_dir / "official-allure-reports"
        if legacy_official_reports_root.exists():
            shutil.rmtree(legacy_official_reports_root)

    browser_runs: list[dict] = []
    exit_code = 0

    pytest_runs = _run_pytest_browser_matrix(
        browsers,
        browser_workers,
        args,
        extra_pytest_args,
        results_root,
        logs_root,
    )

    if args.no_generate_report:
        return max((pytest_run["exit_code"] for pytest_run in pytest_runs), default=0)

    report_kind = configured_report_kind(PROJECT_ROOT, args.report_kind)

    for pytest_run in pytest_runs:
        browser = pytest_run["browser"]
        results_dir = pytest_run["results_dir"]
        report_dir = reports_root / browser
        browser_exit_code = pytest_run["exit_code"]
        exit_code = max(exit_code, browser_exit_code)

        report_path = _generate_browser_report(
            results_dir,
            report_dir,
            report_kind=report_kind,
            browser=browser,
            env_name=args.env,
        )
        tests = read_allure_results(results_dir)
        summary = summarize_results(tests)
        if browser_exit_code != 0 and summary["status"] == "passed":
            summary["status"] = "failed"

        browser_runs.append(
            {
                "browser": browser,
                "exit_code": browser_exit_code,
                "summary": summary,
                "report_path": report_path,
                "report_href": _relative_href(matrix_dir, report_path),
                "log_href": f"logs/{browser}.log",
            }
        )

    dashboard_path = generate_browser_matrix_dashboard(browser_runs, matrix_dir)
    LOGGER.info("Generated browser matrix dashboard: %s", dashboard_path)

    if not args.no_open_report:
        _open_report_if_local(dashboard_path)

    return exit_code


def _parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(description="Run pytest once per browser and build a browser matrix dashboard.")
    parser.add_argument(
        "--browsers",
        nargs="+",
        help="Browsers to run. Defaults to execution.browsers in config/settings.yaml.",
    )
    parser.add_argument("--env", default="qa", help="Environment name.")
    parser.add_argument("--base-url", help="Override the environment base URL.")
    parser.add_argument("-m", "--markers", help="Pytest marker expression.")
    parser.add_argument("--headed", action="store_true", help="Run headed browsers.")
    parser.add_argument("-n", "--parallel-workers", help="pytest-xdist worker count.")
    parser.add_argument(
        "--browser-workers",
        type=int,
        help="Number of browsers to execute in parallel. Defaults to execution.browser_workers.",
    )
    parser.add_argument("--reruns", help="Retry failed tests.")
    parser.add_argument("--reruns-delay", help="Delay between retries.")
    parser.add_argument(
        "--run-reporting-demo",
        action="store_true",
        help="Include the intentional reporting demo failure.",
    )
    parser.add_argument(
        "--no-open-report",
        action="store_true",
        help="Do not open the matrix dashboard in the default browser.",
    )
    parser.add_argument(
        "--no-generate-report",
        action="store_true",
        help="Run pytest per browser without generating browser reports or the matrix dashboard.",
    )
    parser.add_argument(
        "--report-kind",
        choices=VALID_REPORT_KINDS,
        help="Per-browser report kind: core, allure, both, or summary. Defaults to config/settings.yaml.",
    )
    return parser.parse_known_args()


def _resolve_browsers(
    cli_browsers: list[str] | None,
    settings: dict,
) -> list[str]:
    configured_browsers = settings.get("execution", {}).get("browsers", ["chromium"])
    browsers = cli_browsers or configured_browsers
    invalid = [browser for browser in browsers if browser not in VALID_BROWSERS]
    if invalid:
        raise SystemExit(f"Invalid browser(s): {', '.join(invalid)}")
    return browsers


def _resolve_browser_workers(
    cli_browser_workers: int | None,
    settings: dict,
    browser_count: int,
) -> int:
    configured_workers = settings.get("execution", {}).get("browser_workers", 1)
    workers = cli_browser_workers if cli_browser_workers is not None else configured_workers
    if workers < 1:
        raise SystemExit("--browser-workers must be 1 or greater")
    return min(workers, browser_count)


def _warn_about_nested_parallelism(
    browser_workers: int,
    test_workers: str | None,
) -> None:
    if browser_workers <= 1 or not test_workers:
        return
    if not test_workers.isdigit():
        LOGGER.warning(
            "Browser-level parallelism is enabled with pytest workers '%s'. "
            "Check total machine capacity because both levels multiply browser load.",
            test_workers,
        )
        return

    total_workers = browser_workers * int(test_workers)
    LOGGER.warning(
        "Nested parallelism enabled: %s browser workers x %s pytest workers = up to %s concurrent test workers. "
        "Lower --browser-workers or -n if the machine becomes unstable.",
        browser_workers,
        test_workers,
        total_workers,
    )


def _run_pytest_browser_matrix(
    browsers: list[str],
    browser_workers: int,
    args: argparse.Namespace,
    extra_pytest_args: list[str],
    results_root: Path,
    logs_root: Path,
) -> list[dict]:
    LOGGER.info(
        "Executing browser matrix with %s browser worker(s): %s",
        browser_workers,
        ", ".join(browsers),
    )
    if browser_workers == 1:
        return [
            _run_pytest_for_browser(
                browser,
                args,
                extra_pytest_args,
                results_root / browser,
                logs_root / f"{browser}.log",
            )
            for browser in browsers
        ]

    results_by_browser: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=browser_workers) as executor:
        futures = {
            executor.submit(
                _run_pytest_for_browser,
                browser,
                args,
                extra_pytest_args,
                results_root / browser,
                logs_root / f"{browser}.log",
            ): browser
            for browser in browsers
        }
        for future in as_completed(futures):
            browser = futures[future]
            results_by_browser[browser] = future.result()
            LOGGER.info(
                "Finished browser matrix run: %s with exit code %s",
                browser,
                results_by_browser[browser]["exit_code"],
            )

    return [results_by_browser[browser] for browser in browsers]


def _run_pytest_for_browser(
    browser: str,
    args: argparse.Namespace,
    extra_pytest_args: list[str],
    results_dir: Path,
    log_path: Path,
) -> dict:
    LOGGER.info("Starting browser matrix run: %s", browser)
    results_dir.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        "-m",
        "pytest",
        "--browser",
        browser,
        "--env",
        args.env,
        f"--alluredir={results_dir}",
        "--clean-alluredir",
        "--no-generate-report",
        "--no-open-report",
    ]
    if args.markers:
        command.extend(["-m", args.markers])
    if args.base_url:
        command.extend(["--base-url", args.base_url])
    if args.headed:
        command.append("--headed")
    if args.parallel_workers:
        command.extend(["-n", args.parallel_workers])
    if args.reruns:
        command.extend(["--reruns", args.reruns])
    if args.reruns_delay:
        command.extend(["--reruns-delay", args.reruns_delay])
    if args.run_reporting_demo:
        command.append("--run-reporting-demo")
    command.extend(extra_pytest_args)

    LOGGER.info("Executing: %s", " ".join(command))
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    _write_browser_log(log_path, command, completed)
    LOGGER.info(
        "Browser %s finished with exit code %s. Log: %s",
        browser,
        completed.returncode,
        log_path,
    )
    return {
        "browser": browser,
        "exit_code": completed.returncode,
        "results_dir": results_dir,
        "log_path": log_path,
    }


def _write_browser_log(
    log_path: Path,
    command: list[str],
    completed: subprocess.CompletedProcess,
) -> None:
    log_path.write_text(
        "$ "
        + " ".join(command)
        + "\n\n=== STDOUT ===\n"
        + completed.stdout
        + "\n\n=== STDERR ===\n"
        + completed.stderr,
        encoding="utf-8",
    )


def _generate_browser_report(
    results_dir: Path,
    report_dir: Path,
    *,
    report_kind: str,
    browser: str,
    env_name: str,
) -> Path:
    framework_config = _load_framework_config(env_name)
    metadata = build_web_report_metadata(
        PROJECT_ROOT,
        framework_config=framework_config,
        browser=browser,
        extra={"browser_matrix": True},
    )
    result = finalize_web_report(
        project_root=PROJECT_ROOT,
        results_dir=results_dir,
        report_kind=report_kind,
        output_dir=report_dir,
        allure_output_dir=report_dir / "allure",
        summary_output_dir=report_dir,
        metadata=metadata,
        logger=LOGGER,
    )
    report_path = primary_report_path(result)
    if report_path:
        return report_path
    LOGGER.warning("No browser report was generated for %s; dashboard will link to the expected path.", browser)
    return report_dir / "index.html"


def _load_framework_config(env_name: str) -> dict:
    try:
        return ConfigReader(PROJECT_ROOT).load(env_name)
    except Exception as error:
        LOGGER.warning("Could not load framework metadata for browser matrix report: %s", error)
        return {}


def _open_report_if_local(report_path: Path) -> None:
    open_report(report_path, LOGGER)


def _relative_href(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
