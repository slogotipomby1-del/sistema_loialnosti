import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.bonuses.models import BonusLedgerEntry, BonusSpendRequest
from apps.referrals.models import ReferralLead
from apps.users.models import Participant


@pytest.fixture
def admin_user(db):
    user_model = get_user_model()
    return user_model.objects.create_superuser(
        username="admin_polish",
        email="admin_polish@example.com",
        password="StrongPassword123!",
    )


@pytest.fixture
def sample_participant(db):
    return Participant.objects.create(
        telegram_id="200500",
        full_name="Ольга Санюк",
        phone="+375291234568",
        company="ООО Пример",
        position="Маркетолог",
        consent_accepted=True,
    )


@pytest.mark.django_db
def test_bonus_entry_change_page_shows_summary_card(client, admin_user, sample_participant):
    lead = ReferralLead.objects.create(
        referral_link=None,
        client_company="ООО Клиент",
        client_name="Иван Иванов",
        client_phone="+375299999998",
        product_interest="Рюкзаки",
    )
    entry = BonusLedgerEntry.objects.create(
        participant=sample_participant,
        lead=lead,
        amount="60.00",
        reason="Ручное начисление",
    )

    client.force_login(admin_user)
    response = client.get(reverse("admin:bonuses_bonusledgerentry_change", args=[entry.pk]))

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert 'data-testid="admin-client-card"' in content
    assert "Карточка бонусной операции" in content
    assert "Участник" in content
    assert "Основание" in content
    assert "Сумма" in content
    assert "Реферальная заявка" in content


@pytest.mark.django_db
def test_bonus_spend_request_change_page_shows_summary_card(client, admin_user, sample_participant):
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
    assert 'data-testid="admin-client-card"' in content
    assert "Карточка запроса на списание" in content
    assert "Участник" in content
    assert "Компания" in content
    assert "Телефон" in content
    assert "Подарок или комментарий" in content
    assert "Сумма" in content


@pytest.mark.django_db
def test_bonus_spend_request_change_page_shows_action_links(client, admin_user, sample_participant):
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
    assert 'data-testid="admin-action-links-card"' in content
    assert "Открыть участника" in content
    assert "Найти заявки этого участника" in content
