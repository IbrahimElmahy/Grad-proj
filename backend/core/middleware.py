import re
from django.conf import settings
from django.http import HttpResponse


class DevCorsMiddleware:
    ALLOWED_ORIGINS = {
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:5174",
        "http://localhost:5174",
        "http://127.0.0.1:8080",
        "http://localhost:8080",
        "http://127.0.0.1:8085",
        "http://localhost:8085",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    }
    
    LOCAL_ORIGIN_RE = re.compile(r"^https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "OPTIONS":
            response = HttpResponse()
        else:
            response = self.get_response(request)

        origin = request.headers.get("Origin")
        if origin:
            is_allowed = (
                settings.DEBUG
                or origin in self.ALLOWED_ORIGINS
                or self.LOCAL_ORIGIN_RE.match(origin)
            )
            if is_allowed:
                response["Access-Control-Allow-Origin"] = origin
                response["Vary"] = "Origin"
                response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
                response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept, Origin, X-Requested-With"
                response["Access-Control-Allow-Credentials"] = "true"

        return response
