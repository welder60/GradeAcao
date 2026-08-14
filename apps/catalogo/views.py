"""
Views de consulta do catálogo e da oferta.

Toda tela de catálogo expõe o período letivo de referência e a data da última
atualização dos dados (RF12, RF45) por meio de `ContextoDeOfertaMixin`.
"""

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from apps.catalogo.models import (
    ComponenteCurricular,
    ComponenteRelacao,
    MatrizComponente,
    MatrizCurricular,
    Semestre,
    Turma,
)
from apps.comum.models import Campus, CodigoDia, Turno
from apps.planejamento.servicos import turmas_da_oferta


class ContextoDeOfertaMixin:
    """Injeta o semestre de referência e a data de coleta no contexto."""

    def get_semestre(self) -> Semestre | None:
        codigo = self.request.GET.get("semestre")
        if codigo:
            return Semestre.objects.filter(codigo=codigo).first()
        return Semestre.objects.atual()

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        semestre = self.get_semestre()
        contexto["semestre"] = semestre
        contexto["oferta_atualizada_em"] = semestre.oferta_atualizada_em if semestre else None
        contexto["semestres"] = Semestre.objects.order_by("-ano", "-periodo")
        return contexto


class ComponenteListView(ContextoDeOfertaMixin, ListView):
    """Busca de componentes por código, nome ou parte do nome (RF09)."""

    model = ComponenteCurricular
    template_name = "catalogo/componente_lista.html"
    context_object_name = "componentes"
    paginate_by = 25

    def get_queryset(self):
        consulta = ComponenteCurricular.objects.filter(ativo=True)
        termo = self.request.GET.get("q", "").strip()
        if termo:
            consulta = consulta.filter(Q(codigo__icontains=termo) | Q(nome__icontains=termo))
        departamento = self.request.GET.get("departamento")
        if departamento:
            consulta = consulta.filter(departamento=departamento)
        return consulta.order_by("codigo")

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["termo"] = self.request.GET.get("q", "")
        contexto["departamentos"] = (
            ComponenteCurricular.objects.exclude(departamento__isnull=True)
            .exclude(departamento="")
            .values_list("departamento", flat=True)
            .distinct()
            .order_by("departamento")
        )
        return contexto


class ComponenteDetailView(ContextoDeOfertaMixin, DetailView):
    """Ficha do componente com pré-requisitos, co-requisitos e turmas (RF07)."""

    model = ComponenteCurricular
    template_name = "catalogo/componente_detalhe.html"
    context_object_name = "componente"
    slug_field = "codigo"
    slug_url_kwarg = "codigo"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        componente = self.object
        relacoes = componente.relacoes.select_related("componente_relacionado")

        contexto["pre_requisitos"] = relacoes.filter(tipo=ComponenteRelacao.Tipo.PRE_REQUISITO)
        contexto["co_requisitos"] = relacoes.filter(tipo=ComponenteRelacao.Tipo.CO_REQUISITO)
        # Equivalências bidirecionais valem nos dois sentidos (RN06, A03).
        contexto["equivalencias"] = list(
            relacoes.filter(tipo=ComponenteRelacao.Tipo.EQUIVALENCIA)
        ) + list(
            componente.relacoes_inversas.filter(
                tipo=ComponenteRelacao.Tipo.EQUIVALENCIA, bidirecional=True
            ).select_related("componente")
        )

        semestre = contexto.get("semestre")
        contexto["turmas"] = (
            Turma.objects.filter(componente=componente, semestre=semestre)
            .prefetch_related("horarios__codigo_dia", "horarios__codigo_horario", "docentes")
            .order_by("codigo")
            if semestre
            else Turma.objects.none()
        )
        return contexto


class OfertaListView(ContextoDeOfertaMixin, ListView):
    """
    Oferta do período letivo, com filtros por campus, turno, dia da semana,
    docente e departamento (RF08, RF10).
    """

    model = Turma
    template_name = "catalogo/oferta_lista.html"
    context_object_name = "turmas"
    paginate_by = 30

    def get_queryset(self):
        semestre = self.get_semestre()
        if semestre is None:
            return Turma.objects.none()

        consulta = turmas_da_oferta(
            semestre,
            {
                "campus": self.request.GET.get("campus"),
                "turno": self.request.GET.get("turno"),
                "dia": self.request.GET.get("dia"),
                "docente": self.request.GET.get("docente"),
                "departamento": self.request.GET.get("departamento"),
            },
        )

        termo = self.request.GET.get("q", "").strip()
        if termo:
            consulta = consulta.filter(
                Q(componente__codigo__icontains=termo) | Q(componente__nome__icontains=termo)
            )

        if self.request.GET.get("respeitar_restricoes") and self.request.user.is_authenticated:
            consulta = self._ocultar_indisponiveis(consulta)

        return consulta.order_by("componente__codigo", "codigo")

    def _ocultar_indisponiveis(self, consulta):
        """Oculta turmas incompatíveis com as restrições do discente (RF28)."""
        from apps.planejamento.models import RestricaoDisponibilidade

        restricoes = RestricaoDisponibilidade.objects.filter(usuario=self.request.user).values_list(
            "codigo_dia_id", "codigo_horario_id"
        )

        for dia_id, horario_id in restricoes:
            consulta = consulta.exclude(
                horarios__codigo_dia_id=dia_id, horarios__codigo_horario_id=horario_id
            )
        return consulta

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["campi"] = Campus.objects.all()
        contexto["dias"] = CodigoDia.objects.all()
        contexto["turnos"] = Turno.choices
        contexto["filtros"] = self.request.GET.dict()
        return contexto


class MatrizCurricularDetailView(ContextoDeOfertaMixin, DetailView):
    """Matriz curricular organizada por período recomendado (RF11)."""

    model = MatrizCurricular
    template_name = "catalogo/matriz_detalhe.html"
    context_object_name = "matriz"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        itens = (
            MatrizComponente.objects.filter(matriz=self.object)
            .select_related("componente")
            .order_by("periodo_recomendado", "componente__codigo")
        )

        status_por_componente: dict[int, str] = {}
        if self.request.user.is_authenticated:
            from apps.contas.models import ProgressoComponente

            status_por_componente = dict(
                ProgressoComponente.objects.filter(usuario=self.request.user).values_list(
                    "componente_id", "status"
                )
            )

        periodos: dict[int | None, list] = {}
        for item in itens:
            item.status_declarado = status_por_componente.get(item.componente_id)
            periodos.setdefault(item.periodo_recomendado, []).append(item)

        contexto["periodos"] = sorted(periodos.items(), key=lambda par: (par[0] is None, par[0]))
        return contexto


class MatrizCurricularListView(ListView):
    """Lista de matrizes disponíveis para vínculo no perfil."""

    model = MatrizCurricular
    template_name = "catalogo/matriz_lista.html"
    context_object_name = "matrizes"

    def get_queryset(self):
        consulta = MatrizCurricular.objects.select_related("curso", "curso__campus")
        curso_id = self.request.GET.get("curso")
        if curso_id:
            consulta = consulta.filter(curso_id=curso_id)
        return consulta.order_by("curso__nome", "-vigencia_inicio")


class TurmaDetailView(ContextoDeOfertaMixin, DetailView):
    """Detalhe de uma turma ofertada."""

    model = Turma
    template_name = "catalogo/turma_detalhe.html"
    context_object_name = "turma"

    def get_object(self, queryset=None):
        return get_object_or_404(
            Turma.objects.select_related("componente", "semestre").prefetch_related(
                "horarios__codigo_dia", "horarios__codigo_horario", "horarios__campus", "docentes"
            ),
            pk=self.kwargs["pk"],
        )
