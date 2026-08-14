"""
Views da área de curadoria dos dados públicos (RF15, RN14, RF46).

Um único conjunto de views genéricas atende todas as entidades descritas em
`apps.curadoria.registro`. A entidade é resolvida pelo trecho `<slug>` da URL;
slug desconhecido resulta em 404, e não em tela em branco.

Todo acesso passa por `CuradorRequeridoMixin`: a área é restrita a curadores e
administradores. Toda escrita gera registro em log (RF46).
"""

from django.contrib import messages
from django.db.models import Count, Q
from django.forms import Form
from django.http import Http404
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from apps.catalogo.models import ComponenteCurricular, Curso, MatrizCurricular, Semestre, Turma
from apps.comum.models import RegistroCarga
from apps.curadoria.permissoes import CuradorRequeridoMixin
from apps.curadoria.registro import REGISTRO, EntidadeCuradoria, entidades_por_secao
from apps.curadoria.servicos import (
    ACAO_CRIACAO,
    ACAO_EDICAO,
    ACAO_EXCLUSAO,
    registrar_operacao,
)


class BaseCuradoriaMixin(CuradorRequeridoMixin):
    """Contexto comum a todas as telas da área."""

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["secoes"] = entidades_por_secao()
        return contexto


class EntidadeMixin(BaseCuradoriaMixin):
    """Resolve a entidade a partir do slug da URL."""

    @property
    def entidade(self) -> EntidadeCuradoria:
        try:
            return REGISTRO[self.kwargs["slug"]]
        except KeyError as erro:
            raise Http404("Entidade de curadoria inexistente.") from erro

    @property
    def model(self):  # usado pelas views genéricas do Django
        return self.entidade.modelo

    def get_form_class(self):
        return self.entidade.formulario

    def get_queryset(self):
        return self.entidade.queryset()

    def get_success_url(self) -> str:
        return reverse("curadoria:lista", args=[self.entidade.slug])

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["entidade"] = self.entidade
        return contexto


# ---------------------------------------------------------------------------
# Painel
# ---------------------------------------------------------------------------


class PainelView(BaseCuradoriaMixin, TemplateView):
    """Porta de entrada da curadoria: volumes, pendências e últimas cargas."""

    template_name = "curadoria/painel.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["secoes_com_totais"] = [
            (
                secao,
                [
                    {"entidade": entidade, "total": entidade.modelo._default_manager.count()}
                    for entidade in entidades
                ],
            )
            for secao, entidades in contexto["secoes"]
        ]
        contexto["semestre_ativo"] = Semestre.objects.atual()
        contexto["ultimas_cargas"] = RegistroCarga.objects.select_related("curador")[:10]
        contexto["pendencias"] = self._pendencias()
        return contexto

    def _pendencias(self) -> list[str]:
        """Sinaliza lacunas que comprometem a qualidade do catálogo."""
        avisos: list[str] = []
        if not Semestre.objects.filter(ativo=True).exists():
            avisos.append("Nenhum semestre está marcado como ativo.")

        sem_horario = (
            Turma.objects.annotate(total=Count("horarios")).filter(total=0).count()
            if Turma.objects.exists()
            else 0
        )
        if sem_horario:
            avisos.append(f"{sem_horario} turma(s) sem nenhum horário cadastrado.")

        sem_carga = ComponenteCurricular.objects.filter(
            Q(carga_horaria__isnull=True) | Q(carga_horaria=0), ativo=True
        ).count()
        if sem_carga:
            avisos.append(f"{sem_carga} componente(s) ativo(s) sem carga horária.")

        matrizes_vazias = (
            MatrizCurricular.objects.annotate(total=Count("componentes")).filter(total=0).count()
        )
        if matrizes_vazias:
            avisos.append(f"{matrizes_vazias} matriz(es) sem componentes vinculados.")

        cursos_sem_matriz = Curso.objects.annotate(total=Count("matrizes")).filter(total=0).count()
        if cursos_sem_matriz:
            avisos.append(f"{cursos_sem_matriz} curso(s) sem matriz curricular.")
        return avisos


# ---------------------------------------------------------------------------
# CRUD genérico
# ---------------------------------------------------------------------------


class ListaView(EntidadeMixin, ListView):
    """Listagem com busca, filtros e paginação (RF15)."""

    template_name = "curadoria/lista.html"
    context_object_name = "objetos"
    paginate_by = 25

    def get_queryset(self):
        consulta = super().get_queryset()

        termo = self.request.GET.get("q", "").strip()
        if termo and self.entidade.busca:
            condicao = Q()
            for campo in self.entidade.busca:
                condicao |= Q(**{f"{campo}__icontains": termo})
            consulta = consulta.filter(condicao)

        for nome in self.entidade.filtros:
            valor = self.request.GET.get(nome)
            if valor in (None, ""):
                continue
            consulta = consulta.filter(**{nome: self._converte(nome, valor)})
        return consulta

    def _converte(self, nome: str, valor: str):
        """Converte o valor do filtro conforme o tipo do campo."""
        campo = self.entidade.modelo._meta.get_field(nome)
        if campo.get_internal_type() == "BooleanField":
            return valor in ("1", "true", "True")
        return valor

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        entidade = self.entidade
        contexto["cabecalhos"] = entidade.cabecalhos()
        contexto["linhas"] = [
            {"objeto": objeto, "valores": entidade.linha(objeto)} for objeto in contexto["objetos"]
        ]
        contexto["termo"] = self.request.GET.get("q", "")
        aplicados = {nome: self.request.GET.get(nome, "") for nome in entidade.filtros}
        contexto["opcoes_de_filtro"] = entidade.opcoes_de_filtro(aplicados)
        contexto["total"] = contexto["paginator"].count if contexto.get("paginator") else 0
        contexto["parametros"] = self._parametros_preservados()
        return contexto

    def _parametros_preservados(self) -> str:
        """Querystring de busca e filtros, para preservá-la na paginação."""
        parametros = self.request.GET.copy()
        parametros.pop("page", None)
        codificados = parametros.urlencode()
        return f"{codificados}&" if codificados else ""


class CriarView(EntidadeMixin, CreateView):
    """Criação de um registro da entidade (RF15)."""

    template_name = "curadoria/formulario.html"

    def form_valid(self, form):
        resposta = super().form_valid(form)
        registrar_operacao(
            curador=self.request.user,
            entidade=self.entidade,
            acao=ACAO_CRIACAO,
            descricao=str(self.object),
        )
        messages.success(self.request, f"{self.entidade.rotulo.capitalize()} criado(a).")
        return resposta

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["acao"] = "Novo registro"
        return contexto


class EditarView(EntidadeMixin, UpdateView):
    """Edição de um registro da entidade (RF15)."""

    template_name = "curadoria/formulario.html"

    def form_valid(self, form):
        resposta = super().form_valid(form)
        registrar_operacao(
            curador=self.request.user,
            entidade=self.entidade,
            acao=ACAO_EDICAO,
            descricao=str(self.object),
        )
        messages.success(self.request, f"{self.entidade.rotulo.capitalize()} atualizado(a).")
        return resposta

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["acao"] = "Editar registro"
        return contexto


class ExcluirView(EntidadeMixin, DeleteView):
    """
    Exclusão de um registro da entidade (RF15).

    O log é gravado antes da remoção, porque a representação textual do objeto
    depende de relações que deixam de existir depois dela.
    """

    template_name = "curadoria/confirmar_exclusao.html"
    context_object_name = "objeto"

    def get_form_class(self):
        # A confirmação não edita campos: o ModelForm da entidade não se aplica.
        return Form

    def form_valid(self, form):
        registrar_operacao(
            curador=self.request.user,
            entidade=self.entidade,
            acao=ACAO_EXCLUSAO,
            descricao=str(self.object),
        )
        messages.success(self.request, f"{self.entidade.rotulo.capitalize()} excluído(a).")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["dependentes"] = self._dependentes()
        return contexto

    def _dependentes(self) -> list[str]:
        """Registros que serão afetados pela exclusão em cascata."""
        resumo: list[str] = []
        for relacao in self.entidade.modelo._meta.related_objects:
            nome = relacao.get_accessor_name()
            gerenciador = getattr(self.object, nome, None)
            if gerenciador is None or not hasattr(gerenciador, "count"):
                continue
            total = gerenciador.count()
            if total:
                rotulo = relacao.related_model._meta.verbose_name_plural
                resumo.append(f"{total} {rotulo}")
        return resumo


# ---------------------------------------------------------------------------
# Log de operações (RF46)
# ---------------------------------------------------------------------------


class RegistroCargaListView(BaseCuradoriaMixin, ListView):
    """Histórico das operações de carga e de edição manual (RF46)."""

    model = RegistroCarga
    template_name = "curadoria/registro_carga.html"
    context_object_name = "registros"
    paginate_by = 50

    def get_queryset(self):
        consulta = RegistroCarga.objects.select_related("curador")
        entidade = self.request.GET.get("entidade")
        if entidade:
            consulta = consulta.filter(entidade=entidade)
        origem = self.request.GET.get("origem")
        if origem:
            consulta = consulta.filter(origem=origem)
        return consulta

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["entidades_registradas"] = (
            RegistroCarga.objects.values_list("entidade", flat=True).distinct().order_by("entidade")
        )
        contexto["origens"] = RegistroCarga.Origem.choices
        contexto["filtros"] = self.request.GET.dict()
        return contexto
