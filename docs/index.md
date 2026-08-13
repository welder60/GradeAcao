# GradeAção

Planejador de grade horária para discentes da Universidade de Brasília.

!!! warning "Aviso de desvinculação institucional"
    O GradeAção é uma iniciativa independente, concebida e desenvolvida por
    discentes. **Não possui qualquer vínculo, patrocínio, convênio ou endosso da
    Universidade de Brasília (UnB)**, de seus decanatos, institutos, faculdades
    ou de qualquer outro órgão da instituição.

    A ferramenta não realiza integração com sistemas institucionais, não efetua
    matrícula e não substitui os canais oficiais da Universidade. O resultado do
    planejamento tem caráter **auxiliar e não vinculante**.

## O que é

O GradeAção permite ao discente montar, comparar e avaliar cenários de grade
horária antes do período de matrícula, a partir de dados públicos de oferta de
componentes curriculares e da matriz curricular de seu curso.

## Por onde começar

- [Documento de Requisitos](requisitos/documento-de-requisitos.md) — especificação completa (RF, RNF, RN, casos de uso)
- [Visão Geral da Arquitetura](arquitetura/visao-geral.md) — estrutura do monolito Django
- [Ambiente Local](desenvolvimento/ambiente-local.md) — como rodar o projeto

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Django (monolito, templates server-side) |
| Banco de dados | PostgreSQL (Supabase) |
| Autenticação | Supabase Auth |
| Armazenamento | Supabase Storage |
| Hospedagem / CI-CD | Railway |
| Front-end | Templates Django + CSS + JS leve |
| Documentação | MkDocs + Material |
