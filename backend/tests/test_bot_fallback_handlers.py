import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from apps.bot.handlers.fallback import handle_fallback
from apps.bot.ui import build_main_menu_keyboard, build_start_keyboard


def test_handle_fallback_returns_main_menu_for_registered_participant(monkeypatch):
    message = AsyncMock()
    message.from_user = SimpleNamespace(id=12345)

    monkeypatch.setattr(
        "apps.bot.handlers.fallback.get_participant_referral_data",
        lambda **kwargs: ("Анна Иванова", "abc123"),
    )

    asyncio.run(handle_fallback(message))

    message.answer.assert_awaited_once()
    assert message.answer.await_args.kwargs["reply_markup"] == build_main_menu_keyboard()


def test_handle_fallback_returns_start_menu_for_unregistered_participant(monkeypatch):
    message = AsyncMock()
    message.from_user = SimpleNamespace(id=12345)

    monkeypatch.setattr(
        "apps.bot.handlers.fallback.get_participant_referral_data",
        lambda **kwargs: None,
    )

    asyncio.run(handle_fallback(message))

    message.answer.assert_awaited_once()
    assert message.answer.await_args.kwargs["reply_markup"] == build_start_keyboard()
