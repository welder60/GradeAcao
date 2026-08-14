"""
Views de perfil, progresso acadêmico e gestão da conta.

Toda view desta camada verifica a titularidade dos dados (RNF18): o queryset é
sempre restrito ao usuário autenticado.
"""

import json

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from apps.catalogo.models import MatrizComponente
from apps.contas.forms import (
    PerfilDiscenteForm,
    ProgressoComponenteForm,
    RegistroEmLoteForm,
)
from apps.contas.models import PerfilDiscente, ProgressoComponente


class PerfilMixin(LoginRequiredMixin):
    """Garante a existência do perfil do usuário autenticado."""

    def get_perfil(self) -> PerfilDiscente:
        perfil, _ = PerfilDiscente.objects.get_or_create(usuario=self.request.user)
        return perfil


class PerfilUpdateView(PerfilMixin, UpdateView):
    """Criação e edição do perfil acadêmico (RF04, RF05)."""

    model = PerfilDiscente
    form_class = PerfilDiscenteForm
    template_name = "contas/perfil_form.html"
    success_url = reverse_lazy("contas:perfil")

    def get_object(self, queryset=None) -> PerfilDiscente:
        return self.get_perfil()

    def form_valid(self, form):
        messages.success(self.request, "Perfil atualizado.")
        return super().form_valid(form)


class ProgressoListView(PerfilMixin, ListView):
    """
    Painel de progresso: situação por componente e totais de créditos
    (RF16, RF18, RF20).
    """

    model = ProgressoComponente
    template_name = "contas/progresso_lista.html"
    context_object_name = "progressos"

    def get_queryset(self):
        return (
            ProgressoComponente.objects.filter(usuario=self.request.user)
            .select_related("componente", "componente_equivalente")
            .order_by("componente__codigo")
        )

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        perfil = self.get_perfil()
        contexto["perfil"] = perfil
        contexto["resumo"] = perfil.resumo_creditos()
        contexto["periodos_restantes"] = perfil.periodos_restantes()
        contexto["form_lote"] = RegistroEmLoteForm()

        if perfil.matriz_id:
            registrados = set(self.get_queryset().values_list("componente_id", flat=True))
            contexto["componentes_sem_registro"] = (
                MatrizComponente.objects.filter(matriz_id=perfil.matriz_id)
                .exclude(componente_id__in=registrados)
                .select_related("componente")
                .order_by("periodo_recomendado", "componente__codigo")
            )
        return contexto


class ProgressoCreateView(PerfilMixin, CreateView):
    """Registro da situação de um componente (RF16, RF17, RF19)."""

    model = ProgressoComponente
    form_class = ProgressoComponenteForm
    template_name = "contas/progresso_form.html"
    success_url = reverse_lazy("contas:progresso")

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        kwargs["usuario"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, "Situação registrada.")
        return super().form_valid(form)


class ProgressoUpdateView(PerfilMixin, UpdateView):
    """Edição da situação declarada."""

    model = ProgressoComponente
    form_class = ProgressoComponenteForm
    template_name = "contas/progresso_form.html"
    success_url = reverse_lazy("contas:progresso")

    def get_queryset(self):
        return ProgressoComponente.objects.filter(usuario=self.request.user)

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        kwargs["usuario"] = self.request.user
        return kwargs


class ProgressoDeleteView(PerfilMixin, DeleteView):
    """Remoção de um registro de progresso."""

    model = ProgressoComponente
    template_name = "contas/progresso_confirmar_exclusao.html"
    success_url = reverse_lazy("contas:progresso")

    def get_queryset(self):
        return ProgressoComponente.objects.filter(usuario=self.request.user)


class ProgressoEmLoteView(PerfilMixin, View):
    """Marcação de vários componentes com a mesma situação (RF16)."""

    def post(self, request, *args, **kwargs):
        form = RegistroEmLoteForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data["status"]
            for componente in form.cleaned_data["componentes"]:
                ProgressoComponente.objects.update_or_create(
                    usuario=request.user,
                    componente=componente,
                    defaults={"status": status},
                )
            messages.success(request, "Situações atualizadas.")
        else:
            messages.error(request, "Não foi possível registrar as situações.")

        from django.shortcuts import redirect

        return redirect("contas:progresso")


class ExportarDadosView(PerfilMixin, View):
    """Exportação dos dados pessoais em formato legível por máquina (RF44)."""

    def get(self, request, *args, **kwargs):
        perfil = self.get_perfil()
        dados = {
            "conta": {
                "usuario": request.user.get_username(),
                "email": request.user.email,
                "criado_em": request.user.date_joined.isoformat(),
            },
            "perfil": {
                "matriz": str(perfil.matriz) if perfil.matriz else None,
                "periodo_ingresso": perfil.periodo_ingresso,
                "media_creditos_por_periodo": perfil.media_creditos_por_periodo,
            },
            "progresso": [
                {
                    "componente": p.componente.codigo,
                    "status": p.status,
                    "natureza": p.natureza,
                    "por_equivalencia": p.por_equivalencia,
                }
                for p in ProgressoComponente.objects.filter(usuario=request.user).select_related(
                    "componente"
                )
            ],
            "grades": [
                {
                    "nome": g.nome,
                    "semestre": g.semestre.codigo,
                    "valida": g.valida,
                    "turmas": [
                        {
                            "componente": i.turma.componente.codigo,
                            "turma": i.turma.codigo,
                            "prioridade": i.prioridade,
                        }
                        for i in g.itens.select_related("turma__componente")
                    ],
                }
                for g in request.user.grades.select_related("semestre")
            ],
            "aviso": (
                "Documento gerado por ferramenta não oficial. Não constitui "
                "comprovante de matrícula (RF41)."
            ),
        }

        resposta = HttpResponse(
            json.dumps(dados, ensure_ascii=False, indent=2),
            content_type="application/json; charset=utf-8",
        )
        resposta["Content-Disposition"] = 'attachment; filename="meus-dados-gradeacao.json"'
        return resposta


class ExcluirContaView(LoginRequiredMixin, TemplateView):
    """
    Exclusão da conta e de todos os dados associados (RF05, RN13).

    A remoção é física: os `ON DELETE CASCADE` a partir de `auth_user` apagam
    perfil, progresso e grades.
    """

    template_name = "contas/excluir_conta.html"

    def post(self, request, *args, **kwargs):
        from django.shortcuts import redirect

        usuario = request.user
        logout(request)
        usuario.delete()
        messages.success(request, "Conta e dados associados foram excluídos.")
        return redirect("comum:pagina_inicial")
