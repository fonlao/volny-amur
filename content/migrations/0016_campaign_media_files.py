from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("content", "0015_telegram_state_and_payment_notice")]
    operations = [
        migrations.AlterField(model_name="newslettercampaign", name="image_1", field=models.FileField(blank=True, help_text="JPG, PNG или WebP", upload_to="newsletter/%Y/%m/", verbose_name="Изображение 1")),
        migrations.AlterField(model_name="newslettercampaign", name="image_2", field=models.FileField(blank=True, help_text="Необязательно", upload_to="newsletter/%Y/%m/", verbose_name="Изображение 2")),
        migrations.AlterField(model_name="newslettercampaign", name="image_3", field=models.FileField(blank=True, help_text="Необязательно", upload_to="newsletter/%Y/%m/", verbose_name="Изображение 3")),
    ]
