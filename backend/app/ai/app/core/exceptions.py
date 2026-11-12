class AIServiceError(Exception):
    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ConfigurationError(AIServiceError):
    status_code = 500
    code = "configuration_error"


class AuthenticationError(AIServiceError):
    status_code = 401
    code = "unauthorized"


class ProviderError(AIServiceError):
    status_code = 503
    code = "provider_unavailable"


class StoreError(AIServiceError):
    status_code = 503
    code = "store_unavailable"
