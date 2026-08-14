"""Área administrativa de perfil e progresso."""

from django.contrib import admin

from apps.contas.models import PerfilDiscente, ProgressoComponente


@admin.register(PerfilDiscente)
class PerfilDiscenteAdmin(admin.ModelAdmin):
    list_display = ("usuario", "matriz", "periodo_ingresso")
    search_fields = ("usuario__username", "usuario__email")
    autocomplete_fields = ("matriz",)


@admin.register(ProgressoComponente)
class ProgressoComponenteAdmin(admin.ModelAdmin):
    list_display = ("usuario", "componente", "status", "natureza", "por_equivalencia")
    list_filter = ("status", "natureza", "por_equivalencia")
    search_fields = ("usuario__username", "componente__codigo")
    autocomplete_fields = ("componente", "componente_equivalente")
