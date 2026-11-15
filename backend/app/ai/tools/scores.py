import argparse
import sys

from app.ai.container import build_repository
from app.ai.core.config import get_settings
from app.ai.core.exceptions import AIServiceError
from app.ai.providers.base import EmbeddingProvider
from app.ai.providers.factory import build_embedding_provider
from app.ai.repositories.chunks import ChunkRepository
from app.ai.services.retrieval import VectorIndex


def describe_scores(
    repository: ChunkRepository,
    embedder: EmbeddingProvider,
    question: str,
    state: str | None,
    municipality: str | None,
    min_score: float,
) -> list[str]:
    chunks = repository.load_chunks(embedder.model_name)
    index = VectorIndex(chunks)
    hits = index.search(embedder.embed_query(question), state, municipality, len(chunks), -0.99)
    lines = [
        f"Modelo: {embedder.model_name} | chunks no índice: {len(chunks)} | "
        f"corte atual (RETRIEVAL_MIN_SCORE): {min_score}",
        f"Dentro do filtro regional: {len(hits)} | fora do filtro: {len(chunks) - len(hits)}",
    ]
    for hit in hits:
        chunk = hit.chunk
        mark = "passa " if hit.score >= min_score else "abaixo"
        preview = chunk.content.replace("\n", " ")[:70]
        lines.append(
            f"{hit.score:.3f} {mark} programa {chunk.opportunity_id} "
            f"[{chunk.region_level}/{chunk.region_name}] chunk {chunk.chunk_index}: "
            f"{chunk.opportunity_title} | {preview}"
        )
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m app.ai.tools.scores")
    parser.add_argument("question")
    parser.add_argument("--state")
    parser.add_argument("--municipality")
    args = parser.parse_args()
    settings = get_settings()
    try:
        lines = describe_scores(
            build_repository(settings),
            build_embedding_provider(settings),
            args.question,
            args.state,
            args.municipality,
            settings.retrieval_min_score,
        )
    except AIServiceError as exc:
        print(f"Erro: {exc.message}", file=sys.stderr)
        return 1
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())