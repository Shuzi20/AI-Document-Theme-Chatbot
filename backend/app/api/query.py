from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from groq import Groq
import os
from dotenv import load_dotenv
import tiktoken
from uuid import uuid4
from datetime import datetime

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant as QdrantStore

# 🔐 Load environment
load_dotenv()

router = APIRouter()

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
qdrant_client = QdrantClient(host="localhost", port=6333)

qdrant = QdrantStore(
    client=qdrant_client,
    collection_name="documents_collection",
    embeddings=embedding_model
)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class QueryRequest(BaseModel):
    question: str
    top_k: int = 100
    excluded_docs: List[str] = []

@router.post("/ask")
def ask_question(payload: QueryRequest):
    try:
        # Filter logic for excluded docs
        filter_conditions = None
        if payload.excluded_docs:
            filter_conditions = Filter(
                must_not=[
                    FieldCondition(
                        key="metadata.doc_name",
                        match=MatchValue(value=doc)
                    ) for doc in payload.excluded_docs
                ]
            )

        # Vector search
        raw_results = qdrant.similarity_search_with_score(
            payload.question,
            k=payload.top_k,
            filter=filter_conditions
        )

        results = [r for r in raw_results if r[1] > 0.3]
        print(f"[DEBUG] Filtered to {len(results)} relevant chunks")

        if not results:
            return {
                "chat_id": str(uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "question": payload.question,
                "document_answers": [],
                "theme_summary": "No relevant information found."
            }

        # Map doc_name → display ID
        unique_docs = sorted({doc.metadata["doc_name"] for doc, _ in results})
        doc_id_map = {name: f"DOC{str(i+1).zfill(3)}" for i, name in enumerate(unique_docs)}

        doc_map = {}
        top_chunks = []

        for doc, score in results:
            doc_name = doc.metadata["doc_name"]
            page = doc.metadata.get("page", "N/A").replace("page_", "")
            chunk = doc.metadata.get("chunk_index", "?")
            doc_id = doc_id_map[doc_name]

            if doc_id not in doc_map:
                doc_map[doc_id] = {
                    "doc_id": doc_id,
                    "doc_name": doc_name,
                    "answer": doc.page_content,
                    "citation": f"Page {page}, Chunk {chunk}"
                }

            top_chunks.append({
                "doc_id": doc_id,
                "doc_name": doc_name,
                "page": page,
                "chunk_index": chunk,
                "text": doc.page_content
            })

        # Token-limited theme summary
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        MAX_TOKENS = 4800
        total_tokens = 0
        final_chunks = []

        for chunk in top_chunks:
            formatted = f"[{chunk['doc_id']}, Page {chunk['page']}, Chunk {chunk['chunk_index']}] {chunk['text']}"
            token_count = len(encoding.encode(formatted))
            if total_tokens + token_count > MAX_TOKENS:
                break
            final_chunks.append(formatted)
            total_tokens += token_count

        summary_prompt = (
            "You are a helpful AI assistant. Analyze the following excerpts from multiple documents "
            "and identify 1–3 key themes. Group supporting citations by document and explain clearly.\n\n"
            + "\n\n".join(final_chunks)
        )

        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful legal summarizer AI."},
                {"role": "user", "content": summary_prompt}
            ],
            temperature=0.4
        )

        return {
            "chat_id": str(uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "question": payload.question,
            "document_answers": list(doc_map.values()),
            "theme_summary": response.choices[0].message.content,
            "matched_docs": [
                {"doc_id": doc_id, "doc_name": doc_name}
                for doc_name, doc_id in doc_id_map.items()
            ]
        }


    except Exception as e:
        import traceback
        print("[ERROR]", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
