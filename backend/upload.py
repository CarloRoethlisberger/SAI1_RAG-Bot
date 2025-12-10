# backend/upload.py

from pathlib import Path

from rag import index_book


def save_book_file(book_id: str, text: str) -> None:
    """
    Speichert den Text als .txt unter backend/data/<book_id>.txt
    und indexiert das Buch anschließend in Chroma.
    """
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)

    file_path = data_dir / f"{book_id}.txt"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

    # danach: Embeddings erzeugen und in Chroma speichern
    index_book(book_id)
