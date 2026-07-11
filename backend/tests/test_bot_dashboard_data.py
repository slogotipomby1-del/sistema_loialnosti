import pytest


@pytest.mark.django_db
def test_self_lead_request_is_not_shown_in_invited_list():
    from apps.bot.services import create_self_lead_request, get_participant_dashboard_data, register_participant

    register_participant(
        telegram_id="2001",
        full_name="Ольга",
        phone="+375291111111",
        consent_accepted=True,
    )

    create_self_lead_request(
        telegram_id="2001",
        product="Подарочные наборы",
        quantity="50",
        comment="Для своей компании",
    )

    dashboard = get_participant_dashboard_data(telegram_id="2001")

    assert dashboard is not None
    assert dashboard["invited_leads"] == []


@pytest.mark.django_db
def test_real_referral_lead_is_shown_in_invited_list():
    from apps.bot.services import create_referral_lead, get_participant_dashboard_data, register_participant
    from apps.referrals.models import ReferralLink

    participant = register_participant(
        telegram_id="2002",
        full_name="Ольга",
        phone="+375292222222",
        consent_accepted=True,
    )
    link = ReferralLink.objects.get(participant=participant)

    create_referral_lead(
        referral_code=link.code,
        client_name="ООО Клиент",
        client_phone="+375293333333",
        client_company="ООО Клиент",
    )

    dashboard = get_participant_dashboard_data(telegram_id="2002")

    assert dashboard is not None
    assert len(dashboard["invited_leads"]) == 1
    assert dashboard["invited_leads"][0][0] == "ООО Клиент"
