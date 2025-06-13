
# 📚 Document Theme Chatbot – Wasserstoff Gen-AI Internship Task

This project is a **Document Research and Theme Identification Chatbot** built as part of the **Wasserstoff Generative AI Internship Qualification Task**. It enables users to upload a wide range of documents (PDFs, text, scanned images), ask natural language questions, and receive document-cited answers and theme-based summaries using LLMs and vector search.

---

## 🔍 Features

### ✅ Core Functionality

- Upload **75+ documents** (PDF, scans, text)
- **OCR support** for scanned PDFs using PyMuPDF
- Chunking + embedding using **LangChain + MiniLM**
- Vector storage in **Qdrant**
- **Semantic search** to retrieve top matching document chunks
- Answers include:
  - **Document ID**
  - **Page number**
  - **Chunk number**
- Theme-based summarization using **Groq + LLaMA 3**
- Advanced filtering:
  - **By date**
  - **By document type**
  - **By inclusion/exclusion**
  - **Sort by relevance/newest/oldest**

---

### 🎯 Extra Credit Implemented

- ✅ **Paragraph/Chunk-level citations** (e.g., *Page 3, Chunk 2*)
- ✅ **Clickable citations** inside chat that show chunk modal
- ✅ **Filter sidebar** shows only matched documents
- ✅ **Re-run** query on selected subset of docs
- ✅ Sidebar filters: exclude, sort, type, date
- ✅ Modern UI features:
  - Upload & loading states
  - **Clear Chat** option
  - **Chat history persisted** in localStorage
  - Chat-style flow with **latest message near input**, like ChatGPT

---

## 🧠 Tech Stack

| Layer     | Tooling                       |
|-----------|-------------------------------|
| Frontend  | Next.js 14, Tailwind CSS      |
| Backend   | FastAPI                       |
| LLM       | Groq API + LLaMA 3 (8B)       |
| Embedding | HuggingFace `all-MiniLM-L6-v2`|
| Vector DB | Qdrant                        |
| OCR       | PyMuPDF (fitz)                |
| Deployment| (Local Dev) – HuggingFace, Render, Railway supported |

---

## 🧪 How It Works

### 🔹 Document Upload
- Extract text from each page (OCR if needed)
- Split into overlapping chunks
- Embed using `MiniLM`
- Store in Qdrant with metadata:
  - doc_name, page, chunk_index, uploaded_at

### 🔹 Asking a Question
- Embed user question
- Search top-k relevant chunks in Qdrant
- Return each with doc ID, page, chunk
- Generate LLM summary using Groq LLaMA-3

### 🔹 Frontend Display
- Shows document answer table
- Synthesized theme summary
- Clickable references to exact chunks
- Filter sidebar allows re-querying with refined criteria

---

## 📦 Project Structure


chatbot-theme-identifier/
├── backend/
│ ├── app/
│ │ ├── api/
│ │ │ ├── query.py ← Main QA logic
│ │ │ ├── query_filters.py ← Filtering logic
│ │ │ └── documents.py ← List uploaded docs
│ │ ├── services/
│ │ │ ├── text_extractor.py
│ │ │ └── embedding_pipeline.py
│ │ └── main.py ← FastAPI entrypoint
├── frontend/ (Next.js 14)
│ └── app/index/page.tsx ← Core Chat UI
├── data/ ← Optional: test documents
└── README.md


---

## 🚀 Running Locally

### 1️⃣ Clone & Install

```bash
git clone https://github.com/yourname/document-theme-chatbot
cd document-theme-chatbot/backend
pip install -r requirements.txt

2️⃣ Start Backend
# Start Qdrant (requires Docker)
docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant

# Start FastAPI server
uvicorn app.main:app --reload


3️⃣ Start Frontend
cd ../document-theme-chatbot
npm install
npm run dev

App runs at http://localhost:3000 and connects to backend on http://localhost:8000

✅ Setup via Docker 
To run Qdrant locally without manual installation, use the included docker-compose.yml.

1️⃣ Add docker-compose.yml at the project root:
yaml
Copy
Edit
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant
    container_name: qdrant
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant_storage:/qdrant/storage
This will:

Pull the official Qdrant image

Expose it on localhost:6333

Mount a local qdrant_storage/ directory to persist vector data

2️⃣ Create storage folder (optional)
bash
Copy
Edit
mkdir qdrant_storage
3️⃣ Start Qdrant service
bash
Copy
Edit
docker-compose up -d
4️⃣ Confirm it’s running
Visit: http://localhost:6333

Your FastAPI backend connects automatically using:

python
Copy
Edit
QdrantClient(host="localhost", port=6333)


🎥 Demo Preview
📝 Upload documents
Drag and drop PDFs or images (OCR supported)

💬 Ask a question
Example: "What is the penalty mentioned in each compliance file?"

📊 See answers:
Extracted text with DOC ID, Page, Chunk

Synthesized themes grouped across documents

Filter results by type/date/exclusion

Click chunk references to read source
