import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from apps.bot.handlers.member import (
    CONSENT_BUTTON_TEXT,
    RegistrationStates,
    handle_consent,
    handle_full_name,
    handle_phone,
    start_registration,
)


class FakeState:
    def __init__(self):
        self.current_state = None
        self.data = {}
        self.cleared = False

    async def set_state(self, state):
        self.current_state = state

    async def update_data(self, **kwargs):
        self.data.update(kwargs)

    async def get_data(self):
        return self.data

    async def clear(self):
        self.cleared = True
        self.current_state = None


def test_start_registration_asks_for_name():
    message = AsyncMock()
    state = FakeState()

    asyncio.run(start_registration(message, state))

    assert state.current_state == RegistrationStates.waiting_full_name
    message.answer.assert_awaited_once_with("Как вас зовут?")


def test_handle_full_name_stores_name_and_asks_for_phone():
    message = AsyncMock()
    message.text = "Анна Иванова"
    state = FakeState()

    asyncio.run(handle_full_name(message, state))

    assert state.current_state == RegistrationStates.waiting_phone
    assert state.data["full_name"] == "Анна Иванова"
    message.answer.assert_awaited_once()
    assert "телефон" in message.answer.await_args.args[0].lower()


def test_handle_phone_stores_phone_and_asks_for_consent():
    message = AsyncMock()
    message.text = "+375291112233"
    message.contact = None
    state = FakeState()

    asyncio.run(handle_phone(message, state))

    assert state.current_state == RegistrationStates.waiting_consent
    assert state.data["phone"] == "+375291112233"
    message.answer.assert_awaited_once()
    assert "согласие" in message.answer.await_args.args[0].lower()


def test_handle_consent_registers_participant_and_returns_referral_link(monkeypatch):
    message = AsyncMock()
    message.text = CONSENT_BUTTON_TEXT
    message.from_user = SimpleNamespace(id=12345)
    message.bot = AsyncMock()
    message.bot.get_me.return_value = SimpleNamespace(username="SvoyCorpStyleBot")

    participant = SimpleNamespace(
        full_name="Анна Иванова",
        referral_link=SimpleNamespace(code="abc123"),
    )

    state = FakeState()
    state.data = {"full_name": "Анна Иванова", "phone": "+375291112233"}

    register_mock = AsyncMock()
    monkeypatch.setattr(
        "apps.bot.handlers.member.register_participant",
        lambda **kwargs: participant,
    )

    asyncio.run(handle_consent(message, state))

    assert state.cleared is True
    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0]
    assert "зарегистрированы" in sent_text.lower()
    assert "https://t.me/SvoyCorpStyleBot?start=abc123" in sent_text
