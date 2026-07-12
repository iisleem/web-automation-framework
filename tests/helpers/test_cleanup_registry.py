import pytest

from utils.helpers.cleanup import CleanupRegistry, assert_cleanup_success


pytestmark = pytest.mark.helpers


def test_cleanup_registry_runs_actions_in_reverse_order_by_default():
    registry = CleanupRegistry()
    calls = []

    registry.add("delete child", calls.append, "child")
    registry.add("delete parent", calls.append, "parent")

    results = registry.run_all()

    assert calls == ["parent", "child"]
    assert [result.success for result in results] == [True, True]
    assert registry.actions == ()


def test_cleanup_registry_can_run_actions_in_registration_order():
    registry = CleanupRegistry()
    calls = []

    registry.add("first", calls.append, "first")
    registry.add("second", calls.append, "second")

    registry.run_all(reverse=False)

    assert calls == ["first", "second"]


def test_cleanup_registry_passes_args_and_kwargs():
    registry = CleanupRegistry()
    calls = []

    def record(name, *, status):
        calls.append((name, status))

    registry.add("record order", record, "order-1", status="deleted")

    registry.run_all()

    assert calls == [("order-1", "deleted")]


def test_cleanup_registry_continues_after_failure_by_default():
    registry = CleanupRegistry()
    calls = []

    def fail():
        calls.append("fail")
        raise RuntimeError("delete failed")

    registry.add("successful cleanup", calls.append, "success")
    registry.add("failing cleanup", fail)

    results = registry.run_all()

    assert calls == ["fail", "success"]
    assert [result.name for result in results] == ["failing cleanup", "successful cleanup"]
    assert [result.success for result in results] == [False, True]
    assert isinstance(results[0].error, RuntimeError)


def test_cleanup_registry_can_stop_after_first_failure():
    registry = CleanupRegistry()
    calls = []

    def fail():
        calls.append("fail")
        raise RuntimeError("delete failed")

    registry.add("will not run", calls.append, "success")
    registry.add("failing cleanup", fail)

    results = registry.run_all(continue_on_error=False)

    assert calls == ["fail"]
    assert len(results) == 1
    assert results[0].success is False


def test_cleanup_registry_can_keep_registered_actions_after_run():
    registry = CleanupRegistry()

    registry.add("noop", lambda: None)

    registry.run_all(clear=False)

    assert len(registry.actions) == 1


def test_cleanup_registry_clear_removes_actions():
    registry = CleanupRegistry()

    registry.add("noop", lambda: None)
    registry.clear()

    assert registry.actions == ()


def test_assert_cleanup_success_passes_for_successful_results():
    registry = CleanupRegistry()
    registry.add("noop", lambda: None)

    results = registry.run_all()

    assert_cleanup_success(results)


def test_assert_cleanup_success_reports_all_failures():
    registry = CleanupRegistry()

    def fail_one():
        raise RuntimeError("first")

    def fail_two():
        raise ValueError("second")

    registry.add("delete user", fail_one)
    registry.add("delete order", fail_two)

    results = registry.run_all()

    with pytest.raises(AssertionError, match="(?s)delete order.*delete user"):
        assert_cleanup_success(results)
