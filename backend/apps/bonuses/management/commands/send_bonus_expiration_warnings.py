from django.core.management.base import BaseCommand

from apps.bonuses.services import (
    get_upcoming_expiration_warning_preview,
    send_upcoming_expiration_warnings,
)


class Command(BaseCommand):
    help = "Отправляет участникам предупреждения о скором сгорании бонусов."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Показать, кому уйдут предупреждения, без отправки.",
        )

    def handle(self, *args, **options):
        if options["dry_run"]:
            preview_items = get_upcoming_expiration_warning_preview()
            self.stdout.write(self.style.WARNING(f"Dry run: предупреждений к отправке: {len(preview_items)}"))
            for item in preview_items:
                self.stdout.write(
                    f"- {item.participant.full_name} ({item.participant.telegram_id}) -> "
                    f"{item.remaining_amount:.2f} до {item.entry.expires_at:%d.%m.%Y}"
                )
            return

        warnings_sent = send_upcoming_expiration_warnings()
        self.stdout.write(self.style.SUCCESS(f"Отправлено предупреждений: {warnings_sent}"))
