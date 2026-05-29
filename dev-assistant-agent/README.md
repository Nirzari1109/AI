# 🤖 Dev Assistant — Multi-Agent AI System

A production-grade multi-agent AI system that routes software engineering questions
to specialist agents using LangGraph orchestration.

![Demo](demo.gif)

---

## 🏗️ Architecture

```
User Query
    ↓
🧠 Planner Agent (LLM-based routing)
    ↓
┌───────────────┬──────────────────┬──────────────────┐
│  📚 RAG Agent │  🔍 Code Agent   │  🌐 Search Agent  │
│  ChromaDB     │  Local codebase  │  Tavily web       │
│  vector store │  file search     │  search           │
└───────────────┴──────────────────┴──────────────────┘
    ↓
✍️ Synthesiser Agent
    ↓
Final Answer
```

---

## ✨ Features

- **LLM-powered routing** — Planner uses an LLM to decide which agent handles each query, not brittle keyword matching
- **RAG pipeline** — ChromaDB vector store ingested with real documentation (FastAPI, GitHub Actions, Docker, Python packaging)
- **Live agent trace** — UI shows every step of the agent pipeline animating in real time
- **Web search** — Search agent fetches live results via Tavily for current information
- **Code search** — Scans local codebase for relevant file matches
- **Dockerised** — Full stack runs with a single `docker compose up`

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Agent orchestration | LangGraph |
| Vector store | ChromaDB |
| Embeddings | ONNX (local, no API cost) |
| LLM | Groq (LLaMA 3.3 70B) |
| Backend API | FastAPI |
| Frontend | Streamlit |
| Containerisation | Docker + docker-compose |

---

## 🚀 Quick Start

### Option A — Docker (recommended)

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/dev-assistant-agent.git
cd dev-assistant-agent

# 2. Add your API keys
cp .env.example .env
# Edit .env with your GROQ_API_KEY and TAVILY_API_KEY

# 3. Ingest documentation into ChromaDB
python src/tools/ingest.py

# 4. Start everything
docker compose up --build
```

Open http://localhost:8501

### Option B — Local Development

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
python src/tools/ingest.py

# Terminal 1
uvicorn main:app --reload

# Terminal 2
python -m streamlit run app.py
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_key_here
TAVILY_API_KEY=your_tavily_key_here
```

Get free API keys:
- **Groq** (LLM): https://console.groq.com
- **Tavily** (Web search): https://tavily.com

---

## 📁 Project Structure

```
dev-assistant-agent/
├── main.py                  # FastAPI backend
├── app.py                   # Streamlit frontend
├── docker-compose.yml       # Multi-container setup
├── Dockerfile.api           # API container
├── Dockerfile.ui            # UI container
├── requirements.txt
├── .env.example
└── src/
    ├── graph.py             # LangGraph orchestration
    ├── agents/
    │   ├── planner.py       # LLM-based query router
    │   ├── rag_agent.py     # ChromaDB retrieval + synthesis
    │   ├── code_agent.py    # Local codebase file search
    │   └── search_agent.py  # Tavily web search
    ├── tools/
    │   ├── ingest.py        # Doc ingestion pipeline
    │   └── retriever.py     # ChromaDB query helper
    └── utils/
        ├── llm.py           # LLM client (Groq)
        └── embeddings.py    # ONNX embeddings
```

---

## 💡 Example Queries

| Query | Agent Routed To |
|---|---|
| "How does FastAPI request body work?" | 📚 RAG Agent |
| "Show me code that uses similarity_search" | 🔍 Code Agent |
| "Latest updates to Python packaging" | 🌐 Search Agent |
| "How do I set up GitHub Actions for Python?" | 📚 RAG Agent |
| "How do I use Docker multi-container setup?" | 📚 RAG Agent |

---

## 🔍 How the Agent Trace Works

Every query shows a live step-by-step trace in the UI:

```
🧠 Planner      ✅ Routed to → RAG Agent
📚 RAG Agent    ✅ Retrieved relevant chunks from vector store
✍️ Synthesiser  ✅ Answer ready
```

Each step animates from ⏳ running → ✅ done, making the agent decision-making fully transparent.

---
