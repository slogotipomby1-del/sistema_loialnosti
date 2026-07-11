import asyncio
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

from apps.bot.handlers.member import (
    CONSENT_BUTTON_TEXT,
    RegistrationStates,
    SKIP_BUTTON_TEXT,
    handle_company,
    handle_consent,
    handle_full_name,
    handle_invite_client,
    handle_my_balance,
    handle_my_invited,
    handle_phone,
    handle_position,
    handle_share_link,
    start_registration,
)
from apps.bot.ui import (
    build_empty_invited_text,
    build_invited_text,
    build_profile_company_prompt_text,
    build_profile_position_prompt_text,
    build_profile_saved_text,
    build_registration_success_text,
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
    message.answer.assert_awaited_once()


def test_handle_share_link_returns_personal_link_for_registered_participant(monkeypatch):
    message = AsyncMock()
    message.from_user = SimpleNamespace(id=12345)
    message.bot = AsyncMock()
    message.bot.get_me.return_value = SimpleNamespace(username="SvoyCorpStyleBot")

    monkeypatch.setattr(
        "apps.bot.handlers.member.get_participant_referral_data",
        lambda **kwargs: ("РђРЅРЅР° РРІР°РЅРѕРІР°", "abc123"),
    )

    asyncio.run(handle_share_link(message))

    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0]
    assert "https://t.me/SvoyCorpStyleBot?start=abc123" in sent_text


def test_handle_share_link_asks_to_register_if_participant_not_found(monkeypatch):
    message = AsyncMock()
    message.from_user = SimpleNamespace(id=12345)

    monkeypatch.setattr(
        "apps.bot.handlers.member.get_participant_referral_data",
        lambda **kwargs: None,
    )

    asyncio.run(handle_share_link(message))

    message.answer.assert_awaited_once()


def test_handle_invite_client_returns_ready_message(monkeypatch):
    message = AsyncMock()
    message.from_user = SimpleNamespace(id=12345)
    message.bot = AsyncMock()
    message.bot.get_me.return_value = SimpleNamespace(username="SvoyCorpStyleBot")

    monkeypatch.setattr(
        "apps.bot.handlers.member.get_participant_referral_data",
        lambda **kwargs: ("РђРЅРЅР° РРІР°РЅРѕРІР°", "abc123"),
    )

    asyncio.run(handle_invite_client(message))

    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0]
    assert "https://t.me/SvoyCorpStyleBot?start=abc123" in sent_text


def test_handle_my_balance_returns_balance(monkeypatch):
    message = AsyncMock()
    message.from_user = SimpleNamespace(id=12345)

    monkeypatch.setattr(
        "apps.bot.handlers.member.get_participant_dashboard_data",
        lambda **kwargs: {
            "full_name": "РђРЅРЅР° РРІР°РЅРѕРІР°",
            "referral_code": "abc123",
            "balance": 125.00,
            "invited_leads": [],
        },
    )

    asyncio.run(handle_my_balance(message))

    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0]
    assert "125.00" in sent_text


def test_handle_my_invited_returns_empty_state(monkeypatch):
    message = AsyncMock()
    message.from_user = SimpleNamespace(id=12345)

    monkeypatch.setattr(
        "apps.bot.handlers.member.get_participant_dashboard_data",
        lambda **kwargs: {
            "full_name": "РђРЅРЅР° РРІР°РЅРѕРІР°",
            "referral_code": "abc123",
            "balance": 0,
            "invited_leads": [],
        },
    )

    asyncio.run(handle_my_invited(message))

    message.answer.assert_awaited_once_with(
        build_empty_invited_text(),
        reply_markup=message.answer.await_args.kwargs["reply_markup"],
    )


def test_handle_my_invited_returns_leads(monkeypatch):
    message = AsyncMock()
    message.from_user = SimpleNamespace(id=12345)

    monkeypatch.setattr(
        "apps.bot.handlers.member.get_participant_dashboard_data",
        lambda **kwargs: {
            "full_name": "РђРЅРЅР° РРІР°РЅРѕРІР°",
            "referral_code": "abc123",
            "balance": 0,
            "invited_leads": [("РљРѕРјРїР°РЅРёСЏ Рђ", "ordered", datetime(2026, 7, 10))],
        },
    )

    asyncio.run(handle_my_invited(message))

    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0]
    assert "10.07.2026" in sent_text
    assert "abc123" not in sent_text


def test_handle_full_name_stores_name_and_asks_for_phone():
    message = AsyncMock()
    message.text = "РђРЅРЅР° РРІР°РЅРѕРІР°"
    state = FakeState()

    asyncio.run(handle_full_name(message, state))

    assert state.current_state == RegistrationStates.waiting_phone
    assert state.data["full_name"] == "РђРЅРЅР° РРІР°РЅРѕРІР°"
    message.answer.assert_awaited_once()


def test_handle_phone_stores_phone_and_asks_for_consent():
    message = AsyncMock()
    message.text = "+375291112233"
    message.contact = None
    state = FakeState()

    asyncio.run(handle_phone(message, state))

    assert state.current_state == RegistrationStates.waiting_consent
    assert state.data["phone"] == "+375291112233"
    message.answer.assert_awaited_once()


def test_handle_consent_registers_participant_and_asks_for_company(monkeypatch):
    message = AsyncMock()
    message.text = CONSENT_BUTTON_TEXT
    message.from_user = SimpleNamespace(id=12345)
    message.bot = AsyncMock()
    message.bot.get_me.return_value = SimpleNamespace(username="SvoyCorpStyleBot")

    state = FakeState()
    state.data = {"full_name": "РђРЅРЅР° РРІР°РЅРѕРІР°", "phone": "+375291112233"}
    monkeypatch.setattr(
        "apps.bot.handlers.member.register_participant_with_referral_code",
        lambda **kwargs: ("РђРЅРЅР° РРІР°РЅРѕРІР°", "abc123"),
    )

    asyncio.run(handle_consent(message, state))

    assert state.current_state == RegistrationStates.waiting_company
    assert message.answer.await_count == 2
    assert message.answer.await_args_list[0].args[0] == build_registration_success_text(
        full_name="РђРЅРЅР° РРІР°РЅРѕРІР°",
        referral_url="https://t.me/SvoyCorpStyleBot?start=abc123",
    )
    assert message.answer.await_args_list[1].args[0] == build_profile_company_prompt_text()


def test_handle_company_stores_value_and_asks_for_position():
    message = AsyncMock()
    message.text = "OOO Corporate Style"
    state = FakeState()

    asyncio.run(handle_company(message, state))

    assert state.current_state == RegistrationStates.waiting_position
    assert state.data["company"] == "OOO Corporate Style"
    message.answer.assert_awaited_once_with(
        build_profile_position_prompt_text(),
        reply_markup=message.answer.await_args.kwargs["reply_markup"],
    )


def test_handle_company_skip_keeps_company_empty():
    message = AsyncMock()
    message.text = SKIP_BUTTON_TEXT
    state = FakeState()

    asyncio.run(handle_company(message, state))

    assert state.current_state == RegistrationStates.waiting_position
    assert state.data["company"] == ""


def test_handle_position_saves_profile_and_returns_menu(monkeypatch):
    message = AsyncMock()
    message.text = "РњР°СЂРєРµС‚РѕР»РѕРі"
    message.from_user = SimpleNamespace(id=12345)
    state = FakeState()
    state.data = {"company": "OOO Corporate Style"}

    monkeypatch.setattr(
        "apps.bot.handlers.member.update_participant_profile",
        lambda **kwargs: SimpleNamespace(company=kwargs["company"], position=kwargs["position"]),
    )

    asyncio.run(handle_position(message, state))

    assert state.cleared is True
    message.answer.assert_awaited_once()
    assert message.answer.await_args.args[0] == build_profile_saved_text(
        company="OOO Corporate Style",
        position="РњР°СЂРєРµС‚РѕР»РѕРі",
    )
