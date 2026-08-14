"""
Views de montagem, visualização e compartilhamento de grades.

Todas as views de escrita restringem o queryset ao titular da grade (RNF18).
A visualização por token público é a única exceção e é somente-leitura (RF40).
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
    View,
)

from apps.catalogo.models import Semestre, Turma
from apps.comum.models import CodigoDia
from apps.planejamento.forms import (
    AdicionarTurmaForm,
    CompararGradesForm,
    DuplicarGradeForm,
    GradeForm,
    ReconhecerChoqueForm,
    RestricaoDisponibilidadeForm,
)
from apps.planejamento.models import Grade, GradeTurma, RestricaoDisponibilidade
from apps.planejamento.regras.horarios import dias_sem_aula, janelas_livres
from apps.planejamento.servicos import (
    adicionar_turma,
    alertas_da_grade,
    atualizar_validade,
    choques_da_grade,
    definir_preferida,
    duplicar_grade,
    encontros_da_grade,
    grade_para_calendario,
    remover_turma,
)


class GradeDoUsuarioMixin(LoginRequiredMixin):
    """Restringe o acesso às grades do usuário autenticado (RNF18)."""

    def get_queryset(self):
        return Grade.objects.do_usuario(self.request.user).select_related("semestre")


class GradeListView(GradeDoUsuarioMixin, ListView):
    """Grades salvas pelo discente, agrupadas por semestre (RF31)."""

    model = Grade
    template_name = "planejamento/grade_lista.html"
    context_object_name = "grades"

    def get_queryset(self):
        consulta = super().get_queryset()
        codigo = self.request.GET.get("semestre")
        if codigo:
            consulta = consulta.filter(semestre__codigo=codigo)
        return consulta.order_by("-preferida", "-atualizado_em")

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["semestres"] = Semestre.objects.order_by("-ano", "-periodo")
        contexto["semestre_ativo"] = Semestre.objects.atual()
        return contexto


class GradeCreateView(LoginRequiredMixin, CreateView):
    """Criação de um novo cenário de grade (RF31)."""

    model = Grade
    form_class = GradeForm
    template_name = "planejamento/grade_form.html"

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        kwargs["usuario"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse("planejamento:grade_montar", args=[self.object.pk])


class GradeUpdateView(GradeDoUsuarioMixin, UpdateView):
    """Renomeação de uma grade salva (RF32)."""

    model = Grade
    form_class = GradeForm
    template_name = "planejamento/grade_form.html"

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        kwargs["usuario"] = self.request.user
        return kwargs

    def get_success_url(self) -> str:
        return reverse("planejamento:grade_detalhe", args=[self.object.pk])


class GradeDeleteView(GradeDoUsuarioMixin, DeleteView):
    """Exclusão de uma grade salva (RF32)."""

    model = Grade
    template_name = "planejamento/grade_confirmar_exclusao.html"
    success_url = reverse_lazy("planejamento:grade_lista")


class GradeContextoMixin:
    """Monta o contexto compartilhado pelas telas de uma grade."""

    def contexto_da_grade(self, grade: Grade) -> dict:
        encontros = encontros_da_grade(grade)
        return {
            "grade": grade,
            "itens": grade.itens.select_related("turma__componente").prefetch_related(
                "turma__horarios__codigo_dia",
                "turma__horarios__codigo_horario",
                "turma__horarios__campus",
                "turma__docentes",
            ),
            "choques": choques_da_grade(grade),
            "alertas": alertas_da_grade(grade),
            "calendario": grade_para_calendario(grade),
            "total_creditos": grade.total_creditos,
            "carga_horaria_semanal": grade.carga_horaria_semanal,
            "dias_sem_aula": dias_sem_aula(
                encontros, list(CodigoDia.objects.values_list("codigo", flat=True))
            ),
            "janelas_livres": janelas_livres(encontros),
            # RF41 — todo compartilhamento e exportação leva este aviso.
            "aviso_nao_oficial": (
                "Documento gerado por ferramenta não oficial. Não constitui "
                "comprovante de matrícula."
            ),
        }


class GradeDetailView(GradeDoUsuarioMixin, GradeContextoMixin, DetailView):
    """
    Visualização da grade em calendário semanal e em lista (RF35, RF36).

    O template alterna entre os formatos; ambos os dados vão no contexto.
    """

    model = Grade
    template_name = "planejamento/grade_detalhe.html"
    context_object_name = "grade"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto.update(self.contexto_da_grade(self.object))
        contexto["formato"] = self.request.GET.get("formato", "calendario")
        return contexto


class GradeMontarView(GradeDoUsuarioMixin, GradeContextoMixin, DetailView):
    """
    Tela de montagem: oferta filtrável ao lado da grade em construção
    (RF21, RF22, RF24, RF25, RF26, RF27).
    """

    model = Grade
    template_name = "planejamento/grade_montar.html"
    context_object_name = "grade"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        grade = self.object
        contexto.update(self.contexto_da_grade(grade))
        contexto["form_turma"] = AdicionarTurmaForm(grade=grade)
        contexto["form_choque"] = ReconhecerChoqueForm(grade=grade)

        selecionadas = set(grade.itens.values_list("turma_id", flat=True))
        contexto["turmas_disponiveis"] = (
            Turma.objects.filter(semestre=grade.semestre)
            .exclude(pk__in=selecionadas)
            .select_related("componente")
            .prefetch_related("horarios__codigo_dia", "horarios__codigo_horario")
            .order_by("componente__codigo", "codigo")[:200]
        )
        return contexto


class AdicionarTurmaView(GradeDoUsuarioMixin, View):
    """Inclusão de uma turma na grade (RF21)."""

    def post(self, request, pk, *args, **kwargs):
        grade = get_object_or_404(self.get_queryset(), pk=pk)
        form = AdicionarTurmaForm(request.POST, grade=grade)
        if form.is_valid():
            try:
                adicionar_turma(
                    grade,
                    form.cleaned_data["turma"],
                    form.cleaned_data.get("prioridade") or None,
                )
            except ValidationError as erro:
                messages.error(request, erro.message)
            else:
                messages.success(request, "Turma adicionada à grade.")
        else:
            messages.error(request, "Turma inválida para esta grade.")
        return redirect("planejamento:grade_montar", pk=grade.pk)


class RemoverTurmaView(GradeDoUsuarioMixin, View):
    """Remoção de uma turma da grade (RF21)."""

    def post(self, request, pk, turma_id, *args, **kwargs):
        grade = get_object_or_404(self.get_queryset(), pk=pk)
        remover_turma(grade, turma_id)
        messages.success(request, "Turma removida da grade.")
        return redirect("planejamento:grade_montar", pk=grade.pk)


class ReconhecerChoqueView(GradeDoUsuarioMixin, View):
    """
    Reconhecimento de choques pelo discente (RF23).

    Enquanto houver choque não reconhecido, a grade permanece inválida (RN02).
    """

    def post(self, request, pk, *args, **kwargs):
        grade = get_object_or_404(self.get_queryset(), pk=pk)
        form = ReconhecerChoqueForm(request.POST, grade=grade)
        if form.is_valid():
            reconhecidas = [t.pk for t in form.cleaned_data["turmas"]]
            GradeTurma.objects.filter(grade=grade).update(choque_reconhecido=False)
            GradeTurma.objects.filter(grade=grade, turma_id__in=reconhecidas).update(
                choque_reconhecido=True
            )
            valida = atualizar_validade(grade)
            messages.success(
                request,
                "Grade gravada." if valida else "Ainda há choque não reconhecido.",
            )
        return redirect("planejamento:grade_montar", pk=grade.pk)


class DuplicarGradeView(GradeDoUsuarioMixin, FormView):
    """Duplicação de uma grade salva (RF32)."""

    form_class = DuplicarGradeForm
    template_name = "planejamento/grade_duplicar.html"

    def dispatch(self, request, *args, **kwargs):
        self.grade = get_object_or_404(
            Grade.objects.do_usuario(request.user)
            if request.user.is_authenticated
            else Grade.objects.none(),
            pk=kwargs["pk"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self) -> dict:
        return {"nome": f"{self.grade.nome} (cópia)"}

    def form_valid(self, form):
        self.copia = duplicar_grade(self.grade, form.cleaned_data["nome"])
        messages.success(self.request, "Grade duplicada.")
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse("planejamento:grade_detalhe", args=[self.copia.pk])


class DefinirPreferidaView(GradeDoUsuarioMixin, View):
    """Marcação da grade preferida do semestre (RF34)."""

    def post(self, request, pk, *args, **kwargs):
        grade = get_object_or_404(self.get_queryset(), pk=pk)
        definir_preferida(grade)
        messages.success(request, f"'{grade.nome}' definida como preferida.")
        return redirect("planejamento:grade_lista")


class CompartilharGradeView(GradeDoUsuarioMixin, View):
    """Geração e revogação do link público somente-leitura (RF40)."""

    def post(self, request, pk, *args, **kwargs):
        grade = get_object_or_404(self.get_queryset(), pk=pk)
        if request.POST.get("acao") == "revogar":
            grade.revogar_link()
            messages.success(request, "Link público revogado.")
        else:
            grade.publicar()
            messages.success(request, "Link público gerado.")
        return redirect("planejamento:grade_detalhe", pk=grade.pk)


class GradePublicaView(GradeContextoMixin, DetailView):
    """
    Visualização somente-leitura por token público (RF40, RF41).

    Não exige autenticação e não expõe identificação do titular.
    """

    model = Grade
    template_name = "planejamento/grade_publica.html"
    context_object_name = "grade"

    def get_object(self, queryset=None) -> Grade:
        return get_object_or_404(
            Grade.objects.exclude(token_publico__isnull=True).select_related("semestre"),
            token_publico=self.kwargs["token"],
        )

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto.update(self.contexto_da_grade(self.object))
        contexto["somente_leitura"] = True
        return contexto


class CompararGradesView(LoginRequiredMixin, GradeContextoMixin, FormView):
    """Comparação lado a lado de duas ou três grades (RF33)."""

    form_class = CompararGradesForm
    template_name = "planejamento/grade_comparar.html"

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        kwargs["usuario"] = self.request.user
        if self.request.GET.get("grades"):
            kwargs["data"] = self.request.GET
        return kwargs

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        form = contexto["form"]
        if form.is_bound and form.is_valid():
            colunas = [self.contexto_da_grade(g) for g in form.cleaned_data["grades"]]
            contexto["colunas"] = colunas

            conjuntos = [{i.turma.componente.codigo for i in coluna["itens"]} for coluna in colunas]
            comuns = set.intersection(*conjuntos) if conjuntos else set()
            for coluna, conjunto in zip(colunas, conjuntos, strict=True):
                coluna["componentes_exclusivos"] = sorted(conjunto - comuns)
            contexto["componentes_comuns"] = sorted(comuns)
        return contexto


class RestricaoListView(LoginRequiredMixin, ListView):
    """Restrições de disponibilidade declaradas pelo discente (RF28)."""

    model = RestricaoDisponibilidade
    template_name = "planejamento/restricao_lista.html"
    context_object_name = "restricoes"

    def get_queryset(self):
        return RestricaoDisponibilidade.objects.filter(usuario=self.request.user).select_related(
            "codigo_dia", "codigo_horario"
        )

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["form"] = RestricaoDisponibilidadeForm()
        return contexto


class RestricaoCreateView(LoginRequiredMixin, CreateView):
    """Registro de uma faixa de indisponibilidade (RF28)."""

    model = RestricaoDisponibilidade
    form_class = RestricaoDisponibilidadeForm
    template_name = "planejamento/restricao_lista.html"
    success_url = reverse_lazy("planejamento:restricao_lista")

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)


class RestricaoDeleteView(LoginRequiredMixin, DeleteView):
    """Remoção de uma restrição de disponibilidade."""

    model = RestricaoDisponibilidade
    template_name = "planejamento/restricao_confirmar_exclusao.html"
    success_url = reverse_lazy("planejamento:restricao_lista")

    def get_queryset(self):
        return RestricaoDisponibilidade.objects.filter(usuario=self.request.user)
