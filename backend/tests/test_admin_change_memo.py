import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.bonuses.models import BonusLedgerEntry, BonusSpendRequest
from apps.referrals.models import ReferralLead, ReferralLink
from apps.users.models import Participant


@pytest.fixture
def admin_user(db):
    user_model = get_user_model()
    return user_model.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="StrongPassword123!",
    )


@pytest.fixture
def sample_participant(db):
    return Participant.objects.create(
        telegram_id="100500",
        full_name="Olga Saniuk",
        phone="+375291234567",
        company="ООО Пример",
        consent_accepted=True,
    )


@pytest.mark.django_db
def test_referral_lead_change_page_shows_memo(client, admin_user, sample_participant):
    link = ReferralLink.objects.create(code="ref-100500", participant=sample_participant)
    lead = ReferralLead.objects.create(
        referral_link=link,
        client_company="ООО Новый клиент",
        client_name="Иван Иванов",
        client_phone="+375299999999",
    )

    client.force_login(admin_user)
    response = client.get(reverse("admin:referrals_referrallead_change", args=[lead.pk]))

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert 'data-testid="admin-change-memo-card"' in content
    assert "Проверка реферальной заявки" in content


@pytest.mark.django_db
def test_bonus_entry_change_page_shows_memo(client, admin_user, sample_participant):
    entry = BonusLedgerEntry.objects.create(
        participant=sample_participant,
        amount="60.00",
        reason="Ручное начисление",
    )

    client.force_login(admin_user)
    response = client.get(reverse("admin:bonuses_bonusledgerentry_change", args=[entry.pk]))

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert 'data-testid="admin-change-memo-card"' in content
    assert "Проверка начисления бонусов" in content


@pytest.mark.django_db
def test_bonus_spend_request_change_page_shows_memo(client, admin_user, sample_participant):
    request_obj = BonusSpendRequest.objects.create(
        participant=sample_participant,
        amount="40.00",
        comment="Доставка",
        status="pending",
    )

    client.force_login(admin_user)
    response = client.get(reverse("admin:bonuses_bonusspendrequest_change", args=[request_obj.pk]))

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert 'data-testid="admin-change-memo-card"' in content
    assert "Проверка списания бонусов" in content
