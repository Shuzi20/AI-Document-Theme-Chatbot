from fastapi import FastAPI, File, UploadFile
from app.text_extractor import extract_text_from_file

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
