"""
Módulo de validação acadêmica.

As funções deste pacote são **puras**: recebem estruturas de dados simples e
não acessam o ORM nem a camada de apresentação (RNF22).
"""

from .horarios import Choque, Encontro, blocos_ocupados, detectar_choques
from .requisitos import (
    Alerta,
    avaliar_co_requisitos,
    avaliar_limite_de_creditos,
    avaliar_pre_requisitos,
)

__all__ = [
    "Encontro",
    "Choque",
    "detectar_choques",
    "blocos_ocupados",
    "Alerta",
    "avaliar_pre_requisitos",
    "avaliar_co_requisitos",
    "avaliar_limite_de_creditos",
]
