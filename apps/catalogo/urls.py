from django.urls import path

from apps.catalogo import views

app_name = "catalogo"

urlpatterns = [
    path("componentes/", views.ComponenteListView.as_view(), name="componente_lista"),
    path(
        "componentes/<str:codigo>/",
        views.ComponenteDetailView.as_view(),
        name="componente_detalhe",
    ),
    path("oferta/", views.OfertaListView.as_view(), name="oferta_lista"),
    path("turmas/<int:pk>/", views.TurmaDetailView.as_view(), name="turma_detalhe"),
    path("matrizes/", views.MatrizCurricularListView.as_view(), name="matriz_lista"),
    path(
        "matrizes/<int:pk>/",
        views.MatrizCurricularDetailView.as_view(),
        name="matriz_detalhe",
    ),
]
