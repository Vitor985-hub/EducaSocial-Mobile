import argparse
import sys

from pydantic import ValidationError

from app.ai.container import build_rag_service
from app.ai.core.config import get_settings
from app.ai.core.exceptions import AIServiceError
from app.ai.schemas.query import QueryRequest


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m app.ai.tools.ask")
    parser.add_argument("question")
    parser.add_argument("--state")
    parser.add_argument("--municipality")
    args = parser.parse_args()
    try:
        request = QueryRequest(
            question=args.question, state=args.state, municipality=args.municipality
        )
        response = build_rag_service(get_settings()).ask(request)
    except ValidationError as exc:
        print(f"Parâmetros inválidos: {exc.errors()[0]['msg']}", file=sys.stderr)
        return 1
    except AIServiceError as exc:
        print(f"Erro: {exc.message}", file=sys.stderr)
        return 1
    print(response.answer)
    if response.sources:
        print("\nFontes:")
        for source in response.sources:
            print(f"- {source.title} (programa {source.program_id}) {source.url or ''}".rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
