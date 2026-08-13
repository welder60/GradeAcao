# GradeAção

Planejador de grade horária para discentes da Universidade de Brasília.
Projeto acadêmico independente.

> **Aviso de desvinculação institucional**
> O GradeAção não possui qualquer vínculo, patrocínio, convênio ou endosso da
> Universidade de Brasília (UnB). A ferramenta não se integra a sistemas
> institucionais, não efetua matrícula e não substitui os canais oficiais da
> Universidade. O resultado do planejamento tem caráter auxiliar e não
> vinculante.

## Stack

Django · PostgreSQL (Supabase) · Supabase Auth e Storage · Railway · MkDocs Material

## Início rápido

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env          # preencha DJANGO_SECRET_KEY e DATABASE_URL
python manage.py migrate
python manage.py runserver
```

Documentação completa: `mkdocs serve` ou veja [`docs/`](docs/index.md).

## Estrutura

```
apps/comum          páginas institucionais e utilitários
apps/contas         perfil acadêmico e progresso
apps/catalogo       componentes, turmas e matrizes curriculares
apps/planejamento   grades, cenários e validação acadêmica
config/settings     base · dev · prod
docs/               documentação MkDocs
```

## Comandos úteis

| Comando | Ação |
|---|---|
| `python manage.py runserver` | Servidor de desenvolvimento |
| `pytest` | Testes com cobertura |
| `ruff check .` | Análise estática |
| `mkdocs serve` | Documentação local |
| `mkdocs build --strict` | Build de verificação da documentação |

## Licença

[MIT](LICENSE).
