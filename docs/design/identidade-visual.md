# Identidade Visual

Este documento disciplina a identidade visual do **GradeAção** — aplicação, site de documentação e materiais de divulgação. O objetivo é garantir consistência visual em todas as interfaces e facilitar decisões de design durante o desenvolvimento.

!!! warning "Relação com a identidade visual da UnB"
    O GradeAção é um **projeto acadêmico independente, sem vínculo, patrocínio ou endosso da Universidade de Brasília (UnB)**. A identidade visual do projeto é *inspirada* na paleta institucional da UnB, por ser uma ferramenta voltada aos discentes da universidade, mas:

    - É **proibido** usar o símbolo, o brasão ou o logotipo da UnB em qualquer parte da aplicação, documentação ou divulgação. A marca UnB é registrada no INPI e protegida pela Lei nº 9.279/1996.
    - É **proibido** qualquer elemento que sugira que o GradeAção é um produto oficial da UnB.
    - O aviso de desvinculação (`templates/parciais/aviso_desvinculacao.html`) deve permanecer visível em todas as páginas da aplicação.

## Princípios

1. **Clareza antes de ornamento** — a grade horária é o conteúdo central; a interface deve destacá-la, não competir com ela.
2. **Mobile-first** — todo componente é desenhado primeiro para telas pequenas (RNF01) e progressivamente aprimorado.
3. **Acessibilidade** — contraste mínimo WCAG 2.1 AA (4,5:1 para texto normal; 3:1 para texto grande e elementos de interface).
4. **Suporte a modo claro e escuro** — a aplicação declara `color-scheme: light dark` e toda cor deve ter equivalente legível nos dois modos.

## Paleta de cores

### Cores institucionais de referência (UnB)

A paleta primária do GradeAção deriva das duas cores oficiais definidas no Manual de Identidade Visual da UnB:

| Cor | Pantone | CMYK | Hex |
|---|---|---|---|
| Azul UnB | 654 | 100 / 65 / 0 / 35 | `#003366` |
| Verde UnB | 348 | 100 / 0 / 100 / 20 | `#006633` |

### Paleta da aplicação

As cores são definidas como *custom properties* CSS em `static/css/estilo.css` e devem ser referenciadas sempre pelos tokens — nunca por valores hexadecimais soltos no código.

#### Cores de marca

| Token | Valor (claro) | Valor (escuro) | Uso |
|---|---|---|---|
| `--cor-primaria` | `#003366` | `#6699cc` | Cabeçalhos, barra de navegação, links, botões primários |
| `--cor-primaria-hover` | `#00264d` | `#85add6` | Estados *hover*/*focus* de elementos primários |
| `--cor-secundaria` | `#006633` | `#66cc99` | Ações de confirmação, destaques positivos, elementos de apoio |
| `--cor-secundaria-hover` | `#004d26` | `#85d6ad` | Estados *hover*/*focus* de elementos secundários |

#### Cores neutras

| Token | Valor (claro) | Valor (escuro) | Uso |
|---|---|---|---|
| `--cor-fundo` | `#ffffff` | `#121a24` | Fundo da página |
| `--cor-superficie` | `#f2f5f8` | `#1c2733` | Cartões, painéis, células da grade |
| `--cor-borda` | `#c8d1da` | `#3a4a5c` | Bordas e divisores |
| `--cor-texto` | `#1a2733` | `#e6ecf2` | Texto principal |
| `--cor-texto-suave` | `#5c6b7a` | `#9fb0c0` | Texto secundário, legendas, metadados |

#### Cores de feedback

| Token | Valor (claro) | Valor (escuro) | Uso |
|---|---|---|---|
| `--cor-sucesso` | `#006633` | `#66cc99` | Operação concluída, matrícula possível |
| `--cor-alerta` | `#8a6d00` | `#e6c34d` | Avisos, pré-requisitos pendentes |
| `--cor-erro` | `#992200` | `#ff8866` | Erros, conflitos de horário |
| `--cor-info` | `#003366` | `#6699cc` | Mensagens informativas |

!!! note "Regra de contraste"
    Os valores da coluna "claro" são usados sobre fundos claros e os da coluna "escuro" sobre fundos escuros. Ao criar variações, verifique o contraste (por exemplo, com o [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)) antes de adicionar o token.

### Cores na grade horária

A grade é o componente central da aplicação e segue regras próprias:

- Cada disciplina alocada recebe uma cor de fundo derivada da paleta, sempre com texto em contraste AA.
- **Conflitos de horário** usam exclusivamente `--cor-erro`.
- Estados especiais (turma cheia, pré-requisito pendente) usam `--cor-alerta`.
- Cores de disciplina nunca reutilizam os tons exatos de feedback, para não gerar ambiguidade.

## Tipografia

A UnB adota as fontes institucionais **UnB Office** e **UnB Pro**, derivadas da família livre **Liberation Sans**. Como essas fontes não são distribuídas com a aplicação, o GradeAção usa uma pilha de fontes de sistema de aparência equivalente (sem serifa, humanista):

```css
--fonte-texto: system-ui, -apple-system, "Segoe UI", Roboto,
               "Liberation Sans", Arial, sans-serif;
--fonte-mono: ui-monospace, "Cascadia Code", "Source Code Pro",
              Menlo, Consolas, monospace;
```

### Escala tipográfica

| Elemento | Tamanho | Peso |
|---|---|---|
| Título de página (`h1`) | 2rem | 700 |
| Título de seção (`h2`) | 1.5rem | 700 |
| Subtítulo (`h3`) | 1.25rem | 600 |
| Texto corrido | 1rem | 400 |
| Legendas e metadados | 0.875rem | 400 |

- O tamanho-base é `1rem` (16px) e nunca deve ser reduzido abaixo de `0.875rem` em texto informativo.
- Altura de linha mínima de `1.5` para texto corrido.
- Ênfase se faz com **peso** ou cor (`--cor-primaria`), nunca com sublinhado — sublinhado é reservado para links.

## Nome e logotipo

- O nome da aplicação é grafado **GradeAção**, em CamelCase, com cedilha e til — nunca "Gradeacao", "Grade Ação" ou "GRADEAÇÃO" em texto corrido.
- Enquanto não houver logotipo próprio, o nome tipográfico em `--cor-primaria` e peso 700 cumpre esse papel.
- Um eventual logotipo deve ser original: não pode derivar do símbolo da UnB nem de qualquer marca registrada.

## Componentes de interface

### Botões

| Variante | Fundo | Texto | Uso |
|---|---|---|---|
| Primário | `--cor-primaria` | `#ffffff` | Ação principal da tela (uma por tela) |
| Secundário | transparente, borda `--cor-primaria` | `--cor-primaria` | Ações alternativas |
| Perigo | `--cor-erro` | `#ffffff` | Exclusões e ações destrutivas |

- Cantos arredondados de `0.375rem`, altura mínima de toque de `44px` (mobile-first).
- Estado de foco sempre visível: contorno de `2px` em `--cor-primaria-hover`.

### Links

- Cor `--cor-primaria`, sublinhados em texto corrido.
- Em navegação e menus, o sublinhado pode ser omitido, desde que haja outro indicador de interatividade.

### Formulários

- Rótulos sempre visíveis (não usar apenas `placeholder`).
- Campos com borda `--cor-borda`; em foco, borda `--cor-primaria`.
- Mensagens de validação com as cores de feedback e ícone ou texto — nunca cor sozinha como único indicador.

## Aplicação no site de documentação

O site MkDocs (tema Material) usa a mesma paleta, configurada em `docs/stylesheets/extra.css`:

- Cor primária do tema: Azul `#003366` (modo claro) / `#6699cc` (modo escuro).
- Cor de destaque (*accent*): Verde `#006633` / `#66cc99`.

Alterações na paleta da aplicação devem ser refletidas nesse arquivo para manter documentação e produto visualmente coerentes.

## O que não fazer

- ❌ Usar o brasão, símbolo ou logotipo da UnB.
- ❌ Introduzir cores fora da paleta sem registrar o token neste documento.
- ❌ Usar valores hexadecimais diretamente em templates ou CSS de componentes.
- ❌ Transmitir informação apenas por cor (conflito de horário, por exemplo, deve ter também texto ou ícone).
- ❌ Reduzir contraste abaixo de WCAG AA para fins estéticos.

## Referências

- Manual de Identidade Visual da UnB — [cic.unb.br](https://cic.unb.br/images/marca-cic/Manual_Identidade_Visual_UnB.pdf)
- [WCAG 2.1 — Contraste mínimo (1.4.3)](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
- [Liberation Fonts](https://github.com/liberationfonts/liberation-fonts) — base das fontes institucionais da UnB
