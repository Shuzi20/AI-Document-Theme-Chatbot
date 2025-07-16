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
    model = get_embedding_model()
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

    # ✅ Final safe conversion: only valid non-empty strings go into embedding
    langchain_docs = []
    for doc in documents:
        text = doc.get("text", "")
        if isinstance(text, str):
            text = text.strip()
        if not text:
            continue
        langchain_docs.append(
            Document(
                page_content=text,
                metadata=doc["metadata"]
            )
        )

    print(f"[DEBUG] Valid langchain_docs: {len(langchain_docs)}")
    if langchain_docs:
        print(f"[DEBUG] First chunk for embedding: {langchain_docs[0].page_content[:100]}")

    # ✅ Extract raw text + metadata and sanitize inputs
    texts = []
    for doc in langchain_docs:
        raw = doc.page_content

        if not isinstance(raw, str):
            print(f"[WARNING] Skipped non-string content: {type(raw)}")
            continue

        cleaned = str(raw).replace("\n", " ").replace("\r", " ").strip()

        if not cleaned or not isinstance(cleaned, str):
            print(f"[WARNING] Skipped empty or invalid cleaned chunk: {repr(raw)}")
            continue

        texts.append(cleaned)


    metadatas = [doc.metadata for doc in langchain_docs][:len(texts)]

    print(f"[DEBUG] Final embedding input preview: {texts[:1]}")
    print(f"[DEBUG] Embedding {len(texts)} texts...")

    qdrant = Qdrant(
        client=client,
        collection_name=COLLECTION_NAME,
        embeddings=model
    )

    qdrant.add_texts(
        texts=texts,
        metadatas=metadatas
    )

    print(f"[DEBUG] Stored {len(texts)} chunks into Qdrant.")
    return len(texts)
