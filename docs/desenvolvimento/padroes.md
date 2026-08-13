# Padrões de Código

## Estilo

- **PEP 8**, verificado por `ruff` na integração contínua (**RNF20**).
- Linha de até 100 caracteres.
- Nomes de módulos, classes, campos e rotas em **português**, coerentes com o
  glossário do documento de requisitos (**RNF04**).
- Docstrings em português.

## Organização

- Cada app expõe `urls.py` com `app_name` definido.
- Templates de app ficam em `apps/<app>/templates/<app>/`.
- Templates globais e parciais ficam em `templates/`.
- Regras de validação acadêmica ficam em `apps/planejamento/regras/`, como
  funções puras, sem acesso ao ORM (**RNF22**).
- Testes ficam em `apps/<app>/tests/`, com arquivos `test_*.py`.

## Migrações

- Uma migração por mudança lógica; nome descritivo em português.
- Migrações são versionadas e nunca editadas após o merge.

## Commits

Formato [Conventional Commits](https://www.conventionalcommits.org/pt-br/):

```
feat(catalogo): adicionar filtro por faixa de horário
fix(planejamento): corrigir detecção de choque parcial
docs(requisitos): atualizar RF28
```

## Antes de abrir um Pull Request

```bash
ruff check .
ruff format --check .
pytest
mkdocs build --strict
```

## Segurança

- Segredos apenas em variáveis de ambiente (**RNF19**).
- Nunca solicitar, armazenar ou transmitir credenciais de sistemas
  institucionais (**RNF17**).
- Toda view que exponha dados de usuário deve verificar a titularidade
  (**RNF18**).
