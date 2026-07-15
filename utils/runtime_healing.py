from __future__ import annotations

import json
import os
import re
from collections.abc import Callable
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import allure
from automation_core.healing import (
    CandidateDescriptor,
    CandidateScore,
    HealingConfig,
    HealingDecision,
    HealingMode,
    HealingResult,
    LocatorDescriptor,
    add_healing_result,
    append_healing_event,
    evaluate_healing,
)
from playwright.sync_api import Error, Locator, Page

from utils.logger import get_logger
from utils.self_healing import LocatorCandidate


LOGGER = get_logger("runtime-healing")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT_PATH = "reports/healing/events.jsonl"
RUNTIME_ACTIONS = ("click", "fill", "select", "text", "expect_visible")


@dataclass(frozen=True)
class RuntimeHealingSettings:
    config: HealingConfig
    audit_path: Path
    enabled: bool


def runtime_healing_settings(settings: dict[str, Any], project_root: Path | None = None) -> RuntimeHealingSettings:
    raw = settings.get("runtime_healing") or {}
    root = project_root or PROJECT_ROOT
    mode = str(raw.get("mode", "disabled")).strip().lower()
    config = HealingConfig(
        mode=mode,
        min_score=float(raw.get("min_score", 0.78)),
        ambiguity_delta=float(raw.get("ambiguity_delta", 0.05)),
        max_candidates=int(raw.get("max_candidates", 10)),
        allowed_actions=tuple(raw.get("allowed_actions") or RUNTIME_ACTIONS),
        allow_patterns=tuple(raw.get("allow_patterns") or ()),
        deny_patterns=tuple(raw.get("deny_patterns") or ()),
    )
    audit_path = _resolve_project_path(root, raw.get("audit_path", DEFAULT_AUDIT_PATH))
    return RuntimeHealingSettings(
        config=config, audit_path=audit_path, enabled=config.normalized_mode() != HealingMode.DISABLED
    )


def attempt_runtime_healing(
    *,
    page: Page,
    description: str,
    primary: LocatorCandidate,
    action: str,
    action_runner: Callable[[Locator], Any],
    settings: RuntimeHealingSettings,
    original_error: Exception,
) -> Any:
    if not settings.enabled:
        raise original_error

    original = LocatorDescriptor(
        strategy="css",
        value=primary.selector,
        category="locator",
        action=action,
        label=description,
        metadata={"source": "web", "description": primary.description},
    )
    candidates = discover_healing_candidates(page, primary, description)
    result = evaluate_healing(
        original,
        candidates,
        settings.config,
        action=action,
        test_id=current_test_id(),
        metadata={
            "description": description,
            "original_error": f"{type(original_error).__name__}: {original_error}",
            "url": getattr(page, "url", ""),
        },
    )
    _record_healing_result(result, settings.audit_path)

    if result.decision != HealingDecision.APPLIED or not result.selected:
        raise RuntimeError(_failure_message(description, result)) from original_error

    healed_locator = page.locator(result.selected.candidate.value)
    if not _candidate_safe_for_action(healed_locator, action):
        raise RuntimeError(
            f"Runtime healing selected an unsafe candidate for '{description}'. "
            f"Original action still failed. Candidate: {result.selected.candidate.value}"
        ) from original_error

    try:
        return action_runner(healed_locator)
    except Exception as healed_error:
        raise RuntimeError(
            f"Runtime healing candidate failed for '{description}'. "
            f"Candidate: {result.selected.candidate.value}. Error: {healed_error}"
        ) from original_error


def discover_healing_candidates(
    page: Page,
    primary: LocatorCandidate,
    description: str,
) -> list[CandidateDescriptor]:
    elements = _candidate_elements(page)
    candidates: list[CandidateDescriptor] = []
    seen: set[str] = set()
    for element in elements:
        for selector, strategy, signal_bonus in _selectors_for_element(element):
            if selector in seen:
                continue
            seen.add(selector)
            unique = _safe_count(page, selector) == 1
            signals = _candidate_signals(
                selector=selector,
                element=element,
                primary_selector=primary.selector,
                description=description,
                signal_bonus=signal_bonus,
            )
            candidates.append(
                CandidateDescriptor(
                    strategy=strategy,
                    value=selector,
                    category="locator",
                    label=element.get("text") or element.get("ariaLabel") or element.get("id") or selector,
                    source="playwright-dom",
                    signals=signals,
                    metadata={
                        "tag": element.get("tag"),
                        "role": element.get("role"),
                        "text": element.get("text"),
                    },
                    unique=unique,
                )
            )
    return candidates


def healing_report_enricher(audit_path: Path | str):
    path = Path(audit_path)

    def enrich(report):
        results = _read_healing_results(path)
        if not results:
            return report
        unmatched: list[dict[str, Any]] = []
        for result in results:
            matched = False
            for test in report.tests:
                if _result_matches_test(result, test):
                    add_healing_result(test, result)
                    matched = True
            if not matched:
                unmatched.append(result.to_dict())
        if unmatched:
            report.metadata.setdefault("unmatched_healing_events", []).extend(unmatched)
        report.metadata["healing_audit_path"] = str(path)
        return report

    return enrich


def current_test_id() -> str:
    raw = os.getenv("PYTEST_CURRENT_TEST", "")
    return raw.split(" ", 1)[0]


def _record_healing_result(result: HealingResult, audit_path: Path) -> None:
    append_healing_event(audit_path, result)
    message = (
        f"Runtime healing {result.decision.value} for '{result.original.label}' " f"({result.action}): {result.reason}"
    )
    LOGGER.warning(message)
    with allure.step(message):
        allure.attach(
            json.dumps(result.to_dict(), indent=2, sort_keys=True),
            name="runtime healing event",
            attachment_type=allure.attachment_type.JSON,
        )


def _failure_message(description: str, result: HealingResult) -> str:
    selected = f" Selected: {result.selected.candidate.value}." if result.selected else ""
    return (
        f"Runtime healing could not safely recover '{description}'. "
        f"Decision: {result.decision.value}. Reason: {result.reason}.{selected} "
        "Original action failure is preserved."
    )


def _candidate_elements(page: Page) -> list[dict[str, Any]]:
    script = """
    () => Array.from(document.querySelectorAll('button, input, select, textarea, a, [role], [data-test], [data-testid], [aria-label], [name], [id]'))
      .slice(0, 250)
      .map((element) => ({
        tag: element.tagName.toLowerCase(),
        id: element.getAttribute('id') || '',
        name: element.getAttribute('name') || '',
        dataTest: element.getAttribute('data-test') || '',
        dataTestId: element.getAttribute('data-testid') || '',
        ariaLabel: element.getAttribute('aria-label') || '',
        role: element.getAttribute('role') || '',
        type: element.getAttribute('type') || '',
        text: (element.innerText || element.getAttribute('value') || element.getAttribute('placeholder') || '').trim().slice(0, 120)
      }))
    """
    try:
        value = page.evaluate(script)
    except Error:
        return []
    return [item for item in value if isinstance(item, dict)]


def _selectors_for_element(element: dict[str, Any]) -> list[tuple[str, str, dict[str, float]]]:
    selectors: list[tuple[str, str, dict[str, float]]] = []
    if element.get("dataTest"):
        selectors.append((f"[data-test='{_css_quote(element['dataTest'])}']", "css", {"stable_id": 1.0}))
    if element.get("dataTestId"):
        selectors.append((f"[data-testid='{_css_quote(element['dataTestId'])}']", "css", {"stable_id": 1.0}))
    if element.get("id"):
        selectors.append((f"#{_css_identifier(str(element['id']))}", "css", {"stable_id": 0.95}))
    if element.get("name"):
        selectors.append((f"[name='{_css_quote(element['name'])}']", "css", {"name": 1.0}))
    if element.get("ariaLabel"):
        selectors.append((f"[aria-label='{_css_quote(element['ariaLabel'])}']", "css", {"accessibility": 1.0}))
    if element.get("role"):
        selectors.append((f"[role='{_css_quote(element['role'])}']", "css", {"accessibility": 0.65}))
    return selectors


def _candidate_signals(
    *,
    selector: str,
    element: dict[str, Any],
    primary_selector: str,
    description: str,
    signal_bonus: dict[str, float],
) -> dict[str, float]:
    text = str(element.get("text") or "")
    labels = " ".join(
        str(element.get(key) or "") for key in ("dataTest", "dataTestId", "id", "name", "ariaLabel", "role", "type")
    )
    return {
        **signal_bonus,
        "exact": 1.0 if selector == primary_selector else 0.0,
        "text": _similarity(description, text),
        "name": _similarity(description, labels),
        "accessibility": max(
            signal_bonus.get("accessibility", 0.0), _similarity(description, str(element.get("ariaLabel") or ""))
        ),
        "type": 1.0 if str(element.get("tag") or "") in {"button", "input", "select", "textarea", "a"} else 0.0,
        "context": _similarity(primary_selector, selector),
    }


def _candidate_safe_for_action(locator: Locator, action: str) -> bool:
    try:
        if locator.count() != 1:
            return False
        if action in {"click", "fill", "select", "text", "expect_visible"}:
            return locator.first.is_visible()
    except Error:
        return False
    return False


def _safe_count(page: Page, selector: str) -> int:
    try:
        return page.locator(selector).count()
    except Error:
        return 0


def _similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, _normalize(left), _normalize(right)).ratio()


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _css_quote(value: str) -> str:
    return str(value).replace("\\", "\\\\").replace("'", "\\'")


def _css_identifier(value: str) -> str:
    return re.sub(r"([^A-Za-z0-9_-])", r"\\\1", value)


def _resolve_project_path(project_root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def _read_healing_results(path: Path) -> list[HealingResult]:
    if not path.exists():
        return []
    results: list[HealingResult] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        results.append(_healing_result_from_dict(json.loads(line)))
    return results


def _healing_result_from_dict(data: dict[str, Any]) -> HealingResult:
    return HealingResult(
        mode=HealingMode(data["mode"]),
        decision=HealingDecision(data["decision"]),
        original=LocatorDescriptor(**data["original"]),
        candidates=[_candidate_score_from_dict(item) for item in data.get("candidates", [])],
        selected=_candidate_score_from_dict(data["selected"]) if data.get("selected") else None,
        reason=data.get("reason", ""),
        action=data.get("action", ""),
        test_id=data.get("test_id", ""),
        metadata=data.get("metadata", {}),
    )


def _candidate_score_from_dict(data: dict[str, Any]) -> CandidateScore:
    return CandidateScore(
        candidate=CandidateDescriptor(**data["candidate"]),
        score=float(data.get("score", 0)),
        reasons=list(data.get("reasons", [])),
        rejected_reasons=list(data.get("rejected_reasons", [])),
    )


def _result_matches_test(result: HealingResult, test) -> bool:
    event_id = result.test_id
    if not event_id:
        return False
    candidates = {test.id, test.name, test.full_name, test.full_name.replace("#", "::")}
    normalized_event = _normalize_test_id(event_id)
    return any(normalized_event == _normalize_test_id(candidate) for candidate in candidates if candidate)


def _normalize_test_id(value: str) -> str:
    value = value.split("[", 1)[0]
    value = value.replace("/", ".").replace("::", "#")
    return re.sub(r"\.py\b", "", value)
