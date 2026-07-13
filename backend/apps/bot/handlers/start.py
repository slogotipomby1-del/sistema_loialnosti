from pathlib import Path

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message
from asgiref.sync import sync_to_async

from apps.bot.services import get_participant_referral_data
from apps.bot.ui import (
    build_main_menu_keyboard,
    build_member_start_text,
    build_start_keyboard,
    build_start_text,
)


router = Router(name="start")
WELCOME_CARD_PATH = Path(__file__).resolve().parent.parent / "assets" / "welcome_card.png"


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext) -> None:
    await state.clear()

    participant_data = await sync_to_async(
        get_participant_referral_data,
        thread_sensitive=True,
    )(telegram_id=str(message.from_user.id))

    if participant_data:
        full_name, _ = participant_data
        await message.answer(
            build_member_start_text(full_name=full_name),
            reply_markup=build_main_menu_keyboard(),
        )
        return

    await message.answer_photo(
        photo=FSInputFile(str(WELCOME_CARD_PATH)),
    )
    await message.answer(
        build_start_text(),
        reply_markup=build_start_keyboard(),
    )
