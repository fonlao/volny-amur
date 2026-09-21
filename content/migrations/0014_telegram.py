from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("content", "0013_campaign_telegram")]
    operations = [
        migrations.CreateModel(
            name="TelegramContact",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("chat_id", models.BigIntegerField(unique=True, verbose_name="Chat ID")),
                ("username", models.CharField(blank=True, max_length=100, verbose_name="Username")),
                ("first_name", models.CharField(blank=True, max_length=120, verbose_name="Имя")),
                ("is_active", models.BooleanField(default=True, verbose_name="Получает сообщения")),
                ("started_at", models.DateTimeField(auto_now_add=True, verbose_name="Первый запуск")),
                ("last_seen_at", models.DateTimeField(auto_now=True, verbose_name="Последняя активность")),
            ],
            options={"verbose_name": "Подписчик Telegram", "verbose_name_plural": "Подписчики Telegram", "ordering": ("-last_seen_at",)},
        ),
        migrations.CreateModel(
            name="TelegramReservation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("new", "Новая"), ("paid", "Оплачена"), ("cancelled", "Отменена")], default="new", max_length=20, verbose_name="Статус")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создана")),
                ("contact", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reservations", to="content.telegramcontact", verbose_name="Подписчик")),
                ("payment", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="content.payment", verbose_name="Платёж")),
                ("route", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="telegram_reservations", to="content.route", verbose_name="Маршрут")),
            ],
            options={"verbose_name": "Запись из Telegram", "verbose_name_plural": "Записи из Telegram", "ordering": ("-created_at",)},
        ),
    ]
