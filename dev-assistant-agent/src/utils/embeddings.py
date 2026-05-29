from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
from langchain_core.embeddings import Embeddings


class ONNXEmbeddings(Embeddings):

    def __init__(self):
        self.model = ONNXMiniLM_L6_V2()

    def embed_documents(self, texts):
        return self.model(texts)

    def embed_query(self, text):
        return self.model([text])[0]