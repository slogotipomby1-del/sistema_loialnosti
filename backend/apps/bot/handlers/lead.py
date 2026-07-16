from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from asgiref.sync import sync_to_async

from apps.bot.services import create_self_lead_request
from apps.bot.ui import OWN_COMPANY_ORDER_BUTTON_TEXT, SKIP_BUTTON_TEXT, build_cabinet_keyboard, build_skip_keyboard


router = Router(name="lead")


class LeadStates(StatesGroup):
    waiting_product = State()
    waiting_quantity = State()
    waiting_budget = State()
    waiting_deadline = State()
    waiting_email = State()
    waiting_comment = State()


@router.message(F.text == OWN_COMPANY_ORDER_BUTTON_TEXT)
async def start_lead_flow(message: Message, state: FSMContext) -> None:
    await state.set_state(LeadStates.waiting_product)
    await message.answer("Какая продукция вас интересует?")


@router.message(LeadStates.waiting_product)
async def handle_lead_product(message: Message, state: FSMContext) -> None:
    product = (message.text or "").strip()
    if not product:
        await message.answer("Пожалуйста, напишите, какая продукция вас интересует.")
        return

    await state.update_data(product=product)
    await state.set_state(LeadStates.waiting_quantity)
    await message.answer("Какой нужен тираж?")


@router.message(LeadStates.waiting_quantity)
async def handle_lead_quantity(message: Message, state: FSMContext) -> None:
    quantity = (message.text or "").strip()
    if not quantity:
        await message.answer("Пожалуйста, напишите нужный тираж.")
        return

    await state.update_data(quantity=quantity)
    await state.set_state(LeadStates.waiting_budget)
    await message.answer("Какой ориентировочно бюджет?")


@router.message(LeadStates.waiting_budget)
async def handle_lead_budget(message: Message, state: FSMContext) -> None:
    budget = (message.text or "").strip()
    if not budget:
        await message.answer("Пожалуйста, напишите ориентировочный бюджет.")
        return

    await state.update_data(budget=budget)
    await state.set_state(LeadStates.waiting_deadline)
    await message.answer("Какой желаемый срок?")


@router.message(LeadStates.waiting_deadline)
async def handle_lead_deadline(message: Message, state: FSMContext) -> None:
    deadline = (message.text or "").strip()
    if not deadline:
        await message.answer("Пожалуйста, напишите желаемый срок.")
        return

    await state.update_data(deadline=deadline)
    await state.set_state(LeadStates.waiting_email)
    await message.answer(
        "Если хотите, укажите email для связи. Если не нужно — нажмите «Пропустить».",
        reply_markup=build_skip_keyboard(),
    )


@router.message(LeadStates.waiting_email)
async def handle_lead_email(message: Message, state: FSMContext) -> None:
    email = (message.text or "").strip()
    if email == SKIP_BUTTON_TEXT:
        email = ""
    elif not email:
        await message.answer(
            "Пожалуйста, укажите email или нажмите «Пропустить».",
            reply_markup=build_skip_keyboard(),
        )
        return

    await state.update_data(client_email=email)
    await state.set_state(LeadStates.waiting_comment)
    await message.answer("Комментарий к заявке", reply_markup=build_skip_keyboard())


@router.message(LeadStates.waiting_comment)
async def handle_lead_comment(message: Message, state: FSMContext) -> None:
    comment = (message.text or "").strip()
    if comment == SKIP_BUTTON_TEXT:
        comment = ""
    elif not comment:
        await message.answer("Пожалуйста, добавьте комментарий к заявке.")
        return

    data = await state.get_data()
    await sync_to_async(create_self_lead_request, thread_sensitive=True)(
        telegram_id=str(message.from_user.id),
        product=data["product"],
        quantity=data["quantity"],
        budget=data["budget"],
        deadline=data["deadline"],
        client_email=data.get("client_email", ""),
        comment=comment,
    )
    await state.clear()
    await message.answer(
        "Заявка принята. Мы свяжемся с вами после обработки.",
        reply_markup=build_cabinet_keyboard(),
    )
