#from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from src.utils.embeddings import ONNXEmbeddings

embedding_fn = ONNXEmbeddings()

db = Chroma(
    persist_directory=".chroma",
    embedding_function=embedding_fn
)

docs = db.similarity_search("FastAPI request body", k=2)

for i, doc in enumerate(docs, 1):
    print(f"\n--- DOC {i} ---")
    print("SOURCE:", doc.metadata)
    print(doc.page_content[:500])
