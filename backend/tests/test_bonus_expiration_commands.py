from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.management import call_command


@pytest.mark.django_db
def test_send_bonus_expiration_warnings_dry_run_prints_preview(capsys):
    from apps.bonuses.models import BonusLedgerEntry
    from apps.users.models import Participant

    participant = Participant.objects.create(
        telegram_id="401",
        full_name="Ольга",
        phone="+375294010101",
        consent_accepted=True,
    )
    BonusLedgerEntry.objects.create(
        participant=participant,
        amount=Decimal("80.00"),
        reason="Бонус за заказ",
        expires_at=date.today() + timedelta(days=30),
    )

    call_command("send_bonus_expiration_warnings", "--dry-run")

    output = capsys.readouterr().out
    assert "Dry run" in output
    assert "Ольга" in output
    assert "80.00" in output


@pytest.mark.django_db
def test_expire_bonus_entries_dry_run_prints_preview(capsys):
    from apps.bonuses.models import BonusLedgerEntry
    from apps.users.models import Participant

    participant = Participant.objects.create(
        telegram_id="402",
        full_name="Мария",
        phone="+375294020202",
        consent_accepted=True,
    )
    BonusLedgerEntry.objects.create(
        participant=participant,
        amount=Decimal("60.00"),
        reason="Бонус за заказ",
        expires_at=date(2026, 7, 1),
    )

    call_command("expire_bonus_entries", "--dry-run")

    output = capsys.readouterr().out
    assert "Dry run" in output
    assert "Мария" in output
    assert "60.00" in output
