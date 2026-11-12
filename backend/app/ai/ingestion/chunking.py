from app.repositories.chunks import NewDocument, OpportunityRecord


def split_text(text: str, max_chars: int, overlap: int) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]
    pieces: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            window = text[start:end]
            cut = max(window.rfind("\n"), window.rfind(". "), window.rfind("; "))
            if cut > max_chars // 2:
                end = start + cut + 1
        piece = text[start:end].strip()
        if piece:
            pieces.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return pieces


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _steps(items: list[str]) -> str:
    return "\n".join(f"{number}. {item}" for number, item in enumerate(items, start=1))


def build_opportunity_chunks(
    record: OpportunityRecord, max_chars: int, overlap: int
) -> list[NewDocument]:
    sections = [
        ("Descrição", record.description),
        ("Elegibilidade", record.eligibility),
        ("Documentos necessários", _bullets(record.required_documents)),
        ("Como solicitar", _steps(record.application_steps)),
    ]
    documents: list[NewDocument] = []
    for label, text in sections:
        for piece in split_text(text, max_chars, overlap):
            documents.append(
                NewDocument(
                    opportunity_id=record.id,
                    source_id=record.source_id,
                    chunk_index=len(documents),
                    content=f"{record.title}\n{label}: {piece}",
                )
            )
    return documents
