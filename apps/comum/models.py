"""
Modelos de domínio compartilhados do GradeAção.

Concentra as tabelas de domínio (`campus`, `codigo_dia`, `codigo_horario`) e
os modelos abstratos de auditoria reutilizados pelos demais apps.

Referência: docs/arquitetura/modelo-de-dados.md, seções 3.1, 3.10 e 3.11.
"""

from django.core.validators import MinValueValidator
from django.db import models


class ModeloCriado(models.Model):
    """Mixin de auditoria com a data de criação do registro."""

    criado_em = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        abstract = True


class ModeloAuditado(ModeloCriado):
    """Mixin de auditoria para tabelas de escrita frequente."""

    atualizado_em = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        abstract = True


class Turno(models.TextChoices):
    """Turnos institucionais usados nos blocos de horário."""

    MATUTINO = "M", "Matutino"
    VESPERTINO = "T", "Vespertino"
    NOTURNO = "N", "Noturno"


class Campus(ModeloCriado):
    """Unidade física em que ocorrem as aulas."""

    codigo = models.CharField("código", max_length=10, unique=True)
    nome = models.CharField("nome", max_length=120)

    class Meta:
        db_table = "campus"
        verbose_name = "campus"
        verbose_name_plural = "campi"
        ordering = ["codigo"]

    def __str__(self) -> str:
        return f"{self.codigo} — {self.nome}"


class CodigoDia(ModeloCriado):
    """Tabela de domínio dos dias da semana."""

    codigo = models.CharField("código", max_length=2, unique=True)
    dia_da_semana = models.CharField("dia da semana", max_length=20)
    ordem = models.SmallIntegerField("ordem", unique=True)

    class Meta:
        db_table = "codigo_dia"
        verbose_name = "código de dia"
        verbose_name_plural = "códigos de dia"
        ordering = ["ordem"]

    def __str__(self) -> str:
        return self.dia_da_semana


class CodigoHorario(ModeloCriado):
    """
    Tabela de domínio dos blocos de horário.

    As colunas `hora_inicio` e `hora_fim` existem porque a detecção de choque
    (RN01) exige comparação de intervalos, e não de códigos textuais.
    """

    codigo = models.CharField("código", max_length=4, unique=True)
    horario = models.CharField("horário", max_length=20)
    hora_inicio = models.TimeField("hora de início")
    hora_fim = models.TimeField("hora de término")
    turno = models.CharField("turno", max_length=1, choices=Turno.choices)
    ordem = models.SmallIntegerField("ordem", unique=True)

    class Meta:
        db_table = "codigo_horario"
        verbose_name = "código de horário"
        verbose_name_plural = "códigos de horário"
        ordering = ["ordem"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(hora_inicio__lt=models.F("hora_fim")),
                name="codigo_horario_inicio_antes_do_fim",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.codigo} ({self.horario})"

    def sobrepoe(self, outro: "CodigoHorario") -> bool:
        """Indica se este bloco se sobrepõe temporalmente a `outro` (RN01)."""
        return self.hora_inicio < outro.hora_fim and outro.hora_inicio < self.hora_fim


class RegistroCarga(ModeloCriado):
    """
    Log das operações de carga de dados públicos (RF46).

    Registra o curador responsável, o volume afetado e o resultado da
    importação, sem armazenar o arquivo de origem.
    """

    class Origem(models.TextChoices):
        IMPORTACAO_CSV = "CSV", "Importação de arquivo"
        MANUAL = "MANUAL", "Edição manual"
        MIGRACAO = "MIGRACAO", "Migração de dados"

    curador = models.ForeignKey(
        "auth.User",
        verbose_name="curador",
        on_delete=models.SET_NULL,
        null=True,
        related_name="cargas",
    )
    origem = models.CharField(
        "origem", max_length=10, choices=Origem.choices, default=Origem.IMPORTACAO_CSV
    )
    entidade = models.CharField("entidade afetada", max_length=60)
    registros_afetados = models.IntegerField(
        "registros afetados", default=0, validators=[MinValueValidator(0)]
    )
    detalhe = models.TextField("detalhe", blank=True)

    class Meta:
        db_table = "registro_carga"
        verbose_name = "registro de carga"
        verbose_name_plural = "registros de carga"
        ordering = ["-criado_em"]

    def __str__(self) -> str:
        return f"{self.entidade}: {self.registros_afetados} registro(s)"
