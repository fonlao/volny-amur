import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0011_lead_user_payment_user_customerprofile"),
    ]

    operations = [
        migrations.CreateModel(
            name="NewsletterCampaign",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("subject", models.CharField(max_length=200, verbose_name="Тема письма")),
                ("body", models.TextField(verbose_name="Текст письма")),
                ("status", models.CharField(choices=[("draft", "Черновик"), ("sending", "Отправляется"), ("sent", "Отправлена"), ("partial", "Отправлена частично"), ("error", "Ошибка")], default="draft", max_length=20, verbose_name="Статус")),
                ("sent_count", models.PositiveSmallIntegerField(default=0, verbose_name="Успешно отправлено")),
                ("failed_count", models.PositiveSmallIntegerField(default=0, verbose_name="Ошибок")),
                ("last_error", models.TextField(blank=True, verbose_name="Последняя ошибка")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создана")),
                ("sent_at", models.DateTimeField(blank=True, null=True, verbose_name="Отправлена")),
            ],
            options={"verbose_name": "Рассылка", "verbose_name_plural": "Новостные рассылки", "ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="NewsletterSubscriber",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(max_length=254, unique=True, verbose_name="E-mail")),
                ("consent", models.BooleanField(default=False, verbose_name="Согласие на рекламную рассылку")),
                ("is_active", models.BooleanField(default=True, verbose_name="Подписка активна")),
                ("consent_text", models.TextField(verbose_name="Текст согласия")),
                ("consent_ip", models.GenericIPAddressField(blank=True, null=True, verbose_name="IP при подписке")),
                ("consent_user_agent", models.CharField(blank=True, max_length=500, verbose_name="Браузер при подписке")),
                ("consent_at", models.DateTimeField(auto_now_add=True, verbose_name="Согласие получено")),
                ("unsubscribed_at", models.DateTimeField(blank=True, null=True, verbose_name="Дата отписки")),
                ("unsubscribe_token", models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Токен отписки")),
            ],
            options={"verbose_name": "Подписчик", "verbose_name_plural": "Подписчики рассылки", "ordering": ("-consent_at",)},
        ),
    ]
