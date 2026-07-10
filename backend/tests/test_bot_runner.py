import os
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from apps.bot import run_polling


def test_get_bot_token_reads_environment(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token-123")

    assert run_polling.get_bot_token() == "token-123"


def test_get_bot_token_raises_without_environment(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)

    with pytest.raises(RuntimeError, match="TELEGRAM_BOT_TOKEN"):
        run_polling.get_bot_token()


def test_run_deletes_webhook_before_polling(monkeypatch):
    delete_webhook = AsyncMock()
    start_polling = AsyncMock()
    fake_bot = SimpleNamespace(delete_webhook=delete_webhook)
    fake_dispatcher = SimpleNamespace(start_polling=start_polling)

    monkeypatch.setattr(run_polling, "Bot", lambda token: fake_bot)
    monkeypatch.setattr(run_polling, "build_dispatcher", lambda: fake_dispatcher)
    monkeypatch.setattr(run_polling, "get_bot_token", lambda: "token-123")

    import asyncio

    asyncio.run(run_polling.run())

    delete_webhook.assert_awaited_once_with(drop_pending_updates=True)
    start_polling.assert_awaited_once_with(fake_bot)
