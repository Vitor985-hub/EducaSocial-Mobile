import argparse
import json
import sys
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.ai.container import build_repository
from app.ai.core.config import get_settings
from app.ai.core.exceptions import AIServiceError
from app.ai.providers.base import EmbeddingProvider
from app.ai.providers.factory import build_embedding_provider, build_llm_provider
from app.ai.schemas.query import QueryRequest
from app.ai.services.prompts import NO_EVIDENCE_MESSAGE
from app.ai.services.rag_service import RagService
from app.ai.services.retrieval import ChunkIndexProvider, VectorIndex

REFUSAL_EXPECTED = {"no_evidence", "no_evidence_ok", "fora_do_lote"}


@dataclass(frozen=True, slots=True)
class Row:
    question: str
    expect: str
    verdict: str
    detail: str
    score: float | None = None
    matched: bool = False


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def expected_titles(case: dict[str, Any], programs: dict[str, dict[str, Any]]) -> set[str]:
    return {programs[key]["title"] for key in case["expected_programs"] if key in programs}


def expected_urls(case: dict[str, Any], programs: dict[str, dict[str, Any]]) -> set[str]:
    urls: set[str] = set()
    for key in case["expected_programs"]:
        program = programs.get(key)
        if program is None:
            continue
        for source in [program["source"]] if "source" in program else program.get("sources", []):
            urls.add(source["url"])
    return urls


def evaluate_retrieval(
    index: VectorIndex,
    embedder: EmbeddingProvider,
    cases: Sequence[dict[str, Any]],
    programs: dict[str, dict[str, Any]],
    min_score: float,
    delay: float = 0.0,
    sleep: Callable[[float], None] = time.sleep,
) -> list[Row]:
    rows: list[Row] = []
    for position, case in enumerate(cases):
        if position and delay:
            sleep(delay)
        expect = case["expect"]
        try:
            query_vector = embedder.embed_query(case["question"])
        except AIServiceError as exc:
            rows.append(Row(case["question"], expect, "ERRO", exc.message))
            continue
        hits = index.search(
            query_vector,
            case.get("state"),
            case.get("municipality"),
            max(len(index), 1),
            -0.99,
        )
        if not hits:
            rows.append(Row(case["question"], expect, "sem trechos", "nenhum trecho no filtro"))
            continue
        top = hits[0]
        passes = top.score >= min_score
        wanted = expected_titles(case, programs)
        available = {hit.chunk.opportunity_title for hit in hits}
        matched = top.chunk.opportunity_title in wanted
        if expect in REFUSAL_EXPECTED:
            verdict = "ok" if not passes else "depende do LLM"
        elif not wanted & available:
            verdict = "FALHA: programa não está no banco"
        elif not passes:
            verdict = "FALHA: abaixo do corte"
        elif not matched:
            verdict = "FALHA: programa errado"
        else:
            verdict = "ok"
        rows.append(
            Row(
                case["question"],
                expect,
                verdict,
                top.chunk.opportunity_title,
                score=top.score,
                matched=matched,
            )
        )
    return rows


def evaluate_generation(
    service: RagService,
    cases: Sequence[dict[str, Any]],
    programs: dict[str, dict[str, Any]],
    delay: float = 0.0,
    sleep: Callable[[float], None] = time.sleep,
) -> list[Row]:
    rows: list[Row] = []
    for position, case in enumerate(cases):
        if position and delay:
            sleep(delay)
        try:
            response = service.ask(
                QueryRequest(
                    question=case["question"],
                    state=case.get("state"),
                    municipality=case.get("municipality"),
                )
            )
        except AIServiceError as exc:
            rows.append(Row(case["question"], case["expect"], "ERRO", exc.message))
            continue
        refused = response.answer == NO_EVIDENCE_MESSAGE
        urls = {source.url for source in response.sources}
        expect = case["expect"]
        if expect == "answer":
            if refused:
                verdict = "FALHA: recusou"
            elif not urls & expected_urls(case, programs):
                verdict = "FALHA: fonte errada"
            else:
                verdict = "ok"
        elif expect == "no_evidence":
            verdict = "ok" if refused else "FALHA: respondeu"
        else:
            verdict = "ok" if refused else "revisar resposta"
        detail = "recusou" if refused else response.answer.replace("\n", " ")[:90]
        rows.append(Row(case["question"], expect, verdict, detail))
    return rows


def calibration_summary(rows: Sequence[Row]) -> str:
    answered = [
        row.score
        for row in rows
        if row.expect == "answer" and row.matched and row.score is not None
    ]
    refused = [
        row.score for row in rows if row.expect in REFUSAL_EXPECTED and row.score is not None
    ]
    if not answered or not refused:
        return "Corte: não há perguntas suficientes dos dois tipos para sugerir."
    lowest, highest = min(answered), max(refused)
    if highest < lowest:
        return (
            f"Corte: maior score entre as que devem recusar = {highest:.3f}; "
            f"menor entre as que devem responder = {lowest:.3f}. "
            f"Qualquer valor nessa faixa separa os dois grupos."
        )
    return (
        f"Corte: há sobreposição. Perguntas para recusar chegam a {highest:.3f} e "
        f"perguntas para responder caem até {lowest:.3f}. Nenhum corte separa tudo; "
        f"a recusa do LLM precisa cobrir o resto."
    )


def format_rows(rows: Sequence[Row]) -> list[str]:
    lines = []
    for row in rows:
        score = f"{row.score:.3f}" if row.score is not None else "  -  "
        lines.append(f"{score} {row.verdict:<34} [{row.expect}] {row.question} -> {row.detail}")
    failures = sum(row.verdict.startswith("FALHA") for row in rows)
    errors = sum(row.verdict == "ERRO" for row in rows)
    review = sum(row.verdict in {"depende do LLM", "revisar resposta"} for row in rows)
    lines.append(
        f"\n{len(rows)} perguntas | {failures} falhas | {errors} erros | {review} para revisar"
    )
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m app.ai.tools.evaluate")
    parser.add_argument("--cases", default="data/avaliacao_lote1.json")
    parser.add_argument("--programs", default="data/lote1_programas.json")
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--delay", type=float, default=None)
    args = parser.parse_args()
    settings = get_settings()
    delay = args.delay if args.delay is not None else (6.0 if args.generate else 0.0)
    try:
        cases = load_json(Path(args.cases))["perguntas"]
        programs = {item["key"]: item for item in load_json(Path(args.programs))["programas"]}
        embedder = build_embedding_provider(settings)
        provider = ChunkIndexProvider(
            build_repository(settings), embedder.model_name, settings.index_ttl_seconds
        )
        if args.generate:
            service = RagService(
                embedder,
                build_llm_provider(settings),
                provider,
                settings.retrieval_top_k,
                settings.retrieval_min_score,
            )
            rows = evaluate_generation(service, cases, programs, delay)
        else:
            rows = evaluate_retrieval(
                provider.get(), embedder, cases, programs, settings.retrieval_min_score, delay
            )
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        print(
            f"Não foi possível ler os arquivos de avaliação: {type(exc).__name__}", file=sys.stderr
        )
        return 1
    except AIServiceError as exc:
        print(f"Erro: {exc.message}", file=sys.stderr)
        return 1
    print(f"Modelo: {embedder.model_name} | corte: {settings.retrieval_min_score}")
    print("\n".join(format_rows(rows)))
    if not args.generate:
        print(calibration_summary(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
