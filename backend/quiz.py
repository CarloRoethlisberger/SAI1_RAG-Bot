# backend/quiz.py

import json
import random
import re
from typing import List, Dict, Any

from openai import OpenAI
from rag import get_all_chunks


def _is_bad_question(q: str) -> bool:
    """
    Filtert Fragen raus, die nur auf Formales abzielen
    (Buchstaben, Wörter, Anzahl, Position etc.).
    """
    q_lower = q.lower()

    banned_keywords = [
        "buchstabe",
        "buchstaben",
        "wort",
        "wörter",
        "anzahl der",
        "wie viele",
        "erstes wort",
        "zweites wort",
        "drittes wort",
        "erster buchstabe",
        "zweiter buchstabe",
        "abschnitt",
        "zeile",
        "zeichen",
        "satzzeichen",
    ]

    return any(bad in q_lower for bad in banned_keywords)


def generate_quiz(client: OpenAI, book_id: str, num_questions: int = 5) -> List[Dict[str, Any]]:
    """
    Erzeugt Quizfragen basierend auf dem Buchkontext.
    Format:
    [
      {"question": "...", "answer": "..."},
      ...
    ]
    """

    # 🔹 Chunks holen & ggf. flatten
    chunks = get_all_chunks(book_id)
    if not chunks:
        return []

    if isinstance(chunks[0], list):
        chunks = [x for sub in chunks for x in sub]

    # 🔹 Mehr Kontext → bessere Fragen
    sample = random.sample(chunks, k=min(len(chunks), 30))
    context = "\n\n---\n\n".join(sample)

    # 🔹 Prompt: Nur inhaltliche Fragen erlaubt
    prompt_system = (
        "Du bist ein Quizgenerator für Literatur.\n"
        "Du bekommst Textausschnitte aus einem Buch.\n\n"
        "Erzeuge genau die gewünschte Anzahl Quizfragen im JSON-Format:\n"
        '[{"question": "...", "answer": "..."}]\n\n'
        "WICHTIG:\n"
        "- Stelle NUR inhaltliche Fragen zu Figuren, Beziehungen, Handlung, Orten, Motiven, Konflikten.\n"
        "- KEINE Fragen über Buchstaben, Wörter, Anzahl von Wörtern oder Buchstaben,\n"
        "  keine Fragen wie 'Was ist der erste Buchstabe...', 'Wie viele Wörter...',\n"
        "  nichts über Abschnitte, Zeilen oder Satzzeichen.\n"
        "- Fragen müssen aus dem Text ableitbar sein.\n"
        "- Keine Fakten erfinden.\n"
        "- Gib NUR reines JSON zurück, ohne erklärenden Text.\n"
    )

    prompt_user = (
        f"Hier sind Textausschnitte aus dem Buch:\n\n{context}\n\n"
        f"Erzeuge GENAU {num_questions} sinnvolle, inhaltliche Quizfragen."
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user},
        ],
    )

    raw = completion.choices[0].message.content

    # 🔹 JSON-Block extrahieren
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    data: List[Dict[str, Any]]

    if match:
        try:
            data = json.loads(match.group(0))
        except Exception:
            # Fallback: Rohtext
            return [{"question": "Fehler beim JSON-Parsing", "answer": raw}]
    else:
        return [{"question": "Kein JSON gefunden", "answer": raw}]

    # 🔹 Schlechte Fragen rausfiltern
    cleaned: List[Dict[str, Any]] = []
    for card in data:
        q = str(card.get("question", ""))
        a = str(card.get("answer", ""))
        if not q.strip() or not a.strip():
            continue
        if _is_bad_question(q):
            continue
        cleaned.append({"question": q.strip(), "answer": a.strip()})

    # Wenn nach Filterung alles weg ist → Fallback
    if not cleaned:
        return [{"question": "Fehler: Nur ungeeignete Fragen generiert.", "answer": raw}]

    # Ggf. auf gewünschte Anzahl kürzen
    return cleaned[:num_questions]
