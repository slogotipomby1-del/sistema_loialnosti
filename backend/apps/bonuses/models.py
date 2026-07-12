from django.db import models

from apps.common.choices import (
    SPEND_REQUEST_STATUS_CHOICES,
    SPEND_REQUEST_STATUS_PENDING,
)
from apps.referrals.models import ReferralLead
from apps.users.models import Participant


class BonusLedgerEntry(models.Model):
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name="bonus_entries",
    )
    lead = models.ForeignKey(
        ReferralLead,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="bonus_entries",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Начисление бонусов"
        verbose_name_plural = "Начисления бонусов"


class BonusSpendRequest(models.Model):
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name="spend_requests",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    comment = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(
        max_length=32,
        choices=SPEND_REQUEST_STATUS_CHOICES,
        default=SPEND_REQUEST_STATUS_PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Запрос на списание бонусов"
        verbose_name_plural = "Запросы на списание бонусов"
