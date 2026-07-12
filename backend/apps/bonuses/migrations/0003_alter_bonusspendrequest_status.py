from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bonuses", "0002_bonusspendrequest_comment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bonusspendrequest",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "На рассмотрении"),
                    ("approved", "Подтверждена"),
                    ("rejected", "Отклонена"),
                ],
                default="pending",
                max_length=32,
            ),
        ),
    ]
