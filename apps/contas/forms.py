"""Formulários de perfil e progresso acadêmico."""

from django import forms

from apps.catalogo.models import ComponenteCurricular, Curso, MatrizCurricular
from apps.contas.models import PerfilDiscente, ProgressoComponente


class PerfilDiscenteForm(forms.ModelForm):
    """Registro do perfil acadêmico declarado (RF04)."""

    curso = forms.ModelChoiceField(
        label="curso",
        queryset=Curso.objects.select_related("campus").order_by("nome"),
        required=False,
        help_text="Selecione o curso para filtrar as matrizes disponíveis.",
    )

    class Meta:
        model = PerfilDiscente
        fields = ["curso", "matriz", "periodo_ingresso", "media_creditos_por_periodo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["matriz"].queryset = MatrizCurricular.objects.select_related("curso").order_by(
            "curso__nome", "-vigencia_inicio"
        )

        curso_id = self.data.get("curso") or (
            self.instance.matriz.curso_id if self.instance.pk and self.instance.matriz_id else None
        )
        if curso_id:
            self.fields["matriz"].queryset = self.fields["matriz"].queryset.filter(
                curso_id=curso_id
            )
            self.fields["curso"].initial = curso_id

    def clean_periodo_ingresso(self) -> str:
        valor = (self.cleaned_data.get("periodo_ingresso") or "").strip()
        if not valor:
            return valor
        if not (valor.isdigit() and len(valor) == 5):
            raise forms.ValidationError("Informe o período no formato AAAAP, ex.: 20241.")
        if valor[-1] not in "012":
            raise forms.ValidationError("O período deve terminar em 0, 1 ou 2.")
        return valor


class ProgressoComponenteForm(forms.ModelForm):
    """
    Registro da situação de um componente (RF16, RF17, RF19).

    Componentes fora da matriz devem ser classificados como optativos ou de
    módulo livre.
    """

    class Meta:
        model = ProgressoComponente
        fields = [
            "componente",
            "status",
            "natureza",
            "por_equivalencia",
            "componente_equivalente",
        ]

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario
        ativos = ComponenteCurricular.objects.filter(ativo=True).order_by("codigo")
        self.fields["componente"].queryset = ativos
        self.fields["componente_equivalente"].queryset = ativos
        self.fields["componente_equivalente"].required = False

    def clean(self) -> dict:
        dados = super().clean()
        if dados.get("por_equivalencia") and not dados.get("componente_equivalente"):
            self.add_error(
                "componente_equivalente",
                "Informe o componente aproveitado como equivalente.",
            )
        if dados.get("componente_equivalente") == dados.get("componente"):
            self.add_error(
                "componente_equivalente",
                "O componente equivalente deve ser diferente do componente cursado.",
            )

        componente = dados.get("componente")
        if componente and self.usuario:
            duplicado = ProgressoComponente.objects.filter(
                usuario=self.usuario, componente=componente
            ).exclude(pk=self.instance.pk)
            if duplicado.exists():
                self.add_error("componente", "Este componente já possui situação registrada.")
        return dados


class RegistroEmLoteForm(forms.Form):
    """Marcação rápida de vários componentes com a mesma situação (RF16)."""

    componentes = forms.ModelMultipleChoiceField(
        label="componentes",
        queryset=ComponenteCurricular.objects.filter(ativo=True).order_by("codigo"),
        widget=forms.CheckboxSelectMultiple,
    )
    status = forms.ChoiceField(label="situação", choices=ProgressoComponente.Status.choices)
