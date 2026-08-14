"""
Registro declarativo das entidades sob curadoria.

A área de curadoria não repete uma view por tabela: descreve cada entidade
aqui e reaproveita um único conjunto de views genéricas (`apps.curadoria.views`).
Incluir uma nova tabela no CRUD é acrescentar uma `EntidadeCuradoria` a
`ENTIDADES`.

Referência: RF15, RN14.
"""

from dataclasses import dataclass, field

from django.core.exceptions import FieldDoesNotExist
from django.db import models

from apps.catalogo.models import (
    ComponenteCurricular,
    ComponenteRelacao,
    Curso,
    Docente,
    MatrizComponente,
    MatrizCurricular,
    Semestre,
    Turma,
    TurmaDocente,
    TurmaHorario,
)
from apps.comum.models import Campus, CodigoDia, CodigoHorario
from apps.curadoria import forms

# Seções do painel, na ordem em que são exibidas.
SECAO_DOMINIO = "Tabelas de domínio"
SECAO_ESTRUTURA = "Estrutura acadêmica"
SECAO_OFERTA = "Oferta"


@dataclass(frozen=True)
class EntidadeCuradoria:
    """Descreve uma tabela sob curadoria e como ela é listada e editada."""

    slug: str
    modelo: type[models.Model]
    formulario: type[forms.FormularioDeCuradoria]
    colunas: tuple[str, ...]
    secao: str
    descricao: str = ""
    busca: tuple[str, ...] = ()
    filtros: tuple[str, ...] = ()
    ordenacao: tuple[str, ...] = ()
    relacionados: tuple[str, ...] = ()
    prefetch: tuple[str, ...] = field(default_factory=tuple)

    # -- Rótulos -----------------------------------------------------------

    @property
    def rotulo(self) -> str:
        return str(self.modelo._meta.verbose_name)

    @property
    def rotulo_plural(self) -> str:
        return str(self.modelo._meta.verbose_name_plural)

    # -- Consulta ----------------------------------------------------------

    def queryset(self):
        consulta = self.modelo._default_manager.all()
        if self.relacionados:
            consulta = consulta.select_related(*self.relacionados)
        if self.prefetch:
            consulta = consulta.prefetch_related(*self.prefetch)
        if self.ordenacao:
            consulta = consulta.order_by(*self.ordenacao)
        return consulta

    def cabecalhos(self) -> list[str]:
        return [rotulo_de_campo(self.modelo, nome) for nome in self.colunas]

    def linha(self, objeto) -> list[str]:
        return [valor_de_campo(objeto, nome) for nome in self.colunas]

    def opcoes_de_filtro(self, aplicados: dict[str, str] | None = None) -> list[dict]:
        """Opções de cada filtro declarado, já marcando o valor selecionado."""
        aplicados = aplicados or {}
        opcoes = []
        for nome in self.filtros:
            campo = self.modelo._meta.get_field(nome)
            if campo.choices:
                valores = [(str(v), str(r)) for v, r in campo.choices]
            elif campo.is_relation:
                valores = [
                    (str(o.pk), str(o)) for o in campo.related_model._default_manager.all()[:200]
                ]
            else:
                valores = [("1", "Sim"), ("0", "Não")]

            selecionado = str(aplicados.get(nome, ""))
            opcoes.append(
                {
                    "nome": nome,
                    "rotulo": rotulo_de_campo(self.modelo, nome),
                    "valores": [
                        {"valor": valor, "rotulo": rotulo, "selecionado": valor == selecionado}
                        for valor, rotulo in valores
                    ],
                }
            )
        return opcoes


def rotulo_de_campo(modelo: type[models.Model], nome: str) -> str:
    """Rótulo legível de um campo, atributo ou propriedade do modelo."""
    try:
        return str(modelo._meta.get_field(nome).verbose_name)
    except FieldDoesNotExist:
        return nome.replace("_", " ")


def valor_de_campo(objeto, nome: str) -> str:
    """Valor formatado de um campo para exibição na listagem."""
    exibicao = getattr(objeto, f"get_{nome}_display", None)
    valor = exibicao() if callable(exibicao) else getattr(objeto, nome, None)
    if callable(valor):
        valor = valor()
    if isinstance(valor, bool):
        return "Sim" if valor else "Não"
    if valor is None or valor == "":
        return "—"
    return str(valor)


ENTIDADES: tuple[EntidadeCuradoria, ...] = (
    # -- Tabelas de domínio -------------------------------------------------
    EntidadeCuradoria(
        slug="campi",
        modelo=Campus,
        formulario=forms.CampusForm,
        colunas=("codigo", "nome"),
        secao=SECAO_DOMINIO,
        descricao="Unidades físicas em que ocorrem as aulas.",
        busca=("codigo", "nome"),
    ),
    EntidadeCuradoria(
        slug="codigos-de-dia",
        modelo=CodigoDia,
        formulario=forms.CodigoDiaForm,
        colunas=("ordem", "codigo", "dia_da_semana"),
        secao=SECAO_DOMINIO,
        descricao="Dias da semana usados nos encontros das turmas.",
        busca=("codigo", "dia_da_semana"),
    ),
    EntidadeCuradoria(
        slug="codigos-de-horario",
        modelo=CodigoHorario,
        formulario=forms.CodigoHorarioForm,
        colunas=("ordem", "codigo", "horario", "hora_inicio", "hora_fim", "turno"),
        secao=SECAO_DOMINIO,
        descricao="Blocos de horário; base da detecção de choque (RN01).",
        busca=("codigo", "horario"),
        filtros=("turno",),
    ),
    # -- Estrutura acadêmica ------------------------------------------------
    EntidadeCuradoria(
        slug="cursos",
        modelo=Curso,
        formulario=forms.CursoForm,
        colunas=("nome", "codigo", "campus", "turno"),
        secao=SECAO_ESTRUTURA,
        descricao="Programas de formação aos quais o discente se vincula.",
        busca=("nome", "codigo"),
        filtros=("campus", "turno"),
        relacionados=("campus",),
    ),
    EntidadeCuradoria(
        slug="matrizes",
        modelo=MatrizCurricular,
        formulario=forms.MatrizCurricularForm,
        colunas=("nome", "curso", "codigo", "vigencia_inicio", "vigencia_fim", "vigente"),
        secao=SECAO_ESTRUTURA,
        descricao="Conjuntos de componentes exigidos para a integralização.",
        busca=("nome", "codigo", "curso__nome"),
        filtros=("curso",),
        relacionados=("curso",),
    ),
    EntidadeCuradoria(
        slug="componentes",
        modelo=ComponenteCurricular,
        formulario=forms.ComponenteCurricularForm,
        colunas=("codigo", "nome", "carga_horaria", "creditos", "departamento", "ativo"),
        secao=SECAO_ESTRUTURA,
        descricao="Catálogo de componentes curriculares (RF07).",
        busca=("codigo", "nome", "departamento"),
        filtros=("ativo",),
    ),
    EntidadeCuradoria(
        slug="relacoes-entre-componentes",
        modelo=ComponenteRelacao,
        formulario=forms.ComponenteRelacaoForm,
        colunas=("componente", "tipo", "componente_relacionado", "grupo", "bidirecional"),
        secao=SECAO_ESTRUTURA,
        descricao="Pré-requisitos, co-requisitos e equivalências (RN06).",
        busca=("componente__codigo", "componente_relacionado__codigo"),
        filtros=("tipo",),
        relacionados=("componente", "componente_relacionado"),
    ),
    EntidadeCuradoria(
        slug="componentes-da-matriz",
        modelo=MatrizComponente,
        formulario=forms.MatrizComponenteForm,
        colunas=("matriz", "componente", "periodo_recomendado", "natureza"),
        secao=SECAO_ESTRUTURA,
        descricao="Vínculo entre matriz curricular e componente (RF11).",
        busca=("matriz__nome", "componente__codigo", "componente__nome"),
        filtros=("matriz", "natureza"),
        relacionados=("matriz", "matriz__curso", "componente"),
    ),
    # -- Oferta -------------------------------------------------------------
    EntidadeCuradoria(
        slug="semestres",
        modelo=Semestre,
        formulario=forms.SemestreForm,
        colunas=("codigo", "ano", "periodo", "ativo", "oferta_atualizada_em"),
        secao=SECAO_OFERTA,
        descricao="Períodos letivos e data da última carga de oferta (RF45).",
        busca=("codigo",),
        filtros=("ativo",),
    ),
    EntidadeCuradoria(
        slug="docentes",
        modelo=Docente,
        formulario=forms.DocenteForm,
        colunas=("nome",),
        secao=SECAO_OFERTA,
        descricao="Nomes divulgados publicamente na oferta (RNF17).",
        busca=("nome",),
    ),
    EntidadeCuradoria(
        slug="turmas",
        modelo=Turma,
        formulario=forms.TurmaForm,
        colunas=(
            "componente",
            "codigo",
            "semestre",
            "modalidade",
            "vagas_ofertadas",
            "vagas_ocupadas",
            "coletado_em",
        ),
        secao=SECAO_OFERTA,
        descricao="Instâncias de componentes em um período letivo (RF08).",
        busca=("codigo", "componente__codigo", "componente__nome"),
        filtros=("semestre", "modalidade"),
        relacionados=("componente", "semestre"),
    ),
    EntidadeCuradoria(
        slug="horarios-de-turma",
        modelo=TurmaHorario,
        formulario=forms.TurmaHorarioForm,
        colunas=("turma", "codigo_dia", "codigo_horario", "campus", "local"),
        secao=SECAO_OFERTA,
        descricao="Encontros semanais de cada turma.",
        busca=("turma__codigo", "turma__componente__codigo", "local"),
        filtros=("codigo_dia",),
        relacionados=(
            "turma",
            "turma__componente",
            "turma__semestre",
            "codigo_dia",
            "codigo_horario",
            "campus",
        ),
    ),
    EntidadeCuradoria(
        slug="docentes-de-turma",
        modelo=TurmaDocente,
        formulario=forms.TurmaDocenteForm,
        colunas=("turma", "docente", "adicionado_em"),
        secao=SECAO_OFERTA,
        descricao="Vínculo entre turma e docente divulgado na oferta.",
        busca=("turma__codigo", "turma__componente__codigo", "docente__nome"),
        ordenacao=("turma__componente__codigo", "docente__nome"),
        relacionados=("turma", "turma__componente", "docente"),
    ),
)

REGISTRO: dict[str, EntidadeCuradoria] = {entidade.slug: entidade for entidade in ENTIDADES}

SECOES: tuple[str, ...] = (SECAO_DOMINIO, SECAO_ESTRUTURA, SECAO_OFERTA)


def entidades_por_secao() -> list[tuple[str, list[EntidadeCuradoria]]]:
    """Entidades agrupadas para o painel e para a navegação lateral."""
    return [(secao, [e for e in ENTIDADES if e.secao == secao]) for secao in SECOES]
