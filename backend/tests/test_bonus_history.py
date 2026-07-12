from decimal import Decimal

import pytest


@pytest.mark.django_db
def test_get_participant_bonus_history_data_returns_accruals_and_approved_spendings():
    from apps.bot.services import get_participant_bonus_history_data
    from apps.bonuses.models import BonusLedgerEntry, BonusSpendRequest
    from apps.common.choices import SPEND_REQUEST_STATUS_APPROVED, SPEND_REQUEST_STATUS_PENDING
    from apps.users.models import Participant

    participant = Participant.objects.create(
        telegram_id="777",
        full_name="Olga Saniuk",
        phone="+375291234567",
        consent_accepted=True,
    )

    BonusLedgerEntry.objects.create(
        participant=participant,
        amount=Decimal("60.00"),
        reason="За рекомендацию",
    )
    BonusSpendRequest.objects.create(
        participant=participant,
        amount=Decimal("40.00"),
        comment="Термокружка",
        status=SPEND_REQUEST_STATUS_APPROVED,
    )
    BonusSpendRequest.objects.create(
        participant=participant,
        amount=Decimal("30.00"),
        comment="Доставка",
        status=SPEND_REQUEST_STATUS_PENDING,
    )

    data = get_participant_bonus_history_data(telegram_id="777")

    assert data is not None
    assert len(data["accruals"]) == 1
    assert len(data["spendings"]) == 1
    assert data["accruals"][0][1] == "За рекомендацию"
    assert data["spendings"][0][1] == "Термокружка"
