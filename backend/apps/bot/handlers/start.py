from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from apps.bot.ui import build_start_keyboard, build_start_text


router = Router(name="start")


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    await message.answer(
        build_start_text(),
        reply_markup=build_start_keyboard(),
    )
