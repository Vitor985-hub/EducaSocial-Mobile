from app.core.exceptions import InvalidFilterError

BRAZILIAN_STATES = frozenset(
    "AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split()
)


def validate_location(state: str | None, municipality: str | None) -> tuple[str | None, str | None]:
    normalized_state = state.strip().upper() if state else None
    normalized_municipality = municipality.strip() if municipality else None

    if normalized_state is not None and normalized_state not in BRAZILIAN_STATES:
        raise InvalidFilterError(f"UF inválida: '{state}'.")
    if normalized_municipality and normalized_state is None:
        raise InvalidFilterError("O filtro 'municipality' exige o filtro 'state'.")

    return normalized_state, normalized_municipality or None
