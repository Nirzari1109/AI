# 📊 LLM Evaluation & Observability Framework

An end-to-end evaluation framework for RAG pipelines — measures faithfulness, relevance, and latency across 50 test questions using LLM-as-judge scoring, stores results in SQLite, and visualises everything on an interactive Streamlit dashboard.

![Dashboard](demo.gif)

---

## 🏗️ Architecture

```
Golden Test Set (50 questions)
        ↓
🏃 Evaluation Runner
        ↓
┌─────────────────────────────────────────┐
│  RAG API (Project 1 — Dev Assistant)    │
│  → Returns answer + agent route         │
└─────────────────────────────────────────┘
        ↓
┌──────────────────┬──────────────────────┐
│ 🧑‍⚖️ Faithfulness  │  🎯 Relevance scorer  │
│ LLM-as-judge     │  LLM-as-judge        │
│ (Groq LLaMA 3.3) │  (Groq LLaMA 3.3)   │
└──────────────────┴──────────────────────┘
        ↓
⏱️ Latency Tracker
        ↓
🗄️ SQLite Database
        ↓
📊 Streamlit Dashboard
```

---

## ✨ Features

- **LLM-as-judge scoring** — uses Groq LLaMA 3.3 to score faithfulness and relevance on a 1–5 scale, normalised to 0–1
- **50-question golden test set** — covers FastAPI, GitHub Actions, Docker, and Python packaging topics across easy/medium/hard difficulties
- **Latency tracking** — measures end-to-end response time for every query
- **SQLite persistence** — all results stored with run IDs for historical comparison
- **Interactive dashboard** — 4 charts + worst-performing questions panel + full results table
- **Run comparison** — select different eval runs from the sidebar to compare performance over time

---

## 📈 Sample Results

| Metric | Score |
|---|---|
| Avg Faithfulness | 0.84 |
| Avg Relevance | 0.99 |
| Avg Latency | 6835ms |
| Low Faithfulness Questions | 4 / 50 |

**Key finding:** GitHub Actions caching and middleware questions scored lowest — pointing to insufficient chunk coverage in the ingested documentation for those topics.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM Judge | Groq (LLaMA 3.3 70B) |
| Vector Store | ChromaDB (via Project 1) |
| Database | SQLite |
| Dashboard | Streamlit + Plotly |
| RAG Backend | FastAPI (Project 1) |

---

## 🚀 Quick Start

### Prerequisites
Project 1 (Dev Assistant) must be running:
```bash
cd ../dev-assistant-agent
uvicorn main:app --reload
```

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/Nirzari1109/AI.git
cd AI/llm-eval-framework

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
cp .env.example .env
# Edit .env with your GROQ_API_KEY
```

### Run Evaluation

```bash
# Run all 50 questions through the RAG pipeline
python -m src.runner
```

Output:
```
==================================================
EVAL RUN: a3d50362
Questions: 50
==================================================
[1/50] How do I create a basic FastAPI application?...
  ✓ Routed: rag | Faithfulness: 1.0 | Relevance: 1.0 | Latency: 5821ms
...
==================================================
RUN a3d50362 COMPLETE
Avg Faithfulness : 0.84
Avg Relevance    : 0.99
Avg Latency      : 6835ms
==================================================
```

### Launch Dashboard

```bash
python -m streamlit run dashboard.py
```

Open **http://localhost:8501**

---

## 🔑 Environment Variables

```
GROQ_API_KEY=your_groq_key_here
RAG_API_URL=http://127.0.0.1:8000
```

Get a free Groq key at **https://console.groq.com**

---

## 📁 Project Structure

```
llm-eval-framework/
├── dashboard.py             # Streamlit dashboard
├── requirements.txt
├── .env.example
└── src/
    ├── runner.py            # Main eval pipeline
    ├── db.py                # SQLite logger
    ├── evaluators/
    │   ├── faithfulness.py  # LLM-as-judge faithfulness scorer
    │   ├── relevance.py     # LLM-as-judge relevance scorer
    │   └── latency.py       # Response time tracker
    └── data/
        └── golden_set.json  # 50 test questions with expected answers
```

---

## 💡 How LLM-as-Judge Works

Each answer is scored by calling the LLM with a structured prompt:

```
QUESTION: How does FastAPI handle request body validation?
EXPECTED: FastAPI uses Pydantic models to automatically validate...
ACTUAL:   FastAPI uses Pydantic BaseModel classes to define...

Score 1-5 for faithfulness. Reply with one integer only.
→ 4  (= 0.8 normalised)
```

This approach catches hallucinations and partial answers that keyword matching would miss.

---
