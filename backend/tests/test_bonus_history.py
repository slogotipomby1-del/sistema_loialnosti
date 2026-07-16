from decimal import Decimal

import pytest


@pytest.mark.django_db
def test_get_participant_bonus_history_data_returns_all_confirmed_entry_types():
    from apps.bot.services import get_participant_bonus_history_data
    from apps.bonuses.models import BonusLedgerEntry, BonusSpendRequest
    from apps.common.choices import (
        BONUS_ENTRY_TYPE_EXPIRATION,
        BONUS_ENTRY_TYPE_REVERSAL,
        SPEND_REQUEST_STATUS_APPROVED,
        SPEND_REQUEST_STATUS_PENDING,
    )
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
    BonusLedgerEntry.objects.create(
        participant=participant,
        amount=Decimal("-20.00"),
        reason="Возврат по заказу",
        entry_type=BONUS_ENTRY_TYPE_REVERSAL,
    )
    BonusLedgerEntry.objects.create(
        participant=participant,
        amount=Decimal("-10.00"),
        reason="Сгорание бонусов",
        entry_type=BONUS_ENTRY_TYPE_EXPIRATION,
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
    assert len(data["entries"]) == 4
    labels = [entry["label"] for entry in data["entries"]]
    reasons = [entry["reason"] for entry in data["entries"]]
    assert "Начисление" in labels
    assert "Списание" in labels
    assert "Аннулирование" in labels
    assert "Сгорание" in labels
    assert "За рекомендацию" in reasons
    assert "Термокружка" in reasons
