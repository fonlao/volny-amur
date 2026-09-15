from django.urls import reverse


def dashboard_counts(request):
    if request.path != reverse("admin:index") or not request.user.is_authenticated or not request.user.is_staff:
        return {}

    from .models import Lead, Payment, Route

    return {
        "dashboard_stats": {
            "new_leads": Lead.objects.filter(status="new").count(),
            "all_leads": Lead.objects.count(),
            "pending_payments": Payment.objects.filter(status="pending").count(),
            "active_routes": Route.objects.filter(is_active=True).count(),
        }
    }
