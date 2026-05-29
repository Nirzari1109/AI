from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()


class SearchAgent:

    def __init__(self):

        self.client = TavilyClient(
            api_key=os.getenv(
                "TAVILY_API_KEY"
            )
        )

    def run(self, query):

        result = self.client.search(
            query=query
        )

        return result


if __name__ == "__main__":

    agent = SearchAgent()

    result = agent.run(
        "Latest FastAPI updates"
    )

    print(result)
