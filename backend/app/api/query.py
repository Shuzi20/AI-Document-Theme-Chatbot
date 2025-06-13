from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Literal
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from groq import Groq
import os
from dotenv import load_dotenv
import tiktoken
from uuid import uuid4
from datetime import datetime

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant as QdrantStore
from app.api.query_filters import build_query_filter  # ✅ <-- imported here

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
    sort_by: Literal["relevance", "newest", "oldest"] = "relevance"
    doc_type: str = None
    date_after: str = None  # ISO format (e.g., "2025-06-01")
    date_before: str = None

@router.post("/ask")
def ask_question(payload: QueryRequest):
    try:
        # ✅ Build advanced filters
        filter_conditions = build_query_filter(
            excluded_docs=payload.excluded_docs,
            doc_type=payload.doc_type,
            date_after=payload.date_after,
            date_before=payload.date_before
        )

        embedded_query = embedding_model.embed_query(payload.question)

        search_result = qdrant_client.search(
            collection_name="documents_collection",
            query_vector=embedded_query,
            limit=payload.top_k,
            score_threshold=0.3,
            with_payload=True,
            query_filter=filter_conditions
        )

        for r in search_result:
            print("[DEBUG] Payload sample:", r.payload)
        print(f"[DEBUG] Retrieved {len(search_result)} results after filtering")

        if not search_result:
            return {
                "chat_id": str(uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "question": payload.question,
                "document_answers": [],
                "theme_summary": "No relevant information found."
            }

        raw_results = [
            (
                Document(
                    page_content=hit.payload.get("page_content", ""),
                    metadata=hit.payload.get("metadata", {})
                ),
                hit.score
            )
            for hit in search_result
        ]

        if payload.sort_by == "newest":
            raw_results.sort(key=lambda r: r[0].metadata.get("uploaded_at", ""), reverse=True)
        elif payload.sort_by == "oldest":
            raw_results.sort(key=lambda r: r[0].metadata.get("uploaded_at", ""))

        unique_docs = sorted({doc.metadata["doc_name"] for doc, _ in raw_results})
        doc_id_map = {name: f"DOC{str(i+1).zfill(3)}" for i, name in enumerate(unique_docs)}

        doc_map = {}
        top_chunks = []

        for doc, score in raw_results:
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

        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        MAX_TOKENS = 4800
        total_tokens = 0
        final_chunks = []

        for chunk in top_chunks:
            if not chunk.get("text") or not chunk["text"].strip():
                print("[SKIP] Empty or invalid chunk:", chunk)
                continue

            formatted = f"[{chunk['doc_id']}, Page {chunk['page']}, Chunk {chunk['chunk_index']}] {chunk['text']}"
            token_count = len(encoding.encode(formatted))

            if total_tokens + token_count > MAX_TOKENS:
                break

            final_chunks.append(formatted)
            total_tokens += token_count

        print(f"[DEBUG] Final chunks for theme summary: {len(final_chunks)}")

        if not final_chunks:
            return {
                "chat_id": str(uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "question": payload.question,
                "document_answers": list(doc_map.values()),
                "theme_summary": "⚠️ No valid excerpts found to generate themes."
            }

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
            "theme_summary": response.choices[0].message.content
        }

    except Exception as e:
        import traceback
        print("[ERROR]", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
