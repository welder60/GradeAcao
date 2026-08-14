"""
Modelos de estrutura acadêmica e de oferta do GradeAção.

Cobre os domínios "Estrutura acadêmica" (`curso`, `matriz_curricular`,
`componente_curricular`, `componente_relacao`, `matriz_componente`) e "Oferta"
(`semestre`, `docente`, `turma`, `turma_docente`, `turma_horario`).

Referência: docs/arquitetura/modelo-de-dados.md, seções 3.2 a 3.12 e 4.1.
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.comum.models import ModeloAuditado, ModeloCriado

# ---------------------------------------------------------------------------
# Estrutura acadêmica
# ---------------------------------------------------------------------------


class Curso(ModeloCriado):
    """Programa de formação ao qual o discente se vincula."""

    class Turno(models.TextChoices):
        DIURNO = "DIURNO", "Diurno"
        NOTURNO = "NOTURNO", "Noturno"
        INTEGRAL = "INTEGRAL", "Integral"

    nome = models.CharField("nome", max_length=160)
    # NULL, e não string vazia: a restrição UNIQUE não admite repetição de "".
    codigo = models.CharField(  # noqa: DJ001
        "código", max_length=20, unique=True, null=True, blank=True
    )
    campus = models.ForeignKey(
        "comum.Campus",
        verbose_name="campus",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cursos",
    )
    turno = models.CharField("turno", max_length=20, choices=Turno.choices, blank=True)

    class Meta:
        db_table = "curso"
        verbose_name = "curso"
        verbose_name_plural = "cursos"
        ordering = ["nome"]

    def __str__(self) -> str:
        return self.nome


class MatrizCurricular(ModeloCriado):
    """
    Conjunto de componentes exigidos para a integralização de um curso.

    Um curso pode possuir várias matrizes ao longo do tempo; `vigencia_fim`
    nulo indica a matriz vigente.
    """

    curso = models.ForeignKey(
        Curso, verbose_name="curso", on_delete=models.CASCADE, related_name="matrizes"
    )
    nome = models.CharField("nome", max_length=160)
    codigo = models.CharField("código", max_length=20, blank=True)
    vigencia_inicio = models.CharField(
        "início de vigência",
        max_length=6,
        blank=True,
        help_text="Semestre no formato AAAAP.",
    )
    vigencia_fim = models.CharField(
        "fim de vigência",
        max_length=6,
        blank=True,
        help_text="Vazio quando a matriz está vigente.",
    )
    carga_horaria_minima_periodo_letivo = models.SmallIntegerField(
        "carga horária mínima por período",
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    carga_horaria_maxima_periodo_letivo = models.SmallIntegerField(
        "carga horária máxima por período",
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        db_table = "matriz_curricular"
        verbose_name = "matriz curricular"
        verbose_name_plural = "matrizes curriculares"
        ordering = ["curso__nome", "-vigencia_inicio"]
        constraints = [
            models.UniqueConstraint(
                fields=["curso", "nome"], name="matriz_curricular_unica_por_curso"
            ),
            models.CheckConstraint(
                condition=models.Q(carga_horaria_minima_periodo_letivo__gte=0)
                | models.Q(carga_horaria_minima_periodo_letivo__isnull=True),
                name="matriz_curricular_ch_minima_nao_negativa",
            ),
            models.CheckConstraint(
                condition=models.Q(carga_horaria_maxima_periodo_letivo__gte=0)
                | models.Q(carga_horaria_maxima_periodo_letivo__isnull=True),
                name="matriz_curricular_ch_maxima_nao_negativa",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.curso.nome} — {self.nome}"

    @property
    def vigente(self) -> bool:
        return not self.vigencia_fim


class ComponenteCurricular(ModeloAuditado):
    """Unidade de ensino com código e créditos próprios (RF07)."""

    codigo = models.CharField("código", max_length=15, unique=True)
    nome = models.CharField("nome", max_length=200)
    carga_horaria = models.SmallIntegerField(
        "carga horária", null=True, blank=True, validators=[MinValueValidator(0)]
    )
    departamento = models.CharField("departamento", max_length=120, blank=True)
    ementa = models.TextField("ementa", blank=True)
    ativo = models.BooleanField("ativo", default=True)

    class Meta:
        db_table = "componente_curricular"
        verbose_name = "componente curricular"
        verbose_name_plural = "componentes curriculares"
        ordering = ["codigo"]
        indexes = [
            models.Index(fields=["nome"], name="componente_nome_idx"),
            models.Index(fields=["departamento"], name="componente_departamento_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(carga_horaria__gte=0) | models.Q(carga_horaria__isnull=True),
                name="componente_carga_horaria_nao_negativa",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.codigo} — {self.nome}"

    @property
    def creditos(self) -> int:
        """Créditos derivados da carga horária (15 horas por crédito)."""
        return (self.carga_horaria or 0) // 15


class ComponenteRelacao(models.Model):
    """
    Relação dirigida e tipificada entre dois componentes curriculares.

    Relações de mesmo `componente`, mesmo `tipo` e mesmo `grupo` combinam-se
    por OU; grupos distintos combinam-se por E.
    """

    class Tipo(models.TextChoices):
        PRE_REQUISITO = "PRE_REQUISITO", "Pré-requisito"
        CO_REQUISITO = "CO_REQUISITO", "Co-requisito"
        EQUIVALENCIA = "EQUIVALENCIA", "Equivalência"

    componente = models.ForeignKey(
        ComponenteCurricular,
        verbose_name="componente",
        on_delete=models.CASCADE,
        related_name="relacoes",
    )
    componente_relacionado = models.ForeignKey(
        ComponenteCurricular,
        verbose_name="componente relacionado",
        on_delete=models.CASCADE,
        related_name="relacoes_inversas",
    )
    tipo = models.CharField("tipo", max_length=15, choices=Tipo.choices)
    grupo = models.SmallIntegerField(
        "grupo",
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Relações do mesmo grupo combinam-se por OU.",
    )
    bidirecional = models.BooleanField(
        "bidirecional", default=False, help_text="Aplicável a equivalências (RN06)."
    )
    observacao = models.TextField("observação", blank=True)

    class Meta:
        db_table = "componente_relacao"
        verbose_name = "relação entre componentes"
        verbose_name_plural = "relações entre componentes"
        ordering = ["componente__codigo", "tipo", "grupo"]
        constraints = [
            models.UniqueConstraint(
                fields=["componente", "componente_relacionado", "tipo"],
                name="componente_relacao_unica",
            ),
            models.CheckConstraint(
                condition=~models.Q(componente=models.F("componente_relacionado")),
                name="componente_relacao_sem_auto_referencia",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.componente.codigo} {self.get_tipo_display()} "
            f"{self.componente_relacionado.codigo}"
        )


class MatrizComponente(models.Model):
    """Associação entre matriz curricular e componente (RF11, RF18)."""

    class Natureza(models.TextChoices):
        OBRIGATORIO = "OBRIGATORIO", "Obrigatório"
        OPTATIVO = "OPTATIVO", "Optativo"
        MODULO_LIVRE = "MODULO_LIVRE", "Módulo livre"

    matriz = models.ForeignKey(
        MatrizCurricular,
        verbose_name="matriz",
        on_delete=models.CASCADE,
        related_name="componentes",
    )
    componente = models.ForeignKey(
        ComponenteCurricular,
        verbose_name="componente",
        on_delete=models.CASCADE,
        related_name="matrizes",
    )
    periodo_recomendado = models.SmallIntegerField(
        "período recomendado",
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
    )
    natureza = models.CharField(
        "natureza",
        max_length=15,
        choices=Natureza.choices,
        default=Natureza.OBRIGATORIO,
    )

    class Meta:
        db_table = "matriz_componente"
        verbose_name = "componente da matriz"
        verbose_name_plural = "componentes da matriz"
        ordering = ["periodo_recomendado", "componente__codigo"]
        constraints = [
            models.UniqueConstraint(
                fields=["matriz", "componente"], name="matriz_componente_unico"
            ),
            models.CheckConstraint(
                condition=models.Q(periodo_recomendado__range=(1, 20))
                | models.Q(periodo_recomendado__isnull=True),
                name="matriz_componente_periodo_valido",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.matriz.nome} · {self.componente.codigo}"


# ---------------------------------------------------------------------------
# Oferta
# ---------------------------------------------------------------------------


class SemestreQuerySet(models.QuerySet):
    """Consultas reutilizáveis sobre períodos letivos."""

    def atual(self) -> "Semestre | None":
        """Semestre marcado como ativo, exibido por padrão no planejador."""
        return self.filter(ativo=True).order_by("-ano", "-periodo").first()


class Semestre(models.Model):
    """Período letivo ao qual se vinculam a oferta e as grades."""

    class Periodo(models.IntegerChoices):
        VERAO = 0, "Verão"
        PRIMEIRO = 1, "1º período"
        SEGUNDO = 2, "2º período"

    codigo = models.CharField(
        "código", max_length=6, unique=True, help_text="Formato AAAAP (ex.: 20262)."
    )
    ano = models.SmallIntegerField("ano", validators=[MinValueValidator(2000)])
    periodo = models.SmallIntegerField("período", choices=Periodo.choices)
    data_inicio = models.DateField("início das aulas", null=True, blank=True)
    data_fim = models.DateField("fim das aulas", null=True, blank=True)
    ativo = models.BooleanField("ativo", default=False)
    oferta_atualizada_em = models.DateTimeField(
        "oferta atualizada em",
        null=True,
        blank=True,
        help_text="Data da última carga de oferta (RF12, RF45).",
    )

    objects = SemestreQuerySet.as_manager()

    class Meta:
        db_table = "semestre"
        verbose_name = "semestre"
        verbose_name_plural = "semestres"
        ordering = ["-ano", "-periodo"]
        constraints = [
            models.UniqueConstraint(fields=["ano", "periodo"], name="semestre_unico"),
            models.CheckConstraint(condition=models.Q(ano__gte=2000), name="semestre_ano_valido"),
            models.CheckConstraint(
                condition=models.Q(periodo__in=[0, 1, 2]), name="semestre_periodo_valido"
            ),
        ]

    def __str__(self) -> str:
        return self.codigo

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = f"{self.ano}{self.periodo}"
        super().save(*args, **kwargs)


class Docente(ModeloCriado):
    """
    Professor responsável por turmas.

    Alimentado apenas com o nome divulgado publicamente na oferta (RNF17).
    """

    nome = models.CharField("nome", max_length=200, unique=True)

    class Meta:
        db_table = "docente"
        verbose_name = "docente"
        verbose_name_plural = "docentes"
        ordering = ["nome"]

    def __str__(self) -> str:
        return self.nome


class Turma(models.Model):
    """Instância concreta de um componente curricular em um semestre (RF08)."""

    class Modalidade(models.TextChoices):
        PRESENCIAL = "PRESENCIAL", "Presencial"
        REMOTA = "REMOTA", "Remota"
        HIBRIDA = "HIBRIDA", "Híbrida"

    semestre = models.ForeignKey(
        Semestre, verbose_name="semestre", on_delete=models.CASCADE, related_name="turmas"
    )
    componente = models.ForeignKey(
        ComponenteCurricular,
        verbose_name="componente",
        on_delete=models.CASCADE,
        related_name="turmas",
    )
    codigo = models.CharField("código", max_length=10)
    vagas_ofertadas = models.SmallIntegerField(
        "vagas ofertadas", null=True, blank=True, validators=[MinValueValidator(0)]
    )
    vagas_ocupadas = models.SmallIntegerField(
        "vagas ocupadas", null=True, blank=True, validators=[MinValueValidator(0)]
    )
    modalidade = models.CharField(
        "modalidade", max_length=20, choices=Modalidade.choices, blank=True
    )
    observacao = models.TextField("observação", blank=True)
    coletado_em = models.DateTimeField(
        "coletado em",
        null=True,
        blank=True,
        help_text="Data da coleta dos dados desta turma (RF45).",
    )

    docentes = models.ManyToManyField(
        Docente,
        verbose_name="docentes",
        through="TurmaDocente",
        related_name="turmas",
        blank=True,
    )

    class Meta:
        db_table = "turma"
        verbose_name = "turma"
        verbose_name_plural = "turmas"
        ordering = ["componente__codigo", "codigo"]
        constraints = [
            models.UniqueConstraint(
                fields=["semestre", "componente", "codigo"], name="turma_unica_no_semestre"
            ),
            models.CheckConstraint(
                condition=models.Q(vagas_ofertadas__gte=0) | models.Q(vagas_ofertadas__isnull=True),
                name="turma_vagas_ofertadas_nao_negativas",
            ),
            models.CheckConstraint(
                condition=models.Q(vagas_ocupadas__gte=0) | models.Q(vagas_ocupadas__isnull=True),
                name="turma_vagas_ocupadas_nao_negativas",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.componente.codigo} · Turma {self.codigo} ({self.semestre.codigo})"

    @property
    def vagas_restantes(self) -> int | None:
        """Saldo informativo e datado de vagas (RN10)."""
        if self.vagas_ofertadas is None or self.vagas_ocupadas is None:
            return None
        return self.vagas_ofertadas - self.vagas_ocupadas


class TurmaDocente(models.Model):
    """Vínculo entre uma turma e um docente divulgado na oferta."""

    turma = models.ForeignKey(
        Turma, verbose_name="turma", on_delete=models.CASCADE, related_name="vinculos_docente"
    )
    docente = models.ForeignKey(
        Docente,
        verbose_name="docente",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vinculos_turma",
    )
    adicionado_em = models.DateTimeField("adicionado em", auto_now_add=True)

    class Meta:
        db_table = "turma_docente"
        verbose_name = "docente da turma"
        verbose_name_plural = "docentes da turma"
        constraints = [
            models.UniqueConstraint(fields=["turma", "docente"], name="turma_docente_unico"),
        ]

    def __str__(self) -> str:
        return f"{self.turma} · {self.docente or 'a definir'}"


class TurmaHorario(models.Model):
    """
    Encontro semanal de uma turma: onde e quando ocorre.

    O campus reside aqui, e não em `Turma`, porque uma mesma turma pode ter
    encontros em locais distintos.
    """

    turma = models.ForeignKey(
        Turma, verbose_name="turma", on_delete=models.CASCADE, related_name="horarios"
    )
    campus = models.ForeignKey(
        "comum.Campus",
        verbose_name="campus",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="horarios",
    )
    codigo_dia = models.ForeignKey(
        "comum.CodigoDia",
        verbose_name="dia da semana",
        on_delete=models.PROTECT,
        related_name="horarios",
    )
    codigo_horario = models.ForeignKey(
        "comum.CodigoHorario",
        verbose_name="bloco de horário",
        on_delete=models.PROTECT,
        related_name="horarios",
    )
    local = models.CharField("local", max_length=40, blank=True)

    class Meta:
        db_table = "turma_horario"
        verbose_name = "horário da turma"
        verbose_name_plural = "horários da turma"
        ordering = ["codigo_dia__ordem", "codigo_horario__ordem"]
        constraints = [
            models.UniqueConstraint(
                fields=["turma", "codigo_dia", "codigo_horario"],
                name="turma_horario_unico",
            ),
        ]
        indexes = [
            models.Index(fields=["codigo_dia", "codigo_horario"], name="turma_horario_slot_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.codigo_dia.codigo}{self.codigo_horario.codigo}"
