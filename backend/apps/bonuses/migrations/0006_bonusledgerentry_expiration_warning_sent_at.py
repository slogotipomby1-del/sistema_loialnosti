from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bonuses", "0005_bonusledgerentry_entry_type_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="bonusledgerentry",
            name="expiration_warning_sent_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
