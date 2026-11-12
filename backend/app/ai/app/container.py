from sqlalchemy import Engine, create_engine

from app.core.config import Settings
from app.providers.factory import build_embedding_provider, build_llm_provider
from app.repositories.chunks import ChunkRepository
from app.repositories.local import LocalChunkRepository
from app.repositories.mysql import SqlChunkRepository
from app.services.rag_service import RagService
from app.services.retrieval import ChunkIndexProvider


def build_engine(settings: Settings) -> Engine:
    return create_engine(settings.database_url, pool_pre_ping=True, pool_recycle=1800)


def build_repository(settings: Settings) -> ChunkRepository:
    if settings.chunk_store == "local":
        return LocalChunkRepository(settings.local_store_path)
    return SqlChunkRepository(build_engine(settings))


def build_rag_service(settings: Settings) -> RagService:
    embedder = build_embedding_provider(settings)
    llm = build_llm_provider(settings)
    index_provider = ChunkIndexProvider(
        build_repository(settings), embedder.model_name, settings.index_ttl_seconds
    )
    return RagService(
        embedder, llm, index_provider, settings.retrieval_top_k, settings.retrieval_min_score
    )
