from apps.bot import ui


def test_start_keyboard_has_register_button():
    keyboard = ui.build_start_keyboard()

    assert keyboard.keyboard[0][0].text == ui.REGISTER_BUTTON_TEXT


def test_member_actions_keyboard_has_expected_buttons():
    keyboard = ui.build_member_actions_keyboard()
    labels = [row[0].text for row in keyboard.keyboard]

    assert labels == [
        ui.SHARE_LINK_BUTTON_TEXT,
        ui.LEAVE_LEAD_BUTTON_TEXT,
        ui.SPEND_BONUSES_BUTTON_TEXT,
    ]


def test_registration_success_text_contains_referral_url():
    text = ui.build_registration_success_text(
        full_name="Ирина",
        referral_url="https://t.me/SvoyCorpStyleBot?start=abc123",
    )

    assert "Ирина" in text
    assert "https://t.me/SvoyCorpStyleBot?start=abc123" in text
