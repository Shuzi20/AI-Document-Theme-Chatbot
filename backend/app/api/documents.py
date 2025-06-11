from fastapi import APIRouter, HTTPException
from qdrant_client import QdrantClient
from typing import List

router = APIRouter()

qdrant_client = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "documents_collection"

@router.get("/documents", response_model=List[str])
def list_uploaded_documents():
    try:
        collections = qdrant_client.get_collections().collections
        print("[DEBUG] Available collections:", [c.name for c in collections])

        if not any(c.name == COLLECTION_NAME for c in collections):
            print("[DEBUG] Collection does not exist.")
            return []

        scroll_result = qdrant_client.scroll(
            collection_name=COLLECTION_NAME,
            limit=10000,
            with_payload=True
        )

        all_docs = set()
        for point in scroll_result[0]:
            payload = point.payload or {}
            metadata = payload.get("metadata", {})  # ✅ nested field
            doc_name = metadata.get("doc_name")
            if doc_name:
                all_docs.add(doc_name)

        print(f"[DEBUG] Found {len(all_docs)} unique documents.")
        return sorted(all_docs)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
