from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message


router = Router(name="start")


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    await message.answer(
        "Здравствуйте! Добро пожаловать в систему лояльности «Корпоративный стиль».\n\n"
        "Здесь вы сможете зарегистрироваться, получить свою реферальную ссылку "
        "и пользоваться возможностями программы."
    )
