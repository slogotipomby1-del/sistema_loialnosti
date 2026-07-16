from django.core.management.base import BaseCommand

from apps.bonuses.services import send_upcoming_expiration_warnings


class Command(BaseCommand):
    help = "Отправляет участникам предупреждения о скором сгорании бонусов."

    def handle(self, *args, **options):
        warnings_sent = send_upcoming_expiration_warnings()
        self.stdout.write(self.style.SUCCESS(f"Отправлено предупреждений: {warnings_sent}"))
