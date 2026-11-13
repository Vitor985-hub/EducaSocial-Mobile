from collections.abc import Sequence

from app.ai.services.retrieval import Hit

NO_EVIDENCE_TOKEN = "SEM_EVIDENCIA"

NO_EVIDENCE_MESSAGE = (
    "Não encontrei evidências suficientes nas fontes disponíveis para responder a essa pergunta. "
    "Confira diretamente no site oficial do programa."
)

SYSTEM_PROMPT = (
    "Você é o assistente do Educa Social, que ajuda pessoas a entender programas sociais, "
    "benefícios e oportunidades no Brasil.\n"
    "Responda apenas com base nos trechos numerados do CONTEXTO. Não use conhecimento externo "
    "e não invente regras, valores, requisitos, prazos ou procedimentos.\n"
    f"Se o contexto não tiver informação suficiente para responder, responda exatamente "
    f"{NO_EVIDENCE_TOKEN} e nada mais.\n"
    "Cite os trechos usados com o número entre colchetes, como [1].\n"
    "Responda em português do Brasil, em linguagem simples e de forma objetiva.\n"
    "Se um trecho tiver status diferente de current, avise que a informação pode estar "
    "desatualizada e deve ser confirmada na fonte oficial."
)


def _format_hit(number: int, hit: Hit) -> str:
    chunk = hit.chunk
    reviewed = chunk.last_reviewed.isoformat() if chunk.last_reviewed else "desconhecida"
    source = chunk.source_name or "sem fonte registrada"
    if chunk.source_url:
        source = f"{source} ({chunk.source_url})"
    return (
        f"[{number}] Programa: {chunk.opportunity_title}\n"
        f"Status: {chunk.status or 'desconhecido'} | Última revisão: {reviewed}\n"
        f"Fonte: {source}\n"
        f"Trecho: {chunk.content}"
    )


def build_user_prompt(question: str, hits: Sequence[Hit]) -> str:
    context = "\n\n".join(_format_hit(number, hit) for number, hit in enumerate(hits, start=1))
    return f"CONTEXTO:\n{context}\n\nPERGUNTA: {question}"
