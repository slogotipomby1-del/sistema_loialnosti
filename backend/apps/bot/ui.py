from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


REGISTER_BUTTON_TEXT = "Зарегистрироваться"
SHARE_LINK_BUTTON_TEXT = "Получить мою ссылку"
LEAVE_LEAD_BUTTON_TEXT = "Оставить заявку"
SPEND_BONUSES_BUTTON_TEXT = "Использовать бонусы"
SEND_PHONE_BUTTON_TEXT = "Отправить телефон"
CONSENT_BUTTON_TEXT = "Согласен(на)"


def build_start_text() -> str:
    return (
        "Здравствуйте!\n"
        "Добро пожаловать в систему лояльности «Корпоративный стиль».\n\n"
        "Здесь вы сможете зарегистрироваться, получить свою реферальную ссылку "
        "и пользоваться возможностями программы."
    )


def build_start_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=REGISTER_BUTTON_TEXT)]],
        resize_keyboard=True,
    )


def build_member_actions_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=SHARE_LINK_BUTTON_TEXT)],
            [KeyboardButton(text=LEAVE_LEAD_BUTTON_TEXT)],
            [KeyboardButton(text=SPEND_BONUSES_BUTTON_TEXT)],
        ],
        resize_keyboard=True,
    )


def build_phone_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=SEND_PHONE_BUTTON_TEXT, request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def build_consent_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=CONSENT_BUTTON_TEXT)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def build_registration_success_text(*, full_name: str, referral_url: str) -> str:
    return (
        f"{full_name}, вы зарегистрированы в системе лояльности «Корпоративный стиль».\n\n"
        "Ваша персональная реферальная ссылка:\n"
        f"{referral_url}\n\n"
        "Теперь вы можете делиться ссылкой с друзьями и пользоваться возможностями программы."
    )


def build_share_link_text(*, full_name: str, referral_url: str) -> str:
    return (
        f"{full_name}, вот ваша персональная реферальная ссылка:\n"
        f"{referral_url}\n\n"
        "Отправьте ее другу или клиенту. Когда он зайдет по этой ссылке и оставит заявку, "
        "мы свяжем эту заявку с вами.\n\n"
        "Готовый текст для отправки:\n"
        "Здравствуйте! Если вам интересна продукция «Корпоративный стиль», "
        f"вот ссылка для быстрой заявки: {referral_url}"
    )
