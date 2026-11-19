import { useRef, useState } from "react";
import { askAssistant, getCatalogSuggestions } from "@/services/chat.service";
import { getPrograms } from "@/services/catalog";
import type { ChatMessage, ChatService } from "@/types/chat/chat.types";

const welcomeMessage: ChatMessage = {
  id: "welcome",
  role: "assistant",
  text: "Olá! Posso ajudar você a encontrar serviços e benefícios disponíveis no app. O que gostaria de saber?",
};

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([welcomeMessage]);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const nextId = useRef(1);
  const lastQuestion = useRef<string | null>(null);
  const requestInProgress = useRef(false);

  async function submitQuestion(message: string, addToHistory: boolean) {
    const text = message.trim();
    if (requestInProgress.current || !text) {
      return;
    }

    requestInProgress.current = true;
    lastQuestion.current = text;
    setError(null);
    setIsSending(true);

    if (addToHistory) {
      setMessages((currentMessages) => [
        ...currentMessages,
        { id: `user-${nextId.current++}`, role: "user", text },
      ]);
    }

    try {
      const reply = await askAssistant(text);
      let services: ChatService[] = [];
      let serviceSuggestionError: string | undefined;
      try {
        services = getCatalogSuggestions(text, await getPrograms());
      } catch (suggestionError) {
        serviceSuggestionError =
          suggestionError instanceof Error
            ? suggestionError.message
            : "Não foi possível carregar sugestões de serviços.";
      }

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: `assistant-${nextId.current++}`,
          role: "assistant",
          text: reply.answer,
          sources: reply.sources,
          services,
          serviceSuggestionError,
        },
      ]);
      lastQuestion.current = null;
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Não foi possível obter uma resposta do assistente.",
      );
    } finally {
      requestInProgress.current = false;
      setIsSending(false);
    }
  }

  function sendMessage(message: string) {
    const text = message.trim();
    if (text.length < 3) {
      setError("Digite uma pergunta com pelo menos 3 caracteres.");
      return;
    }

    if (text.length > 1000) {
      setError("A pergunta deve ter no máximo 1000 caracteres.");
      return;
    }

    void submitQuestion(text, true);
  }

  function retryLastMessage() {
    if (lastQuestion.current) {
      void submitQuestion(lastQuestion.current, false);
    }
  }

  return { messages, sendMessage, retryLastMessage, isSending, error };
}