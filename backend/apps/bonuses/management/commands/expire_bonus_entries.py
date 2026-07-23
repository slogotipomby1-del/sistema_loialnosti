from django.core.management.base import BaseCommand

from apps.bonuses.services import expire_bonus_entries, get_expiring_bonus_preview


class Command(BaseCommand):
    help = "Создаёт записи о сгорании бонусов, срок действия которых истёк."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Показать, что сгорит, без создания операций.",
        )

    def handle(self, *args, **options):
        if options["dry_run"]:
            preview_items = get_expiring_bonus_preview()
            self.stdout.write(self.style.WARNING(f"Dry run: начислений к сгоранию: {len(preview_items)}"))
            for item in preview_items:
                self.stdout.write(
                    f"- {item.participant.full_name} ({item.participant.telegram_id}) -> "
                    f"{item.remaining_amount:.2f} от начисления #{item.entry.id}"
                )
            return

        expired_count = expire_bonus_entries()
        self.stdout.write(self.style.SUCCESS(f"Сгорело начислений: {expired_count}"))
