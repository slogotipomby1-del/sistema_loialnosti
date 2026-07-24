from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from apps.bonuses.models import BonusLedgerEntry, BonusSpendRequest
from apps.common.choices import LEAD_STATUS_ORDERED, SPEND_REQUEST_STATUS_APPROVED
from apps.referrals.models import ReferralLead, ReferralLink
from apps.users.models import Participant


@pytest.mark.django_db
def test_owner_report_requires_admin_login(client):
    response = client.get("/admin/owner-report.csv")

    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


@pytest.mark.django_db
def test_owner_report_csv_contains_program_snapshot(client):
    user_model = get_user_model()
    admin_user = user_model.objects.create_superuser(
        username="owner",
        email="owner@example.com",
        password="StrongPassword123!",
    )
    participant = Participant.objects.create(
        telegram_id="owner-report-1",
        full_name="Ирина",
        phone="+375291111119",
        company="ООО Отчёт",
        position="HR",
        is_primary_contact=True,
        consent_accepted=True,
    )
    link = ReferralLink.objects.create(code="owner-report-link", participant=participant)
    lead = ReferralLead.objects.create(
        referral_link=link,
        client_company="ООО Клиент",
        client_name="Анна",
        client_phone="+375291111120",
        product_interest="Welcome pack",
        status=LEAD_STATUS_ORDERED,
    )
    BonusLedgerEntry.objects.create(
        participant=participant,
        lead=lead,
        amount=Decimal("120.00"),
        reason="Бонус за заказ",
    )
    BonusSpendRequest.objects.create(
        participant=participant,
        amount=Decimal("40.00"),
        comment="Доставка",
        status=SPEND_REQUEST_STATUS_APPROVED,
    )

    client.force_login(admin_user)
    response = client.get("/admin/owner-report.csv")

    assert response.status_code == 200
    assert response["Content-Disposition"] == 'attachment; filename="owner_report.csv"'
    content = response.content.decode("utf-8")
    assert "Тип строки" in content
    assert "Участник" in content
    assert "Реферальная заявка" in content
    assert "Бонусная операция" in content
    assert "Запрос на списание" in content
    assert "Ирина" in content
    assert "ООО Отчёт" in content
    assert "ООО Клиент" in content
    assert "Welcome pack" in content
    assert "120.00" in content
    assert "Доставка" in content
