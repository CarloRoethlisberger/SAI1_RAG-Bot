# backend/rag.py

import os
from typing import List
from sentence_transformers import SentenceTransformer
import chromadb

# Pfad für die Vektordatenbank
DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

# Embedding-Modell (klein & schnell)
_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# ChromaDB-Client (persistente DB auf der Platte)
_client = chromadb.PersistentClient(path=DB_DIR)


def _get_collection(book_id: str):
    """Hole oder erstelle eine Collection für ein bestimmtes Buch."""
    return _client.get_or_create_collection(name=f"book_{book_id}")


def load_book_text(book_id: str) -> str:
    """Liest den Volltext des Buches aus backend/data/<book_id>.txt."""
    filename = f"{book_id}.txt"
    path = os.path.join(os.path.dirname(__file__), "data", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def split_into_chunks(text: str, max_chars: int = 800) -> List[str]:
    """Teilt den Text in überschaubare Textabschnitte (Chunks)."""
    paragraphs = text.split("\n\n")
    chunks: List[str] = []
    current = ""

    for p in paragraphs:
        p = p.strip()
        if not p:
            continue

        # packe mehrere Absätze in einen Chunk, bis max_chars erreicht sind
        if len(current) + len(p) + 2 <= max_chars:
            current += ("\n\n" if current else "") + p
        else:
            if current:
                chunks.append(current)
            current = p

    if current:
        chunks.append(current)

    return chunks


def index_book(book_id: str) -> None:
    """Erstellt Embeddings für ein Buch und speichert sie in Chroma."""
    collection = _get_collection(book_id)

    # Wenn schon Daten vorhanden sind, nicht nochmal indexieren
    if collection.count() > 0:
        return

    text = load_book_text(book_id)
    chunks = split_into_chunks(text)

    ids = [f"{book_id}_{i}" for i in range(len(chunks))]
    embeddings = _embedding_model.encode(chunks).tolist()

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
    )


def retrieve_context(book_id: str, question: str, k: int = 5) -> List[str]:
    """
    Holt die k relevantesten Textabschnitte aus dem indexierten Buch
    zu einer gegebenen Frage.
    """
    collection = _get_collection(book_id)

    # Falls noch nicht indexiert, jetzt einmalig indexieren
    if collection.count() == 0:
        index_book(book_id)

    # Frage embedden und per Embedding suchen (robust ohne Chroma embedding_function)
    q_emb = _embedding_model.encode([question]).tolist()

    results = collection.query(
        query_embeddings=q_emb,
        n_results=k,
        include=["documents"],
    )

    return results["documents"][0]


def get_all_chunks(book_id: str) -> List[str]:
    """
    Holt alle gespeicherten Text-Chunks für ein Buch aus Chroma.
    Falls die Collection noch leer ist, wird zuerst indexiert.
    """
    collection = _get_collection(book_id)

    if collection.count() == 0:
        index_book(book_id)

    results = collection.get(include=["documents"])
    docs_lists = results.get("documents", [])

    # docs_lists ist eine Liste von Listen → wir flatten sie
    chunks: List[str] = []
    for lst in docs_lists:
        chunks.extend(lst)

    return chunks
