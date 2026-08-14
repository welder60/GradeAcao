"""
Formulários de curadoria dos dados públicos (RF15).

Cada formulário cobre uma entidade do catálogo, da oferta ou das tabelas de
domínio. As validações aqui traduzem para o curador as restrições declaradas
no banco (constraints de `apps.catalogo.models` e `apps.comum.models`), de
modo que o erro apareça no campo, e não como falha de integridade.
"""

from django import forms

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


def valida_semestre_textual(valor: str, rotulo: str = "período") -> str:
    """Valida um código de período letivo no formato AAAAP."""
    valor = (valor or "").strip()
    if not valor:
        return valor
    if not (valor.isdigit() and len(valor) == 5):
        raise forms.ValidationError(f"Informe o {rotulo} no formato AAAAP, ex.: 20241.")
    if valor[-1] not in "012":
        raise forms.ValidationError(f"O {rotulo} deve terminar em 0, 1 ou 2.")
    return valor


class FormularioDeCuradoria(forms.ModelForm):
    """Base dos formulários da área: aplica a classe CSS padrão aos campos."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            widget = campo.widget
            if isinstance(widget, forms.CheckboxInput | forms.CheckboxSelectMultiple):
                continue
            classes = widget.attrs.get("class", "")
            widget.attrs["class"] = f"{classes} campo".strip()


# ---------------------------------------------------------------------------
# Tabelas de domínio
# ---------------------------------------------------------------------------


class CampusForm(FormularioDeCuradoria):
    class Meta:
        model = Campus
        fields = ["codigo", "nome"]


class CodigoDiaForm(FormularioDeCuradoria):
    class Meta:
        model = CodigoDia
        fields = ["codigo", "dia_da_semana", "ordem"]


class CodigoHorarioForm(FormularioDeCuradoria):
    class Meta:
        model = CodigoHorario
        fields = ["codigo", "horario", "hora_inicio", "hora_fim", "turno", "ordem"]
        widgets = {
            "hora_inicio": forms.TimeInput(attrs={"type": "time"}),
            "hora_fim": forms.TimeInput(attrs={"type": "time"}),
        }

    def clean(self) -> dict:
        dados = super().clean()
        inicio, fim = dados.get("hora_inicio"), dados.get("hora_fim")
        if inicio and fim and inicio >= fim:
            self.add_error("hora_fim", "A hora de término deve ser posterior à de início.")
        return dados


# ---------------------------------------------------------------------------
# Estrutura acadêmica
# ---------------------------------------------------------------------------


class CursoForm(FormularioDeCuradoria):
    class Meta:
        model = Curso
        fields = ["nome", "codigo", "campus", "turno"]

    def clean_codigo(self) -> str | None:
        # A coluna é UNIQUE e admite NULL, mas não repetição de string vazia.
        return (self.cleaned_data.get("codigo") or "").strip() or None


class MatrizCurricularForm(FormularioDeCuradoria):
    class Meta:
        model = MatrizCurricular
        fields = [
            "curso",
            "nome",
            "codigo",
            "vigencia_inicio",
            "vigencia_fim",
            "carga_horaria_minima_periodo_letivo",
            "carga_horaria_maxima_periodo_letivo",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["curso"].queryset = Curso.objects.order_by("nome")

    def clean_vigencia_inicio(self) -> str:
        return valida_semestre_textual(
            self.cleaned_data.get("vigencia_inicio"), "início de vigência"
        )

    def clean_vigencia_fim(self) -> str:
        return valida_semestre_textual(self.cleaned_data.get("vigencia_fim"), "fim de vigência")

    def clean(self) -> dict:
        dados = super().clean()
        minima = dados.get("carga_horaria_minima_periodo_letivo")
        maxima = dados.get("carga_horaria_maxima_periodo_letivo")
        if minima is not None and maxima is not None and minima > maxima:
            self.add_error(
                "carga_horaria_maxima_periodo_letivo",
                "A carga horária máxima não pode ser menor que a mínima.",
            )
        return dados


class ComponenteCurricularForm(FormularioDeCuradoria):
    class Meta:
        model = ComponenteCurricular
        fields = ["codigo", "nome", "carga_horaria", "departamento", "ementa", "ativo"]
        widgets = {"ementa": forms.Textarea(attrs={"rows": 4})}

    def clean_codigo(self) -> str:
        return (self.cleaned_data.get("codigo") or "").strip().upper()


class ComponenteRelacaoForm(FormularioDeCuradoria):
    """Pré-requisito, co-requisito ou equivalência entre componentes (RN06)."""

    class Meta:
        model = ComponenteRelacao
        fields = [
            "componente",
            "tipo",
            "componente_relacionado",
            "grupo",
            "bidirecional",
            "observacao",
        ]
        widgets = {"observacao": forms.Textarea(attrs={"rows": 2})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ativos = ComponenteCurricular.objects.order_by("codigo")
        self.fields["componente"].queryset = ativos
        self.fields["componente_relacionado"].queryset = ativos

    def clean(self) -> dict:
        dados = super().clean()
        componente = dados.get("componente")
        relacionado = dados.get("componente_relacionado")
        tipo = dados.get("tipo")

        if componente and relacionado and componente == relacionado:
            self.add_error(
                "componente_relacionado",
                "Um componente não se relaciona consigo mesmo.",
            )
        elif componente and relacionado and tipo:
            duplicada = ComponenteRelacao.objects.filter(
                componente=componente, componente_relacionado=relacionado, tipo=tipo
            ).exclude(pk=self.instance.pk)
            if duplicada.exists():
                self.add_error("componente_relacionado", "Esta relação já está cadastrada.")

        if dados.get("bidirecional") and tipo != ComponenteRelacao.Tipo.EQUIVALENCIA:
            self.add_error(
                "bidirecional",
                "Somente equivalências podem ser bidirecionais (RN06).",
            )
        return dados


class MatrizComponenteForm(FormularioDeCuradoria):
    class Meta:
        model = MatrizComponente
        fields = ["matriz", "componente", "periodo_recomendado", "natureza"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["matriz"].queryset = MatrizCurricular.objects.select_related("curso").order_by(
            "curso__nome", "-vigencia_inicio"
        )
        self.fields["componente"].queryset = ComponenteCurricular.objects.order_by("codigo")

    def clean(self) -> dict:
        dados = super().clean()
        matriz, componente = dados.get("matriz"), dados.get("componente")
        if matriz and componente:
            duplicado = MatrizComponente.objects.filter(
                matriz=matriz, componente=componente
            ).exclude(pk=self.instance.pk)
            if duplicado.exists():
                self.add_error("componente", "Este componente já consta desta matriz.")
        return dados


# ---------------------------------------------------------------------------
# Oferta
# ---------------------------------------------------------------------------


class SemestreForm(FormularioDeCuradoria):
    """Período letivo. O código é derivado de ano e período quando omitido."""

    class Meta:
        model = Semestre
        fields = ["ano", "periodo", "codigo", "data_inicio", "data_fim", "ativo"]
        widgets = {
            "data_inicio": forms.DateInput(attrs={"type": "date"}),
            "data_fim": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["codigo"].required = False
        self.fields["codigo"].help_text = "Deixe vazio para gerar a partir do ano e do período."

    def clean(self) -> dict:
        dados = super().clean()
        ano, periodo = dados.get("ano"), dados.get("periodo")
        if not dados.get("codigo") and ano is not None and periodo is not None:
            dados["codigo"] = f"{ano}{periodo}"
            self.instance.codigo = dados["codigo"]

        inicio, fim = dados.get("data_inicio"), dados.get("data_fim")
        if inicio and fim and inicio > fim:
            self.add_error("data_fim", "O fim das aulas deve ser posterior ao início.")
        return dados


class DocenteForm(FormularioDeCuradoria):
    """Docente da oferta. Apenas o nome divulgado publicamente (RNF17)."""

    class Meta:
        model = Docente
        fields = ["nome"]


class TurmaForm(FormularioDeCuradoria):
    class Meta:
        model = Turma
        fields = [
            "semestre",
            "componente",
            "codigo",
            "modalidade",
            "vagas_ofertadas",
            "vagas_ocupadas",
            "coletado_em",
            "observacao",
        ]
        widgets = {
            "observacao": forms.Textarea(attrs={"rows": 2}),
            "coletado_em": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["semestre"].queryset = Semestre.objects.order_by("-ano", "-periodo")
        self.fields["componente"].queryset = ComponenteCurricular.objects.order_by("codigo")

    def clean(self) -> dict:
        dados = super().clean()
        ofertadas, ocupadas = dados.get("vagas_ofertadas"), dados.get("vagas_ocupadas")
        if ofertadas is not None and ocupadas is not None and ocupadas > ofertadas:
            self.add_error(
                "vagas_ocupadas",
                "As vagas ocupadas não podem exceder as ofertadas.",
            )

        semestre, componente, codigo = (
            dados.get("semestre"),
            dados.get("componente"),
            dados.get("codigo"),
        )
        if semestre and componente and codigo:
            duplicada = Turma.objects.filter(
                semestre=semestre, componente=componente, codigo=codigo
            ).exclude(pk=self.instance.pk)
            if duplicada.exists():
                self.add_error("codigo", "Já existe esta turma para o componente no semestre.")
        return dados


class TurmaHorarioForm(FormularioDeCuradoria):
    """Encontro semanal de uma turma: dia, bloco, campus e local."""

    class Meta:
        model = TurmaHorario
        fields = ["turma", "codigo_dia", "codigo_horario", "campus", "local"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["turma"].queryset = Turma.objects.select_related(
            "componente", "semestre"
        ).order_by("-semestre__ano", "componente__codigo", "codigo")

    def clean(self) -> dict:
        dados = super().clean()
        turma, dia, horario = (
            dados.get("turma"),
            dados.get("codigo_dia"),
            dados.get("codigo_horario"),
        )
        if turma and dia and horario:
            duplicado = TurmaHorario.objects.filter(
                turma=turma, codigo_dia=dia, codigo_horario=horario
            ).exclude(pk=self.instance.pk)
            if duplicado.exists():
                self.add_error("codigo_horario", "Este encontro já está registrado na turma.")
        return dados


class TurmaDocenteForm(FormularioDeCuradoria):
    class Meta:
        model = TurmaDocente
        fields = ["turma", "docente"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["turma"].queryset = Turma.objects.select_related(
            "componente", "semestre"
        ).order_by("-semestre__ano", "componente__codigo", "codigo")
        self.fields["docente"].queryset = Docente.objects.order_by("nome")

    def clean(self) -> dict:
        dados = super().clean()
        turma, docente = dados.get("turma"), dados.get("docente")
        if turma and docente:
            duplicado = TurmaDocente.objects.filter(turma=turma, docente=docente).exclude(
                pk=self.instance.pk
            )
            if duplicado.exists():
                self.add_error("docente", "Este docente já está vinculado à turma.")
        return dados
