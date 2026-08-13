# GradeAção

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django 5.0+](https://img.shields.io/badge/Django-5.0+-darkgreen.svg)](https://www.djangoproject.com/)

Planejador de grade horária para discentes da Universidade de Brasília.
Projeto acadêmico independente.

**[Documentação](https://welder60.github.io/GradeAcao/)** · **[Aplicação](https://gradeacao.com.br)** (em desenvolvimento)

## ⚠️ Aviso de desvinculação institucional

O GradeAção não possui qualquer vínculo, patrocínio, convênio ou endosso da Universidade de Brasília (UnB). A ferramenta não se integra a sistemas institucionais, não efetua matrícula e não substitui os canais oficiais da Universidade. O resultado do planejamento tem caráter auxiliar e não vinculante.

## ✨ Funcionalidades

- Montagem interativa de grades horárias a partir de dados públicos da UnB
- Comparação de múltiplos cenários antes do período de matrícula
- Validação acadêmica contra matrizes curriculares
- Autenticação segura com Supabase
- Interface responsiva e intuitiva

## 🛠️ Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Django 5.0+ |
| Banco de dados | PostgreSQL (Supabase) |
| Autenticação | Supabase Auth |
| Armazenamento | Supabase Storage |
| Hospedagem / CI-CD | Railway |
| Front-end | Templates Django + CSS + JavaScript |
| Documentação | MkDocs + Material |

## 🚀 Início rápido

### Pré-requisitos
- Python 3.11+
- pip ou pipenv
- PostgreSQL (ou usar Supabase)

### Instalação local

```bash
# Clonar repositório
git clone https://github.com/welder60/GradeAcao.git
cd GradeAcao

# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# Instalar dependências
pip install -r requirements-dev.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Preencha DJANGO_SECRET_KEY e DATABASE_URL no .env

# Preparar banco de dados
python manage.py migrate

# Executar servidor
python manage.py runserver
```

A aplicação estará disponível em `http://localhost:8000`.

## 📁 Estrutura do projeto

```
GradeAcao/
├── apps/
│   ├── comum/          # Páginas institucionais e utilitários
│   ├── contas/         # Perfil acadêmico e progresso
│   ├── catalogo/       # Componentes, turmas e matrizes curriculares
│   └── planejamento/   # Grades, cenários e validação acadêmica
├── config/
│   └── settings/       # Base, dev, prod
├── docs/               # Documentação MkDocs
├── static/             # Arquivos estáticos (CSS, JS, imagens)
├── templates/          # Templates Django
├── manage.py           # CLI do Django
└── requirements*.txt   # Dependências Python
```

## 🧪 Desenvolvimento

### Comandos úteis

| Comando | Descrição |
|---------|-----------|
| `python manage.py runserver` | Servidor de desenvolvimento |
| `pytest` | Executar testes com cobertura |
| `pytest --cov` | Relatório de cobertura |
| `ruff check .` | Análise estática de código |
| `mkdocs serve` | Documentação local em `http://localhost:8000/docs` |
| `mkdocs build --strict` | Build de documentação com validação |

### Testes

```bash
pytest                    # Rodar todos os testes
pytest --cov            # Com relatório de cobertura
pytest apps/planejamento/ -v  # Testes de um módulo específico
```

### Formatação e linting

```bash
ruff check .            # Verificar código
ruff check . --fix      # Corrigir automaticamente
```

## 📚 Documentação

A documentação completa está em [`docs/`](docs/index.md) ou via MkDocs:

```bash
mkdocs serve
```

Inclui:
- [Documento de Requisitos](https://welder60.github.io/GradeAcao/requisitos/documento-de-requisitos/)
- [Visão Geral da Arquitetura](https://welder60.github.io/GradeAcao/arquitetura/visao-geral/)
- [Guia de Desenvolvimento](https://welder60.github.io/GradeAcao/desenvolvimento/ambiente-local/)
- [Padrões de Código](https://welder60.github.io/GradeAcao/desenvolvimento/padroes/)

## 🚢 Deployment

O projeto usa [Railway](https://railway.app) para deployment contínuo. Consulte `railway.json` para configuração.

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Abra uma [issue](https://github.com/welder60/GradeAcao/issues) descrevendo o problema ou funcionalidade
2. Faça um fork do repositório
3. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
4. Commit suas alterações (`git commit -m 'Add AmazingFeature'`)
5. Push para a branch (`git push origin feature/AmazingFeature`)
6. Abra um Pull Request

### Checklist de PR
- [ ] Testes passando (`pytest`)
- [ ] Cobertura mantida ou melhorada
- [ ] Linting ok (`ruff check .`)
- [ ] Documentação atualizada

## 📜 Licença

Este projeto é licenciado sob a [MIT License](LICENSE) - veja o arquivo LICENSE para detalhes.

## 📧 Contato

Para dúvidas ou sugestões, abra uma [issue](https://github.com/welder60/GradeAcao/issues).
