from pathlib import Path

readme_text = """
# 🧠 Document Theme Chatbot (Wasserstoff Gen-AI Internship Project)

An AI-powered document research chatbot that lets you upload multiple documents, ask natural language questions, get document-wise answers with citations, and see synthesized themes across documents — all in a clean chat-style interface.

---

## 🚀 Features

### 📁 Upload & Ingest Documents
- Supports **PDFs**, **image scans (with OCR)**, and **text** files.
- Automatic **text extraction**, **chunking**, and **semantic embedding** using `MiniLM`.
- Stores chunks in **Qdrant** vector database.

### 🔍 Ask Natural Language Questions
- Users can ask any question.
- The system:
  - Searches each document for relevant chunks.
  - Returns **document-wise answers** with page + chunk citations.
  - Generates a **theme summary** that synthesizes insights from top results.

### 🗂️ Smart UI for Querying
- Filters: Document type, upload date, exclusion list, and sort by relevance/newest/oldest.
- Sidebar lets users exclude documents **per query**.
- Results appear in a familiar **chat format**.
- Includes **chunk-level citation highlighting and modals**.

### ✅ Extra Features (for extra credit)
- Paragraph/chunk-level citations: `[DOC001, Page 4, Chunk 2]`
- Document filters + exclusion are dynamic.
- UI shows only matched documents in filter sidebar (just like ChatGPT).
- Popup notifications for upload progress and success.
- Option to **Clear Chat**.
- Latest messages appear closest to input field.

---

## 🛠️ Tech Stack

| Layer       | Tech Used |
|-------------|-----------|
| Frontend    | Next.js, Tailwind CSS, Lucide, TypeScript |
| Backend     | FastAPI (Python), LangChain, HuggingFace, Groq (LLM) |
| Vector DB   | Qdrant |
| OCR         | PyMuPDF / PaddleOCR (for image-based PDFs) |
| LLM         | Groq (LLaMA3-8B) |
| Embeddings  | `sentence-transformers/all-MiniLM-L6-v2` |
| Deployment  | Localhost / Railway / HuggingFace (flexible) |

---

## 🧠 Architecture

