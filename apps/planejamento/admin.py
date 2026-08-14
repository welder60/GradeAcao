"""Área administrativa do planejamento (uso de suporte)."""

from django.contrib import admin

from apps.planejamento.models import Grade, GradeTurma, RestricaoDisponibilidade


class GradeTurmaInline(admin.TabularInline):
    model = GradeTurma
    extra = 0
    autocomplete_fields = ("turma",)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("nome", "usuario", "semestre", "valida", "preferida", "atualizado_em")
    list_filter = ("semestre", "valida", "preferida")
    search_fields = ("nome", "usuario__username")
    inlines = [GradeTurmaInline]


@admin.register(RestricaoDisponibilidade)
class RestricaoDisponibilidadeAdmin(admin.ModelAdmin):
    list_display = ("usuario", "codigo_dia", "codigo_horario", "motivo")
    list_filter = ("codigo_dia", "codigo_horario")
