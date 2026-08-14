"""Views institucionais e de página inicial."""

from django.views.generic import TemplateView

from apps.catalogo.models import Semestre


class PaginaInicialView(TemplateView):
    """Porta de entrada do planejador."""

    template_name = "comum/pagina_inicial.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["semestre_ativo"] = Semestre.objects.atual()
        return contexto


class AvisoDesvinculacaoView(TemplateView):
    """Aviso de desvinculação institucional (RF42)."""

    template_name = "comum/aviso_desvinculacao.html"


class PoliticaPrivacidadeView(TemplateView):
    """Política de privacidade (RF43)."""

    template_name = "comum/politica_de_privacidade.html"


class SobreView(TemplateView):
    """Informações sobre o projeto e sobre a origem dos dados (RF45)."""

    template_name = "comum/sobre.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["semestres"] = Semestre.objects.order_by("-ano", "-periodo")[:6]
        return contexto
