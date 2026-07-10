from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


SITE_URL = "https://slogotipom.by/"

REGISTER_BUTTON_TEXT = "Зарегистрироваться"
MY_LINK_BUTTON_TEXT = "Моя ссылка"
INVITE_CLIENT_BUTTON_TEXT = "Пригласить клиента"
CONSULTATION_BUTTON_TEXT = "Получить консультацию"
SPEND_BONUSES_BUTTON_TEXT = "Как потратить бонусы"
RULES_BUTTON_TEXT = "Правила программы"
CATALOG_BUTTON_TEXT = "Каталог / идеи подарков"
SEND_PHONE_BUTTON_TEXT = "Отправить телефон"
CONSENT_BUTTON_TEXT = "Согласен(на)"


def build_start_text() -> str:
    return (
        "Добро пожаловать в программу «Мерч-бонусы» 🎁\n\n"
        "Здесь вы можете получать бонусы за заказы и рекомендации «Корпоративного стиля».\n"
        "Бонусы можно использовать на подарки, доставку, нанесение или часть следующего заказа.\n\n"
        "Чтобы начать, нужно пройти короткую регистрацию."
    )


def build_start_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=REGISTER_BUTTON_TEXT)]],
        resize_keyboard=True,
    )


def build_member_actions_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MY_LINK_BUTTON_TEXT)],
            [KeyboardButton(text=INVITE_CLIENT_BUTTON_TEXT)],
            [KeyboardButton(text=CONSULTATION_BUTTON_TEXT)],
            [KeyboardButton(text=SPEND_BONUSES_BUTTON_TEXT)],
            [KeyboardButton(text=RULES_BUTTON_TEXT)],
            [KeyboardButton(text=CATALOG_BUTTON_TEXT)],
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
        f"Готово! {full_name}, вы зарегистрированы в программе «Мерч-бонусы» 🎁\n\n"
        "Ваша персональная ссылка уже создана:\n"
        f"{referral_url}\n\n"
        "Делитесь ею с компаниями, которым могут быть нужны корпоративные подарки, мерч, "
        "наборы или нанесение логотипа."
    )


def build_member_start_text(*, full_name: str) -> str:
    return (
        f"{full_name}, рады снова видеть вас в программе «Мерч-бонусы».\n\n"
        "Здесь вы можете посмотреть свою ссылку, пригласить клиента, изучить правила программы "
        "и оставить заявку для себя."
    )


def build_share_link_text(*, full_name: str, referral_url: str) -> str:
    return (
        f"{full_name}, ваша персональная ссылка:\n"
        f"{referral_url}\n\n"
        "Зачем ей делиться:\n"
        "— чтобы приглашать новые компании в «Корпоративный стиль»;\n"
        "— чтобы фиксировать рекомендацию именно за вами;\n"
        "— чтобы получать мерч-бонусы за успешные рекомендации.\n\n"
        "Что вы получите:\n"
        "Если человек перейдёт по вашей ссылке, оставит заявку и сделает заказ, "
        "вам начислятся мерч-бонусы после оплаты, отгрузки и подтверждения заказа администратором.\n\n"
        "Кому можно отправить ссылку:\n"
        "— знакомым маркетологам;\n"
        "— HR;\n"
        "— руководителям;\n"
        "— закупщикам;\n"
        "— партнёрам;\n"
        "— компаниям, которым могут быть нужны корпоративные подарки, мерч или нанесение логотипа."
    )


def build_invite_client_text(*, referral_url: str) -> str:
    return (
        "Готовый вариант для пересылки:\n\n"
        "Добрый день!\n"
        "Хочу порекомендовать компанию «Корпоративный стиль». "
        "Они занимаются корпоративными подарками, мерчем и нанесением логотипа для B2B-клиентов.\n"
        "Можно обратиться, если нужны подарки сотрудникам, клиентам, партнёрам, welcome pack, "
        "мерч для мероприятий или сезонные корпоративные заказы.\n"
        "Заявку удобно оставить здесь:\n"
        f"{referral_url}\n\n"
        "Если по вашей рекомендации клиент сделает заказ, вам могут быть начислены мерч-бонусы "
        "по правилам программы."
    )


def build_spend_bonuses_text() -> str:
    return (
        "Мерч-бонусы можно использовать внутри «Корпоративного стиля»:\n"
        "— на подарок;\n"
        "— на доставку;\n"
        "— на нанесение;\n"
        "— как часть оплаты следующего заказа.\n\n"
        "Ограничения:\n"
        "— до 20% суммы заказа;\n"
        "— не более 200 BYN на один заказ;\n"
        "— нельзя суммировать со скидками и спецусловиями;\n"
        "— нельзя использовать в тендерных и низкомаржинальных заказах;\n"
        "— нельзя вывести деньгами или передать другому человеку."
    )


def build_rules_text() -> str:
    return (
        "Короткие правила программы «Мерч-бонусы»:\n\n"
        "1. Мерч-бонусы — это внутренняя бонусная единица программы.\n"
        "2. Их нельзя вывести деньгами, перевести на карту или передать другому человеку.\n"
        "3. Бонусы могут начисляться за свои заказы и за успешные рекомендации новых клиентов.\n"
        "4. Бонусы начисляются только после оплаты, отгрузки и подтверждения заказа администратором.\n"
        "5. Минимальная сумма заказа для начисления — от 2000 BYN.\n"
        "6. Бонусы не начисляются на тендерные, скидочные, спецусловные и низкомаржинальные заказы.\n"
        "7. Рекомендация засчитывается по первой зафиксированной ссылке.\n"
        "8. Бонусы можно использовать на подарок, доставку, нанесение или часть следующего заказа."
    )


def build_catalog_text() -> str:
    return (
        "Что можно заказать в «Корпоративном стиле»:\n"
        "— подарки сотрудникам;\n"
        "— подарки клиентам и партнёрам;\n"
        "— welcome pack;\n"
        "— мерч для мероприятий;\n"
        "— новогодние корпоративные подарки;\n"
        "— VIP-подарки;\n"
        "— брендированную продукцию с логотипом.\n\n"
        "На сайте можно посмотреть каталог и идеи подарков:\n"
        f"{SITE_URL}\n\n"
        "Если захотите подборку под задачу, бюджет, тираж и сроки — вернитесь в бот и оставьте заявку."
    )
