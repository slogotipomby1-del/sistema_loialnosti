import asyncio
import os

from aiogram import Bot, Dispatcher

from apps.bot.router import build_router


def get_bot_token() -> str:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required to start the bot")
    return token


def build_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()
    dispatcher.include_router(build_router())
    return dispatcher


async def run() -> None:
    bot = Bot(token=get_bot_token())
    dispatcher = build_dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
