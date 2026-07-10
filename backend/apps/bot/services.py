import secrets
from decimal import Decimal

from apps.bonuses.models import BonusSpendRequest
from apps.notifications import telegram as telegram_notifications
from apps.referrals.models import ReferralLead
from apps.referrals.models import ReferralLink
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


def create_referral_lead(*, referral_code: str | None, client_name: str, client_phone: str):
    referral_link = ReferralLink.objects.filter(code=referral_code).first() if referral_code else None
    lead = ReferralLead.objects.create(
        referral_link=referral_link,
        client_name=client_name,
        client_phone=client_phone,
    )
    telegram_notifications.send_admin_notification(f"Новая заявка: {client_name}, {client_phone}")
    return lead


def create_bonus_spend_request(*, participant, amount: Decimal):
    return BonusSpendRequest.objects.create(
        participant=participant,
        amount=amount,
        status="pending",
    )


def create_self_lead_request(*, telegram_id: str, product: str, quantity: str, comment: str):
    participant = Participant.objects.get(telegram_id=telegram_id)
    referral_link = ReferralLink.objects.get(participant=participant)
    admin_comment = (
        f"Продукция: {product}\n"
        f"Тираж: {quantity}\n"
        f"Комментарий: {comment}"
    )
    lead = ReferralLead.objects.create(
        referral_link=referral_link,
        client_name=participant.full_name,
        client_phone=participant.phone,
        admin_comment=admin_comment,
    )
    telegram_notifications.send_admin_notification(
        f"Новая заявка от участника {participant.full_name}, {participant.phone}. "
        f"Продукция: {product}. Тираж: {quantity}. Комментарий: {comment}"
    )
    return lead
