import asyncio
import time

import pytest

from mooch.decorators.retry import retry


def test_retry_success_first_try(monkeypatch):
    calls = []

    @retry(times=3, delay=0.01)
    def func():
        calls.append(1)
        return "ok"

    assert func() == "ok"
    assert len(calls) == 1


def test_retry_success_after_failures(monkeypatch):
    calls = []

    @retry(times=3, delay=0.01)
    def func():
        if len(calls) < 2:
            calls.append("fail")
            raise ValueError("fail")
        calls.append("ok")
        return "ok"

    assert func() == "ok"
    assert calls == ["fail", "fail", "ok"]


def test_retry_raises_after_all_attempts(monkeypatch):
    calls = []

    @retry(times=2, delay=0.01)
    def func():
        calls.append(1)
        raise RuntimeError("fail")

    with pytest.raises(RuntimeError, match="fail"):
        func()
    assert len(calls) == 2


def test_retry_delay(monkeypatch):
    sleep_calls = []

    def fake_sleep(seconds):
        sleep_calls.append(seconds)

    monkeypatch.setattr(time, "sleep", fake_sleep)

    @retry(times=3, delay=0.01)
    def func():
        raise Exception("fail")

    with pytest.raises(Exception):
        func()
    # Should sleep twice (times-1)
    assert sleep_calls == [0.01, 0.01]


def test_retry_returns_none_when_zero_times(monkeypatch):
    calls = []

    @retry(times=0, delay=0.01)
    def func():
        calls.append(1)
        return "should not be called"

    # Should not call the function at all, returns None
    assert func() is None
    assert calls == []


def test_retry_preserves_function_metadata():
    @retry(1)
    def my_func():
        """Docstring here."""
        return 42

    assert my_func.__name__ == "my_func"
    assert my_func.__doc__ == "Docstring here."


def test_retry_with_args_kwargs(monkeypatch):
    results = []

    @retry(times=2, delay=0.01)
    def func(a, b=2):
        results.append((a, b))
        if a != b:
            raise ValueError("fail")
        return a + b

    assert func(2, b=2) == 4
    assert results == [(2, 2)]


def test_retry_raises_last_exception_if_all_fail(monkeypatch):
    calls = []

    @retry(times=3, delay=0.01)
    def func():
        calls.append(1)
        if len(calls) < 2:
            raise Exception("fail")
        raise ValueError(f"fail {len(calls)}")

    with pytest.raises(ValueError, match="fail 3"):
        func()
    assert len(calls) == 3


def test_retry_raises_value_error_when_fail_on_none_and_none_returned():
    calls = []

    @retry(times=3, delay=0.01, fail_on_none=True)
    def func():
        calls.append(1)

    with pytest.raises(ValueError, match="Function returned None"):
        func()
    assert len(calls) == 3


def test_retry_fallback_value():
    calls = []

    @retry(times=3, delay=0.01, fallback="fallback_value")
    def func():
        calls.append(1)
        raise Exception("fail")

    result = func()
    assert result == "fallback_value"
    assert len(calls) == 3


def test_retry_logs_exceptions_when_log_exceptions_true(caplog):
    calls = []

    @retry(times=2, delay=0.01, log_exceptions=True)
    def func():
        calls.append(1)
        raise Exception("fail")

    with pytest.raises(Exception, match="fail"):
        func()

    assert "Retry #1 Exception in func" in caplog.text
    assert "Retry #2 Exception in func" in caplog.text
    assert len(calls) == 2


def test_retry_does_not_log_exceptions_when_log_exceptions_false(caplog):
    calls = []

    @retry(times=2, delay=0.01, log_exceptions=False)
    def func():
        calls.append(1)
        raise Exception("fail")

    with pytest.raises(Exception, match="fail"):
        func()

    assert "Retry #1 Exception in func" not in caplog.text
    assert "Retry #2 Exception in func" not in caplog.text
    assert len(calls) == 2


async def test_retry_async_function(monkeypatch):
    calls = []

    @retry(times=3, delay=0.01)
    async def async_func():
        calls.append(1)
        return "ok"

    async def run_test():
        result = await async_func()
        assert result == "ok"
        assert len(calls) == 1

    monkeypatch.setattr("asyncio.run", lambda coro: coro())
    await run_test()


async def test_retry_async_function_with_failures(monkeypatch):
    calls = []

    @retry(times=3, delay=0.01)
    async def async_func():
        if len(calls) < 2:
            calls.append("fail")
            raise ValueError("fail")
        calls.append("ok")
        return "ok"

    async def run_test():
        result = await async_func()
        assert result == "ok"
        assert calls == ["fail", "fail", "ok"]

    monkeypatch.setattr("asyncio.run", lambda coro: coro())
    await run_test()


async def test_retry_async_function_raises_after_all_attempts(monkeypatch):
    calls = []

    @retry(times=2, delay=0.01)
    async def async_func():
        calls.append(1)
        raise RuntimeError("fail")

    async def run_test():
        with pytest.raises(RuntimeError, match="fail"):
            await async_func()
        assert len(calls) == 2

    monkeypatch.setattr("asyncio.run", lambda coro: coro())
    await run_test()


async def test_retry_async_function_with_args_kwargs(monkeypatch):
    results = []

    @retry(times=2, delay=0.01)
    async def async_func(a, b=2):
        results.append((a, b))
        if a != b:
            raise ValueError("fail")
        return a + b

    async def run_test():
        result = await async_func(2, b=2)
        assert result == 4
        assert results == [(2, 2)]

    monkeypatch.setattr("asyncio.run", lambda coro: coro())
    await run_test()


async def test_retry_async_function_raises_last_exception_if_all_fail(monkeypatch):
    calls = []

    @retry(times=3, delay=0.01)
    async def async_func():
        calls.append(1)
        if len(calls) < 2:
            raise Exception("fail")
        raise ValueError(f"fail {len(calls)}")

    async def run_test():
        with pytest.raises(ValueError, match="fail 3"):
            await async_func()
        assert len(calls) == 3

    monkeypatch.setattr("asyncio.run", lambda coro: coro())
    await run_test()


def test_retry_async_function_raises_value_error_when_fail_on_none_and_none_returned():
    calls = []

    @retry(times=3, delay=0.01, fail_on_none=True)
    async def async_func():
        calls.append(1)

    async def run_test():
        with pytest.raises(ValueError, match="Function returned None"):
            await async_func()
        assert len(calls) == 3

    asyncio.run(run_test())


def test_retry_async_function_fallback_value():
    calls = []

    @retry(times=3, delay=0.01, fallback="fallback_value")
    async def async_func():
        calls.append(1)
        raise Exception("fail")

    async def run_test():
        result = await async_func()
        assert result == "fallback_value"
        assert len(calls) == 3

    asyncio.run(run_test())


def test_retry_async_function_logs_exceptions_when_log_exceptions_true(caplog):
    calls = []

    @retry(times=2, delay=0.01, log_exceptions=True)
    async def async_func():
        calls.append(1)
        raise Exception("fail")

    async def run_test():
        with pytest.raises(Exception, match="fail"):
            await async_func()

    asyncio.run(run_test())

    assert "Retry #1 Exception in async_func" in caplog.text
    assert "Retry #2 Exception in async_func" in caplog.text
    assert len(calls) == 2


def test_retry_async_function_does_not_log_exceptions_when_log_exceptions_false(caplog):
    calls = []

    @retry(times=2, delay=0.01, log_exceptions=False)
    async def async_func():
        calls.append(1)
        raise Exception("fail")

    async def run_test():
        with pytest.raises(Exception, match="fail"):
            await async_func()

    asyncio.run(run_test())

    assert "Retry #1 Exception in async_func" not in caplog.text
    assert "Retry #2 Exception in async_func" not in caplog.text
    assert len(calls) == 2


def test_retry_async_function_with_zero_times(monkeypatch):
    calls = []

    @retry(times=0, delay=0.01)
    async def async_func():
        calls.append(1)
        return "should not be called"

    async def run_test():
        # Should not call the function at all, returns None
        assert await async_func() is None
        assert calls == []

    asyncio.run(run_test())


def test_retry_async_function_preserves_metadata():
    @retry(1)
    async def my_async_func():
        """Docstring here."""
        return 42

    assert my_async_func.__name__ == "my_async_func"
    assert my_async_func.__doc__ == "Docstring here."


def test_retry_async_function_with_args_kwargs(monkeypatch):
    results = []

    @retry(times=2, delay=0.01)
    async def async_func(a, b=2):
        results.append((a, b))
        if a != b:
            raise ValueError("fail")
        return a + b

    async def run_test():
        result = await async_func(2, b=2)
        assert result == 4
        assert results == [(2, 2)]

    asyncio.run(run_test())
