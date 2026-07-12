import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from apps.bot.handlers.support import SupportStates, handle_support_message, open_help_menu, start_support


class FakeState:
    def __init__(self):
        self.current_state = None
        self.cleared = False

    async def set_state(self, state):
        self.current_state = state

    async def clear(self):
        self.cleared = True
        self.current_state = None


def test_open_help_menu_returns_intro():
    message = AsyncMock()

    asyncio.run(open_help_menu(message))

    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0].lower()
    assert "правила" in sent_text
    assert "администратор" in sent_text


def test_start_support_asks_for_message():
    message = AsyncMock()
    state = FakeState()

    asyncio.run(start_support(message, state))

    assert state.current_state == SupportStates.waiting_message
    message.answer.assert_awaited_once()
    assert "администратор" in message.answer.await_args.args[0].lower()


def test_handle_support_message_sends_notification(monkeypatch):
    sent = {}
    message = AsyncMock()
    message.text = "У меня вопрос по бонусам"
    message.from_user = SimpleNamespace(id=12345, full_name="Ольга", username="olgasanik")
    state = FakeState()

    def fake_send_admin_notification(text: str):
        sent["text"] = text

    monkeypatch.setattr("apps.bot.handlers.support.send_admin_notification", fake_send_admin_notification)

    asyncio.run(handle_support_message(message, state))

    assert state.cleared is True
    assert "Ольга" in sent["text"]
    assert "У меня вопрос по бонусам" in sent["text"]
    message.answer.assert_awaited_once()
    assert "отправлено" in message.answer.await_args.args[0].lower()
