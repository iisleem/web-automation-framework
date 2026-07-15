from pathlib import Path
from types import SimpleNamespace

import pytest

import framework
from utils import reporting


pytestmark = pytest.mark.helpers


def test_finalize_web_report_uses_core_default_paths(tmp_path, monkeypatch):
    _write_settings(tmp_path)
    results_dir = tmp_path / "reports" / "allure-results"
    results_dir.mkdir(parents=True)
    captured = {}

    def fake_finalize_allure_reporting(**kwargs):
        captured.update(kwargs)
        index_path = Path(kwargs["output_dir"]) / "index.html"
        return _result("core", core_path=index_path)

    monkeypatch.setattr(
        reporting,
        "finalize_allure_reporting",
        fake_finalize_allure_reporting,
    )

    result = reporting.finalize_web_report(
        project_root=tmp_path,
        results_dir=results_dir,
        metadata={"path": Path("screenshots/failure.png")},
    )

    assert result.ok
    assert captured["report_kind"] == "core"
    assert captured["output_dir"] == tmp_path / "reports" / "automation-report"
    assert captured["allure_output_dir"] == tmp_path / "reports" / "allure-report"
    assert captured["metadata"]["path"] == "screenshots/failure.png"
    assert reporting.primary_report_path(result) == tmp_path / "reports" / "automation-report" / "index.html"


def test_finalize_web_report_passes_core_report_enrichers(tmp_path, monkeypatch):
    _write_settings(tmp_path)
    results_dir = tmp_path / "reports" / "allure-results"
    results_dir.mkdir(parents=True)
    captured = {}

    def fake_finalize_allure_reporting(**kwargs):
        captured.update(kwargs)
        index_path = Path(kwargs["output_dir"]) / "index.html"
        return _result("core", core_path=index_path)

    monkeypatch.setattr(
        reporting,
        "finalize_allure_reporting",
        fake_finalize_allure_reporting,
    )

    result = reporting.finalize_web_report(project_root=tmp_path, results_dir=results_dir)

    assert result.ok
    assert captured["metadata"]["artifacts"]["healing_audit"] == "reports/healing/events.jsonl"
    assert captured["enrichers"]


def test_finalize_web_report_keeps_allure_optional_for_both(tmp_path, monkeypatch):
    _write_settings(tmp_path)
    results_dir = tmp_path / "reports" / "allure-results"
    results_dir.mkdir(parents=True)
    captured = {}

    def fake_finalize_allure_reporting(**kwargs):
        captured.update(kwargs)
        core_path = Path(kwargs["output_dir"]) / "index.html"
        return _result(
            "both",
            core_path=core_path,
            warnings=["Official Allure CLI was not found; core reporting remains available."],
        )

    monkeypatch.setattr(
        reporting,
        "finalize_allure_reporting",
        fake_finalize_allure_reporting,
    )

    result = reporting.finalize_web_report(
        project_root=tmp_path,
        results_dir=results_dir,
        report_kind="both",
    )

    assert result.ok
    assert captured["report_kind"] == "both"
    assert captured["install_allure_cli"] is True
    assert reporting.primary_report_path(result) == tmp_path / "reports" / "automation-report" / "index.html"


def test_framework_cli_accepts_report_kind_options():
    parser = framework._build_parser()

    run_args, _ = parser.parse_known_args(["run", "--report-kind", "both"])
    generate_args, _ = parser.parse_known_args(["report", "generate", "--report-kind", "allure", "--no-open"])

    assert run_args.report_kind == "both"
    assert generate_args.report_kind == "allure"


def test_framework_report_open_prefers_core_report(tmp_path, monkeypatch):
    core_report = tmp_path / "reports" / "automation-report" / "index.html"
    allure_report = tmp_path / "reports" / "allure-report" / "index.html"
    core_report.parent.mkdir(parents=True)
    allure_report.parent.mkdir(parents=True)
    core_report.write_text("<html>core</html>", encoding="utf-8")
    allure_report.write_text("<html>allure</html>", encoding="utf-8")
    monkeypatch.setattr(framework, "PROJECT_ROOT", tmp_path)

    assert framework._find_report("core") == core_report
    assert framework._find_report("allure") == allure_report


def _write_settings(project_root: Path) -> None:
    config_dir = project_root / "config"
    config_dir.mkdir()
    (config_dir / "settings.yaml").write_text(
        """
reporting:
  report_kind: core
  core_report_dir: reports/automation-report
  allure_report_dir: reports/allure-report
  summary_report_dir: reports/summary-report
""".strip(),
        encoding="utf-8",
    )


def _status(path=None, generated=True, requested=True):
    return SimpleNamespace(
        requested=requested,
        generated=generated,
        path=str(path) if path else None,
        status="generated" if generated else "skipped",
        error="",
        warnings=[],
    )


def _result(report_kind, *, core_path=None, summary_path=None, allure_path=None, warnings=None):
    result = SimpleNamespace(
        report_kind=report_kind,
        core=_status(core_path, generated=bool(core_path), requested=report_kind in {"core", "both"}),
        summary=_status(summary_path, generated=bool(summary_path), requested=report_kind == "summary"),
        allure=_status(allure_path, generated=bool(allure_path), requested=report_kind in {"allure", "both"}),
        warnings=warnings or [],
        errors=[],
    )
    result.ok = bool(core_path or summary_path or allure_path)
    return result
