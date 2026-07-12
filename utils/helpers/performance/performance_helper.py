from __future__ import annotations

import fnmatch
from typing import Any


def get_navigation_timing(page: Any) -> dict[str, float]:
    return page.evaluate(
        """() => {
            const entry = performance.getEntriesByType("navigation")[0];
            if (!entry) return {};
            return {
                startTime: entry.startTime,
                domContentLoadedEventEnd: entry.domContentLoadedEventEnd,
                loadEventEnd: entry.loadEventEnd,
                responseEnd: entry.responseEnd,
                duration: entry.duration
            };
        }"""
    )


def get_resource_timings(page: Any) -> list[dict[str, Any]]:
    return page.evaluate(
        """() => performance.getEntriesByType("resource").map((entry) => ({
            name: entry.name,
            initiatorType: entry.initiatorType,
            duration: entry.duration,
            transferSize: entry.transferSize || 0
        }))"""
    )


def assert_page_load_under(
    page: Any,
    max_ms: float,
    *,
    metric: str = "loadEventEnd",
) -> dict[str, float]:
    timing = get_navigation_timing(page)
    actual = float(timing.get(metric, timing.get("duration", 0)))
    assert actual <= max_ms, (
        f"Expected page performance metric {metric!r} to be <= {max_ms} ms, got {actual} ms"
    )
    return timing


def assert_no_slow_resources(
    page: Any,
    max_duration_ms: float,
    *,
    ignored_url_patterns: list[str] | None = None,
) -> list[dict[str, Any]]:
    ignored = ignored_url_patterns or []
    resources = [
        resource
        for resource in get_resource_timings(page)
        if not _matches_any(resource.get("name", ""), ignored)
    ]
    slow_resources = [
        resource for resource in resources if float(resource.get("duration", 0)) > max_duration_ms
    ]
    assert not slow_resources, (
        f"Expected no resources slower than {max_duration_ms} ms, got {slow_resources!r}"
    )
    return resources


def assert_resource_count_under(
    page: Any,
    max_count: int,
    *,
    resource_type: str | None = None,
) -> list[dict[str, Any]]:
    resources = get_resource_timings(page)
    if resource_type:
        resources = [
            resource for resource in resources if resource.get("initiatorType") == resource_type
        ]
    actual_count = len(resources)
    assert actual_count <= max_count, (
        f"Expected resource count <= {max_count}, got {actual_count}"
    )
    return resources


def get_resource_summary(page: Any) -> dict[str, Any]:
    resources = get_resource_timings(page)
    total_transfer_size = sum(int(resource.get("transferSize", 0)) for resource in resources)
    by_type: dict[str, int] = {}
    for resource in resources:
        resource_type = str(resource.get("initiatorType") or "unknown")
        by_type[resource_type] = by_type.get(resource_type, 0) + 1
    return {
        "count": len(resources),
        "total_transfer_size": total_transfer_size,
        "by_type": by_type,
    }


def _matches_any(value: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(value, pattern) for pattern in patterns)
