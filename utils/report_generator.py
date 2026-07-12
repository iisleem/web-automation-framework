from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


STATUS_ORDER = {"failed": 0, "broken": 1, "skipped": 2, "passed": 3}


def generate_html_report(results_dir: Path, output_dir: Path) -> Path:
    report_data = read_allure_results(results_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "index.html"
    report_path.write_text(_render_html(report_data), encoding="utf-8")
    return report_path


def read_allure_results(results_dir: Path) -> list[dict[str, Any]]:
    if not results_dir.exists():
        raise FileNotFoundError(f"Allure results directory not found: {results_dir}")

    tests: list[dict[str, Any]] = []
    for path in sorted(results_dir.glob("*-result.json")):
        with path.open("r", encoding="utf-8") as file:
            result = json.load(file)
        tests.append(
            {
                "name": result.get("name", path.stem),
                "full_name": result.get("fullName", ""),
                "status": result.get("status", "unknown"),
                "duration_ms": _duration_ms(result),
                "message": result.get("statusDetails", {}).get("message", ""),
            }
        )

    return sorted(
        tests,
        key=lambda item: (STATUS_ORDER.get(item["status"], 9), item["name"]),
    )


def summarize_results(tests: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {
        status: sum(1 for test in tests if test["status"] == status)
        for status in STATUS_ORDER
    }
    total = len(tests)
    passed = counts.get("passed", 0)
    failed = counts.get("failed", 0) + counts.get("broken", 0)
    duration_ms = sum(test["duration_ms"] for test in tests)
    pass_rate = round((passed / total) * 100, 2) if total else 0
    status = "passed" if total and failed == 0 else "failed"
    if total == 0:
        status = "unknown"

    return {
        "total": total,
        "passed": passed,
        "failed": counts.get("failed", 0),
        "broken": counts.get("broken", 0),
        "skipped": counts.get("skipped", 0),
        "duration_ms": duration_ms,
        "pass_rate": pass_rate,
        "status": status,
    }


def generate_browser_matrix_dashboard(
    browser_runs: list[dict[str, Any]],
    output_dir: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "index.html"
    report_path.write_text(_render_browser_matrix_html(browser_runs), encoding="utf-8")
    return report_path


def _duration_ms(result: dict[str, Any]) -> int:
    start = result.get("start", 0)
    stop = result.get("stop", start)
    return max(0, int(stop) - int(start))


def _render_html(tests: list[dict[str, Any]]) -> str:
    total = len(tests)
    counts = {
        status: sum(1 for test in tests if test["status"] == status)
        for status in STATUS_ORDER
    }
    rows = "\n".join(_render_row(test) for test in tests)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Allure Results Summary</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #1f2937; }}
    h1 {{ margin-bottom: 8px; }}
    .summary {{ display: flex; gap: 12px; margin: 24px 0; flex-wrap: wrap; }}
    .metric {{ border: 1px solid #d1d5db; border-radius: 6px; padding: 12px 16px; min-width: 110px; }}
    .metric strong {{ display: block; font-size: 24px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border-bottom: 1px solid #e5e7eb; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ background: #f9fafb; }}
    .passed {{ color: #047857; font-weight: 700; }}
    .failed, .broken {{ color: #b91c1c; font-weight: 700; }}
    .skipped {{ color: #92400e; font-weight: 700; }}
    .message {{ color: #4b5563; white-space: pre-wrap; }}
  </style>
</head>
<body>
  <h1>Allure Results Summary</h1>
  <p>Generated automatically from Allure JSON result files.</p>
  <section class="summary">
    <div class="metric"><strong>{total}</strong>Total</div>
    <div class="metric"><strong>{counts.get("passed", 0)}</strong>Passed</div>
    <div class="metric"><strong>{counts.get("failed", 0)}</strong>Failed</div>
    <div class="metric"><strong>{counts.get("broken", 0)}</strong>Broken</div>
    <div class="metric"><strong>{counts.get("skipped", 0)}</strong>Skipped</div>
  </section>
  <table>
    <thead>
      <tr>
        <th>Status</th>
        <th>Test</th>
        <th>Duration</th>
        <th>Message</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</body>
</html>
"""


def _render_row(test: dict[str, Any]) -> str:
    status = html.escape(test["status"])
    name = html.escape(test["name"])
    full_name = html.escape(test["full_name"])
    duration = f"{test['duration_ms'] / 1000:.2f}s"
    message = html.escape(test["message"])
    return f"""<tr>
  <td class="{status}">{status}</td>
  <td><strong>{name}</strong><br>{full_name}</td>
  <td>{duration}</td>
  <td class="message">{message}</td>
</tr>"""


def _render_browser_matrix_html(browser_runs: list[dict[str, Any]]) -> str:
    totals = _matrix_totals(browser_runs)
    cards = "\n".join(_render_browser_card(run) for run in browser_runs)
    rows = "\n".join(_render_browser_row(run) for run in browser_runs)
    failures = "\n".join(_render_failure_item(run) for run in browser_runs for _ in [0])
    if not failures:
        failures = "<li>No browser-level failures detected.</li>"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Browser Matrix Dashboard</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 0; color: #172033; background: #f6f7f9; }}
    header {{ background: #102033; color: #ffffff; padding: 28px 36px; }}
    h1 {{ margin: 0 0 8px; }}
    main {{ padding: 28px 36px; }}
    .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 14px; margin-bottom: 24px; }}
    .metric {{ background: #ffffff; border: 1px solid #dde3ea; border-radius: 8px; padding: 16px; }}
    .metric strong {{ display: block; font-size: 28px; margin-bottom: 4px; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin: 24px 0; }}
    .card {{ background: #ffffff; border: 1px solid #dde3ea; border-radius: 8px; padding: 18px; }}
    .status {{ display: inline-block; padding: 4px 8px; border-radius: 999px; font-size: 12px; font-weight: 700; text-transform: uppercase; }}
    .passed {{ color: #047857; background: #dff7ed; }}
    .failed {{ color: #b91c1c; background: #fee2e2; }}
    .unknown {{ color: #6b7280; background: #e5e7eb; }}
    .bar {{ height: 9px; background: #e5e7eb; border-radius: 999px; overflow: hidden; margin: 12px 0; }}
    .bar span {{ display: block; height: 100%; background: #0f766e; }}
    table {{ border-collapse: collapse; width: 100%; background: #ffffff; border: 1px solid #dde3ea; }}
    th, td {{ border-bottom: 1px solid #e5e7eb; padding: 11px; text-align: left; }}
    th {{ background: #eef2f6; }}
    a {{ color: #0f5b99; font-weight: 700; }}
    .section {{ margin-top: 28px; }}
  </style>
</head>
<body>
  <header>
    <h1>Browser Matrix Dashboard</h1>
    <p>One dashboard for the full cross-browser automation run, with drill-down reports per browser.</p>
  </header>
  <main>
    <section class="summary">
      <div class="metric"><strong>{totals["browsers"]}</strong>Browsers</div>
      <div class="metric"><strong>{totals["total"]}</strong>Total Tests</div>
      <div class="metric"><strong>{totals["passed"]}</strong>Passed</div>
      <div class="metric"><strong>{totals["failed"] + totals["broken"]}</strong>Failed/Broken</div>
      <div class="metric"><strong>{totals["pass_rate"]}%</strong>Pass Rate</div>
      <div class="metric"><strong>{_format_duration(totals["duration_ms"])}</strong>Total Duration</div>
    </section>
    <section class="cards">
      {cards}
    </section>
    <section class="section">
      <h2>Browser Results</h2>
      <table>
        <thead>
          <tr>
            <th>Browser</th>
            <th>Status</th>
            <th>Total</th>
            <th>Passed</th>
            <th>Failed</th>
            <th>Broken</th>
            <th>Skipped</th>
            <th>Pass Rate</th>
            <th>Duration</th>
            <th>Report</th>
            <th>Log</th>
          </tr>
        </thead>
        <tbody>
          {rows}
        </tbody>
      </table>
    </section>
    <section class="section">
      <h2>Attention Needed</h2>
      <ul>{failures}</ul>
    </section>
  </main>
</body>
</html>
"""


def _matrix_totals(browser_runs: list[dict[str, Any]]) -> dict[str, Any]:
    totals = {
        "browsers": len(browser_runs),
        "total": 0,
        "passed": 0,
        "failed": 0,
        "broken": 0,
        "skipped": 0,
        "duration_ms": 0,
    }
    for run in browser_runs:
        summary = run["summary"]
        for key in ("total", "passed", "failed", "broken", "skipped", "duration_ms"):
            totals[key] += summary[key]
    totals["pass_rate"] = (
        round((totals["passed"] / totals["total"]) * 100, 2)
        if totals["total"]
        else 0
    )
    return totals


def _render_browser_card(run: dict[str, Any]) -> str:
    summary = run["summary"]
    browser = html.escape(run["browser"])
    report_href = html.escape(run["report_href"])
    log_href = html.escape(run.get("log_href", "#"))
    status = html.escape(summary["status"])
    return f"""<article class="card">
  <h2>{browser}</h2>
  <span class="status {status}">{status}</span>
  <div class="bar"><span style="width: {summary["pass_rate"]}%"></span></div>
  <p><strong>{summary["pass_rate"]}%</strong> pass rate across {summary["total"]} tests.</p>
  <p>{summary["passed"]} passed, {summary["failed"] + summary["broken"]} failed/broken, {summary["skipped"]} skipped.</p>
  <p>Duration: {_format_duration(summary["duration_ms"])}</p>
  <a href="{report_href}">Open {browser} report</a>
  <br>
  <a href="{log_href}">Open execution log</a>
</article>"""


def _render_browser_row(run: dict[str, Any]) -> str:
    summary = run["summary"]
    browser = html.escape(run["browser"])
    report_href = html.escape(run["report_href"])
    log_href = html.escape(run.get("log_href", "#"))
    status = html.escape(summary["status"])
    return f"""<tr>
  <td>{browser}</td>
  <td><span class="status {status}">{status}</span></td>
  <td>{summary["total"]}</td>
  <td>{summary["passed"]}</td>
  <td>{summary["failed"]}</td>
  <td>{summary["broken"]}</td>
  <td>{summary["skipped"]}</td>
  <td>{summary["pass_rate"]}%</td>
  <td>{_format_duration(summary["duration_ms"])}</td>
  <td><a href="{report_href}">Details</a></td>
  <td><a href="{log_href}">Log</a></td>
</tr>"""


def _render_failure_item(run: dict[str, Any]) -> str:
    summary = run["summary"]
    if summary["failed"] + summary["broken"] == 0:
        return ""
    browser = html.escape(run["browser"])
    report_href = html.escape(run["report_href"])
    count = summary["failed"] + summary["broken"]
    return f'<li>{browser}: {count} failed/broken tests. <a href="{report_href}">Open report</a></li>'


def _format_duration(duration_ms: int) -> str:
    seconds = round(duration_ms / 1000, 2)
    if seconds < 60:
        return f"{seconds}s"
    minutes = int(seconds // 60)
    remaining = round(seconds % 60, 2)
    return f"{minutes}m {remaining}s"
