from __future__ import annotations

import pytest
from automation_core.healing import (
    CandidateDescriptor,
    HealingConfig,
    LocatorDescriptor,
    append_healing_event,
    evaluate_healing,
)
from automation_core.reporting.models import RunReport, TestCaseReport

from utils.config_reader import ConfigReader
from utils.runtime_healing import attempt_runtime_healing, healing_report_enricher, runtime_healing_settings
from utils.self_healing import LocatorCandidate


pytestmark = pytest.mark.helpers


def test_runtime_healing_default_is_disabled():
    settings = ConfigReader().read_settings()

    runtime_settings = runtime_healing_settings(settings)

    assert runtime_settings.config.normalized_mode().value == "disabled"
    assert runtime_settings.enabled is False


def test_suggest_mode_records_but_does_not_apply(monkeypatch, tmp_path):
    page = FakePage({"[data-test='submit-new']": FakeLocator()})
    settings = runtime_healing_settings(
        {
            "runtime_healing": {
                "mode": "suggest",
                "min_score": 0.7,
                "audit_path": str(tmp_path / "events.jsonl"),
            }
        }
    )
    applied = {"count": 0}
    monkeypatch.setattr(
        "utils.runtime_healing.discover_healing_candidates",
        lambda page, primary, description: [_candidate("[data-test='submit-new']", 0.95)],
    )

    with pytest.raises(RuntimeError, match="suggested"):
        attempt_runtime_healing(
            page=page,
            description="submit button",
            primary=LocatorCandidate("[data-test='submit-old']", "submit old"),
            action="click",
            action_runner=lambda locator: applied.__setitem__("count", applied["count"] + 1),
            settings=settings,
            original_error=AssertionError("old locator failed"),
        )

    assert applied["count"] == 0
    assert "suggested" in (tmp_path / "events.jsonl").read_text(encoding="utf-8")


def test_apply_mode_uses_candidate_when_core_approves(monkeypatch, tmp_path):
    healed = FakeLocator()
    page = FakePage({"[data-test='submit-new']": healed})
    settings = runtime_healing_settings(
        {
            "runtime_healing": {
                "mode": "apply",
                "min_score": 0.7,
                "ambiguity_delta": 0.05,
                "audit_path": str(tmp_path / "events.jsonl"),
            }
        }
    )
    monkeypatch.setattr(
        "utils.runtime_healing.discover_healing_candidates",
        lambda page, primary, description: [_candidate("[data-test='submit-new']", 0.95)],
    )

    result = attempt_runtime_healing(
        page=page,
        description="submit button",
        primary=LocatorCandidate("[data-test='submit-old']", "submit old"),
        action="click",
        action_runner=lambda locator: locator.click(),
        settings=settings,
        original_error=AssertionError("old locator failed"),
    )

    assert result is None
    assert healed.clicked is True
    assert "applied" in (tmp_path / "events.jsonl").read_text(encoding="utf-8")


def test_ambiguous_candidate_fails_clearly(monkeypatch, tmp_path):
    page = FakePage(
        {
            "[data-test='submit-primary']": FakeLocator(),
            "[data-test='submit-secondary']": FakeLocator(),
        }
    )
    settings = runtime_healing_settings(
        {
            "runtime_healing": {
                "mode": "apply",
                "min_score": 0.7,
                "ambiguity_delta": 0.1,
                "audit_path": str(tmp_path / "events.jsonl"),
            }
        }
    )
    monkeypatch.setattr(
        "utils.runtime_healing.discover_healing_candidates",
        lambda page, primary, description: [
            _candidate("[data-test='submit-primary']", 0.95),
            _candidate("[data-test='submit-secondary']", 0.94),
        ],
    )

    with pytest.raises(RuntimeError, match="ambiguous"):
        attempt_runtime_healing(
            page=page,
            description="submit button",
            primary=LocatorCandidate("[data-test='submit-old']", "submit old"),
            action="click",
            action_runner=lambda locator: locator.click(),
            settings=settings,
            original_error=AssertionError("old locator failed"),
        )


def test_healing_report_enricher_adds_core_report_metadata(tmp_path):
    audit_path = tmp_path / "events.jsonl"
    result = evaluate_healing(
        LocatorDescriptor(strategy="css", value="[data-test='old']", action="click", label="submit button"),
        [_candidate("[data-test='new']", 0.95)],
        HealingConfig(mode="apply", min_score=0.7),
        action="click",
        test_id="tests/smoke/test_login.py::test_valid_login",
    )
    append_healing_event(audit_path, result)
    report = RunReport(
        run_id="run-1",
        tests=[
            TestCaseReport(
                id="test-1",
                name="test_valid_login",
                full_name="tests.smoke.test_login#test_valid_login",
            )
        ],
    )

    enriched = healing_report_enricher(audit_path)(report)

    assert enriched.tests[0].metadata["healing_attempt_count"] == 1
    assert enriched.tests[0].metadata["healing_applied_count"] == 1


def _candidate(selector: str, score: float) -> CandidateDescriptor:
    return CandidateDescriptor(
        strategy="css",
        value=selector,
        category="locator",
        source="test",
        signals={"score": score},
        unique=True,
    )


class FakePage:
    url = "https://example.test"

    def __init__(self, locators):
        self.locators = locators

    def locator(self, selector):
        return self.locators[selector]


class FakeLocator:
    first = None

    def __init__(self, *, visible=True):
        self.visible = visible
        self.clicked = False
        self.first = self

    def count(self):
        return 1

    def is_visible(self):
        return self.visible

    def click(self):
        self.clicked = True
