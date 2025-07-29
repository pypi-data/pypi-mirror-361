from __future__ import annotations

from asyncio import TaskGroup
from functools import partial
from itertools import repeat
from typing import TYPE_CHECKING, ClassVar, Literal, assert_never

from pytest import LogCaptureFixture, mark, param, raises

from tests.conftest import SKIPIF_CI_AND_NOT_LINUX
from tests.test_redis import yield_test_redis
from utilities.asyncio import sleep_td
from utilities.pottery import (
    _YieldAccessNumLocksError,
    _YieldAccessUnableToAcquireLockError,
    run_as_service,
    yield_access,
)
from utilities.text import unique_str
from utilities.timer import Timer
from utilities.whenever import SECOND

if TYPE_CHECKING:
    from redis.asyncio import Redis
    from whenever import TimeDelta

    from utilities.types import LoggerOrName


class TestRunAsService:
    delta: ClassVar[TimeDelta] = 0.1 * SECOND

    @mark.parametrize("sync_or_async", [param("sync"), param("async")])
    @mark.parametrize("use_logger", [param(True), param(False)])
    @SKIPIF_CI_AND_NOT_LINUX
    async def test_main(
        self,
        *,
        sync_or_async: Literal["sync", "async"],
        use_logger: bool,
        caplog: LogCaptureFixture,
    ) -> None:
        caplog.set_level("DEBUG", logger=(name := unique_str()))
        lst: list[None] = []
        logger = name if use_logger else None
        key = f"{sync_or_async}/{use_logger}"

        async with yield_test_redis() as redis, TaskGroup() as tg:
            _ = tg.create_task(
                self.service(
                    lst, redis, key, sync_or_async=sync_or_async, logger=logger
                )
            )
            _ = tg.create_task(
                self.delayed(
                    lst, redis, key, sync_or_async=sync_or_async, logger=logger
                )
            )

        match sync_or_async, use_logger:
            case "sync", _:
                assert len(lst) == 2
            case "async", True:
                assert len(lst) == 1
                messages = [r.message for r in caplog.records if r.name == name]
                expected = (
                    f"Unable to acquire any 1 of 1 locks for {key!r} after PT0.1S"
                )
                assert expected in messages
            case "async", False:
                assert len(lst) == 1
            case _ as never:
                assert_never(never)

    def func_main_sync(self, lst: list[None], /) -> None:
        lst.append(None)

    async def func_main_async(self, lst: list[None], /) -> None:
        lst.append(None)
        await sleep_td(5 * self.delta)

    async def service(
        self,
        lst: list[None],
        redis: Redis,
        key: str,
        /,
        *,
        sync_or_async: Literal["sync", "async"],
        logger: LoggerOrName | None = None,
    ) -> None:
        match sync_or_async:
            case "sync":
                make_func = partial(self.func_main_sync, lst)
            case "async":
                make_func = lambda: self.func_main_async(lst)  # noqa: E731
        await run_as_service(
            redis, make_func, key=key, timeout_acquire=self.delta, logger=logger
        )

    async def delayed(
        self,
        lst: list[None],
        redis: Redis,
        key: str,
        /,
        *,
        sync_or_async: Literal["sync", "async"],
        logger: LoggerOrName | None = None,
    ) -> None:
        await sleep_td(self.delta)
        await self.service(lst, redis, key, sync_or_async=sync_or_async, logger=logger)

    @mark.parametrize("use_logger", [param(True), param(False)])
    @SKIPIF_CI_AND_NOT_LINUX
    async def test_error(self, *, use_logger: bool, caplog: LogCaptureFixture) -> None:
        caplog.set_level("DEBUG", logger=(name := unique_str()))
        lst: list[None] = []

        async with yield_test_redis() as redis:
            await run_as_service(
                redis, lambda: self.func_error(lst), logger=name if use_logger else None
            )

        if use_logger:
            messages = [r.message for r in caplog.records if r.name == name]
            expected = list(repeat("Error running 'func_error' as a service", times=3))
            assert messages == expected

    async def func_error(self, lst: list[None], /) -> None:
        lst.append(None)
        if len(lst) <= 3:
            msg = "Failure"
            raise ValueError(msg)


class TestYieldAccess:
    delta: ClassVar[TimeDelta] = 0.1 * SECOND

    @mark.parametrize(
        ("num_tasks", "num_locks", "min_multiple"),
        [
            param(1, 1, 1),
            param(1, 2, 1),
            param(1, 3, 1),
            param(2, 1, 2),
            param(2, 2, 1),
            param(2, 3, 1),
            param(2, 4, 1),
            param(2, 5, 1),
            param(3, 1, 3),
            param(3, 2, 2),
            param(3, 3, 1),
            param(3, 4, 1),
            param(3, 5, 1),
            param(4, 1, 4),
            param(4, 2, 2),
            param(4, 3, 2),
            param(4, 4, 1),
            param(4, 5, 1),
        ],
    )
    @SKIPIF_CI_AND_NOT_LINUX
    async def test_main(
        self, *, num_tasks: int, num_locks: int, min_multiple: int
    ) -> None:
        with Timer() as timer:
            await self.func(num_tasks, unique_str(), num_locks=num_locks)
        assert (min_multiple * self.delta) <= timer <= (5 * min_multiple * self.delta)

    async def test_error_num_locks(self) -> None:
        key = unique_str()
        with raises(
            _YieldAccessNumLocksError,
            match=r"Number of locks for '\w+' must be positive; got 0",
        ):
            async with yield_test_redis() as redis, yield_access(redis, key, num=0):
                ...

    @SKIPIF_CI_AND_NOT_LINUX
    async def test_error_unable_to_acquire_lock(self) -> None:
        key = unique_str()
        delta = 0.1 * SECOND

        async def coroutine(redis: Redis, key: str, /) -> None:
            async with yield_access(
                redis, key, num=1, timeout_acquire=delta, throttle=5 * delta
            ):
                await sleep_td(delta)

        with raises(ExceptionGroup) as exc_info:
            async with yield_test_redis() as redis, TaskGroup() as tg:
                _ = tg.create_task(coroutine(redis, key))
                _ = tg.create_task(coroutine(redis, key))
        assert exc_info.group_contains(
            _YieldAccessUnableToAcquireLockError,
            match=r"Unable to acquire any 1 of 1 locks for '\w+' after .*",
        )

    async def func(self, num_tasks: int, key: str, /, *, num_locks: int = 1) -> None:
        async def coroutine() -> None:
            async with (
                yield_test_redis() as redis,
                yield_access(redis, key, num=num_locks),
            ):
                await sleep_td(self.delta)

        async with TaskGroup() as tg:
            _ = [tg.create_task(coroutine()) for _ in range(num_tasks)]
