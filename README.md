<p align="center">
  <a href="https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" border="0" width="40%" height="40%"></a>
</p>

<br>

# Educa Social

## 👨‍🎓 Integrantes

- <a href="LINK_LINKEDIN">Francismar</a> — backend e API
- <a href="LINK_LINKEDIN">Antonio</a> — banco de dados e curadoria das fontes
- <a href="LINK_LINKEDIN">Beatriz</a> — interface do aplicativo mobile
- <a href="LINK_LINKEDIN">Matheus</a> — integração, testes e documentação
- <a href="https://www.linkedin.com/in/LINK_LINKEDIN">Vitor Eiji</a> — inteligência artificial (RAG, embeddings e avaliação)

> Completar com o nome completo de cada integrante e o link do LinkedIn.

## 👩‍🏫 Professores

### Tutor(a)

- <a href="LINK_LINKEDIN">Nome do tutor(a)</a>

### Coordenador(a)

- <a href="LINK_LINKEDIN">Nome do coordenador(a)</a>

## 📜 Descrição

O **Educa Social** é um aplicativo Android que ajuda famílias de baixa renda a descobrir benefícios sociais, serviços públicos e oportunidades educacionais a que têm direito, em linguagem simples e com fonte oficial indicada. Ele foi desenvolvido para a Global Solution FIAP 2026.2 e se alinha aos ODS 1 (Erradicação da Pobreza), 4 (Educação de Qualidade) e 10 (Redução das Desigualdades).

**O problema.** Muitas pessoas deixam de receber benefícios por não saberem que existem, não entenderem os critérios ou não saberem onde se inscrever. As informações estão espalhadas em sites de diferentes órgãos, em linguagem técnica, e mudam com frequência.

**A solução.** O app reúne em um só lugar programas federais, estaduais e municipais, com a descrição, quem pode participar, documentos necessários, passo a passo para solicitar e o link da fonte oficial. A região piloto é o estado de São Paulo, com foco na capital. Além de navegar por categorias e estados, a pessoa pode fazer perguntas em linguagem natural a um assistente de IA, como "Quem pode se cadastrar no CadÚnico em São Paulo?".

**O assistente de IA.** Ele usa RAG (*Retrieval-Augmented Generation*): a pergunta é convertida em um vetor de embedding, os trechos mais próximos da base curada são recuperados e só então um modelo de linguagem escreve a resposta, citando as fontes numeradas. Se a base não tem evidência suficiente, o assistente recusa em vez de inventar. Os resultados são filtrados por região: programas nacionais sempre entram, estaduais só do estado informado e municipais só da cidade informada.

**Principais decisões técnicas.**

- Monolito modular: o módulo de IA vive em `backend/app/ai` e é chamado dentro do mesmo processo da API, por uma interface definida em contrato, o que dispensa um serviço separado e simplifica a implantação.
- Provedores configuráveis por variável de ambiente: Ollama (local, para desenvolvimento) ou Google AI Studio / Gemini (produção). A chave do LLM fica apenas no backend.
- Busca vetorial em Python (NumPy, similaridade do cosseno) sobre um índice em memória com cache. Os vetores ficam na própria tabela `document` do MySQL, sem banco vetorial dedicado.
- Corte mínimo de similaridade (`RETRIEVAL_MIN_SCORE`, 0,60): abaixo dele o modelo de linguagem nem é chamado.
- Aviso de confiabilidade: programas ainda não confirmados pela curadoria geram uma recomendação de conferir a informação na fonte oficial.

**Dados.** A base atual tem 13 programas reais de São Paulo e do governo federal, cada um com fonte oficial e data de consulta: CadÚnico, Bolsa Família, BPC, Gás do Povo, Tarifa Social de Energia Elétrica, Bolsa do Povo, Programa Operação Trabalho (POT), Bilhete Único de Estudante, Bilhete Único da Pessoa Idosa, Atende+, CRAS, rede socioassistencial (CRAS, CREAS e Centros POP) e canais de atendimento e Ouvidoria da assistência social.

**Avaliação do RAG.** Foi criado um conjunto de 29 perguntas com resposta esperada (responder, recusar ou aceitar ambos). No modo de recuperação, as fontes certas foram encontradas em todas as perguntas respondíveis depois da limpeza da base. No modo de geração com Gemini, o resultado foi de 29 perguntas, 0 falhas e 0 erros: perguntas fora do escopo (como "Qual o preço do dólar hoje?" e "Como tirar a carteira de motorista?") foram recusadas e as demais citaram a fonte esperada.

**Limitações.** O conteúdo cobre apenas a região piloto e 13 programas; valores e regras de benefícios mudam, por isso a informação deve sempre ser confirmada na fonte oficial; a cota gratuita do Gemini limita o volume de perguntas.

## 📱 Frontend (React Native)

> [!NOTE]
> O aplicativo está localizado em `frontend/EducaSocialApp` e foi desenvolvido com **Expo**, **React Native** e **TypeScript**.

### Tecnologias
- **Expo** – gerencia o ciclo de vida e permite execução rápida no dispositivo ou simulador.
- **React Native** – UI nativa para Android (e iOS, se necessário).
- **TypeScript** – tipagem estática, melhora manutenção.
- **React Navigation / Expo Router** – navegação baseada em arquivos (`src/app`).
- **Axios** – chamadas HTTP para a API backend.
- **Zustand / React Context** – gerenciamento simples de estado global (usuário, configurações).
- **Tailwind‑css (nativewind)** – estilos responsivos.


## 📁 Estrutura de pastas

```text
EducaSocial-Mobile/
├─ .github/                # GitHub Actions, workflows, etc.
├─ assets/                 # Logos, imagens estáticas
├─ backend/
│   ├─ app/
│   │   ├─ api/            # Rotas FastAPI (programs, assistant)
│   │   ├─ ai/             # Módulo RAG (provedores, ingestion, services, tools)
│   │   ├─ core/           # Configurações, exceções, utilitários
│   │   ├─ integrations/   # Cliente que conecta a API ao módulo AI
│   │   ├─ models/         # ORM SQLAlchemy (region, opportunity, etc.)
│   │   ├─ repositories/   # Acesso a dados (MySQL, local)
│   │   ├─ schemas/        # Pydantic schemas (API contracts)
│   │   ├─ services/       # Lógica de negócio (program service, assistant)
│   │   └─ main.py
│   ├─ data/               # Dados de avaliação e lotes de programas
│   ├─ docs/               # Documentação técnica (ai‑module.md, contracts)
│   ├─ tests/              # Testes automatizados (pytest)
│   └─ requirements*.txt
├─ database/               # Scripts e arquivos relacionados ao banco
├─ docs/                   # Documentação geral do projeto
├─ frontend/
│   └─ EducaSocialApp/
│       ├─ src/
│       │   ├─ app/                # Telas/rotas (Expo Router)
│       │   ├─ components/         # UI reutilizável
│       │   ├─ hooks/              # Hooks custom
│       │   ├─ services/           # Camada de API (axios)
│       │   ├─ styles/             # Tailwind/nativewind
│       │   └─ types/              # Tipos TypeScript
│       ├─ .env.example
│       └─ App.tsx
└─ README.md               # Este documento
```

- <b>.github</b>: configurações do GitHub para automação de processos do repositório.
- <b>assets</b>: imagens e demais arquivos não estruturados, como o logo da FIAP.
- <b>backend</b>: API em FastAPI e o módulo de IA.
  - <b>backend/app/api</b>: rotas (`programs`, `assistant`), dependências e tratamento de erros.
  - <b>backend/app/ai</b>: módulo de IA (RAG): provedores (Ollama e Gemini), chunking, índice vetorial, serviço de perguntas e respostas, pipeline de ingestão e ferramentas de avaliação.
  - <b>backend/app/core</b>: configurações, exceções e utilitários de texto.
  - <b>backend/app/integrations</b>: cliente que liga a API ao módulo de IA.
  - <b>backend/app/models</b>, <b>schemas</b>, <b>repositories</b>, <b>services</b>: modelos, contratos da API, acesso a dados (MySQL) e regras de negócio.
  - <b>backend/docs</b>: documentação técnica do módulo de IA (`ai-module.md`) e do contrato de integração (`ai-integration-contract.md`).
  - <b>backend/tests</b>: testes automatizados (pytest).
- <b>database</b>: arquivos relacionados ao banco de dados.
- <b>docs</b>: documentos do projeto.
- <b>frontend/EducaSocialApp</b>: aplicativo React Native (Expo) com TypeScript.
  - <b>src/app</b>: telas e rotas (Expo Router): início, categorias, estados e chat.
  - <b>src/components</b>, <b>hooks</b>, <b>services</b>, <b>types</b>, <b>styles</b>: componentes, hooks, chamadas à API, tipos e tema.
- <b>infra</b>: arquivos de infraestrutura e implantação.
- <b>README.md</b>: este documento.

## 🔧 Como executar o código

### Pré-requisitos

- Python 3.11 ou superior
- Node.js 20 ou superior e npm
- Banco MySQL (Amazon RDS) com as tabelas `region`, `category`, `opportunity`, `source` e `document` (esta com a coluna JSON `embedding`)
- Chave do Google AI Studio (Gemini) ou Ollama instalado localmente, com os modelos `bge-m3` e um modelo de chat
- Aplicativo Expo Go no celular Android ou um emulador Android

### 1. Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
copy .env.example .env
```

No Linux ou macOS, ative o ambiente com `source .venv/bin/activate` e use `cp` no lugar de `copy`.

Edite o `.env` com os dados do banco e do provedor de IA. Configuração de produção:

```
AI_ENABLED=true
LLM_PROVIDER=gemini
EMBEDDING_PROVIDER=gemini
GEMINI_API_KEY=<sua chave>
GEMINI_LLM_MODEL=gemini-3.5-flash-lite
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
GEMINI_EMBEDDING_DIMENSIONS=768
DB_HOST=<host do RDS>
DB_PORT=3306
DB_NAME=<banco>
DB_USER=<usuário>
DB_PASSWORD=<senha>
```

Para desenvolvimento local sem Gemini, use `LLM_PROVIDER=ollama` e `EMBEDDING_PROVIDER=ollama` (com `ollama pull bge-m3` e o modelo de chat definido em `OLLAMA_LLM_MODEL`).

Suba o servidor:

```powershell
uvicorn app.main:app --reload
```

- Documentação interativa (Swagger): http://localhost:8000/docs
- `GET /api/v1/programs` lista programas, com filtros por categoria, estado, município e busca por texto.
- `GET /api/v1/programs/{id}` retorna um programa.
- `POST /api/v1/assistant/query` responde perguntas com o assistente de IA.

Exemplo de pergunta ao assistente:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/v1/assistant/query -H "Content-Type: application/json" -d '{\"question\": \"Quem pode se cadastrar no CadÚnico?\", \"state\": \"SP\", \"municipality\": \"São Paulo\"}'
```

> Alterações no `.env` exigem reiniciar o servidor.

### 2. Preparar a base de conhecimento da IA

Depois que os programas estiverem no banco, gere os trechos (chunks) e os embeddings. Os comandos simulam a execução por padrão; `--apply` grava no banco.

```powershell
python -m app.ai.ingestion.pipeline build-documents --apply
python -m app.ai.ingestion.pipeline embed --apply
```

Ferramentas de diagnóstico e avaliação:

```powershell
python -m app.ai.tools.scores "Quem pode se cadastrar no CadÚnico?" --state SP --municipality "São Paulo"
python -m app.ai.tools.evaluate
python -m app.ai.tools.evaluate --generate --delay 8
```

O primeiro mostra a pontuação de similaridade de cada trecho; o segundo avalia só a recuperação (sem custo de LLM); o terceiro avalia também as respostas geradas, com pausa entre as perguntas para respeitar a cota do provedor.

### 3. Testes do backend

```powershell
python -m pytest -q
```

### 4. Aplicativo mobile

```powershell
cd frontend/EducaSocialApp
npm install
copy .env.example .env
```

Em `.env`, defina `EXPO_PUBLIC_API_URL` com o endereço do backend acessível pelo celular, por exemplo `http://192.168.1.10:8000` (o IP da máquina na rede local; `localhost` não funciona no celular). Depois:

```powershell
npx expo start
```

Abra o app com o Expo Go (QR code) ou no emulador Android. Se alterar o `.env`, reinicie o Expo.

## 🗃 Histórico de lançamentos

- 1.0.0 - 19/11/2026
  - Entrega final da Global Solution FIAP 2026.2: aplicativo mobile, API com programas reais de São Paulo e assistente de IA com RAG e citação de fontes.

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/templateFiapVfinal">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>