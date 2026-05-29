import streamlit as st
import requests
import time
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")   

st.set_page_config(
    page_title="Dev Assistant",
    page_icon="🤖",
    layout="centered"
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.trace-box {
    background: #0e1117;
    border: 1px solid #2d2d2d;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-family: monospace;
    font-size: 13px;
}
.trace-running { border-left: 3px solid #f0ad4e; color: #f0ad4e; }
.trace-done    { border-left: 3px solid #5cb85c; color: #e0e0e0; }
.step-label    { font-weight: bold; color: #aaa; margin-right: 8px; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🤖 Dev Assistant")
st.caption("Multi-agent AI system · LangGraph · RAG · Web Search · Code Search")

with st.expander("ℹ️ How it works", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**📚 RAG Agent**\nAnswers from ingested docs — FastAPI, GitHub Actions, Docker, Python packaging")
    with col2:
        st.markdown("**🔍 Code Agent**\nSearches local project files for relevant code")
    with col3:
        st.markdown("**🌐 Search Agent**\nFetches live web results via Tavily")

st.divider()

# ── Input ─────────────────────────────────────────────────────────────────────
if "query" not in st.session_state:
    st.session_state.query = ""

example_queries = [
    "How does FastAPI request body work?",
    "How do I set up GitHub Actions for Python?",
    "Latest updates to Python packaging",
    "Show me code that uses similarity_search",
    "How do I use Docker multi-container setup?",
]

# Example buttons BEFORE text input to avoid session_state conflict
st.caption("Try an example:")
cols = st.columns(len(example_queries))
for i, eq in enumerate(example_queries):
    if cols[i].button(eq[:28] + "…", key=f"ex_{i}"):
        st.session_state.query = eq

# Text input reads from session state
query = st.text_input(
    "Ask a software engineering question:",
    placeholder="e.g. How does FastAPI request body work?",
    value=st.session_state.query
)

# ── Ask button ────────────────────────────────────────────────────────────────
ask = st.button("Ask", type="primary", disabled=not query)

if ask and query:

    # ── Trace panel ───────────────────────────────────────────────────────────
    st.markdown("### 🔍 Agent Trace")
    trace_container = st.container()

    step_icons = {
        "planner":     "🧠 Planner",
        "rag":         "📚 RAG Agent",
        "code":        "🔍 Code Agent",
        "search":      "🌐 Search Agent",
        "synthesiser": "✍️  Synthesiser",
    }

    with trace_container:
        with st.spinner("Running agents..."):
            try:
                resp = requests.post(
                    f"{API_URL}/query",
                    json={"query": query},
                    timeout=60
                )
                data = resp.json()
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend. Make sure `uvicorn main:app --reload` is running.")
                st.stop()
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()

        # Replay trace with true step-by-step animation
        trace = data.get("trace", [])
        done_events = [e for e in trace if e["status"] == "done"]

        # Pre-create one placeholder per step
        placeholders = [st.empty() for _ in done_events]

        for i, event in enumerate(done_events):
            step  = event["step"]
            label = step_icons.get(step, step)
            msg   = event["message"]

            # First show it as "running" (yellow)
            placeholders[i].markdown(
                f'<div class="trace-box trace-running">'
                f'<span class="step-label">{label}</span>'
                f'⏳ {msg}'
                f'</div>',
                unsafe_allow_html=True
            )
            time.sleep(0.6)

            # Then flip to "done" (green)
            placeholders[i].markdown(
                f'<div class="trace-box trace-done">'
                f'<span class="step-label">{label}</span>'
                f'✅ {msg}'
                f'</div>',
                unsafe_allow_html=True
            )
            time.sleep(0.2)

    # ── Answer ────────────────────────────────────────────────────────────────
    st.divider()

    agent_badges = {
        "rag":    ("📚", "RAG Agent"),
        "code":   ("🔍", "Code Agent"),
        "search": ("🌐", "Search Agent"),
    }
    icon, label = agent_badges.get(data.get("routed_to", "rag"), ("🤖", "Agent"))
    st.markdown(f"**Routed to:** {icon} `{label}`")

    st.markdown("### Answer")
    st.markdown(data.get("final_answer", "No answer returned."))

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("Built with LangGraph · ChromaDB · Groq LLaMA 3.3 · FastAPI · Streamlit")