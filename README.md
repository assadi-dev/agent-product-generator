# Product Sheet Generator

An AI agent that generates complete, publication-ready product sheets for marketing and e-commerce teams.

Built as a portfolio project to demonstrate real-world LangGraph agent development.

---

## What it does

Given a product name, category, and target audience, the agent:

1. Optionally scrapes the product URL for context
2. Generates a full product description
3. Extracts key selling features
4. Produces SEO keywords, meta title, and meta description
5. Rewrites the copy in the requested tone (professional / casual / luxury / technical)
6. Optionally translates everything to French
7. Assembles and validates the final product sheet

Output includes: title, tagline, short & full description, key features, technical specs, SEO assets, and target audience — exportable as **PDF** or **JSON**.

---

## Tech stack

| Layer | Technology |
|---|---|
| Agent | LangGraph (ReAct loop) + LangChain |
| LLM | Anthropic Claude / OpenAI / OpenRouter / Amazon Bedrock / Ollama |
| Backend | FastAPI + SSE streaming |
| Frontend | Streamlit |
| Export | ReportLab (PDF) |
| Validation | Pydantic v2 |

---

## Project structure

```
agent-product-generator/
├── backend/
│   ├── agent/
│   │   ├── graph.py        # LangGraph state graph
│   │   ├── state.py        # AgentState definition
│   │   ├── nodes.py        # Graph node functions
│   │   ├── edges.py        # Conditional routing logic
│   │   └── tools/          # 7 specialised agent tools
│   ├── api/routes/         # FastAPI endpoints
│   ├── models/             # Pydantic data models
│   └── services/           # LLM factory, PDF export
├── frontend/
│   ├── app.py              # Streamlit entry point
│   ├── pages/              # Generate, History, About
│   └── components/         # Reusable UI components
├── tests/                  # Unit + integration tests
├── .env.example
└── pyproject.toml
```

---

## Quickstart

### 1. Prérequis — installer uv

```bash
# Windows
winget install astral-sh.uv

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone et installation des dépendances

```bash
git clone <your-repo-url>
cd agent-product-generator
uv sync
```

`uv sync` crée automatiquement le venv et installe toutes les dépendances depuis `pyproject.toml`.

### 3. Configurer l'environnement

```bash
cp .env.example .env
```

Éditer `.env` et renseigner au minimum :

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

### 4. Lancer le backend

```bash
uv run uvicorn backend.main:app --reload
```

API disponible sur `http://localhost:8000`
Docs interactives sur `http://localhost:8000/docs`

### 5. Lancer le frontend (autre terminal)

```bash
uv run streamlit run frontend/app.py
```

UI disponible sur `http://localhost:8501`

---

## LLM providers

Set `LLM_PROVIDER` in `.env` to switch providers. Use `LLM_MODEL` to override the default model.

| Provider | `LLM_PROVIDER` | Required env var | Default model |
|---|---|---|---|
| Anthropic | `anthropic` | `ANTHROPIC_API_KEY` | `claude-sonnet-4-6` |
| OpenAI | `openai` | `OPENAI_API_KEY` | `gpt-4o` |
| OpenRouter | `openrouter` | `OPENROUTER_API_KEY` | `anthropic/claude-sonnet-4-5` |
| Amazon Bedrock | `bedrock` | `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` | `anthropic.claude-3-5-sonnet-20241022-v2:0` |
| Ollama (local) | `ollama` | *(none — Ollama must be running)* | `llama3.2` |

**Ollama setup:**

```bash
# Install Ollama: https://ollama.com
ollama pull llama3.2
# Then set LLM_PROVIDER=ollama in .env
```

**OpenRouter example** (access 200+ models with one API key):

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-...
LLM_MODEL=google/gemini-2.0-flash   # optional override
```

---

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Backend status and active model |
| `POST` | `/api/v1/generate` | Generate a product sheet (synchronous) |
| `POST` | `/api/v1/generate/stream` | Generate with live SSE streaming |
| `POST` | `/api/v1/export/pdf` | Export a product sheet as PDF |
| `POST` | `/api/v1/export/json` | Export a product sheet as JSON |

**Example request:**

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Sony WH-1000XM5",
    "category": "Wireless Headphones",
    "target_audience": "Remote workers and frequent travellers",
    "tone": "professional",
    "language": "en"
  }'
```

---

## Running tests

```bash
pytest tests/
```

Tests use mocked LLM responses — no API key required.

---

## Agent architecture

The agent uses a LangGraph state graph with a ReAct loop:

```
[START] → route_input
             ├─ (has URL) → scrape_url → agent
             └─ (no URL) ──────────────→ agent
                                             │
                                   tool_calls?
                                    ├─ yes → ToolNode → agent  (loop)
                                    └─ no  → validate_output
                                                  │
                                           valid? ├─ yes → END
                                                  └─ no  → agent (retry, max 5)
```

The full Mermaid diagram is available on the **About** page of the UI.
