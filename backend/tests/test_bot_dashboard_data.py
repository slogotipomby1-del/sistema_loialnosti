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
        budget="до 5000 BYN",
        deadline="2 недели",
        client_email="olga@example.com",
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


@pytest.mark.django_db
def test_dashboard_balance_uses_only_confirmed_operations_and_can_be_negative():
    from decimal import Decimal

    from apps.bot.services import calculate_participant_balance, get_participant_dashboard_data, register_participant
    from apps.bonuses.models import BonusLedgerEntry, BonusSpendRequest
    from apps.common.choices import BONUS_ENTRY_TYPE_REVERSAL, SPEND_REQUEST_STATUS_APPROVED, SPEND_REQUEST_STATUS_PENDING

    participant = register_participant(
        telegram_id="2003",
        full_name="Мария",
        phone="+375294444444",
        consent_accepted=True,
    )

    BonusLedgerEntry.objects.create(
        participant=participant,
        amount=Decimal("100.00"),
        reason="Начисление за заказ",
    )
    BonusLedgerEntry.objects.create(
        participant=participant,
        amount=Decimal("-80.00"),
        reason="Частичное аннулирование",
        entry_type=BONUS_ENTRY_TYPE_REVERSAL,
    )
    BonusSpendRequest.objects.create(
        participant=participant,
        amount=Decimal("50.00"),
        comment="Подарок",
        status=SPEND_REQUEST_STATUS_APPROVED,
    )
    BonusSpendRequest.objects.create(
        participant=participant,
        amount=Decimal("40.00"),
        comment="Ожидает решения",
        status=SPEND_REQUEST_STATUS_PENDING,
    )

    dashboard = get_participant_dashboard_data(telegram_id="2003")

    assert dashboard is not None
    assert dashboard["balance"] == Decimal("-30.00")
    assert calculate_participant_balance(participant=participant) == Decimal("-30.00")
