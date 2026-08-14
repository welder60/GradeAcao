"""Restrição de acesso à área de curadoria (RN14)."""

import pytest
from django.contrib.auth.models import Group, User
from django.urls import reverse

from apps.curadoria.permissoes import GRUPO_CURADOR, e_curador
from apps.curadoria.registro import ENTIDADES


@pytest.fixture
def discente(db) -> User:
    return User.objects.create_user("discente", password="senha-de-teste")


@pytest.fixture
def curador(db) -> User:
    usuario = User.objects.create_user("curador", password="senha-de-teste")
    grupo, _ = Group.objects.get_or_create(name=GRUPO_CURADOR)
    usuario.groups.add(grupo)
    return usuario


@pytest.fixture
def administrador(db) -> User:
    return User.objects.create_user("admin", password="senha-de-teste", is_staff=True)


def test_anonimo_e_redirecionado_para_autenticacao(client, db):
    resposta = client.get(reverse("curadoria:painel"))
    assert resposta.status_code == 302
    assert "/conta/entrar/" in resposta["Location"]


def test_discente_sem_papel_recebe_403(client, discente):
    client.force_login(discente)
    assert client.get(reverse("curadoria:painel")).status_code == 403


def test_curador_acessa_o_painel(client, curador):
    client.force_login(curador)
    assert client.get(reverse("curadoria:painel")).status_code == 200


def test_administrador_acessa_o_painel(client, administrador):
    client.force_login(administrador)
    assert client.get(reverse("curadoria:painel")).status_code == 200


@pytest.mark.parametrize("entidade", ENTIDADES, ids=lambda e: e.slug)
def test_listagem_de_cada_entidade_responde(client, curador, entidade):
    client.force_login(curador)
    resposta = client.get(reverse("curadoria:lista", args=[entidade.slug]))
    assert resposta.status_code == 200


@pytest.mark.parametrize("entidade", ENTIDADES, ids=lambda e: e.slug)
def test_formulario_de_criacao_de_cada_entidade_responde(client, curador, entidade):
    client.force_login(curador)
    resposta = client.get(reverse("curadoria:criar", args=[entidade.slug]))
    assert resposta.status_code == 200


def test_slug_desconhecido_resulta_em_404(client, curador):
    client.force_login(curador)
    assert client.get(reverse("curadoria:lista", args=["inexistente"])).status_code == 404


def test_grupo_curador_e_criado_pela_migracao(db):
    assert Group.objects.filter(name=GRUPO_CURADOR).exists()


def test_e_curador_reconhece_os_tres_papeis(db, discente, curador, administrador):
    assert not e_curador(discente)
    assert e_curador(curador)
    assert e_curador(administrador)
