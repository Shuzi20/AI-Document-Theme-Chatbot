from fastapi import FastAPI, File, UploadFile
from app.services.text_extractor import extract_text_from_file
from app.services.embedding_pipeline import process_and_store_text


app = FastAPI()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    text, meta = extract_text_from_file(file.filename, contents)
    return {
        "filename": file.filename,
        "text": text,
        "metadata": meta
    }

@app.get("/test-embedding")
def test_embedding():
    text_by_page = {
        "page_1": "This is a test chunk. Qdrant is a vector search engine.",
        "page_2": "LangChain helps integrate with LLMs like OpenAI or Cohere."
    }
    num_chunks = process_and_store_text("test_doc.pdf", text_by_page)
    return {"status": "success", "chunks_stored": num_chunks}