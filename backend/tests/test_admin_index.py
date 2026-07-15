import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.bonuses.models import BonusSpendRequest
from apps.common.choices import LEAD_STATUS_NEW, LEAD_STATUS_ORDERED, SPEND_REQUEST_STATUS_PENDING
from apps.referrals.models import ReferralLead
from apps.users.models import Participant


@pytest.mark.django_db
def test_admin_index_shows_admin_memo(client):
    user_model = get_user_model()
    admin_user = user_model.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="StrongPassword123!",
    )

    client.force_login(admin_user)
    response = client.get(reverse("admin:index"))

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert 'data-testid="admin-memo-card"' in content


@pytest.mark.django_db
def test_admin_index_shows_operational_dashboard_cards(client):
    user_model = get_user_model()
    admin_user = user_model.objects.create_superuser(
        username="admin2",
        email="admin2@example.com",
        password="StrongPassword123!",
    )
    participant = Participant.objects.create(
        telegram_id="dashboard-1",
        full_name="Ольга",
        phone="+375291111111",
        consent_accepted=True,
    )
    ReferralLead.objects.create(
        referral_link=None,
        client_company="ООО Своя",
        client_name="Ольга",
        client_phone="+375291111111",
        status=LEAD_STATUS_NEW,
        admin_comment="Нужно проверить",
    )
    ReferralLead.objects.create(
        referral_link=None,
        client_company="ООО Еще",
        client_name="Мария",
        client_phone="+375292222222",
        status=LEAD_STATUS_NEW,
    )
    ReferralLead.objects.create(
        referral_link=None,
        client_company="ООО Ждет",
        client_name="Сергей",
        client_phone="+375293333333",
        status=LEAD_STATUS_ORDERED,
    )
    BonusSpendRequest.objects.create(
        participant=participant,
        amount="40.00",
        comment="Доставка",
        status=SPEND_REQUEST_STATUS_PENDING,
    )

    client.force_login(admin_user)
    response = client.get(reverse("admin:index"))

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert 'data-testid="admin-dashboard-card"' in content
    assert 'data-testid="admin-priority-card"' in content
    assert 'data-testid="admin-quick-links"' in content
    assert "Новые заявки" in content
    assert "Свои заявки" in content
    assert "Ждут подтверждения" in content
    assert "Списания на рассмотрении" in content
    assert "Спорные случаи" in content
    assert "Профили без компании" in content
    assert "Что проверить в первую очередь" in content
    assert "Быстрые переходы" in content
    assert ">2<" in content
    assert ">1<" in content
