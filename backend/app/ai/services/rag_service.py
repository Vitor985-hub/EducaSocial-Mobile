import logging
import re
from collections.abc import Sequence

from app.ai.providers.base import EmbeddingProvider, LLMProvider
from app.ai.schemas.query import QueryRequest, QueryResponse, Source
from app.ai.services.prompts import (
    NO_EVIDENCE_MESSAGE,
    NO_EVIDENCE_TOKEN,
    SYSTEM_PROMPT,
    build_user_prompt,
)
from app.ai.services.retrieval import ChunkIndexProvider, Hit

logger = logging.getLogger(__name__)

CITATION_PATTERN = re.compile(r"\[(\d+)\]")


def _cited_hits(answer: str, hits: Sequence[Hit]) -> list[Hit]:
    numbers = {int(match) for match in CITATION_PATTERN.findall(answer)}
    cited = [hit for number, hit in enumerate(hits, start=1) if number in numbers]
    return cited or list(hits)


def _build_sources(hits: Sequence[Hit]) -> list[Source]:
    sources: list[Source] = []
    seen: set[tuple[int, str | None]] = set()
    for hit in hits:
        chunk = hit.chunk
        key = (chunk.opportunity_id, chunk.source_url)
        if key in seen:
            continue
        seen.add(key)
        sources.append(
            Source(
                title=chunk.source_name or chunk.opportunity_title,
                program_id=chunk.opportunity_id,
                url=chunk.source_url,
            )
        )
    return sources


def _no_evidence() -> QueryResponse:
    return QueryResponse(answer=NO_EVIDENCE_MESSAGE, sources=[])


class RagService:
    def __init__(
        self,
        embedder: EmbeddingProvider,
        llm: LLMProvider,
        index_provider: ChunkIndexProvider,
        top_k: int,
        min_score: float,
    ) -> None:
        self._embedder = embedder
        self._llm = llm
        self._index_provider = index_provider
        self._top_k = top_k
        self._min_score = min_score

    def ask(self, request: QueryRequest) -> QueryResponse:
        query_vector = self._embedder.embed_query(request.question)
        index = self._index_provider.get()
        if len(index) == 0:
            logger.warning("Índice vazio para o modelo de embedding %s.", self._embedder.model_name)
        hits = index.search(
            query_vector, request.state, request.municipality, self._top_k, self._min_score
        )
        if not hits:
            return _no_evidence()
        answer = self._llm.generate(SYSTEM_PROMPT, build_user_prompt(request.question, hits))
        answer = answer.strip()
        if not answer or answer.upper().startswith(NO_EVIDENCE_TOKEN):
            return _no_evidence()
        return QueryResponse(answer=answer, sources=_build_sources(_cited_hits(answer, hits)))
