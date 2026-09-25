from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("content", "0014_telegram")]
    operations = [
        migrations.AddField(
            model_name="telegramcontact",
            name="state",
            field=models.CharField(
                choices=[
                    ("idle", "Ожидает команду"),
                    ("route_proposal", "Вводит предложение маршрута"),
                    ("admin_message", "Пишет администратору"),
                ],
                default="idle",
                max_length=30,
                verbose_name="Состояние диалога",
            ),
        ),
        migrations.AddField(
            model_name="telegramreservation",
            name="payment_notified_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Уведомление об оплате отправлено"),
        ),
    ]
