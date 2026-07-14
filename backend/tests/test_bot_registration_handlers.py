import asyncio
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

from apps.bot.handlers.member import (
    CONSENT_BUTTON_TEXT,
    RegistrationStates,
    SKIP_BUTTON_TEXT,
    back_to_main_menu,
    handle_bonus_history,
    handle_company,
    handle_consent,
    handle_full_name,
    handle_invite_client,
    handle_my_balance,
    handle_my_recommendations,
    handle_my_requests,
    handle_phone,
    handle_position,
    handle_share_link,
    open_cabinet_menu,
    open_recommend_menu,
    start_registration,
)
from apps.bot.ui import (
    build_cabinet_intro_text,
    build_consent_prompt_text,
    build_empty_invited_text,
    build_empty_requests_text,
    build_main_menu_keyboard,
    build_profile_company_prompt_text,
    build_profile_position_prompt_text,
    build_profile_saved_text,
    build_recommend_intro_text,
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
    assert "давайте познакомимся" in message.answer.await_args.args[0].lower()


def test_open_cabinet_menu_returns_intro():
    message = AsyncMock()

    asyncio.run(open_cabinet_menu(message))

    message.answer.assert_awaited_once()
    assert message.answer.await_args.args[0] == build_cabinet_intro_text()


def test_open_recommend_menu_returns_intro():
    message = AsyncMock()

    asyncio.run(open_recommend_menu(message))

    message.answer.assert_awaited_once()
    assert message.answer.await_args.args[0] == build_recommend_intro_text()


def test_back_to_main_menu_returns_main_menu():
    message = AsyncMock()

    asyncio.run(back_to_main_menu(message))

    message.answer.assert_awaited_once_with("Главное меню.", reply_markup=build_main_menu_keyboard())


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
    assert "https://t.me/SvoyCorpStyleBot?start=abc123" in message.answer.await_args.args[0]


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
    assert "https://t.me/SvoyCorpStyleBot?start=abc123" in message.answer.await_args.args[0]


def test_handle_my_balance_returns_balance(monkeypatch):
    message = AsyncMock()
    message.from_user = SimpleNamespace(id=12345)

    monkeypatch.setattr(
        "apps.bot.handlers.member.get_participant_dashboard_data",
        lambda **kwargs: {
            "full_name": "Анна Иванова",
            "referral_code": "abc123",
            "balance": 125.00,
            "invited_leads": [],
        },
    )

    asyncio.run(handle_my_balance(message))

    message.answer.assert_awaited_once()
    assert "125.00" in message.answer.await_args.args[0]


def test_handle_bonus_history_returns_empty_state(monkeypatch):
    message = AsyncMock()
    message.from_user = SimpleNamespace(id=12345)

    monkeypatch.setattr(
        "apps.bot.handlers.member.get_participant_bonus_history_data",
        lambda **kwargs: {"accruals": [], "spendings": []},
    )

    asyncio.run(handle_bonus_history(message))

    message.answer.assert_awaited_once()
    assert "истории бонусов нет операций" in message.answer.await_args.args[0].lower()


def test_handle_bonus_history_returns_operations(monkeypatch):
    message = AsyncMock()
    message.from_user = SimpleNamespace(id=12345)

    monkeypatch.setattr(
        "apps.bot.handlers.member.get_participant_bonus_history_data",
        lambda **kwargs: {
            "accruals": [(60, "За рекомендацию", datetime(2026, 7, 10))],
            "spendings": [(40, "Термокружка", datetime(2026, 7, 11))],
        },
    )

    asyncio.run(handle_bonus_history(message))

    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0]
    assert "за рекомендацию" in sent_text.lower()
    assert "термокружка" in sent_text.lower()


def test_handle_my_recommendations_returns_empty_state(monkeypatch):
    message = AsyncMock()
    message.from_user = SimpleNamespace(id=12345)

    monkeypatch.setattr(
        "apps.bot.handlers.member.get_participant_dashboard_data",
        lambda **kwargs: {
            "full_name": "Анна Иванова",
            "referral_code": "abc123",
            "balance": 0,
            "invited_leads": [],
        },
    )

    asyncio.run(handle_my_recommendations(message))

    message.answer.assert_awaited_once()
    assert message.answer.await_args.args[0] == build_empty_invited_text()


def test_handle_my_recommendations_returns_leads(monkeypatch):
    message = AsyncMock()
    message.from_user = SimpleNamespace(id=12345)

    monkeypatch.setattr(
        "apps.bot.handlers.member.get_participant_dashboard_data",
        lambda **kwargs: {
            "full_name": "Анна Иванова",
            "referral_code": "abc123",
            "balance": 0,
            "invited_leads": [("Компания А", "ordered", datetime(2026, 7, 10))],
        },
    )

    asyncio.run(handle_my_recommendations(message))

    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0]
    assert "Компания А" in sent_text
    assert "10.07.2026" in sent_text


def test_handle_my_requests_returns_empty_state(monkeypatch):
    message = AsyncMock()
    message.from_user = SimpleNamespace(id=12345)

    monkeypatch.setattr(
        "apps.bot.handlers.member.get_participant_requests_data",
        lambda **kwargs: {"own_leads": [], "spend_requests": []},
    )

    asyncio.run(handle_my_requests(message))

    message.answer.assert_awaited_once()
    assert message.answer.await_args.args[0] == build_empty_requests_text()


def test_handle_my_requests_returns_requests(monkeypatch):
    message = AsyncMock()
    message.from_user = SimpleNamespace(id=12345)

    monkeypatch.setattr(
        "apps.bot.handlers.member.get_participant_requests_data",
        lambda **kwargs: {
            "own_leads": [("ООО Тест", "new", datetime(2026, 7, 10))],
            "spend_requests": [("Термокружка", "pending", datetime(2026, 7, 11))],
        },
    )

    asyncio.run(handle_my_requests(message))

    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0]
    assert "ООО Тест" in sent_text
    assert "Термокружка" in sent_text


def test_handle_full_name_stores_name_and_asks_for_phone():
    message = AsyncMock()
    message.text = "Анна Иванова"
    state = FakeState()

    asyncio.run(handle_full_name(message, state))

    assert state.current_state == RegistrationStates.waiting_phone
    assert state.data["full_name"] == "Анна Иванова"
    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0].lower()
    assert "укажите ваш телефон" in sent_text
    assert "заявкам и бонусам" in sent_text


def test_handle_phone_stores_phone_and_asks_for_consent():
    message = AsyncMock()
    message.text = "+375291112233"
    message.contact = None
    state = FakeState()

    asyncio.run(handle_phone(message, state))

    assert state.current_state == RegistrationStates.waiting_consent
    assert state.data["phone"] == "+375291112233"
    message.answer.assert_awaited_once()
    assert message.answer.await_args.args[0] == build_consent_prompt_text()


def test_handle_consent_registers_participant_and_asks_for_company(monkeypatch):
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

    assert state.current_state == RegistrationStates.waiting_company
    assert message.answer.await_count == 2
    assert message.answer.await_args_list[0].args[0] == build_registration_success_text(
        full_name="Анна Иванова",
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
    message.answer.assert_awaited_once()
    assert message.answer.await_args.args[0] == build_profile_position_prompt_text()


def test_handle_company_skip_keeps_company_empty():
    message = AsyncMock()
    message.text = SKIP_BUTTON_TEXT
    state = FakeState()

    asyncio.run(handle_company(message, state))

    assert state.current_state == RegistrationStates.waiting_position
    assert state.data["company"] == ""


def test_handle_position_saves_profile_and_returns_menu(monkeypatch):
    message = AsyncMock()
    message.text = "Маркетолог"
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
        position="Маркетолог",
    )


def test_registration_success_text_mentions_available_sections():
    text = build_registration_success_text(
        full_name="Анна Иванова",
        referral_url="https://t.me/SvoyCorpStyleBot?start=abc123",
    )

    assert "ваша ссылка" in text.lower()
    assert "баланс и история бонусов" in text.lower()
    assert "подарки за бонусы" in text.lower()
