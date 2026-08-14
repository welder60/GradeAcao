"""
Modelos de planejamento de grade horária.

Referência: docs/arquitetura/modelo-de-dados.md, seções 3.13 e 3.14.
"""

import uuid

from django.conf import settings
from django.db import models

from apps.catalogo.models import Semestre, Turma
from apps.comum.models import ModeloAuditado


class GradeQuerySet(models.QuerySet):
    """Consultas reutilizáveis sobre grades."""

    def do_usuario(self, usuario) -> "GradeQuerySet":
        """Restringe às grades do titular informado (RNF18)."""
        return self.filter(usuario=usuario)

    def com_relacionados(self) -> "GradeQuerySet":
        return self.select_related("semestre").prefetch_related(
            "itens__turma__componente",
            "itens__turma__horarios__codigo_dia",
            "itens__turma__horarios__codigo_horario",
            "itens__turma__horarios__campus",
        )


class Grade(ModeloAuditado):
    """Cenário de grade horária montado por um discente para um semestre."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="usuário",
        on_delete=models.CASCADE,
        related_name="grades",
    )
    semestre = models.ForeignKey(
        Semestre, verbose_name="semestre", on_delete=models.CASCADE, related_name="grades"
    )
    nome = models.CharField("nome", max_length=80)
    valida = models.BooleanField(
        "válida", default=True, help_text="Falso para rascunho com choque (RN02)."
    )
    preferida = models.BooleanField("preferida", default=False)
    token_publico = models.UUIDField(
        "token público",
        null=True,
        blank=True,
        unique=True,
        help_text="Token do link somente-leitura (RF40).",
    )

    objects = GradeQuerySet.as_manager()

    class Meta:
        db_table = "grade"
        verbose_name = "grade"
        verbose_name_plural = "grades"
        ordering = ["-atualizado_em"]
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "semestre", "nome"], name="grade_nome_unico_por_semestre"
            ),
            models.UniqueConstraint(
                fields=["usuario", "semestre"],
                condition=models.Q(preferida=True),
                name="grade_preferida_unica_por_semestre",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.nome} ({self.semestre.codigo})"

    # -- Compartilhamento (RF40) -------------------------------------------

    def publicar(self) -> uuid.UUID:
        """Gera (ou reaproveita) o token do link somente-leitura."""
        if not self.token_publico:
            self.token_publico = uuid.uuid4()
            self.save(update_fields=["token_publico", "atualizado_em"])
        return self.token_publico

    def revogar_link(self) -> None:
        """Revoga o link público a qualquer momento (RF40)."""
        self.token_publico = None
        self.save(update_fields=["token_publico", "atualizado_em"])

    # -- Totalizadores (RF27) ----------------------------------------------

    def turmas_principais(self):
        return Turma.objects.filter(
            itens_de_grade__grade=self,
            itens_de_grade__prioridade=GradeTurma.Prioridade.PRINCIPAL,
        )

    @property
    def total_creditos(self) -> int:
        return sum(turma.componente.creditos for turma in self.turmas_principais())

    @property
    def carga_horaria_semanal(self) -> int:
        """Número de blocos semanais ocupados pelas turmas principais."""
        from apps.catalogo.models import TurmaHorario

        return TurmaHorario.objects.filter(turma__in=self.turmas_principais()).count()


class GradeTurma(models.Model):
    """Associação entre uma grade e as turmas que a compõem."""

    class Prioridade(models.TextChoices):
        PRINCIPAL = "PRINCIPAL", "Principal"
        ALTERNATIVA = "ALTERNATIVA", "Alternativa"

    grade = models.ForeignKey(
        Grade, verbose_name="grade", on_delete=models.CASCADE, related_name="itens"
    )
    turma = models.ForeignKey(
        Turma, verbose_name="turma", on_delete=models.CASCADE, related_name="itens_de_grade"
    )
    prioridade = models.CharField(
        "prioridade",
        max_length=12,
        choices=Prioridade.choices,
        default=Prioridade.PRINCIPAL,
        help_text="Classificação da turma no cenário (RF29).",
    )
    choque_reconhecido = models.BooleanField(
        "choque reconhecido pelo discente",
        default=False,
        help_text="Permite gravar a grade mesmo com choque (RF23).",
    )
    adicionado_em = models.DateTimeField("adicionado em", auto_now_add=True)

    class Meta:
        db_table = "grade_turma"
        verbose_name = "turma da grade"
        verbose_name_plural = "turmas da grade"
        ordering = ["turma__componente__codigo"]
        constraints = [
            models.UniqueConstraint(fields=["grade", "turma"], name="grade_turma_unica"),
        ]

    def __str__(self) -> str:
        return f"{self.grade.nome} · {self.turma}"


class RestricaoDisponibilidade(models.Model):
    """
    Faixa de indisponibilidade declarada pelo discente (RF28).

    Turmas com encontro no dia e bloco declarados são ocultadas da oferta.
    """

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="usuário",
        on_delete=models.CASCADE,
        related_name="restricoes",
    )
    codigo_dia = models.ForeignKey(
        "comum.CodigoDia",
        verbose_name="dia da semana",
        on_delete=models.CASCADE,
        related_name="restricoes",
    )
    codigo_horario = models.ForeignKey(
        "comum.CodigoHorario",
        verbose_name="bloco de horário",
        on_delete=models.CASCADE,
        related_name="restricoes",
    )
    motivo = models.CharField("motivo", max_length=120, blank=True)

    class Meta:
        db_table = "restricao_disponibilidade"
        verbose_name = "restrição de disponibilidade"
        verbose_name_plural = "restrições de disponibilidade"
        ordering = ["codigo_dia__ordem", "codigo_horario__ordem"]
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "codigo_dia", "codigo_horario"],
                name="restricao_disponibilidade_unica",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.codigo_dia.codigo}{self.codigo_horario.codigo}"
