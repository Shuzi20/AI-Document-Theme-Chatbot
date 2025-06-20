from typing import List
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from app.services.text_extractor import extract_text_from_file
from app.services.embedding_pipeline import process_and_store_text
from app.api import query
from app.api import documents
from fastapi.responses import HTMLResponse
import re

app = FastAPI()

# ✅ Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update this if deployed frontend uses a different domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    print(f"Received {len(files)} files")
    results = []

    for file in files:
        contents = await file.read()
        text, meta = extract_text_from_file(file.filename, contents)

        print(f"[DEBUG] Raw extracted text length: {len(text) if isinstance(text, str) else 'dict'}")

        # ✅ Adapt based on type of `text`
        text_by_page = {}
        if isinstance(text, dict):
            text_by_page = text
        elif isinstance(text, str):
            pages = re.findall(r"\[Page (\d+)]\n(.*?)(?=\n\[Page \d+]|\Z)", text, re.DOTALL)
            for page_num, page_text in pages:
                label = f"page_{page_num}"
                cleaned = page_text.strip()
                text_by_page[label] = cleaned
                print(f"[DEBUG] Extracted {len(cleaned)} characters from {label}")

        chunks_stored = process_and_store_text(file.filename, text_by_page)

        results.append({
            "filename": file.filename,
            "pages": len(text_by_page),
            "chunks_stored": chunks_stored
        })

    return {"uploaded": results}

# ❌ Removed create_qdrant_collection() from startup to reduce memory usage

@app.get("/test-embedding")
def test_embedding():
    text_by_page = {
        "page_1": "This is a test chunk. Qdrant is a vector search engine.",
        "page_2": "LangChain helps integrate with LLMs like OpenAI or Cohere."
    }
    num_chunks = process_and_store_text("test_doc.pdf", text_by_page)
    return {"status": "success", "chunks_stored": num_chunks}

# ✅ Health check for Render
@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# ✅ Include main routers
app.include_router(query.router)
app.include_router(documents.router)

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head><title>Document Theme Chatbot</title></head>
        <body style="font-family: sans-serif;">
            <h2>🚀 Document Theme Chatbot Backend is Live!</h2>
            <p>This FastAPI backend is now running.</p>
            <p>Use <code>/upload</code> or <code>/query</code> to interact with the API.</p>
        </body>
    </html>
    """
