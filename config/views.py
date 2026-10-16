from pathlib import Path

from django.conf import settings
from django.http import HttpResponse


def index(request):
    index_file = Path(settings.BASE_DIR) / "frontend" / "dist" / "index.html"
    try:
        html = index_file.read_text(encoding="utf-8")
    except FileNotFoundError:
        html = (
            "<h1>Frontend no compilado</h1>"
            "<p>Ejecuta <code>compilar.bat</code> (npm run build + collectstatic).</p>"
        )
    return HttpResponse(html, content_type="text/html")
