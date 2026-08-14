# Área de curadoria

Área restrita em `/curadoria/` para manutenção dos dados públicos de estrutura
acadêmica e de oferta (**RF15**), com registro em log de toda operação
(**RF46**).

## Acesso

O acesso é restrito a curadores e administradores (**RN14**):

| Papel | Como é concedido |
|---|---|
| Curador | Usuário no grupo `Curador`, criado pela migração `curadoria.0001_grupo_curador` |
| Administrador | Usuário com `is_staff` ou `is_superuser` |

Usuário anônimo é enviado para a autenticação; usuário autenticado sem o papel
recebe **403**, e não um redirecionamento silencioso.

Para conceder o papel a alguém:

```bash
python manage.py shell -c "
from django.contrib.auth.models import Group, User
User.objects.get(username='fulana').groups.add(Group.objects.get(name='Curador'))
"
```

## Entidades sob curadoria

Cada entidade tem listagem com busca e filtros, criação, edição e exclusão.

| Seção | Entidades |
|---|---|
| Tabelas de domínio | campi, códigos de dia, códigos de horário |
| Estrutura acadêmica | cursos, matrizes curriculares, componentes da matriz, componentes curriculares, relações entre componentes |
| Oferta | semestres, docentes, turmas, horários de turma, docentes de turma |

## Como incluir uma nova entidade

A área não tem uma view por tabela: as views em `apps/curadoria/views.py` são
genéricas e resolvem a entidade pelo `slug` da URL. Incluir uma tabela no CRUD
é:

1. criar o `ModelForm` em `apps/curadoria/forms.py`, herdando de
   `FormularioDeCuradoria`;
2. acrescentar uma `EntidadeCuradoria` a `ENTIDADES`, em
   `apps/curadoria/registro.py`.

```python
EntidadeCuradoria(
    slug="minha-entidade",
    modelo=MinhaEntidade,
    formulario=forms.MinhaEntidadeForm,
    colunas=("codigo", "nome"),
    secao=SECAO_OFERTA,
    busca=("codigo", "nome"),
    filtros=("ativo",),
    relacionados=("curso",),
)
```

Nada mais precisa ser alterado: rotas, templates, navegação, painel e log
passam a contemplar a nova entidade. Os testes parametrizados em
`apps/curadoria/tests/test_acesso.py` cobrem automaticamente a listagem e o
formulário de criação da entidade nova.

## Log de operações (RF46)

Toda criação, edição e exclusão grava um `RegistroCarga` com origem
`MANUAL`, identificando o curador, a tabela afetada e o volume. O log **não**
armazena o conteúdo dos registros. Está disponível em `/curadoria/cargas/`.
