import json
import re
import base64
import urllib.error
import urllib.request
from threading import Thread
from pathlib import Path
from decimal import Decimal
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.http import FileResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import SiteSettings, Advantage, Route, Guide, Lead, Payment

def send_lead_notification(name, phone, route):
    send_mail(
        f"Новая заявка: {route}",
        f"Имя: {name}\nТелефон: {phone}\nМаршрут: {route}",
        settings.DEFAULT_FROM_EMAIL,
        [settings.LEAD_NOTIFICATION_EMAIL],
        fail_silently=True,
    )

def yookassa_request(method, path, payload=None, idempotence_key=None):
    if not settings.YOOKASSA_SHOP_ID or not settings.YOOKASSA_SECRET_KEY:
        raise RuntimeError("ЮKassa не настроена")
    credentials = base64.b64encode(
        f"{settings.YOOKASSA_SHOP_ID}:{settings.YOOKASSA_SECRET_KEY}".encode("utf-8")
    ).decode("ascii")
    headers = {
        "Authorization": f"Basic {credentials}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if idempotence_key:
        headers["Idempotence-Key"] = str(idempotence_key)
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        f"https://api.yookassa.ru/v3{path}",
        data=body,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        try:
            details = json.loads(error.read().decode("utf-8"))
            description = details.get("description") or details.get("code")
        except (ValueError, UnicodeDecodeError):
            description = None
        raise RuntimeError(description or "ЮKassa отклонила запрос") from error
    except urllib.error.URLError as error:
        raise RuntimeError("Нет соединения с ЮKassa") from error

def update_payment_from_yookassa(payment):
    if not payment.yookassa_id:
        return payment
    remote = yookassa_request("GET", f"/payments/{payment.yookassa_id}")
    payment.status = remote.get("status", payment.status)
    payment.paid = bool(remote.get("paid", False))
    cancellation = remote.get("cancellation_details") or {}
    payment.cancellation_reason = cancellation.get("reason", "")
    payment.save(update_fields=("status", "paid", "cancellation_reason", "updated_at"))
    if payment.paid:
        Lead.objects.get_or_create(
            payment=payment,
            defaults={
                "name": payment.name,
                "phone": payment.phone,
                "email": payment.email,
                "route": payment.route,
                "status": "confirmed",
                "notes": "Создано автоматически после оплаты через ЮKassa.",
            },
        )
    return payment

def frontend(request):
    index = Path(settings.BASE_DIR) / "dist" / "index.html"
    return FileResponse(index.open("rb"), content_type="text/html")

@require_http_methods(["GET"])
def content_api(request):
    site = SiteSettings.objects.first() or SiteSettings.objects.create()
    return JsonResponse({
        "site": {f.name: getattr(site, f.name) for f in site._meta.fields if f.name != "id"},
        "advantages": list(Advantage.objects.filter(is_active=True).values("title", "text", "icon")),
        "routes": list(Route.objects.filter(is_active=True).values("title", "tag", "days", "level", "price", "season", "text", "visual_style", "image_url")),
        "guides": list(Guide.objects.filter(is_active=True).values("name", "role", "experience", "quote", "initials", "color", "image_url")),
    }, json_dumps_params={"ensure_ascii": False})

@csrf_exempt
@require_http_methods(["POST"])
def request_api(request):
    try:
        data = json.loads(request.body)
        name, phone, email, route = (str(data.get(k, "")).strip() for k in ("name", "phone", "email", "route"))
        if len(name) < 2 or not re.fullmatch(r"[+0-9 ()-]{7,}", phone) or not route:
            return JsonResponse({"message": "Проверьте имя и номер телефона."}, status=400)
        Lead.objects.create(name=name, phone=phone, email=email, route=route)
        if settings.EMAIL_HOST_PASSWORD and settings.LEAD_NOTIFICATION_EMAIL:
            Thread(target=send_lead_notification, args=(name, phone, route), daemon=True).start()
        return JsonResponse({"ok": True, "message": "Заявка принята"}, status=201)
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({"message": "Некорректные данные."}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def payment_create_api(request):
    try:
        data = json.loads(request.body)
        name, phone, email, route = (
            str(data.get(key, "")).strip() for key in ("name", "phone", "email", "route")
        )
        if (
            len(name) < 2
            or not re.fullmatch(r"[+0-9 ()-]{7,}", phone)
            or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)
            or not route
        ):
            return JsonResponse({"message": "Проверьте имя, телефон и e-mail."}, status=400)

        site = SiteSettings.objects.first() or SiteSettings.objects.create()
        amount = Decimal(site.booking_deposit)
        if amount <= 0:
            return JsonResponse({"message": "Онлайн-оплата временно недоступна."}, status=503)

        customer_ip = request.META.get("HTTP_X_REAL_IP") or request.META.get("REMOTE_ADDR")
        recent_payments = Payment.objects.filter(
            customer_ip=customer_ip,
            created_at__gte=timezone.now() - timedelta(minutes=10),
        ).count()
        if recent_payments >= 5:
            return JsonResponse(
                {"message": "Слишком много попыток. Повторите через несколько минут."},
                status=429,
            )

        payment = Payment.objects.create(
            name=name,
            phone=phone,
            email=email,
            route=route,
            amount=amount,
            customer_ip=customer_ip,
        )
        base_url = settings.PUBLIC_BASE_URL.rstrip("/") or f"{request.scheme}://{request.get_host()}"
        remote = yookassa_request(
            "POST",
            "/payments",
            {
                "amount": {"value": f"{amount:.2f}", "currency": "RUB"},
                "capture": True,
                "confirmation": {
                    "type": "redirect",
                    "return_url": f"{base_url}/?payment={payment.public_id}",
                },
                "description": f"Предоплата за маршрут «{route}»"[:128],
                "metadata": {"payment_public_id": str(payment.public_id)},
            },
            payment.idempotence_key,
        )
        payment.yookassa_id = remote["id"]
        payment.status = remote.get("status", "pending")
        payment.paid = bool(remote.get("paid", False))
        payment.save(update_fields=("yookassa_id", "status", "paid", "updated_at"))
        confirmation_url = (remote.get("confirmation") or {}).get("confirmation_url")
        if not confirmation_url:
            raise RuntimeError("ЮKassa не вернула страницу оплаты")
        return JsonResponse(
            {
                "confirmation_url": confirmation_url,
                "payment_id": str(payment.public_id),
            },
            status=201,
        )
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({"message": "Некорректные данные."}, status=400)
    except RuntimeError as error:
        if "payment" in locals():
            payment.status = "error"
            payment.cancellation_reason = str(error)[:160]
            payment.save(update_fields=("status", "cancellation_reason", "updated_at"))
        return JsonResponse({"message": str(error)}, status=502)

@require_http_methods(["GET"])
def payment_status_api(request, public_id):
    try:
        payment = Payment.objects.get(public_id=public_id)
    except Payment.DoesNotExist:
        return JsonResponse({"message": "Платёж не найден."}, status=404)
    try:
        update_payment_from_yookassa(payment)
    except RuntimeError:
        payment.refresh_from_db()
    return JsonResponse({
        "status": payment.status,
        "paid": payment.paid,
        "amount": f"{payment.amount:.2f}",
        "route": payment.route,
    })

@csrf_exempt
@require_http_methods(["POST"])
def payment_webhook_api(request):
    try:
        event = json.loads(request.body)
        yookassa_id = str((event.get("object") or {}).get("id", ""))
        if not yookassa_id:
            return JsonResponse({"ok": True})
        payment = Payment.objects.filter(yookassa_id=yookassa_id).first()
        if payment:
            update_payment_from_yookassa(payment)
        return JsonResponse({"ok": True})
    except (ValueError, json.JSONDecodeError, RuntimeError):
        return JsonResponse({"ok": True})
