from django.urls import path

from apps.comum import views

app_name = "comum"

urlpatterns = [
    path("", views.PaginaInicialView.as_view(), name="pagina_inicial"),
    path("aviso/", views.AvisoDesvinculacaoView.as_view(), name="aviso_desvinculacao"),
    path(
        "privacidade/",
        views.PoliticaPrivacidadeView.as_view(),
        name="politica_de_privacidade",
    ),
    path("sobre/", views.SobreView.as_view(), name="sobre"),
]
