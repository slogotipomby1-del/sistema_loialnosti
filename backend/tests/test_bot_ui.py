from apps.bot import ui


def test_start_keyboard_has_register_button():
    keyboard = ui.build_start_keyboard()

    assert keyboard.keyboard[0][0].text == ui.REGISTER_BUTTON_TEXT


def test_member_actions_keyboard_has_expected_buttons():
    keyboard = ui.build_member_actions_keyboard()
    labels = [row[0].text for row in keyboard.keyboard]

    assert labels == [
        ui.MY_BALANCE_BUTTON_TEXT,
        ui.MY_LINK_BUTTON_TEXT,
        ui.INVITE_CLIENT_BUTTON_TEXT,
        ui.MY_INVITED_BUTTON_TEXT,
        ui.CONSULTATION_BUTTON_TEXT,
        ui.SPEND_BONUSES_BUTTON_TEXT,
        ui.RULES_BUTTON_TEXT,
        ui.CATALOG_BUTTON_TEXT,
    ]


def test_start_text_contains_program_message():
    text = ui.build_start_text()

    assert "Мерч-бонусы" in text
    assert "рекомендации" in text.lower()
    assert "регистрацию" in text.lower()


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
    assert "зачем" in text.lower()
    assert "мерч-бонусы" in text.lower()


def test_invite_client_text_contains_ready_message():
    text = ui.build_invite_client_text(
        referral_url="https://t.me/SvoyCorpStyleBot?start=abc123",
    )

    assert "https://t.me/SvoyCorpStyleBot?start=abc123" in text
    assert "корпоративный стиль" in text.lower()
    assert "мерч-бонусы" in text.lower()


def test_rules_text_contains_program_restrictions():
    text = ui.build_rules_text()

    assert "нельзя вывести деньгами" in text.lower()
    assert "2000 byn" in text.lower()


def test_catalog_text_contains_site_and_categories():
    text = ui.build_catalog_text()

    assert ui.SITE_URL in text
    assert "welcome pack" in text.lower()


def test_spend_bonuses_text_contains_limits():
    text = ui.build_spend_bonuses_text()

    assert "20%" in text
    assert "200 byn" in text.lower()


def test_balance_text_contains_amount():
    text = ui.build_balance_text(balance="125.00")

    assert "125.00" in text
    assert "1 мерч-бонус = 1 BYN" in text


def test_empty_invited_text_contains_hint():
    text = ui.build_empty_invited_text()

    assert "Пока у вас нет приглашённых" in text


def test_invited_text_contains_status_explanation():
    text = ui.build_invited_text(invited_lines=["— Компания А — Новая — 10.07.2026"])

    assert "Компания А" in text
    assert "ожидает подтверждения" in text.lower()
