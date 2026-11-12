# Educa Social — Módulo de IA

Serviço RAG separado do backend. Recebe uma pergunta, recupera os trechos mais relevantes das fontes cadastradas no banco e gera uma resposta fundamentada, acompanhada das fontes. Quando os trechos não bastam, responde que não encontrou evidências suficientes, sem inventar.

O backend conversa com este serviço por HTTP, conforme `backend/docs/ai-integration-contract.md`. Este módulo não importa nada do backend.

## Como funciona

1. A ingestão transforma cada `opportunity` em chunks na tabela `document` e gera um embedding por chunk na tabela `document_embedding`.
2. Na consulta, o embedding da pergunta é comparado com os dos chunks por similaridade de cosseno, em NumPy. Os vetores ficam em memória, com cache de `INDEX_TTL_SECONDS`.
3. O filtro regional segue a regra do backend: programas nacionais sempre, estaduais da UF e municipais do município pedido.
4. Se nenhum chunk passar de `RETRIEVAL_MIN_SCORE`, a resposta é "sem evidências" e o LLM nem é chamado.
5. Caso contrário, os trechos numerados vão como contexto ao LLM. Se ele responder `SEM_EVIDENCIA`, o resultado é o mesmo. Nas fontes retornadas entram só os trechos citados na resposta (ou todos os recuperados, se nenhum foi citado).

## Estrutura

| Pasta | Papel |
|---|---|
| `app/api` | Rotas HTTP e autenticação por chave |
| `app/core` | Configuração, exceções e utilitários |
| `app/providers` | Interfaces e implementações de LLM e embeddings (Ollama e Gemini) |
| `app/repositories` | Acesso aos chunks: MySQL (`mysql.py`) e arquivo local (`local.py`) |
| `app/services` | Busca vetorial, prompts e serviço RAG |
| `app/schemas` | Contrato de entrada e saída |
| `app/tools` | `check_schema` e `ask`, para linha de comando |
| `ingestion` | Chunking e pipeline de ingestão |

LLM e embeddings são configurados separadamente (`LLM_PROVIDER` e `EMBEDDING_PROVIDER`). Os embeddings gravados ficam identificados por modelo em `document_embedding.embedding_model`, então modelos diferentes coexistem e a consulta usa só o ativo. Para o Gemini o identificador inclui as dimensões, por exemplo `gemini-embedding-001:768`.

## Configuração

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

No Windows (PowerShell), ative com `.venv\Scripts\Activate.ps1`.

Preencha no `.env` as variáveis `DB_*` (as mesmas do backend). O ideal é um usuário do banco com permissão de leitura nas tabelas, mais escrita apenas em `document_embedding` (e em `document`, se for usar `build-documents`).

Com Ollama (padrão):

```bash
ollama pull bge-m3
ollama pull qwen2.5:7b
```

Com Gemini, defina `GEMINI_API_KEY`, `GEMINI_LLM_MODEL` e troque `LLM_PROVIDER` e/ou `EMBEDDING_PROVIDER` para `gemini`.

## Uso

Passo a passo, sempre começando pela verificação (somente leitura):

```bash
python -m app.tools.check_schema
python -m ingestion.pipeline build-documents
python -m ingestion.pipeline embed
```

Os dois comandos de ingestão **simulam** por padrão e só mostram os números. Para gravar, repita com `--apply`:

```bash
python -m ingestion.pipeline build-documents --apply
python -m ingestion.pipeline embed --apply
```

`build-documents` cria chunks em `document` apenas para oportunidades que ainda não têm nenhum. Se a responsável pelo banco já preenche `document`, pule esse passo. Nenhum comando altera o schema.

Perguntar pela linha de comando e subir o serviço:

```bash
python -m app.tools.ask "Como solicito um auxílio de aluguel?" --state SP --municipality "Santo André"
uvicorn app.main:app --port 8001 --reload
```

Para testar sem o banco, use `CHUNK_STORE=local`:

```bash
cp data/local_store.example.json data/local_store.json
python -m ingestion.pipeline embed --apply
```

## Contrato

`POST /v1/query`, com o cabeçalho `X-API-Key` quando `AI_SERVICE_API_KEY` está definida (obrigatória em produção).

```json
{"question": "Como solicito um auxílio de aluguel?", "state": "SP", "municipality": "Santo André"}
```

```json
{
  "answer": "Texto da resposta.",
  "sources": [{"title": "Nome da fonte", "program_id": 11, "url": "https://..."}]
}
```

`program_id` é o `opportunity.id`. Falhas devolvem `{"error": {"code", "message"}}` com 401 (chave), 503 (provedor ou banco indisponível) ou 500 (configuração).

## Testes

```bash
pytest
ruff check .
```

Os testes usam provedores simulados e SQLite em memória; não dependem de Ollama, Gemini nem do RDS.

## Limites conhecidos

- `RETRIEVAL_MIN_SCORE=0.45` é um ponto de partida. Calibre com as 15 a 20 perguntas de avaliação: suba se estiver respondendo o que não devia, baixe se estiver recusando o que devia responder.
- Os provedores Ollama e Gemini foram testados só com respostas simuladas, seguindo o formato das APIs. O primeiro teste de verdade deve ser com `python -m app.tools.ask`.
- A ingestão parte das oportunidades já curadas no banco. A extração automática de páginas oficiais não está implementada.
- `document.embedding_model` não é atualizada pelo módulo; o modelo de cada vetor fica em `document_embedding`.
