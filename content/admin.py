from django.contrib import admin
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.utils import timezone
from django.utils.html import format_html
from .models import (
    SiteSettings, Advantage, Route, RouteDeparture, Guide, Lead, Payment, Visit,
    CustomerProfile, NewsletterSubscriber, NewsletterCampaign,
)

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Главный экран", {"fields": ("hero_eyebrow", "hero_title", "hero_text")}),
        ("Заголовки разделов", {"fields": ("advantages_title", "routes_title", "guides_title")}),
        ("Форма заявки", {"fields": ("request_title", "request_text", "email", "phone")}),
        ("Онлайн-оплата", {"fields": ("booking_deposit",)}),
    )
    def has_add_permission(self, request): return not SiteSettings.objects.exists()
    def has_delete_permission(self, request, obj=None): return False

class OrderedAdmin(admin.ModelAdmin):
    list_display = ("__str__", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)

@admin.register(Advantage)
class AdvantageAdmin(OrderedAdmin): pass

@admin.register(Route)
class RouteAdmin(OrderedAdmin):
    list_display = ("title", "start_location", "tag", "days", "price", "order", "is_active")
    search_fields = ("title", "text", "start_location")
    fieldsets = (
        ("Основная информация", {"fields": ("title", "tag", "days", "level", "price", "season", "text")}),
        ("Изображение", {"fields": ("visual_style", "image_url")}),
        ("Начало маршрута на карте", {"fields": ("start_location", "start_latitude", "start_longitude")}),
        ("Публикация", {"fields": ("order", "is_active")}),
    )

@admin.register(RouteDeparture)
class RouteDepartureAdmin(admin.ModelAdmin):
    list_display = ("route", "start_date", "end_date", "availability", "status_badge", "is_published")
    list_filter = ("status", "is_published", "start_date", "route")
    search_fields = ("route__title", "note")
    list_editable = ("is_published",)
    date_hierarchy = "start_date"
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Заезд", {"fields": ("route", "start_date", "end_date", "status", "is_published")}),
        ("Места", {"fields": ("capacity", "booked_places", "note")}),
        ("Служебная информация", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Свободно")
    def availability(self, obj):
        return f"{obj.available_places} из {obj.capacity}"

    @admin.display(description="Статус", ordering="status")
    def status_badge(self, obj):
        classes = {
            "open": ("status-success", "Есть места"),
            "few": ("status-waiting", "Мало мест"),
            "waitlist": ("status-neutral", "Лист ожидания"),
            "closed": ("status-error", "Закрыт"),
        }
        css_class, label = classes[obj.status]
        return format_html('<span class="status-pill {}">{}</span>', css_class, label)

@admin.register(Guide)
class GuideAdmin(OrderedAdmin):
    list_display = ("name", "role", "experience", "order", "is_active")

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "user", "route", "departure", "status", "notification_state", "payment", "created_at")
    list_filter = ("status", "notification_sent_at", "route", "created_at")
    search_fields = ("name", "phone", "route")
    list_editable = ("status",)
    readonly_fields = ("created_at", "notification_sent_at", "notification_attempted_at", "notification_error")
    actions = ("resend_notifications",)

    @admin.display(description="Уведомление")
    def notification_state(self, obj):
        if obj.notification_sent_at:
            return format_html('<span class="status-pill status-success">{}</span>', "Отправлено")
        if obj.notification_error:
            return format_html('<span class="status-pill status-error">{}</span>', "Ошибка")
        return format_html('<span class="status-pill status-waiting">{}</span>', "Ожидает")

    @admin.action(description="Отправить уведомление повторно")
    def resend_notifications(self, request, queryset):
        from .views import send_lead_notification
        sent = sum(1 for lead in queryset if send_lead_notification(lead.pk))
        self.message_user(request, f"Отправлено уведомлений: {sent} из {queryset.count()}")

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("public_id", "name", "route", "amount", "payment_state", "created_at")
    list_filter = ("status", "paid", "route", "created_at")
    search_fields = ("public_id", "yookassa_id", "name", "phone", "email", "route")
    readonly_fields = (
        "public_id", "yookassa_id", "idempotence_key", "user", "name", "phone", "email",
        "route", "amount", "status", "paid", "cancellation_reason", "customer_ip", "created_at", "updated_at",
    )
    actions = ("refresh_statuses",)

    @admin.display(description="Состояние", ordering="status")
    def payment_state(self, obj):
        if obj.paid:
            return format_html('<span class="status-pill status-success">{}</span>', "Оплачен")
        if obj.status == "canceled":
            return format_html('<span class="status-pill status-error">{}</span>', "Отменён")
        if obj.status == "error":
            return format_html('<span class="status-pill status-error">{}</span>', "Ошибка")
        if obj.status == "pending":
            return format_html('<span class="status-pill status-waiting">{}</span>', "Ожидает")
        return format_html('<span class="status-pill status-neutral">{}</span>', obj.get_status_display())

    @admin.action(description="Обновить статус выбранных платежей из ЮKassa")
    def refresh_statuses(self, request, queryset):
        from .views import update_payment_from_yookassa
        updated = 0
        for payment in queryset.exclude(yookassa_id__isnull=True):
            try:
                update_payment_from_yookassa(payment)
                updated += 1
            except RuntimeError:
                continue
        self.message_user(request, f"Обновлено платежей: {updated}")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("day", "path", "created_at")
    list_filter = ("day", "path")
    search_fields = ("path",)
    readonly_fields = ("day", "path", "session_key", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "created_at")
    search_fields = ("user__email", "user__first_name", "user__last_name", "phone")
    readonly_fields = ("created_at", "updated_at")


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "consent_state", "is_active", "consent_at", "unsubscribed_at")
    list_filter = ("is_active", "consent", "consent_at")
    search_fields = ("email", "consent_ip")
    list_editable = ("is_active",)
    readonly_fields = (
        "email", "consent", "consent_text", "consent_ip", "consent_user_agent",
        "consent_at", "unsubscribed_at", "unsubscribe_token",
    )

    @admin.display(description="Согласие")
    def consent_state(self, obj):
        css_class = "status-success" if obj.consent else "status-error"
        label = "Получено" if obj.consent else "Нет"
        return format_html('<span class="status-pill {}">{}</span>', css_class, label)

    def has_add_permission(self, request):
        return False


@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(admin.ModelAdmin):
    list_display = ("subject", "status_badge", "sent_count", "failed_count", "created_at", "sent_at")
    list_filter = ("status", "created_at")
    search_fields = ("subject", "body")
    readonly_fields = ("status", "sent_count", "failed_count", "last_error", "created_at", "sent_at")
    actions = ("send_to_subscribers",)

    @admin.display(description="Статус", ordering="status")
    def status_badge(self, obj):
        classes = {
            "draft": "status-neutral",
            "sending": "status-waiting",
            "sent": "status-success",
            "partial": "status-waiting",
            "error": "status-error",
        }
        return format_html(
            '<span class="status-pill {}">{}</span>',
            classes.get(obj.status, "status-neutral"),
            obj.get_status_display(),
        )

    @admin.action(description="Отправить выбранную рассылку (не более 80 адресатов)")
    def send_to_subscribers(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Выберите одну рассылку.", level="error")
            return
        campaign = queryset.first()
        if campaign.status != "draft":
            self.message_user(request, "Повторно можно отправить только копию рассылки в статусе «Черновик».", level="error")
            return

        subscribers = list(
            NewsletterSubscriber.objects.filter(consent=True, is_active=True)
            .order_by("consent_at")[:80]
        )
        if not subscribers:
            self.message_user(request, "Нет активных подписчиков с подтверждённым согласием.", level="warning")
            return

        campaign.status = "sending"
        campaign.last_error = ""
        campaign.save(update_fields=("status", "last_error"))
        sent = 0
        errors = []
        base_url = settings.PUBLIC_BASE_URL.rstrip("/")
        connection = get_connection()
        try:
            connection.open()
            for subscriber in subscribers:
                unsubscribe_url = f"{base_url}/api/newsletter/unsubscribe/{subscriber.unsubscribe_token}"
                body = (
                    f"{campaign.body.strip()}\n\n"
                    "Вы получили это письмо, потому что согласились на рекламную рассылку "
                    "«Вольного Амура».\n"
                    f"Отписаться: {unsubscribe_url}"
                )
                message = EmailMultiAlternatives(
                    subject=campaign.subject,
                    body=body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[subscriber.email],
                    connection=connection,
                    headers={
                        "List-Unsubscribe": f"<{unsubscribe_url}>",
                        "Precedence": "bulk",
                    },
                )
                try:
                    sent += message.send(fail_silently=False)
                except Exception as error:
                    errors.append(f"{subscriber.email}: {str(error)[:180]}")
        finally:
            connection.close()

        failed = len(subscribers) - sent
        campaign.sent_count = sent
        campaign.failed_count = failed
        campaign.last_error = "\n".join(errors)[:4000]
        campaign.sent_at = timezone.now()
        campaign.status = "sent" if failed == 0 else ("partial" if sent else "error")
        campaign.save(update_fields=("sent_count", "failed_count", "last_error", "sent_at", "status"))
        self.message_user(request, f"Рассылка завершена: отправлено {sent}, ошибок {failed}.")
