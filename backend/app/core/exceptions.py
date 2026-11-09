class AppError(Exception):
    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ProgramNotFoundError(NotFoundError):
    def __init__(self, program_id: int) -> None:
        super().__init__(f"Programa {program_id} não encontrado.")


class InvalidFilterError(AppError):
    status_code = 422
    code = "invalid_filter"


class AIServiceUnavailableError(AppError):
    status_code = 503
    code = "ai_unavailable"
