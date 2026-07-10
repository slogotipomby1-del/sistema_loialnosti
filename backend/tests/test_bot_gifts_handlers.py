import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from apps.bot.gifts import build_gift_button_text
from apps.bot.handlers.gifts import handle_gift_request, handle_gifts_menu


def test_handle_gifts_menu_shows_gifts_for_registered_participant(monkeypatch):
    message = AsyncMock()
    message.from_user = SimpleNamespace(id=12345)

    monkeypatch.setattr(
        "apps.bot.handlers.gifts.get_participant_by_telegram_id",
        lambda **kwargs: SimpleNamespace(full_name="Ольга", phone="+375291234567"),
    )

    asyncio.run(handle_gifts_menu(message))

    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0]
    assert "Термокружка" in sent_text
    assert "Худи" in sent_text


def test_handle_gift_request_creates_bonus_request_and_notifies_admin(monkeypatch):
    created = {}
    notified = {}
    message = AsyncMock()
    message.text = build_gift_button_text(
        {
            "title": "Термокружка с логотипом",
            "amount": 60,
        }
    )
    message.from_user = SimpleNamespace(id=12345)

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

    asyncio.run(handle_gift_request(message))

    assert created["participant"] is participant
    assert created["amount"] == 60
    assert created["comment"] == "Термокружка с логотипом"
    assert "Термокружка" in notified["text"]
    message.answer.assert_awaited_once()
    assert "Заявка на подарок" in message.answer.await_args.args[0]
