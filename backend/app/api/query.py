# File: backend/app/api/query.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from langchain_qdrant import Qdrant
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from groq import Groq
import os
from dotenv import load_dotenv

# 🔐 Load environment variables
load_dotenv()

# ✅ Check Groq API key
if os.getenv("GROQ_API_KEY"):
    print("✅ Groq key loaded.")
else:
    print("❌ GROQ_API_KEY not found. Check your .env file.")

router = APIRouter()

# 📚 Request Model
class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

# 📘 Response Models
class RetrievedChunk(BaseModel):
    text: str
    metadata: Dict[str, Any]
    score: float

class QueryResponse(BaseModel):
    top_chunks: List[RetrievedChunk]
    theme_summary: str

# 🔗 Load embedding model & Qdrant client
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
qdrant_client = QdrantClient(host="localhost", port=6333)

qdrant = Qdrant(
    client=qdrant_client,
    collection_name="documents_collection",
    embeddings=embedding_model
)

# ✨ Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@router.post("/ask", response_model=QueryResponse)
def ask_question(payload: QueryRequest):
    try:
        # Step 1: Vector similarity search
        results = qdrant.similarity_search_with_score(payload.question, k=payload.top_k)

        top_chunks = [
            RetrievedChunk(
                text=doc.page_content,
                metadata=doc.metadata,
                score=score
            ) for doc, score in results
        ]

        # Step 2: Format input for summarization
        docs_for_summary = [f"[{d.metadata['doc_name']}, Page {d.metadata.get('page')}] {d.text}" for d in top_chunks]

        summary_prompt = (
            "You are a helpful AI assistant. Analyze the following excerpts from multiple documents and identify 1–3 key themes. Group supporting citations and explain them clearly.\n\n"
            + "\n\n".join(docs_for_summary)
        )

        # Step 3: Summarize using Groq + LLaMA 3
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful legal summarizer AI."},
                {"role": "user", "content": summary_prompt}
            ],
            temperature=0.4
        )

        theme_summary = response.choices[0].message.content

        return QueryResponse(top_chunks=top_chunks, theme_summary=theme_summary)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
