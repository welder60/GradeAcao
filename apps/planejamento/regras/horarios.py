"""
Detecção de choque de horário (RN01, RN02, RF22).

Funções puras: operam sobre `Encontro`, uma projeção mínima de
`TurmaHorario` sem dependência do ORM (RNF22).
"""

from dataclasses import dataclass
from datetime import time
from itertools import combinations


@dataclass(frozen=True)
class Encontro:
    """Ocorrência semanal de uma turma em um dia e intervalo."""

    turma_id: int
    rotulo: str
    dia: str
    hora_inicio: time
    hora_fim: time

    def sobrepoe(self, outro: "Encontro") -> bool:
        """Sobreposição parcial ou total no mesmo dia da semana."""
        if self.dia != outro.dia:
            return False
        return self.hora_inicio < outro.hora_fim and outro.hora_inicio < self.hora_fim


@dataclass(frozen=True)
class Choque:
    """Par de encontros conflitantes e o intervalo em comum."""

    primeiro: Encontro
    segundo: Encontro
    dia: str
    inicio: time
    fim: time

    def __str__(self) -> str:
        return (
            f"{self.primeiro.rotulo} × {self.segundo.rotulo} "
            f"— {self.dia}, {self.inicio:%H:%M}–{self.fim:%H:%M}"
        )


def detectar_choques(encontros: list[Encontro]) -> list[Choque]:
    """
    Retorna todos os choques entre os encontros informados.

    Encontros da mesma turma nunca conflitam entre si.
    """
    choques: list[Choque] = []
    for a, b in combinations(encontros, 2):
        if a.turma_id == b.turma_id or not a.sobrepoe(b):
            continue
        choques.append(
            Choque(
                primeiro=a,
                segundo=b,
                dia=a.dia,
                inicio=max(a.hora_inicio, b.hora_inicio),
                fim=min(a.hora_fim, b.hora_fim),
            )
        )
    return choques


def blocos_ocupados(encontros: list[Encontro]) -> set[tuple[str, time]]:
    """Conjunto de pares (dia, hora de início) ocupados pelos encontros."""
    return {(e.dia, e.hora_inicio) for e in encontros}


def dias_sem_aula(encontros: list[Encontro], dias_possiveis: list[str]) -> list[str]:
    """Dias da semana em que nenhum encontro ocorre (RF33)."""
    ocupados = {e.dia for e in encontros}
    return [dia for dia in dias_possiveis if dia not in ocupados]


def janelas_livres(encontros: list[Encontro]) -> dict[str, int]:
    """
    Número de intervalos vagos entre o primeiro e o último encontro de cada dia.

    Serve à comparação de grades (RF33). Considera blocos de 55 minutos com
    início a cada hora cheia.
    """
    por_dia: dict[str, list[Encontro]] = {}
    for e in encontros:
        por_dia.setdefault(e.dia, []).append(e)

    resultado: dict[str, int] = {}
    for dia, itens in por_dia.items():
        ordenados = sorted(itens, key=lambda e: e.hora_inicio)
        vagas = 0
        for anterior, seguinte in zip(ordenados, ordenados[1:], strict=False):
            diferenca = (seguinte.hora_inicio.hour * 60 + seguinte.hora_inicio.minute) - (
                anterior.hora_fim.hour * 60 + anterior.hora_fim.minute
            )
            if diferenca > 5:
                vagas += diferenca // 60
        resultado[dia] = vagas
    return resultado
