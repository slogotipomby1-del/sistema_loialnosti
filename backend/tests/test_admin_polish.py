import pytest
from django.urls import reverse

from apps.bonuses.models import BonusSpendRequest
from apps.referrals.models import ReferralLead, ReferralLink
from apps.users.models import Participant


@pytest.mark.django_db
def test_participant_changelist_uses_russian_column_labels(client, admin_user):
    Participant.objects.create(
        telegram_id="tg-admin-columns-1",
        full_name="Ольга",
        phone="+375291111115",
        company="ООО Пример",
        position="Маркетолог",
        is_primary_contact=True,
        consent_accepted=True,
    )

    client.force_login(admin_user)
    response = client.get(reverse("admin:users_participant_changelist"))

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Участник" in content
    assert "Компания" in content
    assert "Должность" in content
    assert "Основной контакт" in content
    assert "Full name" not in content
    assert "Position" not in content
    assert "Is primary contact" not in content


@pytest.mark.django_db
def test_referral_lead_changelist_uses_russian_column_labels(client, admin_user):
    participant = Participant.objects.create(
        telegram_id="tg-admin-columns-2",
        full_name="Ольга",
        phone="+375291111114",
        company="ООО Партнёр",
        consent_accepted=True,
    )
    link = ReferralLink.objects.create(code="ru-columns-link", participant=participant)
    ReferralLead.objects.create(
        referral_link=link,
        client_company="ООО Клиент",
        client_name="Иван",
        client_phone="+375291111113",
        product_interest="Рюкзаки",
    )

    client.force_login(admin_user)
    response = client.get(reverse("admin:referrals_referrallead_changelist"))

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Компания клиента" in content
    assert "Имя клиента" in content
    assert "Телефон клиента" in content
    assert "Интерес к продукции" in content
    assert "Client company" not in content
    assert "Client name" not in content
    assert "Client phone" not in content
    assert "Product interest" not in content


@pytest.mark.django_db
def test_bonus_spend_request_has_human_readable_string():
    participant = Participant.objects.create(
        telegram_id="tg-admin-columns-3",
        full_name="Ольга",
        phone="+375291111112",
        consent_accepted=True,
    )
    request_obj = BonusSpendRequest.objects.create(
        participant=participant,
        amount="60.00",
        comment="Термокружка",
    )

    assert str(request_obj) == "Ольга — Термокружка — 60.00"
