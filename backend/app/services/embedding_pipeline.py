# ✅ CHUNKING + EMBEDDING + QDRANT STORAGE (Hugging Face Spaces ready with sentence-transformers)

import os
import uuid
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# 🔧 Load from Environment Variables
QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "documents_collection")

# ✅ Load SentenceTransformer model globally (efficient for HF Spaces)
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def get_qdrant_client():
    return QdrantClient(
        url=QDRANT_HOST,
        api_key=QDRANT_API_KEY
    )

def create_qdrant_collection():
    client = get_qdrant_client()
    vector_size = embedding_model.get_sentence_embedding_dimension()

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
        print(f"[DEBUG] Splitting text from {document_name} - Page {page}")
        chunks = splitter.split_text(text)
        print(f"[DEBUG] {len(chunks)} chunks from Page {page}")
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

    print(f"[DEBUG] Total chunks to store: {len(documents)}")

    if not documents:
        print("[WARNING] No chunks created. Possible OCR failure or empty document.")
        return 0

    valid_docs = [doc for doc in documents if doc["text"]]
    texts = [doc["text"] for doc in valid_docs]

    print(f"[DEBUG] Embedding {len(texts)} texts...")

    embeddings = embedding_model.encode(texts, normalize_embeddings=True).tolist()
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
