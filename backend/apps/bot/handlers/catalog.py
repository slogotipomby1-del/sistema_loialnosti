from aiogram import F, Router
from aiogram.types import Message

from apps.bot.ui import (
    CATALOG_BUTTON_TEXT,
    RULES_BUTTON_TEXT,
    SPEND_BONUSES_BUTTON_TEXT,
    build_catalog_text,
    build_member_actions_keyboard,
    build_rules_text,
    build_spend_bonuses_text,
)


router = Router(name="catalog")


@router.message(F.text == CATALOG_BUTTON_TEXT)
async def handle_catalog(message: Message) -> None:
    await message.answer(
        build_catalog_text(),
        reply_markup=build_member_actions_keyboard(),
    )


@router.message(F.text == RULES_BUTTON_TEXT)
async def handle_rules(message: Message) -> None:
    await message.answer(
        build_rules_text(),
        reply_markup=build_member_actions_keyboard(),
    )


@router.message(F.text == SPEND_BONUSES_BUTTON_TEXT)
async def handle_spend_bonuses(message: Message) -> None:
    await message.answer(
        build_spend_bonuses_text(),
        reply_markup=build_member_actions_keyboard(),
    )
