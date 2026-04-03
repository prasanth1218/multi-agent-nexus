# 🚀 NexusAI — Multi-Agent Intelligence Platform

A full-stack AI-powered multi-agent system that delivers **real-time streaming responses** through specialized AI agents working in parallel. Built with **FastAPI** (backend) and **React + Vite** (frontend).

![Architecture](https://img.shields.io/badge/Architecture-Multi--Agent-6c5ce7?style=for-the-badge)
![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge)
![Frontend](https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge)

---

## 🧠 Architecture

```
User → React UI → FastAPI Backend → Orchestrator
                                        │
                                   ┌────┴─────┐
                                   │ Planner   │ (fast routing, <500ms)
                                   └────┬─────┘
                                        │
                         ┌──────────────┼──────────────┐
                         │              │              │
                    ┌────┴───┐    ┌────┴───┐    ┌────┴────┐
                    │ Coder  │    │ Writer │    │Research │  (parallel)
                    └────┬───┘    └────┬───┘    └────┬────┘
                         └──────────────┼──────────────┘
                                        │
                                   ┌────┴─────┐
                                   │ Reviewer  │ (optional, complex tasks only)
                                   └──────────┘
```

### Agents

| Agent | Role | Model |
|-------|------|-------|
| **Planner** | Classifies tasks and routes to correct agents | GPT-3.5-turbo (fast) |
| **Coding Agent** | Code generation, debugging, technical tasks | GPT-4o-mini |
| **Writer Agent** | Content creation, essays, professional docs | GPT-4o-mini |
| **Research Agent** | Factual Q&A, analysis, comparisons | GPT-4o-mini |
| **Reviewer** | Merges multi-agent outputs (complex tasks only) | GPT-4o-mini |

---

## ⚡ Performance Optimizations

| Feature | Impact |
|---------|--------|
| **SSE Streaming** | First token visible in <1 second |
| **Parallel Execution** | Multiple agents run via `asyncio.gather()` |
| **Smart Routing** | Planner uses fast model, selects minimum agents needed |
| **Response Caching** | In-memory LRU cache with TTL for repeated queries |
| **Async Everything** | Non-blocking I/O throughout backend |
| **Conditional Review** | Reviewer only runs for complex multi-agent tasks |
| **Connection Pooling** | Singleton OpenAI client reuses TCP connections |

---

## 📁 Project Structure

```
multi-agent-ai/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Settings (env-based)
│   ├── requirements.txt        # Python dependencies
│   ├── agents/
│   │   ├── base.py             # BaseAgent abstract class
│   │   ├── planner.py          # Task routing (fast model)
│   │   ├── coder.py            # Coding Agent
│   │   ├── writer.py           # Writer Agent
│   │   ├── researcher.py       # Research Agent
│   │   ├── reviewer.py         # Reviewer Agent
│   │   └── orchestrator.py     # Parallel execution + streaming
│   ├── api/
│   │   ├── chat.py             # SSE streaming chat endpoint
│   │   ├── conversations.py    # Conversation CRUD
│   │   └── health.py           # Health check
│   └── services/
│       ├── cache.py            # In-memory LRU cache
│       ├── database.py         # SQLite via aiosqlite
│       └── llm.py              # OpenAI client wrapper
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Root component
│   │   ├── index.css           # Design system (dark theme)
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── MessageBubble.jsx
│   │   │   ├── CodeBlock.jsx
│   │   │   ├── AgentActivityPanel.jsx
│   │   │   └── Sidebar.jsx
│   │   ├── hooks/
│   │   │   ├── useChat.js      # SSE streaming hook
│   │   │   └── useConversations.js
│   │   └── services/
│   │       └── api.js          # API client
│   └── package.json
├── .env.example                # Environment template
└── README.md                   # This file
```

---

## 🛠️ Setup Guide

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **OpenAI API Key** ([get one here](https://platform.openai.com/api-keys))

### Step 1: Clone & Configure

```bash
# Navigate to the project
cd multi-agent-ai

# Create .env file from template
copy .env.example backend\.env

# Edit backend\.env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

### Step 2: Start Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be running at `http://localhost:8000`
API docs available at `http://localhost:8000/docs`

### Step 3: Start Frontend

```bash
cd frontend

# Install dependencies (if not already done)
npm install

# Start dev server
npm run dev
```

The frontend will be running at `http://localhost:5173`

---

## 🧪 Testing Examples

### 1. Coding Task
> "Write a Python function that implements binary search"
- **Expected**: Planner routes to → **Coding Agent** → streams Python code with explanation

### 2. Writing Task
> "Write a cover letter for a software engineering position at Google"
- **Expected**: Planner routes to → **Writer Agent** → streams professional letter

### 3. Research Task
> "Compare React vs Vue vs Angular — pros and cons"
- **Expected**: Planner routes to → **Research Agent** → structured comparison

### 4. Multi-Agent Task (parallel)
> "Build a landing page for an AI startup with compelling marketing copy"
- **Expected**: Planner routes to → **Coding + Writer Agents** (parallel) → **Reviewer** merges → polished result

### 5. Cached Response
> Send the same question twice → second response is **instant** (from cache)

---

## 🔧 Configuration

All settings are configurable via environment variables in `backend/.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (required) | Your OpenAI API key |
| `PLANNER_MODEL` | `gpt-3.5-turbo` | Fast model for task routing |
| `AGENT_MODEL` | `gpt-4o-mini` | Model for agent responses |
| `REVIEWER_MODEL` | `gpt-4o-mini` | Model for review/merge |
| `CACHE_TTL_SECONDS` | `3600` | Cache expiry time |
| `CACHE_MAX_SIZE` | `500` | Max cached responses |
| `MAX_TOKENS` | `4096` | Max response length |
| `TEMPERATURE` | `0.7` | Response creativity |

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Send message, receive SSE stream |
| `GET` | `/api/conversations` | List all conversations |
| `POST` | `/api/conversations` | Create new conversation |
| `GET` | `/api/conversations/:id` | Get conversation + messages |
| `PATCH` | `/api/conversations/:id` | Update conversation title |
| `DELETE` | `/api/conversations/:id` | Delete conversation |
| `GET` | `/api/health` | System health check |

---

## 🎓 For Final Year Project Presentation

### Key Technical Highlights
1. **Multi-Agent Orchestration** — intelligent task routing with minimum agent selection
2. **Real-time Streaming** — SSE-based token streaming for ChatGPT-like UX
3. **Parallel Processing** — concurrent agent execution via `asyncio.gather()`
4. **Smart Caching** — LRU cache with TTL for instant repeated responses
5. **Clean Architecture** — modular, extensible agent design pattern

### Performance Metrics to Demo
- Single-agent response: **first token in <1s**
- Multi-agent parallel: **2-3x faster than sequential**
- Cached response: **<50ms** (instant)
- Planner routing: **<500ms overhead**

---

## 📝 License

Built for academic purposes — Final Year Project.
