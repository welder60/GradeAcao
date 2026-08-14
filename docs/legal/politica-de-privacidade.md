# Política de Privacidade

**Versão:** 1.0
**Vigente desde:** 14 de agosto de 2026
**Última atualização:** 14 de agosto de 2026

Esta Política descreve como o **GradeAção** trata dados pessoais, em observância à
**Lei nº 13.709/2018 — Lei Geral de Proteção de Dados Pessoais (LGPD)**.

!!! warning "Aviso de desvinculação institucional"
    O GradeAção é uma iniciativa independente, concebida e desenvolvida por
    discentes. **Não possui qualquer vínculo, patrocínio, convênio ou endosso da
    Universidade de Brasília (UnB)**, de seus decanatos, institutos, faculdades
    ou de qualquer outro órgão da instituição.

    A ferramenta **não se integra a sistemas institucionais** (SIGAA, Matrícula
    Web, portais de autenticação ou quaisquer APIs internas), **não efetua
    matrícula** e **não consulta dados pessoais de discentes em bases oficiais**.
    Os dados pessoais tratados são exclusivamente aqueles fornecidos pelo próprio
    usuário ou obtidos de seu provedor de autenticação, conforme descrito abaixo.

---

## 1. Quem é o controlador

O controlador dos dados pessoais é a **Equipe GradeAção**, grupo de discentes
responsável pelo desenvolvimento e pela operação da aplicação, no âmbito de
projeto acadêmico independente.

| Item | Informação |
|---|---|
| Controlador | Equipe GradeAção (projeto acadêmico independente) |
| Canal de contato | [Issues do repositório](https://github.com/welder60/GradeAcao/issues) |
| Encarregado (DPO) | Função exercida pelo responsável técnico do projeto, acessível pelo canal acima |

!!! note "Canal de contato"
    Enquanto o projeto não dispuser de endereço de e-mail institucional próprio,
    as solicitações relativas a dados pessoais devem ser encaminhadas pelo canal
    indicado acima. Ao definir um e-mail de contato dedicado, esta seção será
    atualizada e a alteração registrada no histórico de revisões.

---

## 2. Princípio geral: coletamos o mínimo

O GradeAção adota o **princípio da necessidade** (art. 6º, III, da LGPD): são
tratados apenas os dados indispensáveis ao planejamento de grade horária.

Em particular, o GradeAção **não** trata:

- senhas — a autenticação é integralmente delegada ao Google;
- credenciais de sistemas institucionais, em nenhuma hipótese;
- histórico escolar oficial, índices de rendimento acadêmico ou situação de
  matrícula obtidos de bases da Universidade;
- dados pessoais sensíveis, na acepção do art. 5º, II, da LGPD (origem racial ou
  étnica, convicção religiosa, opinião política, filiação sindical, dado
  referente à saúde ou à vida sexual, dado genético ou biométrico);
- dados de crianças ou adolescentes de forma dirigida — o serviço destina-se a
  discentes do ensino superior.

---

## 3. Dados tratados, finalidade e base legal

### 3.1 Dados de conta e autenticação

O acesso autenticado ocorre exclusivamente por **login com conta Google (OAuth
2.0)**. O GradeAção recebe do Google, mediante seu consentimento na tela de
autorização, apenas:

| Dado | Finalidade | Base legal (LGPD) |
|---|---|---|
| Identificador da conta Google | Identificar univocamente o usuário e vincular a ele seu perfil e suas grades | Execução de contrato / procedimentos preliminares (art. 7º, V) |
| Nome | Personalizar a interface e identificar a sessão ativa | Execução de contrato (art. 7º, V) |
| Endereço de e-mail | Identificar a conta, permitir recuperação de acesso e comunicações operacionais essenciais | Execução de contrato (art. 7º, V) |

O GradeAção **não recebe sua senha do Google**, não acessa seus contatos, sua
agenda, seus arquivos ou qualquer outro dado da sua conta Google.

### 3.2 Perfil acadêmico

| Dado | Finalidade | Base legal (LGPD) |
|---|---|---|
| Curso, campus, matriz curricular e período de ingresso | Filtrar a oferta pública, exibir a matriz curricular aplicável e calcular progresso | Execução de contrato (art. 7º, V) |
| Componentes marcados como *cursados*, *em curso* ou *pendentes* | Validar pré-requisitos, co-requisitos e equivalências; calcular créditos e projeção de conclusão | Execução de contrato (art. 7º, V) |
| Equivalências aproveitadas e componentes fora da matriz | Refletir corretamente o progresso na integralização do curso | Execução de contrato (art. 7º, V) |
| Restrições de disponibilidade (dias e faixas de horário) | Ocultar turmas incompatíveis com a sua disponibilidade | Execução de contrato (art. 7º, V) |

!!! info "O perfil acadêmico é declaratório"
    Todos os dados acima são **informados por você** e **não são verificados
    contra qualquer fonte oficial** da Universidade. O GradeAção não tem acesso
    ao seu histórico escolar. As validações produzidas pela ferramenta têm
    caráter **auxiliar e não vinculante**.

### 3.3 Grades e cenários

| Dado | Finalidade | Base legal (LGPD) |
|---|---|---|
| Turmas selecionadas, nomes de grades e cenários salvos | Persistir, comparar, visualizar e exportar seus cenários de grade | Execução de contrato (art. 7º, V) |
| Grade associada a link público, quando você o gerar | Permitir o compartilhamento somente-leitura solicitado por você | Consentimento (art. 7º, I) |

### 3.4 Dados técnicos e de operação

| Dado | Finalidade | Base legal (LGPD) |
|---|---|---|
| Cookies estritamente necessários (sessão e proteção contra CSRF) | Manter você autenticado e proteger formulários contra falsificação de requisição | Legítimo interesse (art. 7º, IX) e execução de contrato (art. 7º, V) |
| Registros de acesso e de erro da aplicação (data, hora, rota, código de resposta e, quando aplicável, endereço IP) | Segurança, diagnóstico de falhas e cumprimento do art. 15 do Marco Civil da Internet | Cumprimento de obrigação legal (art. 7º, II) e legítimo interesse (art. 7º, IX) |
| Registros de carga de dados (identificação do curador, data e volume de registros) | Auditoria e rastreabilidade da curadoria do catálogo | Legítimo interesse (art. 7º, IX) |

O GradeAção **não utiliza cookies de publicidade, de rastreamento entre sites ou
de perfilamento comportamental**, e não emprega ferramentas de análise de
audiência de terceiros.

### 3.5 Uso sem cadastro

É possível consultar o catálogo e montar uma grade **sem criar conta**, em sessão
temporária. Nesse modo, nenhum dado de perfil é persistido: o conteúdo da sessão
é descartado ao seu término e as grades **não são salvas**.

---

## 4. Dados que não são pessoais

O catálogo de componentes curriculares, as turmas ofertadas, os horários, os
departamentos e as matrizes curriculares provêm de **dados públicos** de oferta,
carregados e curados pela equipe. Esses dados não são obtidos a partir do seu
perfil e não constituem dados pessoais seus.

O nome de docente responsável por turma, quando exibido, é reproduzido de
divulgação pública de oferta, com finalidade exclusivamente informativa e de
filtragem do catálogo.

Toda tela de catálogo indica o **período letivo de referência** e a **data da
última atualização** dos dados. Informações de vagas, quando exibidas, referem-se
à data da coleta e **nunca** à disponibilidade em tempo real.

---

## 5. Compartilhamento com terceiros

O GradeAção **não vende, não aluga e não cede** dados pessoais. O compartilhamento
ocorre apenas com os operadores necessários à prestação do serviço:

| Terceiro | Papel | Dados envolvidos |
|---|---|---|
| **Google** (Google Identity / OAuth 2.0) | Provedor de autenticação | Identificador da conta, nome e e-mail, transmitidos a nós mediante sua autorização |
| **Supabase** | Banco de dados PostgreSQL gerenciado e armazenamento de arquivos | Perfil acadêmico, grades, cenários e arquivos de exportação |
| **Railway** | Hospedagem da aplicação e implantação contínua | Dados em trânsito e registros de execução |

Esses provedores atuam como **operadores**, tratando dados por conta e ordem do
controlador e conforme seus próprios termos e políticas de privacidade.

Dados pessoais poderão ainda ser fornecidos a autoridades públicas mediante
**ordem judicial ou requisição legal**, nos estritos limites da determinação.

### 5.1 Transferência internacional

A infraestrutura utilizada (Google, Supabase e Railway) pode processar e
armazenar dados em servidores localizados **fora do Brasil**. Nesses casos, a
transferência internacional apoia-se no art. 33 da LGPD, em especial na
necessidade de execução do contrato firmado com o titular.

### 5.2 Compartilhamento por sua iniciativa

Ao gerar um **link público somente-leitura** de uma grade, você torna aquele
conteúdo acessível a qualquer pessoa que detenha o endereço. O link é
**revogável por você a qualquer momento**, e sua revogação torna a grade
inacessível por aquele endereço.

---

## 6. Retenção e eliminação

| Categoria | Prazo de retenção |
|---|---|
| Dados de conta e perfil acadêmico | Enquanto a conta existir |
| Grades, cenários e links públicos | Enquanto a conta existir ou até que você os exclua |
| Sessão de uso sem cadastro | Até o encerramento da sessão |
| Registros de acesso da aplicação | 6 (seis) meses, conforme o art. 15 do Marco Civil da Internet |
| Cópias de segurança (backups) | Até 7 dias, quando então são sobrescritas pelo ciclo de retenção |

**A exclusão da conta implica a remoção definitiva do perfil, das grades e dos
links públicos associados.** Os dados eliminados permanecem em cópias de
segurança apenas pelo prazo de retenção acima, ao fim do qual são efetivamente
descartados.

---

## 7. Seus direitos como titular

Nos termos do art. 18 da LGPD, você pode, a qualquer tempo:

| Direito | Como exercer |
|---|---|
| **Confirmação e acesso** | Consultar seu perfil e suas grades diretamente na aplicação |
| **Correção** de dados incompletos, inexatos ou desatualizados | Editar o perfil acadêmico e o progresso na própria aplicação |
| **Portabilidade** | Exportar todos os seus dados pessoais em formato legível por máquina, pela aplicação |
| **Eliminação** | Excluir a conta pela aplicação, o que remove perfil, grades e links públicos |
| **Revogação de consentimento** | Revogar o link público de compartilhamento a qualquer momento |
| **Informação sobre compartilhamento** | Consultar a seção 5 desta Política ou solicitar detalhamento pelo canal de contato |
| **Oposição** a tratamento fundado em legítimo interesse | Solicitar pelo canal de contato |
| **Petição perante a ANPD** | Diretamente à Autoridade Nacional de Proteção de Dados |

Solicitações encaminhadas pelo canal de contato são respondidas em **até 15
(quinze) dias**. Por se tratar de projeto acadêmico mantido por discentes, pedidos
recebidos em período de recesso ou de avaliações podem levar mais tempo — nesses
casos, informaremos o prazo previsto.

---

## 8. Segurança

Medidas técnicas e administrativas adotadas:

- toda comunicação entre navegador e servidor ocorre sobre **HTTPS**;
- **nenhuma senha é armazenada** — a autenticação é delegada ao Google;
- segredos da aplicação são mantidos em **variáveis de ambiente**, jamais
  versionados no repositório;
- controle de acesso impede que um usuário acesse perfil ou grades de outro,
  ressalvado o link público que o próprio titular tenha gerado;
- alterações no catálogo são restritas aos papéis de **curador** e
  **administrador**, com registro em log;
- o banco de dados possui rotina de **backup automatizado**.

Nenhum sistema é integralmente imune a incidentes. Na hipótese de incidente de
segurança com risco relevante aos titulares, comunicaremos os afetados e a
**ANPD**, conforme o art. 48 da LGPD.

---

## 9. Decisões automatizadas

O GradeAção executa validações automáticas — detecção de choques de horário,
verificação de pré-requisitos, co-requisitos e equivalências e, quando
disponível, sugestão de grade. Esses processamentos produzem **alertas e
sugestões não vinculantes**, destinados a apoiar sua decisão.

Nenhuma decisão automatizada do GradeAção afeta seus interesses acadêmicos de
forma vinculante: a ferramenta **não efetua matrícula** e **não substitui** os
sistemas oficiais nem a orientação da coordenação de curso. Você pode solicitar
esclarecimentos sobre os critérios dessas validações pelo canal de contato; a
lógica das regras está descrita no
[Documento de Requisitos](../requisitos/documento-de-requisitos.md).

---

## 10. Alterações desta Política

Esta Política pode ser revista para refletir mudanças na aplicação ou na
legislação. Alterações relevantes serão anunciadas na aplicação e registradas no
histórico abaixo. A versão vigente é sempre a publicada nesta página.

---

## 11. Histórico de revisões

| Versão | Data | Descrição |
|---|---|---|
| 1.0 | 14/08/2026 | Versão inicial da Política de Privacidade |

---

*Documento do projeto acadêmico GradeAção. Iniciativa discente independente, sem
vínculo institucional com a Universidade de Brasília.*
