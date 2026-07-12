import asyncio
from unittest.mock import AsyncMock

from apps.bot.handlers.catalog import (
    handle_catalog,
    handle_rules,
    handle_spend_bonuses,
    open_spend_menu,
)


def test_open_spend_menu_returns_intro():
    message = AsyncMock()

    asyncio.run(open_spend_menu(message))

    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0].lower()
    assert "подарки" in sent_text
    assert "списания" in sent_text


def test_handle_catalog_returns_site_and_ideas():
    message = AsyncMock()

    asyncio.run(handle_catalog(message))

    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0]
    assert "https://slogotipom.by/" in sent_text
    assert "welcome pack" in sent_text.lower()


def test_handle_rules_returns_program_rules():
    message = AsyncMock()

    asyncio.run(handle_rules(message))

    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0]
    assert "нельзя вывести деньгами" in sent_text.lower()
    assert "2000 byn" in sent_text.lower()


def test_handle_spend_bonuses_returns_usage_rules():
    message = AsyncMock()

    asyncio.run(handle_spend_bonuses(message))

    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0]
    assert "20%" in sent_text
    assert "200 byn" in sent_text.lower()
