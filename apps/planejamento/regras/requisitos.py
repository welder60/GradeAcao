"""
Avaliação de pré-requisitos, co-requisitos e limite de créditos.

Funções puras (RNF22). Pendências geram **alerta**, nunca bloqueio (RN08).
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Alerta:
    """Sinalização não bloqueante apresentada ao discente."""

    tipo: str
    codigo_componente: str
    mensagem: str
    detalhe: tuple[str, ...] = field(default_factory=tuple)


def _grupos_satisfeitos(grupos: dict[int, set[str]], cumpridos: set[str]) -> list[set[str]]:
    """
    Retorna os grupos não satisfeitos.

    Dentro de um grupo as alternativas combinam-se por OU; grupos distintos
    combinam-se por E.
    """
    return [
        alternativas
        for alternativas in grupos.values()
        if alternativas and not (alternativas & cumpridos)
    ]


def avaliar_pre_requisitos(
    codigo_componente: str,
    grupos_pre_requisito: dict[int, set[str]],
    componentes_cumpridos: set[str],
) -> list[Alerta]:
    """
    Sinaliza pré-requisitos não cumpridos (RF24, RN05).

    `componentes_cumpridos` deve conter apenas componentes com situação
    `CURSADO`; `EM_CURSO` não satisfaz pré-requisito no mesmo semestre.
    """
    pendentes = _grupos_satisfeitos(grupos_pre_requisito, componentes_cumpridos)
    if not pendentes:
        return []
    return [
        Alerta(
            tipo="PRE_REQUISITO",
            codigo_componente=codigo_componente,
            mensagem=(
                f"{codigo_componente} possui pré-requisito não registrado como "
                f"cumprido no seu perfil."
            ),
            detalhe=tuple(" ou ".join(sorted(grupo)) for grupo in pendentes),
        )
    ]


def avaliar_co_requisitos(
    codigo_componente: str,
    grupos_co_requisito: dict[int, set[str]],
    componentes_na_grade: set[str],
    componentes_cumpridos: set[str],
) -> list[Alerta]:
    """Sinaliza co-requisitos ausentes da grade em construção (RF25)."""
    disponiveis = componentes_na_grade | componentes_cumpridos
    pendentes = _grupos_satisfeitos(grupos_co_requisito, disponiveis)
    if not pendentes:
        return []
    return [
        Alerta(
            tipo="CO_REQUISITO",
            codigo_componente=codigo_componente,
            mensagem=(f"{codigo_componente} possui co-requisito ausente na grade em construção."),
            detalhe=tuple(" ou ".join(sorted(grupo)) for grupo in pendentes),
        )
    ]


def avaliar_limite_de_creditos(
    creditos_na_grade: int,
    carga_horaria_maxima: int | None,
    carga_horaria_minima: int | None = None,
) -> list[Alerta]:
    """Sinaliza extrapolação do limite de créditos da matriz (RF26)."""
    alertas: list[Alerta] = []
    carga = creditos_na_grade * 15

    if carga_horaria_maxima and carga > carga_horaria_maxima:
        alertas.append(
            Alerta(
                tipo="LIMITE_MAXIMO",
                codigo_componente="",
                mensagem=(
                    f"A grade soma {carga} horas, acima do máximo de "
                    f"{carga_horaria_maxima} horas previsto na matriz."
                ),
            )
        )
    if carga_horaria_minima and carga < carga_horaria_minima:
        alertas.append(
            Alerta(
                tipo="LIMITE_MINIMO",
                codigo_componente="",
                mensagem=(
                    f"A grade soma {carga} horas, abaixo do mínimo de "
                    f"{carga_horaria_minima} horas previsto na matriz."
                ),
            )
        )
    return alertas
