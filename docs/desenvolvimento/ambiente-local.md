# Ambiente Local

Procedimento para executar o projeto localmente (**RNF24**).

## Pré-requisitos

- Python 3.12 ou superior
- PostgreSQL 14 ou superior (ou `USE_SQLITE=True` para dispensar o banco local)
- Git

## Instalação

```bash
git clone https://github.com/welder60/GradeAcao.git
cd GradeAcao

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements-dev.txt
cp .env.example .env             # Windows: copy .env.example .env
```

Edite o `.env` e defina, no mínimo, `DJANGO_SECRET_KEY` e `DATABASE_URL`.

Para gerar uma chave secreta:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Banco de dados

```bash
createdb gradeacao               # ou defina USE_SQLITE=True no .env
python manage.py migrate
python manage.py createsuperuser
```

## Execução

```bash
python manage.py runserver
```

Aplicação em <http://localhost:8000>, área administrativa em
<http://localhost:8000/admin/>.

## Testes e qualidade

```bash
pytest                 # testes com relatório de cobertura
ruff check .           # análise estática (PEP 8)
ruff format .          # formatação
```

## Documentação

```bash
mkdocs serve           # documentação em http://localhost:8000
mkdocs build --strict  # build de verificação; falha em links quebrados
```

!!! tip "Conflito de porta"
    `runserver` e `mkdocs serve` usam a porta 8000 por padrão. Rode um deles em
    outra porta, por exemplo `mkdocs serve -a localhost:8001`.

## Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|---|---|---|
| `DJANGO_SECRET_KEY` | sim | Chave secreta do Django |
| `DATABASE_URL` | sim | Connection string do PostgreSQL |
| `DEBUG` | não | `True` em desenvolvimento; `False` em produção |
| `ALLOWED_HOSTS` | em produção | Lista separada por vírgula |
| `CSRF_TRUSTED_ORIGINS` | em produção | Lista separada por vírgula |
| `USE_SQLITE` | não | `True` dispensa PostgreSQL local |
| `GOOGLE_CLIENT_ID` | para login | Client ID do OAuth 2.0 no Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | para login | Client secret do OAuth 2.0; nunca exposto ao cliente |
| `SUPABASE_URL` | não | URL do projeto Supabase (Storage) |
| `SUPABASE_ANON_KEY` | não | Chave pública do Supabase |
| `SUPABASE_SERVICE_KEY` | não | Chave de serviço; nunca exposta ao cliente |
