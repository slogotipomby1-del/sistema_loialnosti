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
def test_referral_lead_change_page_shows_client_card_and_memo(client, admin_user, sample_participant):
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
    assert 'data-testid="admin-client-card"' in content
    assert 'data-testid="admin-change-memo-card"' in content
    assert 'data-testid="admin-action-links-card"' in content
    assert "Карточка клиента" in content
    assert "Проверка реферальной заявки" in content
    assert "Тип заявки" in content
    assert "Компания пригласившего" in content
    assert "Возможные дубли по телефону" in content
    assert "Найти заявки по телефону" in content
    assert "Чек-лист перед решением" in content
    assert "от 2000 BYN" in content
    assert "тендер" in content
    assert "Комментарий администратора заполнен" in content


@pytest.mark.django_db
def test_referral_lead_change_page_shows_operational_context(client, admin_user, sample_participant):
    link = ReferralLink.objects.create(code="ref-context", participant=sample_participant)
    lead = ReferralLead.objects.create(
        referral_link=link,
        client_company="ООО Контекст",
        client_name="Иван Иванов",
        client_phone="+375299111222",
        product_interest="Рюкзаки",
    )
    ReferralLead.objects.create(
        referral_link=None,
        client_company="ООО Контекст",
        client_name="Мария",
        client_phone="+375299111333",
    )
    BonusLedgerEntry.objects.create(
        participant=sample_participant,
        amount="120.00",
        reason="Начисление за заказ",
    )
    BonusSpendRequest.objects.create(
        participant=sample_participant,
        amount="40.00",
        comment="Доставка",
        status="pending",
    )

    client.force_login(admin_user)
    response = client.get(reverse("admin:referrals_referrallead_change", args=[lead.pk]))

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert 'data-testid="admin-history-card"' in content
    assert "Операционный контекст заявки" in content
    assert "Баланс пригласившего" in content
    assert "120.00" in content
    assert "Последние списания" in content
    assert "Доставка" in content
    assert "Близкие заявки по компании" in content
    assert "Мария" in content


@pytest.mark.django_db
def test_participant_change_page_shows_profile_card(client, admin_user, sample_participant):
    referral_link = ReferralLink.objects.create(code="ref-profile", participant=sample_participant)
    ReferralLead.objects.create(
        referral_link=referral_link,
        client_company="ООО Клиент",
        client_name="Мария",
        client_phone="+375291111112",
        product_interest="Рюкзаки",
    )
    ReferralLead.objects.create(
        referral_link=None,
        client_company=sample_participant.company,
        client_name=sample_participant.full_name,
        client_phone=sample_participant.phone,
        product_interest="Своя заявка",
    )
    BonusLedgerEntry.objects.create(
        participant=sample_participant,
        amount="100.00",
        reason="Начисление",
    )
    BonusSpendRequest.objects.create(
        participant=sample_participant,
        amount="40.00",
        comment="Доставка",
        status="pending",
    )

    client.force_login(admin_user)
    response = client.get(reverse("admin:users_participant_change", args=[sample_participant.pk]))

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert 'data-testid="admin-client-card"' in content
    assert 'data-testid="admin-action-links-card"' in content
    assert 'data-testid="admin-history-card"' in content
    assert "Карточка участника" in content
    assert "Telegram ID" in content
    assert "Согласие" in content
    assert "Участников в компании" in content
    assert "Доступно бонусов" in content
    assert "Операционный контекст участника" in content
    assert "Последние заявки по ссылке" in content
    assert "Последние свои заявки" in content
    assert "Мария" in content
    assert "Своя заявка" in content
    assert "Запрос на списание" in content
    assert "Открыть списания участника" in content
    assert "Открыть бонусные операции" in content


@pytest.mark.django_db
def test_participant_change_page_shows_program_section_fields(client, admin_user, sample_participant):
    client.force_login(admin_user)
    response = client.get(reverse("admin:users_participant_change", args=[sample_participant.pk]))

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Программа" in content
    assert "consent_accepted" in content


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
    assert "Проверка бонусной операции" in content
    assert "отрицательным" in content
    assert "Основание начисления" in content
    assert "Срок сгорания указан" in content
    assert "причина аннулирования" in content


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
    assert "Компания" in content
    assert "не больше 20% суммы заказа" in content
    assert "не больше 200 BYN" in content
    assert "Назначение списания понятно" in content
