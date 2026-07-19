from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from automation_core.reporting import finalize_allure_reporting

from utils.config_reader import ConfigReader
from utils.runtime_healing import DEFAULT_AUDIT_PATH, healing_report_enricher


ReportKind = Literal["core", "summary", "allure", "both"]
VALID_REPORT_KINDS = ("core", "summary", "allure", "both")
PROJECT_NAME = "web-automation-framework"
FRAMEWORK_NAME = "python-playwright-pytest"


def normalize_report_kind(report_kind: str | None) -> ReportKind:
    kind = (report_kind or "core").strip().lower()
    if kind not in VALID_REPORT_KINDS:
        raise ValueError(f"Invalid report kind '{report_kind}'. Expected one of: " + ", ".join(VALID_REPORT_KINDS))
    return kind  # type: ignore[return-value]


def configured_report_kind(project_root: Path, report_kind: str | None = None) -> ReportKind:
    if report_kind:
        return normalize_report_kind(report_kind)
    settings = ConfigReader(project_root).read_settings()
    return normalize_report_kind(settings.get("reporting", {}).get("report_kind", "core"))


def report_paths(
    project_root: Path,
    *,
    output_dir: Path | str | None = None,
    allure_output_dir: Path | str | None = None,
    summary_output_dir: Path | str | None = None,
) -> dict[str, Path]:
    reporting = ConfigReader(project_root).read_settings().get("reporting", {})
    return {
        "core": _resolve_project_path(
            project_root,
            output_dir or reporting.get("core_report_dir", "reports/automation-report"),
        ),
        "allure": _resolve_project_path(
            project_root,
            allure_output_dir or reporting.get("allure_report_dir", "reports/allure-report"),
        ),
        "summary": _resolve_project_path(
            project_root,
            summary_output_dir or reporting.get("summary_report_dir", "reports/summary-report"),
        ),
    }


def primary_output_dir(paths: dict[str, Path], report_kind: str) -> Path:
    kind = normalize_report_kind(report_kind)
    if kind == "allure":
        return paths["allure"]
    if kind == "summary":
        return paths["summary"]
    return paths["core"]


def primary_report_path(result) -> Path | None:
    if result.report_kind == "allure" and result.allure.generated and result.allure.path:
        return Path(result.allure.path)
    if result.report_kind == "summary" and result.summary.generated and result.summary.path:
        return Path(result.summary.path)
    if result.core.generated and result.core.path:
        return Path(result.core.path)
    if result.summary.generated and result.summary.path:
        return Path(result.summary.path)
    if result.allure.generated and result.allure.path:
        return Path(result.allure.path)
    return None


def build_web_report_metadata(
    project_root: Path,
    *,
    framework_config: dict[str, Any] | None = None,
    browser: Any = None,
    profile: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = framework_config or {}
    browser_settings = config.get("browser", {})
    artifacts = config.get("artifacts", {})
    metadata: dict[str, Any] = {
        "domain": "web",
        "framework": PROJECT_NAME,
        "automation_engine": "playwright",
        "test_runner": "pytest",
        "environment": config.get("env"),
        "base_url": config.get("base_url"),
        "browser": _serializable_browser(browser),
        "profile": profile,
        "viewport": browser_settings.get("viewport"),
        "artifacts": {
            "allure_results": _as_relative_string(
                project_root,
                artifacts.get("allure_results_dir", "reports/allure-results"),
            ),
            "screenshots_dir": _as_relative_string(
                project_root,
                artifacts.get("screenshots_dir", "screenshots"),
            ),
            "videos_dir": _as_relative_string(
                project_root,
                artifacts.get("videos_dir", "videos"),
            ),
            "traces_dir": _as_relative_string(
                project_root,
                artifacts.get("traces_dir", "traces"),
            ),
            "healing_audit": _as_relative_string(
                project_root,
                config.get("runtime_healing", {}).get("audit_path", DEFAULT_AUDIT_PATH),
            ),
        },
    }
    if extra:
        metadata.update(_make_json_safe(extra))
    return _make_json_safe(metadata)


def finalize_web_report(
    *,
    project_root: Path,
    results_dir: Path,
    report_kind: str | None = None,
    output_dir: Path | str | None = None,
    allure_output_dir: Path | str | None = None,
    summary_output_dir: Path | str | None = None,
    open_report: bool = False,
    open_target: str = "auto",
    missing_ok: bool = False,
    metadata: dict[str, Any] | None = None,
    logger=None,
) -> Any:
    kind = configured_report_kind(project_root, report_kind)
    if kind == "allure" and output_dir is not None and allure_output_dir is None:
        allure_output_dir = output_dir
    if kind == "summary" and output_dir is not None and summary_output_dir is None:
        summary_output_dir = output_dir
    paths = report_paths(
        project_root,
        output_dir=output_dir,
        allure_output_dir=allure_output_dir,
        summary_output_dir=summary_output_dir,
    )
    report_metadata = _make_json_safe(metadata) if metadata else build_web_report_metadata(project_root)
    result = finalize_allure_reporting(
        results_dir=results_dir,
        output_dir=primary_output_dir(paths, kind),
        project_name=PROJECT_NAME,
        framework=FRAMEWORK_NAME,
        report_kind=kind,
        open_report=open_report,
        open_target=open_target,
        missing_ok=missing_ok,
        allure_output_dir=paths["allure"],
        summary_output_dir=paths["summary"],
        metadata=report_metadata,
        test_metadata=build_web_test_metadata(results_dir, report_metadata),
        enrichers=[healing_report_enricher(_healing_audit_path(project_root, report_metadata))],
        install_allure_cli=True,
        logger=logger,
    )
    _log_reporting_result(result, logger)
    return result


def build_web_test_metadata(results_dir: Path, metadata: dict[str, Any]) -> dict[str, dict[str, Any]]:
    base_metadata = _test_metadata_from_run_metadata(metadata)
    if not base_metadata:
        return {}

    test_metadata: dict[str, dict[str, Any]] = {}
    for result_path in sorted(Path(results_dir).glob("*-result.json")):
        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        entry = {
            **base_metadata,
            **_test_metadata_from_allure_result(result),
        }
        for key in (result.get("historyId"), result.get("fullName"), result.get("name")):
            if key:
                test_metadata[str(key)] = entry
    return test_metadata


def _test_metadata_from_run_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    artifacts = metadata.get("artifacts", {})
    capabilities = {
        "automation_engine": metadata.get("automation_engine"),
        "test_runner": metadata.get("test_runner"),
        "viewport": metadata.get("viewport"),
    }
    return _make_json_safe(
        {
            "domain": metadata.get("domain", "web"),
            "environment": metadata.get("environment"),
            "profile": metadata.get("profile"),
            "browser": metadata.get("browser"),
            "capabilities": {key: value for key, value in capabilities.items() if value not in (None, "")},
            "artifact_roots": artifacts,
            "base_url": metadata.get("base_url"),
        }
    )


def _test_metadata_from_allure_result(result: dict[str, Any]) -> dict[str, Any]:
    parameters = _allure_parameters(result)
    browser = parameters.get("browser") or parameters.get("browser_name")
    if browser:
        return {"browser": _strip_parameter_quotes(browser), "profile": _strip_parameter_quotes(browser)}
    return {}


def _allure_parameters(result: dict[str, Any]) -> dict[str, str]:
    parameters: dict[str, str] = {}
    for parameter in result.get("parameters", []):
        name = parameter.get("name")
        value = parameter.get("value")
        if name and value is not None:
            parameters[str(name)] = str(value)
    return parameters


def _strip_parameter_quotes(value: str) -> str:
    stripped = value.strip()
    if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in {"'", '"'}:
        return stripped[1:-1]
    return stripped


def _healing_audit_path(project_root: Path, metadata: dict[str, Any]) -> Path:
    audit_path = metadata.get("artifacts", {}).get("healing_audit")
    if not audit_path:
        audit_path = (
            ConfigReader(project_root).read_settings().get("runtime_healing", {}).get("audit_path", DEFAULT_AUDIT_PATH)
        )
    return _resolve_project_path(project_root, audit_path)


def _log_reporting_result(result, logger) -> None:
    if not logger:
        return
    report_path = primary_report_path(result)
    if report_path:
        logger.info("Generated %s report: %s", result.report_kind, report_path)
    if result.core.generated and getattr(result.core, "run_path", None):
        logger.info("Generated latest run details: %s", result.core.run_path)
    for warning in result.warnings:
        logger.warning(warning)
    for error in result.errors:
        if result.ok:
            logger.warning(error)
        else:
            logger.error(error)


def _resolve_project_path(project_root: Path, path: Path | str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return project_root / candidate


def _as_relative_string(project_root: Path, path: Path | str) -> str:
    candidate = _resolve_project_path(project_root, path)
    try:
        return str(candidate.relative_to(project_root))
    except ValueError:
        return str(candidate)


def _serializable_browser(browser: Any) -> Any:
    if browser is None:
        return None
    if isinstance(browser, (str, int, float, bool)):
        return browser
    if isinstance(browser, (list, tuple, set)):
        return [str(item) for item in browser]
    return str(browser)


def _make_json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _make_json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_make_json_safe(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)
