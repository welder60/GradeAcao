"""
Modelos de perfil e progresso acadêmico do discente.

Todos os registros deste módulo são **declaratórios** (RN12): não há
verificação contra fonte oficial. O vínculo com `auth.User` usa
`on_delete=CASCADE` para garantir a remoção integral dos dados na exclusão da
conta (RN13).

Referência: docs/arquitetura/modelo-de-dados.md, seções 4.2 e 4.3.
"""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.catalogo.models import ComponenteCurricular, MatrizComponente
from apps.comum.models import ModeloCriado


class PerfilDiscente(ModeloCriado):
    """Perfil acadêmico declarado pelo discente (RF04)."""

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="usuário",
        on_delete=models.CASCADE,
        related_name="perfil",
    )
    matriz = models.ForeignKey(
        "catalogo.MatrizCurricular",
        verbose_name="matriz curricular",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="perfis",
    )
    periodo_ingresso = models.CharField(
        "período de ingresso",
        max_length=6,
        blank=True,
        help_text="Semestre no formato AAAAP.",
    )
    media_creditos_por_periodo = models.SmallIntegerField(
        "média de créditos por período",
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(40)],
        help_text="Usada na projeção de períodos restantes (RF20).",
    )
    atualizado_em = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        db_table = "perfil_discente"
        verbose_name = "perfil do discente"
        verbose_name_plural = "perfis dos discentes"

    def __str__(self) -> str:
        return f"Perfil de {self.usuario}"

    @property
    def curso(self):
        return self.matriz.curso if self.matriz else None

    # -- Progresso (RF18) ---------------------------------------------------

    def resumo_creditos(self) -> dict[str, int]:
        """
        Totaliza créditos cursados, em curso e pendentes frente à matriz.

        Componentes da matriz sem registro de progresso são contados como
        pendentes.
        """
        if self.matriz_id is None:
            return {"cursados": 0, "em_curso": 0, "pendentes": 0, "total_matriz": 0}

        itens = MatrizComponente.objects.filter(matriz_id=self.matriz_id).select_related(
            "componente"
        )
        status_por_componente = dict(
            ProgressoComponente.objects.filter(usuario_id=self.usuario_id).values_list(
                "componente_id", "status"
            )
        )

        totais = {"cursados": 0, "em_curso": 0, "pendentes": 0, "total_matriz": 0}
        for item in itens:
            creditos = item.componente.creditos
            totais["total_matriz"] += creditos
            status = status_por_componente.get(
                item.componente_id, ProgressoComponente.Status.PENDENTE
            )
            if status == ProgressoComponente.Status.CURSADO:
                totais["cursados"] += creditos
            elif status == ProgressoComponente.Status.EM_CURSO:
                totais["em_curso"] += creditos
            else:
                totais["pendentes"] += creditos
        return totais

    def periodos_restantes(self) -> int | None:
        """Projeção de períodos até a integralização (RF20)."""
        if not self.media_creditos_por_periodo:
            return None
        pendentes = self.resumo_creditos()["pendentes"]
        if pendentes <= 0:
            return 0
        return -(-pendentes // self.media_creditos_por_periodo)


class ProgressoComponente(models.Model):
    """Situação declarada de um componente curricular para um discente."""

    class Status(models.TextChoices):
        CURSADO = "CURSADO", "Cursado"
        EM_CURSO = "EM_CURSO", "Em curso"
        PENDENTE = "PENDENTE", "Pendente"

    class Natureza(models.TextChoices):
        MATRIZ = "MATRIZ", "Consta da matriz"
        OPTATIVO = "OPTATIVO", "Optativo fora da matriz"
        MODULO_LIVRE = "MODULO_LIVRE", "Módulo livre"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="usuário",
        on_delete=models.CASCADE,
        related_name="progresso",
    )
    componente = models.ForeignKey(
        ComponenteCurricular,
        verbose_name="componente",
        on_delete=models.CASCADE,
        related_name="progressos",
    )
    status = models.CharField(
        "situação", max_length=12, choices=Status.choices, default=Status.PENDENTE
    )
    natureza = models.CharField(
        "natureza",
        max_length=15,
        choices=Natureza.choices,
        default=Natureza.MATRIZ,
        help_text="Classificação de componentes fora da matriz (RF17).",
    )
    por_equivalencia = models.BooleanField(
        "cumprido por equivalência",
        default=False,
        help_text="Cumprimento por componente equivalente (RF19).",
    )
    componente_equivalente = models.ForeignKey(
        ComponenteCurricular,
        verbose_name="componente equivalente aproveitado",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equivalencias_aproveitadas",
    )
    atualizado_em = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        db_table = "progresso_componente"
        verbose_name = "progresso em componente"
        verbose_name_plural = "progressos em componentes"
        ordering = ["componente__codigo"]
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "componente"], name="progresso_componente_unico"
            ),
        ]
        indexes = [
            models.Index(fields=["usuario", "status"], name="progresso_usuario_status_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.componente.codigo}: {self.get_status_display()}"

    @property
    def cumprido(self) -> bool:
        """
        Indica se o componente satisfaz um pré-requisito.

        `EM_CURSO` não satisfaz pré-requisito no mesmo semestre (RN05, A04).
        """
        return self.status == self.Status.CURSADO
