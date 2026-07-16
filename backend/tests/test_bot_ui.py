from apps.bot import ui


def test_start_keyboard_has_register_button():
    keyboard = ui.build_start_keyboard()

    assert keyboard.keyboard[0][0].text == ui.REGISTER_BUTTON_TEXT


def test_main_menu_keyboard_has_expected_buttons():
    keyboard = ui.build_main_menu_keyboard()
    labels = [row[0].text for row in keyboard.keyboard]

    assert labels == [
        ui.MAIN_CABINET_BUTTON_TEXT,
        ui.MAIN_RECOMMEND_BUTTON_TEXT,
        ui.MAIN_SPEND_BUTTON_TEXT,
        ui.MAIN_HELP_BUTTON_TEXT,
    ]


def test_cabinet_keyboard_has_expected_buttons():
    keyboard = ui.build_cabinet_keyboard()
    labels = [row[0].text for row in keyboard.keyboard]

    assert labels == [
        ui.MY_BALANCE_BUTTON_TEXT,
        ui.MY_HISTORY_BUTTON_TEXT,
        ui.MY_RECOMMENDATIONS_BUTTON_TEXT,
        ui.MY_REQUESTS_BUTTON_TEXT,
        ui.OWN_COMPANY_ORDER_BUTTON_TEXT,
        ui.BACK_TO_MENU_BUTTON_TEXT,
    ]


def test_recommend_keyboard_has_expected_buttons():
    keyboard = ui.build_recommend_keyboard()
    labels = [row[0].text for row in keyboard.keyboard]

    assert labels == [
        ui.MY_LINK_BUTTON_TEXT,
        ui.READY_TEXT_BUTTON_TEXT,
        ui.BACK_TO_MENU_BUTTON_TEXT,
    ]


def test_spend_menu_keyboard_has_expected_buttons():
    keyboard = ui.build_spend_menu_keyboard()
    labels = [row[0].text for row in keyboard.keyboard]

    assert labels == [
        ui.GIFTS_BUTTON_TEXT,
        ui.HOW_SPEND_BUTTON_TEXT,
        ui.CATALOG_BUTTON_TEXT,
        ui.BACK_TO_MENU_BUTTON_TEXT,
    ]


def test_help_menu_keyboard_has_expected_buttons():
    keyboard = ui.build_help_menu_keyboard()
    labels = [row[0].text for row in keyboard.keyboard]

    assert labels == [
        ui.HOW_IT_WORKS_BUTTON_TEXT,
        ui.RULES_BUTTON_TEXT,
        ui.FAQ_BUTTON_TEXT,
        ui.SUPPORT_BUTTON_TEXT,
        ui.BACK_TO_MENU_BUTTON_TEXT,
    ]


def test_start_text_contains_program_message():
    text = ui.build_start_text()

    assert "Корпоративный стиль" in text
    assert "бонусы" in text.lower()
    assert "подар" in text.lower()
    assert "регистрац" in text.lower()


def test_consent_prompt_text_explains_next_step():
    text = ui.build_consent_prompt_text()

    assert "один короткий шаг" in text.lower()
    assert "обработку персональных данных" in text.lower()


def test_registration_success_text_contains_referral_url():
    text = ui.build_registration_success_text(
        full_name="Ирина",
        referral_url="https://t.me/SvoyCorpStyleBot?start=abc123",
    )

    assert "Ирина" in text
    assert "https://t.me/SvoyCorpStyleBot?start=abc123" in text


def test_share_link_text_explains_reward():
    text = ui.build_share_link_text(
        full_name="Ирина",
        referral_url="https://t.me/SvoyCorpStyleBot?start=abc123",
    )

    assert "https://t.me/SvoyCorpStyleBot?start=abc123" in text
    assert "мерч-бонусы" in text.lower()
    assert "знакомому" in text.lower()


def test_invite_client_text_contains_ready_message():
    text = ui.build_invite_client_text(
        referral_url="https://t.me/SvoyCorpStyleBot?start=abc123",
    )

    assert "https://t.me/SvoyCorpStyleBot?start=abc123" in text
    assert "корпоративный стиль" in text.lower()
    assert "брендированной продукцией" in text.lower()


def test_rules_text_contains_program_restrictions():
    text = ui.build_rules_text()

    assert "нельзя вывести деньгами" in text.lower()
    assert "2000 byn" in text.lower()
    assert "напишите администратору" in text.lower()


def test_help_texts_cover_how_it_works_and_faq():
    how_it_works = ui.build_how_it_works_text()
    faq = ui.build_faq_text()

    assert "получаете персональную ссылку" in how_it_works.lower()
    assert "по первой ссылке" in how_it_works.lower()
    assert "faq" in faq.lower()
    assert "отрицательным" in faq.lower()


def test_catalog_text_contains_site_and_categories():
    text = ui.build_catalog_text()

    assert ui.SITE_URL in text
    assert "welcome pack" in text.lower()


def test_spend_bonuses_text_contains_limits():
    text = ui.build_spend_bonuses_text()

    assert "20%" in text
    assert "200 byn" in text.lower()
    assert "их можно потратить" in text.lower()


def test_gifts_text_and_card_builders_contain_gift_options():
    text = ui.build_gifts_intro_text()
    card_text = ui.build_gift_card_text(
        index=1,
        title="Рюкзак",
        description="Тестовое описание",
        amount=180,
        is_available=True,
    )
    keyboard = ui.build_gift_card_keyboard(slug="backpack", is_available=True)

    assert "подарки, которые можно запросить" in text.lower()
    assert "добавим её позже" in text.lower()
    assert "Рюкзак" in card_text
    assert "180" in card_text
    assert "подарок 1 из 5" in card_text.lower()
    assert keyboard.inline_keyboard[0][0].text == "Хочу этот подарок"


def test_support_texts_are_present():
    prompt = ui.build_support_prompt_text()
    sent = ui.build_support_sent_text()

    assert "администратор" in prompt.lower()
    assert "отправлено" in sent.lower()
    assert "сюда можно написать" in prompt.lower()


def test_balance_text_contains_amount():
    text = ui.build_balance_text(balance="125.00")

    assert "125.00" in text
    assert "1 мерч-бонус = 1 BYN" in text


def test_negative_balance_text_explains_reversal_case():
    text = ui.build_balance_text(balance="-40.00")

    assert "-40.00" in text
    assert "отрицательный" in text.lower()
    assert "аннулированы" in text.lower()


def test_bonus_history_texts_are_present():
    empty_text = ui.build_empty_bonus_history_text()
    filled_text = ui.build_bonus_history_text(
        history_lines=["— Начисление: +60.00 — За рекомендацию — 10.07.2026"]
    )

    assert "истории бонусов нет операций" in empty_text.lower()
    assert "история бонусов" in filled_text.lower()
    assert "аннулирования" in filled_text.lower()
    assert "ручные корректировки" in filled_text.lower()


def test_empty_invited_text_contains_hint():
    text = ui.build_empty_invited_text()

    assert "пока у вас нет рекомендаций" in text.lower()
    assert "отобразится здесь" in text.lower()


def test_intro_texts_explain_sections():
    cabinet = ui.build_cabinet_intro_text()
    recommend = ui.build_recommend_intro_text()
    member = ui.build_member_start_text(full_name="Ирина")
    spend = ui.build_spend_intro_text()
    help_text = ui.build_help_intro_text()

    assert "это ваш кабинет участника" in cabinet.lower()
    assert "инструменты для рекомендации" in recommend.lower()
    assert "выберите, что хотите сделать сейчас" in member.lower()
    assert "потратить накопленные бонусы" in spend.lower()
    assert "вся важная информация" in help_text.lower()


def test_invited_text_contains_status_explanation():
    text = ui.build_invited_text(invited_lines=["— Компания А — Новая — 10.07.2026"])

    assert "Компания А" in text
    assert "ожидает подтверждения" in text.lower()


def test_my_requests_text_builders():
    empty_text = ui.build_empty_requests_text()
    filled_text = ui.build_my_requests_text(
        request_lines=["— Заявка для своей компании — Новая — 10.07.2026"]
    )

    assert "нет собственных заявок" in empty_text.lower()
    assert "появится здесь" in empty_text.lower()
    assert "ваши заявки" in filled_text.lower()


def test_gift_request_sent_text_mentions_requests_section():
    text = ui.build_gift_request_sent_text(gift_title="Рюкзак", gift_amount=180)

    assert "мои заявки" in text.lower()
