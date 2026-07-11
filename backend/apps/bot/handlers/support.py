from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from asgiref.sync import sync_to_async

from apps.bot.ui import (
    MAIN_HELP_BUTTON_TEXT,
    SUPPORT_BUTTON_TEXT,
    build_help_intro_text,
    build_help_menu_keyboard,
    build_support_prompt_text,
    build_support_sent_text,
)
from apps.notifications.telegram import send_admin_notification


router = Router(name="support")


class SupportStates(StatesGroup):
    waiting_message = State()


@router.message(F.text == MAIN_HELP_BUTTON_TEXT)
async def open_help_menu(message: Message) -> None:
    await message.answer(
        build_help_intro_text(),
        reply_markup=build_help_menu_keyboard(),
    )


@router.message(F.text == SUPPORT_BUTTON_TEXT)
async def start_support(message: Message, state: FSMContext) -> None:
    await state.set_state(SupportStates.waiting_message)
    await message.answer(build_support_prompt_text())


@router.message(SupportStates.waiting_message)
async def handle_support_message(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer(build_support_prompt_text())
        return

    username = f"@{message.from_user.username}" if getattr(message.from_user, "username", None) else "без username"
    admin_text = (
        "Новое сообщение администратору из бота.\n"
        f"Пользователь: {message.from_user.full_name}\n"
        f"Telegram ID: {message.from_user.id}\n"
        f"Username: {username}\n"
        f"Сообщение: {text}"
    )
    await sync_to_async(send_admin_notification, thread_sensitive=True)(admin_text)
    await state.clear()
    await message.answer(
        build_support_sent_text(),
        reply_markup=build_help_menu_keyboard(),
    )
