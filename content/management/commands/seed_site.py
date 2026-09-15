from django.core.management.base import BaseCommand
from datetime import timedelta
from django.utils import timezone
from content.models import SiteSettings, Advantage, Route, RouteDeparture, Guide

class Command(BaseCommand):
    help = "Создаёт начальное содержимое сайта"

    def handle(self, *args, **options):
        SiteSettings.objects.get_or_create(pk=1)
        advantages = [
            ("Знаем каждый поворот", "Живём на Дальнем Востоке и ходим этими тропами больше 12 лет.", "⌖"),
            ("Маленькие группы", "До 8 человек — чтобы слышать тайгу, а не шум туристической толпы.", "♢"),
            ("Безопасность в деталях", "Спутниковая связь, проверенное снаряжение и сертифицированные гиды.", "⊕"),
            ("Бережно к природе", "Следуем принципу «не оставляй следов» и поддерживаем заповедники края.", "≈"),
        ]
        for order, (title, text, icon) in enumerate(advantages, 1):
            Advantage.objects.get_or_create(title=title, defaults={"text": text, "icon": icon, "order": order})
        routes = [
            ("Шантарские острова", "Экспедиция", "8 дней", "Средний", "от 168 000 ₽", "июль — сентябрь", "Киты в Охотском море, лежбища тюленей и дикие бухты архипелага. Добираемся катером и живём в тёплом глэмпинге.", "ocean", "Комсомольск-на-Амуре", 50.549923, 137.007948),
            ("Дуссе-Алинь", "Треккинг", "10 дней", "Сложный", "от 124 000 ₽", "июнь — август", "Горные озёра, водопады и каменные цирки заповедного хребта. Настоящая автономная экспедиция с опытным проводником.", "mountain", "Посёлок Бриакан", 50.711744, 134.066509),
            ("По следам тигра", "Экотур", "5 дней", "Лёгкий", "от 76 000 ₽", "февраль — март", "Зимняя тайга Сихотэ-Алиня, следы амурского тигра и ночёвки на кордоне. Наблюдаем природу бережно и с безопасной дистанции.", "forest", "Хабаровск", 48.480223, 135.071917),
            ("Амурские протоки", "Сплав", "4 дня", "Лёгкий", "от 49 000 ₽", "май — октябрь", "Неторопливое путешествие на каяках среди островов великой реки, рыбацких сёл и дальневосточных закатов.", "river", "Хабаровск, набережная Амура", 48.472607, 135.052664),
        ]
        for order, row in enumerate(routes, 1):
            title, tag, days, level, price, season, text, visual_style, start_location, start_latitude, start_longitude = row
            Route.objects.get_or_create(title=title, defaults={"tag": tag, "days": days, "level": level, "price": price, "season": season, "text": text, "visual_style": visual_style, "start_location": start_location, "start_latitude": start_latitude, "start_longitude": start_longitude, "order": order})
        guides = [
            ("Артём Волков", "Экспедиционный гид", "12 лет в тайге", "Знает Шантары как свой дом", "АВ", "green"),
            ("Лидия Ким", "Гид-натуралист", "Кандидат биологических наук", "Переводит язык дикой природы", "ЛК", "blue"),
            ("Михаил Серов", "Горный проводник", "38 восхождений", "В горах выбирает верный темп", "МС", "dark"),
        ]
        for order, row in enumerate(guides, 1):
            name, role, experience, quote, initials, color = row
            Guide.objects.get_or_create(name=name, defaults={"role": role, "experience": experience, "quote": quote, "initials": initials, "color": color, "order": order})
        today = timezone.localdate()
        departure_specs = [
            ("Шантарские острова", 28, 8, 8, 3, "open", "Сбор группы в Комсомольске-на-Амуре"),
            ("Амурские протоки", 12, 4, 8, 6, "few", "Подходит для первого знакомства с краем"),
            ("Дуссе-Алинь", 48, 10, 8, 2, "open", "Требуется опыт многодневных походов"),
            ("По следам тигра", 72, 5, 6, 6, "waitlist", "Можно оставить заявку в лист ожидания"),
        ]
        for title, offset, duration, capacity, booked, status, note in departure_specs:
            route = Route.objects.filter(title=title).first()
            if route:
                start_date = today + timedelta(days=offset)
                RouteDeparture.objects.get_or_create(
                    route=route,
                    start_date=start_date,
                    defaults={
                        "end_date": start_date + timedelta(days=duration - 1),
                        "capacity": capacity,
                        "booked_places": booked,
                        "status": status,
                        "note": note,
                    },
                )
        self.stdout.write(self.style.SUCCESS("Начальное содержимое создано"))
