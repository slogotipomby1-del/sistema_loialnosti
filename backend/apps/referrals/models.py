from django.db import models

from apps.common.choices import LEAD_STATUS_CHOICES, LEAD_STATUS_NEW
from apps.users.models import Participant


class ReferralLink(models.Model):
    code = models.CharField("Код ссылки", max_length=64, unique=True)
    participant = models.OneToOneField(
        Participant,
        on_delete=models.CASCADE,
        related_name="referral_link",
        verbose_name="Участник",
    )

    class Meta:
        verbose_name = "Реферальная ссылка"
        verbose_name_plural = "Реферальные ссылки"

    def __str__(self) -> str:
        return f"{self.participant.full_name} — {self.code}"


class ReferralLead(models.Model):
    referral_link = models.ForeignKey(
        ReferralLink,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="leads",
        verbose_name="Реферальная ссылка",
    )
    client_company = models.CharField("Компания клиента", max_length=255, blank=True, default="")
    client_name = models.CharField("Имя клиента", max_length=255)
    client_phone = models.CharField("Телефон клиента", max_length=32)
    client_position = models.CharField("Должность клиента", max_length=255, blank=True, default="")
    client_email = models.EmailField("Email клиента", blank=True, default="")
    product_interest = models.CharField("Интерес к продукции", max_length=255, blank=True, default="")
    quantity = models.CharField("Тираж", max_length=255, blank=True, default="")
    budget = models.CharField("Бюджет", max_length=255, blank=True, default="")
    deadline = models.CharField("Срок", max_length=255, blank=True, default="")
    status = models.CharField(
        "Статус",
        max_length=32,
        choices=LEAD_STATUS_CHOICES,
        default=LEAD_STATUS_NEW,
    )
    admin_comment = models.TextField("Комментарий администратора", blank=True)
    rejection_reason = models.TextField("Причина отказа", blank=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Реферальная заявка"
        verbose_name_plural = "Реферальные заявки"

    def __str__(self) -> str:
        lead_type = "Своя заявка" if not self.referral_link else "Реферал"
        return f"{self.client_name} — {lead_type}"
