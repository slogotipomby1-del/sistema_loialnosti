from aiogram import F, Router
from aiogram.types import Message
from asgiref.sync import sync_to_async

from apps.bot.gifts import GIFT_OFFERS, build_gift_button_text, get_gift_offer_by_button
from apps.bot.services import create_bonus_spend_request, get_participant_by_telegram_id
from apps.bot.ui import (
    BACK_TO_MENU_BUTTON_TEXT,
    GIFTS_BUTTON_TEXT,
    build_gift_request_sent_text,
    build_gifts_intro_text,
    build_gifts_keyboard,
    build_member_actions_keyboard,
    build_start_keyboard,
)
from apps.notifications.telegram import send_admin_notification


router = Router(name="gifts")


@router.message(F.text == GIFTS_BUTTON_TEXT)
async def handle_gifts_menu(message: Message) -> None:
    participant = await sync_to_async(
        get_participant_by_telegram_id,
        thread_sensitive=True,
    )(telegram_id=str(message.from_user.id))

    if not participant:
        await message.answer(
            "Сначала нужно зарегистрироваться, чтобы заказывать подарки за бонусы.",
            reply_markup=build_start_keyboard(),
        )
        return

    await message.answer(
        build_gifts_intro_text(),
        reply_markup=build_gifts_keyboard(),
    )


@router.message(F.text == BACK_TO_MENU_BUTTON_TEXT)
async def handle_back_to_menu(message: Message) -> None:
    await message.answer(
        "Возвращаю вас в главное меню.",
        reply_markup=build_member_actions_keyboard(),
    )


@router.message(F.text.in_([build_gift_button_text(offer) for offer in GIFT_OFFERS]))
async def handle_gift_request(message: Message) -> None:
    participant = await sync_to_async(
        get_participant_by_telegram_id,
        thread_sensitive=True,
    )(telegram_id=str(message.from_user.id))

    if not participant:
        await message.answer(
            "Сначала нужно зарегистрироваться, чтобы заказывать подарки за бонусы.",
            reply_markup=build_start_keyboard(),
        )
        return

    offer = get_gift_offer_by_button(message.text or "")
    if not offer:
        await message.answer(
            "Не смог понять, какой подарок вы выбрали. Попробуйте ещё раз.",
            reply_markup=build_gifts_keyboard(),
        )
        return

    await sync_to_async(
        create_bonus_spend_request,
        thread_sensitive=True,
    )(
        participant=participant,
        amount=offer["amount"],
        comment=offer["title"],
    )
    send_admin_notification(
        f"Новая заявка на подарок.\n"
        f"Участник: {participant.full_name}\n"
        f"Телефон: {participant.phone}\n"
        f"Подарок: {offer['title']}\n"
        f"Сумма: {offer['amount']} бонусов"
    )
    await message.answer(
        build_gift_request_sent_text(
            gift_title=offer["title"],
            gift_amount=offer["amount"],
        ),
        reply_markup=build_member_actions_keyboard(),
    )
