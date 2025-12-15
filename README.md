# SAI1_RAG-Bot

# AI Reading Assistant (RAG + Project Gutenberg)
  
This project combines **Project Gutenberg** texts with an **AI Reading Assistant** that can **summarize**, **answer questions grounded in the book (RAG)**, and **generate quizzes**.

Please be aware that this is a prototype and thus not yet dockerized or hosted. You will need to clone the repo and start it manually. 

---

## ✨ Features

### 📖 Reading & Learning Tools
- **Free summary**: paste any text and get a summary
- **Book Q&A (RAG)**: ask questions and get answers **based only on the retrieved book passages**
- **Quiz generator**: create flashcard-style Q&A pairs from a selected book

### 📚 Project Gutenberg Integration
- Search and import books from **Project Gutenberg** (via Gutendex)
- Imported books are saved locally and indexed into the vector database automatically

### 🧠 Retrieval-Augmented Generation (RAG)
- Books are split into chunks
- Chunks are embedded and stored in a **ChromaDB** vector store
- For each question, the most relevant chunks are retrieved and passed to the model

---

## 🧩 Tech Stack

### Backend
- **FastAPI** (Python)
- **OpenAI API** (e.g. `gpt-4o-mini`)
- **ChromaDB** (persistent vector database)
- **SentenceTransformers** (`all-MiniLM-L6-v2`) for embeddings
- **httpx** for Gutenberg/Gutendex requests

### Frontend
- **React + TypeScript** (Vite)
- Simple card-based UI
- Sidebar explaining Project Gutenberg + RAG

### How to start up the prototype

Pre-Reqs:
- Git
- Python 3.11

PS:
1. git clone https://github.com/CarloRoethlisberger/SAI1_RAG-Bot.git

2. cd SAI1_RAG-Bot
3. cd backend
4. python -m venv venv
5. venv\Scripts\Activate.ps1
6. Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
7. venv\Scripts\Activate.ps1
8. pip install --upgrade pip
9. pip install fastapi uvicorn "uvicorn[standard]" chromadb sentence-transformers openai httpx python-dotenv

OPENAI_API_KEY=your_key_here

From the Backend Folder: 
python -m uvicorn main:app --reload

The backend is now running. Now switch to the frontend directory. 

1. npm install
2. npm run dev
3. Visit the displayed localhost URL in the browser