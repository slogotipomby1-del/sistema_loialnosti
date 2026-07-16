from decimal import Decimal

from django.db import models

from apps.common.choices import (
    BONUS_ENTRY_TYPE_ACCRUAL,
    BONUS_ENTRY_TYPE_CHOICES,
    SPEND_REQUEST_STATUS_CHOICES,
    SPEND_REQUEST_STATUS_PENDING,
)
from apps.referrals.models import ReferralLead
from apps.users.models import Participant


class BonusLedgerEntry(models.Model):
    participant = models.ForeignKey(
        Participant,
        verbose_name="Участник",
        on_delete=models.CASCADE,
        related_name="bonus_entries",
    )
    lead = models.ForeignKey(
        ReferralLead,
        verbose_name="Реферальная заявка",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="bonus_entries",
    )
    entry_type = models.CharField(
        "Тип операции",
        max_length=32,
        choices=BONUS_ENTRY_TYPE_CHOICES,
        default=BONUS_ENTRY_TYPE_ACCRUAL,
    )
    amount = models.DecimalField("Сумма", max_digits=10, decimal_places=2)
    reason = models.CharField("Основание", max_length=255)
    expires_at = models.DateField("Сгорает", null=True, blank=True)
    expiration_warning_sent_at = models.DateTimeField("Предупреждение отправлено", null=True, blank=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Начисление бонусов"
        verbose_name_plural = "Начисления бонусов"

    def __str__(self) -> str:
        return f"{self.participant.full_name} — {self.amount:.2f}"


class BonusSpendRequest(models.Model):
    participant = models.ForeignKey(
        Participant,
        verbose_name="Участник",
        on_delete=models.CASCADE,
        related_name="spend_requests",
    )
    amount = models.DecimalField("Сумма", max_digits=10, decimal_places=2)
    comment = models.CharField("Подарок или комментарий", max_length=255, blank=True, default="")
    status = models.CharField(
        "Статус",
        max_length=32,
        choices=SPEND_REQUEST_STATUS_CHOICES,
        default=SPEND_REQUEST_STATUS_PENDING,
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Запрос на списание бонусов"
        verbose_name_plural = "Запросы на списание бонусов"

    def __str__(self) -> str:
        label = self.comment or "Запрос на списание"
        return f"{self.participant.full_name} — {label} — {Decimal(self.amount):.2f}"
