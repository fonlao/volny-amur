import json
import re
import base64
import logging
import urllib.error
import urllib.request
from threading import Thread
from pathlib import Path
from decimal import Decimal
from datetime import timedelta
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import close_old_connections, transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import render
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import SiteSettings, Advantage, Route, RouteDeparture, Guide, Lead, Payment, NewsletterSubscriber

logger = logging.getLogger(__name__)

def serialize_user(user):
    profile = getattr(user, "customer_profile", None)
    return {
        "id": user.pk,
        "email": user.email,
        "name": user.get_full_name() or user.username,
        "phone": profile.phone if profile else "",
    }

@ensure_csrf_cookie
@require_http_methods(["GET"])
def auth_csrf_api(request):
    return JsonResponse({"ok": True})

@require_http_methods(["GET"])
def auth_me_api(request):
    if not request.user.is_authenticated or request.user.is_staff:
        return JsonResponse({"authenticated": False})
    leads = Lead.objects.filter(user=request.user).select_related("departure")
    payments = Payment.objects.filter(user=request.user)
    return JsonResponse({
        "authenticated": True,
        "user": serialize_user(request.user),
        "leads": [
            {
                "id": lead.pk,
                "route": lead.route,
                "status": lead.get_status_display(),
                "departure": (
                    f"{lead.departure.start_date:%d.%m.%Y} — {lead.departure.end_date:%d.%m.%Y}"
                    if lead.departure_id else "Дата уточняется"
                ),
                "created_at": timezone.localtime(lead.created_at).strftime("%d.%m.%Y"),
            }
            for lead in leads
        ],
        "payments": [
            {
                "id": str(payment.public_id),
                "route": payment.route,
                "amount": f"{payment.amount:.2f}",
                "status": payment.get_status_display(),
                "paid": payment.paid,
                "created_at": timezone.localtime(payment.created_at).strftime("%d.%m.%Y"),
            }
            for payment in payments
        ],
    }, json_dumps_params={"ensure_ascii": False})

@require_http_methods(["POST"])
def auth_register_api(request):
    try:
        data = json.loads(request.body)
        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip().lower()
        phone = str(data.get("phone", "")).strip()
        password = str(data.get("password", ""))
        if len(name) < 2 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            return JsonResponse({"message": "Введите имя и корректный e-mail."}, status=400)
        if phone and not re.fullmatch(r"[+0-9 ()-]{7,}", phone):
            return JsonResponse({"message": "Проверьте номер телефона."}, status=400)
        if User.objects.filter(email__iexact=email).exists():
            return JsonResponse({"message": "Пользователь с таким e-mail уже зарегистрирован."}, status=409)
        candidate = User(username=email, email=email, first_name=name)
        validate_password(password, candidate)
        candidate.set_password(password)
        candidate.save()
        from .models import CustomerProfile
        CustomerProfile.objects.create(user=candidate, phone=phone)
        Lead.objects.filter(user__isnull=True, email__iexact=email).update(user=candidate)
        Payment.objects.filter(user__isnull=True, email__iexact=email).update(user=candidate)
        login(request, candidate)
        return JsonResponse({"authenticated": True, "user": serialize_user(candidate)}, status=201)
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({"message": "Некорректные данные."}, status=400)
    except Exception as error:
        from django.core.exceptions import ValidationError
        if isinstance(error, ValidationError):
            return JsonResponse({"message": " ".join(error.messages)}, status=400)
        raise

@require_http_methods(["POST"])
def auth_login_api(request):
    try:
        data = json.loads(request.body)
        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))
        user = authenticate(request, username=email, password=password)
        if user is None or user.is_staff:
            return JsonResponse({"message": "Неверный e-mail или пароль."}, status=401)
        login(request, user)
        return JsonResponse({"authenticated": True, "user": serialize_user(user)})
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({"message": "Некорректные данные."}, status=400)

@require_http_methods(["POST"])
def auth_logout_api(request):
    logout(request)
    return JsonResponse({"authenticated": False})

def send_lead_notification(lead_id):
    close_old_connections()
    try:
        lead = Lead.objects.get(pk=lead_id)
        lead.notification_attempted_at = timezone.now()
        lead.notification_error = ""
        lead.save(update_fields=("notification_attempted_at", "notification_error"))

        if not settings.LEAD_NOTIFICATION_EMAIL:
            raise RuntimeError("Не задан LEAD_NOTIFICATION_EMAIL")
        if not settings.EMAIL_HOST_PASSWORD:
            raise RuntimeError("Не задан пароль SMTP")

        base_url = settings.PUBLIC_BASE_URL.rstrip("/")
        admin_url = f"{base_url}/admin/content/lead/{lead.pk}/change/" if base_url else ""
        created = timezone.localtime(lead.created_at).strftime("%d.%m.%Y %H:%M")
        subject = f"Новая заявка с сайта: {lead.route}"
        body = (
            "На сайте «Вольный Амур» оставлена новая заявка.\n\n"
            f"Имя: {lead.name}\n"
            f"Телефон: {lead.phone}\n"
            f"E-mail: {lead.email or 'не указан'}\n"
            f"Маршрут: {lead.route}\n"
        )
        if lead.departure_id:
            body += f"Заезд: {lead.departure.start_date:%d.%m.%Y} — {lead.departure.end_date:%d.%m.%Y}\n"
        body += (
            f"Дата: {created}\n"
            f"Источник: {'оплата ЮKassa' if lead.payment_id else 'форма сайта'}\n"
        )
        if admin_url:
            body += f"\nОткрыть заявку в админке:\n{admin_url}\n"

        message = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.LEAD_NOTIFICATION_EMAIL],
            reply_to=[lead.email] if lead.email else None,
        )
        result = message.send(fail_silently=False)
        if result != 1:
            raise RuntimeError("Почтовый сервер не подтвердил отправку")

        lead.notification_sent_at = timezone.now()
        lead.notification_error = ""
        lead.save(update_fields=("notification_sent_at", "notification_error"))
        logger.info("Lead notification sent for lead_id=%s", lead.pk)
        return True
    except Exception as error:
        logger.exception("Lead notification failed for lead_id=%s", lead_id)
        Lead.objects.filter(pk=lead_id).update(
            notification_attempted_at=timezone.now(),
            notification_error=str(error)[:1000],
        )
        return False
    finally:
        close_old_connections()

def queue_lead_notification(lead_id):
    Thread(target=send_lead_notification, args=(lead_id,), daemon=True).start()

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
        lead, created = Lead.objects.get_or_create(
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
        if created:
            transaction.on_commit(lambda: queue_lead_notification(lead.pk))
        try:
            from .models import TelegramReservation
            from .telegram_bot import send_message
            reservations = TelegramReservation.objects.filter(payment=payment, payment_notified_at__isnull=True).select_related("contact", "route")
            for reservation in reservations:
                send_message(
                    reservation.contact.chat_id,
                    f"✅ Вы успешно оплатили бронь на группу «{reservation.route.title}».\n"
                    "Место подтверждено. Мы свяжемся с вами с деталями поездки.",
                    {"inline_keyboard": [[{"text": "Меню", "callback_data": "menu"}]]},
                )
                reservation.payment_notified_at = timezone.now()
                reservation.status = "paid"
                reservation.save(update_fields=("payment_notified_at", "status"))
        except Exception:
            logger.exception("Telegram payment notification failed for payment_id=%s", payment.pk)
    return payment

def frontend(request):
    index = Path(settings.BASE_DIR) / "dist" / "index.html"
    return FileResponse(index.open("rb"), content_type="text/html")


def miniapp(request):
    return render(request, "miniapp.html")

@require_http_methods(["GET"])
def content_api(request):
    site = SiteSettings.objects.first() or SiteSettings.objects.create()
    return JsonResponse({
        "site": {f.name: getattr(site, f.name) for f in site._meta.fields if f.name != "id"},
        "advantages": list(Advantage.objects.filter(is_active=True).values("title", "text", "icon")),
        "routes": list(Route.objects.filter(is_active=True).values(
            "title", "tag", "days", "level", "price", "season", "text",
            "visual_style", "image_url", "start_location", "start_latitude", "start_longitude",
        )),
        "guides": list(Guide.objects.filter(is_active=True).values("name", "role", "experience", "quote", "initials", "color", "image_url")),
    }, json_dumps_params={"ensure_ascii": False})

@require_http_methods(["GET"])
def departures_api(request):
    today = timezone.localdate()
    departures = RouteDeparture.objects.filter(
        is_published=True,
        start_date__gte=today,
    ).select_related("route")
    data = []
    for departure in departures:
        data.append({
            "id": departure.pk,
            "route": departure.route.title,
            "route_style": departure.route.visual_style,
            "start_date": departure.start_date.isoformat(),
            "end_date": departure.end_date.isoformat(),
            "status": departure.status,
            "available_places": departure.available_places,
            "capacity": departure.capacity,
            "note": departure.note,
        })
    return JsonResponse({"departures": data}, json_dumps_params={"ensure_ascii": False})

@csrf_exempt
@require_http_methods(["POST"])
def request_api(request):
    try:
        data = json.loads(request.body)
        name, phone, email, route = (str(data.get(k, "")).strip() for k in ("name", "phone", "email", "route"))
        departure_id = data.get("departure_id")
        departure = None
        if departure_id:
            try:
                departure = RouteDeparture.objects.get(
                    pk=int(departure_id),
                    route__title=route,
                    is_published=True,
                    start_date__gte=timezone.localdate(),
                )
                if departure.status == "closed" or (
                    departure.status in ("open", "few") and departure.available_places == 0
                ):
                    raise RouteDeparture.DoesNotExist
            except (RouteDeparture.DoesNotExist, TypeError, ValueError):
                return JsonResponse({"message": "Выбранный заезд больше недоступен. Выберите другую дату."}, status=400)
        if len(name) < 2 or not re.fullmatch(r"[+0-9 ()-]{7,}", phone) or not route:
            return JsonResponse({"message": "Проверьте имя и номер телефона."}, status=400)
        lead = Lead.objects.create(name=name, phone=phone, email=email, route=route, departure=departure, user=request.user if request.user.is_authenticated and not request.user.is_staff else None)
        transaction.on_commit(lambda: queue_lead_notification(lead.pk))
        return JsonResponse({"ok": True, "message": "Заявка принята"}, status=201)
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({"message": "Некорректные данные."}, status=400)


NEWSLETTER_CONSENT_TEXT = (
    "Я согласен(на) получать новости и рекламные предложения «Вольного Амура» "
    "по электронной почте. Отписаться можно в любой момент."
)


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return (forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")) or None


@csrf_exempt
@require_http_methods(["POST"])
def newsletter_subscribe_api(request):
    try:
        data = json.loads(request.body)
        email = str(data.get("email", "")).strip().lower()
        consent = data.get("consent") is True
        validate_email(email)
        if not consent:
            return JsonResponse({"message": "Необходимо согласие на получение рекламной рассылки."}, status=400)

        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={
                "consent": True,
                "is_active": True,
                "consent_text": NEWSLETTER_CONSENT_TEXT,
                "consent_ip": client_ip(request),
                "consent_user_agent": request.META.get("HTTP_USER_AGENT", "")[:500],
            },
        )
        if not created:
            subscriber.consent = True
            subscriber.is_active = True
            subscriber.consent_text = NEWSLETTER_CONSENT_TEXT
            subscriber.consent_ip = client_ip(request)
            subscriber.consent_user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]
            subscriber.consent_at = timezone.now()
            subscriber.unsubscribed_at = None
            subscriber.save(update_fields=(
                "consent", "is_active", "consent_text", "consent_ip",
                "consent_user_agent", "consent_at", "unsubscribed_at",
            ))
        return JsonResponse({
            "ok": True,
            "message": "Готово! Вы подписаны на новости «Вольного Амура».",
        }, status=201 if created else 200)
    except ValidationError:
        return JsonResponse({"message": "Введите корректный адрес электронной почты."}, status=400)
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({"message": "Некорректные данные."}, status=400)


@require_http_methods(["GET"])
def newsletter_unsubscribe_api(request, token):
    subscriber = NewsletterSubscriber.objects.filter(unsubscribe_token=token).first()
    if subscriber:
        subscriber.is_active = False
        subscriber.unsubscribed_at = timezone.now()
        subscriber.save(update_fields=("is_active", "unsubscribed_at"))
    return HttpResponse(
        "<!doctype html><html lang='ru'><meta charset='utf-8'>"
        "<title>Подписка отключена</title>"
        "<body style='font-family:Arial;padding:48px;background:#f4faf7;color:#102c24'>"
        "<h1>Вы отписаны от рассылки</h1>"
        "<p>Мы больше не будем отправлять рекламные письма на этот адрес.</p>"
        "<a href='/'>Вернуться на сайт</a></body></html>",
        content_type="text/html; charset=utf-8",
    )

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
            user=request.user if request.user.is_authenticated and not request.user.is_staff else None,
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
