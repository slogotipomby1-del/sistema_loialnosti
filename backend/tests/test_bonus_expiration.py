from datetime import date, timedelta
from decimal import Decimal

import pytest


@pytest.mark.django_db
def test_send_upcoming_expiration_warnings_notifies_only_once(monkeypatch):
    from apps.bonuses.models import BonusLedgerEntry
    from apps.bonuses.services import send_upcoming_expiration_warnings
    from apps.users.models import Participant

    participant = Participant.objects.create(
        telegram_id="301",
        full_name="Ольга",
        phone="+375291010101",
        consent_accepted=True,
    )
    entry = BonusLedgerEntry.objects.create(
        participant=participant,
        amount=Decimal("100.00"),
        reason="Бонус за заказ",
        expires_at=date(2026, 8, 14),
    )

    sent_messages = []

    def fake_send_telegram_message(*, chat_id: str, text: str) -> None:
        sent_messages.append((chat_id, text))

    monkeypatch.setattr(
        "apps.bonuses.services.send_telegram_message",
        fake_send_telegram_message,
    )

    warnings_sent = send_upcoming_expiration_warnings(today=date(2026, 7, 15))

    entry.refresh_from_db()

    assert warnings_sent == 1
    assert len(sent_messages) == 1
    assert sent_messages[0][0] == "301"
    assert "100" in sent_messages[0][1]
    assert "14.08.2026" in sent_messages[0][1]
    assert entry.expiration_warning_sent_at is not None

    warnings_sent = send_upcoming_expiration_warnings(today=date(2026, 7, 15))

    assert warnings_sent == 0
    assert len(sent_messages) == 1


@pytest.mark.django_db
def test_expire_bonus_entries_creates_expiration_only_for_remaining_amount():
    from apps.bonuses.models import BonusLedgerEntry, BonusSpendRequest
    from apps.bonuses.services import expire_bonus_entries
    from apps.common.choices import BONUS_ENTRY_TYPE_EXPIRATION, SPEND_REQUEST_STATUS_APPROVED
    from apps.users.models import Participant

    participant = Participant.objects.create(
        telegram_id="302",
        full_name="Мария",
        phone="+375292020202",
        consent_accepted=True,
    )
    accrual = BonusLedgerEntry.objects.create(
        participant=participant,
        amount=Decimal("100.00"),
        reason="Бонус за заказ",
        expires_at=date(2026, 7, 14),
    )
    BonusSpendRequest.objects.create(
        participant=participant,
        amount=Decimal("40.00"),
        comment="Подарок",
        status=SPEND_REQUEST_STATUS_APPROVED,
    )

    expired_count = expire_bonus_entries(today=date(2026, 7, 15))

    expiration_entries = list(
        BonusLedgerEntry.objects.filter(
            participant=participant,
            entry_type=BONUS_ENTRY_TYPE_EXPIRATION,
        )
    )

    assert expired_count == 1
    assert len(expiration_entries) == 1
    assert expiration_entries[0].amount == Decimal("-60.00")
    assert str(accrual.id) in expiration_entries[0].reason

    expired_count = expire_bonus_entries(today=date(2026, 7, 15))

    assert expired_count == 0
    assert (
        BonusLedgerEntry.objects.filter(
            participant=participant,
            entry_type=BONUS_ENTRY_TYPE_EXPIRATION,
        ).count()
        == 1
    )


@pytest.mark.django_db
def test_send_upcoming_expiration_warnings_skips_fully_spent_bonus(monkeypatch):
    from apps.bonuses.models import BonusLedgerEntry, BonusSpendRequest
    from apps.bonuses.services import send_upcoming_expiration_warnings
    from apps.common.choices import SPEND_REQUEST_STATUS_APPROVED
    from apps.users.models import Participant

    participant = Participant.objects.create(
        telegram_id="303",
        full_name="Анна",
        phone="+375293030303",
        consent_accepted=True,
    )
    BonusLedgerEntry.objects.create(
        participant=participant,
        amount=Decimal("50.00"),
        reason="Бонус за заказ",
        expires_at=date(2026, 8, 14),
    )
    BonusSpendRequest.objects.create(
        participant=participant,
        amount=Decimal("50.00"),
        comment="Доставка",
        status=SPEND_REQUEST_STATUS_APPROVED,
    )

    sent_messages = []

    def fake_send_telegram_message(*, chat_id: str, text: str) -> None:
        sent_messages.append((chat_id, text))

    monkeypatch.setattr(
        "apps.bonuses.services.send_telegram_message",
        fake_send_telegram_message,
    )

    warnings_sent = send_upcoming_expiration_warnings(today=date(2026, 7, 15))

    assert warnings_sent == 0
    assert sent_messages == []
