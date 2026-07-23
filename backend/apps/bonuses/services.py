from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.bonuses.models import BonusLedgerEntry, BonusSpendRequest
from apps.common.choices import (
    BONUS_ENTRY_TYPE_ACCRUAL,
    BONUS_ENTRY_TYPE_EXPIRATION,
    SPEND_REQUEST_STATUS_APPROVED,
)
from apps.notifications.telegram import send_telegram_message
from apps.users.models import Participant


WARNING_DAYS_BEFORE_EXPIRATION = 30


@dataclass
class BonusLot:
    entry: BonusLedgerEntry
    remaining_amount: Decimal


@dataclass
class BonusExpirationPreview:
    participant: Participant
    entry: BonusLedgerEntry
    remaining_amount: Decimal


def _build_bonus_lots(*, participant: Participant) -> list[BonusLot]:
    accrual_entries = list(
        BonusLedgerEntry.objects.filter(
            participant=participant,
            entry_type=BONUS_ENTRY_TYPE_ACCRUAL,
            amount__gt=0,
        ).order_by("created_at", "id")
    )
    lots = [BonusLot(entry=entry, remaining_amount=entry.amount) for entry in accrual_entries]

    consumptions: list[tuple] = []

    for created_at, entry_id, amount in (
        BonusLedgerEntry.objects.filter(participant=participant, amount__lt=0)
        .exclude(entry_type=BONUS_ENTRY_TYPE_ACCRUAL)
        .order_by("created_at", "id")
        .values_list("created_at", "id", "amount")
    ):
        consumptions.append((created_at, f"ledger-{entry_id}", abs(amount)))

    for created_at, request_id, amount in (
        BonusSpendRequest.objects.filter(
            participant=participant,
            status=SPEND_REQUEST_STATUS_APPROVED,
        )
        .order_by("created_at", "id")
        .values_list("created_at", "id", "amount")
    ):
        consumptions.append((created_at, f"spend-{request_id}", amount))

    consumptions.sort(key=lambda item: (item[0], item[1]))

    for _, _, consumption_amount in consumptions:
        remaining_to_allocate = consumption_amount
        for lot in lots:
            if remaining_to_allocate <= 0:
                break
            if lot.remaining_amount <= 0:
                continue

            allocated_amount = min(lot.remaining_amount, remaining_to_allocate)
            lot.remaining_amount -= allocated_amount
            remaining_to_allocate -= allocated_amount

    return lots


def get_upcoming_expiration_warning_preview(*, today: date | None = None) -> list[BonusExpirationPreview]:
    today = today or timezone.localdate()
    warning_date = today + timedelta(days=WARNING_DAYS_BEFORE_EXPIRATION)
    preview_items: list[BonusExpirationPreview] = []

    participant_ids = (
        BonusLedgerEntry.objects.filter(
            entry_type=BONUS_ENTRY_TYPE_ACCRUAL,
            expires_at=warning_date,
            expiration_warning_sent_at__isnull=True,
        )
        .values_list("participant_id", flat=True)
        .distinct()
    )

    for participant in Participant.objects.filter(id__in=participant_ids):
        for lot in _build_bonus_lots(participant=participant):
            if (
                lot.entry.expires_at != warning_date
                or lot.entry.expiration_warning_sent_at is not None
                or lot.remaining_amount <= 0
            ):
                continue

            preview_items.append(
                BonusExpirationPreview(
                    participant=participant,
                    entry=lot.entry,
                    remaining_amount=lot.remaining_amount,
                )
            )

    return preview_items


def send_upcoming_expiration_warnings(*, today: date | None = None) -> int:
    warnings_sent = 0

    for item in get_upcoming_expiration_warning_preview(today=today):
        send_telegram_message(
            chat_id=item.participant.telegram_id,
            text=(
                f"Напоминаем: {item.remaining_amount:.2f} бонуса(ов) "
                f"сгорят {item.entry.expires_at:%d.%m.%Y}.\n"
                "Если хотите использовать их раньше — оставьте заявку в разделе подарков."
            ),
        )
        item.entry.expiration_warning_sent_at = timezone.now()
        item.entry.save(update_fields=["expiration_warning_sent_at"])
        warnings_sent += 1

    return warnings_sent


def get_expiring_bonus_preview(*, today: date | None = None) -> list[BonusExpirationPreview]:
    today = today or timezone.localdate()
    preview_items: list[BonusExpirationPreview] = []

    participant_ids = (
        BonusLedgerEntry.objects.filter(
            entry_type=BONUS_ENTRY_TYPE_ACCRUAL,
            expires_at__lt=today,
        )
        .values_list("participant_id", flat=True)
        .distinct()
    )

    for participant in Participant.objects.filter(id__in=participant_ids):
        for lot in _build_bonus_lots(participant=participant):
            if not lot.entry.expires_at or lot.entry.expires_at >= today or lot.remaining_amount <= 0:
                continue

            preview_items.append(
                BonusExpirationPreview(
                    participant=participant,
                    entry=lot.entry,
                    remaining_amount=lot.remaining_amount,
                )
            )

    return preview_items


def expire_bonus_entries(*, today: date | None = None) -> int:
    expired_count = 0

    for item in get_expiring_bonus_preview(today=today):
        with transaction.atomic():
            BonusLedgerEntry.objects.create(
                participant=item.participant,
                lead=item.entry.lead,
                entry_type=BONUS_ENTRY_TYPE_EXPIRATION,
                amount=-item.remaining_amount,
                reason=(
                    f"Сгорание остатка по начислению #{item.entry.id} "
                    f"от {item.entry.created_at:%d.%m.%Y}"
                ),
            )
        expired_count += 1

    return expired_count
