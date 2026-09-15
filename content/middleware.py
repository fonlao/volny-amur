from django.utils import timezone
from .models import Visit


class VisitTrackingMiddleware:
    """Count public HTML page views without storing IP addresses or user agents."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        should_track = (
            request.method == "GET"
            and request.path == "/"
            and not request.path.startswith(("/admin", "/api", "/static", "/assets"))
        )
        if should_track and not request.session.session_key:
            request.session.create()
        response = self.get_response(request)
        if (
            should_track
            and response.status_code == 200
            and getattr(request, "session", None) is not None
        ):
            session_key = request.session.session_key
            if session_key:
                Visit.objects.create(
                    day=timezone.localdate(),
                    path=request.path,
                    session_key=session_key,
                )
        return response
