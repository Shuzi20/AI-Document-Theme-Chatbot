import io
import shutil
from pathlib import Path
from PIL import Image
import pytesseract
import pdfplumber


# 🔧 Try dynamic detection or fallback to default install location
pytesseract.pytesseract.tesseract_cmd = (
    shutil.which("tesseract") or r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# 🛡️ Optional: verify it actually works
if not shutil.which("tesseract") and not Path(pytesseract.pytesseract.tesseract_cmd).exists():
    raise EnvironmentError("❌ Tesseract OCR is not installed or not found in system PATH.")


def extract_text_from_file(filename, content_bytes):
    extension = filename.split(".")[-1].lower()
    if extension == "pdf":
        return extract_text_from_pdf(content_bytes)
    elif extension in ["png", "jpg", "jpeg"]:
        return extract_text_from_image(content_bytes)
    else:
        return {}, {"error": "Unsupported file type"}


def extract_text_from_pdf(file_bytes):
    page_dict = {}
    meta = {}

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            page_num = f"page_{i+1}"
            if page_text:
                page_dict[page_num] = page_text
                meta[page_num] = len(page_text)

    return page_dict, meta



def extract_text_from_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(image)
    return {"page_1": text}, {"ocr": True}
