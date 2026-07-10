import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from apps.bot.handlers import start


class FakeState:
    def __init__(self):
        self.cleared = False

    async def clear(self):
        self.cleared = True


def test_start_command_replies_with_welcome_message_for_new_user(monkeypatch):
    message = AsyncMock()
    message.from_user = SimpleNamespace(id=12345)
    state = FakeState()

    monkeypatch.setattr(
        "apps.bot.handlers.start.get_participant_referral_data",
        lambda **kwargs: None,
    )

    asyncio.run(start.handle_start(message, state))

    assert state.cleared is True
    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0]
    assert "Корпоративный стиль" in sent_text
    assert "зарегистрироваться" in sent_text.lower()


def test_start_command_shows_member_menu_for_registered_user(monkeypatch):
    message = AsyncMock()
    message.from_user = SimpleNamespace(id=12345)
    state = FakeState()

    monkeypatch.setattr(
        "apps.bot.handlers.start.get_participant_referral_data",
        lambda **kwargs: ("Ольга", "abc123"),
    )

    asyncio.run(start.handle_start(message, state))

    assert state.cleared is True
    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0]
    assert "Ольга" in sent_text
    assert "рады снова видеть" in sent_text.lower()
