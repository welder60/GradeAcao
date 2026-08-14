from django.contrib.auth import views as auth_views
from django.urls import path

from apps.contas import views

app_name = "contas"

urlpatterns = [
    # Autenticação (RF02). O provedor OAuth é plugado sobre estas rotas.
    path(
        "entrar/",
        auth_views.LoginView.as_view(template_name="contas/entrar.html"),
        name="entrar",
    ),
    path("sair/", auth_views.LogoutView.as_view(), name="sair"),
    # Perfil e progresso
    path("perfil/", views.PerfilUpdateView.as_view(), name="perfil"),
    path("progresso/", views.ProgressoListView.as_view(), name="progresso"),
    path("progresso/novo/", views.ProgressoCreateView.as_view(), name="progresso_novo"),
    path(
        "progresso/<int:pk>/editar/",
        views.ProgressoUpdateView.as_view(),
        name="progresso_editar",
    ),
    path(
        "progresso/<int:pk>/excluir/",
        views.ProgressoDeleteView.as_view(),
        name="progresso_excluir",
    ),
    path("progresso/lote/", views.ProgressoEmLoteView.as_view(), name="progresso_lote"),
    # Dados pessoais
    path("dados/exportar/", views.ExportarDadosView.as_view(), name="exportar_dados"),
    path("excluir/", views.ExcluirContaView.as_view(), name="excluir_conta"),
]
