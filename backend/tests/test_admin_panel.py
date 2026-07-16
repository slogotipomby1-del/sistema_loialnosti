import pytest
from django.contrib.admin.sites import site
from django.test import RequestFactory
from django.urls import reverse

from apps.bonuses.models import BonusLedgerEntry, BonusSpendRequest
from apps.common.choices import (
    BONUS_ENTRY_TYPE_REVERSAL,
    LEAD_STATUS_BONUS_CONFIRMED,
    LEAD_STATUS_IN_PROGRESS,
    LEAD_STATUS_NEW,
    LEAD_STATUS_ORDERED,
    LEAD_STATUS_REJECTED,
    SPEND_REQUEST_STATUS_PENDING,
    SPEND_REQUEST_STATUS_APPROVED,
    SPEND_REQUEST_STATUS_REJECTED,
)
from apps.referrals.models import ReferralLead, ReferralLink
from apps.users.models import Participant


def test_referral_lead_admin_has_main_columns():
    admin_instance = site._registry[ReferralLead]

    assert admin_instance.list_display == (
        "lead_type_label",
        "client_company",
        "client_name",
        "client_phone",
        "product_interest",
        "referrer_name",
        "referrer_company",
        "status_label",
        "created_at",
    )


def test_bonus_spend_request_admin_has_main_columns():
    admin_instance = site._registry[BonusSpendRequest]

    assert admin_instance.list_display == (
        "participant",
        "participant_company",
        "participant_phone",
        "comment",
        "amount",
        "status_label",
        "created_at",
    )


def test_referral_link_admin_is_registered_for_autocomplete():
    admin_instance = site._registry[ReferralLink]

    assert admin_instance.search_fields == ("code", "participant__full_name", "participant__phone")


def test_participant_admin_has_useful_dashboard_columns():
    admin_instance = site._registry[Participant]

    assert admin_instance.list_display == (
        "full_name",
        "company",
        "position",
        "is_primary_contact",
        "bonus_balance",
        "invited_leads_count",
        "spend_requests_count",
        "phone",
        "telegram_id",
        "consent_accepted",
        "created_at",
    )
    assert admin_instance.ordering == ("-created_at",)
    assert admin_instance.list_per_page == 25
    assert admin_instance.readonly_fields == ("created_at", "bonus_balance", "invited_leads_count", "spend_requests_count")
    assert "export_selected_to_csv" in admin_instance.actions


def test_referral_lead_admin_has_helpful_list_settings():
    admin_instance = site._registry[ReferralLead]
    filter_names = tuple(
        item if isinstance(item, str) else item.parameter_name
        for item in admin_instance.list_filter
    )

    assert admin_instance.ordering == ("-created_at",)
    assert admin_instance.date_hierarchy == "created_at"
    assert admin_instance.list_per_page == 25
    assert filter_names == ("status", "created_at", "lead_source", "has_admin_comment")
    assert admin_instance.readonly_fields == ("lead_type_label", "referrer_name", "referrer_company", "created_at")
    assert "export_selected_to_csv" in admin_instance.actions


def test_bonus_spend_request_admin_has_helpful_list_settings():
    admin_instance = site._registry[BonusSpendRequest]
    filter_names = tuple(
        item if isinstance(item, str) else item.parameter_name
        for item in admin_instance.list_filter
    )

    assert admin_instance.ordering == ("-created_at",)
    assert admin_instance.date_hierarchy == "created_at"
    assert admin_instance.list_per_page == 25
    assert filter_names == ("status", "created_at", "has_comment")
    assert admin_instance.readonly_fields == ("participant_phone", "participant_company", "created_at")


@pytest.mark.django_db
def test_participant_admin_dashboard_counters_are_calculated():
    participant = Participant.objects.create(
        telegram_id="tg-admin-3",
        full_name="Ольга",
        phone="+375294444444",
        company="ООО Тест",
        consent_accepted=True,
    )
    link = ReferralLink.objects.create(code="link-olga", participant=participant)
    ReferralLead.objects.create(
        referral_link=link,
        client_company="ООО Клиент",
        client_name="Иван",
        client_phone="+375295555555",
    )
    ReferralLead.objects.create(
        referral_link=None,
        client_company="ООО Тест",
        client_name="Ольга",
        client_phone="+375294444444",
    )
    BonusLedgerEntry.objects.create(
        participant=participant,
        amount="120.00",
        reason="Начисление за заказ",
    )
    BonusSpendRequest.objects.create(
        participant=participant,
        amount="40.00",
        comment="Доставка",
        status=SPEND_REQUEST_STATUS_PENDING,
    )

    admin_instance = site._registry[Participant]

    assert str(admin_instance.bonus_balance(participant)) == "120.00"
    assert admin_instance.invited_leads_count(participant) == 1
    assert admin_instance.spend_requests_count(participant) == 1


@pytest.mark.django_db
def test_referral_lead_changelist_filters_self_requests(client, admin_user):
    participant = Participant.objects.create(
        telegram_id="tg-admin-4",
        full_name="Ольга",
        phone="+375296666666",
        consent_accepted=True,
    )
    link = ReferralLink.objects.create(code="filter-link", participant=participant)
    ReferralLead.objects.create(
        referral_link=link,
        client_company="ООО Клиент",
        client_name="Иван",
        client_phone="+375297777777",
    )
    self_lead = ReferralLead.objects.create(
        referral_link=None,
        client_company="ООО Своя",
        client_name="Ольга",
        client_phone="+375296666666",
    )

    client.force_login(admin_user)
    response = client.get(
        reverse("admin:referrals_referrallead_changelist"),
        {"lead_source": "self"},
    )

    assert response.status_code == 200
    result_list = response.context["cl"].queryset
    assert list(result_list) == [self_lead]


@pytest.mark.django_db
def test_bonus_spend_request_changelist_filters_items_with_comment(client, admin_user):
    participant = Participant.objects.create(
        telegram_id="tg-admin-5",
        full_name="Мария",
        phone="+375298888888",
        consent_accepted=True,
    )
    with_comment = BonusSpendRequest.objects.create(
        participant=participant,
        amount="40.00",
        comment="Доставка",
    )
    BonusSpendRequest.objects.create(
        participant=participant,
        amount="60.00",
        comment="",
    )

    client.force_login(admin_user)
    response = client.get(
        reverse("admin:bonuses_bonusspendrequest_changelist"),
        {"has_comment": "yes"},
    )

    assert response.status_code == 200
    result_list = response.context["cl"].queryset
    assert list(result_list) == [with_comment]


@pytest.mark.django_db
def test_referral_lead_admin_bulk_actions_update_statuses():
    participant = Participant.objects.create(
        telegram_id="tg-admin-1",
        full_name="Ольга",
        phone="+375291111111",
        consent_accepted=True,
    )
    referral_link = ReferralLink.objects.create(code="abc123", participant=participant)
    lead = ReferralLead.objects.create(
        referral_link=referral_link,
        client_company="ООО Ромашка",
        client_name="Иван",
        client_phone="+375292222222",
    )
    admin_instance = site._registry[ReferralLead]
    request = RequestFactory().post("/admin/referrals/referrallead/")

    admin_instance.mark_as_in_progress(request, ReferralLead.objects.filter(pk=lead.pk))
    lead.refresh_from_db()
    assert lead.status == LEAD_STATUS_IN_PROGRESS

    admin_instance.mark_as_ordered(request, ReferralLead.objects.filter(pk=lead.pk))
    lead.refresh_from_db()
    assert lead.status == LEAD_STATUS_ORDERED

    admin_instance.mark_as_bonus_confirmed(request, ReferralLead.objects.filter(pk=lead.pk))
    lead.refresh_from_db()
    assert lead.status == LEAD_STATUS_BONUS_CONFIRMED

    admin_instance.mark_as_rejected(request, ReferralLead.objects.filter(pk=lead.pk))
    lead.refresh_from_db()
    assert lead.status == LEAD_STATUS_REJECTED


@pytest.mark.django_db
def test_referral_lead_admin_shows_type_and_referrer_company():
    participant = Participant.objects.create(
        telegram_id="tg-admin-6",
        full_name="Ольга",
        phone="+375299111111",
        company="ООО Партнер",
        consent_accepted=True,
    )
    referral_link = ReferralLink.objects.create(code="company-ref", participant=participant)
    referral_lead = ReferralLead.objects.create(
        referral_link=referral_link,
        client_company="ООО Клиент",
        client_name="Иван",
        client_phone="+375299222222",
    )
    self_lead = ReferralLead.objects.create(
        referral_link=None,
        client_company="ООО Своя",
        client_name="Ольга",
        client_phone="+375299111111",
    )
    admin_instance = site._registry[ReferralLead]

    assert admin_instance.lead_type_label(referral_lead) == "Реферал"
    assert admin_instance.referrer_company(referral_lead) == "ООО Партнер"
    assert admin_instance.lead_type_label(self_lead) == "Своя заявка"
    assert admin_instance.referrer_company(self_lead) == "—"


@pytest.mark.django_db
def test_referral_lead_admin_counts_possible_duplicates():
    participant = Participant.objects.create(
        telegram_id="tg-admin-dup",
        full_name="Ольга",
        phone="+375299111112",
        consent_accepted=True,
    )
    referral_link = ReferralLink.objects.create(code="dup-ref", participant=participant)
    lead = ReferralLead.objects.create(
        referral_link=referral_link,
        client_company="ООО Клиент",
        client_name="Иван",
        client_phone="+375299000001",
    )
    ReferralLead.objects.create(
        referral_link=None,
        client_company="ООО Клиент",
        client_name="Мария",
        client_phone="+375299000001",
    )
    admin_instance = site._registry[ReferralLead]

    assert admin_instance.phone_duplicates_count(lead) == 1
    assert admin_instance.company_duplicates_count(lead) == 1


@pytest.mark.django_db
def test_bonus_spend_request_admin_bulk_actions_update_statuses():
    participant = Participant.objects.create(
        telegram_id="tg-admin-2",
        full_name="Мария",
        phone="+375293333333",
        consent_accepted=True,
    )
    request_obj = BonusSpendRequest.objects.create(
        participant=participant,
        amount="60.00",
        comment="Термокружка",
    )
    admin_instance = site._registry[BonusSpendRequest]
    request = RequestFactory().post("/admin/bonuses/bonusspendrequest/")

    admin_instance.mark_as_approved(request, BonusSpendRequest.objects.filter(pk=request_obj.pk))
    request_obj.refresh_from_db()
    assert request_obj.status == SPEND_REQUEST_STATUS_APPROVED

    admin_instance.mark_as_rejected(request, BonusSpendRequest.objects.filter(pk=request_obj.pk))
    request_obj.refresh_from_db()
    assert request_obj.status == SPEND_REQUEST_STATUS_REJECTED


@pytest.mark.django_db
def test_bonus_spend_request_admin_shows_participant_company():
    participant = Participant.objects.create(
        telegram_id="tg-admin-7",
        full_name="Елена",
        phone="+375291010101",
        company="ООО Альфа",
        consent_accepted=True,
    )
    request_obj = BonusSpendRequest.objects.create(
        participant=participant,
        amount="50.00",
        comment="Доставка",
    )
    admin_instance = site._registry[BonusSpendRequest]

    assert admin_instance.participant_company(request_obj) == "ООО Альфа"


def test_bonus_ledger_entry_admin_has_operation_type_column():
    admin_instance = site._registry[BonusLedgerEntry]

    assert admin_instance.list_display == (
        "participant",
        "entry_type_label",
        "amount",
        "reason",
        "expires_at",
        "lead",
        "created_at",
    )


@pytest.mark.django_db
def test_participant_admin_balance_can_be_negative_after_reversal_and_approved_spending():
    participant = Participant.objects.create(
        telegram_id="tg-admin-8",
        full_name="Наталья",
        phone="+375291111119",
        consent_accepted=True,
    )
    BonusLedgerEntry.objects.create(
        participant=participant,
        amount="100.00",
        reason="Начисление",
    )
    BonusLedgerEntry.objects.create(
        participant=participant,
        amount="-70.00",
        reason="Аннулирование",
        entry_type=BONUS_ENTRY_TYPE_REVERSAL,
    )
    BonusSpendRequest.objects.create(
        participant=participant,
        amount="50.00",
        comment="Подарок",
        status=SPEND_REQUEST_STATUS_APPROVED,
    )
    admin_instance = site._registry[Participant]

    assert str(admin_instance.bonus_balance(participant)) == "-20.00"


@pytest.mark.django_db
def test_participant_admin_can_export_selected_to_csv():
    participant = Participant.objects.create(
        telegram_id="tg-export-1",
        full_name="Ирина",
        phone="+375291111118",
        company="ООО Экспорт",
        position="Маркетолог",
        consent_accepted=True,
    )
    admin_instance = site._registry[Participant]
    request = RequestFactory().post("/admin/users/participant/")

    response = admin_instance.export_selected_to_csv(request, Participant.objects.filter(pk=participant.pk))

    assert response.status_code == 200
    assert response["Content-Disposition"] == 'attachment; filename="participants_export.csv"'
    content = response.content.decode("utf-8")
    assert "Ирина" in content
    assert "ООО Экспорт" in content


@pytest.mark.django_db
def test_referral_lead_admin_can_export_selected_to_csv():
    participant = Participant.objects.create(
        telegram_id="tg-export-2",
        full_name="Ольга",
        phone="+375291111117",
        consent_accepted=True,
    )
    link = ReferralLink.objects.create(code="export-link", participant=participant)
    lead = ReferralLead.objects.create(
        referral_link=link,
        client_company="ООО Клиент",
        client_name="Иван",
        client_phone="+375291111116",
        client_email="ivan@example.com",
        product_interest="Рюкзаки",
        status=LEAD_STATUS_NEW,
    )
    admin_instance = site._registry[ReferralLead]
    request = RequestFactory().post("/admin/referrals/referrallead/")

    response = admin_instance.export_selected_to_csv(request, ReferralLead.objects.filter(pk=lead.pk))

    assert response.status_code == 200
    assert response["Content-Disposition"] == 'attachment; filename="referral_leads_export.csv"'
    content = response.content.decode("utf-8")
    assert "Иван" in content
    assert "ivan@example.com" in content
    assert "Рюкзаки" in content
