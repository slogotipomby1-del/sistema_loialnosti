from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from asgiref.sync import sync_to_async

from apps.bot.gifts import GIFT_OFFERS, get_gift_offer
from apps.bot.services import create_bonus_spend_request, get_participant_by_telegram_id
from apps.bot.ui import (
    GIFTS_BUTTON_TEXT,
    build_gift_card_keyboard,
    build_gift_card_text,
    build_gift_request_sent_text,
    build_gifts_intro_text,
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
        reply_markup=build_member_actions_keyboard(),
    )

    for index, offer in enumerate(GIFT_OFFERS, start=1):
        await message.answer(
            build_gift_card_text(
                index=index,
                title=offer["title"],
                description=offer["description"],
                amount=offer["amount"],
                is_available=offer["is_available"],
            ),
            reply_markup=build_gift_card_keyboard(
                slug=offer["slug"],
                is_available=offer["is_available"],
            ),
        )


@router.callback_query(F.data.startswith("gift:choose:"))
async def handle_gift_request(callback: CallbackQuery) -> None:
    participant = await sync_to_async(
        get_participant_by_telegram_id,
        thread_sensitive=True,
    )(telegram_id=str(callback.from_user.id))

    if not participant:
        await callback.answer("Сначала нужно зарегистрироваться.", show_alert=True)
        if callback.message:
            await callback.message.answer(
                "Сначала нужно зарегистрироваться, чтобы заказывать подарки за бонусы.",
                reply_markup=build_start_keyboard(),
            )
        return

    slug = callback.data.split(":")[-1]
    offer = get_gift_offer(slug)
    if not offer or not offer["is_available"]:
        await callback.answer("Этот подарок пока недоступен.", show_alert=True)
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
    await callback.answer("Заявка отправлена")
    if callback.message:
        await callback.message.answer(
            build_gift_request_sent_text(
                gift_title=offer["title"],
                gift_amount=offer["amount"],
            ),
            reply_markup=build_member_actions_keyboard(),
        )


@router.callback_query(F.data.startswith("gift:soon:"))
async def handle_soon_gift(callback: CallbackQuery) -> None:
    await callback.answer("Эта позиция пока в разработке.", show_alert=True)
