import pytest
from django.contrib.admin.sites import site
from django.test import RequestFactory
from django.urls import reverse

from apps.adminpanel.admin import ParticipantCompanyStateFilter, ReferralLeadSourceFilter
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


def test_referral_lead_source_filter_has_human_labels():
    filter_instance = ReferralLeadSourceFilter(
        request=None,
        params={},
        model=ReferralLead,
        model_admin=site._registry[ReferralLead],
    )

    assert filter_instance.title == "Тип заявки"
    assert filter_instance.lookups(None, None) == (
        ("self", "Своя заявка"),
        ("referral", "Реферал"),
    )


def test_participant_company_state_filter_has_human_labels():
    filter_instance = ParticipantCompanyStateFilter(
        request=None,
        params={},
        model=Participant,
        model_admin=site._registry[Participant],
    )

    assert filter_instance.title == "Компания"
    assert filter_instance.lookups(None, None) == (
        ("with_company", "Есть компания"),
        ("without_company", "Без компании"),
        ("team", "В компании несколько участников"),
        ("without_primary", "В компании нет основного контакта"),
    )


def test_referral_lead_admin_has_main_columns():
    admin_instance = site._registry[ReferralLead]

    assert admin_instance.list_display == (
        "lead_type_label",
        "client_company",
        "client_name",
        "client_phone",
        "phone_duplicates_badge",
        "company_duplicates_badge",
        "product_interest",
        "referrer_name",
        "referrer_company",
        "status_badge",
        "quick_actions",
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
        "status_badge",
        "quick_actions",
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
        "company_team_size",
        "position",
        "is_primary_contact",
        "bonus_balance_badge",
        "invited_leads_count",
        "spend_requests_count",
        "quick_actions",
        "phone",
        "telegram_id",
        "consent_accepted",
        "created_at",
    )
    assert admin_instance.ordering == ("-created_at",)
    assert admin_instance.list_per_page == 25
    assert admin_instance.readonly_fields == ("created_at", "bonus_balance", "invited_leads_count", "spend_requests_count")
    assert "export_selected_to_csv" in admin_instance.actions
    filter_names = tuple(
        item if isinstance(item, str) else item.parameter_name
        for item in admin_instance.list_filter
    )
    assert filter_names == ("consent_accepted", "is_primary_contact", "created_at", "company_state")


def test_referral_lead_admin_has_helpful_list_settings():
    admin_instance = site._registry[ReferralLead]
    filter_names = tuple(
        item if isinstance(item, str) else item.parameter_name
        for item in admin_instance.list_filter
    )

    assert admin_instance.ordering == ("-created_at",)
    assert admin_instance.date_hierarchy == "created_at"
    assert admin_instance.list_per_page == 25
    assert filter_names == ("status", "created_at", "lead_source", "has_admin_comment", "duplicate_state")
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


def test_referral_lead_admin_badge_columns_have_human_descriptions():
    admin_instance = site._registry[ReferralLead]

    assert admin_instance.status_label.short_description == "Статус"
    assert admin_instance.status_badge.short_description == "Статус"
    assert admin_instance.quick_actions.short_description == "Быстрые действия"


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
    assert "+120.00" in admin_instance.bonus_balance_badge(participant)
    assert admin_instance.company_team_size(participant) == 1
    assert admin_instance.invited_leads_count(participant) == 1
    assert admin_instance.spend_requests_count(participant) == 1


@pytest.mark.django_db
def test_participant_changelist_filters_companies_without_primary_contact(client, admin_user):
    Participant.objects.create(
        telegram_id="tg-company-filter-1",
        full_name="Анна",
        phone="+375290000101",
        company="ООО Без главного",
        consent_accepted=True,
        is_primary_contact=False,
    )
    participant_without_primary = Participant.objects.create(
        telegram_id="tg-company-filter-2",
        full_name="Мария",
        phone="+375290000102",
        company="ООО Без главного",
        consent_accepted=True,
        is_primary_contact=False,
    )
    Participant.objects.create(
        telegram_id="tg-company-filter-3",
        full_name="Ольга",
        phone="+375290000103",
        company="ООО С главным",
        consent_accepted=True,
        is_primary_contact=True,
    )

    client.force_login(admin_user)
    response = client.get(
        reverse("admin:users_participant_changelist"),
        {"company_state": "without_primary"},
    )

    assert response.status_code == 200
    result_list = list(response.context["cl"].queryset)
    assert participant_without_primary in result_list


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
    messages = []

    def capture_message(request, message):
        messages.append(message)

    admin_instance.message_user = capture_message

    admin_instance.mark_as_in_progress(request, ReferralLead.objects.filter(pk=lead.pk))
    lead.refresh_from_db()
    assert lead.status == LEAD_STATUS_IN_PROGRESS
    assert messages[-1] == "Заявок переведено в статус «В работе»: 1."

    admin_instance.mark_as_ordered(request, ReferralLead.objects.filter(pk=lead.pk))
    lead.refresh_from_db()
    assert lead.status == LEAD_STATUS_ORDERED
    assert messages[-1] == "Заявок переведено в статус «Ожидает подтверждения»: 1."

    admin_instance.mark_as_bonus_confirmed(request, ReferralLead.objects.filter(pk=lead.pk))
    lead.refresh_from_db()
    assert lead.status == LEAD_STATUS_BONUS_CONFIRMED
    assert messages[-1] == "Заявок переведено в статус «Бонус начислен»: 1."

    admin_instance.mark_as_rejected(request, ReferralLead.objects.filter(pk=lead.pk))
    lead.refresh_from_db()
    assert lead.status == LEAD_STATUS_REJECTED
    assert messages[-1] == "Заявок переведено в статус «Отклонена»: 1."


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
def test_referral_lead_changelist_filters_possible_duplicates(client, admin_user):
    participant = Participant.objects.create(
        telegram_id="tg-admin-dup-filter",
        full_name="Ольга",
        phone="+375299111113",
        consent_accepted=True,
    )
    link = ReferralLink.objects.create(code="dup-filter", participant=participant)
    duplicate_lead = ReferralLead.objects.create(
        referral_link=link,
        client_company="ООО Клиент",
        client_name="Иван",
        client_phone="+375299000002",
    )
    ReferralLead.objects.create(
        referral_link=None,
        client_company="ООО Клиент",
        client_name="Мария",
        client_phone="+375299000002",
    )
    clean_lead = ReferralLead.objects.create(
        referral_link=None,
        client_company="ООО Чистая",
        client_name="Анна",
        client_phone="+375299000003",
    )

    client.force_login(admin_user)
    response = client.get(
        reverse("admin:referrals_referrallead_changelist"),
        {"duplicate_state": "yes"},
    )

    assert response.status_code == 200
    result_list = list(response.context["cl"].queryset)
    assert duplicate_lead in result_list
    assert clean_lead not in result_list


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
    messages = []

    def capture_message(request, message):
        messages.append(message)

    admin_instance.message_user = capture_message

    admin_instance.mark_as_approved(request, BonusSpendRequest.objects.filter(pk=request_obj.pk))
    request_obj.refresh_from_db()
    assert request_obj.status == SPEND_REQUEST_STATUS_APPROVED
    assert messages[-1] == "Подтверждено списаний: 1."

    admin_instance.mark_as_rejected(request, BonusSpendRequest.objects.filter(pk=request_obj.pk))
    request_obj.refresh_from_db()
    assert request_obj.status == SPEND_REQUEST_STATUS_REJECTED
    assert messages[-1] == "Отклонено списаний: 1."


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
    filter_names = tuple(
        item if isinstance(item, str) else item.parameter_name
        for item in admin_instance.list_filter
    )

    assert admin_instance.list_display == (
        "participant",
        "participant_company",
        "entry_type_label",
        "amount",
        "reason",
        "lead_client",
        "expires_at",
        "quick_actions",
        "created_at",
    )
    assert filter_names == ("entry_type", "created_at", "bonus_expiration_state")


@pytest.mark.django_db
def test_participant_admin_renders_quick_actions():
    participant = Participant.objects.create(
        telegram_id="tg-quick-participant",
        full_name="Ольга",
        phone="+375291111120",
        company="ООО Альфа",
        consent_accepted=True,
    )
    admin_instance = site._registry[Participant]

    actions_html = admin_instance.quick_actions(participant)

    assert "Открыть" in actions_html
    assert "Списания" in actions_html
    assert "Компания" in actions_html


@pytest.mark.django_db
def test_bonus_ledger_entry_admin_shows_company_client_and_quick_actions():
    participant = Participant.objects.create(
        telegram_id="tg-ledger-quick",
        full_name="Мария",
        phone="+375291111121",
        company="ООО Бета",
        consent_accepted=True,
    )
    lead = ReferralLead.objects.create(
        referral_link=None,
        client_company="ООО Клиент",
        client_name="Иван",
        client_phone="+375291111122",
    )
    entry = BonusLedgerEntry.objects.create(
        participant=participant,
        lead=lead,
        amount="70.00",
        reason="Начисление",
    )
    admin_instance = site._registry[BonusLedgerEntry]

    assert admin_instance.participant_company(entry) == "ООО Бета"
    assert admin_instance.lead_client(entry) == "Иван"

    actions_html = admin_instance.quick_actions(entry)

    assert "Участник" in actions_html
    assert "Лид" in actions_html


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
    assert "-20.00" in admin_instance.bonus_balance_badge(participant)


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


@pytest.mark.django_db
def test_referral_lead_admin_renders_status_badge_and_quick_actions():
    participant = Participant.objects.create(
        telegram_id="tg-admin-badge",
        full_name="?????",
        phone="+375299111119",
        company="??? ???????",
        consent_accepted=True,
    )
    referral_link = ReferralLink.objects.create(code="badge-ref", participant=participant)
    lead = ReferralLead.objects.create(
        referral_link=referral_link,
        client_company="??? ??????",
        client_name="????",
        client_phone="+375299222229",
        status=LEAD_STATUS_IN_PROGRESS,
    )
    admin_instance = site._registry[ReferralLead]

    status_html = admin_instance.status_badge(lead)
    actions_html = admin_instance.quick_actions(lead)

    assert admin_instance.status_label(lead) in status_html
    assert "badge" in status_html
    assert "Телефон" in actions_html
    assert "Компания" in actions_html
    assert "Участник" in actions_html
