import csv

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse

from apps.bonuses.models import BonusLedgerEntry, BonusSpendRequest
from apps.bot.services import calculate_participant_balance
from apps.common.choices import (
    get_bonus_entry_type_label,
    get_lead_status_label,
    get_spend_request_status_label,
)
from apps.referrals.models import ReferralLead
from apps.users.models import Participant


OWNER_REPORT_HEADER = [
    "Тип строки",
    "Дата",
    "Участник",
    "Компания участника",
    "Основной контакт",
    "Телефон участника",
    "Баланс",
    "Клиент",
    "Компания клиента",
    "Телефон клиента",
    "Продукция",
    "Тираж",
    "Бюджет",
    "Срок",
    "Статус",
    "Сумма",
    "Основание / комментарий",
    "Кто пригласил",
]


def build_owner_report_rows() -> list[list[str]]:
    rows = []

    for participant in Participant.objects.order_by("-created_at"):
        rows.append(
            [
                "Участник",
                participant.created_at.strftime("%d.%m.%Y %H:%M"),
                participant.full_name,
                participant.company,
                "Да" if participant.is_primary_contact else "Нет",
                participant.phone,
                f"{calculate_participant_balance(participant=participant):.2f}",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "Зарегистрирован",
                "",
                participant.position,
                "",
            ]
        )

    for lead in ReferralLead.objects.select_related("referral_link__participant").order_by("-created_at"):
        referrer = lead.referral_link.participant if lead.referral_link else None
        rows.append(
            [
                "Реферальная заявка" if referrer else "Своя заявка",
                lead.created_at.strftime("%d.%m.%Y %H:%M"),
                referrer.full_name if referrer else "",
                referrer.company if referrer else "",
                "Да" if referrer and referrer.is_primary_contact else "",
                referrer.phone if referrer else "",
                f"{calculate_participant_balance(participant=referrer):.2f}" if referrer else "",
                lead.client_name,
                lead.client_company,
                lead.client_phone,
                lead.product_interest,
                lead.quantity,
                lead.budget,
                lead.deadline,
                get_lead_status_label(lead.status),
                "",
                lead.admin_comment or lead.rejection_reason,
                referrer.full_name if referrer else "Без реферала",
            ]
        )

    for entry in BonusLedgerEntry.objects.select_related("participant", "lead").order_by("-created_at"):
        rows.append(
            [
                "Бонусная операция",
                entry.created_at.strftime("%d.%m.%Y %H:%M"),
                entry.participant.full_name,
                entry.participant.company,
                "Да" if entry.participant.is_primary_contact else "Нет",
                entry.participant.phone,
                f"{calculate_participant_balance(participant=entry.participant):.2f}",
                entry.lead.client_name if entry.lead else "",
                entry.lead.client_company if entry.lead else "",
                entry.lead.client_phone if entry.lead else "",
                entry.lead.product_interest if entry.lead else "",
                entry.lead.quantity if entry.lead else "",
                entry.lead.budget if entry.lead else "",
                entry.lead.deadline if entry.lead else "",
                get_bonus_entry_type_label(entry.entry_type),
                f"{entry.amount:.2f}",
                entry.reason,
                entry.lead.referral_link.participant.full_name
                if entry.lead and entry.lead.referral_link
                else "",
            ]
        )

    for spend_request in BonusSpendRequest.objects.select_related("participant").order_by("-created_at"):
        rows.append(
            [
                "Запрос на списание",
                spend_request.created_at.strftime("%d.%m.%Y %H:%M"),
                spend_request.participant.full_name,
                spend_request.participant.company,
                "Да" if spend_request.participant.is_primary_contact else "Нет",
                spend_request.participant.phone,
                f"{calculate_participant_balance(participant=spend_request.participant):.2f}",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                get_spend_request_status_label(spend_request.status),
                f"{spend_request.amount:.2f}",
                spend_request.comment,
                "",
            ]
        )

    return rows


@staff_member_required
def owner_report_csv(request):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="owner_report.csv"'
    response.write("\ufeff")
    writer = csv.writer(response, delimiter=";")
    writer.writerow(OWNER_REPORT_HEADER)
    writer.writerows(build_owner_report_rows())
    return response
