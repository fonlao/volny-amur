from django.contrib import admin
from django.utils.html import format_html
from .models import SiteSettings, Advantage, Route, RouteDeparture, Guide, Lead, Payment, Visit, CustomerProfile

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
