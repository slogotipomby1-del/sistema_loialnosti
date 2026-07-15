from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

SITE_URL = "https://slogotipom.by/"

REGISTER_BUTTON_TEXT = "✨ Зарегистрироваться"
MAIN_CABINET_BUTTON_TEXT = "👤 Мой кабинет"
MAIN_RECOMMEND_BUTTON_TEXT = "🤝 Рекомендовать компанию"
MAIN_SPEND_BUTTON_TEXT = "🎁 Потратить бонусы"
MAIN_HELP_BUTTON_TEXT = "📘 Помощь и правила"

MY_BALANCE_BUTTON_TEXT = "💳 Мой баланс"
MY_HISTORY_BUTTON_TEXT = "🧾 История бонусов"
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
        "Здравствуйте!\n"
        "Добро пожаловать в программу лояльности «Корпоративный стиль».\n\n"
        "Здесь вы можете рекомендовать нас знакомым и партнёрам, "
        "получать бонусы за заказы и рекомендации, а затем обменивать их на подарки.\n\n"
        "В боте вы сможете:\n"
        "— получить персональную ссылку для рекомендации;\n"
        "— оставить заявку для своей компании;\n"
        "— следить за бонусами и заявками;\n"
        "— выбрать подарок за накопленные бонусы.\n\n"
        "Чтобы начать, пройдите короткую регистрацию 👇"
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
            [KeyboardButton(text=MY_HISTORY_BUTTON_TEXT)],
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
    return (
        "Это ваш кабинет участника.\n\n"
        "Здесь вы можете:\n"
        "— посмотреть баланс бонусов;\n"
        "— проверить историю начислений и списаний;\n"
        "— увидеть свои рекомендации;\n"
        "— отследить заявки своей компании."
    )


def build_recommend_intro_text() -> str:
    return (
        "Здесь собраны инструменты для рекомендации.\n\n"
        "Вы можете:\n"
        "— взять персональную ссылку;\n"
        "— скопировать готовый текст для отправки;\n"
        "— переслать его знакомому, партнёру или клиенту."
    )


def build_spend_intro_text() -> str:
    return (
        "Здесь вы можете потратить накопленные бонусы.\n\n"
        "В этом разделе доступны:\n"
        "— подарки за бонусы;\n"
        "— правила списания;\n"
        "— идеи продукции и подарков."
    )


def build_help_intro_text() -> str:
    return (
        "Здесь собрана вся важная информация по программе.\n\n"
        "Вы можете:\n"
        "— быстро посмотреть правила;\n"
        "— уточнить спорный вопрос;\n"
        "— написать администратору."
    )


def build_registration_success_text(*, full_name: str, referral_url: str) -> str:
    return (
        f"Готово, {full_name}!\n"
        "Вы зарегистрированы в программе «Мерч-бонусы».\n\n"
        "Ваша персональная ссылка уже создана:\n"
        f"{referral_url}\n\n"
        "Делитесь ею с компаниями, которым могут быть нужны корпоративные подарки, мерч, "
        "наборы или нанесение логотипа.\n\n"
        "Теперь вам доступны:\n"
        "— ваша ссылка для рекомендации;\n"
        "— баланс и история бонусов;\n"
        "— заявки вашей компании;\n"
        "— подарки за бонусы."
    )


def build_consent_prompt_text() -> str:
    return (
        "Остался один короткий шаг.\n\n"
        "Нажимая кнопку согласия, вы подтверждаете согласие на обработку персональных данных "
        "для участия в программе лояльности и обработки ваших заявок.\n\n"
        "Без этого мы не сможем завершить регистрацию."
    )


def build_profile_company_prompt_text() -> str:
    return (
        "Давайте сразу дополним профиль.\n\n"
        "Напишите название вашей компании — это поможет точнее учитывать рекомендации "
        "и не создавать дубли.\n\n"
        "Если пока не хотите заполнять это поле, нажмите «Пропустить»."
    )


def build_profile_position_prompt_text() -> str:
    return (
        "Теперь укажите вашу должность, если хотите.\n"
        "Например: HR, маркетолог, руководитель, закупки.\n\n"
        "Это поле тоже можно пропустить."
    )


def build_profile_saved_text(*, company: str, position: str) -> str:
    company_text = company or "не указана"
    position_text = position or "не указана"
    return (
        "Профиль сохранён.\n"
        f"Компания: {company_text}\n"
        f"Должность: {position_text}\n\n"
        "Если в одной компании будет несколько участников, основного контакта "
        "администратор назначит вручную."
    )


def build_member_start_text(*, full_name: str) -> str:
    return (
        f"{full_name}, рады снова видеть вас в программе «Мерч-бонусы».\n\n"
        "С возвращением! Выберите, что хотите сделать сейчас:\n"
        "— посмотреть свою ссылку;\n"
        "— проверить бонусы;\n"
        "— отследить заявки;\n"
        "— выбрать подарок."
    )


def build_share_link_text(*, full_name: str, referral_url: str) -> str:
    return (
        f"{full_name}, вот ваша персональная ссылка:\n"
        f"{referral_url}\n\n"
        "Отправьте её знакомому, партнёру или клиенту.\n"
        "Если человек перейдёт по этой ссылке и оставит заявку, рекомендация закрепится за вами.\n\n"
        "За подтверждённые заказы по вашим рекомендациям начисляются мерч-бонусы по правилам программы."
    )


def build_invite_client_text(*, referral_url: str) -> str:
    return (
        "Готовый текст для отправки:\n\n"
        "Добрый день!\n"
        "Хочу порекомендовать компанию «Корпоративный стиль».\n"
        "Они помогают бизнесу с корпоративными подарками, мерчем и брендированной продукцией.\n"
        "Можно обратиться, если нужны подарки сотрудникам, клиентам и партнёрам, welcome pack, "
        "мерч для мероприятий или сезонные корпоративные заказы.\n"
        "Заявку удобно оставить здесь:\n"
        f"{referral_url}"
    )


def build_spend_bonuses_text() -> str:
    return (
        "Мерч-бонусы можно использовать внутри «Корпоративного стиля».\n\n"
        "Их можно потратить:\n"
        "— на подарок;\n"
        "— на доставку;\n"
        "— на нанесение;\n"
        "— как часть оплаты следующего заказа.\n\n"
        "Важно знать ограничения:\n"
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
        "8. Если в одной компании несколько участников, бонус за покупку компании начисляется основному контакту, которого администратор назначает вручную.\n\n"
        "Если останутся вопросы по начислению или списанию, напишите администратору через бот."
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
        "Ниже — подарки, которые можно запросить за мерч-бонусы.\n\n"
        "Выберите подходящий вариант — и бот сразу отправит заявку администратору.\n"
        "После подтверждения с вами свяжутся по деталям.\n\n"
        "Если какой-то позиции пока нет, мы добавим её позже."
    )


def build_gift_card_text(*, index: int, title: str, description: str, amount: int, is_available: bool) -> str:
    price_line = f"Стоимость: {amount} бонусов" if is_available else "Статус: скоро появится"
    action_line = "Нажмите кнопку ниже, чтобы отправить заявку." if is_available else "Эту карточку мы заполним одной из следующих позиций."
    return (
        f"🎁 Подарок {index} из 5\n"
        f"{title}\n\n"
        f"{description}\n\n"
        f"{price_line}\n"
        f"{action_line}"
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
        "Администратор проверит заявку и свяжется с вами по подтверждению.\n\n"
        "Статус заявки позже можно посмотреть в разделе «Мои заявки»."
    )


def build_support_prompt_text() -> str:
    return (
        "Напишите ваш вопрос администратору программы.\n\n"
        "Сюда можно написать по вопросам:\n"
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


def build_empty_bonus_history_text() -> str:
    return (
        "Пока в истории бонусов нет операций.\n"
        "Когда будут подтверждённые начисления или списания, они появятся здесь."
    )


def build_bonus_history_text(*, history_lines: list[str]) -> str:
    history_block = "\n".join(history_lines)
    return (
        "История бонусов:\n"
        f"{history_block}\n\n"
        "Здесь показываются только подтверждённые операции:\n"
        "— начисления бонусов;\n"
        "— подтверждённые списания."
    )


def build_empty_invited_text() -> str:
    return (
        "Пока у вас нет рекомендаций.\n"
        "Отправьте вашу персональную ссылку тем, кому могут быть нужны корпоративные подарки, "
        "мерч или нанесение логотипа.\n\n"
        "Как только по вашей ссылке появится новая заявка, она отобразится здесь."
    )


def build_invited_text(*, invited_lines: list[str]) -> str:
    invited_block = "\n".join(invited_lines)
    return (
        "Ваши рекомендации:\n"
        f"{invited_block}\n\n"
        "Как читать статусы:\n"
        "— «Новая» — заявка только что зафиксирована;\n"
        "— «В работе» — клиент уже в обработке;\n"
        "— «Ожидает подтверждения» — заказ состоялся, ждём ручного подтверждения бонуса;\n"
        "— «Бонус начислен» — бонус уже добавлен в баланс;\n"
        "— «Отклонена» — заявка не подошла под правила программы."
    )


def build_empty_requests_text() -> str:
    return (
        "Пока у вас нет собственных заявок.\n\n"
        "Когда вы отправите заявку для своей компании или запросите подарок за бонусы, она появится здесь."
    )


def build_my_requests_text(*, request_lines: list[str]) -> str:
    request_block = "\n".join(request_lines)
    return (
        "Ваши заявки:\n"
        f"{request_block}\n\n"
        "Статусы:\n"
        "— для заявок: «Новая», «В работе», «Ожидает подтверждения», «Бонус начислен», «Отклонена»;\n"
        "— для подарков и списаний: «На рассмотрении», «Подтверждена», «Отклонена»."
    )
