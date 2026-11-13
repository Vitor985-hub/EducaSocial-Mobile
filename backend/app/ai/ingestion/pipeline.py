import argparse
import sys
from collections.abc import Sequence
from dataclasses import dataclass

from app.ai.container import build_repository
from app.ai.core.config import get_settings
from app.ai.core.exceptions import AIServiceError, ProviderError
from app.ai.ingestion.chunking import build_opportunity_chunks
from app.ai.providers.base import EmbeddingProvider
from app.ai.providers.factory import build_embedding_provider
from app.ai.repositories.chunks import ChunkRepository, NewDocument

EMBED_BATCH_SIZE = 32


@dataclass(frozen=True, slots=True)
class BuildReport:
    opportunities: int
    documents: int
    applied: bool


@dataclass(frozen=True, slots=True)
class EmbedReport:
    pending: int
    embedded: int
    applied: bool


def build_documents(
    repository: ChunkRepository, max_chars: int, overlap: int, apply: bool
) -> BuildReport:
    records = repository.opportunities_without_documents()
    documents: list[NewDocument] = []
    for record in records:
        documents.extend(build_opportunity_chunks(record, max_chars, overlap))
    if apply:
        repository.insert_documents(documents)
    return BuildReport(opportunities=len(records), documents=len(documents), applied=apply)


def embed_pending(
    repository: ChunkRepository,
    provider: EmbeddingProvider,
    apply: bool,
    batch_size: int = EMBED_BATCH_SIZE,
) -> EmbedReport:
    pending = repository.pending_documents(provider.model_name)
    if not apply:
        return EmbedReport(pending=len(pending), embedded=0, applied=False)
    embedded = 0
    for start in range(0, len(pending), batch_size):
        batch = pending[start : start + batch_size]
        vectors = provider.embed_documents([item.content for item in batch])
        if len(vectors) != len(batch) or len({len(vector) for vector in vectors}) > 1:
            raise ProviderError("O provedor retornou vetores inconsistentes.")
        repository.save_embeddings(
            provider.model_name,
            {item.document_id: vector for item, vector in zip(batch, vectors, strict=True)},
        )
        embedded += len(batch)
        print(f"  {embedded}/{len(pending)} documentos com embedding", flush=True)
    return EmbedReport(pending=len(pending), embedded=embedded, applied=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.ai.ingestion.pipeline")
    parser.add_argument("command", choices=["build-documents", "embed"])
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Grava no banco. Sem esta opção, apenas simula e mostra os números.",
    )
    args = parser.parse_args(argv)
    settings = get_settings()
    try:
        repository = build_repository(settings)
        if args.command == "build-documents":
            build_report = build_documents(
                repository, settings.chunk_max_chars, settings.chunk_overlap_chars, args.apply
            )
            mode = "gravados" if build_report.applied else "a gravar (simulação)"
            print(
                f"{build_report.opportunities} oportunidades sem documentos; "
                f"{build_report.documents} documentos {mode}."
            )
        else:
            provider = build_embedding_provider(settings)
            embed_report = embed_pending(repository, provider, args.apply)
            if embed_report.applied:
                print(f"{embed_report.embedded} embeddings gravados para {provider.model_name}.")
            else:
                print(
                    f"{embed_report.pending} documentos sem embedding para "
                    f"{provider.model_name} (simulação; use --apply para gerar)."
                )
    except AIServiceError as exc:
        print(f"Erro: {exc.message}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
