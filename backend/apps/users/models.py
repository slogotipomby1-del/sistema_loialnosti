from django.core.exceptions import ValidationError
from django.db import models, transaction


class Participant(models.Model):
    telegram_id = models.CharField("Telegram ID", max_length=64, unique=True)
    full_name = models.CharField("Участник", max_length=255)
    phone = models.CharField("Телефон", max_length=32)
    company = models.CharField("Компания", max_length=255, blank=True, default="")
    position = models.CharField("Должность", max_length=255, blank=True, default="")
    is_primary_contact = models.BooleanField("Основной контакт", default=False)
    consent_accepted = models.BooleanField("Согласие получено", default=False)
    created_at = models.DateTimeField("Дата регистрации", auto_now_add=True)

    class Meta:
        verbose_name = "Участник"
        verbose_name_plural = "Участники"

    def __str__(self) -> str:
        return self.full_name

    def clean(self) -> None:
        self.company = (self.company or "").strip()
        self.position = (self.position or "").strip()

        if self.is_primary_contact and not self.company:
            raise ValidationError({"company": "Нельзя назначить основного контакта без компании."})

    def save(self, *args, **kwargs):
        self.full_clean()

        with transaction.atomic():
            super().save(*args, **kwargs)

            if self.is_primary_contact and self.company:
                (
                    Participant.objects.filter(company=self.company, is_primary_contact=True)
                    .exclude(pk=self.pk)
                    .update(is_primary_contact=False)
                )
