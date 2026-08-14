"""
Controle de acesso da área de curadoria (RN14).

Somente usuários com papel de **curador** ou **administrador** alteram o
catálogo, a oferta e as tabelas de domínio. O papel de curador é representado
pelo grupo `Curador`, criado pela migração `0001_grupo_curador`.
"""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

GRUPO_CURADOR = "Curador"


def e_curador(usuario) -> bool:
    """Indica se o usuário pode alterar os dados públicos (RN14)."""
    if not usuario.is_authenticated:
        return False
    if usuario.is_superuser or usuario.is_staff:
        return True
    return usuario.groups.filter(name=GRUPO_CURADOR).exists()


class CuradorRequeridoMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Restringe a view a curadores e administradores.

    Usuário anônimo é enviado para a autenticação; usuário autenticado sem o
    papel recebe 403, e não um redirecionamento silencioso.
    """

    raise_exception = True
    permission_denied_message = (
        "Área restrita à curadoria de dados. Solicite o papel de curador à equipe."
    )

    def test_func(self) -> bool:
        return e_curador(self.request.user)

    def handle_no_permission(self):
        # Anônimo não deve receber 403: ele apenas ainda não se identificou.
        if not self.request.user.is_authenticated:
            self.raise_exception = False
        return super().handle_no_permission()
