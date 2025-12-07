from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Wenn kein API-Key gesetzt ist, nutzen wir einen Dummy-Client
client = OpenAI(api_key=api_key) if api_key else None

app = FastAPI()

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
                {"role": "system", "content": "You generate concise summaries of text."},
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
