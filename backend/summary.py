# backend/summary.py

from openai import OpenAI


def generate_summary(client: OpenAI, text: str) -> str:
    """
    Erzeugt eine kurze Zusammenfassung für den gegebenen Text.
    """
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=200,
        messages=[
            {
                "role": "system",
                "content": (
                    "You generate concise summaries of text. "
                    "Only answer from provided context. "
                    "If no information is available, say: 'Ich weiss es nicht'."
                ),
            },
            {"role": "user", "content": text},
        ],
    )
    return completion.choices[0].message.content
