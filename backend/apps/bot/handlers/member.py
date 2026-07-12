from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from asgiref.sync import sync_to_async

from apps.bot.services import (
    get_participant_bonus_history_data,
    get_participant_dashboard_data,
    get_participant_referral_data,
    get_participant_requests_data,
    register_participant_with_referral_code,
    update_participant_profile,
)
from apps.common.choices import get_lead_status_label, get_spend_request_status_label
from apps.bot.ui import (
    BACK_TO_MENU_BUTTON_TEXT,
    CONSENT_BUTTON_TEXT,
    MAIN_CABINET_BUTTON_TEXT,
    MAIN_RECOMMEND_BUTTON_TEXT,
    MY_BALANCE_BUTTON_TEXT,
    MY_HISTORY_BUTTON_TEXT,
    MY_LINK_BUTTON_TEXT,
    MY_RECOMMENDATIONS_BUTTON_TEXT,
    MY_REQUESTS_BUTTON_TEXT,
    READY_TEXT_BUTTON_TEXT,
    REGISTER_BUTTON_TEXT,
    SKIP_BUTTON_TEXT,
    build_balance_text,
    build_bonus_history_text,
    build_cabinet_intro_text,
    build_cabinet_keyboard,
    build_consent_keyboard,
    build_empty_invited_text,
    build_empty_bonus_history_text,
    build_empty_requests_text,
    build_help_menu_keyboard,
    build_invite_client_text,
    build_invited_text,
    build_main_menu_keyboard,
    build_member_actions_keyboard,
    build_my_requests_text,
    build_phone_keyboard,
    build_profile_company_prompt_text,
    build_profile_position_prompt_text,
    build_profile_saved_text,
    build_recommend_intro_text,
    build_recommend_keyboard,
    build_registration_success_text,
    build_share_link_text,
    build_skip_keyboard,
    build_spend_menu_keyboard,
    build_start_keyboard,
)


router = Router(name="member")


class RegistrationStates(StatesGroup):
    waiting_full_name = State()
    waiting_phone = State()
    waiting_consent = State()
    waiting_company = State()
    waiting_position = State()


async def build_referral_url(message: Message, referral_code: str) -> str:
    bot_info = await message.bot.get_me()
    return f"https://t.me/{bot_info.username}?start={referral_code}"


@router.message(F.text == REGISTER_BUTTON_TEXT)
async def start_registration(message: Message, state: FSMContext) -> None:
    await state.set_state(RegistrationStates.waiting_full_name)
    await message.answer("Как вас зовут?")


@router.message(F.text == MAIN_CABINET_BUTTON_TEXT)
async def open_cabinet_menu(message: Message) -> None:
    await message.answer(
        build_cabinet_intro_text(),
        reply_markup=build_cabinet_keyboard(),
    )


@router.message(F.text == MAIN_RECOMMEND_BUTTON_TEXT)
async def open_recommend_menu(message: Message) -> None:
    await message.answer(
        build_recommend_intro_text(),
        reply_markup=build_recommend_keyboard(),
    )


@router.message(F.text == BACK_TO_MENU_BUTTON_TEXT)
async def back_to_main_menu(message: Message) -> None:
    await message.answer(
        "Главное меню.",
        reply_markup=build_main_menu_keyboard(),
    )


@router.message(F.text == MY_LINK_BUTTON_TEXT)
async def handle_share_link(message: Message) -> None:
    participant_data = await sync_to_async(get_participant_referral_data, thread_sensitive=True)(
        telegram_id=str(message.from_user.id)
    )

    if not participant_data:
        await message.answer(
            "Сначала нужно зарегистрироваться, чтобы получить персональную ссылку.",
            reply_markup=build_start_keyboard(),
        )
        return

    full_name, referral_code = participant_data
    referral_url = await build_referral_url(message, referral_code)
    await message.answer(
        build_share_link_text(full_name=full_name, referral_url=referral_url),
        reply_markup=build_recommend_keyboard(),
    )


@router.message(F.text == READY_TEXT_BUTTON_TEXT)
async def handle_invite_client(message: Message) -> None:
    participant_data = await sync_to_async(get_participant_referral_data, thread_sensitive=True)(
        telegram_id=str(message.from_user.id)
    )

    if not participant_data:
        await message.answer(
            "Сначала нужно зарегистрироваться, чтобы приглашать клиентов.",
            reply_markup=build_start_keyboard(),
        )
        return

    _, referral_code = participant_data
    referral_url = await build_referral_url(message, referral_code)
    await message.answer(
        build_invite_client_text(referral_url=referral_url),
        reply_markup=build_recommend_keyboard(),
    )


@router.message(F.text == MY_BALANCE_BUTTON_TEXT)
async def handle_my_balance(message: Message) -> None:
    dashboard_data = await sync_to_async(get_participant_dashboard_data, thread_sensitive=True)(
        telegram_id=str(message.from_user.id)
    )

    if not dashboard_data:
        await message.answer(
            "Сначала нужно зарегистрироваться, чтобы смотреть баланс.",
            reply_markup=build_start_keyboard(),
        )
        return

    balance = f"{dashboard_data['balance']:.2f}"
    await message.answer(
        build_balance_text(balance=balance),
        reply_markup=build_cabinet_keyboard(),
    )


@router.message(F.text == MY_HISTORY_BUTTON_TEXT)
async def handle_bonus_history(message: Message) -> None:
    history_data = await sync_to_async(get_participant_bonus_history_data, thread_sensitive=True)(
        telegram_id=str(message.from_user.id)
    )

    if not history_data:
        await message.answer(
            "Сначала нужно зарегистрироваться, чтобы смотреть историю бонусов.",
            reply_markup=build_start_keyboard(),
        )
        return

    history_lines = []

    for amount, reason, created_at in history_data["accruals"]:
        title = reason or "начисление бонусов"
        history_lines.append(
            f"— Начисление: +{amount:.2f} — {title} — {created_at:%d.%m.%Y}"
        )

    for amount, comment, created_at in history_data["spendings"]:
        title = comment or "списание бонусов"
        history_lines.append(
            f"— Списание: -{amount:.2f} — {title} — {created_at:%d.%m.%Y}"
        )

    if not history_lines:
        await message.answer(
            build_empty_bonus_history_text(),
            reply_markup=build_cabinet_keyboard(),
        )
        return

    await message.answer(
        build_bonus_history_text(history_lines=history_lines),
        reply_markup=build_cabinet_keyboard(),
    )


@router.message(F.text == MY_RECOMMENDATIONS_BUTTON_TEXT)
async def handle_my_recommendations(message: Message) -> None:
    dashboard_data = await sync_to_async(get_participant_dashboard_data, thread_sensitive=True)(
        telegram_id=str(message.from_user.id)
    )

    if not dashboard_data:
        await message.answer(
            "Сначала нужно зарегистрироваться, чтобы смотреть рекомендации.",
            reply_markup=build_start_keyboard(),
        )
        return

    invited_leads = dashboard_data["invited_leads"]
    if not invited_leads:
        await message.answer(
            build_empty_invited_text(),
            reply_markup=build_cabinet_keyboard(),
        )
        return

    invited_lines = [
        f"— {client_name} — {get_lead_status_label(status)} — {created_at:%d.%m.%Y}"
        for client_name, status, created_at in invited_leads
    ]
    await message.answer(
        build_invited_text(invited_lines=invited_lines),
        reply_markup=build_cabinet_keyboard(),
    )


@router.message(F.text == MY_REQUESTS_BUTTON_TEXT)
async def handle_my_requests(message: Message) -> None:
    requests_data = await sync_to_async(get_participant_requests_data, thread_sensitive=True)(
        telegram_id=str(message.from_user.id)
    )

    if not requests_data:
        await message.answer(
            "Сначала нужно зарегистрироваться, чтобы смотреть заявки.",
            reply_markup=build_start_keyboard(),
        )
        return

    request_lines = []

    for company, status, created_at in requests_data["own_leads"]:
        company_name = company or "без компании"
        request_lines.append(
            f"— Заявка для своей компании: {company_name} — {get_lead_status_label(status)} — {created_at:%d.%m.%Y}"
        )

    for comment, status, created_at in requests_data["spend_requests"]:
        title = comment or "списание бонусов"
        request_lines.append(
            f"— Запрос на подарок: {title} — {get_spend_request_status_label(status)} — {created_at:%d.%m.%Y}"
        )

    if not request_lines:
        await message.answer(
            build_empty_requests_text(),
            reply_markup=build_cabinet_keyboard(),
        )
        return

    await message.answer(
        build_my_requests_text(request_lines=request_lines),
        reply_markup=build_cabinet_keyboard(),
    )


@router.message(RegistrationStates.waiting_full_name)
async def handle_full_name(message: Message, state: FSMContext) -> None:
    full_name = (message.text or "").strip()
    if not full_name:
        await message.answer("Пожалуйста, напишите ваше имя.")
        return

    await state.update_data(full_name=full_name)
    await state.set_state(RegistrationStates.waiting_phone)
    await message.answer("Укажите ваш телефон.", reply_markup=build_phone_keyboard())


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
    await state.set_state(RegistrationStates.waiting_company)
    await message.answer(
        build_registration_success_text(full_name=full_name, referral_url=referral_url)
    )
    await message.answer(
        build_profile_company_prompt_text(),
        reply_markup=build_skip_keyboard(),
    )


@router.message(RegistrationStates.waiting_company)
async def handle_company(message: Message, state: FSMContext) -> None:
    company = (message.text or "").strip()
    if company == SKIP_BUTTON_TEXT:
        company = ""

    await state.update_data(company=company)
    await state.set_state(RegistrationStates.waiting_position)
    await message.answer(
        build_profile_position_prompt_text(),
        reply_markup=build_skip_keyboard(),
    )


@router.message(RegistrationStates.waiting_position)
async def handle_position(message: Message, state: FSMContext) -> None:
    position = (message.text or "").strip()
    if position == SKIP_BUTTON_TEXT:
        position = ""

    data = await state.get_data()
    participant = await sync_to_async(update_participant_profile, thread_sensitive=True)(
        telegram_id=str(message.from_user.id),
        company=data.get("company", ""),
        position=position,
    )
    await state.clear()
    await message.answer(
        build_profile_saved_text(company=participant.company, position=participant.position),
        reply_markup=build_member_actions_keyboard(),
    )


@router.message(RegistrationStates.waiting_consent)
async def handle_consent_required(message: Message) -> None:
    await message.answer(
        "Чтобы завершить регистрацию, нажмите кнопку согласия.",
        reply_markup=build_consent_keyboard(),
    )
