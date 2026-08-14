"""Formulários de montagem e gestão de grades."""

from django import forms

from apps.catalogo.models import Semestre, Turma
from apps.planejamento.models import Grade, GradeTurma, RestricaoDisponibilidade


class GradeForm(forms.ModelForm):
    """Criação e renomeação de cenários de grade (RF31, RF32)."""

    class Meta:
        model = Grade
        fields = ["nome", "semestre"]

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario
        self.fields["semestre"].queryset = Semestre.objects.order_by("-ano", "-periodo")
        semestre_ativo = Semestre.objects.atual()
        if semestre_ativo and not self.instance.pk:
            self.fields["semestre"].initial = semestre_ativo

    def clean(self) -> dict:
        dados = super().clean()
        nome, semestre = dados.get("nome"), dados.get("semestre")
        if nome and semestre and self.usuario:
            duplicada = Grade.objects.filter(
                usuario=self.usuario, semestre=semestre, nome=nome
            ).exclude(pk=self.instance.pk)
            if duplicada.exists():
                self.add_error("nome", "Você já possui uma grade com este nome neste semestre.")
        return dados


class DuplicarGradeForm(forms.Form):
    """Cópia de uma grade existente (RF32)."""

    nome = forms.CharField(label="nome da cópia", max_length=80)


class AdicionarTurmaForm(forms.Form):
    """Inclusão de turma na grade em construção (RF21, RF29)."""

    turma = forms.ModelChoiceField(label="turma", queryset=Turma.objects.none())
    prioridade = forms.ChoiceField(
        label="prioridade",
        choices=GradeTurma.Prioridade.choices,
        initial=GradeTurma.Prioridade.PRINCIPAL,
        required=False,
    )

    def __init__(self, *args, grade: Grade | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if grade is not None:
            # RN09: apenas turmas do mesmo período letivo da grade.
            self.fields["turma"].queryset = Turma.objects.filter(
                semestre=grade.semestre
            ).select_related("componente")


class ReconhecerChoqueForm(forms.Form):
    """
    Reconhecimento explícito de um choque de horário (RF23).

    Sem este reconhecimento, a grade permanece com `valida = False`.
    """

    turmas = forms.ModelMultipleChoiceField(
        label="turmas com choque reconhecido",
        queryset=Turma.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, grade: Grade | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if grade is not None:
            self.fields["turmas"].queryset = Turma.objects.filter(
                itens_de_grade__grade=grade
            ).select_related("componente")


class RestricaoDisponibilidadeForm(forms.ModelForm):
    """Declaração de indisponibilidade por dia e bloco (RF28)."""

    class Meta:
        model = RestricaoDisponibilidade
        fields = ["codigo_dia", "codigo_horario", "motivo"]


class CompararGradesForm(forms.Form):
    """Seleção de duas ou três grades para comparação (RF33)."""

    grades = forms.ModelMultipleChoiceField(
        label="grades", queryset=Grade.objects.none(), widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        if usuario is not None:
            self.fields["grades"].queryset = Grade.objects.do_usuario(usuario).select_related(
                "semestre"
            )

    def clean_grades(self):
        grades = self.cleaned_data["grades"]
        if not 2 <= len(grades) <= 3:
            raise forms.ValidationError("Selecione duas ou três grades para comparar.")
        if len({g.semestre_id for g in grades}) > 1:
            raise forms.ValidationError("A comparação exige grades do mesmo período letivo.")
        return grades
