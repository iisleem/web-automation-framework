import argparse

import pytest

import framework
from scripts import run_browser_matrix
from utils.browser_support import (
    append_pytest_browser_args,
    browser_artifact_name,
    channel_error_message,
    resolve_browser_target,
)


pytestmark = pytest.mark.helpers


def test_browser_aliases_resolve_to_playwright_engine_and_channel():
    assert resolve_browser_target("chromium").engine == "chromium"
    assert resolve_browser_target("firefox").engine == "firefox"
    assert resolve_browser_target("webkit").engine == "webkit"
    assert resolve_browser_target("safari").engine == "webkit"

    chrome = resolve_browser_target("chrome")
    msedge = resolve_browser_target("msedge")

    assert chrome.engine == "chromium"
    assert chrome.channel == "chrome"
    assert msedge.engine == "chromium"
    assert msedge.channel == "msedge"


def test_pytest_browser_args_use_channels_for_real_browser_brands():
    command = ["python", "-m", "pytest"]
    append_pytest_browser_args(command, "chrome")
    assert command[-4:] == ["--browser", "chromium", "--browser-channel", "chrome"]

    command = ["python", "-m", "pytest"]
    append_pytest_browser_args(command, "msedge")
    assert command[-4:] == ["--browser", "chromium", "--browser-channel", "msedge"]

    command = ["python", "-m", "pytest"]
    append_pytest_browser_args(command, "safari")
    assert command[-2:] == ["--browser", "webkit"]


def test_framework_cli_accepts_browser_channel_names():
    parser = framework._build_parser()

    chrome_args, _ = parser.parse_known_args(["run", "--browser", "chrome"])
    matrix_args, _ = parser.parse_known_args(["run", "--browsers", "chrome", "msedge", "safari"])

    assert chrome_args.browser == "chrome"
    assert matrix_args.browsers == ["chrome", "msedge", "safari"]


def test_framework_single_browser_command_builds_browser_channel(monkeypatch):
    captured = {}

    def fake_run_command(command):
        captured["command"] = command
        return 0

    monkeypatch.setattr(framework, "_run_command", fake_run_command)
    monkeypatch.setattr(framework, "channel_preflight_failure", lambda browser: None)
    args = argparse.Namespace(
        env="qa",
        base_url=None,
        browser="chrome",
        browsers=None,
        browser_workers=None,
        headed=False,
        parallel=None,
        markers="smoke",
        smoke=False,
        regression=False,
        e2e=False,
        negative=False,
        helpers=False,
        reruns=None,
        reruns_delay=None,
        run_reporting_demo=False,
        report_kind="core",
        no_open_report=True,
        no_generate_report=False,
        matrix=False,
    )

    assert framework._run_tests(args, []) == 0
    assert "--browser" in captured["command"]
    assert captured["command"][captured["command"].index("--browser") + 1] == "chromium"
    assert "--browser-channel" in captured["command"]
    assert captured["command"][captured["command"].index("--browser-channel") + 1] == "chrome"


def test_framework_single_browser_channel_preflight_fails_before_pytest(monkeypatch, capsys):
    def fail_if_called(command):
        raise AssertionError(f"pytest command should not run: {command}")

    monkeypatch.setattr(framework, "_run_command", fail_if_called)
    monkeypatch.setattr(
        framework,
        "channel_preflight_failure",
        lambda browser: "Install Microsoft Edge or run: python -m playwright install msedge",
    )
    args = argparse.Namespace(
        env="qa",
        base_url=None,
        browser="msedge",
        browsers=None,
        browser_workers=None,
        headed=False,
        parallel=None,
        markers="smoke",
        smoke=False,
        regression=False,
        e2e=False,
        negative=False,
        helpers=False,
        reruns=None,
        reruns_delay=None,
        run_reporting_demo=False,
        report_kind="core",
        no_open_report=True,
        no_generate_report=False,
        matrix=False,
    )

    assert framework._run_tests(args, []) == 1
    assert "python -m playwright install msedge" in capsys.readouterr().err


def test_browser_matrix_uses_requested_names_for_artifacts_and_channel_args():
    command = ["python", "-m", "pytest"]
    append_pytest_browser_args(command, "msedge")

    assert browser_artifact_name("msedge") == "msedge"
    assert command[-4:] == ["--browser", "chromium", "--browser-channel", "msedge"]
    assert run_browser_matrix.VALID_BROWSERS.issuperset({"chrome", "msedge", "safari"})


def test_browser_matrix_channel_preflight_writes_log_without_pytest(monkeypatch, tmp_path):
    def fail_if_called(*args, **kwargs):
        raise AssertionError("subprocess.run should not run when channel preflight fails")

    monkeypatch.setattr(run_browser_matrix.subprocess, "run", fail_if_called)
    monkeypatch.setattr(
        run_browser_matrix,
        "channel_preflight_failure",
        lambda browser: "Install Microsoft Edge or run: python -m playwright install msedge",
    )
    args = argparse.Namespace(
        env="qa",
        markers="smoke",
        base_url=None,
        headed=False,
        parallel_workers=None,
        reruns=None,
        reruns_delay=None,
        run_reporting_demo=False,
    )

    result = run_browser_matrix._run_pytest_for_browser(
        "msedge",
        args,
        [],
        tmp_path / "results" / "msedge",
        tmp_path / "logs" / "msedge.log",
    )

    assert result["exit_code"] == 1
    log_text = (tmp_path / "logs" / "msedge.log").read_text(encoding="utf-8")
    assert "PREFLIGHT FAILURE" in log_text
    assert "python -m playwright install msedge" in log_text
    assert "pytest" not in log_text


def test_channel_error_message_is_actionable():
    message = channel_error_message("msedge")

    assert "python -m playwright install msedge" in message
    assert "--browser-channel" in message
