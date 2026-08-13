"""Configurações de produção (Railway + Supabase)."""

from .base import *  # noqa: F403
from .base import env

DEBUG = False

# Railway expõe o domínio público da aplicação nesta variável.
RAILWAY_DOMAIN = env("RAILWAY_PUBLIC_DOMAIN", default="")
if RAILWAY_DOMAIN:
    ALLOWED_HOSTS = [*ALLOWED_HOSTS, RAILWAY_DOMAIN]  # noqa: F405
    CSRF_TRUSTED_ORIGINS = [*CSRF_TRUSTED_ORIGINS, f"https://{RAILWAY_DOMAIN}"]  # noqa: F405

# Segurança (RNF14) — TLS terminado no proxy da plataforma.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

EMAIL_BACKEND = env(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="nao-responda@gradeacao.app")
