"""Área administrativa das tabelas de domínio (RF15)."""

from django.contrib import admin

from apps.comum.models import Campus, CodigoDia, CodigoHorario, RegistroCarga


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome")
    search_fields = ("codigo", "nome")


@admin.register(CodigoDia)
class CodigoDiaAdmin(admin.ModelAdmin):
    list_display = ("ordem", "codigo", "dia_da_semana")
    ordering = ("ordem",)


@admin.register(CodigoHorario)
class CodigoHorarioAdmin(admin.ModelAdmin):
    list_display = ("ordem", "codigo", "horario", "turno", "hora_inicio", "hora_fim")
    list_filter = ("turno",)
    ordering = ("ordem",)


@admin.register(RegistroCarga)
class RegistroCargaAdmin(admin.ModelAdmin):
    list_display = ("criado_em", "entidade", "origem", "registros_afetados", "curador")
    list_filter = ("origem", "entidade")
    readonly_fields = ("criado_em",)
    date_hierarchy = "criado_em"
