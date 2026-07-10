import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from apps.bot.handlers.member import (
    CONSENT_BUTTON_TEXT,
    RegistrationStates,
    handle_consent,
    handle_full_name,
    handle_invite_client,
    handle_phone,
    handle_share_link,
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


def test_handle_share_link_returns_personal_link_for_registered_participant(monkeypatch):
    message = AsyncMock()
    message.from_user = SimpleNamespace(id=12345)
    message.bot = AsyncMock()
    message.bot.get_me.return_value = SimpleNamespace(username="SvoyCorpStyleBot")

    monkeypatch.setattr(
        "apps.bot.handlers.member.get_participant_referral_data",
        lambda **kwargs: ("Анна Иванова", "abc123"),
    )

    asyncio.run(handle_share_link(message))

    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0]
    assert "Анна Иванова" in sent_text
    assert "https://t.me/SvoyCorpStyleBot?start=abc123" in sent_text
    assert "мерч-бонусы" in sent_text.lower()


def test_handle_share_link_asks_to_register_if_participant_not_found(monkeypatch):
    message = AsyncMock()
    message.from_user = SimpleNamespace(id=12345)

    monkeypatch.setattr(
        "apps.bot.handlers.member.get_participant_referral_data",
        lambda **kwargs: None,
    )

    asyncio.run(handle_share_link(message))

    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0]
    assert "Сначала нужно зарегистрироваться" in sent_text


def test_handle_invite_client_returns_ready_message(monkeypatch):
    message = AsyncMock()
    message.from_user = SimpleNamespace(id=12345)
    message.bot = AsyncMock()
    message.bot.get_me.return_value = SimpleNamespace(username="SvoyCorpStyleBot")

    monkeypatch.setattr(
        "apps.bot.handlers.member.get_participant_referral_data",
        lambda **kwargs: ("Анна Иванова", "abc123"),
    )

    asyncio.run(handle_invite_client(message))

    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0]
    assert "https://t.me/SvoyCorpStyleBot?start=abc123" in sent_text
    assert "корпоративный стиль" in sent_text.lower()


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

    state = FakeState()
    state.data = {"full_name": "Анна Иванова", "phone": "+375291112233"}
    monkeypatch.setattr(
        "apps.bot.handlers.member.register_participant_with_referral_code",
        lambda **kwargs: ("Анна Иванова", "abc123"),
    )

    asyncio.run(handle_consent(message, state))

    assert state.cleared is True
    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0]
    assert "зарегистрированы" in sent_text.lower()
    assert "https://t.me/SvoyCorpStyleBot?start=abc123" in sent_text
