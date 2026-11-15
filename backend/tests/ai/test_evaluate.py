from app.ai.services.prompts import NO_EVIDENCE_MESSAGE
from app.ai.services.rag_service import RagService
from app.ai.services.retrieval import ChunkIndexProvider, VectorIndex
from app.ai.tools.evaluate import (
    calibration_summary,
    evaluate_generation,
    evaluate_retrieval,
    format_rows,
)
from tests.ai.fakes import HashEmbedder, ScriptedLLM, StaticRepository, make_chunk

EMBEDDER = HashEmbedder()

PROGRAMS = {
    "aluguel": {"title": "Apoio ao Aluguel", "source": {"url": "https://a.invalid"}},
    "bolsa": {"title": "Bolsa de Estudo", "source": {"url": "https://b.invalid"}},
}

CASES = [
    {
        "question": "como pedir apoio ao aluguel",
        "state": "SP",
        "municipality": None,
        "expect": "answer",
        "expected_programs": ["aluguel"],
    },
    {
        "question": "bolsa de estudo para faculdade",
        "state": "SP",
        "municipality": None,
        "expect": "answer",
        "expected_programs": ["aluguel"],
    },
    {
        "question": "cotação do dólar hoje",
        "state": "SP",
        "municipality": None,
        "expect": "no_evidence",
        "expected_programs": [],
    },
]


def chunks():
    return [
        make_chunk(
            EMBEDDER,
            document_id=1,
            opportunity_id=1,
            content="apoio ao aluguel como pedir apoio ao aluguel no município",
            opportunity_title="Apoio ao Aluguel",
            source_url="https://a.invalid",
        ),
        make_chunk(
            EMBEDDER,
            document_id=2,
            opportunity_id=2,
            content="bolsa de estudo para faculdade estudantes",
            opportunity_title="Bolsa de Estudo",
            source_url="https://b.invalid",
        ),
    ]


def test_retrieval_marks_correct_wrong_and_refused_questions() -> None:
    rows = evaluate_retrieval(VectorIndex(chunks()), EMBEDDER, CASES, PROGRAMS, 0.3)

    assert [row.verdict for row in rows] == ["ok", "FALHA: programa errado", "ok"]
    assert rows[0].score and rows[0].score > 0.3
    assert rows[2].score is not None and rows[2].score < 0.3


def test_calibration_summary_reports_separating_range() -> None:
    rows = evaluate_retrieval(VectorIndex(chunks()), EMBEDDER, CASES[:1] + CASES[2:], PROGRAMS, 0.3)

    summary = calibration_summary(rows)

    assert "separa os dois grupos" in summary


def test_calibration_summary_needs_both_kinds_of_questions() -> None:
    rows = evaluate_retrieval(VectorIndex(chunks()), EMBEDDER, CASES[:1], PROGRAMS, 0.3)

    assert "não há perguntas suficientes" in calibration_summary(rows)


def test_generation_checks_refusal_and_cited_source() -> None:
    index = ChunkIndexProvider(StaticRepository(chunks()), EMBEDDER.model_name, 300)
    answering = RagService(EMBEDDER, ScriptedLLM("Procure o município [1]."), index, 3, 0.3)

    rows = evaluate_generation(answering, CASES[:1], PROGRAMS)

    assert rows[0].verdict == "ok"

    refusing = RagService(EMBEDDER, ScriptedLLM("SEM_EVIDENCIA"), index, 3, 0.3)
    rows = evaluate_generation(refusing, CASES[:1] + CASES[2:], PROGRAMS)

    assert rows[0].verdict == "FALHA: recusou"
    assert rows[1].verdict == "ok"
    assert rows[1].detail == "recusou"


def test_format_rows_counts_failures() -> None:
    rows = evaluate_retrieval(VectorIndex(chunks()), EMBEDDER, CASES, PROGRAMS, 0.3)

    assert "3 perguntas | 1 falhas | 0 para revisar" in format_rows(rows)[-1]
    assert NO_EVIDENCE_MESSAGE


def test_retrieval_reports_expected_program_missing_from_the_index() -> None:
    programs = {**PROGRAMS, "pot": {"title": "POT", "source": {"url": "https://p.invalid"}}}
    case = {**CASES[0], "expected_programs": ["pot"]}

    rows = evaluate_retrieval(VectorIndex(chunks()), EMBEDDER, [case], programs, 0.3)

    assert rows[0].verdict == "FALHA: programa não está no banco"