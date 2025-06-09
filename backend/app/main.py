from fastapi import FastAPI, File, UploadFile
from app.services.text_extractor import extract_text_from_file
from app.services.embedding_pipeline import process_and_store_text
from app.api import query


app = FastAPI()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    text, meta = extract_text_from_file(file.filename, contents)
    
    # 👉 Convert meta back to full text-by-page format
    text_by_page = {}
    for line in text.split('\n\n'):
        if line.strip().startswith('[Page'):
            parts = line.strip().split(']\n', 1)
            if len(parts) == 2:
                page_label = "page_" + parts[0].split('Page')[-1].strip()
                text_by_page[page_label] = parts[1]

    chunks_stored = process_and_store_text(file.filename, text_by_page)

    return {
        "filename": file.filename,
        "text": text,
        "metadata": meta,
        "chunks_stored": chunks_stored
    }


@app.get("/test-embedding")
def test_embedding():
    text_by_page = {
        "page_1": "This is a test chunk. Qdrant is a vector search engine.",
        "page_2": "LangChain helps integrate with LLMs like OpenAI or Cohere."
    }
    num_chunks = process_and_store_text("test_doc.pdf", text_by_page)
    return {"status": "success", "chunks_stored": num_chunks}


app.include_router(query.router)
