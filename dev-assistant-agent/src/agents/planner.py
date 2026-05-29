from src.agents.rag_agent import RAGAgent
from src.agents.code_agent import CodeAgent
from src.agents.search_agent import SearchAgent


class Planner:

    def __init__(self):

        self.rag=RAGAgent()
        self.code=CodeAgent()
        self.web=SearchAgent()

    def route(self, query):

        print("\nPlanner running...")
        print("QUERY RECEIVED:", query)

        q = query.lower()

        if "code" in q:

            print("→ Using CodeAgent")

            return self.code.run(query)

        elif any(word in q for word in [
            "latest",
            "news",
            "recent",
            "update"
        ]):

            print("→ Using SearchAgent")

            return self.web.run(query)

        else:

            print("→ Using RAGAgent")

            return self.rag.run(query)
        
if __name__ == "__main__":

    planner = Planner()

    result = planner.route(
        "latest FastAPI updates"
    )

    print(result)