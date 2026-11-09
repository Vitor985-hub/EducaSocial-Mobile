# Contrato de integração com o módulo de IA

Status: proposta para validação com quem implementar o módulo de IA. O backend define a interface e não contém lógica de IA.

## Responsabilidades

| Componente | Responsabilidade |
|---|---|
| Aplicativo | Enviar a pergunta do usuário ao backend. Nunca fala com o módulo de IA diretamente. |
| Backend | Validar a entrada, normalizar filtros geográficos, encaminhar ao módulo de IA, traduzir falhas em erros padronizados. |
| Módulo de IA | Indexação, embeddings, recuperação, contexto, LLM e geração da resposta com fontes. |

Chaves de LLM e de provedores ficam somente no módulo de IA. Nenhuma delas vai para o aplicativo.

## 1. Aplicativo para backend

`POST /api/v1/assistant/query`

Requisição:

```json
{
  "question": "Como solicito um auxílio de aluguel?",
  "state": "SP",
  "municipality": "Santo André"
}
```

| Campo | Tipo | Regras |
|---|---|---|
| `question` | string | Obrigatório, de 3 a 1000 caracteres, espaços nas pontas removidos. |
| `state` | string | Opcional, sigla de UF válida, normalizada para maiúsculas. |
| `municipality` | string | Opcional, de 2 a 100 caracteres. Exige `state`. |

Resposta `200`:

```json
{
  "answer": "Texto da resposta em linguagem natural.",
  "sources": [
    { "title": "Nome da fonte", "program_id": 11, "url": null }
  ]
}
```

| Campo | Tipo | Regras |
|---|---|---|
| `answer` | string | Resposta gerada pelo módulo de IA. |
| `sources` | lista | Pode ser vazia. Cada item tem `title` obrigatório, `program_id` e `url` opcionais. |

Erros, sempre no formato `{"error": {"code": "...", "message": "..."}}`:

| Status | `code` | Quando |
|---|---|---|
| 422 | `validation_error` | Corpo fora das regras acima. |
| 422 | `invalid_filter` | UF desconhecida ou município sem estado. |
| 503 | `ai_unavailable` | Módulo de IA desligado, fora do ar ou com timeout. |

Enquanto o módulo de IA não estiver conectado, o endpoint responde `503 ai_unavailable`.

## 2. Backend para módulo de IA

Proposta: HTTP com JSON, versionado.

`POST {AI_SERVICE_URL}/v1/query`

Requisição: o mesmo corpo da seção 1, já validado e normalizado.

Resposta `200`: o mesmo corpo da resposta da seção 1.

Autenticação: cabeçalho `X-API-Key` com o valor de `AI_SERVICE_API_KEY`.

Timeout: `AI_SERVICE_TIMEOUT_SECONDS`, sugestão inicial de 30 segundos.

Tratamento de falhas pelo backend:

| Situação no módulo de IA | Resultado no backend |
|---|---|
| Timeout, conexão recusada, 5xx | `503 ai_unavailable` |
| 4xx | `503 ai_unavailable`, com o detalhe registrado em log e sem repassar ao aplicativo |
| Corpo fora do contrato | `503 ai_unavailable` |

## 3. Onde isso vive no código

| Arquivo | Papel |
|---|---|
| `app/schemas/ai.py` | `AIQueryRequest`, `AIQueryResponse`, `AISource`. É o contrato. |
| `app/integrations/ai_client.py` | Interface `AIServiceClient` e `DisabledAIClient`, usado enquanto o módulo não existe. |
| `app/services/assistant_service.py` | Normaliza a localização e delega ao cliente. |
| `app/api/routes/assistant.py` | Endpoint exposto ao aplicativo. |
| `app/api/dependencies.py` | `get_ai_client`, único ponto a trocar para ligar o cliente real. |

## 4. Para conectar o módulo real

1. Adicionar `httpx` em `requirements.txt`.
2. Criar `HttpAIClient` em `app/integrations/` implementando `AIServiceClient`, traduzindo qualquer falha em `AIServiceUnavailableError`.
3. Adicionar `ai_service_url`, `ai_service_api_key` e `ai_service_timeout_seconds` em `Settings` e no `.env.example`.
4. Fazer `get_ai_client` devolver o `HttpAIClient` quando `ai_service_url` estiver configurada, e o `DisabledAIClient` caso contrário.

Rotas, serviços e testes existentes não mudam.
