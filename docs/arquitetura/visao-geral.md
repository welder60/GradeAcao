# Visão Geral da Arquitetura

O GradeAção é um **monolito Django** com renderização server-side e
interatividade progressiva no cliente. A escolha é deliberada: o escopo do
produto, o tamanho da equipe e o horizonte do projeto não justificam a
complexidade operacional de uma arquitetura distribuída.

## Estrutura de diretórios

```
GradeAcao/
├── apps/
│   ├── comum/          # páginas institucionais, base de templates, utilitários
│   ├── contas/         # perfil acadêmico, autenticação (Google OAuth), progresso
│   ├── catalogo/       # componentes curriculares, turmas, matrizes, oferta
│   └── planejamento/   # grades, cenários, validação acadêmica, exportação
├── config/
│   ├── settings/
│   │   ├── base.py     # comum a todos os ambientes
│   │   ├── dev.py      # desenvolvimento local
│   │   └── prod.py     # Railway + Supabase
│   ├── urls.py
│   ├── wsgi.py         # aponta para config.settings.prod
│   └── asgi.py
├── docs/               # documentação MkDocs
├── static/             # CSS e JS do projeto
├── templates/          # templates globais (base, parciais)
└── manage.py           # aponta para config.settings.dev
```

## Responsabilidade de cada app

| App | Responsabilidade |
|---|---|
| `comum` | Página inicial, aviso de desvinculação, política de privacidade, template base, mixins e utilitários compartilhados |
| `contas` | Cadastro e autenticação via conta Google (OAuth 2.0, django-allauth), perfil acadêmico declaratório, registro de progresso na matriz |
| `catalogo` | Componentes curriculares, pré-requisitos, co-requisitos, equivalências, turmas, períodos letivos, matrizes e importação de oferta |
| `planejamento` | Montagem de grade, cenários, comparação, exportação, compartilhamento por link público |

## Regras de validação acadêmica

O **RNF22** exige que as regras de validação acadêmica (choque de horário,
pré-requisitos, co-requisitos, equivalências, limite de créditos) residam em
módulo próprio, desacoplado das camadas de apresentação e de persistência.

Convenção adotada: `apps/planejamento/regras/` — funções puras que recebem
estruturas de dados simples e devolvem diagnósticos, sem acessar o ORM nem
depender de `request`. Isso viabiliza a cobertura mínima de 80% exigida pelo
**RNF21**.

## Ambiente de execução

```
Navegador  ──HTTPS──▶  Django (Railway)  ──▶  PostgreSQL / Storage (Supabase)
                              │
                              └──OAuth 2.0──▶  Google (autenticação de usuários)
```

Segredos vivem exclusivamente em variáveis de ambiente (**RNF19**); veja
`.env.example`.
