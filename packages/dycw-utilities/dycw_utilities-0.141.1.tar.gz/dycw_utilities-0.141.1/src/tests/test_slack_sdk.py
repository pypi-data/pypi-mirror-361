from __future__ import annotations

from asyncio import timeout
from logging import getLogger
from typing import TYPE_CHECKING, ClassVar

from aiohttp import InvalidUrlClientError
from pytest import mark, param, raises
from slack_sdk.webhook.async_client import AsyncWebhookClient

from utilities.os import get_env_var
from utilities.pytest import throttle
from utilities.slack_sdk import SlackHandlerService, _get_client, send_to_slack
from utilities.whenever import MINUTE, SECOND

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from whenever import TimeDelta


class TestGetClient:
    def test_main(self) -> None:
        client = _get_client("url")
        assert isinstance(client, AsyncWebhookClient)


class TestSendToSlack:
    async def test_main(self) -> None:
        with raises(InvalidUrlClientError, match="url"):
            await send_to_slack("url", "message")

    @mark.skipif(get_env_var("SLACK", nullable=True) is None, reason="'SLACK' not set")
    @throttle(delta=5 * MINUTE)
    async def test_real(self) -> None:
        url = get_env_var("SLACK")
        await send_to_slack(
            url, f"message from {TestSendToSlack.test_real.__qualname__}"
        )


class TestSlackHandlerService:
    freq: ClassVar[TimeDelta] = 0.01 * SECOND

    @mark.parametrize("auto_start", [param(True), param(False)])
    async def test_main(self, *, tmp_path: Path, auto_start: bool) -> None:
        messages: Sequence[str] = []

        async def sender(_: str, text: str, /) -> None:
            messages.append(text)

        logger = getLogger(str(tmp_path))
        logger.addHandler(
            handler := SlackHandlerService(
                auto_start=auto_start,
                url="url",
                freq=self.freq,
                timeout=SECOND,
                sender=sender,
            )
        )
        async with handler:
            logger.warning("message")
        assert messages == ["message"]

    @mark.skipif(get_env_var("SLACK", nullable=True) is None, reason="'SLACK' not set")
    @throttle(delta=5 * MINUTE)
    async def test_real(self, *, tmp_path: Path) -> None:
        url = get_env_var("SLACK")
        logger = getLogger(str(tmp_path))
        logger.addHandler(handler := SlackHandlerService(url=url, freq=self.freq))
        async with timeout(1.0), handler:
            for i in range(10):
                logger.warning(
                    "message %d from %s",
                    i,
                    TestSlackHandlerService.test_real.__qualname__,
                )

    async def test_replace(self) -> None:
        handler = SlackHandlerService(url="url")
        new = handler.replace(freq=10 * SECOND)
        assert new.url == handler.url
        assert new.freq == 10 * SECOND
