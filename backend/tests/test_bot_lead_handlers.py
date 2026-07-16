import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from apps.bot.handlers.lead import (
    LeadStates,
    handle_lead_budget,
    handle_lead_comment,
    handle_lead_deadline,
    handle_lead_email,
    handle_lead_product,
    handle_lead_quantity,
    start_lead_flow,
)


class FakeState:
    def __init__(self):
        self.current_state = None
        self.data = {}
        self.cleared = False

    async def set_state(self, state):
        self.current_state = state

    async def update_data(self, **kwargs):
        self.data.update(kwargs)

    async def get_data(self):
        return self.data

    async def clear(self):
        self.cleared = True
        self.current_state = None


def test_start_lead_flow_asks_for_product():
    message = AsyncMock()
    state = FakeState()

    asyncio.run(start_lead_flow(message, state))

    assert state.current_state == LeadStates.waiting_product
    message.answer.assert_awaited_once()
    assert "продукция" in message.answer.await_args.args[0].lower()


def test_handle_lead_product_asks_for_quantity():
    message = AsyncMock()
    message.text = "Визитки"
    state = FakeState()

    asyncio.run(handle_lead_product(message, state))

    assert state.current_state == LeadStates.waiting_quantity
    assert state.data["product"] == "Визитки"
    assert "тираж" in message.answer.await_args.args[0].lower()


def test_handle_lead_quantity_asks_for_comment():
    message = AsyncMock()
    message.text = "500"
    state = FakeState()

    asyncio.run(handle_lead_quantity(message, state))

    assert state.current_state == LeadStates.waiting_budget
    assert state.data["quantity"] == "500"
    assert "бюджет" in message.answer.await_args.args[0].lower()


def test_handle_lead_budget_asks_for_deadline():
    message = AsyncMock()
    message.text = "до 3000 BYN"
    state = FakeState()

    asyncio.run(handle_lead_budget(message, state))

    assert state.current_state == LeadStates.waiting_deadline
    assert state.data["budget"] == "до 3000 BYN"
    assert "срок" in message.answer.await_args.args[0].lower()


def test_handle_lead_deadline_asks_for_email():
    message = AsyncMock()
    message.text = "до конца месяца"
    state = FakeState()

    asyncio.run(handle_lead_deadline(message, state))

    assert state.current_state == LeadStates.waiting_email
    assert state.data["deadline"] == "до конца месяца"
    assert "email" in message.answer.await_args.args[0].lower()


def test_handle_lead_email_asks_for_comment():
    message = AsyncMock()
    message.text = "test@example.com"
    state = FakeState()

    asyncio.run(handle_lead_email(message, state))

    assert state.current_state == LeadStates.waiting_comment
    assert state.data["client_email"] == "test@example.com"
    assert "комментар" in message.answer.await_args.args[0].lower()


def test_handle_lead_comment_creates_request_and_confirms(monkeypatch):
    message = AsyncMock()
    message.text = "Нужно срочно"
    message.from_user = SimpleNamespace(id=123)
    state = FakeState()
    state.data = {
        "product": "Визитки",
        "quantity": "500",
        "budget": "до 3000 BYN",
        "deadline": "до конца месяца",
        "client_email": "test@example.com",
    }

    monkeypatch.setattr(
        "apps.bot.handlers.lead.create_self_lead_request",
        lambda **kwargs: None,
    )

    asyncio.run(handle_lead_comment(message, state))

    assert state.cleared is True
    message.answer.assert_awaited_once()
    assert "заявка принята" in message.answer.await_args.args[0].lower()
