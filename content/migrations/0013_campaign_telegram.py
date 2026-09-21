from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("content", "0012_newsletter")]
    operations = [
        migrations.AddField(model_name="newslettercampaign", name="image_1", field=models.URLField(blank=True, help_text="Прямая HTTPS-ссылка на изображение", verbose_name="Изображение 1")),
        migrations.AddField(model_name="newslettercampaign", name="image_2", field=models.URLField(blank=True, help_text="Необязательно", verbose_name="Изображение 2")),
        migrations.AddField(model_name="newslettercampaign", name="image_3", field=models.URLField(blank=True, help_text="Необязательно", verbose_name="Изображение 3")),
        migrations.AddField(model_name="newslettercampaign", name="telegram_enabled", field=models.BooleanField(default=True, verbose_name="Отправлять в Telegram")),
        migrations.AddField(model_name="newslettercampaign", name="miniapp_url", field=models.URLField(blank=True, verbose_name="Ссылка на мини-приложение")),
        migrations.AddField(model_name="newslettercampaign", name="telegram_sent_count", field=models.PositiveSmallIntegerField(default=0, verbose_name="Отправлено в Telegram")),
    ]
