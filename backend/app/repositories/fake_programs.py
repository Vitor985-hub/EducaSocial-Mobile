from app.models.program import CoverageScope, Program, ProgramCategory

NAME_PREFIX = "[FICTÍCIO]"
FICTITIOUS_NOTICE = (
    "Dado fictício para desenvolvimento e testes; não representa um programa oficial."
)


def _build(
    program_id: int,
    name: str,
    summary: str,
    category: ProgramCategory,
    scope: CoverageScope,
    state: str | None = None,
    municipality: str | None = None,
) -> Program:
    return Program(
        id=program_id,
        name=f"{NAME_PREFIX} {name}",
        summary=summary,
        description=f"{FICTITIOUS_NOTICE} {summary}",
        category=category,
        scope=scope,
        state=state,
        municipality=municipality,
        managing_body="Órgão fictício",
        eligibility=(
            "Critério fictício de elegibilidade A.",
            "Critério fictício de elegibilidade B.",
        ),
        how_to_apply=(
            "Informação fictícia: o procedimento real de solicitação "
            "será definido com dados oficiais."
        ),
        official_url=None,
    )


FAKE_PROGRAMS: tuple[Program, ...] = (
    _build(
        1,
        "Auxílio Renda Exemplo",
        "Transferência de renda fictícia para famílias de baixa renda.",
        ProgramCategory.RENDA,
        CoverageScope.NACIONAL,
    ),
    _build(
        2,
        "Bolsa Estudo Exemplo",
        "Bolsa fictícia para estudantes de famílias de baixa renda.",
        ProgramCategory.EDUCACAO,
        CoverageScope.NACIONAL,
    ),
    _build(
        3,
        "Cuidado em Saúde Exemplo",
        "Atendimento de saúde fictício para a atenção básica.",
        ProgramCategory.SAUDE,
        CoverageScope.NACIONAL,
    ),
    _build(
        4,
        "Cesta Alimentar Estadual",
        "Cesta de alimentos fictícia distribuída no estado.",
        ProgramCategory.ALIMENTACAO,
        CoverageScope.ESTADUAL,
        state="SP",
    ),
    _build(
        5,
        "Qualificação Profissional Estadual",
        "Cursos fictícios de qualificação para o mercado de trabalho.",
        ProgramCategory.TRABALHO,
        CoverageScope.ESTADUAL,
        state="SP",
    ),
    _build(
        6,
        "Moradia Solidária Estadual",
        "Apoio habitacional fictício para famílias do estado.",
        ProgramCategory.MORADIA,
        CoverageScope.ESTADUAL,
        state="RJ",
    ),
    _build(
        7,
        "Transporte Estudantil Estadual",
        "Passe de transporte fictício para estudantes.",
        ProgramCategory.EDUCACAO,
        CoverageScope.ESTADUAL,
        state="MG",
    ),
    _build(
        8,
        "Material Escolar Estadual",
        "Kit de material escolar fictício para a rede estadual.",
        ProgramCategory.EDUCACAO,
        CoverageScope.ESTADUAL,
        state="BA",
    ),
    _build(
        9,
        "Refeição Popular Municipal",
        "Refeições fictícias a preço simbólico no município.",
        ProgramCategory.ALIMENTACAO,
        CoverageScope.MUNICIPAL,
        state="SP",
        municipality="São Paulo",
    ),
    _build(
        10,
        "Reforço Escolar Municipal",
        "Aulas de reforço fictícias para estudantes da rede municipal.",
        ProgramCategory.EDUCACAO,
        CoverageScope.MUNICIPAL,
        state="SP",
        municipality="Campinas",
    ),
    _build(
        11,
        "Apoio ao Aluguel Municipal",
        "Auxílio fictício para pagamento de aluguel no município.",
        ProgramCategory.MORADIA,
        CoverageScope.MUNICIPAL,
        state="SP",
        municipality="Santo André",
    ),
    _build(
        12,
        "Microcrédito Municipal",
        "Microcrédito fictício para pequenos empreendedores.",
        ProgramCategory.TRABALHO,
        CoverageScope.MUNICIPAL,
        state="RJ",
        municipality="Rio de Janeiro",
    ),
)
