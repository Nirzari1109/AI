import os, requests, hashlib
from pathlib import Path
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from src.utils.embeddings import ONNXEmbeddings
from dotenv import load_dotenv

load_dotenv()

# Public documentation URLs we'll ingest
DOC_SOURCES = [
    # GitHub Actions docs
    "https://docs.github.com/en/actions/writing-workflows/quickstart",
    "https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions",
    # Python packaging
    "https://packaging.python.org/en/latest/tutorials/packaging-projects/",
    # FastAPI
    "https://fastapi.tiangolo.com/tutorial/first-steps/",
    "https://fastapi.tiangolo.com/tutorial/path-params/",
    "https://fastapi.tiangolo.com/tutorial/body/",
    # Docker
    "https://docs.docker.com/get-started/02_our_app/",
    "https://docs.docker.com/get-started/07_multi_container/",
]

def fetch_page_text(url: str) -> str:
    """Fetch and clean text from a documentation page."""
    headers = {"User-Agent": "Mozilla/5.0 (educational project)"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        # Remove nav, footer, script, style noise
        for tag in soup(["nav", "footer", "script", "style", "header"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return ""

def build_vectorstore(persist_dir: str = ".chroma"):
    """Fetch all docs, chunk them, embed and store in ChromaDB."""
    print("Fetching documentation pages...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    all_chunks = []
    all_metas  = []

    for url in DOC_SOURCES:
        print(f"  → {url}")
        text = fetch_page_text(url)
        if not text:
            continue
        chunks = splitter.split_text(text)
        all_chunks.extend(chunks)
        all_metas.extend([{"source": url}] * len(chunks))

    print(f"\nTotal chunks: {len(all_chunks)}")
    print("Embedding and storing in ChromaDB (this takes ~1 min)...")

    vectorstore = Chroma.from_texts(
        texts=all_chunks,
        metadatas=all_metas,
        embedding=ONNXEmbeddings(),
        persist_directory=persist_dir,
    )
    print("Done. Vector store saved to", persist_dir)
    return vectorstore

if __name__ == "__main__":
    build_vectorstore()