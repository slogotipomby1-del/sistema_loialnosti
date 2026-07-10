from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


SITE_URL = "https://slogotipom.by/"

REGISTER_BUTTON_TEXT = "Зарегистрироваться"
SHARE_LINK_BUTTON_TEXT = "Получить мою ссылку"
LEAVE_LEAD_BUTTON_TEXT = "Оставить заявку"
SPEND_BONUSES_BUTTON_TEXT = "Использовать бонусы"
SEND_PHONE_BUTTON_TEXT = "Отправить телефон"
CONSENT_BUTTON_TEXT = "Согласен(на)"


def build_start_text() -> str:
    return (
        "Добро пожаловать в программу «Мерч-бонусы» 🎁\n\n"
        "«Корпоративный стиль» — B2B-компания по мерчу, корпоративным подаркам и брендированной продукции.\n"
        "Мы помогаем компаниям подобрать решения под задачу, бюджет, тираж и сроки: "
        "подарки сотрудникам, клиентам и партнёрам, welcome pack, мерч для мероприятий, "
        "нанесение логотипа, упаковку и доставку.\n\n"
        f"Сайт и каталог: {SITE_URL}\n\n"
        "Здесь вы можете зарегистрироваться, получить персональную ссылку и рекомендовать нас "
        "знакомым компаниям, партнёрам и коллегам."
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
        f"{full_name}, вы зарегистрированы в программе «Мерч-бонусы».\n\n"
        "Ваша персональная реферальная ссылка:\n"
        f"{referral_url}\n\n"
        "Её можно отправлять знакомым маркетологам, HR, руководителям, закупщикам, партнёрам "
        "и компаниям, которым могут быть нужны корпоративные подарки, мерч или нанесение логотипа.\n\n"
        f"Сайт и каталог: {SITE_URL}"
    )


def build_share_link_text(*, full_name: str, referral_url: str) -> str:
    return (
        f"{full_name}, вот ваша персональная реферальная ссылка:\n"
        f"{referral_url}\n\n"
        "Кому её можно отправить:\n"
        "— знакомому из бизнеса;\n"
        "— партнёру;\n"
        "— коллеге;\n"
        "— компании, которой могут быть нужны корпоративные подарки, мерч или брендированная продукция.\n\n"
        "Что делает «Корпоративный стиль»:\n"
        "— подбирает корпоративные подарки, welcome pack, мерч и наборы;\n"
        "— помогает с нанесением логотипа, упаковкой и доставкой;\n"
        "— предлагает решения под задачу, бюджет, тираж и сроки.\n\n"
        "Какие бизнес-задачи это решает:\n"
        "— подарки сотрудникам, клиентам и партнёрам;\n"
        "— welcome pack и onboarding;\n"
        "— мероприятия, выставки и конференции;\n"
        "— сезонные и новогодние корпоративные заказы.\n\n"
        f"Сайт и каталог: {SITE_URL}\n\n"
        "Готовый текст для отправки:\n"
        "Добрый день! Хочу порекомендовать «Корпоративный стиль».\n"
        "Это B2B-компания по корпоративным подаркам, мерчу и брендированной продукции.\n"
        "Они помогают подобрать решения под задачу, бюджет, тираж и сроки: "
        "подарки сотрудникам, клиентам и партнёрам, welcome pack, мерч для мероприятий, "
        "нанесение логотипа, упаковку и доставку.\n"
        f"Сайт и каталог: {SITE_URL}\n"
        f"Если удобнее сразу оставить заявку в Telegram, вот ссылка: {referral_url}"
    )
