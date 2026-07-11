import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from apps.bot.handlers.gifts import handle_gift_request, handle_gifts_menu, handle_soon_gift


def test_handle_gifts_menu_sends_intro_and_five_cards(monkeypatch):
    message = AsyncMock()
    message.from_user = SimpleNamespace(id=12345)

    monkeypatch.setattr(
        "apps.bot.handlers.gifts.get_participant_by_telegram_id",
        lambda **kwargs: SimpleNamespace(full_name="Ольга", phone="+375291234567"),
    )

    asyncio.run(handle_gifts_menu(message))

    assert message.answer.await_count == 6
    first_text = message.answer.await_args_list[0].args[0]
    second_text = message.answer.await_args_list[1].args[0]
    third_text = message.answer.await_args_list[2].args[0]
    assert "5 карточек" in first_text
    assert "Рюкзак" in second_text
    assert "Термокружка" in third_text


def test_handle_gift_request_creates_bonus_request_and_notifies_admin(monkeypatch):
    created = {}
    notified = {}
    callback = AsyncMock()
    callback.data = "gift:choose:mug"
    callback.from_user = SimpleNamespace(id=12345)
    callback.message = AsyncMock()

    participant = SimpleNamespace(full_name="Ольга", phone="+375291234567")

    monkeypatch.setattr(
        "apps.bot.handlers.gifts.get_participant_by_telegram_id",
        lambda **kwargs: participant,
    )

    def fake_create_bonus_spend_request(**kwargs):
        created.update(kwargs)

    def fake_send_admin_notification(text: str):
        notified["text"] = text

    monkeypatch.setattr("apps.bot.handlers.gifts.create_bonus_spend_request", fake_create_bonus_spend_request)
    monkeypatch.setattr("apps.bot.handlers.gifts.send_admin_notification", fake_send_admin_notification)

    asyncio.run(handle_gift_request(callback))

    assert created["participant"] is participant
    assert created["amount"] == 60
    assert created["comment"] == "Термокружка"
    assert "Термокружка" in notified["text"]
    callback.answer.assert_awaited()
    callback.message.answer.assert_awaited_once()


def test_handle_soon_gift_shows_placeholder_message():
    callback = AsyncMock()
    callback.data = "gift:soon:soon_1"

    asyncio.run(handle_soon_gift(callback))

    callback.answer.assert_awaited_once()
