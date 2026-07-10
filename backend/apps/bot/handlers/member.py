from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from asgiref.sync import sync_to_async

from apps.bot.services import (
    get_participant_referral_data,
    register_participant_with_referral_code,
)
from apps.bot.ui import (
    CONSENT_BUTTON_TEXT,
    REGISTER_BUTTON_TEXT,
    SHARE_LINK_BUTTON_TEXT,
    build_consent_keyboard,
    build_member_actions_keyboard,
    build_phone_keyboard,
    build_registration_success_text,
    build_share_link_text,
    build_start_keyboard,
)


router = Router(name="member")


class RegistrationStates(StatesGroup):
    waiting_full_name = State()
    waiting_phone = State()
    waiting_consent = State()


async def build_referral_url(message: Message, referral_code: str) -> str:
    bot_info = await message.bot.get_me()
    return f"https://t.me/{bot_info.username}?start={referral_code}"


@router.message(F.text == REGISTER_BUTTON_TEXT)
async def start_registration(message: Message, state: FSMContext) -> None:
    await state.set_state(RegistrationStates.waiting_full_name)
    await message.answer("Как вас зовут?")


@router.message(F.text == SHARE_LINK_BUTTON_TEXT)
async def handle_share_link(message: Message) -> None:
    participant_data = await sync_to_async(
        get_participant_referral_data,
        thread_sensitive=True,
    )(telegram_id=str(message.from_user.id))

    if not participant_data:
        await message.answer(
            "Сначала нужно зарегистрироваться, чтобы получить персональную ссылку.",
            reply_markup=build_start_keyboard(),
        )
        return

    full_name, referral_code = participant_data
    referral_url = await build_referral_url(message, referral_code)
    await message.answer(
        build_share_link_text(
            full_name=full_name,
            referral_url=referral_url,
        ),
        reply_markup=build_member_actions_keyboard(),
    )


@router.message(RegistrationStates.waiting_full_name)
async def handle_full_name(message: Message, state: FSMContext) -> None:
    full_name = (message.text or "").strip()
    if not full_name:
        await message.answer("Пожалуйста, напишите ваше имя.")
        return

    await state.update_data(full_name=full_name)
    await state.set_state(RegistrationStates.waiting_phone)
    await message.answer(
        "Укажите ваш телефон.",
        reply_markup=build_phone_keyboard(),
    )


@router.message(RegistrationStates.waiting_phone)
async def handle_phone(message: Message, state: FSMContext) -> None:
    phone = ""
    if message.contact and message.contact.phone_number:
        phone = message.contact.phone_number.strip()
    elif message.text:
        phone = message.text.strip()

    if not phone:
        await message.answer(
            "Пожалуйста, отправьте номер телефона.",
            reply_markup=build_phone_keyboard(),
        )
        return

    await state.update_data(phone=phone)
    await state.set_state(RegistrationStates.waiting_consent)
    await message.answer(
        "Подтвердите согласие на обработку персональных данных.",
        reply_markup=build_consent_keyboard(),
    )


@router.message(RegistrationStates.waiting_consent, F.text == CONSENT_BUTTON_TEXT)
async def handle_consent(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    full_name, referral_code = await sync_to_async(
        register_participant_with_referral_code,
        thread_sensitive=True,
    )(
        telegram_id=str(message.from_user.id),
        full_name=data["full_name"],
        phone=data["phone"],
        consent_accepted=True,
    )
    referral_url = await build_referral_url(message, referral_code)
    await state.clear()
    await message.answer(
        build_registration_success_text(
            full_name=full_name,
            referral_url=referral_url,
        ),
        reply_markup=build_member_actions_keyboard(),
    )


@router.message(RegistrationStates.waiting_consent)
async def handle_consent_required(message: Message) -> None:
    await message.answer(
        "Чтобы завершить регистрацию, нажмите кнопку согласия.",
        reply_markup=build_consent_keyboard(),
    )
