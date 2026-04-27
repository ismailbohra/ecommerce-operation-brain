# EcomX

An intelligent multi-agent AI system for e-commerce business operations, built with LangGraph and FastAPI. This application provides a conversational interface powered by specialized AI agents that handle sales analytics, inventory management, customer support, marketing campaigns, and organizational memory.

---

## About

**EcomX** is a sophisticated AI-powered assistant designed to streamline e-commerce operations through natural language interactions. The system uses a **multi-agent architecture** where a supervisor (router) agent routes user queries to specialized domain agents, each equipped with specific tools and knowledge bases.

### Key Features

- **Sales Agent**: Analyzes sales data, revenue trends, and order patterns
- **Inventory Agent**: Monitors stock levels, identifies low/out-of-stock items, manages reorder alerts
- **Support Agent**: Handles customer tickets, prioritizes issues, and resolves support queries
- **Marketing Agent**: Manages campaigns, tracks ad spend, and monitors marketing metrics
- **Memory Agent**: Maintains organizational knowledge through past incidents and context
- **Human-in-the-Loop (HITL)**: Actions requiring approval are presented to users before execution
- **Real-time Streaming**: SSE-based streaming with per-agent progress events
- **Dashboard**: Live metrics for sales, inventory, support, and marketing

---

## Architecture

The project is split into a **FastAPI backend** and a **React frontend**, connected via a REST/SSE API.

```
┌─────────────────────────────────────────────────────────────────┐
│                     React SPA (Vite + TS)                       │
│   ChatContainer │ SessionList │ Dashboard │ ActionApproval      │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP / SSE
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (:8000)                        │
│   POST /api/chat/stream   GET /api/metrics   /api/sessions/…    │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LangGraph Workflow                         │
│                                                                 │
│  START → [router] ─────────────────────────────→ [synthesis]   │
│                  │                                      ↑       │
│                  └→ [sales_agent]    ────────────────── ┘       │
│                  └→ [inventory_agent] ───────────────── ┘       │
│                  └→ [support_agent]  ────────────────── ┘       │
│                  └→ [marketing_agent] ───────────────── ┘       │
│                  └→ [memory_agent]   ────────────────── ┘       │
│                                                                 │
│            [synthesis] → [action] ──has_actions──→ [execute]   │
│                                   └─no_actions──→  END         │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌──────────────────┐            ┌──────────────────┐
│  PostgreSQL (DB) │            │  Qdrant Vector   │
│   - products     │            │     Store        │
│   - sales        │            │   - incidents    │
│   - inventory    │            │   - tickets      │
│   - tickets      │            │   - products     │
│   - campaigns    │            │                  │
│   - incidents    │            │                  │
│   - sessions     │            │                  │
│   - messages     │            │                  │
└──────────────────┘            └──────────────────┘
```

### Workflow Flow

1. **Router Node**: Analyzes the user query with the supervisor LLM and decides which agents to call (or responds directly if no agents are needed)
2. **Agent Nodes**: Fan-out via `Send` — selected agents run in parallel, each calling domain-specific tools against the database/vector store
3. **Synthesis Node**: Fan-in — aggregates all agent outputs into a coherent response using the supervisor LLM
4. **Action Node**: Scans the synthesis for executable actions (e.g., reorder stock, close a ticket) and emits structured `proposed_actions`
5. **Execute Node**: Pauses for HITL confirmation (`interrupt_before=["execute"]`), then runs only the approved actions

---

## Project Structure

```
ecomx-ecommerce-agent/
├── docker-compose.yml              # Orchestrates app + postgres + qdrant
│
├── backend/
│   ├── requirements.txt            # Python dependencies
│   ├── python.ini                  # Pytest / logging configuration
│   ├── Dockerfile
│   ├── .dockerignore
│   │
│   ├── config.py                   # Config class + LLM/embedding factory helpers
│   ├── logger.py                   # Logging setup
│   │
│   ├── api/                        # FastAPI application
│   │   ├── main.py                 # App factory, lifespan (DB + vectorstore + workflow init)
│   │   ├── models.py               # Pydantic request/response models
│   │   └── routes/
│   │       ├── __init__.py         # APIRouter aggregation (prefix: /api)
│   │       ├── chat.py             # POST /chat, POST /chat/stream, POST /chat/actions
│   │       ├── metrics.py          # GET /metrics
│   │       └── sessions.py         # CRUD /sessions
│   │
│   ├── graph/                      # LangGraph workflow
│   │   ├── __init__.py
│   │   ├── workflow.py             # Graph definition, create_workflow(), run_query(), resume_with_actions()
│   │   ├── nodes.py                # router_node, agent nodes, synthesis_node, action_node, execute_actions_node
│   │   ├── state.py                # AgentState TypedDict
│   │   ├── actions.py              # Action parsing and execution logic
│   │   ├── prompts.py              # Loads prompt .md files at import time
│   │   ├── events.py               # Per-request SSE progress event emitter
│   │   │
│   │   ├── agents/                 # Specialized domain agents
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # BaseAgent abstract class
│   │   │   ├── sales.py
│   │   │   ├── inventory.py
│   │   │   ├── support.py
│   │   │   ├── marketing.py
│   │   │   └── memory.py
│   │   │
│   │   └── tools/                  # LangChain tools used by agents
│   │       ├── __init__.py
│   │       ├── utils.py
│   │       ├── sales.py
│   │       ├── inventory.py
│   │       ├── support.py
│   │       ├── marketing.py
│   │       └── memory.py
│   │
│   ├── db/                         # PostgreSQL database layer
│   │   ├── __init__.py
│   │   ├── database.py             # Async DB operations (asyncpg)
│   │   └── seed.py                 # Database seeding with sample data
│   │
│   ├── vectorstore/                # Qdrant vector store layer
│   │   ├── __init__.py
│   │   ├── store.py                # Qdrant client wrapper
│   │   └── seed.py                 # Vector store seeding
│   │
│   ├── prompts/                    # Markdown prompt templates
│   │   ├── router.md
│   │   ├── synthesis.md
│   │   ├── action.md
│   │   └── agents/
│   │       ├── sales.md
│   │       ├── inventory.md
│   │       ├── support.md
│   │       ├── marketing.md
│   │       └── memory.md
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── metrics.py
│       ├── test_action.py
│       ├── test_router.py
│       ├── test_synthesis.py
│       ├── test_workflow.py
│       └── test_agents/
│           ├── test_sales.py
│           ├── test_inventory.py
│           ├── test_support.py
│           ├── test_marketing.py
│           └── test_memory.py
│
└── frontend/                       # React + TypeScript + Vite SPA
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx
    │   ├── types/index.ts
    │   ├── lib/
    │   │   ├── api.ts              # Typed API client (fetch + SSE)
    │   │   └── utils.ts
    │   ├── hooks/
    │   │   ├── useChat.ts
    │   │   ├── useSessions.ts
    │   │   └── useMetrics.ts
    │   └── components/
    │       ├── layout/AppLayout.tsx
    │       ├── chat/
    │       │   ├── ChatContainer.tsx
    │       │   ├── ChatMessage.tsx
    │       │   ├── ChatInput.tsx
    │       │   ├── SessionList.tsx
    │       │   ├── AgentBadges.tsx
    │       │   ├── AgentProgress.tsx
    │       │   └── EmptyState.tsx
    │       ├── dashboard/
    │       │   ├── Sidebar.tsx
    │       │   └── MetricCard.tsx
    │       └── actions/
    │           └── ActionApproval.tsx
    └── package.json
```

---

## Frameworks, Tools & Dependencies

### Backend

| Package | Purpose |
|---------|---------|
| **FastAPI** | REST API + SSE streaming |
| **LangGraph** | Graph-based multi-agent workflow |
| **LangChain** | LLM orchestration and tool integration |
| `langgraph-checkpoint-postgres` | Workflow state persistence (PostgreSQL) |
| `langchain-openai` | Azure OpenAI LLM + embeddings |
| **asyncpg / psycopg** | Async PostgreSQL driver |
| **Qdrant** | Vector database for semantic search |
| `sse-starlette` | Server-Sent Events support |
| `python-dotenv` | Environment variable management |

### Frontend

| Package | Purpose |
|---------|---------|
| **React 18 + TypeScript** | UI framework |
| **Vite** | Build tool and dev server |
| **Tailwind CSS** | Utility-first styling |
| **shadcn/ui** | Component library |

### Testing

| Package | Purpose |
|---------|---------|
| `pytest` / `pytest-asyncio` | Test framework |
| `deepeval` | LLM output evaluation |
| `langsmith` | Tracing and observability |

---

## Configuration

Create a `.env` file inside `backend/`:

```env
# Azure OpenAI
DIAL_API_KEY=your_api_key
AZURE_ENDPOINT=https://your-endpoint.openai.azure.com/
API_VERSION=2024-02-15-preview

# Model overrides (optional)
MODEL_SUPERVISOR=claude-sonnet-4@20250514
MODEL_SALES=claude-haiku-4-5@20251001
MODEL_INVENTORY=claude-haiku-4-5@20251001
MODEL_SUPPORT=claude-haiku-4-5@20251001
MODEL_MARKETING=claude-haiku-4-5@20251001
MODEL_MEMORY=claude-haiku-4-5@20251001
MODEL_ACTION=claude-haiku-4-5@20251001
MODEL_EMBEDDING=text-embedding-3-small-1

# PostgreSQL
DATABASE_URL=postgresql://ecomx:ecomx@localhost:5432/ecomx

# Qdrant
QDRANT_MODE=server          # Options: memory, local, server
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_PATH=data/qdrant
```

---

## Running the Application

### Option 1: Docker Compose (recommended)

```bash
# Clone the repo
git clone <repository-url>
cd ecomx-ecommerce-agent

# Create backend env file
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Start all services (app + postgres + qdrant)
docker compose up --build
```

Access the app at `http://localhost:8000`.

#### Docker Services

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `app` | local build | 8000 | FastAPI + React SPA |
| `postgres` | postgres:16-alpine | 5432 | Primary database |
| `qdrant` | qdrant/qdrant | 6333 / 6334 | Vector store |

---

### Option 2: Local Development

#### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ running locally
- Qdrant running locally (or use `QDRANT_MODE=memory` for in-process)

#### Backend

```bash
cd backend

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt

# Copy and fill in env
cp .env.example .env

# Start the API server
uvicorn api.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev        # starts on http://localhost:5173
```

The frontend dev server proxies API requests to `http://localhost:8000`. For a production build:

```bash
npm run build      # outputs to frontend/dist/
# FastAPI serves the dist/ folder automatically
```

---

### Running Tests

```bash
cd backend

# Run all tests
pytest

# Verbose
pytest -v

# Specific file
pytest tests/test_workflow.py

# Parallel
pytest -n auto

# With coverage
pytest --cov=graph --cov=db --cov=vectorstore
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/chat` | Single-turn chat (blocking) |
| `POST` | `/api/chat/stream` | Streaming chat via SSE |
| `POST` | `/api/chat/actions` | Approve and execute proposed actions |
| `GET` | `/api/metrics` | Dashboard metrics (sales, inventory, support, marketing) |
| `GET` | `/api/sessions` | List all sessions |
| `POST` | `/api/sessions` | Create a session |
| `GET` | `/api/sessions/{id}` | Session detail + message history |
| `PATCH` | `/api/sessions/{id}` | Rename session |
| `DELETE` | `/api/sessions/{id}` | Delete session |
| `GET` | `/api/health` | Health check |

### SSE Events (`/api/chat/stream`)

Events are emitted in order during a streaming response:

```
status → router_start → router_done → agents_start →
  agent_start (×N) / agent_done (×N) →
agents_done → synthesis_start → synthesis_done →
action_start → action_done →
agents → token (×N) → actions? → done
```

---

## Usage Examples

Once the application is running, interact through natural language:

- **Sales**: "What were our top-selling products last week?"
- **Inventory**: "Which products are running low on stock?"
- **Support**: "Show me all high-priority open tickets"
- **Marketing**: "What's the performance of our current campaigns?"
- **General**: "Give me a business overview for today"

The system routes your query to the appropriate agents, runs them in parallel, and synthesizes a comprehensive response. If the response includes actionable items (e.g., reorder stock), they are presented for approval before execution.
