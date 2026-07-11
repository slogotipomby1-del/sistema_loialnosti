from aiogram import F, Router
from aiogram.types import Message

from apps.bot.ui import (
    CATALOG_BUTTON_TEXT,
    HOW_SPEND_BUTTON_TEXT,
    MAIN_SPEND_BUTTON_TEXT,
    RULES_BUTTON_TEXT,
    build_catalog_text,
    build_help_menu_keyboard,
    build_rules_text,
    build_spend_bonuses_text,
    build_spend_intro_text,
    build_spend_menu_keyboard,
)


router = Router(name="catalog")


@router.message(F.text == MAIN_SPEND_BUTTON_TEXT)
async def open_spend_menu(message: Message) -> None:
    await message.answer(
        build_spend_intro_text(),
        reply_markup=build_spend_menu_keyboard(),
    )


@router.message(F.text == CATALOG_BUTTON_TEXT)
async def handle_catalog(message: Message) -> None:
    await message.answer(
        build_catalog_text(),
        reply_markup=build_spend_menu_keyboard(),
    )


@router.message(F.text == RULES_BUTTON_TEXT)
async def handle_rules(message: Message) -> None:
    await message.answer(
        build_rules_text(),
        reply_markup=build_help_menu_keyboard(),
    )


@router.message(F.text == HOW_SPEND_BUTTON_TEXT)
async def handle_spend_bonuses(message: Message) -> None:
    await message.answer(
        build_spend_bonuses_text(),
        reply_markup=build_spend_menu_keyboard(),
    )
