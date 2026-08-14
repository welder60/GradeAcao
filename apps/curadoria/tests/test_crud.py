"""CRUD das entidades sob curadoria e registro em log (RF15, RF46)."""

import pytest
from django.contrib.auth.models import Group, User
from django.urls import reverse

from apps.catalogo.models import ComponenteCurricular, ComponenteRelacao, Curso, Semestre, Turma
from apps.comum.models import Campus, RegistroCarga
from apps.curadoria.permissoes import GRUPO_CURADOR


@pytest.fixture
def curador(db) -> User:
    usuario = User.objects.create_user("curador", password="senha-de-teste")
    grupo, _ = Group.objects.get_or_create(name=GRUPO_CURADOR)
    usuario.groups.add(grupo)
    return usuario


@pytest.fixture
def cliente(client, curador):
    client.force_login(curador)
    return client


# -- Criação ---------------------------------------------------------------


def test_cria_campus_e_registra_operacao(cliente, curador):
    resposta = cliente.post(
        reverse("curadoria:criar", args=["campi"]),
        {"codigo": "FGA", "nome": "Faculdade do Gama"},
    )

    assert resposta.status_code == 302
    assert Campus.objects.filter(codigo="FGA").exists()

    registro = RegistroCarga.objects.latest("criado_em")
    assert registro.curador == curador
    assert registro.origem == RegistroCarga.Origem.MANUAL
    assert registro.entidade == "campus"
    assert registro.registros_afetados == 1


def test_cria_componente_normalizando_o_codigo(cliente):
    cliente.post(
        reverse("curadoria:criar", args=["componentes"]),
        {"codigo": " cic0004 ", "nome": "Algoritmos", "carga_horaria": 60, "ativo": "on"},
    )
    assert ComponenteCurricular.objects.filter(codigo="CIC0004").exists()


def test_cria_semestre_derivando_o_codigo(cliente):
    cliente.post(
        reverse("curadoria:criar", args=["semestres"]),
        {"ano": 2026, "periodo": 2, "codigo": ""},
    )
    assert Semestre.objects.filter(codigo="20262").exists()


# -- Edição ----------------------------------------------------------------


def test_edita_curso(cliente):
    curso = Curso.objects.create(nome="Engenharia de Software")

    resposta = cliente.post(
        reverse("curadoria:editar", args=["cursos", curso.pk]),
        {"nome": "Engenharia de Software (FGA)", "codigo": "", "turno": "INTEGRAL"},
    )

    assert resposta.status_code == 302
    curso.refresh_from_db()
    assert curso.nome == "Engenharia de Software (FGA)"
    assert curso.codigo is None
    assert RegistroCarga.objects.filter(entidade="curso").exists()


# -- Exclusão --------------------------------------------------------------


def test_exclui_docente_e_registra_operacao(cliente):
    from apps.catalogo.models import Docente

    docente = Docente.objects.create(nome="Fulana de Tal")

    resposta = cliente.post(reverse("curadoria:excluir", args=["docentes", docente.pk]))

    assert resposta.status_code == 302
    assert not Docente.objects.filter(pk=docente.pk).exists()
    registro = RegistroCarga.objects.latest("criado_em")
    assert "Exclusão" in registro.detalhe


def test_confirmacao_de_exclusao_lista_dependentes(cliente):
    componente = ComponenteCurricular.objects.create(codigo="CIC0001", nome="Introdução")
    semestre = Semestre.objects.create(ano=2026, periodo=1, codigo="20261")
    Turma.objects.create(semestre=semestre, componente=componente, codigo="A")

    resposta = cliente.get(reverse("curadoria:excluir", args=["componentes", componente.pk]))

    assert resposta.status_code == 200
    assert any("turmas" in item for item in resposta.context["dependentes"])


# -- Validações ------------------------------------------------------------


def test_relacao_de_componente_consigo_mesmo_e_rejeitada(cliente):
    componente = ComponenteCurricular.objects.create(codigo="CIC0002", nome="Estruturas")

    resposta = cliente.post(
        reverse("curadoria:criar", args=["relacoes-entre-componentes"]),
        {
            "componente": componente.pk,
            "componente_relacionado": componente.pk,
            "tipo": ComponenteRelacao.Tipo.PRE_REQUISITO,
            "grupo": 1,
        },
    )

    assert resposta.status_code == 200
    assert ComponenteRelacao.objects.count() == 0
    assert "componente_relacionado" in resposta.context["form"].errors


def test_turma_com_mais_ocupadas_que_ofertadas_e_rejeitada(cliente):
    componente = ComponenteCurricular.objects.create(codigo="CIC0003", nome="Compiladores")
    semestre = Semestre.objects.create(ano=2026, periodo=1, codigo="20261")

    resposta = cliente.post(
        reverse("curadoria:criar", args=["turmas"]),
        {
            "semestre": semestre.pk,
            "componente": componente.pk,
            "codigo": "A",
            "vagas_ofertadas": 10,
            "vagas_ocupadas": 20,
        },
    )

    assert resposta.status_code == 200
    assert Turma.objects.count() == 0
    assert "vagas_ocupadas" in resposta.context["form"].errors


# -- Busca, filtros e log ---------------------------------------------------


def test_busca_filtra_a_listagem(cliente):
    ComponenteCurricular.objects.create(codigo="CIC0010", nome="Banco de Dados")
    ComponenteCurricular.objects.create(codigo="FGA0010", nome="Métodos de Desenvolvimento")

    resposta = cliente.get(reverse("curadoria:lista", args=["componentes"]), {"q": "banco"})

    assert resposta.status_code == 200
    assert resposta.context["total"] == 1


def test_log_de_operacoes_lista_os_registros(cliente):
    cliente.post(
        reverse("curadoria:criar", args=["campi"]),
        {"codigo": "UNB-X", "nome": "Campus experimental"},
    )

    resposta = cliente.get(reverse("curadoria:registro_carga"))

    assert resposta.status_code == 200
    assert len(resposta.context["registros"]) == 1
