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
    client_name = models.CharField(max_length=255)
    client_phone = models.CharField(max_length=32)
    status = models.CharField(
        max_length=32,
        choices=LEAD_STATUS_CHOICES,
        default=LEAD_STATUS_NEW,
    )
    admin_comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.client_name
