# Ecom

An intelligent multi-agent AI system for e-commerce business operations, built with LangGraph and LangChain. This application provides a conversational interface powered by specialized AI agents that handle sales analytics, inventory management, customer support, marketing campaigns, and organizational memory.

---

## 📋 About

**E-commerce AI Brain** is a sophisticated AI-powered assistant designed to streamline e-commerce operations through natural language interactions. The system uses a **multi-agent architecture** where a supervisor agent routes user queries to specialized domain agents, each equipped with specific tools and knowledge bases.

### Key Features

- **🛒 Sales Agent**: Analyzes sales data, revenue trends, and order patterns
- **📦 Inventory Agent**: Monitors stock levels, identifies low/out-of-stock items, manages reorder alerts
- **🎧 Support Agent**: Handles customer tickets, prioritizes issues, and resolves support queries
- **📢 Marketing Agent**: Manages campaigns, tracks ad spend, and monitors marketing metrics
- **🧠 Memory Agent**: Maintains organizational knowledge through past incidents and context
- **✅ Human-in-the-Loop (HITL)**: Actions requiring approval are presented to users before execution
- **📊 Real-time Dashboard**: Live metrics for sales, inventory, support, and marketing

---

## 🏗️ Architecture

The project follows a **graph-based multi-agent architecture** using LangGraph:

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                    (Streamlit Web Application)                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LangGraph Workflow                         │
│  ┌──────────┐   ┌──────────┐   ┌───────────┐   ┌────────────┐   │
│  │  Router  │ → │  Agents  │ → │ Synthesis │ → │   Action   │   │
│  │   Node   │   │   Node   │   │    Node   │   │    Node    │   │
│  └──────────┘   └──────────┘   └───────────┘   └────────────┘   │
│                      │                               │          │
│         ┌────────────┼────────────┐                  ▼          │
│         ▼            ▼            ▼          ┌────────────┐     │
│    ┌─────────┐ ┌───────────┐ ┌─────────┐    │  Execute   │      │
│    │  Sales  │ │ Inventory │ │ Support │    │   (HITL)   │      │
│    └─────────┘ └───────────┘ └─────────┘    └────────────┘      │
│         ▼            ▼            ▼                             │
│    ┌─────────┐ ┌───────────┐                                    │
│    │Marketing│ │  Memory   │                                    │
│    └─────────┘ └───────────┘                                    │
└─────────────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌──────────────────┐            ┌──────────────────┐
│   SQLite (DB)    │            │  Qdrant Vector   │
│   - Products     │            │     Store        │
│   - Sales        │            │   - Incidents    │
│   - Inventory    │            │   - Tickets      │
│   - Tickets      │            │   - Products     │
│   - Campaigns    │            │                  │
│   - Incidents    │            │                  │
└──────────────────┘            └──────────────────┘
```

### Workflow Flow

1. **Router Node**: Analyzes user query and determines which specialized agents to invoke
2. **Agents Node**: Executes selected agents in parallel, each using domain-specific tools
3. **Synthesis Node**: Combines outputs from multiple agents into a coherent response
4. **Action Node**: Identifies actionable items requiring execution
5. **Execute Node**: Executes approved actions with Human-in-the-Loop confirmation

---

## 📁 Project Structure

```
ecommerce_ai_brain/
├── app.py                      # Main Streamlit application entry point
├── config.py                   # Configuration and LLM initialization
├── logger.py                   # Logging configuration and utilities
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker container configuration
├── docker-compose.yml          # Multi-container Docker setup
├── python.ini                  # Python configuration
│
├── db/                         # Database layer
│   ├── __init__.py
│   ├── database.py             # SQLite database operations (async)
│   └── seed.py                 # Database seeding with sample data
│
├── graph/                      # LangGraph workflow components
│   ├── __init__.py
│   ├── workflow.py             # Main graph workflow definition
│   ├── nodes.py                # Graph node implementations
│   ├── state.py                # Agent state definitions
│   ├── actions.py              # Action execution logic
│   ├── prompts.py              # System prompts for nodes
│   ├── data_fetchers.py        # Data retrieval utilities
│   ├── formatters.py           # Output formatting utilities
│   │
│   ├── agents/                 # Specialized domain agents
│   │   ├── __init__.py
│   │   ├── base.py             # Base agent abstract class
│   │   ├── sales.py            # Sales analytics agent
│   │   ├── inventory.py        # Inventory management agent
│   │   ├── support.py          # Customer support agent
│   │   ├── marketing.py        # Marketing campaign agent
│   │   └── memory.py           # Organizational memory agent
│   │
│   └── tools/                  # Agent-specific tools
│       ├── __init__.py
│       ├── sales.py            # Sales data tools
│       ├── inventory.py        # Inventory query tools
│       ├── support.py          # Ticket management tools
│       ├── marketing.py        # Campaign management tools
│       └── memory.py           # Knowledge retrieval tools
│
├── prompts/                    # Markdown prompt templates
│   ├── action.md               # Action extraction prompt
│   ├── router.md               # Agent routing prompt
│   ├── synthesis.md            # Response synthesis prompt
│   └── agents/                 # Agent-specific prompts
│       ├── sales.md
│       ├── inventory.md
│       ├── support.md
│       ├── marketing.md
│       └── memory.md
│
├── vectorstore/                # Vector database layer
│   ├── __init__.py
│   ├── store.py                # Qdrant vector store operations
│   └── seed.py                 # Vector store seeding
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Pytest configuration & fixtures
│   ├── metrics.py              # Test metrics utilities
│   ├── test_action.py          # Action node tests
│   ├── test_router.py          # Router node tests
│   ├── test_synthesis.py       # Synthesis node tests
│   ├── test_workflow.py        # End-to-end workflow tests
│   └── test_agents/            # Agent-specific tests
│       ├── test_sales.py
│       ├── test_inventory.py
│       ├── test_support.py
│       ├── test_marketing.py
│       └── test_memory.py
│
└── data/                       # Storage for DB and vectorstore
```

---

## 🛠️ Frameworks, Tools & Dependencies

### Core Frameworks

| Framework | Version | Purpose |
|-----------|---------|---------|
| **LangChain** | 1.2.6 | LLM orchestration and tool integration |
| **LangGraph** | 1.0.6 | Graph-based multi-agent workflow |
| **Streamlit** | 1.53.0 | Web UI and dashboard |
| **Azure OpenAI** | 2.15.0 | LLM API integration |

### AI/ML Libraries

| Library | Purpose |
|---------|---------|
| `langchain-openai` | Azure OpenAI integration |
| `langchain-core` | Core LangChain abstractions |
| `langgraph-checkpoint` | Workflow state persistence |
| `tiktoken` | Token counting for LLMs |

### Data Storage

| Technology | Purpose |
|------------|---------|
| **SQLite** (via `aiosqlite`) | Relational database for business data |
| **Qdrant** | Vector database for semantic search |

### Observability

| Tool | Purpose |
|------|---------|
| **Langfuse** | LLM observability and tracing |
| **OpenTelemetry** | Distributed tracing |

### Testing

| Framework | Purpose |
|-----------|---------|
| `pytest` | Test framework |
| `pytest-asyncio` | Async test support |
| `pytest-xdist` | Parallel test execution |
| `deepeval` | LLM output evaluation |

### Data Processing

| Library | Purpose |
|---------|---------|
| `pandas` | Data manipulation |
| `numpy` | Numerical computing |
| `plotly` | Data visualization |

### Other Dependencies

- `python-dotenv` - Environment variable management
- `pydantic` - Data validation
- `httpx` / `aiohttp` - HTTP clients
- `grpcio` - gRPC for Qdrant communication

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Required - Azure OpenAI Configuration
DIAL_API_KEY=your_api_key
AZURE_ENDPOINT=https://your-endpoint.openai.azure.com/
API_VERSION=2024-02-15-preview

# Optional - Model Overrides
MODEL_SUPERVISOR=claude-sonnet-4@20250514
MODEL_SALES=claude-haiku-4-5@20251001
MODEL_INVENTORY=claude-haiku-4-5@20251001
MODEL_SUPPORT=claude-haiku-4-5@20251001
MODEL_MARKETING=claude-haiku-4-5@20251001
MODEL_MEMORY=claude-haiku-4-5@20251001
MODEL_ACTION=claude-haiku-4-5@20251001
MODEL_EMBEDDING=text-embedding-3-small-1

# Database Configuration
DB_PATH=data/ecommerce.db

# Qdrant Configuration
QDRANT_MODE=memory          # Options: memory, local, server
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_PATH=data/qdrant

# Optional - Langfuse Observability
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_HOST=https://cloud.langfuse.com
```

---

## 🚀 Instructions to Run

### Option 1: Local Development

#### Prerequisites

- Python 3.11+
- pip or uv package manager

#### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ecommerce_ai_brain
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example and fill in your values
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Access the application**
   
   Open your browser and navigate to `http://localhost:8501`

---

### Option 2: Docker Deployment

#### Prerequisites

- Docker
- Docker Compose

#### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ecommerce_ai_brain
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   
   Open your browser and navigate to `http://localhost:8501`

#### Docker Services

- **app**: Main Streamlit application (port 8501)
- **qdrant**: Vector database service (port 6333)

#### Data Persistence

Docker volumes persist data between container restarts:
- `app-data`: SQLite database and Qdrant storage

---

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_workflow.py

# Run tests in parallel
pytest -n auto

# Run with coverage
pytest --cov=graph --cov=db --cov=vectorstore
```

---

## 📖 Usage Examples

Once the application is running, you can interact with the AI through natural language:

- **Sales**: "What were our top-selling products last week?"
- **Inventory**: "Which products are running low on stock?"
- **Support**: "Show me all high-priority open tickets"
- **Marketing**: "What's the performance of our current campaigns?"
- **General**: "Give me a business overview for today"

The system will automatically route your query to the appropriate agents and synthesize a comprehensive response.

---

