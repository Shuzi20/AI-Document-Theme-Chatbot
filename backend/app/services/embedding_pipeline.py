# ✅ CHUNKING + EMBEDDING + QDRANT STORAGE (LangChain + Qdrant Cloud)

import os
import uuid
from datetime import datetime
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# 🔧 Load from Environment Variables (Cloud-Safe)
QDRANT_HOST = os.getenv("QDRANT_HOST")  # e.g. https://your-cluster.aws.cloud.qdrant.io
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "documents_collection")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"  # public cloud-safe model

# ✅ Initialize embedding model
embedding_model = HuggingFaceEmbeddings(model_name=MODEL_NAME)

# ✅ Initialize Qdrant Cloud Client with API Key
qdrant_client = QdrantClient(
    url=QDRANT_HOST,
    api_key=QDRANT_API_KEY
)

# ✅ Create collection if it doesn’t exist
def create_qdrant_collection():
    if COLLECTION_NAME not in [c.name for c in qdrant_client.get_collections().collections]:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=len(embedding_model.embed_query("test")),
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
                "text": chunk,
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

    langchain_docs = [
        Document(
            page_content=doc["text"],
            metadata=doc["metadata"]
        )
        for doc in documents
    ]

    # ✅ Store documents in Qdrant Cloud
    Qdrant.from_documents(
        documents=langchain_docs,
        embedding=embedding_model,
        collection_name=COLLECTION_NAME,
        client=qdrant_client
    )

    print(f"[DEBUG] Stored {len(langchain_docs)} chunks into Qdrant.")
    return len(langchain_docs)
