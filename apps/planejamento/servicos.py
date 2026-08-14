"""
Camada de serviço do planejamento.

Faz a ponte entre o ORM e o módulo de regras (`apps.planejamento.regras`),
que é puro e não conhece o banco de dados (RNF22).
"""

from django.core.exceptions import ValidationError
from django.db.models import Prefetch

from apps.catalogo.models import ComponenteRelacao, Turma, TurmaHorario
from apps.contas.models import ProgressoComponente
from apps.planejamento.models import Grade, GradeTurma
from apps.planejamento.regras import Alerta, Choque, Encontro, detectar_choques
from apps.planejamento.regras.requisitos import (
    avaliar_co_requisitos,
    avaliar_limite_de_creditos,
    avaliar_pre_requisitos,
)


def encontros_da_grade(grade: Grade) -> list[Encontro]:
    """Projeta os horários das turmas principais da grade em `Encontro`."""
    horarios = (
        TurmaHorario.objects.filter(
            turma__itens_de_grade__grade=grade,
            turma__itens_de_grade__prioridade=GradeTurma.Prioridade.PRINCIPAL,
        )
        .select_related("turma__componente", "codigo_dia", "codigo_horario")
        .distinct()
    )
    return [
        Encontro(
            turma_id=h.turma_id,
            rotulo=f"{h.turma.componente.codigo} T{h.turma.codigo}",
            dia=h.codigo_dia.codigo,
            hora_inicio=h.codigo_horario.hora_inicio,
            hora_fim=h.codigo_horario.hora_fim,
        )
        for h in horarios
    ]


def choques_da_grade(grade: Grade) -> list[Choque]:
    """Choques de horário da grade (RF22)."""
    return detectar_choques(encontros_da_grade(grade))


def _grupos_de_relacao(codigos: list[str], tipo: str) -> dict[str, dict[int, set[str]]]:
    """Agrupa relações por componente e por grupo lógico."""
    relacoes = ComponenteRelacao.objects.filter(
        componente__codigo__in=codigos, tipo=tipo
    ).select_related("componente", "componente_relacionado")

    resultado: dict[str, dict[int, set[str]]] = {}
    for relacao in relacoes:
        por_grupo = resultado.setdefault(relacao.componente.codigo, {})
        por_grupo.setdefault(relacao.grupo, set()).add(relacao.componente_relacionado.codigo)
    return resultado


def componentes_cumpridos(usuario) -> set[str]:
    """
    Códigos de componentes considerados cumpridos pelo discente.

    Inclui equivalências aproveitadas (RF19). `EM_CURSO` é excluído porque não
    satisfaz pré-requisito no mesmo semestre (RN05).
    """
    if not usuario or not usuario.is_authenticated:
        return set()

    cumpridos = set(
        ProgressoComponente.objects.filter(
            usuario=usuario, status=ProgressoComponente.Status.CURSADO
        ).values_list("componente__codigo", flat=True)
    )

    equivalentes = ComponenteRelacao.objects.filter(
        tipo=ComponenteRelacao.Tipo.EQUIVALENCIA,
        componente_relacionado__codigo__in=cumpridos,
    ).values_list("componente__codigo", flat=True)
    cumpridos.update(equivalentes)
    return cumpridos


def alertas_da_grade(grade: Grade) -> list[Alerta]:
    """
    Alertas acadêmicos da grade: pré-requisito, co-requisito e limite de
    créditos. Nenhum deles bloqueia a montagem (RN08).
    """
    turmas = list(
        Turma.objects.filter(
            itens_de_grade__grade=grade,
            itens_de_grade__prioridade=GradeTurma.Prioridade.PRINCIPAL,
        ).select_related("componente")
    )
    codigos_na_grade = {t.componente.codigo for t in turmas}
    cumpridos = componentes_cumpridos(grade.usuario)

    pre = _grupos_de_relacao(list(codigos_na_grade), ComponenteRelacao.Tipo.PRE_REQUISITO)
    co = _grupos_de_relacao(list(codigos_na_grade), ComponenteRelacao.Tipo.CO_REQUISITO)

    alertas: list[Alerta] = []
    for codigo in sorted(codigos_na_grade):
        alertas += avaliar_pre_requisitos(codigo, pre.get(codigo, {}), cumpridos)
        alertas += avaliar_co_requisitos(codigo, co.get(codigo, {}), codigos_na_grade, cumpridos)

    perfil = getattr(grade.usuario, "perfil", None)
    matriz = perfil.matriz if perfil else None
    alertas += avaliar_limite_de_creditos(
        creditos_na_grade=sum(t.componente.creditos for t in turmas),
        carga_horaria_maxima=(matriz.carga_horaria_maxima_periodo_letivo if matriz else None),
        carga_horaria_minima=(matriz.carga_horaria_minima_periodo_letivo if matriz else None),
    )
    return alertas


def adicionar_turma(grade: Grade, turma: Turma, prioridade: str | None = None) -> GradeTurma:
    """
    Inclui uma turma na grade (RF21).

    Valida que a turma pertence ao mesmo semestre da grade (RN09, A01) e
    reavalia a validade do cenário.
    """
    if turma.semestre_id != grade.semestre_id:
        raise ValidationError(
            "A turma pertence a outro período letivo e não pode compor esta grade."
        )

    item, _ = GradeTurma.objects.get_or_create(
        grade=grade,
        turma=turma,
        defaults={"prioridade": prioridade or GradeTurma.Prioridade.PRINCIPAL},
    )
    atualizar_validade(grade)
    return item


def remover_turma(grade: Grade, turma_id: int) -> None:
    """Remove uma turma da grade (RF21)."""
    GradeTurma.objects.filter(grade=grade, turma_id=turma_id).delete()
    atualizar_validade(grade)


def atualizar_validade(grade: Grade) -> bool:
    """
    Recalcula `grade.valida` a partir dos choques não reconhecidos (RN02, RF23).

    Um choque deixa de invalidar a grade quando ambas as turmas envolvidas
    estão marcadas com `choque_reconhecido`.
    """
    choques = choques_da_grade(grade)
    reconhecidas = set(
        GradeTurma.objects.filter(grade=grade, choque_reconhecido=True).values_list(
            "turma_id", flat=True
        )
    )
    pendentes = [
        c
        for c in choques
        if c.primeiro.turma_id not in reconhecidas or c.segundo.turma_id not in reconhecidas
    ]
    valida = not pendentes
    if grade.valida != valida:
        grade.valida = valida
        grade.save(update_fields=["valida", "atualizado_em"])
    return valida


def duplicar_grade(grade: Grade, novo_nome: str) -> Grade:
    """Cria uma cópia da grade com outro nome (RF32)."""
    itens = list(grade.itens.all())
    copia = Grade.objects.create(
        usuario=grade.usuario,
        semestre=grade.semestre,
        nome=novo_nome,
        valida=grade.valida,
    )
    GradeTurma.objects.bulk_create(
        GradeTurma(
            grade=copia,
            turma_id=item.turma_id,
            prioridade=item.prioridade,
            choque_reconhecido=item.choque_reconhecido,
        )
        for item in itens
    )
    return copia


def definir_preferida(grade: Grade) -> None:
    """Marca a grade como preferida, desmarcando as demais (RF34, I08)."""
    Grade.objects.filter(usuario=grade.usuario, semestre=grade.semestre, preferida=True).exclude(
        pk=grade.pk
    ).update(preferida=False)
    if not grade.preferida:
        grade.preferida = True
        grade.save(update_fields=["preferida", "atualizado_em"])


def grade_para_calendario(grade: Grade) -> dict:
    """
    Estrutura a grade em uma matriz dia × bloco para o calendário semanal
    (RF35).
    """
    from apps.comum.models import CodigoDia, CodigoHorario

    dias = list(CodigoDia.objects.all())
    blocos = list(CodigoHorario.objects.all())

    horarios = (
        TurmaHorario.objects.filter(
            turma__itens_de_grade__grade=grade,
            turma__itens_de_grade__prioridade=GradeTurma.Prioridade.PRINCIPAL,
        )
        .select_related("turma__componente", "codigo_dia", "codigo_horario", "campus")
        .distinct()
    )

    celulas: dict[tuple[int, int], list[TurmaHorario]] = {}
    for h in horarios:
        celulas.setdefault((h.codigo_horario_id, h.codigo_dia_id), []).append(h)

    linhas = [
        {
            "bloco": bloco,
            "celulas": [
                {"dia": dia, "encontros": celulas.get((bloco.id, dia.id), [])} for dia in dias
            ],
        }
        for bloco in blocos
    ]
    return {"dias": dias, "linhas": linhas}


def turmas_da_oferta(semestre, filtros: dict | None = None):
    """
    Queryset de turmas do semestre com os relacionamentos necessários à
    listagem da oferta (RF08, RF10).
    """
    filtros = filtros or {}
    consulta = (
        Turma.objects.filter(semestre=semestre)
        .select_related("componente", "semestre")
        .prefetch_related(
            Prefetch(
                "horarios",
                queryset=TurmaHorario.objects.select_related(
                    "codigo_dia", "codigo_horario", "campus"
                ),
            ),
            "docentes",
        )
    )
    if filtros.get("campus"):
        consulta = consulta.filter(horarios__campus_id=filtros["campus"])
    if filtros.get("turno"):
        consulta = consulta.filter(horarios__codigo_horario__turno=filtros["turno"])
    if filtros.get("dia"):
        consulta = consulta.filter(horarios__codigo_dia_id=filtros["dia"])
    if filtros.get("docente"):
        consulta = consulta.filter(docentes__id=filtros["docente"])
    if filtros.get("departamento"):
        consulta = consulta.filter(componente__departamento=filtros["departamento"])
    return consulta.distinct()
