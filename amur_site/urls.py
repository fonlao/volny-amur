from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve
from content import views
from django.conf import settings

admin.site.site_header = "Вольный Амур — управление сайтом"
admin.site.site_title = "Вольный Амур"
admin.site.index_title = "Содержание и заявки"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/content", views.content_api),
    path("api/auth/csrf", views.auth_csrf_api),
    path("api/auth/me", views.auth_me_api),
    path("api/auth/register", views.auth_register_api),
    path("api/auth/login", views.auth_login_api),
    path("api/auth/logout", views.auth_logout_api),
    path("api/departures", views.departures_api),
    path("api/requests", views.request_api),
    path("api/newsletter/subscribe", views.newsletter_subscribe_api),
    path("api/newsletter/unsubscribe/<uuid:token>", views.newsletter_unsubscribe_api),
    path("api/payments/create", views.payment_create_api),
    path("api/payments/status/<uuid:public_id>", views.payment_status_api),
    path("api/payments/webhook", views.payment_webhook_api),
    re_path(r"^assets/(?P<path>.*)$", serve, {"document_root": settings.BASE_DIR / "dist" / "assets"}),
    re_path(r"^(?!admin/|api/|assets/).*$", views.frontend),
]
