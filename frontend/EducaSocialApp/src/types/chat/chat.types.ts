import type { ProgramSummary } from "@/services/catalog";

export type ChatRole = "user" | "assistant";

export type ChatService = ProgramSummary;

export type AssistantSource = {
  title: string;
  program_id?: number | null;
  url?: string | null;
};

export type ChatMessage = {
  id: string;
  role: ChatRole;
  text: string;
  services?: ChatService[];
  serviceSuggestionError?: string;
  sources?: AssistantSource[];
};

export type AssistantReply = {
  answer: string;
  sources: AssistantSource[];
};