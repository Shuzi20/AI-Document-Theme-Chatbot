import io
import pdfplumber
from PIL import Image
import pytesseract

def extract_text_from_file(filename, content_bytes):
    extension = filename.split(".")[-1].lower()
    if extension == "pdf":
        return extract_text_from_pdf(content_bytes)
    elif extension in ["png", "jpg", "jpeg"]:
        return extract_text_from_image(content_bytes)
    else:
        return "Unsupported file type", {}

def extract_text_from_pdf(file_bytes):
    text = ""
    meta = {}
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n\n[Page {i+1}]\n" + page_text
                meta[f"page_{i+1}"] = len(page_text)
    return text, meta

def extract_text_from_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(image)
    return text, {"ocr": True}
