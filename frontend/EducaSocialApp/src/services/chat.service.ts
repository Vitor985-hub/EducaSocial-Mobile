import {
  categoryLabels,
  type ProgramCategory,
  type ProgramSummary,
} from "@/services/catalog";
import { requestApi } from "@/services/api";
import type { AssistantReply, AssistantSource, ChatService } from "@/types/chat/chat.types";

const categoryIntents: { terms: string[]; categories: ProgramCategory[] }[] = [
  {
    terms: [
      "beneficio",
      "beneficios",
      "renda",
      "baixa renda",
      "cadunico",
      "assistencia social",
    ],
    categories: ["renda", "assistencia_social"],
  },
  { terms: ["transporte", "mobilidade", "passagem"], categories: ["mobilidade"] },
  { terms: ["estudo", "estudante", "escola"], categories: ["educacao"] },
  {
    terms: ["cidadao", "documento", "atendimento ao cidadao"],
    categories: ["atendimento_ao_cidadao"],
  },
  { terms: ["moradia", "agua", "energia", "luz"], categories: ["moradia"] },
  { terms: ["comida", "alimento", "alimentacao"], categories: ["alimentacao"] },
  { terms: ["saude", "atendimento medico"], categories: ["saude"] },
  { terms: ["trabalho", "emprego", "qualificacao"], categories: ["trabalho"] },
];

const ignoredWords = new Set([
  "ajuda",
  "como",
  "com",
  "da",
  "das",
  "de",
  "do",
  "dos",
  "e",
  "eu",
  "me",
  "o",
  "para",
  "preciso",
  "que",
  "qual",
  "quais",
  "quero",
  "sobre",
  "um",
  "uma",
]);

function normalize(value: string) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

export function getCatalogSuggestions(
  message: string,
  programs: ProgramSummary[],
): ChatService[] {
  const normalizedMessage = normalize(message);
  const words = normalizedMessage
    .split(/[^a-z0-9]+/)
    .filter((word) => word.length > 2 && !ignoredWords.has(word));
  const intents = categoryIntents.filter(({ terms }) =>
    terms.some((term) => normalizedMessage.includes(term)),
  );

  return programs
    .map((program) => {
      const categoryName = normalize(categoryLabels[program.category]);
      const programName = normalize(program.name);
      const summary = normalize(program.summary);
      let score = 0;

      for (const word of words) {
        if (programName.includes(word)) score += 4;
        if (categoryName.includes(word)) score += 2;
        if (summary.includes(word)) score += 1;
      }

      if (intents.some(({ categories }) => categories.includes(program.category))) {
        score += 3;
      }

      return { program, score };
    })
    .filter(({ score }) => score > 0)
    .sort((left, right) => right.score - left.score || left.program.id - right.program.id)
    .slice(0, 3)
    .map(({ program }) => program);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isAssistantSource(value: unknown): value is AssistantSource {
  if (!isRecord(value) || typeof value.title !== "string") {
    return false;
  }

  return (
    (value.program_id === undefined ||
      value.program_id === null ||
      typeof value.program_id === "number") &&
    (value.url === undefined || value.url === null || typeof value.url === "string")
  );
}

function isAssistantReply(value: unknown): value is AssistantReply {
  return (
    isRecord(value) &&
    typeof value.answer === "string" &&
    Array.isArray(value.sources) &&
    value.sources.every(isAssistantSource)
  );
}

export async function askAssistant(question: string): Promise<AssistantReply> {
  const payload = await requestApi("/api/v1/assistant/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!isAssistantReply(payload)) {
    throw new Error("A resposta do assistente veio em um formato inválido.");
  }

  return payload;
}