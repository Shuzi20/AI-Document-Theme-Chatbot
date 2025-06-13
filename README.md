📚 Document Theme Chatbot – Wasserstoff Gen-AI Internship Task
This project is a document research and theme identification chatbot built for the Wasserstoff Generative AI Internship Qualification Task. It allows users to upload documents (PDF, scanned images, text), ask questions in natural language, and receive cited answers and theme-based summaries using LLMs and vector search.

🔍 Features
✅ Core Functionality
Upload 75+ documents (PDFs, scans, text)

OCR support for scanned image PDFs using PyMuPDF + optional fallback

Chunking + Embedding with LangChain + MiniLM and storage in Qdrant

Ask natural questions – semantic search returns relevant text chunks

Document-level answers – with citations (Document ID, Page, Chunk)

Theme-based summarization – synthesized LLM summary grouped by theme

Filters: by date, document type, exclusion list, sort order

🎯 Extra Credit Implemented
✅ Paragraph/Chunk-level citation (e.g., Page 3, Chunk 2)

✅ Clickable citations in chat (modal view)

✅ Filter by matched docs only

✅ Re-run query on selected subset of docs

✅ Sidebar filters: exclude, sort by relevance/date

✅ Modern assistant-style chat UI with:

Upload & loading states

Clear chat option

LocalStorage chat history

Newest message appears near input bar (like ChatGPT)

🧠 Tech Stack
Layer	Tooling
Frontend	Next.js 14 + Tailwind CSS
Backend	FastAPI
LLM	Groq + LLaMA 3 (8B)
Embeddings	HuggingFace MiniLM
Vector DB	Qdrant
OCR	PyMuPDF (fitz)
Deployment	(Local Dev) – Easily deployable on Hugging Face, Render, Railway

🧪 How It Works
Document Upload

Extracts text from each page.

Splits into overlapping chunks.

Embeds using HuggingFace MiniLM.

Stores with metadata in Qdrant.

Asking a Question

Question is embedded and searched in Qdrant.

Top-k chunks are retrieved (filtered by user criteria).

Each chunk is cited (DOC ID, Page, Chunk).

A Groq LLaMA-3 model summarizes the top chunks into themes.

Frontend Display

Shows individual document answers (tabular).

Theme summary in chat format.

Clickable citation links to view source chunk.

Sidebar filters and exclusions applied dynamically.

📦 Project Structure
mathematica
Copy
Edit
chatbot-theme-identifier/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── query.py         ← Main QA logic
│   │   │   ├── query_filters.py ← Filtering logic
│   │   │   └── documents.py     ← List uploaded docs
│   │   ├── services/
│   │   │   ├── text_extractor.py
│   │   │   └── embedding_pipeline.py
│   │   └── main.py              ← FastAPI entrypoint
├── frontend/ (Next.js project)
│   └── app/index/page.tsx      ← Core UI
├── data/                       ← Optional: sample docs
└── README.md
🚀 Running Locally
1. Clone + Install
bash
Copy
Edit
git clone https://github.com/yourname/document-theme-chatbot
cd document-theme-chatbot/backend
pip install -r requirements.txt
2. Start Backend
bash
Copy
Edit
# Start Qdrant
docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant

# Start FastAPI
uvicorn app.main:app --reload
3. Start Frontend (Next.js)
bash
Copy
Edit
cd frontend
npm install
npm run dev
🎥 Demo Preview
📄 Upload documents

🧠 Ask “What is the main topic discussed?”

📌 See:

Per-document citations

Synthesized theme answers

Filter, re-run, clear history

Document match map

