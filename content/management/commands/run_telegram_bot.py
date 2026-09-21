from django.core.management.base import BaseCommand, CommandError
from content.telegram_bot import run_polling
from django.conf import settings


class Command(BaseCommand):
    help = "Запускает Telegram-бота Вольного Амура в long polling режиме"

    def handle(self, *args, **options):
        if not settings.TELEGRAM_BOT_TOKEN:
            raise CommandError("TELEGRAM_BOT_TOKEN не задан")
        self.stdout.write(self.style.SUCCESS("Telegram bot polling started"))
        run_polling()
