# ✅ CHUNKING + EMBEDDING + QDRANT STORAGE (LangChain + Qdrant Cloud via Groq)

import os
import uuid
from datetime import datetime
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# 🔧 Load from Environment Variables
QDRANT_HOST = os.getenv("QDRANT_HOST") 
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "documents_collection")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ✅ Lazy-loaded embedding model using Groq (via OpenAI-compatible API)
def get_embedding_model():
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=GROQ_API_KEY,
        openai_api_base="https://api.groq.com/openai/v1"
    )    

# ✅ Lazy-loaded Qdrant client
def get_qdrant_client():
    return QdrantClient(
        url=QDRANT_HOST,
        api_key=QDRANT_API_KEY
    )

# ✅ Create collection if it doesn’t exist
def create_qdrant_collection():
    client = get_qdrant_client()
    model = get_embedding_model()

    if COLLECTION_NAME not in [c.name for c in client.get_collections().collections]:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=len(model.embed_query("test")),
                distance=Distance.COSINE
            )
        )

# 🔍 Simple type inference from filename
def infer_doc_type(filename: str):
    name = filename.lower()
    if "legal" in name:
        return "legal"
    if "report" in name:
        return "report"
    if "policy" in name:
        return "policy"
    return "other"

# ✅ Full pipeline to process & embed document
def process_and_store_text(document_name, text_by_page):
    client = get_qdrant_client()
    embedding_model = get_embedding_model()
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
    metadatas = [doc["metadata"] for doc in valid_docs]

    if not texts:
        print("[WARNING] No valid texts to embed.")
        return 0

    print(f"[DEBUG] Embedding {len(texts)} texts...")

    # 🔔 Explicit manual embedding here (bypass Qdrant.add_texts)
    embeddings = embedding_model.embed_documents(texts)
    print(f"[DEBUG] Got {len(embeddings)} embeddings.")

    # ✅ Manual upsert to Qdrant
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
