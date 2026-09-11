from django.contrib import admin
from .models import SiteSettings, Advantage, Route, Guide, Lead, Payment

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
    list_display = ("title", "tag", "days", "price", "order", "is_active")
    search_fields = ("title", "text")

@admin.register(Guide)
class GuideAdmin(OrderedAdmin):
    list_display = ("name", "role", "experience", "order", "is_active")

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "route", "status", "payment", "created_at")
    list_filter = ("status", "route", "created_at")
    search_fields = ("name", "phone", "route")
    list_editable = ("status",)
    readonly_fields = ("created_at",)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("public_id", "name", "route", "amount", "status", "paid", "created_at")
    list_filter = ("status", "paid", "route", "created_at")
    search_fields = ("public_id", "yookassa_id", "name", "phone", "email", "route")
    readonly_fields = (
        "public_id", "yookassa_id", "idempotence_key", "name", "phone", "email",
        "route", "amount", "status", "paid", "cancellation_reason", "customer_ip", "created_at", "updated_at",
    )
    actions = ("refresh_statuses",)

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
