"""
Carga inicial das tabelas de domínio.

Os valores são um ponto de partida e devem ser conferidos contra a oferta
pública antes da carga definitiva (docs/arquitetura/modelo-de-dados.md, §6).
"""

from datetime import time

from django.db import migrations

CAMPI = [
    ("DAR", "Campus Darcy Ribeiro"),
    ("FCTE", "Campus Gama"),
    ("FCE", "Campus Ceilândia"),
    ("FUP", "Campus Planaltina"),
]

DIAS = [
    ("2", "Segunda-feira", 1),
    ("3", "Terça-feira", 2),
    ("4", "Quarta-feira", 3),
    ("5", "Quinta-feira", 4),
    ("6", "Sexta-feira", 5),
    ("7", "Sábado", 6),
]

BLOCOS = [
    ("M1", time(8, 0), time(8, 55), "M", 1),
    ("M2", time(9, 0), time(9, 55), "M", 2),
    ("M3", time(10, 0), time(10, 55), "M", 3),
    ("M4", time(11, 0), time(11, 55), "M", 4),
    ("M5", time(12, 0), time(12, 55), "M", 5),
    ("T1", time(14, 0), time(14, 55), "T", 6),
    ("T2", time(15, 0), time(15, 55), "T", 7),
    ("T3", time(16, 0), time(16, 55), "T", 8),
    ("T4", time(17, 0), time(17, 55), "T", 9),
    ("T5", time(18, 0), time(18, 55), "T", 10),
    ("N1", time(19, 0), time(19, 55), "N", 11),
    ("N2", time(20, 0), time(20, 55), "N", 12),
    ("N3", time(21, 0), time(21, 55), "N", 13),
    ("N4", time(22, 0), time(22, 55), "N", 14),
]


def carregar(apps, schema_editor):
    Campus = apps.get_model("comum", "Campus")
    CodigoDia = apps.get_model("comum", "CodigoDia")
    CodigoHorario = apps.get_model("comum", "CodigoHorario")

    for codigo, nome in CAMPI:
        Campus.objects.update_or_create(codigo=codigo, defaults={"nome": nome})

    for codigo, nome, ordem in DIAS:
        CodigoDia.objects.update_or_create(
            codigo=codigo, defaults={"dia_da_semana": nome, "ordem": ordem}
        )

    for codigo, inicio, fim, turno, ordem in BLOCOS:
        CodigoHorario.objects.update_or_create(
            codigo=codigo,
            defaults={
                "horario": f"{inicio:%H:%M}–{fim:%H:%M}",
                "hora_inicio": inicio,
                "hora_fim": fim,
                "turno": turno,
                "ordem": ordem,
            },
        )


def remover(apps, schema_editor):
    apps.get_model("comum", "CodigoHorario").objects.filter(
        codigo__in=[b[0] for b in BLOCOS]
    ).delete()
    apps.get_model("comum", "CodigoDia").objects.filter(
        codigo__in=[d[0] for d in DIAS]
    ).delete()
    apps.get_model("comum", "Campus").objects.filter(
        codigo__in=[c[0] for c in CAMPI]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("comum", "0001_initial")]

    operations = [migrations.RunPython(carregar, remover)]
