import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os
 
st.set_page_config(page_title="LLM Eval Dashboard", page_icon="📊", layout="wide")
st.title("📊 LLM Evaluation Dashboard")
st.caption("Observability framework for RAG pipeline quality")
 
DB_PATH = os.path.join(os.getcwd(), "eval_results.db")
 
# ── Trigger new eval run ──────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown("### Run New Evaluation")
 
if st.sidebar.button("▶ Run Eval (50 questions)", type="primary"):
    st.sidebar.info("Starting eval run... this takes ~8 mins")
 
    import json, uuid, time
    from src.db import init_db, save_result
    from src.evaluators.faithfulness import score_faithfulness
    from src.evaluators.relevance import score_relevance
    from src.evaluators.latency import query_with_latency
 
    init_db()
    with open("src/data/golden_set.json", encoding="utf-8") as f:
        golden_set = json.load(f)
 
    run_id = str(uuid.uuid4())[:8]
    results = []
 
    # ── UI placeholders — created BEFORE the loop ─────────────────────────────
    progress = st.progress(0)
    status   = st.empty()
 
    st.markdown("### Live Metrics")
    live_c1, live_c2, live_c3, live_c4 = st.columns(4)
    m1 = live_c1.empty()
    m2 = live_c2.empty()
    m3 = live_c3.empty()
    m4 = live_c4.empty()
 
    # Initialise metric cards at zero so they show from question 1
    m1.metric("Avg Faithfulness", 0.0)
    m2.metric("Avg Relevance",    0.0)
    m3.metric("Avg Latency",      "0ms")
    m4.metric("Scored so far",    "0/50")
 
    st.divider()
    chart_a, chart_b = st.columns(2)
    with chart_a:
        st.markdown("#### Faithfulness by Topic")
        chart_topic = st.empty()
    with chart_b:
        st.markdown("#### Faithfulness by Difficulty")
        chart_diff = st.empty()
 
    chart_c, chart_d = st.columns(2)
    with chart_c:
        st.markdown("#### Latency Distribution")
        chart_lat = st.empty()
    with chart_d:
        st.markdown("#### Faithfulness vs Latency")
        chart_scatter = st.empty()
 
    # ── Retry helper — retries once on failure ────────────────────────────────
    def query_with_retry(question):
        result = query_with_latency(question)
        if result["error"]:
            time.sleep(2)
            result = query_with_latency(question)
        return result
 
    # ── Main eval loop ────────────────────────────────────────────────────────
    for i, item in enumerate(golden_set, 1):
        progress.progress(i / 50)
        status.markdown(f"**[{i}/50]** `{item['question'][:70]}...`  \n*Querying RAG API...*")
 
        # Query with retry on failure
        result = query_with_retry(item["question"])
 
        if result["error"]:
            status.warning(f"[{i}/50] Skipped — API error: {result['error'][:80]}")
            time.sleep(1)
            continue
 
        status.markdown(f"**[{i}/50]** `{item['question'][:70]}...`  \n*Scoring with LLM judge...*")
 
        faithfulness = score_faithfulness(
            item["question"], item["expected_answer"], result["answer"]
        )
        relevance = score_relevance(item["question"], result["answer"])
 
        save_result(
            run_id=run_id,
            question_id=item["id"],
            question=item["question"],
            topic=item["topic"],
            difficulty=item["difficulty"],
            expected_answer=item["expected_answer"],
            actual_answer=result["answer"],
            routed_to=result["routed_to"],
            faithfulness=faithfulness,
            relevance=relevance,
            latency_ms=result["latency_ms"]
        )
 
        results.append({
            "faithfulness": faithfulness,
            "relevance":    relevance,
            "latency_ms":   result["latency_ms"],
            "topic":        item["topic"],
            "difficulty":   item["difficulty"],
            "question":     item["question"]
        })
 
        # ── Update metric cards after EVERY scored question ───────────────────
        n = len(results)
        avg_f = round(sum(r["faithfulness"] for r in results) / n, 2)
        avg_r = round(sum(r["relevance"]    for r in results) / n, 2)
        avg_l = round(sum(r["latency_ms"]   for r in results) / n, 0)
 
        m1.metric("Avg Faithfulness", avg_f)
        m2.metric("Avg Relevance",    avg_r)
        m3.metric("Avg Latency",      f"{avg_l}ms")
        m4.metric("Scored so far",    f"{n}/50")
 
        status.markdown(f"""
**[{i}/50]** `{item['question'][:60]}...`
 
| Metric | Live Average |
|---|---|
| Faithfulness | `{avg_f}` |
| Relevance | `{avg_r}` |
| Latency | `{avg_l}ms` |
""")
 
        # ── Update charts every 3 questions (consistent interval) ─────────────
        if n % 3 == 0 or i == 50:
            df_live = pd.DataFrame(results)
 
            tf = df_live.groupby("topic")["faithfulness"].mean().reset_index()
            fig1 = px.bar(tf, x="topic", y="faithfulness",
                          color="faithfulness",
                          color_continuous_scale=["#d62728","#ff7f0e","#2ca02c"],
                          range_color=[0,1])
            fig1.update_layout(height=280, margin=dict(t=10,b=10))
            chart_topic.plotly_chart(fig1, use_container_width=True)
 
            dif = df_live.groupby("difficulty")["faithfulness"].mean().reset_index()
            dif["order"] = dif["difficulty"].map({"easy":0,"medium":1,"hard":2})
            dif = dif.sort_values("order")
            fig2 = px.bar(dif, x="difficulty", y="faithfulness",
                          color="faithfulness",
                          color_continuous_scale=["#d62728","#ff7f0e","#2ca02c"],
                          range_color=[0,1])
            fig2.update_layout(height=280, margin=dict(t=10,b=10))
            chart_diff.plotly_chart(fig2, use_container_width=True)
 
            fig3 = px.histogram(df_live, x="latency_ms", nbins=20,
                                color_discrete_sequence=["#1A3C6B"])
            fig3.update_layout(height=280, margin=dict(t=10,b=10))
            chart_lat.plotly_chart(fig3, use_container_width=True)
 
            fig4 = px.scatter(df_live, x="latency_ms", y="faithfulness",
                              color="topic",
                              hover_data=["question","difficulty"])
            fig4.update_layout(height=280, margin=dict(t=10,b=10))
            chart_scatter.plotly_chart(fig4, use_container_width=True)
 
        time.sleep(0.5)
 
    # ── Final summary ─────────────────────────────────────────────────────────
    progress.progress(100)
    if results:
        avg_f = round(sum(r["faithfulness"] for r in results) / len(results), 2)
        avg_r = round(sum(r["relevance"]    for r in results) / len(results), 2)
        avg_l = round(sum(r["latency_ms"]   for r in results) / len(results), 0)
        status.success(
            f"Run {run_id} complete — {len(results)}/50 scored | "
            f"Faithfulness: {avg_f} | Relevance: {avg_r} | Latency: {avg_l}ms"
        )
    else:
        status.error("Run failed — no results scored. Check Project 1 API is running.")
 
    st.cache_data.clear()
    st.rerun()
 
# ── Load data ─────────────────────────────────────────────────────────────────
try:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM eval_results", conn)
    conn.close()
except Exception as e:
    st.error(f"DB Error: {e}")
    st.stop()
 
if df.empty:
    st.warning("No data found. Click Run Eval in the sidebar to start.")
    st.stop()
 
# ── Run selector ──────────────────────────────────────────────────────────────
runs = df["run_id"].unique().tolist()
selected_run = st.sidebar.selectbox("Select eval run:", runs)
df_run = df[df["run_id"] == selected_run].copy()
 
st.sidebar.markdown(f"**Questions:** {len(df_run)}")
st.sidebar.markdown(f"**Run timestamp:** {df_run['timestamp'].min()[:16]}")
 
# ── Metrics ───────────────────────────────────────────────────────────────────
st.markdown("### Overall Metrics")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Avg Faithfulness", round(float(df_run["faithfulness"].mean()), 2))
c2.metric("Avg Relevance",    round(float(df_run["relevance"].mean()), 2))
c3.metric("Avg Latency",      f"{round(float(df_run['latency_ms'].mean()), 0)}ms")
c4.metric("Low Faith (<0.6)", int(len(df_run[df_run["faithfulness"] < 0.6])))
 
st.divider()
 
# ── Charts ────────────────────────────────────────────────────────────────────
ca, cb = st.columns(2)
with ca:
    st.markdown("#### Faithfulness by Topic")
    tf = df_run.groupby("topic")["faithfulness"].mean().reset_index()
    fig1 = px.bar(tf, x="topic", y="faithfulness",
                  color="faithfulness",
                  color_continuous_scale=["#d62728","#ff7f0e","#2ca02c"],
                  range_color=[0,1])
    fig1.update_layout(height=300, margin=dict(t=10,b=10))
    st.plotly_chart(fig1, use_container_width=True)
 
with cb:
    st.markdown("#### Faithfulness by Difficulty")
    dif = df_run.groupby("difficulty")["faithfulness"].mean().reset_index()
    dif["order"] = dif["difficulty"].map({"easy":0,"medium":1,"hard":2})
    dif = dif.sort_values("order")
    fig2 = px.bar(dif, x="difficulty", y="faithfulness",
                  color="faithfulness",
                  color_continuous_scale=["#d62728","#ff7f0e","#2ca02c"],
                  range_color=[0,1])
    fig2.update_layout(height=300, margin=dict(t=10,b=10))
    st.plotly_chart(fig2, use_container_width=True)
 
cc, cd = st.columns(2)
with cc:
    st.markdown("#### Latency Distribution")
    fig3 = px.histogram(df_run, x="latency_ms", nbins=20,
                        color_discrete_sequence=["#1A3C6B"])
    fig3.update_layout(height=300, margin=dict(t=10,b=10))
    st.plotly_chart(fig3, use_container_width=True)
 
with cd:
    st.markdown("#### Faithfulness vs Latency")
    fig4 = px.scatter(df_run, x="latency_ms", y="faithfulness",
                      color="topic",
                      hover_data=["question","difficulty"])
    fig4.update_layout(height=300, margin=dict(t=10,b=10))
    st.plotly_chart(fig4, use_container_width=True)
 
st.divider()
 
# ── Worst performing ──────────────────────────────────────────────────────────
st.markdown("#### Worst Performing Questions (Faithfulness < 0.6)")
worst = df_run[df_run["faithfulness"] < 0.6].sort_values("faithfulness")
 
if worst.empty:
    st.success("No low-faithfulness answers in this run!")
else:
    for _, row in worst.iterrows():
        with st.expander(f"[{row['faithfulness']}] {row['question'][:80]}"):
            st.markdown(f"**Topic:** {row['topic']}  |  **Difficulty:** {row['difficulty']}")
            st.markdown(f"**Faithfulness:** {row['faithfulness']}  |  **Relevance:** {row['relevance']}  |  **Latency:** {row['latency_ms']}ms")
            st.info(row["actual_answer"])
 
st.divider()
 
# ── Full results table ────────────────────────────────────────────────────────
st.markdown("#### All Results")
st.dataframe(
    df_run[["question_id","question","topic","difficulty",
            "faithfulness","relevance","latency_ms","routed_to"]]
    .sort_values("faithfulness"),
    use_container_width=True,
    height=400
)
