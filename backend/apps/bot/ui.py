from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

SITE_URL = "https://slogotipom.by/"

REGISTER_BUTTON_TEXT = "✨ Зарегистрироваться"
MAIN_CABINET_BUTTON_TEXT = "👤 Мой кабинет"
MAIN_RECOMMEND_BUTTON_TEXT = "🤝 Рекомендовать компанию"
MAIN_SPEND_BUTTON_TEXT = "🎁 Потратить бонусы"
MAIN_HELP_BUTTON_TEXT = "📘 Помощь и правила"

MY_BALANCE_BUTTON_TEXT = "💳 Мой баланс"
MY_RECOMMENDATIONS_BUTTON_TEXT = "📈 Мои рекомендации"
MY_REQUESTS_BUTTON_TEXT = "📄 Мои заявки"
OWN_COMPANY_ORDER_BUTTON_TEXT = "🏢 Заказать для своей компании"

MY_LINK_BUTTON_TEXT = "🔗 Моя ссылка"
READY_TEXT_BUTTON_TEXT = "✉️ Готовый текст для отправки"

GIFTS_BUTTON_TEXT = "🎁 Подарки за бонусы"
HOW_SPEND_BUTTON_TEXT = "💡 Как потратить бонусы"
CATALOG_BUTTON_TEXT = "🛍️ Каталог / идеи подарков"

RULES_BUTTON_TEXT = "📋 Правила программы"
SUPPORT_BUTTON_TEXT = "💬 Написать администратору"

BACK_TO_MENU_BUTTON_TEXT = "⬅️ Назад в меню"
SEND_PHONE_BUTTON_TEXT = "📱 Отправить телефон"
CONSENT_BUTTON_TEXT = "✅ Согласен(на)"
SKIP_BUTTON_TEXT = "⏭️ Пропустить"


def build_start_text() -> str:
    return (
        "Добро пожаловать в программу «Мерч-бонусы».\n\n"
        "Здесь вы можете получать бонусы за свои заказы и рекомендации для компании "
        "«Корпоративный стиль».\n"
        "Бонусы можно использовать на подарки, доставку, нанесение или часть следующего заказа.\n\n"
        "Чтобы начать, нужно пройти короткую регистрацию."
    )


def build_start_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=REGISTER_BUTTON_TEXT)]],
        resize_keyboard=True,
    )


def build_main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MAIN_CABINET_BUTTON_TEXT)],
            [KeyboardButton(text=MAIN_RECOMMEND_BUTTON_TEXT)],
            [KeyboardButton(text=MAIN_SPEND_BUTTON_TEXT)],
            [KeyboardButton(text=MAIN_HELP_BUTTON_TEXT)],
        ],
        resize_keyboard=True,
    )


def build_member_actions_keyboard() -> ReplyKeyboardMarkup:
    return build_main_menu_keyboard()


def build_cabinet_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MY_BALANCE_BUTTON_TEXT)],
            [KeyboardButton(text=MY_RECOMMENDATIONS_BUTTON_TEXT)],
            [KeyboardButton(text=MY_REQUESTS_BUTTON_TEXT)],
            [KeyboardButton(text=OWN_COMPANY_ORDER_BUTTON_TEXT)],
            [KeyboardButton(text=BACK_TO_MENU_BUTTON_TEXT)],
        ],
        resize_keyboard=True,
    )


def build_recommend_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MY_LINK_BUTTON_TEXT)],
            [KeyboardButton(text=READY_TEXT_BUTTON_TEXT)],
            [KeyboardButton(text=BACK_TO_MENU_BUTTON_TEXT)],
        ],
        resize_keyboard=True,
    )


def build_spend_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=GIFTS_BUTTON_TEXT)],
            [KeyboardButton(text=HOW_SPEND_BUTTON_TEXT)],
            [KeyboardButton(text=CATALOG_BUTTON_TEXT)],
            [KeyboardButton(text=BACK_TO_MENU_BUTTON_TEXT)],
        ],
        resize_keyboard=True,
    )


def build_help_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=RULES_BUTTON_TEXT)],
            [KeyboardButton(text=SUPPORT_BUTTON_TEXT)],
            [KeyboardButton(text=BACK_TO_MENU_BUTTON_TEXT)],
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


def build_skip_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=SKIP_BUTTON_TEXT)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def build_cabinet_intro_text() -> str:
    return "Раздел «Мой кабинет». Здесь ваш баланс, рекомендации и собственные заявки."


def build_recommend_intro_text() -> str:
    return "Раздел «Рекомендовать компанию». Здесь ваша ссылка и готовый текст для отправки клиенту."


def build_spend_intro_text() -> str:
    return "Раздел «Потратить бонусы». Здесь подарки, правила списания и идеи продукции."


def build_help_intro_text() -> str:
    return "Раздел «Помощь и правила». Здесь правила программы и связь с администратором."


def build_registration_success_text(*, full_name: str, referral_url: str) -> str:
    return (
        f"Готово! {full_name}, вы зарегистрированы в программе «Мерч-бонусы».\n\n"
        "Ваша персональная ссылка уже создана:\n"
        f"{referral_url}\n\n"
        "Делитесь ею с компаниями, которым могут быть нужны корпоративные подарки, мерч, "
        "наборы или нанесение логотипа."
    )


def build_profile_company_prompt_text() -> str:
    return (
        "Чтобы точнее учитывать рекомендации и избегать дублей, можно сразу заполнить профиль.\n\n"
        "Укажите вашу компанию, если хотите. Это поле можно пропустить."
    )


def build_profile_position_prompt_text() -> str:
    return "Укажите вашу должность, если хотите. Например: HR, маркетолог, руководитель, закупки."


def build_profile_saved_text(*, company: str, position: str) -> str:
    company_text = company or "не указана"
    position_text = position or "не указана"
    return (
        "Профиль участника сохранён.\n"
        f"Компания: {company_text}\n"
        f"Должность: {position_text}\n\n"
        "Если в одной компании будет несколько участников, основного контакта администратор назначит вручную."
    )


def build_member_start_text(*, full_name: str) -> str:
    return (
        f"{full_name}, рады снова видеть вас в программе «Мерч-бонусы».\n\n"
        "Выберите нужный раздел в меню."
    )


def build_share_link_text(*, full_name: str, referral_url: str) -> str:
    return (
        f"{full_name}, ваша персональная ссылка:\n"
        f"{referral_url}\n\n"
        "Делитесь ею с новыми компаниями, чтобы фиксировать рекомендацию именно за вами и получать "
        "мерч-бонусы по правилам программы."
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
        f"{referral_url}"
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
        "8. Если в одной компании несколько участников, бонус за покупку компании начисляется основному контакту, которого администратор назначает вручную."
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


def build_gifts_intro_text() -> str:
    return (
        "Ниже — 5 карточек подарков за мерч-бонусы.\n\n"
        "Пока показываем каталог без изображений. Позже сюда добавим фото для каждой позиции.\n"
        "Если нажмёте на кнопку под карточкой, заявка сразу уйдёт администратору."
    )


def build_gift_card_text(*, index: int, title: str, description: str, amount: int, is_available: bool) -> str:
    price_line = f"Стоимость: {amount} бонусов" if is_available else "Скоро появится"
    return (
        f"Подарок {index}/5\n"
        f"{title}\n\n"
        f"{description}\n\n"
        f"{price_line}"
    )


def build_gift_card_keyboard(*, slug: str, is_available: bool) -> InlineKeyboardMarkup:
    if is_available:
        button = InlineKeyboardButton(text="Хочу этот подарок", callback_data=f"gift:choose:{slug}")
    else:
        button = InlineKeyboardButton(text="Скоро добавим", callback_data=f"gift:soon:{slug}")
    return InlineKeyboardMarkup(inline_keyboard=[[button]])


def build_gift_request_sent_text(*, gift_title: str, gift_amount: int) -> str:
    return (
        f"Заявка на подарок «{gift_title}» отправлена.\n\n"
        f"Зарезервировано: {gift_amount} бонусов.\n"
        "Администратор посмотрит заявку и свяжется с вами по подтверждению."
    )


def build_support_prompt_text() -> str:
    return (
        "Напишите ваш вопрос администратору программы.\n\n"
        "Можно обратиться по вопросам:\n"
        "— начисления бонусов;\n"
        "— списания бонусов;\n"
        "— приглашённых клиентов;\n"
        "— заявок;\n"
        "— правил программы."
    )


def build_support_sent_text() -> str:
    return "Сообщение отправлено администратору. Мы ответим вам в ближайшее рабочее время."


def build_balance_text(*, balance: str) -> str:
    return (
        "Ваш баланс:\n"
        f"{balance} мерч-бонусов\n\n"
        "1 мерч-бонус = 1 BYN внутри программы.\n"
        "Бонусы можно использовать на подарок, доставку, нанесение или часть следующего заказа."
    )


def build_empty_invited_text() -> str:
    return (
        "Пока у вас нет рекомендаций.\n"
        "Отправьте вашу персональную ссылку тем, кому могут быть нужны корпоративные подарки, "
        "мерч или нанесение логотипа."
    )


def build_invited_text(*, invited_lines: list[str]) -> str:
    invited_block = "\n".join(invited_lines)
    return (
        "Ваши рекомендации:\n"
        f"{invited_block}\n\n"
        "Статус «ожидает подтверждения» означает, что заявка уже зафиксирована, "
        "но бонусы ещё не подтверждены администратором."
    )


def build_empty_requests_text() -> str:
    return "Пока у вас нет собственных заявок."


def build_my_requests_text(*, request_lines: list[str]) -> str:
    request_block = "\n".join(request_lines)
    return f"Ваши заявки:\n{request_block}"
