from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.types import Message
from asgiref.sync import sync_to_async

from apps.bot.services import get_participant_referral_data
from apps.bot.ui import build_main_menu_keyboard, build_start_keyboard


router = Router(name="fallback")


@router.message(StateFilter(None))
async def handle_fallback(message: Message) -> None:
    participant_data = await sync_to_async(
        get_participant_referral_data,
        thread_sensitive=True,
    )(telegram_id=str(message.from_user.id))

    if participant_data:
        await message.answer(
            "Похоже, клавиатура скрылась. Показываю главное меню.",
            reply_markup=build_main_menu_keyboard(),
        )
        return

    await message.answer(
        "Показываю стартовое меню. Нажмите кнопку ниже, чтобы зарегистрироваться.",
        reply_markup=build_start_keyboard(),
    )
