from django.core.management.base import BaseCommand

from apps.bonuses.services import expire_bonus_entries


class Command(BaseCommand):
    help = "Создаёт записи о сгорании бонусов, срок действия которых истёк."

    def handle(self, *args, **options):
        expired_count = expire_bonus_entries()
        self.stdout.write(self.style.SUCCESS(f"Сгорело начислений: {expired_count}"))
