import os

import pytest

from apps.bot import run_polling


def test_get_bot_token_reads_environment(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token-123")

    assert run_polling.get_bot_token() == "token-123"


def test_get_bot_token_raises_without_environment(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)

    with pytest.raises(RuntimeError, match="TELEGRAM_BOT_TOKEN"):
        run_polling.get_bot_token()
