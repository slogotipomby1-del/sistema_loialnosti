import secrets
from decimal import Decimal

from apps.bonuses.models import BonusLedgerEntry, BonusSpendRequest
from apps.common.choices import SPEND_REQUEST_STATUS_APPROVED, SPEND_REQUEST_STATUS_PENDING
from apps.notifications import telegram as telegram_notifications
from apps.referrals.models import ReferralLead, ReferralLink
from apps.users.models import Participant


def register_participant(*, telegram_id: str, full_name: str, phone: str, consent_accepted: bool):
    participant, _ = Participant.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            "full_name": full_name,
            "phone": phone,
            "consent_accepted": consent_accepted,
        },
    )
    ReferralLink.objects.get_or_create(
        participant=participant,
        defaults={"code": secrets.token_urlsafe(8)},
    )
    return participant


def register_participant_with_referral_code(
    *, telegram_id: str, full_name: str, phone: str, consent_accepted: bool
):
    participant = register_participant(
        telegram_id=telegram_id,
        full_name=full_name,
        phone=phone,
        consent_accepted=consent_accepted,
    )
    referral_link = ReferralLink.objects.get(participant=participant)
    return participant.full_name, referral_link.code


def get_participant_referral_data(*, telegram_id: str):
    participant = Participant.objects.filter(telegram_id=telegram_id).first()
    if not participant:
        return None

    referral_link = ReferralLink.objects.get(participant=participant)
    return participant.full_name, referral_link.code


def get_participant_by_telegram_id(*, telegram_id: str):
    return Participant.objects.filter(telegram_id=telegram_id).first()


def update_participant_profile(*, telegram_id: str, company: str = "", position: str = ""):
    participant = Participant.objects.get(telegram_id=telegram_id)
    if company:
        participant.company = company
    if position:
        participant.position = position
    participant.save(update_fields=["company", "position"])
    return participant


def get_participant_dashboard_data(*, telegram_id: str):
    participant = Participant.objects.filter(telegram_id=telegram_id).first()
    if not participant:
        return None

    referral_link = ReferralLink.objects.get(participant=participant)
    accrued = BonusLedgerEntry.objects.filter(participant=participant).values_list("amount", flat=True)
    spent = BonusSpendRequest.objects.filter(
        participant=participant,
        status=SPEND_REQUEST_STATUS_PENDING,
    ).values_list("amount", flat=True)

    balance = sum(accrued, Decimal("0.00")) - sum(spent, Decimal("0.00"))

    invited_leads = list(
        ReferralLead.objects.filter(referral_link=referral_link)
        .exclude(client_name=participant.full_name, client_phone=participant.phone)
        .order_by("-created_at")
        .values_list("client_name", "status", "created_at")
    )

    return {
        "full_name": participant.full_name,
        "referral_code": referral_link.code,
        "balance": balance,
        "invited_leads": invited_leads,
    }


def get_participant_requests_data(*, telegram_id: str):
    participant = Participant.objects.filter(telegram_id=telegram_id).first()
    if not participant:
        return None

    own_leads = list(
        ReferralLead.objects.filter(
            referral_link__isnull=True,
            client_name=participant.full_name,
            client_phone=participant.phone,
        )
        .order_by("-created_at")
        .values_list("client_company", "status", "created_at")
    )
    spend_requests = list(
        BonusSpendRequest.objects.filter(participant=participant)
        .order_by("-created_at")
        .values_list("comment", "status", "created_at")
    )

    return {
        "own_leads": own_leads,
        "spend_requests": spend_requests,
    }


def get_participant_bonus_history_data(*, telegram_id: str):
    participant = Participant.objects.filter(telegram_id=telegram_id).first()
    if not participant:
        return None

    accruals = list(
        BonusLedgerEntry.objects.filter(participant=participant)
        .order_by("-created_at")
        .values_list("amount", "reason", "created_at")
    )
    spendings = list(
        BonusSpendRequest.objects.filter(
            participant=participant,
            status=SPEND_REQUEST_STATUS_APPROVED,
        )
        .order_by("-created_at")
        .values_list("amount", "comment", "created_at")
    )

    return {
        "accruals": accruals,
        "spendings": spendings,
    }


def create_referral_lead(
    *,
    referral_code: str | None,
    client_name: str,
    client_phone: str,
    client_company: str = "",
):
    referral_link = ReferralLink.objects.filter(code=referral_code).first() if referral_code else None
    lead = ReferralLead.objects.create(
        referral_link=referral_link,
        client_company=client_company,
        client_name=client_name,
        client_phone=client_phone,
    )
    company_line = f"\nКомпания: {client_company}" if client_company else ""
    telegram_notifications.send_admin_notification(
        f"Новая заявка:{company_line}\nКонтакт: {client_name}\nТелефон: {client_phone}"
    )
    return lead


def create_bonus_spend_request(*, participant, amount: Decimal, comment: str = ""):
    return BonusSpendRequest.objects.create(
        participant=participant,
        amount=amount,
        comment=comment,
        status=SPEND_REQUEST_STATUS_PENDING,
    )


def create_self_lead_request(*, telegram_id: str, product: str, quantity: str, comment: str):
    participant = Participant.objects.get(telegram_id=telegram_id)
    participant_company = participant.company or "не указана"
    participant_position = participant.position or "не указана"
    admin_comment = (
        f"Участник программы: {participant.full_name}, {participant.phone}\n"
        f"Компания участника: {participant_company}\n"
        f"Должность: {participant_position}\n"
        f"Продукция: {product}\n"
        f"Тираж: {quantity}\n"
        f"Комментарий: {comment}"
    )
    lead = ReferralLead.objects.create(
        referral_link=None,
        client_company=participant.company,
        client_name=participant.full_name,
        client_phone=participant.phone,
        admin_comment=admin_comment,
    )
    telegram_notifications.send_admin_notification(
        f"Новая заявка от участника.\n"
        f"Участник: {participant.full_name}\n"
        f"Телефон: {participant.phone}\n"
        f"Компания: {participant_company}\n"
        f"Должность: {participant_position}\n"
        f"Продукция: {product}\n"
        f"Тираж: {quantity}\n"
        f"Комментарий: {comment}"
    )
    return lead
