# Documento de Requisitos de Software — GradeAção

**Projeto:** GradeAção — Planejador de Grade Horária para Discentes da UnB
**Versão:** 1.1
**Data:** 13 de agosto de 2026
**Natureza:** Projeto acadêmico independente, desenvolvido por discentes

---

> **Aviso de desvinculação institucional**
>
> O GradeAção é uma iniciativa independente, concebida e desenvolvida por discentes. **Não possui qualquer vínculo, patrocínio, convênio ou endosso da Universidade de Brasília (UnB), de seus decanatos, institutos, faculdades ou de qualquer outro órgão da instituição.**
>
> A ferramenta **não realiza integração com sistemas institucionais** (SIGAA, Matrícula Web, portais de autenticação ou quaisquer APIs internas), não efetua matrícula, não consulta dados pessoais de alunos em bases oficiais e não substitui os canais oficiais da Universidade. Todo o conteúdo acadêmico manipulado pelo sistema provém exclusivamente de **dados públicos** de oferta e de matriz curricular, além de informações fornecidas voluntariamente pelo próprio usuário.
>
> O resultado do planejamento produzido pela ferramenta tem caráter **auxiliar e não vinculante**. A confirmação de qualquer matrícula depende exclusivamente dos sistemas oficiais da Universidade.

---

## Sumário

1. [Introdução](#1-introdução)
2. [Descrição Geral](#2-descrição-geral)
3. [Requisitos Funcionais](#3-requisitos-funcionais)
4. [Requisitos Não Funcionais](#4-requisitos-não-funcionais)
5. [Regras de Negócio](#5-regras-de-negócio)
6. [Casos de Uso](#6-casos-de-uso)
7. [Matriz de Rastreabilidade](#7-matriz-de-rastreabilidade)
8. [Critérios de Aceitação](#8-critérios-de-aceitação)
9. [Restrições, Suposições e Riscos](#9-restrições-suposições-e-riscos)
10. [Glossário](#10-glossário)
11. [Referências](#11-referências)
12. [Histórico de Revisões](#12-histórico-de-revisões)

---

## 1. Introdução

### 1.1 Propósito

Este documento especifica os requisitos funcionais e não funcionais do **GradeAção**, uma aplicação web destinada a apoiar discentes da Universidade de Brasília no planejamento de sua grade horária semestral.

O documento destina-se à equipe de desenvolvimento, à coordenação do projeto acadêmico em que a ferramenta se insere e a eventuais avaliadores, servindo como referência para implementação, verificação e validação do produto.

### 1.2 Escopo do Produto

O GradeAção permite ao discente montar, comparar e avaliar cenários de grade horária antes do período de matrícula, a partir de dados públicos de oferta de componentes curriculares e da matriz curricular de seu curso.

**O produto se propõe a:**

- Registrar o perfil acadêmico do discente (curso, campus, matriz curricular, componentes já cursados);
- Permitir a montagem manual de grades a partir de turmas ofertadas;
- Detectar automaticamente choques de horário entre turmas selecionadas;
- Sinalizar pendências de pré-requisitos, co-requisitos e equivalências;
- Gerar e comparar múltiplos cenários de grade;
- Visualizar a grade em formato de calendário semanal e exportá-la;
- Projetar o progresso do discente na matriz curricular.

**O produto explicitamente não se propõe a:**

- Efetuar, alterar ou cancelar matrículas;
- Integrar-se a sistemas institucionais ou autenticar usuários com credenciais da Universidade;
- Consultar históricos escolares oficiais, índices de rendimento acadêmico ou situação de vagas em tempo real;
- Substituir orientação de coordenação de curso ou de docentes;
- Garantir a disponibilidade de vagas em qualquer turma.

### 1.3 Público-Alvo do Documento

| Público | Interesse principal |
|---|---|
| Equipe de desenvolvimento | Especificação para implementação e testes |
| Product Owner / Scrum Master | Priorização, planejamento de sprints e validação |
| Docente orientador / avaliadores | Avaliação de completude, coerência e rastreabilidade |
| Usuários representativos | Validação de aderência às necessidades reais |

### 1.4 Convenções

- Requisitos funcionais são identificados por **RF** seguido de numeração sequencial (`RF01`, `RF02`, ...).
- Requisitos não funcionais são identificados por **RNF**.
- Regras de negócio são identificadas por **RN**.
- Casos de uso são identificados por **UC**.
- A priorização segue o método **MoSCoW**:

| Sigla | Significado | Interpretação |
|---|---|---|
| **M** | *Must have* | Indispensável para a primeira entrega |
| **S** | *Should have* | Importante, mas contornável na primeira entrega |
| **C** | *Could have* | Desejável; implementado se houver folga |
| **W** | *Won't have (this time)* | Fora do escopo desta versão |

---

## 2. Descrição Geral

### 2.1 Perspectiva do Produto

O GradeAção é um sistema **novo e autocontido**, sem dependência operacional de sistemas institucionais; os únicos serviços externos utilizados são de infraestrutura (Railway, Supabase) e de autenticação (Google OAuth 2.0). Adota arquitetura **monolítica**, com renderização server-side e interatividade progressiva no cliente.

```
┌──────────────────────────────────────────────────────┐
│                    Navegador                          │
│         (HTML + CSS + JS progressivo)                 │
└───────────────────────┬──────────────────────────────┘
                        │ HTTPS
┌───────────────────────▼──────────────────────────────┐
│              Aplicação Django (monolito)              │
│  ┌─────────────┬──────────────┬───────────────────┐  │
│  │  contas     │  catalogo    │  planejamento     │  │
│  │  (perfil)   │  (oferta,    │  (grades,         │  │
│  │             │   matriz)    │   validações)     │  │
│  └─────────────┴──────────────┴───────────────────┘  │
│              Hospedagem: Railway                      │
└───────────┬───────────────────────────┬──────────────┘
            │                           │ OAuth 2.0
┌───────────▼──────────────┐    ┌───────▼──────────────┐
│         Supabase         │    │        Google        │
│  PostgreSQL  ·  Storage  │    │   (autenticação de   │
│       (arquivos)         │    │      usuários)       │
└──────────────────────────┘    └──────────────────────┘
            ▲
            │ carga manual / importação
┌───────────┴──────────────────┐
│  Dados públicos de oferta e  │
│  de matriz curricular        │
└──────────────────────────────┘
```

### 2.2 Stack Tecnológica

| Camada | Tecnologia | Observação |
|---|---|---|
| Arquitetura | Monolito | Aplicação única, módulos internos por domínio |
| Backend / Framework | Django | Python; templates server-side; Django ORM |
| Banco de dados | PostgreSQL (Supabase) | Instância gerenciada |
| Autenticação | Google OAuth 2.0 (django-allauth) | Login exclusivo com conta Google; o sistema não gerencia senhas |
| Armazenamento de arquivos | Supabase Storage | Exportações e arquivos de carga de dados |
| Hospedagem / CI-CD | Railway | Deploy contínuo a partir do repositório |
| Front-end | Templates Django + CSS + JS leve | Sem framework SPA; interatividade progressiva |

> **Nota:** a escolha do monolito é deliberada. O escopo do produto, o tamanho da equipe e o horizonte do projeto não justificam a complexidade operacional de uma arquitetura distribuída.

### 2.3 Funções Principais do Produto

| # | Função | Descrição resumida |
|---|---|---|
| F1 | Gestão de perfil acadêmico | Curso, campus, matriz curricular e período de ingresso |
| F2 | Catálogo de componentes e turmas | Consulta à oferta pública carregada no sistema |
| F3 | Registro de progresso | Marcação de componentes cursados, em curso e pendentes |
| F4 | Montagem de grade | Seleção de turmas com validação em tempo real |
| F5 | Validação acadêmica | Choques, pré-requisitos, co-requisitos, equivalências e créditos |
| F6 | Cenários alternativos | Criação, nomeação e comparação de múltiplas grades |
| F7 | Visualização e exportação | Calendário semanal, PDF, imagem e arquivo de calendário |
| F8 | Projeção de matriz | Percentual de conclusão e componentes remanescentes |
| F9 | Compartilhamento | Link público somente-leitura de uma grade |
| F10 | Administração de dados | Carga e curadoria da oferta e das matrizes curriculares |

### 2.4 Classes de Usuário

| Ator | Descrição | Frequência de uso |
|---|---|---|
| **Discente visitante** | Acessa sem cadastro; explora o catálogo e monta grade em sessão temporária | Ocasional |
| **Discente cadastrado** | Possui perfil, salva grades e acompanha progresso na matriz | Intensa em período de matrícula |
| **Curador de dados** | Membro da equipe responsável por carregar e validar a oferta pública e as matrizes | Semestral |
| **Administrador** | Membro da equipe com acesso ao Django Admin; gerencia usuários e configurações | Eventual |

### 2.5 Personas

**Persona 1 — Calouro que segue a matriz**
Ingressou no semestre corrente, ainda não conhece as siglas dos componentes nem a lógica de pré-requisitos. Precisa de uma sugestão fiel à matriz curricular e de uma linguagem que explique os termos.

**Persona 2 — Veterano com pendências**
Reprovou componentes em semestres anteriores e precisa encaixar dependências junto a componentes do período regular. Sua maior dor é o choque de horário entre turmas escassas.

**Persona 3 — Discente que trabalha**
Tem disponibilidade restrita a um turno específico. Precisa filtrar a oferta por janela de horário e descartar rapidamente cenários inviáveis.

**Persona 4 — Discente em transição de matriz**
Mudou de curso ou teve alteração de matriz curricular. Precisa entender quais equivalências reduzem sua carga pendente.

### 2.6 Ambiente Operacional

- **Cliente:** navegadores modernos (Chrome, Firefox, Safari, Edge), em desktop e dispositivos móveis. Layout *mobile-first*.
- **Servidor:** aplicação Django hospedada em Railway; banco PostgreSQL e serviços auxiliares em Supabase.
- **Conectividade:** requer conexão à internet; operação offline não faz parte do escopo desta versão.

---

## 3. Requisitos Funcionais

### 3.1 Conta e Perfil Acadêmico

| ID | Requisito | Prioridade |
|---|---|---|
| **RF01** | O sistema deve permitir que o discente crie conta autenticando-se com sua conta Google (OAuth 2.0), sem cadastro de senha local. | M |
| **RF02** | O sistema deve permitir a autenticação via conta Google e o encerramento de sessão. | M |
| **RF03** | ~~Recuperação de senha por e-mail.~~ **Não se aplica:** a autenticação é delegada ao Google e o sistema não gerencia senhas. | W |
| **RF04** | O sistema deve permitir que o discente registre seu perfil acadêmico: curso, campus, matriz curricular e período de ingresso. | M |
| **RF05** | O sistema deve permitir que o discente edite ou exclua seu perfil e sua conta, com remoção dos dados associados. | M |
| **RF06** | O sistema deve permitir o uso do planejador sem cadastro, em sessão temporária, com a ressalva de que as grades não serão persistidas. | S |

### 3.2 Catálogo de Componentes Curriculares e Turmas

| ID | Requisito | Prioridade |
|---|---|---|
| **RF07** | O sistema deve manter um catálogo de componentes curriculares contendo código, nome, créditos, ementa resumida (quando pública), pré-requisitos, co-requisitos e equivalências. | M |
| **RF08** | O sistema deve manter as turmas ofertadas por período letivo, contendo identificação da turma, campus, horários, docente responsável (quando público) e número de vagas divulgado. | M |
| **RF09** | O sistema deve permitir a busca de componentes curriculares por código, nome ou parte do nome. | M |
| **RF10** | O sistema deve permitir a filtragem da oferta por campus, turno, dia da semana, faixa de horário, docente e departamento. | M |
| **RF11** | O sistema deve exibir a matriz curricular do curso do discente, organizada por período recomendado. | M |
| **RF12** | O sistema deve indicar visivelmente, em toda tela de catálogo, o período letivo de referência e a data da última atualização dos dados. | M |
| **RF13** | O sistema deve permitir que o curador carregue a oferta de um período letivo por meio de importação de arquivo estruturado (CSV ou similar). | M |
| **RF14** | O sistema deve validar o arquivo importado e apresentar relatório de erros por linha, sem gravar registros inconsistentes. | S |
| **RF15** | O sistema deve permitir a criação e edição manual de componentes, turmas e matrizes curriculares por meio de área administrativa. | M |

### 3.3 Progresso Acadêmico do Discente

| ID | Requisito | Prioridade |
|---|---|---|
| **RF16** | O sistema deve permitir que o discente marque componentes curriculares como *cursados*, *em curso* ou *pendentes*. | M |
| **RF17** | O sistema deve permitir que o discente registre componentes cursados que não constem de sua matriz, classificando-os como optativos ou de módulo livre. | S |
| **RF18** | O sistema deve calcular e exibir o total de créditos cursados, em curso e pendentes em relação à matriz curricular. | M |
| **RF19** | O sistema deve permitir o registro de equivalências aproveitadas pelo discente, considerando o componente equivalente como cumprido para fins de validação. | S |
| **RF20** | O sistema deve exibir a projeção de períodos restantes para conclusão, com base na média de créditos por período informada pelo discente. | C |

### 3.4 Montagem da Grade

| ID | Requisito | Prioridade |
|---|---|---|
| **RF21** | O sistema deve permitir que o discente adicione e remova turmas de uma grade em construção. | M |
| **RF22** | O sistema deve detectar e sinalizar choques de horário entre turmas selecionadas, identificando as turmas e os intervalos conflitantes. | M |
| **RF23** | O sistema deve impedir a gravação de uma grade que contenha choque de horário não reconhecido pelo discente. | M |
| **RF24** | O sistema deve sinalizar quando um componente selecionado possuir pré-requisito não registrado como cumprido no perfil do discente. | M |
| **RF25** | O sistema deve sinalizar quando um componente selecionado possuir co-requisito ausente na grade em construção. | M |
| **RF26** | O sistema deve exibir alerta quando o total de créditos da grade exceder o limite configurado para o curso. | S |
| **RF27** | O sistema deve calcular e exibir o total de créditos e a carga horária semanal da grade em construção. | M |
| **RF28** | O sistema deve permitir que o discente defina restrições de disponibilidade (dias e faixas de horário indisponíveis) e ocultar da oferta as turmas incompatíveis. | S |
| **RF29** | O sistema deve permitir marcar turmas como "prioritárias" e "alternativas" dentro de um mesmo componente curricular. | C |
| **RF30** | O sistema deve sugerir automaticamente uma grade a partir da matriz curricular, do progresso registrado e das restrições de disponibilidade do discente. | C |

### 3.5 Cenários de Grade

| ID | Requisito | Prioridade |
|---|---|---|
| **RF31** | O sistema deve permitir que o discente cadastrado salve múltiplas grades para um mesmo período letivo, com nome identificador. | M |
| **RF32** | O sistema deve permitir renomear, duplicar e excluir grades salvas. | M |
| **RF33** | O sistema deve permitir a comparação lado a lado de duas ou três grades, exibindo créditos, componentes distintos, janelas livres e dias sem aula. | S |
| **RF34** | O sistema deve permitir que o discente marque uma grade como preferida. | C |

### 3.6 Visualização, Exportação e Compartilhamento

| ID | Requisito | Prioridade |
|---|---|---|
| **RF35** | O sistema deve exibir a grade em formato de calendário semanal, com blocos posicionados por dia e horário. | M |
| **RF36** | O sistema deve exibir a grade em formato de lista, com código, nome, turma, horário, docente e campus. | M |
| **RF37** | O sistema deve permitir a exportação da grade em PDF. | S |
| **RF38** | O sistema deve permitir a exportação da grade como imagem. | C |
| **RF39** | O sistema deve permitir a exportação da grade em formato de calendário (`.ics`), com eventos recorrentes semanais. | C |
| **RF40** | O sistema deve permitir a geração de link público somente-leitura de uma grade, revogável pelo discente a qualquer momento. | C |
| **RF41** | Toda exportação e todo compartilhamento devem conter aviso de que o documento é gerado por ferramenta não oficial e não constitui comprovante de matrícula. | M |

### 3.7 Transparência e Conformidade

| ID | Requisito | Prioridade |
|---|---|---|
| **RF42** | O sistema deve exibir, em página dedicada e acessível a partir de todas as telas, o aviso de desvinculação institucional. | M |
| **RF43** | O sistema deve disponibilizar página de política de privacidade descrevendo os dados coletados, sua finalidade, sua base legal e o prazo de retenção. | M |
| **RF44** | O sistema deve permitir que o discente exporte todos os seus dados pessoais em formato legível por máquina. | S |
| **RF45** | O sistema deve informar a origem e a data de coleta dos dados públicos de oferta exibidos. | M |
| **RF46** | O sistema deve registrar em log as operações de carga de dados, com identificação do curador, data e volume de registros afetados. | S |

---

## 4. Requisitos Não Funcionais

### 4.1 Usabilidade

| ID | Requisito | Métrica de verificação |
|---|---|---|
| **RNF01** | A interface deve ser responsiva e projetada com abordagem *mobile-first*. | Uso pleno das funções em viewport de 360 px de largura |
| **RNF02** | Um discente sem treinamento prévio deve conseguir montar uma grade com quatro componentes em até 10 minutos. | Teste de usabilidade com 5 participantes; taxa de sucesso ≥ 80% |
| **RNF03** | Choques de horário e pendências de pré-requisito devem ser sinalizados por cor **e** por texto, sem depender exclusivamente de cor. | Inspeção manual e simulação de daltonismo |
| **RNF04** | A terminologia da interface deve seguir a nomenclatura do glossário deste documento. | Revisão de textos da interface |

### 4.2 Acessibilidade

| ID | Requisito | Métrica de verificação |
|---|---|---|
| **RNF05** | As telas principais devem atender ao nível AA da WCAG 2.1. | Auditoria automatizada com zero violações críticas |
| **RNF06** | Todas as funções devem ser operáveis por teclado. | Percurso completo sem uso de mouse |
| **RNF07** | O contraste mínimo de texto deve ser de 4,5:1. | Verificação automatizada |

### 4.3 Desempenho

| ID | Requisito | Métrica de verificação |
|---|---|---|
| **RNF08** | A busca no catálogo deve retornar resultados em até 2 segundos para 95% das requisições. | Teste de carga sobre base com 5.000 turmas |
| **RNF09** | A validação de choque de horário deve ocorrer sem recarga completa de página, em até 500 ms. | Medição no cliente |
| **RNF10** | O sistema deve suportar 100 usuários simultâneos sem degradação superior a 50% no tempo de resposta. | Teste de carga em ambiente de homologação |

### 4.4 Confiabilidade e Disponibilidade

| ID | Requisito | Métrica de verificação |
|---|---|---|
| **RNF11** | O sistema deve apresentar disponibilidade mínima de 99% durante o período de matrícula divulgado. | Monitoramento de *uptime* |
| **RNF12** | O banco de dados deve possuir rotina de backup automatizada, com retenção mínima de 7 dias. | Configuração verificada no Supabase |
| **RNF13** | Falhas em operações de exportação não devem comprometer a integridade das grades salvas. | Teste de injeção de falha |

### 4.5 Segurança e Privacidade

| ID | Requisito | Métrica de verificação |
|---|---|---|
| **RNF14** | Toda comunicação entre cliente e servidor deve ocorrer sobre HTTPS. | Verificação de certificado e redirecionamento |
| **RNF15** | O sistema não deve armazenar senhas de usuários; a autenticação é integralmente delegada ao Google (OAuth 2.0), persistindo-se apenas o identificador da conta, o nome e o e-mail. | Revisão do modelo de dados e de configuração |
| **RNF16** | O sistema deve coletar apenas os dados estritamente necessários à finalidade declarada, em observância ao princípio da necessidade previsto na LGPD. | Revisão do modelo de dados |
| **RNF17** | O sistema não deve solicitar, armazenar ou transmitir credenciais de sistemas institucionais em nenhuma hipótese. | Revisão de código e de formulários |
| **RNF18** | Um usuário não deve acessar grades ou perfis de outro usuário, exceto por link público expressamente gerado pelo titular. | Teste de controle de acesso |
| **RNF19** | Segredos de aplicação devem ser mantidos em variáveis de ambiente, nunca versionados no repositório. | Inspeção do repositório |

### 4.6 Manutenibilidade e Portabilidade

| ID | Requisito | Métrica de verificação |
|---|---|---|
| **RNF20** | O código deve seguir a PEP 8 e ser verificado por analisador estático na integração contínua. | Pipeline sem violações bloqueantes |
| **RNF21** | A cobertura de testes automatizados nos módulos de validação acadêmica deve ser de no mínimo 80%. | Relatório de cobertura |
| **RNF22** | As regras de validação acadêmica devem residir em módulo próprio, desacoplado das camadas de apresentação e de persistência. | Revisão de arquitetura |
| **RNF23** | O sistema deve suportar múltiplos cursos, campi e matrizes curriculares por configuração de dados, sem alteração de código. | Cadastro de segundo curso em ambiente de teste |
| **RNF24** | O sistema deve ser executável localmente por meio de procedimento documentado, com banco PostgreSQL local. | Execução por membro externo à equipe seguindo o README |
| **RNF25** | O deploy deve ser automatizado a partir do repositório principal. | Pipeline Railway ativo |

### 4.7 Internacionalização e Conteúdo

| ID | Requisito | Métrica de verificação |
|---|---|---|
| **RNF26** | A interface deve ser integralmente em português brasileiro. | Revisão de textos |
| **RNF27** | Datas e horários devem seguir o formato brasileiro e o fuso horário `America/Sao_Paulo`. | Inspeção de renderização |

---

## 5. Regras de Negócio

| ID | Regra |
|---|---|
| **RN01** | Duas turmas apresentam **choque de horário** quando possuem interseção não vazia de intervalo em um mesmo dia da semana, ainda que parcial. |
| **RN02** | Uma grade contendo choque de horário não pode ser salva como grade válida; pode, contudo, ser mantida como rascunho explicitamente marcado como inválido. |
| **RN03** | Um **pré-requisito** é considerado cumprido quando o componente exigido está marcado como *cursado* no perfil do discente ou quando há **equivalência** registrada como cumprida. |
| **RN04** | Um **co-requisito** é considerado atendido quando o componente exigido está presente na mesma grade em construção ou já consta como *cursado*. |
| **RN05** | Componente marcado como *em curso* não satisfaz pré-requisito para o mesmo período letivo, apenas para períodos subsequentes. |
| **RN06** | A **equivalência** é bidirecional apenas quando assim registrada no cadastro; caso contrário, vale no sentido declarado. |
| **RN07** | O limite de créditos por período é atributo configurável por curso; na ausência de valor cadastrado, o sistema apenas informa o total, sem bloquear. |
| **RN08** | Pendências de pré-requisito e de co-requisito geram **alerta**, não bloqueio, uma vez que o sistema não dispõe de dados oficiais do histórico do discente. |
| **RN09** | Todo dado de oferta pertence a exatamente um período letivo; grades são sempre vinculadas a um período letivo. |
| **RN10** | Dados de vagas, quando exibidos, são informativos e referem-se à data da coleta, jamais a disponibilidade em tempo real. |
| **RN11** | O sistema não emite, sob nenhuma forma, documento com aparência de comprovante oficial de matrícula. |
| **RN12** | O perfil acadêmico é declaratório: os dados são informados pelo próprio discente e não são verificados contra fonte oficial. |
| **RN13** | A exclusão da conta implica a remoção definitiva do perfil, das grades e dos links públicos associados. |
| **RN14** | Somente usuários com papel de curador ou administrador podem alterar o catálogo de componentes, turmas e matrizes. |

---

## 6. Casos de Uso

### 6.1 Atores

| Ator | Descrição |
|---|---|
| Discente visitante | Usuário não autenticado |
| Discente cadastrado | Usuário autenticado com perfil acadêmico |
| Curador de dados | Responsável pela carga e curadoria dos dados públicos |
| Administrador | Responsável pela gestão do sistema |

### 6.2 Diagrama de Casos de Uso (visão textual)

```
Discente visitante
  ├── UC01 Consultar oferta de componentes
  └── UC02 Montar grade em sessão temporária

Discente cadastrado  (herda de Discente visitante)
  ├── UC03 Manter perfil acadêmico
  ├── UC04 Registrar progresso na matriz curricular
  ├── UC05 Montar e salvar grade
  │      ├── «include» UC06 Validar choques de horário
  │      └── «include» UC07 Validar pré-requisitos e co-requisitos
  ├── UC08 Comparar cenários de grade
  ├── UC09 Exportar grade
  └── UC10 Compartilhar grade por link público

Curador de dados
  ├── UC11 Importar oferta de período letivo
  └── UC12 Manter matriz curricular

Administrador
  └── UC13 Gerenciar usuários e papéis
```

### 6.3 Especificação dos Casos de Uso Principais

---

#### UC05 — Montar e salvar grade

| Campo | Conteúdo |
|---|---|
| **Ator principal** | Discente cadastrado |
| **Objetivo** | Compor uma grade horária válida para um período letivo |
| **Pré-condições** | Usuário autenticado com perfil acadêmico preenchido; oferta do período carregada no sistema |
| **Pós-condições** | Grade persistida e vinculada ao perfil do discente |
| **Requisitos relacionados** | RF21–RF28, RF31, RF35 |

**Fluxo principal**

1. O discente seleciona o período letivo desejado.
2. O sistema apresenta a oferta filtrada pelo curso e campus do perfil.
3. O discente aplica filtros de turno, dia e faixa de horário.
4. O discente seleciona uma turma.
5. O sistema executa **UC06** e **UC07** e atualiza a visualização.
6. O discente repete os passos 4 e 5 até concluir a composição.
7. O sistema exibe o total de créditos e a carga horária semanal.
8. O discente atribui um nome à grade e solicita a gravação.
9. O sistema valida a ausência de choques e persiste a grade.
10. O sistema confirma a gravação e exibe a grade em calendário semanal.

**Fluxos alternativos**

- **FA1 — Choque de horário detectado (passo 5):** o sistema destaca as turmas conflitantes e o intervalo de sobreposição; o discente remove uma das turmas e o fluxo retorna ao passo 4.
- **FA2 — Pré-requisito pendente (passo 5):** o sistema exibe alerta identificando o componente exigido; o discente pode prosseguir cientemente ou remover a turma.
- **FA3 — Limite de créditos excedido (passo 7):** o sistema exibe alerta informativo; o discente decide se prossegue.
- **FA4 — Tentativa de gravação com choque (passo 9):** o sistema recusa a gravação como grade válida e oferece a alternativa de salvar como rascunho inválido.

**Fluxos de exceção**

- **FE1 — Falha de persistência:** o sistema informa o erro, preserva a composição em memória e permite nova tentativa.

---

#### UC06 — Validar choques de horário

| Campo | Conteúdo |
|---|---|
| **Ator principal** | Sistema (invocado por UC05) |
| **Objetivo** | Identificar sobreposições de horário entre turmas da grade |
| **Pré-condições** | Ao menos duas turmas presentes na grade em construção |
| **Pós-condições** | Conjunto de conflitos identificado e apresentado |
| **Requisitos relacionados** | RF22, RF23; regras RN01, RN02 |

**Fluxo principal**

1. O sistema obtém os horários de todas as turmas da grade.
2. O sistema compara par a par os intervalos de cada dia da semana.
3. Para cada interseção não vazia, o sistema registra um conflito.
4. O sistema retorna a lista de conflitos com as turmas e os intervalos envolvidos.

---

#### UC07 — Validar pré-requisitos e co-requisitos

| Campo | Conteúdo |
|---|---|
| **Ator principal** | Sistema (invocado por UC05) |
| **Objetivo** | Sinalizar pendências acadêmicas nos componentes selecionados |
| **Pré-condições** | Perfil com progresso registrado; componentes com dependências cadastradas |
| **Pós-condições** | Alertas apresentados ao discente |
| **Requisitos relacionados** | RF24, RF25, RF19; regras RN03, RN04, RN05, RN06, RN08 |

**Fluxo principal**

1. Para cada componente da grade, o sistema recupera pré-requisitos, co-requisitos e equivalências.
2. O sistema verifica se cada pré-requisito consta como *cursado* ou coberto por equivalência cumprida.
3. O sistema verifica se cada co-requisito está presente na grade ou já foi cursado.
4. O sistema retorna a lista de pendências, classificadas por tipo e severidade.
5. O sistema apresenta as pendências como **alertas não bloqueantes**, conforme RN08.

---

#### UC11 — Importar oferta de período letivo

| Campo | Conteúdo |
|---|---|
| **Ator principal** | Curador de dados |
| **Objetivo** | Carregar no sistema a oferta pública de um período letivo |
| **Pré-condições** | Usuário autenticado com papel de curador; arquivo estruturado disponível |
| **Pós-condições** | Turmas do período disponíveis no catálogo, com data de atualização registrada |
| **Requisitos relacionados** | RF13, RF14, RF45, RF46; regras RN09, RN10, RN14 |

**Fluxo principal**

1. O curador seleciona o período letivo de destino e envia o arquivo.
2. O sistema valida a estrutura e o conteúdo de cada linha.
3. O sistema apresenta prévia com o total de registros válidos e inválidos.
4. O curador confirma a importação.
5. O sistema persiste os registros válidos e atualiza a data de coleta.
6. O sistema registra a operação em log.

**Fluxos alternativos**

- **FA1 — Arquivo com inconsistências:** o sistema apresenta relatório por linha e não persiste nenhum registro até correção e reenvio.
- **FA2 — Turma já existente:** o sistema apresenta as divergências e solicita decisão entre atualizar ou ignorar.

---

## 7. Matriz de Rastreabilidade

| Requisito | Caso de uso | Regra de negócio | Prioridade |
|---|---|---|---|
| RF01–RF02 | UC03 | — | M |
| RF03 | — (não se aplica) | — | W |
| RF04–RF05 | UC03 | RN12, RN13 | M |
| RF06 | UC02 | — | S |
| RF07–RF08 | UC01, UC11 | RN09 | M |
| RF09–RF10 | UC01 | — | M |
| RF11 | UC04 | — | M |
| RF12 | UC01 | RN10 | M |
| RF13–RF14 | UC11 | RN09, RN14 | M / S |
| RF15 | UC12, UC13 | RN14 | M |
| RF16–RF18 | UC04 | RN03, RN05, RN12 | M |
| RF19 | UC04, UC07 | RN03, RN06 | S |
| RF20 | UC04 | — | C |
| RF21 | UC05 | — | M |
| RF22–RF23 | UC06 | RN01, RN02 | M |
| RF24–RF25 | UC07 | RN03, RN04, RN08 | M |
| RF26 | UC05 | RN07 | S |
| RF27 | UC05 | — | M |
| RF28–RF29 | UC05 | — | S / C |
| RF30 | UC05 | RN03, RN07 | C |
| RF31–RF32 | UC05 | RN09 | M |
| RF33–RF34 | UC08 | — | S / C |
| RF35–RF36 | UC05 | — | M |
| RF37–RF39 | UC09 | RN11 | S / C |
| RF40 | UC10 | RN13 | C |
| RF41 | UC09, UC10 | RN11 | M |
| RF42–RF43 | — (transversal) | RN11, RN12 | M |
| RF44 | UC03 | RN13 | S |
| RF45 | UC01, UC11 | RN10 | M |
| RF46 | UC11 | RN14 | S |

---

## 8. Critérios de Aceitação

A versão 1.0 do GradeAção será considerada aceita quando:

1. Todos os requisitos de prioridade **Must have** estiverem implementados e verificados por teste automatizado ou por roteiro de teste manual documentado.
2. Um discente conseguir, partindo de conta nova, registrar perfil, montar grade com no mínimo quatro componentes, receber sinalização correta de choque e salvar a grade sem intervenção da equipe.
3. A detecção de choque de horário apresentar zero falsos negativos em um conjunto de teste com ao menos 30 casos, incluindo sobreposições parciais e turmas com múltiplos encontros semanais.
4. O aviso de desvinculação institucional estiver acessível a partir de todas as telas e presente em todas as exportações.
5. A auditoria de acessibilidade das telas principais não apresentar violações de nível A ou AA classificadas como críticas.
6. A cobertura de testes do módulo de validação acadêmica atingir no mínimo 80%.
7. A aplicação estiver implantada em ambiente acessível publicamente, com HTTPS e deploy automatizado.
8. A política de privacidade estiver publicada e coerente com os dados efetivamente coletados.

---

## 9. Restrições, Suposições e Riscos

### 9.1 Restrições

| ID | Restrição |
|---|---|
| **RE01** | Arquitetura monolítica em Django, hospedada em Railway, com PostgreSQL em Supabase. |
| **RE02** | Vedada qualquer integração com sistemas institucionais, bem como o uso de credenciais institucionais. |
| **RE03** | Somente dados públicos e dados declarados pelo próprio usuário podem alimentar o sistema. |
| **RE04** | Equipe composta exclusivamente por discentes, com disponibilidade limitada pelo calendário acadêmico. |
| **RE05** | Orçamento restrito aos planos gratuitos ou de baixo custo das plataformas adotadas. |
| **RE06** | O produto não pode apresentar identidade visual que sugira caráter oficial da Universidade. |

### 9.2 Suposições

| ID | Suposição |
|---|---|
| **SU01** | Os dados públicos de oferta permanecerão acessíveis e em formato tratável a cada período letivo. |
| **SU02** | Os discentes conhecem seu próprio histórico com precisão suficiente para alimentar o perfil. |
| **SU03** | A estrutura de matriz curricular, pré-requisitos e co-requisitos permanecerá estável ao longo do desenvolvimento. |
| **SU04** | O volume de usuários simultâneos permanecerá compatível com os planos contratados nas plataformas. |

### 9.3 Riscos

| ID | Risco | Impacto | Prob. | Mitigação |
|---|---|---|---|---|
| **RI01** | Mudança no formato ou na disponibilidade dos dados públicos | Alto | Média | Camada de importação desacoplada; possibilidade de carga manual |
| **RI02** | Dados de oferta desatualizados induzirem o discente a erro | Alto | Média | Exibição obrigatória da data de coleta (RF12, RF45) e avisos em exportações |
| **RI03** | Percepção equivocada de que a ferramenta é oficial | Alto | Média | Aviso de desvinculação em todas as telas e exportações (RF41, RF42) |
| **RI04** | Pico de acesso no período de matrícula exceder a capacidade contratada | Médio | Alta | Teste de carga prévio; *cache* de consultas de catálogo |
| **RI05** | Complexidade das regras de equivalência superar a estimativa | Médio | Média | Priorização MoSCoW; equivalências como *Should have* |
| **RI06** | Indisponibilidade da equipe em período de provas | Médio | Alta | Planejamento de sprints alinhado ao calendário acadêmico |
| **RI07** | Tratamento inadequado de dados pessoais | Alto | Baixa | Minimização de dados (RNF16), política de privacidade e exclusão completa de conta |
| **RI08** | Dependência exclusiva do login com Google: indisponibilidade do provedor ou perda de acesso à conta Google impede o uso da ferramenta | Médio | Baixa | Autenticação delegada a provedor de alta disponibilidade; exportação de dados pessoais (RF44) preserva o acesso ao conteúdo |

---

## 10. Glossário

| Termo | Definição |
|---|---|
| **Campus** | Unidade física da Universidade na qual são ofertados cursos e componentes curriculares. No contexto do GradeAção, atributo de filtragem da oferta e do perfil do discente, relevante para o cálculo de deslocamento entre aulas. |
| **Co-requisito** | Componente curricular que deve ser cursado no mesmo período letivo que outro componente, ou já ter sido cursado anteriormente. Diferencia-se do pré-requisito por admitir cumprimento simultâneo. |
| **Componente curricular** | Unidade de ensino com código, denominação, carga horária e créditos próprios, ofertada em turmas. Corresponde ao que coloquialmente se denomina "disciplina" ou "matéria". |
| **Curso** | Programa de formação ao qual o discente está vinculado, associado a uma ou mais matrizes curriculares e a um campus de oferta. |
| **Discente** | Estudante regularmente vinculado a um curso da Universidade. Usuário-alvo primário do GradeAção. |
| **Docente** | Professor responsável pela condução de uma turma. No sistema, atributo informativo da turma, utilizável como critério de filtragem quando publicamente divulgado. |
| **Equivalência** | Relação entre componentes curriculares pela qual o cumprimento de um satisfaz a exigência do outro, total ou parcialmente. Pode ser unidirecional ou bidirecional, conforme cadastrado (RN06). |
| **Matriz curricular** | Conjunto estruturado de componentes curriculares — obrigatórios e optativos — exigidos para a integralização de um curso, com distribuição recomendada por período. |
| **Pré-requisito** | Componente curricular cujo cumprimento prévio é condição para a cursada de outro componente. |

### 10.1 Termos auxiliares do projeto

| Termo | Definição |
|---|---|
| **Grade** | Conjunto de turmas selecionadas pelo discente para um período letivo. |
| **Cenário** | Grade alternativa salva para fins de comparação. |
| **Choque de horário** | Sobreposição, total ou parcial, entre os intervalos de duas turmas em um mesmo dia da semana. |
| **Oferta** | Conjunto de turmas disponibilizadas em um determinado período letivo. |
| **Período letivo** | Intervalo acadêmico ao qual se vinculam a oferta e as grades (ex.: 2026/2). |
| **Turma** | Instância concreta de um componente curricular em um período letivo, com horário, campus, docente e vagas próprios. |
| **Curador de dados** | Membro da equipe responsável pela carga e pela conferência dos dados públicos no sistema. |

---

## 11. Referências

- **Lei nº 13.709/2018** — Lei Geral de Proteção de Dados Pessoais (LGPD).
- **Lei nº 12.527/2011** — Lei de Acesso à Informação.
- **IEEE 830-1998** — *Recommended Practice for Software Requirements Specifications* (estrutura de referência).
- **W3C WCAG 2.1** — *Web Content Accessibility Guidelines*, nível AA.
- **PEP 8** — *Style Guide for Python Code*.
- Documentação oficial do Django, do django-allauth, do Google Identity (OAuth 2.0), do Supabase e do Railway.

---

## 12. Histórico de Revisões

| Versão | Data | Descrição | Responsável |
|---|---|---|---|
| 1.0 | 13/08/2026 | Versão inicial do documento de requisitos | Equipe GradeAção |
| 1.1 | 13/08/2026 | Autenticação alterada para login exclusivo com conta Google (OAuth 2.0 via django-allauth), em substituição a e-mail/senha (Supabase Auth): RF01–RF03, RNF15, stack, diagrama, riscos e referências | Equipe GradeAção |

---

*Documento elaborado para o projeto acadêmico GradeAção. Iniciativa discente independente, sem vínculo institucional com a Universidade de Brasília.*
