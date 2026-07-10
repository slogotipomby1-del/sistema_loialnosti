import asyncio
from unittest.mock import AsyncMock

from apps.bot.handlers import start


def test_start_command_replies_with_welcome_message():
    message = AsyncMock()

    asyncio.run(start.handle_start(message))

    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0]
    assert "Корпоративный стиль" in sent_text
    assert "зарегистрироваться" in sent_text.lower()
