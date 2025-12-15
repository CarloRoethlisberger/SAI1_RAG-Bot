# backend/main.py

import os
import httpx
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel

from rag import retrieve_context, index_book
from summary import generate_summary
from quiz import generate_quiz
from upload import save_book_file


# .env laden
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("OPENAI_API_KEY ist nicht gesetzt (.env prüfen)")

client = OpenAI(api_key=api_key)

app = FastAPI(
    title="AI Reading Assistant",
    description="Backend für Summary, Buchfragen (RAG) und Quiz",
)

# Buch "faust" beim Start einmal indexieren
index_book("faust")


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # später einschränken
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Pydantic Modelle
# -----------------------------

class SummaryRequest(BaseModel):
    text: str


class SummaryResponse(BaseModel):
    summary: str


class BookQuestionRequest(BaseModel):
    book_id: str  # z.B. "faust"
    question: str


class BookAnswerResponse(BaseModel):
    answer: str
    context: List[str]


class QuizRequest(BaseModel):
    book_id: str
    num_questions: int = 5
    instruction: str | None = None  # optionaler Kontext für die Fragen



class QuizCard(BaseModel):
    question: str
    answer: str


class QuizResponse(BaseModel):
    cards: List[QuizCard]


class UploadBookResponse(BaseModel):
    book_id: str
    message: str

class GutenbergBook(BaseModel):
    id: int
    title: str
    authors: List[str]
    text_url: Optional[str] = None


class GutenbergSearchResponse(BaseModel):
    books: List[GutenbergBook]


class GutenbergImportRequest(BaseModel):
    gutenberg_id: int
    book_id: Optional[str] = None


class GutenbergImportResponse(BaseModel):
    book_id: str
    title: str
    authors: List[str]
    char_count: int
    message: str


# -----------------------------
# Health Check
# -----------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# -----------------------------
# Summary Endpoint
# -----------------------------

@app.post("/summary", response_model=SummaryResponse)
def summary_endpoint(req: SummaryRequest):
    try:
        result = generate_summary(client, req.text)
        return SummaryResponse(summary=result)
    except Exception as e:
        print("Fehler bei generate_summary:", e)
        return SummaryResponse(summary="(Fallback-Summary wegen Fehler)")


# -----------------------------
# RAG: Fragen zum Buch
# -----------------------------

@app.post("/ask_book", response_model=BookAnswerResponse)
def ask_book(req: BookQuestionRequest):
    try:
        # 1) relevante Textstellen aus der Vektordatenbank holen
        context_chunks = retrieve_context(req.book_id, req.question, k=5)
        context_text = "\n\n---\n\n".join(context_chunks)

        # 2) LLM mit Kontext anfragen
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Du bist ein hilfreicher Tutor für Literatur. "
                        "Beantworte Fragen NUR anhand des folgenden Buch-Kontexts. "
                        "Wenn du es nicht weisst, sage: 'Ich weiss es nicht'."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Kontext aus dem Buch (Ausschnitte):\n{context_text}\n\n"
                        f"Frage: {req.question}"
                    ),
                },
            ],
        )

        answer_text = completion.choices[0].message.content

        return BookAnswerResponse(
            answer=answer_text,
            context=context_chunks,
        )
    except Exception as e:
        print("Fehler in /ask_book:", e)
        raise HTTPException(status_code=500, detail="Fehler beim Beantworten der Buchfrage")


# -----------------------------
# Quiz Endpoint
# -----------------------------

@app.post("/quiz", response_model=QuizResponse)
def quiz_endpoint(req: QuizRequest):
    try:
        cards_data = generate_quiz(
            client,
            req.book_id,
            req.num_questions,
            instruction=req.instruction,
        )
        cards = [QuizCard(**c) for c in cards_data]
        return QuizResponse(cards=cards)
    except Exception as e:
        print("Fehler in /quiz:", e)
        raise HTTPException(status_code=500, detail="Fehler beim Erzeugen des Quiz")



# -----------------------------
# Buch-Upload Endpoint
# -----------------------------

@app.post("/upload_book", response_model=UploadBookResponse)
async def upload_book(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="Nur .txt-Dateien sind erlaubt.")

    try:
        content_bytes = await file.read()
        content = content_bytes.decode("utf-8", errors="ignore")

        # Buch-ID aus Dateiname (ohne .txt)
        book_id = Path(file.filename).stem

        save_book_file(book_id, content)
        index_book(book_id)

        return UploadBookResponse(
            book_id=book_id,
            message=f"Buch '{book_id}' gespeichert und indexiert.",
        )
    except Exception as e:
        print("Fehler in /upload_book:", e)
        raise HTTPException(status_code=500, detail="Fehler beim Hochladen des Buches")
    

@app.get("/books", response_model=List[str])
def list_books():
    """
    Gibt eine Liste aller verfügbaren Buch-IDs zurück.
    Grundlage sind alle .txt-Dateien im Ordner backend/data.
    Beispiel: ["faust", "mein_buch", ...]
    """
    data_dir = Path(__file__).parent / "data"
    if not data_dir.exists():
        return []

    book_ids = [p.stem for p in data_dir.glob("*.txt")]
    return sorted(book_ids)


# -----------------------------
# Gutenberg
# -----------------------------

@app.get("/gutenberg/search", response_model=GutenbergSearchResponse)
async def gutenberg_search(query: str):
    try:
        async with httpx.AsyncClient(timeout=30.0) as http:
            r = await http.get(
                "https://gutendex.com/books/",
                params={"search": query},
            )
            r.raise_for_status()
            data = r.json()

        books: List[GutenbergBook] = []
        for b in data.get("results", [])[:10]:
            formats = b.get("formats", {})
            text_url = (
                formats.get("text/plain; charset=utf-8")
                or formats.get("text/plain; charset=us-ascii")
                or formats.get("text/plain")
                or next(
                    (
                        u
                        for u in formats.values()
                        if isinstance(u, str) and u.endswith(".txt")
                    ),
                    None,
                )
            )

            books.append(
                GutenbergBook(
                    id=b.get("id"),
                    title=b.get("title", "Unknown Title"),
                    authors=[a.get("name", "Unknown") for a in b.get("authors", [])],
                    text_url=text_url,
                )
            )

        return GutenbergSearchResponse(books=books)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching Gutenberg: {str(e)}",
        )


@app.post("/gutenberg/import", response_model=GutenbergImportResponse)
async def gutenberg_import(req: GutenbergImportRequest):
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as http:
        meta_r = await http.get(f"https://gutendex.com/books/{req.gutenberg_id}/")
        meta_r.raise_for_status()
        meta = meta_r.json()

        formats = meta.get("formats", {})
        text_url = (
            formats.get("text/plain; charset=utf-8")
            or formats.get("text/plain; charset=us-ascii")
            or formats.get("text/plain")
            or next((u for u in formats.values() if isinstance(u, str) and u.endswith(".txt")), None)
        )
        if not text_url:
            raise HTTPException(status_code=404, detail="No plain-text format available for this book.")

        txt_r = await http.get(text_url)
        txt_r.raise_for_status()
        text = txt_r.text

    book_id = req.book_id or f"gutenberg_{req.gutenberg_id}"

    save_book_file(book_id, text)
    index_book(book_id)  # indexes into Chroma

    return GutenbergImportResponse(
        book_id=book_id,
        title=meta.get("title", "Unknown Title"),
        authors=[a.get("name", "Unknown") for a in meta.get("authors", [])],
        char_count=len(text),
        message=f"Gutenberg book imported, saved, and indexed as '{book_id}'.",
    )