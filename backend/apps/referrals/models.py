from django.db import models

from apps.common.choices import LEAD_STATUS_CHOICES, LEAD_STATUS_NEW
from apps.users.models import Participant


class ReferralLink(models.Model):
    code = models.CharField(max_length=64, unique=True)
    participant = models.OneToOneField(
        Participant,
        on_delete=models.CASCADE,
        related_name="referral_link",
    )

    class Meta:
        verbose_name = "Реферальная ссылка"
        verbose_name_plural = "Реферальные ссылки"

    def __str__(self) -> str:
        return self.code


class ReferralLead(models.Model):
    referral_link = models.ForeignKey(
        ReferralLink,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="leads",
    )
    client_company = models.CharField(max_length=255, blank=True, default="")
    client_name = models.CharField(max_length=255)
    client_phone = models.CharField(max_length=32)
    client_position = models.CharField(max_length=255, blank=True, default="")
    client_email = models.EmailField(blank=True, default="")
    product_interest = models.CharField(max_length=255, blank=True, default="")
    quantity = models.CharField(max_length=255, blank=True, default="")
    budget = models.CharField(max_length=255, blank=True, default="")
    deadline = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(
        max_length=32,
        choices=LEAD_STATUS_CHOICES,
        default=LEAD_STATUS_NEW,
    )
    admin_comment = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Реферальная заявка"
        verbose_name_plural = "Реферальные заявки"

    def __str__(self) -> str:
        return self.client_name
