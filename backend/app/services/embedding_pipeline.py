import os
import uuid
from datetime import datetime

# ✅ Only keep lightweight modules at top
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# 🔧 Load from Environment Variables
QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "documents_collection")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# ✅ Lazy import inside function
def get_embedding_model():
    from langchain_community.embeddings import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name=MODEL_NAME)

def get_qdrant_client():
    from qdrant_client import QdrantClient
    return QdrantClient(url=QDRANT_HOST, api_key=QDRANT_API_KEY)

def create_qdrant_collection():
    from qdrant_client.models import VectorParams, Distance
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
    from langchain_community.vectorstores import Qdrant

    client = get_qdrant_client()
    model = get_embedding_model()
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
                "text": chunk,
                "metadata": {
                    "doc_name": flat_doc_name,
                    "doc_type": infer_doc_type(flat_doc_name),
                    "page": page,
                    "chunk_index": idx,
                    "uploaded_at": now
                }
            })

    if not documents:
        return 0

    langchain_docs = [
        Document(
            page_content=doc["text"],
            metadata=doc["metadata"]
        )
        for doc in documents
    ]

    Qdrant.from_documents(
        documents=langchain_docs,
        embedding=model,
        collection_name=COLLECTION_NAME,
        client=client
    )

    return len(langchain_docs)
