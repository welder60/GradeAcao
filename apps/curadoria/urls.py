"""
Rotas da área de curadoria.

A rota do log vem antes das rotas genéricas por entidade para que `cargas`
não seja interpretado como um slug de entidade.
"""

from django.urls import path

from apps.curadoria import views

app_name = "curadoria"

urlpatterns = [
    path("", views.PainelView.as_view(), name="painel"),
    path("cargas/", views.RegistroCargaListView.as_view(), name="registro_carga"),
    path("<slug:slug>/", views.ListaView.as_view(), name="lista"),
    path("<slug:slug>/novo/", views.CriarView.as_view(), name="criar"),
    path("<slug:slug>/<int:pk>/editar/", views.EditarView.as_view(), name="editar"),
    path("<slug:slug>/<int:pk>/excluir/", views.ExcluirView.as_view(), name="excluir"),
]
