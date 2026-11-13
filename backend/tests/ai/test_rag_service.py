from app.ai.schemas.query import QueryRequest
from app.ai.services.prompts import NO_EVIDENCE_MESSAGE
from app.ai.services.rag_service import RagService
from app.ai.services.retrieval import ChunkIndexProvider
from tests.ai.fakes import HashEmbedder, ScriptedLLM, StaticRepository, make_chunk

EMBEDDER = HashEmbedder()


def build_service(llm: ScriptedLLM, chunks, min_score: float = 0.3) -> RagService:
    index = ChunkIndexProvider(StaticRepository(chunks), EMBEDDER.model_name, 300)
    return RagService(EMBEDDER, llm, index, top_k=3, min_score=min_score)


def rent_chunks():
    return [
        make_chunk(
            EMBEDDER,
            document_id=1,
            opportunity_id=10,
            content="Apoio ao aluguel: o interessado deve procurar o atendimento do município",
            opportunity_title="Apoio ao Aluguel",
            source_name="Prefeitura",
            source_url="https://prefeitura.invalid/aluguel",
            status="unconfirmed",
        ),
        make_chunk(
            EMBEDDER,
            document_id=2,
            opportunity_id=10,
            content="Apoio ao aluguel: documentos exigidos RG CPF comprovante de residência",
            opportunity_title="Apoio ao Aluguel",
            source_name="Prefeitura",
            source_url="https://prefeitura.invalid/aluguel",
        ),
        make_chunk(
            EMBEDDER,
            document_id=3,
            opportunity_id=20,
            content="Bolsa de estudo para estudantes de faculdade",
            opportunity_title="Bolsa Estudo",
            source_name="Ministério",
            source_url="https://ministerio.invalid/bolsa",
        ),
    ]


def test_grounded_answer_returns_cited_sources_without_duplicates() -> None:
    llm = ScriptedLLM("Procure o atendimento do município [1] e leve RG e CPF [2].")
    service = build_service(llm, rent_chunks())

    response = service.ask(QueryRequest(question="Como pedir apoio ao aluguel?"))

    assert response.answer.startswith("Procure o atendimento")
    assert [(source.title, source.program_id) for source in response.sources] == [
        ("Prefeitura", 10)
    ]
    assert response.sources[0].url == "https://prefeitura.invalid/aluguel"


def test_sources_fall_back_to_all_hits_when_nothing_is_cited() -> None:
    llm = ScriptedLLM("Procure o atendimento do município.")
    service = build_service(llm, rent_chunks(), min_score=0.1)

    response = service.ask(QueryRequest(question="apoio aluguel atendimento município bolsa"))

    assert {source.program_id for source in response.sources} == {10, 20}


def test_prompt_contains_numbered_context_status_and_question() -> None:
    llm = ScriptedLLM("Resposta [1].")
    service = build_service(llm, rent_chunks())

    service.ask(QueryRequest(question="Como pedir apoio ao aluguel?"))

    system, prompt = llm.calls[0]
    assert "SEM_EVIDENCIA" in system
    assert "[1] Programa: Apoio ao Aluguel" in prompt
    assert "Status: unconfirmed" in prompt
    assert "https://prefeitura.invalid/aluguel" in prompt
    assert prompt.endswith("PERGUNTA: Como pedir apoio ao aluguel?")


def test_no_relevant_chunks_skips_the_llm() -> None:
    llm = ScriptedLLM("não deveria ser chamado")
    service = build_service(llm, rent_chunks(), min_score=0.6)

    response = service.ask(QueryRequest(question="previsão do tempo amanhã"))

    assert response.answer == NO_EVIDENCE_MESSAGE
    assert response.sources == []
    assert llm.calls == []


def test_llm_can_declare_lack_of_evidence() -> None:
    llm = ScriptedLLM("SEM_EVIDENCIA")
    service = build_service(llm, rent_chunks())

    response = service.ask(QueryRequest(question="Como pedir apoio ao aluguel?"))

    assert response.answer == NO_EVIDENCE_MESSAGE
    assert response.sources == []
    assert len(llm.calls) == 1


def test_empty_index_answers_without_evidence() -> None:
    llm = ScriptedLLM("não deveria ser chamado")
    service = build_service(llm, [])

    response = service.ask(QueryRequest(question="Qualquer pergunta"))

    assert response.answer == NO_EVIDENCE_MESSAGE
    assert llm.calls == []


def test_location_filter_is_applied_before_answering() -> None:
    chunks = [
        make_chunk(
            EMBEDDER,
            document_id=1,
            opportunity_id=10,
            content="auxílio aluguel moradia",
            region_level="city",
            region_state="SP",
            region_name="Campinas",
        )
    ]
    llm = ScriptedLLM("não deveria ser chamado")
    service = build_service(llm, chunks)

    response = service.ask(
        QueryRequest(question="auxílio aluguel moradia", state="SP", municipality="Santos")
    )

    assert response.answer == NO_EVIDENCE_MESSAGE
    assert llm.calls == []
