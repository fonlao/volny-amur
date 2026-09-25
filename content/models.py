from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import uuid

class SiteSettings(models.Model):
    hero_eyebrow = models.CharField("Надзаголовок", max_length=160, default="Хабаровский край · Дальний Восток")
    hero_title = models.CharField("Главный заголовок", max_length=160, default="Там, где начинается настоящее")
    hero_text = models.TextField("Описание", default="Авторские путешествия в места, где тайга встречается с океаном, а каждый день становится историей.")
    advantages_title = models.CharField("Заголовок преимуществ", max_length=160, default="Дальше — только настоящее")
    routes_title = models.CharField("Заголовок маршрутов", max_length=160, default="Выберите своё направление")
    guides_title = models.CharField("Заголовок команды", max_length=160, default="Люди, которым доверяют путь")
    request_title = models.CharField("Заголовок формы", max_length=160, default="Ваше приключение начинается здесь")
    request_text = models.TextField("Текст формы", default="Оставьте контакты — наш эксперт позвонит и поможет выбрать идеальный маршрут.")
    email = models.EmailField("E-mail", default="hello@volniyamur.ru")
    phone = models.CharField("Телефон", max_length=40, default="+7 4212 99-00-48")
    booking_deposit = models.DecimalField("Предоплата за бронирование", max_digits=10, decimal_places=2, default=5000)

    class Meta:
        verbose_name = "Общие настройки"
        verbose_name_plural = "Общие настройки"

    def __str__(self): return "Тексты и контакты сайта"

class OrderedActiveModel(models.Model):
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показывать на сайте", default=True)
    class Meta:
        abstract = True
        ordering = ("order", "id")

class Advantage(OrderedActiveModel):
    title = models.CharField("Название", max_length=120)
    text = models.TextField("Описание")
    icon = models.CharField("Символ", max_length=8, default="⌖")
    class Meta(OrderedActiveModel.Meta):
        verbose_name = "Преимущество"
        verbose_name_plural = "Преимущества"
    def __str__(self): return self.title

class Route(OrderedActiveModel):
    title = models.CharField("Название", max_length=120)
    tag = models.CharField("Тип путешествия", max_length=40)
    days = models.CharField("Продолжительность", max_length=40)
    level = models.CharField("Сложность", max_length=40)
    price = models.CharField("Цена", max_length=80)
    season = models.CharField("Сезон", max_length=80)
    text = models.TextField("Описание")
    visual_style = models.CharField("Стиль иллюстрации", max_length=20, choices=[("ocean","Океан"),("mountain","Горы"),("forest","Лес"),("river","Река")], default="forest")
    image_url = models.URLField("Ссылка на фотографию", blank=True, help_text="Необязательно: прямая https-ссылка на изображение")
    start_location = models.CharField("Точка начала маршрута", max_length=160, blank=True)
    start_latitude = models.DecimalField(
        "Широта точки старта", max_digits=9, decimal_places=6, null=True, blank=True,
        help_text="Например: 48.480223",
    )
    start_longitude = models.DecimalField(
        "Долгота точки старта", max_digits=9, decimal_places=6, null=True, blank=True,
        help_text="Например: 135.071917",
    )
    class Meta(OrderedActiveModel.Meta):
        verbose_name = "Маршрут"
        verbose_name_plural = "Маршруты"
    def __str__(self): return self.title


class RouteDeparture(models.Model):
    STATUS = [
        ("open", "Есть места"),
        ("few", "Осталось мало мест"),
        ("waitlist", "Лист ожидания"),
        ("closed", "Набор закрыт"),
    ]
    route = models.ForeignKey(Route, verbose_name="Маршрут", on_delete=models.CASCADE, related_name="departures")
    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата окончания")
    capacity = models.PositiveSmallIntegerField("Всего мест", default=8)
    booked_places = models.PositiveSmallIntegerField("Занято мест", default=0)
    status = models.CharField("Статус", max_length=12, choices=STATUS, default="open")
    note = models.CharField("Примечание", max_length=160, blank=True)
    is_published = models.BooleanField("Показывать на сайте", default=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)

    class Meta:
        ordering = ("start_date", "route__order", "route__title")
        verbose_name = "Заезд"
        verbose_name_plural = "Календарь заездов"
        constraints = [
            models.UniqueConstraint(fields=("route", "start_date"), name="unique_route_departure_date"),
        ]

    def clean(self):
        errors = {}
        if self.end_date and self.start_date and self.end_date < self.start_date:
            errors["end_date"] = "Дата окончания не может быть раньше даты начала."
        if self.booked_places > self.capacity:
            errors["booked_places"] = "Число занятых мест не может превышать вместимость."
        if errors:
            raise ValidationError(errors)

    @property
    def available_places(self):
        return max(self.capacity - self.booked_places, 0)

    def __str__(self):
        return f"{self.route.title} — {self.start_date:%d.%m.%Y}"


class Visit(models.Model):
    day = models.DateField("День")
    path = models.CharField("Страница", max_length=255)
    session_key = models.CharField("Анонимная сессия", max_length=40)
    created_at = models.DateTimeField("Время визита", auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Посещение"
        verbose_name_plural = "Посещения сайта"
        indexes = [
            models.Index(fields=("day", "path")),
            models.Index(fields=("day", "session_key")),
        ]

    def __str__(self):
        return f"{self.day} — {self.path}"


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, verbose_name="Пользователь", on_delete=models.CASCADE, related_name="customer_profile")
    phone = models.CharField("Телефон", max_length=40, blank=True)
    created_at = models.DateTimeField("Дата регистрации", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)

    class Meta:
        verbose_name = "Профиль клиента"
        verbose_name_plural = "Профили клиентов"

    def __str__(self):
        return self.user.get_full_name() or self.user.email or self.user.username

class Guide(OrderedActiveModel):
    name = models.CharField("Имя", max_length=100)
    role = models.CharField("Специализация", max_length=100)
    experience = models.CharField("Опыт", max_length=100)
    quote = models.CharField("Короткая цитата", max_length=180)
    initials = models.CharField("Инициалы", max_length=4)
    color = models.CharField("Цвет карточки", max_length=20, choices=[("green","Зелёный"),("blue","Голубой"),("dark","Тёмный")], default="green")
    image_url = models.URLField("Ссылка на фотографию", blank=True, help_text="Необязательно: прямая https-ссылка на изображение")
    class Meta(OrderedActiveModel.Meta):
        verbose_name = "Специалист"
        verbose_name_plural = "Наши специалисты"
    def __str__(self): return self.name

class Lead(models.Model):
    STATUS = [("new","Новая"),("contacted","Связались"),("confirmed","Подтверждена"),("closed","Закрыта")]
    name = models.CharField("Имя", max_length=100)
    phone = models.CharField("Телефон", max_length=40)
    email = models.EmailField("E-mail", blank=True)
    route = models.CharField("Маршрут", max_length=120)
    status = models.CharField("Статус", max_length=20, choices=STATUS, default="new")
    notes = models.TextField("Заметки менеджера", blank=True)
    payment = models.OneToOneField("Payment", verbose_name="Платёж", on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, verbose_name="Клиент", on_delete=models.SET_NULL, null=True, blank=True, related_name="travel_leads")
    departure = models.ForeignKey("RouteDeparture", verbose_name="Выбранный заезд", on_delete=models.SET_NULL, null=True, blank=True, related_name="leads")
    notification_sent_at = models.DateTimeField("Уведомление отправлено", null=True, blank=True)
    notification_attempted_at = models.DateTimeField("Последняя попытка отправки", null=True, blank=True)
    notification_error = models.TextField("Ошибка отправки", blank=True)
    created_at = models.DateTimeField("Дата заявки", auto_now_add=True)
    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
    def __str__(self): return f"{self.name} — {self.route}"

class Payment(models.Model):
    STATUS = [
        ("created", "Создан локально"),
        ("pending", "Ожидает оплаты"),
        ("succeeded", "Оплачен"),
        ("canceled", "Отменён"),
        ("error", "Ошибка"),
    ]
    public_id = models.UUIDField("Номер бронирования", default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, verbose_name="Клиент", on_delete=models.SET_NULL, null=True, blank=True, related_name="travel_payments")
    yookassa_id = models.CharField("ID платежа ЮKassa", max_length=64, blank=True, unique=True, null=True)
    idempotence_key = models.UUIDField("Ключ идемпотентности", default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField("Имя", max_length=100)
    phone = models.CharField("Телефон", max_length=40)
    email = models.EmailField("E-mail")
    route = models.CharField("Маршрут", max_length=120)
    amount = models.DecimalField("Сумма", max_digits=10, decimal_places=2)
    status = models.CharField("Статус", max_length=20, choices=STATUS, default="created")
    paid = models.BooleanField("Оплачен", default=False)
    cancellation_reason = models.CharField("Причина отмены", max_length=160, blank=True)
    customer_ip = models.GenericIPAddressField("IP клиента", null=True, blank=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи ЮKassa"

    def __str__(self):
        return f"{self.public_id} — {self.amount} ₽"


class NewsletterSubscriber(models.Model):
    email = models.EmailField("E-mail", unique=True)
    consent = models.BooleanField("Согласие на рекламную рассылку", default=False)
    is_active = models.BooleanField("Подписка активна", default=True)
    consent_text = models.TextField("Текст согласия")
    consent_ip = models.GenericIPAddressField("IP при подписке", null=True, blank=True)
    consent_user_agent = models.CharField("Браузер при подписке", max_length=500, blank=True)
    consent_at = models.DateTimeField("Согласие получено", auto_now_add=True)
    unsubscribed_at = models.DateTimeField("Дата отписки", null=True, blank=True)
    unsubscribe_token = models.UUIDField("Токен отписки", default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        ordering = ("-consent_at",)
        verbose_name = "Подписчик"
        verbose_name_plural = "Подписчики рассылки"

    def __str__(self):
        return self.email


class NewsletterCampaign(models.Model):
    STATUS = [
        ("draft", "Черновик"),
        ("sending", "Отправляется"),
        ("sent", "Отправлена"),
        ("partial", "Отправлена частично"),
        ("error", "Ошибка"),
    ]
    subject = models.CharField("Тема письма", max_length=200)
    body = models.TextField("Текст письма")
    image_1 = models.FileField("Изображение 1", upload_to="newsletter/%Y/%m/", blank=True, help_text="JPG, PNG или WebP")
    image_2 = models.FileField("Изображение 2", upload_to="newsletter/%Y/%m/", blank=True, help_text="Необязательно")
    image_3 = models.FileField("Изображение 3", upload_to="newsletter/%Y/%m/", blank=True, help_text="Необязательно")
    telegram_enabled = models.BooleanField("Отправлять в Telegram", default=True)
    miniapp_url = models.URLField("Ссылка на мини-приложение", blank=True)
    telegram_sent_count = models.PositiveSmallIntegerField("Отправлено в Telegram", default=0)
    status = models.CharField("Статус", max_length=20, choices=STATUS, default="draft")
    sent_count = models.PositiveSmallIntegerField("Успешно отправлено", default=0)
    failed_count = models.PositiveSmallIntegerField("Ошибок", default=0)
    last_error = models.TextField("Последняя ошибка", blank=True)
    created_at = models.DateTimeField("Создана", auto_now_add=True)
    sent_at = models.DateTimeField("Отправлена", null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Рассылка"
        verbose_name_plural = "Новостные рассылки"

    def __str__(self):
        return self.subject


class TelegramContact(models.Model):
    STATE = [
        ("idle", "Ожидает команду"),
        ("route_proposal", "Вводит предложение маршрута"),
        ("admin_message", "Пишет администратору"),
    ]
    chat_id = models.BigIntegerField("Chat ID", unique=True)
    username = models.CharField("Username", max_length=100, blank=True)
    first_name = models.CharField("Имя", max_length=120, blank=True)
    state = models.CharField("Состояние диалога", max_length=30, choices=STATE, default="idle")
    is_active = models.BooleanField("Получает сообщения", default=True)
    started_at = models.DateTimeField("Первый запуск", auto_now_add=True)
    last_seen_at = models.DateTimeField("Последняя активность", auto_now=True)

    class Meta:
        ordering = ("-last_seen_at",)
        verbose_name = "Подписчик Telegram"
        verbose_name_plural = "Подписчики Telegram"

    def __str__(self):
        return str(self.first_name or self.username or self.chat_id)


class TelegramReservation(models.Model):
    STATUS = [("new", "Новая"), ("paid", "Оплачена"), ("cancelled", "Отменена")]
    contact = models.ForeignKey(TelegramContact, verbose_name="Подписчик", on_delete=models.CASCADE, related_name="reservations")
    route = models.ForeignKey(Route, verbose_name="Маршрут", on_delete=models.PROTECT, related_name="telegram_reservations")
    status = models.CharField("Статус", max_length=20, choices=STATUS, default="new")
    payment = models.ForeignKey(Payment, verbose_name="Платёж", on_delete=models.SET_NULL, null=True, blank=True)
    payment_notified_at = models.DateTimeField("Уведомление об оплате отправлено", null=True, blank=True)
    created_at = models.DateTimeField("Создана", auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Запись из Telegram"
        verbose_name_plural = "Записи из Telegram"

    def __str__(self):
        return f"{self.contact} — {self.route}"
