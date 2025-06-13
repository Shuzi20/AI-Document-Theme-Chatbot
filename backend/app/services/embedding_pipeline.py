# ✅ CHUNKING + EMBEDDING + QDRANT STORAGE (LangChain)

# File: backend/app/services/embedding_pipeline.py

import os
import uuid
from datetime import datetime
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# 🔧 Configure Paths and Models
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "documents_collection"
MODEL_NAME = "all-MiniLM-L6-v2"  # Fast + free local model

# Load local embedding model
embedding_model = HuggingFaceEmbeddings(model_name=MODEL_NAME)

# Initialize Qdrant client
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# Create collection if not exists
def create_qdrant_collection():
    if COLLECTION_NAME not in [c.name for c in qdrant_client.get_collections().collections]:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=len(embedding_model.embed_query("test")),
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

# Chunk, Embed, and Store Text in Qdrant
def process_and_store_text(document_name, text_by_page):
    create_qdrant_collection()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    documents = []

    now = datetime.utcnow().isoformat()
    flat_doc_name = document_name.strip().lower()

    for page, text in text_by_page.items():
        print(f"[DEBUG] Splitting text from {document_name} - {page}")
        chunks = splitter.split_text(text)
        print(f"[DEBUG] {len(chunks)} chunks from {page}")
        for idx, chunk in enumerate(chunks):
            # Flatten doc_name into metadata for filter compatibility
            documents.append({
                "id": str(uuid.uuid4()),
                "text": chunk,
                "metadata": {
                    "doc_name": flat_doc_name,
                    "doc_type": infer_doc_type(flat_doc_name),  # ✅ NEW
                    "page": page,
                    "chunk_index": idx,
                    "uploaded_at": now
                }
            })

    print(f"[DEBUG] Total chunks to store: {len(documents)}")

    if not documents:
        print("[WARNING] No chunks created. Possible OCR failure or empty document.")
        return 0

    # Convert to LangChain Document format
    langchain_docs = [
        Document(
            page_content=doc["text"],
            metadata=doc["metadata"]
        )
        for doc in documents
    ]

    # Store into Qdrant
    Qdrant.from_documents(
        documents=langchain_docs,
        embedding=embedding_model,
        collection_name=COLLECTION_NAME,
        url=f"http://{QDRANT_HOST}:{QDRANT_PORT}"
    )

    print(f"[DEBUG] Stored {len(langchain_docs)} chunks into Qdrant.")
    return len(langchain_docs)
