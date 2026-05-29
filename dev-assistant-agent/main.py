from fastapi import FastAPI
from pydantic import BaseModel
from src.graph import agent_graph

app = FastAPI(title="Dev Assistant Multi-Agent System")


class QueryRequest(BaseModel):
    query: str


@app.get("/")
def home():
    return {"message": "Multi-Agent AI System Running", "status": "ok"}


@app.post("/query")
def query(request: QueryRequest):
    result = agent_graph.invoke({
        "query":        request.query,
        "route":        "",
        "agent_output": "",
        "final_answer": "",
        "trace":        []
    })
    return {
        "query":        result["query"],
        "routed_to":    result["route"],
        "trace":        result["trace"],
        "final_answer": result["final_answer"]
    }