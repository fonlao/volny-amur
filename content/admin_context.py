from django.urls import reverse


def dashboard_counts(request):
    if request.path != reverse("admin:index") or not request.user.is_authenticated or not request.user.is_staff:
        return {}

    from .models import Lead, Payment, Route, RouteDeparture, Visit, NewsletterSubscriber, NewsletterCampaign, TelegramContact, TelegramReservation
    from django.utils import timezone
    from django.db.models import Count
    from datetime import timedelta

    today = timezone.localdate()
    week_start = today - timedelta(days=6)
    visits = Visit.objects.filter(day__gte=week_start, day__lte=today)
    daily_visits = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        daily_visits.append({
            "label": day.strftime("%d.%m"),
            "value": visits.filter(day=day).count(),
        })
    max_daily = max((item["value"] for item in daily_visits), default=1) or 1
    for item in daily_visits:
        item["height"] = round(item["value"] / max_daily * 100)
    top_pages = list(
        visits.values("path").annotate(total=Count("id")).order_by("-total")[:5]
    )

    return {
        "dashboard_stats": {
            "new_leads": Lead.objects.filter(status="new").count(),
            "all_leads": Lead.objects.count(),
            "pending_payments": Payment.objects.filter(status="pending").count(),
            "active_routes": Route.objects.filter(is_active=True).count(),
            "upcoming_departures": RouteDeparture.objects.filter(
                is_published=True,
                start_date__gte=timezone.localdate(),
            ).count(),
            "visits_today": Visit.objects.filter(day=today).count(),
            "unique_today": Visit.objects.filter(day=today).values("session_key").distinct().count(),
            "visits_7_days": visits.count(),
            "newsletter_subscribers": NewsletterSubscriber.objects.filter(consent=True, is_active=True).count(),
            "newsletter_campaigns": NewsletterCampaign.objects.count(),
            "telegram_subscribers": TelegramContact.objects.filter(is_active=True).count(),
            "telegram_reservations": TelegramReservation.objects.count(),
            "buyers": Payment.objects.filter(paid=True).values("email").distinct().count(),
            "daily_visits": daily_visits,
            "top_pages": top_pages,
        }
    }
