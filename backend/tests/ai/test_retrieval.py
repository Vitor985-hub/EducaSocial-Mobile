import pytest

from app.ai.core.exceptions import ConfigurationError
from app.ai.services.retrieval import ChunkIndexProvider, VectorIndex, location_matches
from tests.ai.fakes import HashEmbedder, StaticRepository, make_chunk

EMBEDDER = HashEmbedder()


def make_index() -> VectorIndex:
    return VectorIndex(
        [
            make_chunk(EMBEDDER, document_id=1, content="auxílio aluguel moradia família"),
            make_chunk(EMBEDDER, document_id=2, content="bolsa estudo faculdade estudante"),
            make_chunk(EMBEDDER, document_id=3, content="cesta alimentos distribuição"),
        ]
    )


def test_most_similar_chunk_comes_first() -> None:
    hits = make_index().search(EMBEDDER.vector("aluguel moradia"), None, None, 3, 0.1)

    assert hits[0].chunk.document_id == 1
    assert hits[0].score > 0.5


def test_chunks_below_min_score_are_dropped() -> None:
    hits = make_index().search(EMBEDDER.vector("aluguel moradia"), None, None, 3, 0.3)

    assert [hit.chunk.document_id for hit in hits] == [1]


def test_top_k_limits_results() -> None:
    hits = make_index().search(EMBEDDER.vector("aluguel bolsa cesta"), None, None, 2, 0.0)

    assert len(hits) == 2


def test_empty_index_returns_nothing() -> None:
    assert VectorIndex([]).search(EMBEDDER.vector("qualquer"), None, None, 3, 0.0) == []


def test_zero_query_vector_returns_nothing() -> None:
    assert make_index().search([0.0] * 256, None, None, 3, 0.0) == []


def test_dimension_mismatch_is_a_configuration_error() -> None:
    with pytest.raises(ConfigurationError):
        make_index().search([1.0, 0.0], None, None, 3, 0.0)


def test_mixed_dimensions_are_rejected_when_building_index() -> None:
    chunks = [make_chunk(EMBEDDER, document_id=1), make_chunk(EMBEDDER, document_id=2)]
    broken = [chunks[0], make_chunk(HashEmbedder(dimensions=8), document_id=3)]

    with pytest.raises(ConfigurationError):
        VectorIndex(broken)


def test_location_rules() -> None:
    national = make_chunk(region_level="national")
    state = make_chunk(region_level="state", region_state="SP", region_name="São Paulo")
    city = make_chunk(region_level="city", region_state="SP", region_name="Santo André")

    assert location_matches(national, "RJ", "Niterói")
    assert location_matches(state, "SP", None)
    assert location_matches(state, "SP", "Campinas")
    assert not location_matches(state, "RJ", None)
    assert location_matches(city, "SP", None)
    assert location_matches(city, "SP", "santo andre")
    assert not location_matches(city, "SP", "Campinas")
    assert not location_matches(city, "RJ", "Santo André")
    assert location_matches(city, None, None)


def test_search_applies_location_filter() -> None:
    index = VectorIndex(
        [
            make_chunk(EMBEDDER, document_id=1, content="aluguel", region_level="national"),
            make_chunk(
                EMBEDDER,
                document_id=2,
                content="aluguel",
                region_level="city",
                region_state="SP",
                region_name="Santo André",
            ),
            make_chunk(
                EMBEDDER,
                document_id=3,
                content="aluguel",
                region_level="city",
                region_state="SP",
                region_name="Campinas",
            ),
        ]
    )

    hits = index.search(EMBEDDER.vector("aluguel"), "SP", "Santo André", 5, 0.1)

    assert sorted(hit.chunk.document_id for hit in hits) == [1, 2]


def test_index_is_cached_until_ttl_expires() -> None:
    repository = StaticRepository([make_chunk(EMBEDDER)])
    now = [0.0]
    provider = ChunkIndexProvider(repository, "m", 60, clock=lambda: now[0])

    provider.get()
    now[0] = 30
    provider.get()
    assert repository.loads == 1

    now[0] = 61
    provider.get()
    assert repository.loads == 2
