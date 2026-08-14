"""Área administrativa do catálogo e da oferta (RF15, RN14)."""

from django.contrib import admin

from apps.catalogo.models import (
    ComponenteCurricular,
    ComponenteRelacao,
    Curso,
    Docente,
    MatrizComponente,
    MatrizCurricular,
    Semestre,
    Turma,
    TurmaDocente,
    TurmaHorario,
)


class ComponenteRelacaoInline(admin.TabularInline):
    model = ComponenteRelacao
    fk_name = "componente"
    extra = 0
    autocomplete_fields = ("componente_relacionado",)


class MatrizComponenteInline(admin.TabularInline):
    model = MatrizComponente
    extra = 0
    autocomplete_fields = ("componente",)


class TurmaHorarioInline(admin.TabularInline):
    model = TurmaHorario
    extra = 1


class TurmaDocenteInline(admin.TabularInline):
    model = TurmaDocente
    extra = 1
    autocomplete_fields = ("docente",)


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ("nome", "codigo", "campus", "turno")
    list_filter = ("campus", "turno")
    search_fields = ("nome", "codigo")


@admin.register(MatrizCurricular)
class MatrizCurricularAdmin(admin.ModelAdmin):
    list_display = ("nome", "curso", "vigencia_inicio", "vigencia_fim")
    list_filter = ("curso",)
    search_fields = ("nome", "codigo", "curso__nome")
    inlines = [MatrizComponenteInline]


@admin.register(ComponenteCurricular)
class ComponenteCurricularAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "carga_horaria", "departamento", "ativo")
    list_filter = ("ativo", "departamento")
    search_fields = ("codigo", "nome")
    inlines = [ComponenteRelacaoInline]


@admin.register(ComponenteRelacao)
class ComponenteRelacaoAdmin(admin.ModelAdmin):
    list_display = ("componente", "tipo", "componente_relacionado", "grupo", "bidirecional")
    list_filter = ("tipo", "bidirecional")
    search_fields = ("componente__codigo", "componente_relacionado__codigo")
    autocomplete_fields = ("componente", "componente_relacionado")


@admin.register(Semestre)
class SemestreAdmin(admin.ModelAdmin):
    list_display = ("codigo", "ano", "periodo", "ativo", "oferta_atualizada_em")
    list_filter = ("ativo", "ano")


@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = (
        "componente",
        "codigo",
        "semestre",
        "modalidade",
        "vagas_ofertadas",
        "vagas_ocupadas",
        "coletado_em",
    )
    list_filter = ("semestre", "modalidade")
    search_fields = ("componente__codigo", "componente__nome", "codigo")
    autocomplete_fields = ("componente",)
    inlines = [TurmaHorarioInline, TurmaDocenteInline]
