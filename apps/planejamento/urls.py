from django.urls import path

from apps.planejamento import views

app_name = "planejamento"

urlpatterns = [
    path("grades/", views.GradeListView.as_view(), name="grade_lista"),
    path("grades/nova/", views.GradeCreateView.as_view(), name="grade_nova"),
    path("grades/comparar/", views.CompararGradesView.as_view(), name="grade_comparar"),
    path("grades/<int:pk>/", views.GradeDetailView.as_view(), name="grade_detalhe"),
    path("grades/<int:pk>/montar/", views.GradeMontarView.as_view(), name="grade_montar"),
    path("grades/<int:pk>/editar/", views.GradeUpdateView.as_view(), name="grade_editar"),
    path("grades/<int:pk>/excluir/", views.GradeDeleteView.as_view(), name="grade_excluir"),
    path(
        "grades/<int:pk>/duplicar/",
        views.DuplicarGradeView.as_view(),
        name="grade_duplicar",
    ),
    path(
        "grades/<int:pk>/preferida/",
        views.DefinirPreferidaView.as_view(),
        name="grade_preferida",
    ),
    path(
        "grades/<int:pk>/compartilhar/",
        views.CompartilharGradeView.as_view(),
        name="grade_compartilhar",
    ),
    # Montagem
    path(
        "grades/<int:pk>/turmas/adicionar/",
        views.AdicionarTurmaView.as_view(),
        name="grade_adicionar_turma",
    ),
    path(
        "grades/<int:pk>/turmas/<int:turma_id>/remover/",
        views.RemoverTurmaView.as_view(),
        name="grade_remover_turma",
    ),
    path(
        "grades/<int:pk>/choques/reconhecer/",
        views.ReconhecerChoqueView.as_view(),
        name="grade_reconhecer_choque",
    ),
    # Disponibilidade
    path("restricoes/", views.RestricaoListView.as_view(), name="restricao_lista"),
    path("restricoes/nova/", views.RestricaoCreateView.as_view(), name="restricao_nova"),
    path(
        "restricoes/<int:pk>/excluir/",
        views.RestricaoDeleteView.as_view(),
        name="restricao_excluir",
    ),
    # Compartilhamento público (RF40)
    path("g/<uuid:token>/", views.GradePublicaView.as_view(), name="grade_publica"),
]
