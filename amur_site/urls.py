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
    path("api/requests", views.request_api),
    path("api/payments/create", views.payment_create_api),
    path("api/payments/status/<uuid:public_id>", views.payment_status_api),
    path("api/payments/webhook", views.payment_webhook_api),
    re_path(r"^assets/(?P<path>.*)$", serve, {"document_root": settings.BASE_DIR / "dist" / "assets"}),
    re_path(r"^(?!admin/|api/|assets/).*$", views.frontend),
]
