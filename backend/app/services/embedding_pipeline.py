# ✅ CHUNKING + EMBEDDING + QDRANT STORAGE (Direct Groq API call)

import os
import uuid
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import httpx

# 🔧 Load from Environment Variables
QDRANT_HOST = os.getenv("QDRANT_HOST") 
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "documents_collection")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_EMBEDDING_MODEL = "text-embedding-3-small"

def get_qdrant_client():
    return QdrantClient(
        url=QDRANT_HOST,
        api_key=QDRANT_API_KEY
    )

def get_groq_embeddings(texts: list[str], api_key: str, model: str = GROQ_EMBEDDING_MODEL):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "input": texts
    }
    response = httpx.post(
        "https://api.groq.com/openai/v1/embeddings",
        headers=headers,
        json=payload
    )
    response.raise_for_status()
    data = response.json()
    return [r["embedding"] for r in data["data"]]

def create_qdrant_collection():
    client = get_qdrant_client()
    test_vector = get_groq_embeddings(["test"], GROQ_API_KEY)[0]
    vector_size = len(test_vector)

    if COLLECTION_NAME not in [c.name for c in client.get_collections().collections]:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )

def infer_doc_type(filename: str):
    name = filename.lower()
    if "legal" in name:
        return "legal"
    if "report" in name:
        return "report"
    if "policy" in name:
        return "policy"
    return "other"

def process_and_store_text(document_name, text_by_page):
    client = get_qdrant_client()
    create_qdrant_collection()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    documents = []

    now = datetime.utcnow().isoformat()
    flat_doc_name = document_name.strip().lower()

    for page, text in text_by_page.items():
        chunks = splitter.split_text(text)
        for idx, chunk in enumerate(chunks):
            documents.append({
                "id": str(uuid.uuid4()),
                "text": chunk.strip(),
                "metadata": {
                    "doc_name": flat_doc_name,
                    "doc_type": infer_doc_type(flat_doc_name),
                    "page": page,
                    "chunk_index": idx,
                    "uploaded_at": now
                }
            })

    valid_docs = [doc for doc in documents if doc["text"]]
    texts = [doc["text"] for doc in valid_docs]

    if not texts:
        print("[WARNING] No valid texts to embed.")
        return 0

    print(f"[DEBUG] Embedding {len(texts)} texts...")

    embeddings = get_groq_embeddings(texts, GROQ_API_KEY)
    print(f"[DEBUG] Got {len(embeddings)} embeddings.")

    points = []
    for doc, vector in zip(valid_docs, embeddings):
        points.append({
            "id": doc["id"],
            "vector": vector,
            "payload": {
                "page_content": doc["text"],
                "metadata": doc["metadata"]
            }
        })

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    print(f"[DEBUG] Stored {len(points)} chunks into Qdrant manually.")
    return len(points)
