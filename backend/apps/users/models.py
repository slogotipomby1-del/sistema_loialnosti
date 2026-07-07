from django.db import models


class Participant(models.Model):
    telegram_id = models.CharField(max_length=64, unique=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=32)
    consent_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.full_name
