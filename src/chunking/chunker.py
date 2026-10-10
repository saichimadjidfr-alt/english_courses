import re


def split_long(paragraph: str, max_chars: int) -> list[str]:
    """Coupe un paragraphe trop long par phrases."""
    if len(paragraph) <= max_chars:
        return [paragraph]

    pieces = []
    current = ""
    for sentence in re.split(r"(?<=[.!?])\s+", paragraph):
        while len(sentence) > max_chars:
            if current:
                pieces.append(current)
                current = ""
            pieces.append(sentence[:max_chars])
            sentence = sentence[max_chars:]
        if current and len(current) + 1 + len(sentence) > max_chars:
            pieces.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        pieces.append(current)
    return pieces


def overlap_tail(text: str, overlap: int) -> str:
    """Fin du chunk précédent, coupée proprement au début d'un mot."""
    if overlap <= 0 or len(text) <= overlap:
        return ""
    tail = text[-overlap:]
    idx = tail.find(" ")
    return tail[idx + 1:] if idx != -1 else tail


def chunk_text(text: str, max_chars: int, overlap: int) -> list[str]:
    pieces = []
    for paragraph in text.split("\n\n"):
        paragraph = paragraph.strip()
        if paragraph:
            pieces.extend(split_long(paragraph, max_chars))

    chunks = []
    current = ""
    for piece in pieces:
        if current and len(current) + 2 + len(piece) > max_chars:
            chunks.append(current)
            current = (overlap_tail(current, overlap) + "\n\n" + piece).strip()
        else:
            current = f"{current}\n\n{piece}" if current else piece
    if current:
        chunks.append(current)
    return chunks


def chunk_sections(sections, max_chars=1500, overlap=200, min_chars=100):
    """Transforme les sections en chunks, en gardant le livre et l'endroit."""
    chunks = []
    for s in sections:
        pieces = chunk_text(s["text"], max_chars, overlap)
        for n, piece in enumerate(pieces, start=1):
            if len(piece) < min_chars:
                continue
            chunks.append(
                {
                    "id": f"{s['source']}|{s['location']}|{n}",
                    "text": piece,
                    "source": s["source"],
                    "location": s["location"],
                }
            )
    return chunks