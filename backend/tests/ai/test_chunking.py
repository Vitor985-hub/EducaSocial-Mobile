from app.ai.ingestion.chunking import build_opportunity_chunks, split_text
from app.ai.repositories.chunks import OpportunityRecord


def test_short_text_is_a_single_chunk() -> None:
    assert split_text("  texto curto  ", 100, 10) == ["texto curto"]


def test_empty_text_has_no_chunks() -> None:
    assert split_text("   ", 100, 10) == []


def test_long_text_is_split_within_limit_with_overlap() -> None:
    text = " ".join(f"Frase número {number}." for number in range(60))

    pieces = split_text(text, 200, 40)

    assert len(pieces) > 1
    assert all(len(piece) <= 200 for piece in pieces)
    assert pieces[0][-20:].strip() in pieces[1]


def test_split_always_makes_progress_without_natural_breaks() -> None:
    pieces = split_text("a" * 1000, 100, 30)

    assert all(len(piece) <= 100 for piece in pieces)
    assert sum(len(piece) for piece in pieces) >= 1000


def test_opportunity_chunks_have_title_label_and_sequential_index() -> None:
    record = OpportunityRecord(
        id=7,
        title="Programa X",
        description="Descrição do programa.",
        eligibility="Quem pode participar.",
        required_documents=["RG", "CPF"],
        application_steps=["Ir ao posto", "Entregar documentos"],
        source_id=3,
    )

    chunks = build_opportunity_chunks(record, 1200, 150)

    assert [chunk.chunk_index for chunk in chunks] == [0, 1, 2, 3]
    assert all(chunk.opportunity_id == 7 and chunk.source_id == 3 for chunk in chunks)
    assert chunks[0].content == "Programa X\nDescrição: Descrição do programa."
    assert chunks[2].content == "Programa X\nDocumentos necessários: - RG\n- CPF"
    assert chunks[3].content.endswith("1. Ir ao posto\n2. Entregar documentos")


def test_empty_sections_are_skipped() -> None:
    record = OpportunityRecord(
        id=1,
        title="Programa Y",
        description="Só descrição.",
        eligibility="",
        required_documents=[],
        application_steps=[],
        source_id=None,
    )

    chunks = build_opportunity_chunks(record, 1200, 150)

    assert len(chunks) == 1
    assert chunks[0].source_id is None
