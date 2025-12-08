from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import os
from typing import List
from rag import retrieve_context, index_book


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Wenn kein API-Key gesetzt ist, nutzen wir einen Dummy-Client
client = OpenAI(api_key=api_key) if api_key else None

app = FastAPI()

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

# HEALTH CHECK
@app.get("/health")
def health():
    return {"status": "ok"}

# MODELS
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


# SUMMARY ENDPOINT
@app.post("/summary", response_model=SummaryResponse)
def summary_endpoint(req: SummaryRequest):
    # Falls kein API-Key vorhanden ist oder OpenAI nicht konfiguriert → Dummy-Summary
    if client is None:
        print("WARNUNG: Kein OPENAI_API_KEY gesetzt – benutze Dummy-Summary.")
        return SummaryResponse(summary=f"(Dummy-Summary) {req.text[:150]}...")

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=200,
            messages=[
                {"role": "system", "content": "You generate concise summaries of text. Only answer from provided context. If no information is available, say: 'Ich weiss es nicht'."},
                {"role": "user", "content": req.text},
            ],
        )
        # bei neuer OpenAI-Bibliothek:
        result = completion.choices[0].message.content
        return SummaryResponse(summary=result)
    except Exception as e:
        # Fallback, damit das Frontend NIE leer bleibt
        print("Fehler bei OpenAI:", e)
        return SummaryResponse(summary=f"(Fallback-Summary wegen Fehler) {req.text[:150]}...")

@app.post("/ask_book", response_model=BookAnswerResponse)
def ask_book(req: BookQuestionRequest):
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

    # gleiche Art wie in deinem /summary-Endpoint
    answer_text = completion.choices[0].message.content


    return BookAnswerResponse(
        answer=answer_text,
        context=context_chunks,
    )
