"""
Serviços de apoio à curadoria.

Concentra o registro em log das operações de escrita (RF46), para que as views
não precisem conhecer a estrutura de `RegistroCarga`.
"""

from apps.comum.models import RegistroCarga
from apps.curadoria.registro import EntidadeCuradoria

ACAO_CRIACAO = "criação"
ACAO_EDICAO = "edição"
ACAO_EXCLUSAO = "exclusão"


def registrar_operacao(
    *,
    curador,
    entidade: EntidadeCuradoria,
    acao: str,
    descricao: str,
    registros_afetados: int = 1,
) -> RegistroCarga:
    """
    Registra em log uma operação manual de curadoria (RF46).

    O log guarda quem alterou, o que foi alterado e o volume — nunca o
    conteúdo do registro em si.
    """
    return RegistroCarga.objects.create(
        curador=curador if getattr(curador, "is_authenticated", False) else None,
        origem=RegistroCarga.Origem.MANUAL,
        entidade=entidade.modelo._meta.db_table[:60],
        registros_afetados=registros_afetados,
        detalhe=f"{acao.capitalize()} de {entidade.rotulo}: {descricao}"[:2000],
    )
