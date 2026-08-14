"""
Cria o grupo `Curador` com permissão de escrita sobre os dados públicos (RN14).

As permissões padrão são criadas no sinal `post_migrate`, que ainda não rodou
quando esta migração executa; por isso elas são obtidas com `get_or_create` a
partir do `ContentType`, e não apenas consultadas.
"""

from django.db import migrations

GRUPO = "Curador"

# (app_label, model) das tabelas sob curadoria.
MODELOS = [
    ("comum", "campus"),
    ("comum", "codigodia"),
    ("comum", "codigohorario"),
    ("comum", "registrocarga"),
    ("catalogo", "curso"),
    ("catalogo", "matrizcurricular"),
    ("catalogo", "matrizcomponente"),
    ("catalogo", "componentecurricular"),
    ("catalogo", "componenterelacao"),
    ("catalogo", "semestre"),
    ("catalogo", "docente"),
    ("catalogo", "turma"),
    ("catalogo", "turmahorario"),
    ("catalogo", "turmadocente"),
]

ACOES = {
    "add": "Can add",
    "change": "Can change",
    "delete": "Can delete",
    "view": "Can view",
}


def criar_grupo(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    grupo, _ = Group.objects.get_or_create(name=GRUPO)

    permissoes = []
    for app_label, modelo in MODELOS:
        tipo, _ = ContentType.objects.get_or_create(app_label=app_label, model=modelo)
        for acao, prefixo in ACOES.items():
            permissao, _ = Permission.objects.get_or_create(
                codename=f"{acao}_{modelo}",
                content_type=tipo,
                defaults={"name": f"{prefixo} {modelo}"},
            )
            permissoes.append(permissao)

    grupo.permissions.add(*permissoes)


def remover_grupo(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name=GRUPO).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("comum", "0002_carga_inicial_dominio"),
        ("catalogo", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(criar_grupo, remover_grupo),
    ]
