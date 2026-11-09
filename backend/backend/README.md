# Educa Social — Backend

API REST em FastAPI para consulta de programas sociais, com filtros por estado e município. O módulo de IA (RAG) é um serviço separado, consumido por uma interface definida em `docs/ai-integration-contract.md`.

## Aviso sobre dados

Todos os programas retornados hoje são **fictícios**, mantidos em memória em `app/repositories/fake_programs.py`. Cada nome começa com `[FICTÍCIO]`. Nenhum dado representa um programa oficial.

## Requisitos

Python 3.11 ou superior.

## Configuração

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

No Windows (PowerShell), ative o ambiente com `.venv\Scripts\Activate.ps1`.

## Execução

```bash
uvicorn app.main:app --reload
```

- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

## Testes e qualidade

```bash
pytest
ruff check .
ruff format --check .
```

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/health` | Estado da API e versão. |
| GET | `/api/v1/programs` | Lista paginada com filtros. |
| GET | `/api/v1/programs/{id}` | Detalhes de um programa. |
| POST | `/api/v1/assistant/query` | Pergunta em linguagem natural. Responde 503 até o módulo de IA ser conectado. |

Parâmetros de `GET /api/v1/programs`:

| Parâmetro | Descrição |
|---|---|
| `q` | Busca por texto no nome, resumo e descrição, sem distinção de acentos ou maiúsculas. Todas as palavras precisam aparecer. |
| `category` | `renda`, `educacao`, `saude`, `moradia`, `alimentacao` ou `trabalho`. |
| `state` | Sigla da UF. |
| `municipality` | Município. Exige `state`, porque nomes de município se repetem entre estados. |
| `page`, `page_size` | Página (a partir de 1) e tamanho (1 a 100, padrão 20). |

Regra do filtro geográfico: programas nacionais aparecem em qualquer localidade. Com `state`, entram também os programas estaduais desse estado e os municipais de qualquer município dele. Com `state` e `municipality`, os municipais ficam restritos àquele município.

Erros seguem sempre o formato `{"error": {"code": "...", "message": "..."}}`, com `details` nos erros de validação.

## Arquitetura

```
rota → serviço → repositório → dados
```

| Camada | Pasta | Responsabilidade |
|---|---|---|
| Rotas | `app/api/routes` | Receber e devolver HTTP. Sem regra de negócio e sem acesso a dados. |
| Serviços | `app/services` | Regras de negócio e validações. |
| Repositórios | `app/repositories` | Acesso a dados. Hoje em memória. |
| Modelos | `app/models` | Entidades de domínio. |
| Schemas | `app/schemas` | Contratos de entrada e saída da API. |
| Integrações | `app/integrations` | Clientes de serviços externos, como o módulo de IA. |
| Core | `app/core` | Configuração, exceções e utilitários. |

`ProgramRepository` é um `Protocol`. Trocar o repositório em memória pelo PostgreSQL significa escrever uma nova implementação e apontar `get_program_repository` para ela, sem alterar serviços, rotas ou contratos.

## Pendente

Etapa 7: PostgreSQL, SQLAlchemy e Alembic, quando o banco estiver pronto.
