from langchain_chroma import Chroma
from src.utils.embeddings import ONNXEmbeddings
from src.utils.llm import ask_claude

class RAGAgent:

    def __init__(self):
        self.db = Chroma(
            persist_directory=".chroma",
            embedding_function=ONNXEmbeddings()
        )

    def run(self, query):

        docs = self.db.similarity_search(query, k=3)

        # return "\n\n".join([
        #     d.page_content[:600]
        #     for d in docs
        # ])
        context = "\n\n".join([
            d.page_content[:500]
            for d in docs
        ])

        prompt = f"""
        Answer the user's question using the context below.

        QUESTION:
        {query}

        CONTEXT:
        {context}

        Provide a clean concise answer.
        """

        answer = ask_claude(prompt)

        return answer

if __name__ == "__main__":

    agent = RAGAgent()

    result = agent.run(
        "How does FastAPI request body work?"
    )

    print(result)