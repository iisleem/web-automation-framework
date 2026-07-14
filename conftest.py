from collections.abc import Generator
from pathlib import Path
import re

import allure
import pytest
from playwright.sync_api import Browser, Error, Page

from utils.config_reader import ConfigReader
from utils.data_reader import DataReader
from utils.helpers.email import EmailOtpHelper, ImapEmailClient
from utils.logger import get_logger
from utils.report_opener import open_report
from utils.reporting import (
    VALID_REPORT_KINDS,
    build_web_report_metadata,
    configured_report_kind,
    finalize_web_report,
    primary_report_path,
)
from utils.screenshot_helper import capture_screenshot


PROJECT_ROOT = Path(__file__).resolve().parent
LOGGER = get_logger("framework")
ARTIFACT_DIRECTORIES = ("reports", "screenshots", "videos", "traces")


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("web-automation-framework")
    group.addoption(
        "--env",
        action="store",
        default="qa",
        help="Environment name from config/environments.yaml. Example: --env qa",
    )
    group.addoption(
        "--run-reporting-demo",
        action="store_true",
        default=False,
        help="Include the intentionally failing reporting demo test.",
    )
    group.addoption(
        "--no-generate-report",
        action="store_true",
        default=False,
        help="Do not generate the HTML report after the test session.",
    )
    group.addoption(
        "--no-open-report",
        action="store_true",
        default=False,
        help="Do not open the generated HTML report in the default browser.",
    )
    group.addoption(
        "--report-kind",
        action="store",
        choices=VALID_REPORT_KINDS,
        default=None,
        help="Post-run report kind: core, allure, both, or summary. Defaults to config/settings.yaml.",
    )


def pytest_configure() -> None:
    for directory in ARTIFACT_DIRECTORIES:
        (PROJECT_ROOT / directory).mkdir(parents=True, exist_ok=True)


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    if config.getoption("--run-reporting-demo"):
        return

    skip_reporting_demo = pytest.mark.skip(
        reason="Intentional reporting demo. Run with --run-reporting-demo to include it."
    )
    for item in items:
        if "reporting_demo" in item.keywords:
            item.add_marker(skip_reporting_demo)


def pytest_sessionfinish(
    session: pytest.Session,
    exitstatus: int,
) -> None:
    if hasattr(session.config, "workerinput"):
        return
    if session.config.getoption("--no-generate-report"):
        return

    report_path = _generate_report_after_session(session.config)
    if report_path and not session.config.getoption("--no-open-report"):
        _open_report_if_local(report_path)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo,
) -> Generator[None, None, None]:
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture(scope="session")
def framework_config(pytestconfig: pytest.Config) -> dict:
    env_name = pytestconfig.getoption("--env")
    config = ConfigReader(PROJECT_ROOT).load(env_name)
    LOGGER.info("Loaded framework config for environment: %s", env_name)
    return config


@pytest.fixture(scope="session")
def base_url(pytestconfig: pytest.Config, framework_config: dict) -> str:
    cli_base_url = pytestconfig.getoption("base_url", default=None)
    return cli_base_url or framework_config["base_url"]


@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: dict,
    framework_config: dict,
) -> dict:
    video_dir = PROJECT_ROOT / framework_config["artifacts"]["videos_dir"]
    video_dir.mkdir(parents=True, exist_ok=True)

    return {
        **browser_context_args,
        "viewport": framework_config["browser"]["viewport"],
        "ignore_https_errors": framework_config["browser"]["ignore_https_errors"],
        "record_video_dir": str(video_dir),
        "record_video_size": framework_config["browser"]["record_video_size"],
    }


@pytest.fixture
def page(
    browser: Browser,
    browser_context_args: dict,
    framework_config: dict,
    request: pytest.FixtureRequest,
) -> Generator[Page, None, None]:
    test_name = _safe_artifact_name(request.node.nodeid)
    context = browser.new_context(**browser_context_args)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)

    page = context.new_page()
    page.set_default_timeout(framework_config["timeouts"]["default_timeout_ms"])
    page.set_default_navigation_timeout(framework_config["timeouts"]["navigation_timeout_ms"])

    LOGGER.info("Starting test: %s", request.node.nodeid)
    try:
        yield page
    finally:
        failed = bool(getattr(request.node, "rep_call", None) and request.node.rep_call.failed)
        video = page.video

        if failed:
            _capture_and_attach_screenshot(page, framework_config, test_name)

        _stop_tracing(context, framework_config, test_name, failed)
        try:
            context.close()
        except Error as error:
            LOGGER.error("Could not close browser context cleanly: %s", error)
        _handle_video(video, framework_config, test_name, failed)

        LOGGER.info("Finished test: %s", request.node.nodeid)


@pytest.fixture(scope="session")
def users() -> dict:
    return DataReader(PROJECT_ROOT).read_json("users.json")


@pytest.fixture(scope="session")
def checkout_data() -> dict:
    return DataReader(PROJECT_ROOT).read_json("checkout_data.json")


@pytest.fixture(scope="session")
def email_client(framework_config: dict) -> ImapEmailClient:
    return ImapEmailClient.from_config(framework_config["email"])


@pytest.fixture(scope="session")
def email_otp_helper(
    email_client: ImapEmailClient,
    framework_config: dict,
) -> EmailOtpHelper:
    email_config = framework_config["email"]
    return EmailOtpHelper(
        email_client=email_client,
        mailbox=email_config.get("mailbox", "INBOX"),
        default_regex=email_config.get("default_otp_regex", r"\b\d{4,8}\b"),
    )


def _safe_artifact_name(nodeid: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", nodeid).strip("_")


def _capture_and_attach_screenshot(
    page: Page,
    framework_config: dict,
    test_name: str,
) -> None:
    screenshot_path = PROJECT_ROOT / framework_config["artifacts"]["screenshots_dir"] / f"{test_name}.png"
    try:
        capture_screenshot(page, screenshot_path)
        _attach_file(
            screenshot_path,
            "failure screenshot",
            allure.attachment_type.PNG,
        )
        LOGGER.error("Test failed. Screenshot captured: %s", screenshot_path)
    except Error as error:
        LOGGER.error("Could not capture screenshot for failed test: %s", error)


def _stop_tracing(
    context,
    framework_config: dict,
    test_name: str,
    failed: bool,
) -> None:
    trace_path = PROJECT_ROOT / framework_config["artifacts"]["traces_dir"] / f"{test_name}.zip"
    try:
        if failed:
            trace_path.parent.mkdir(parents=True, exist_ok=True)
            context.tracing.stop(path=str(trace_path))
            _attach_file(trace_path, "playwright trace", "application/zip", "zip")
            LOGGER.error("Trace captured: %s", trace_path)
        else:
            context.tracing.stop()
    except Error as error:
        LOGGER.error("Could not stop Playwright tracing cleanly: %s", error)


def _handle_video(
    video,
    framework_config: dict,
    test_name: str,
    failed: bool,
) -> None:
    if not video:
        return

    if failed:
        video_path = PROJECT_ROOT / framework_config["artifacts"]["videos_dir"] / f"{test_name}.webm"
        try:
            video.save_as(str(video_path))
            video.delete()
            _attach_file(video_path, "failure video", "video/webm", "webm")
            LOGGER.error("Video captured: %s", video_path)
        except Error as error:
            LOGGER.error("Could not preserve failure video: %s", error)
    else:
        try:
            video.delete()
        except Error as error:
            LOGGER.warning("Could not delete passed-test video: %s", error)


def _attach_file(
    path: Path,
    name: str,
    attachment_type,
    extension: str | None = None,
) -> None:
    try:
        allure.attach.file(
            str(path),
            name=name,
            attachment_type=attachment_type,
            extension=extension,
        )
    except Exception as error:
        LOGGER.error("Could not attach %s to Allure: %s", path, error)


def _generate_report_after_session(config: pytest.Config) -> Path | None:
    framework_config = _load_framework_config_for_reporting(config)
    results_dir = PROJECT_ROOT / "reports" / "allure-results"
    report_kind = configured_report_kind(PROJECT_ROOT, config.getoption("--report-kind"))
    metadata = build_web_report_metadata(
        PROJECT_ROOT,
        framework_config=framework_config,
        browser=config.getoption("browser", default=None),
    )
    try:
        result = finalize_web_report(
            project_root=PROJECT_ROOT,
            results_dir=results_dir,
            report_kind=report_kind,
            metadata=metadata,
            logger=LOGGER,
        )
        return primary_report_path(result)
    except Exception as error:
        LOGGER.warning("Could not generate report after test session: %s", error)
        return None


def _open_report_if_local(report_path: Path) -> None:
    open_report(report_path, LOGGER)


def _load_framework_config_for_reporting(config: pytest.Config) -> dict:
    try:
        env_name = config.getoption("--env")
        return ConfigReader(PROJECT_ROOT).load(env_name)
    except Exception as error:
        LOGGER.warning("Could not load framework metadata for report: %s", error)
        return {}
