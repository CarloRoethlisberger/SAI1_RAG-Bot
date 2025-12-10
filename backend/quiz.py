# backend/quiz.py

import json
import random
from typing import List, Dict, Any, Optional

from openai import OpenAI
from rag import get_all_chunks


def generate_quiz(
    client: OpenAI,
    book_id: str,
    num_questions: int = 5,
    instruction: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Erzeugt Quizfragen basierend auf dem Buchkontext.

    Rückgabeformat (Python-Objekt):
    [
      {"question": "...", "answer": "..."},
      ...
    ]
    """

    # --- 1) Chunks aus der Vektordatenbank holen -----------------------
    chunks = get_all_chunks(book_id)
    if not chunks:
        return [{"question": "Keine Daten für dieses Buch gefunden.", "answer": ""}]

    # get_all_chunks liefert evtl. eine Liste von Listen -> flatten
    if isinstance(chunks[0], list):
        flat_chunks: List[str] = []
        for sub in chunks:
            flat_chunks.extend(sub)
        chunks = flat_chunks  # type: ignore[assignment]

    # --- 2) Kontext vorbereiten ----------------------------------------
    sample = random.sample(chunks, k=min(len(chunks), 30))
    context = "\n\n---\n\n".join(sample)

    # --- 3) Thema / Modus festlegen ------------------------------------
    # instruction == None oder "" -> zufällige Fragen zum Buch
    if instruction and instruction.strip():
        focus_text = (
            "Fokussiere die Fragen auf folgendes Thema, das vom Benutzer vorgegeben wurde:\n"
            f"\"{instruction.strip()}\".\n"
        )
    else:
        focus_text = (
            "Stelle allgemein gemischte Verständnisfragen zum Inhalt des Buches, "
            "ohne dich auf einen speziellen Aspekt zu beschränken.\n"
        )

    # --- 4) Prompt bauen -----------------------------------------------
    system_prompt = (
        "Du bist ein Quizgenerator für Literatur.\n"
        f"Das Buch hat die ID: '{book_id}'. Alle Textausschnitte im Kontext stammen NUR aus diesem Buch.\n\n"
        "AUFGABE:\n"
        "- Erzeuge Verständnisfragen auf DEUTSCH.\n"
        "- Die Fragen müssen sich klar auf Figuren, Beziehungen, Handlung, Orte, Motive oder Konflikte "
        "aus dem KONTEXT beziehen.\n"
        "- Jede Frage MUSS durch den Kontext beantwortbar sein (wörtlich oder sinngemäß).\n"
        "- Erfinde KEINE Informationen, die nicht im Kontext stehen.\n"
        "- Antworte ausschließlich mit einem JSON-OBJEKT mit folgendem Schema:\n"
        "{\n"
        '  \"cards\": [\n'
        '    {\"question\": \"...\", \"answer\": \"...\"},\n'
        '    ...\n'
        "  ]\n"
        "}\n"
        "- Das Feld \"cards\" soll ungefähr die angeforderte Anzahl an Einträgen enthalten.\n"
        "- Sprache: durchgehend DEUTSCH.\n"
    )

    user_prompt = (
        "Hier sind Textausschnitte aus dem Buch:\n\n"
        f"{context}\n\n"
        f"{focus_text}\n"
        f"Erzeuge GENAU {num_questions} sinnvolle, inhaltliche Quizfragen "
        "zum Inhalt dieses Buches. Verwende das oben beschriebene JSON-Schema."
    )

    # --- 5) Modell mit JSON-Response-Format aufrufen -------------------
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        temperature=0.4,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    raw = completion.choices[0].message.content or ""
    print("RAW QUIZ JSON:", raw)  # Debug im Terminal

    # --- 6) JSON parsen ------------------------------------------------
    try:
        obj = json.loads(raw)
    except Exception:
        return [{"question": "Fehler beim JSON-Parsing", "answer": raw}]

    cards_list = obj.get("cards")
    if not isinstance(cards_list, list):
        if isinstance(obj, list):
            cards_list = obj
        else:
            return [{"question": "Fehler: JSON hat kein 'cards'-Feld", "answer": raw}]

    if len(cards_list) == 0:
        return [{"question": "Modell hat keine Quizkarten erzeugt.", "answer": raw}]

    # --- 7) Aufbereiten & begrenzen ------------------------------------
    cleaned: List[Dict[str, Any]] = []
    for card in cards_list:
        q = str(card.get("question", "")).strip()
        a = str(card.get("answer", "")).strip()
        if not q or not a:
            continue
        cleaned.append({"question": q, "answer": a})

    if not cleaned:
        return [{"question": "Keine verwertbaren Fragen generiert.", "answer": raw}]

    return cleaned[:num_questions]
