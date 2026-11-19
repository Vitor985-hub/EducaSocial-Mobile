import { requestApi } from "@/services/api";

export type ProgramCategory =
  | "renda"
  | "educacao"
  | "saude"
  | "moradia"
  | "alimentacao"
  | "trabalho"
  | "mobilidade"
  | "assistencia_social"
  | "atendimento_ao_cidadao";

export type ProgramSummary = {
  id: number;
  name: string;
  summary: string;
  category: ProgramCategory;
  scope: "nacional" | "estadual" | "municipal";
  state: string | null;
  municipality: string | null;
};

export type ProgramDetail = ProgramSummary & {
  description: string;
  managing_body: string;
  eligibility: string[];
  how_to_apply: string;
  official_url: string | null;
};

export type ProgramCategoryCard = {
  id: ProgramCategory;
  name: string;
};

export const categoryLabels: Record<ProgramCategory, string> = {
  renda: "Renda",
  educacao: "Educação",
  saude: "Saúde",
  moradia: "Moradia",
  alimentacao: "Alimentação",
  trabalho: "Trabalho",
  mobilidade: "Mobilidade",
  assistencia_social: "Assistência Social",
  atendimento_ao_cidadao: "Atendimento ao Cidadão",
};

export function getProgramCategories(
  programs: ProgramSummary[],
): ProgramCategoryCard[] {
  const categories = new Set(programs.map((program) => program.category));
  return Array.from(categories, (id) => ({
    id,
    name: categoryLabels[id],
  }));
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isProgramCategory(value: unknown): value is ProgramCategory {
  return (
    typeof value === "string" &&
    Object.prototype.hasOwnProperty.call(categoryLabels, value)
  );
}

function isProgramSummary(value: unknown): value is ProgramSummary {
  return (
    isRecord(value) &&
    typeof value.id === "number" &&
    typeof value.name === "string" &&
    typeof value.summary === "string" &&
    isProgramCategory(value.category) &&
    (value.scope === "nacional" ||
      value.scope === "estadual" ||
      value.scope === "municipal") &&
    (value.state === null || typeof value.state === "string") &&
    (value.municipality === null || typeof value.municipality === "string")
  );
}

function isProgramDetail(value: unknown): value is ProgramDetail {
  if (!isRecord(value)) {
    return false;
  }

  const detail = value;
  if (!isProgramSummary(value)) {
    return false;
  }

  return (
    typeof detail.description === "string" &&
    typeof detail.managing_body === "string" &&
    Array.isArray(detail.eligibility) &&
    detail.eligibility.every((item: unknown) => typeof item === "string") &&
    typeof detail.how_to_apply === "string" &&
    (detail.official_url === null || typeof detail.official_url === "string")
  );
}

function parseProgramPage(value: unknown): {
  items: ProgramSummary[];
  totalPages: number;
} {
  if (
    !isRecord(value) ||
    !Array.isArray(value.items) ||
    !value.items.every(isProgramSummary) ||
    typeof value.total_pages !== "number" ||
    !Number.isInteger(value.total_pages) ||
    value.total_pages < 0
  ) {
    throw new Error("A resposta do catálogo veio em um formato inválido.");
  }

  return { items: value.items, totalPages: value.total_pages };
}

async function fetchPrograms(): Promise<ProgramSummary[]> {
  const pageSize = 100;
  const firstPage = parseProgramPage(
    await requestApi(`/api/v1/programs?page=1&page_size=${pageSize}`),
  );
  const programs = [...firstPage.items];

  for (let page = 2; page <= firstPage.totalPages; page += 1) {
    const nextPage = parseProgramPage(
      await requestApi(`/api/v1/programs?page=${page}&page_size=${pageSize}`),
    );
    programs.push(...nextPage.items);
  }

  return programs;
}

let programsCache: ProgramSummary[] | undefined;
let programsRequest: Promise<ProgramSummary[]> | undefined;

export function getPrograms(): Promise<ProgramSummary[]> {
  if (programsCache) {
    return Promise.resolve(programsCache);
  }
  if (!programsRequest) {
    programsRequest = fetchPrograms()
      .then((programs) => {
        programsCache = programs;
        return programs;
      })
      .catch((error: unknown) => {
        programsRequest = undefined;
        throw error;
      });
  }
  return programsRequest;
}

export async function getProgramDetail(programId: number): Promise<ProgramDetail> {
  const detail = await requestApi(`/api/v1/programs/${programId}`);
  if (!isProgramDetail(detail)) {
    throw new Error("Os detalhes do serviço vieram em um formato inválido.");
  }
  return detail;
}

export const regions = [
  { id: 1, name: "Brasil", stateCode: null },
  { id: 2, name: "Acre", stateCode: "AC" },
  { id: 3, name: "Alagoas", stateCode: "AL" },
  { id: 4, name: "Amapá", stateCode: "AP" },
  { id: 5, name: "Amazonas", stateCode: "AM" },
  { id: 6, name: "Bahia", stateCode: "BA" },
  { id: 7, name: "Ceará", stateCode: "CE" },
  { id: 8, name: "Distrito Federal", stateCode: "DF" },
  { id: 9, name: "Espírito Santo", stateCode: "ES" },
  { id: 10, name: "Goiás", stateCode: "GO" },
  { id: 11, name: "Maranhão", stateCode: "MA" },
  { id: 12, name: "Mato Grosso", stateCode: "MT" },
  { id: 13, name: "Mato Grosso do Sul", stateCode: "MS" },
  { id: 14, name: "Minas Gerais", stateCode: "MG" },
  { id: 15, name: "Pará", stateCode: "PA" },
  { id: 16, name: "Paraíba", stateCode: "PB" },
  { id: 17, name: "Paraná", stateCode: "PR" },
  { id: 18, name: "Pernambuco", stateCode: "PE" },
  { id: 19, name: "Piauí", stateCode: "PI" },
  { id: 20, name: "Rio de Janeiro", stateCode: "RJ" },
  { id: 21, name: "Rio Grande do Norte", stateCode: "RN" },
  { id: 22, name: "Rio Grande do Sul", stateCode: "RS" },
  { id: 23, name: "Rondônia", stateCode: "RO" },
  { id: 24, name: "Roraima", stateCode: "RR" },
  { id: 25, name: "Santa Catarina", stateCode: "SC" },
  { id: 26, name: "São Paulo", stateCode: "SP" },
  { id: 27, name: "Sergipe", stateCode: "SE" },
  { id: 28, name: "Tocantins", stateCode: "TO" },
] as const;

/*
 * Catálogo mockado antigo, mantido apenas como referência para testes manuais.
 * Os cards usam exclusivamente os dados de GET /api/v1/programs.
 *
 * export const mockCategories = [
 *   { id: 1, name: "Assistência Social" },
 *   { id: 2, name: "Atendimento ao Cidadão" },
 *   { id: 3, name: "Educação" },
 *   { id: 4, name: "Mobilidade" },
 *   { id: 5, name: "Moradia" },
 *   { id: 6, name: "Renda" },
 *   { id: 7, name: "Trabalho" },
 * ];
 *
 * export const mockServices = [
 *   {
 *     id: 1,
 *     categoryId: 6,
 *     name: "CadÚnico — Cadastro Único (Prefeitura de São Paulo)",
 *     description: "O CadÚnico reúne as famílias de baixa renda do país e permite participar de programas sociais.",
 *     regions: 26,
 *   },
 *   {
 *     id: 2,
 *     categoryId: 1,
 *     name: "Bolsa Família",
 *     description: "Programa federal de transferência de renda.",
 *     regions: 1,
 *   },
 *   {
 *     id: 3,
 *     categoryId: 6,
 *     name: "BPC — Benefício de Prestação Continuada",
 *     description: "Benefício assistencial para pessoas com deficiência e idosos.",
 *     regions: 1,
 *   },
 *   {
 *     id: 4,
 *     categoryId: 5,
 *     name: "Tarifa Social de Energia Elétrica",
 *     description: "Desconto na conta de energia para famílias de baixa renda.",
 *     regions: 1,
 *   },
 *   {
 *     id: 5,
 *     categoryId: 5,
 *     name: "Tarifa Social de Água",
 *     description: "Desconto na conta de água para famílias de baixa renda.",
 *     regions: 1,
 *   },
 *   {
 *     id: 6,
 *     categoryId: 4,
 *     name: "Bilhete Único da Pessoa Idosa — gratuidade no transporte (SPTrans)",
 *     description: "Gratuidade no transporte público municipal para pessoas idosas.",
 *     regions: 26,
 *   },
 *   {
 *     id: 7,
 *     categoryId: 4,
 *     name: "Atende+ — transporte porta a porta gratuito (SPTrans)",
 *     description: "Transporte gratuito para pessoas com deficiência ou mobilidade reduzida.",
 *     regions: 26,
 *   },
 *   {
 *     id: 8,
 *     categoryId: 3,
 *     name: "Bilhete Único de Estudante (SPTrans)",
 *     description: "Benefício de transporte público para estudantes.",
 *     regions: 26,
 *   },
 * ];
 */
