from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.adminpanel.templatetags.admin_dashboard import (
    admin_dashboard_cards,
    admin_dashboard_priority_items,
    admin_dashboard_quick_links,
)
from apps.bonuses.models import BonusLedgerEntry
from apps.users.models import Participant


@pytest.mark.django_db
def test_bonus_ledger_changelist_filters_upcoming_expiration_entries(client):
    admin_user = get_user_model().objects.create_superuser(
        username="bonus-filter-admin-1",
        email="bonus-filter-admin-1@example.com",
        password="StrongPassword123!",
    )
    participant = Participant.objects.create(
        telegram_id="bonus-warning-1",
        full_name="Ольга",
        phone="+375291234501",
        consent_accepted=True,
    )
    upcoming_entry = BonusLedgerEntry.objects.create(
        participant=participant,
        amount=Decimal("80.00"),
        reason="Скоро сгорит",
        expires_at=date.today() + timedelta(days=30),
    )
    BonusLedgerEntry.objects.create(
        participant=participant,
        amount=Decimal("40.00"),
        reason="Пока не скоро",
        expires_at=date.today() + timedelta(days=60),
    )

    client.force_login(admin_user)
    response = client.get(
        reverse("admin:bonuses_bonusledgerentry_changelist"),
        {"bonus_expiration_state": "warning"},
    )

    assert response.status_code == 200
    assert list(response.context["cl"].queryset) == [upcoming_entry]


@pytest.mark.django_db
def test_bonus_ledger_changelist_filters_expired_entries(client):
    admin_user = get_user_model().objects.create_superuser(
        username="bonus-filter-admin-2",
        email="bonus-filter-admin-2@example.com",
        password="StrongPassword123!",
    )
    participant = Participant.objects.create(
        telegram_id="bonus-expired-1",
        full_name="Мария",
        phone="+375291234502",
        consent_accepted=True,
    )
    expired_entry = BonusLedgerEntry.objects.create(
        participant=participant,
        amount=Decimal("60.00"),
        reason="Уже сгорел",
        expires_at=date(2026, 7, 1),
    )
    BonusLedgerEntry.objects.create(
        participant=participant,
        amount=Decimal("50.00"),
        reason="Еще активен",
        expires_at=date(2026, 8, 25),
    )

    client.force_login(admin_user)
    response = client.get(
        reverse("admin:bonuses_bonusledgerentry_changelist"),
        {"bonus_expiration_state": "expired"},
    )

    assert response.status_code == 200
    assert list(response.context["cl"].queryset) == [expired_entry]


@pytest.mark.django_db
def test_bonus_dashboard_links_point_to_bonus_expiration_filters():
    participant = Participant.objects.create(
        telegram_id="bonus-dashboard-links",
        full_name="Ирина",
        phone="+375291234503",
        consent_accepted=True,
    )
    BonusLedgerEntry.objects.create(
        participant=participant,
        amount=Decimal("70.00"),
        reason="Скоро сгорит",
        expires_at=date.today() + timedelta(days=30),
    )
    BonusLedgerEntry.objects.create(
        participant=participant,
        amount=Decimal("55.00"),
        reason="Уже просрочен",
        expires_at=date(2026, 7, 1),
    )

    cards = admin_dashboard_cards()
    priority_items = admin_dashboard_priority_items()
    quick_links = admin_dashboard_quick_links()

    warning_url = reverse("admin:bonuses_bonusledgerentry_changelist") + "?bonus_expiration_state=warning"
    expired_url = reverse("admin:bonuses_bonusledgerentry_changelist") + "?bonus_expiration_state=expired"

    assert any(card["url"] == warning_url for card in cards if "Скоро" in card["title"])
    assert any(card["url"] == expired_url for card in cards if "просроч" in card["title"].lower())
    assert any(item["url"] == warning_url for item in priority_items if "Сгорание" in item["title"])
    assert any(link["url"] == warning_url for link in quick_links if "операции" in link["title"].lower())
