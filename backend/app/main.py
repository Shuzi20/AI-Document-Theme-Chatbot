from typing import List
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from app.services.text_extractor import extract_text_from_file
from app.services.embedding_pipeline import process_and_store_text
from app.api import query
from fastapi import Request

app = FastAPI()

# ✅ Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload/")
async def upload_files(request: Request):
    form = await request.form()
    files = [v for v in form.values() if isinstance(v, UploadFile)]
    

    results = []
    print(f"Received {len(files)} files")
    for file in files:
        contents = await file.read()
        text, meta = extract_text_from_file(file.filename, contents)

        text_by_page = {}
        for line in text.split('\n\n'):
            if line.strip().startswith('[Page'):
                parts = line.strip().split(']\n', 1)
                if len(parts) == 2:
                    page_label = "page_" + parts[0].split('Page')[-1].strip()
                    text_by_page[page_label] = parts[1]

        chunks_stored = process_and_store_text(file.filename, text_by_page)

        results.append({
            "filename": file.filename,
            "pages": len(text_by_page),
            "chunks_stored": chunks_stored
        })

    return {"uploaded": results}

@app.get("/test-embedding")
def test_embedding():
    text_by_page = {
        "page_1": "This is a test chunk. Qdrant is a vector search engine.",
        "page_2": "LangChain helps integrate with LLMs like OpenAI or Cohere."
    }
    num_chunks = process_and_store_text("test_doc.pdf", text_by_page)
    return {"status": "success", "chunks_stored": num_chunks}

app.include_router(query.router)
