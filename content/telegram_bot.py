import json
import logging
import urllib.error
import urllib.request
import mimetypes
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import NewsletterCampaign, Payment, Route, SiteSettings, TelegramContact, TelegramReservation
from .views import yookassa_request

logger = logging.getLogger(__name__)
MENU = [["Выбрать маршрут"], ["Предложить свой маршрут"], ["Внести предоплату"], ["Написать админу бота"]]


def telegram_request(method, payload):
    if not settings.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN не задан")
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/{method}",
        data=body, headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))
    if not data.get("ok"):
        raise RuntimeError(data.get("description", "Telegram API error"))
    return data.get("result")


def telegram_upload(method, fields, file_path, field_name="photo"):
    if not settings.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN не задан")
    boundary = "----VolnyAmurTelegramBoundary"
    parts = []
    for key, value in fields.items():
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n{value}\r\n".encode())
    path = str(file_path)
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    filename = path.replace("\\", "/").rsplit("/", 1)[-1]
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{field_name}\"; filename=\"{filename}\"\r\nContent-Type: {mime}\r\n\r\n".encode())
    parts.append(open(path, "rb").read())
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/{method}",
        data=b"".join(parts),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))
    if not data.get("ok"):
        raise RuntimeError(data.get("description", "Telegram API upload error"))
    return data.get("result")


def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return telegram_request("sendMessage", payload)


def menu_markup():
    keyboard = [[{"text": item} for item in row] for row in MENU]
    miniapp_url = settings.TELEGRAM_MINIAPP_URL or (
        f"{settings.PUBLIC_BASE_URL.rstrip('/')}/miniapp/" if settings.PUBLIC_BASE_URL else ""
    )
    if miniapp_url:
        keyboard.insert(1, [{"text": "Открыть мини‑приложение", "web_app": {"url": miniapp_url}}])
    return {"keyboard": keyboard, "resize_keyboard": True}


def inline_routes():
    return {"inline_keyboard": [[{"text": route.title, "callback_data": f"route:{route.pk}"}] for route in Route.objects.filter(is_active=True)]}


def miniapp_markup(url=None):
    target = url or settings.TELEGRAM_MINIAPP_URL or settings.PUBLIC_BASE_URL
    return {"inline_keyboard": [[{"text": "Открыть маршруты", "web_app": {"url": target}}], [{"text": "Меню", "callback_data": "menu"}]]}


def upsert_contact(user):
    contact, _ = TelegramContact.objects.update_or_create(
        chat_id=user["id"], defaults={"username": user.get("username", ""), "first_name": user.get("first_name", ""), "is_active": True}
    )
    return contact


def operator_message(chat_id, text):
    if settings.TELEGRAM_ADMIN_CHAT_ID:
        send_message(settings.TELEGRAM_ADMIN_CHAT_ID, f"<b>Сообщение из бота</b>\nОт: <code>{chat_id}</code>\n\n{text}")


def create_route_payment(contact, route):
    site = SiteSettings.objects.first()
    site_deposit = site.booking_deposit if site else Decimal("5000")
    payment = Payment.objects.create(
        name=contact.first_name or contact.username or "Telegram-путешественник",
        phone="telegram",
        email=f"telegram-{contact.chat_id}@volniyamur.local",
        route=route.title,
        amount=site_deposit,
        status="created",
    )
    remote = yookassa_request("POST", "/payments", {
        "amount": {"value": f"{site_deposit:.2f}", "currency": "RUB"}, "capture": True,
        "confirmation": {"type": "redirect", "return_url": settings.PUBLIC_BASE_URL or "https://201.51.30.55/"},
        "description": f"Предоплата за маршрут «{route.title}»"[:128],
        "metadata": {"payment_public_id": str(payment.public_id)},
    }, payment.idempotence_key)
    payment.yookassa_id = remote["id"]
    payment.status = remote.get("status", "pending")
    payment.save(update_fields=("yookassa_id", "status", "updated_at"))
    return payment, remote["confirmation"]["confirmation_url"]


def handle_update(update):
    callback = update.get("callback_query")
    message = update.get("message") or (callback or {}).get("message")
    if not message:
        return
    user = (message.get("from") or callback.get("from"))
    chat_id = message["chat"]["id"]
    contact = upsert_contact(user)
    web_app_data = message.get("web_app_data")
    if web_app_data:
        try:
            payload = json.loads(web_app_data.get("data", "{}"))
            if payload.get("action") == "route":
                route = Route.objects.filter(title=payload.get("title"), is_active=True).first()
                if route:
                    TelegramReservation.objects.get_or_create(contact=contact, route=route, status="new")
                    count = TelegramReservation.objects.filter(route=route, status__in=("new", "paid")).count()
                    send_message(chat_id, f"Вы успешно записаны на маршрут «{route.title}».\nТекущее количество туристов: {count}. Группа стартует от 8 человек.", {"inline_keyboard": [[{"text": "Внести предоплату", "callback_data": f"pay:{route.pk}"}], [{"text": "Меню", "callback_data": "menu"}]]})
                    return
        except (ValueError, json.JSONDecodeError):
            logger.warning("Invalid Telegram Web App payload")
    if callback:
        data = callback.get("data", "")
        telegram_request("answerCallbackQuery", {"callback_query_id": callback["id"]})
        if data == "menu":
            send_message(chat_id, "Главное меню:", menu_markup()); return
        if data == "routes":
            send_message(chat_id, "Выберите маршрут:", inline_routes()); return
        if data.startswith("route:"):
            route = Route.objects.filter(pk=data.split(":", 1)[1], is_active=True).first()
            if route:
                reservation, created = TelegramReservation.objects.get_or_create(contact=contact, route=route, status="new")
                count = TelegramReservation.objects.filter(route=route, status__in=("new", "paid")).count()
                send_message(chat_id, f"Вы успешно записаны на маршрут «{route.title}».\nТекущее количество туристов: {count}. Группа стартует от 8 человек.", {"inline_keyboard": [[{"text": "Внести предоплату", "callback_data": f"pay:{route.pk}"}], [{"text": "Меню", "callback_data": "menu"}]]})
            return
        if data.startswith("pay:"):
            route = Route.objects.filter(pk=data.split(":", 1)[1], is_active=True).first()
            if route:
                try:
                    payment, url = create_route_payment(contact, route)
                    TelegramReservation.objects.update_or_create(contact=contact, route=route, defaults={"payment": payment})
                    send_message(chat_id, f"Вы выбрали маршрут «{route.title}». Перейдите к оплате брони:", {"inline_keyboard": [[{"text": "Оплатить через ЮKassa", "url": url}], [{"text": "Меню", "callback_data": "menu"}]]})
                except Exception as error:
                    logger.exception("Telegram payment failed")
                    send_message(chat_id, "Не удалось создать платёж. Напишите администратору бота.", menu_markup())
            return
    text = (message.get("text") or "").strip()
    if text in ("/start", "/menu", "/", "Меню"):
        send_message(chat_id, "Добро пожаловать в «Вольный Амур»! Выберите действие:", menu_markup()); return
    if text in ("Выбрать маршрут", "/routes"):
        send_message(chat_id, "Выберите маршрут:", inline_routes()); return
    if text == "Внести предоплату":
        send_message(chat_id, "Сначала выберите маршрут:", inline_routes()); return
    if text in ("Предложить свой маршрут", "Написать админу бота"):
        contact.state = "route_proposal" if text.startswith("Предложить") else "admin_message"
        contact.save(update_fields=("state", "last_seen_at"))
        send_message(chat_id, "Введите сообщение для оператора. Ваш текст будет доставлен, ожидайте ответ!", menu_markup()); return
    if contact.state in ("route_proposal", "admin_message"):
        operator_message(chat_id, text)
        contact.state = "idle"
        contact.save(update_fields=("state", "last_seen_at"))
        send_message(chat_id, "Ваше сообщение успешно доставлено, ожидайте ответ!", menu_markup())


def send_campaign_to_telegram(campaign):
    if not settings.TELEGRAM_BOT_TOKEN or not campaign.telegram_enabled:
        return 0
    contacts = TelegramContact.objects.filter(is_active=True)
    count = 0
    markup = {"inline_keyboard": [[{"text": "Меню", "callback_data": "menu"}, {"text": "Маршруты", "callback_data": "routes"}]]}
    if campaign.miniapp_url or settings.TELEGRAM_MINIAPP_URL:
        markup["inline_keyboard"].append([{ "text": "Открыть мини‑апп", "web_app": {"url": campaign.miniapp_url or settings.TELEGRAM_MINIAPP_URL} }])
    for contact in contacts.iterator():
        try:
            images = [image for image in (campaign.image_1, campaign.image_2, campaign.image_3) if image]
            if images:
                for image in images:
                    telegram_upload("sendPhoto", {"chat_id": contact.chat_id}, image.path)
                send_message(contact.chat_id, campaign.body, markup)
            else:
                send_message(contact.chat_id, campaign.body, markup)
            count += 1
        except Exception:
            logger.exception("Telegram campaign failed for chat_id=%s", contact.chat_id)
    return count


def run_polling(stop_event=None):
    miniapp_url = settings.TELEGRAM_MINIAPP_URL or (
        f"{settings.PUBLIC_BASE_URL.rstrip('/')}/miniapp/" if settings.PUBLIC_BASE_URL else ""
    )
    telegram_request("setMyCommands", {"commands": [
        {"command": "start", "description": "Запустить бота"},
        {"command": "menu", "description": "Открыть главное меню"},
        {"command": "routes", "description": "Выбрать маршрут"},
    ]})
    if miniapp_url:
        telegram_request("setChatMenuButton", {
            "menu_button": {"type": "web_app", "text": "Маршруты", "web_app": {"url": miniapp_url}}
        })
    offset = 0
    while not stop_event or not stop_event.is_set():
        updates = telegram_request("getUpdates", {"timeout": 25, "offset": offset, "allowed_updates": ["message", "callback_query"]})
        for update in updates:
            offset = update["update_id"] + 1
            try:
                handle_update(update)
            except Exception:
                logger.exception("Telegram update failed")
