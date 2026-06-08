import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()
RAG_API_URL = os.getenv("RAG_API_URL", "http://127.0.0.1:8000")

def query_with_latency(question: str) -> dict:
    """
    Calls the RAG API and measures response time.
    Returns dict with answer, routed_to, and latency_ms.
    """
    start = time.time()
    try:
        resp = requests.post(
            f"{RAG_API_URL}/query",
            json={"query": question},
            timeout=90
        )
        latency_ms = round((time.time() - start) * 1000, 2)
        data = resp.json()
        return {
            "answer":     data.get("final_answer", ""),
            "routed_to":  data.get("routed_to", "unknown"),
            "latency_ms": latency_ms,
            "error":      None
        }
    except Exception as e:
        latency_ms = round((time.time() - start) * 1000, 2)
        return {
            "answer":     "",
            "routed_to":  "error",
            "latency_ms": latency_ms,
            "error":      str(e)
        }
