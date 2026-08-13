"""Roteamento raiz do GradeAção."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.comum.urls")),
    path("conta/", include("apps.contas.urls")),
    path("catalogo/", include("apps.catalogo.urls")),
    path("planejamento/", include("apps.planejamento.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
