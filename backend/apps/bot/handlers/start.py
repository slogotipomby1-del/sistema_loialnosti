from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from asgiref.sync import sync_to_async

from apps.bot.services import get_participant_referral_data
from apps.bot.ui import (
    build_member_actions_keyboard,
    build_member_start_text,
    build_start_keyboard,
    build_start_text,
)


router = Router(name="start")


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
            reply_markup=build_member_actions_keyboard(),
        )
        return

    await message.answer(
        build_start_text(),
        reply_markup=build_start_keyboard(),
    )
