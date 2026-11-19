import { router } from "expo-router";
import { useRef, useState } from "react";
import {
  KeyboardAvoidingView,
  Pressable,
  ScrollView,
  StyleSheet,
  type ScrollViewInstance,
  Text,
  TextInput,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useChat } from "@/hooks/chat/useChat";
import { usePopularity } from "@/hooks/popularity/PopularityProvider";
import { theme } from "@/styles/theme";
import type { ChatMessage, ChatService } from "@/types/chat/chat.types";

const quickQuestions = [
  "Quais benefícios ajudam famílias de baixa renda?",
  "Preciso de transporte gratuito",
  "Como funciona o CadÚnico?",
];

function ServiceSuggestion({
  service,
  onPress,
}: {
  service: ChatService;
  onPress: () => void;
}) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={`Ver ${service.name}`}
      onPress={onPress}
      className="mt-2 flex-row items-center justify-between rounded-2xl border p-3"
      style={styles.suggestionCard}
    >
      <View className="mr-3 flex-1">
        <Text style={styles.suggestionTitle}>{service.name}</Text>
        <Text className="mt-1" style={styles.caption} numberOfLines={2}>
          {service.summary}
        </Text>
      </View>
      <Text style={styles.chevron}>›</Text>
    </Pressable>
  );
}

function MessageBubble({
  message,
  onSelectService,
}: {
  message: ChatMessage;
  onSelectService: (service: ChatService) => void;
}) {
  const isUser = message.role === "user";

  return (
    <View className={`mb-4 max-w-[88%] ${isUser ? "self-end" : "self-start"}`}>
      <View
        className="rounded-3xl px-4 py-3"
        style={isUser ? styles.userBubble : styles.assistantBubble}
      >
        <Text style={isUser ? styles.userMessage : styles.assistantMessage}>
          {message.text}
        </Text>
      </View>
      {!isUser && Boolean(message.sources?.length) && (
        <View className="mt-2 rounded-2xl border p-3" style={styles.sourceCard}>
          <Text className="mb-1" style={styles.sourceHeading}>
            Fontes da resposta
          </Text>
          {message.sources?.map((source, index) => (
            <View key={`${message.id}-source-${index}`} className="py-1">
              <Text style={styles.caption}>{source.title}</Text>
              {source.url && (
                <Text style={styles.sourceUrl} numberOfLines={1}>
                  {source.url}
                </Text>
              )}
            </View>
          ))}
        </View>
      )}
      {!isUser &&
        message.services?.map((service) => (
          <ServiceSuggestion
            key={`${message.id}-${service.id}`}
            service={service}
            onPress={() => onSelectService(service)}
          />
        ))}
      {!isUser && message.serviceSuggestionError && (
        <Text className="mt-2" style={styles.serviceError}>
          Não foi possível carregar sugestões de serviços:{" "}
          {message.serviceSuggestionError}
        </Text>
      )}
    </View>
  );
}

export default function Chat() {
  const {
    messages,
    sendMessage,
    retryLastMessage,
    isSending,
    error,
  } = useChat();
  const { recordCategoryAccess, recordServiceAccess } = usePopularity();
  const [draft, setDraft] = useState("");
  const scrollViewRef = useRef<ScrollViewInstance | null>(null);

  function submitMessage(text = draft) {
    if (!text.trim()) {
      return;
    }

    sendMessage(text);
    setDraft("");
  }

  function openService(service: ChatService) {
    recordServiceAccess(service.id);
    recordCategoryAccess(service.category);
    router.push({
      pathname: "/pages/categories/[categoryId]",
      params: {
        categoryId: service.category,
        serviceId: String(service.id),
      },
    });
  }

  return (
    <SafeAreaView className="flex-1" style={styles.screen}>
      <KeyboardAvoidingView
        className="flex-1"
        behavior="padding"
      >
        <View className="flex-1">
          <View
            className="flex-row items-center border-b px-5 py-3"
            style={styles.header}
          >
            <Pressable
              accessibilityRole="button"
              accessibilityLabel="Voltar"
              onPress={() => router.back()}
              className="mr-3 h-10 w-10 items-center justify-center rounded-full border"
              style={styles.backButton}
            >
              <Text style={styles.backIcon}>←</Text>
            </Pressable>
            <View className="flex-1">
              <Text style={styles.headerTitle}>
                Chat de dúvidas com IA
              </Text>
              <Text style={styles.caption}>
                Respostas baseadas nos serviços do app
              </Text>
            </View>
            <Text style={styles.headerSparkle}>✦</Text>
          </View>

          <ScrollView
            ref={scrollViewRef}
            className="flex-1 px-5 pt-5"
            contentContainerStyle={{ paddingBottom: 16 }}
            keyboardShouldPersistTaps="handled"
            showsVerticalScrollIndicator={false}
            onContentSizeChange={() =>
              scrollViewRef.current?.scrollToEnd({ animated: true })
            }
          >
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                onSelectService={openService}
              />
            ))}

            {isSending && (
              <View
                className="mb-4 self-start rounded-3xl px-4 py-3"
                style={styles.assistantBubble}
              >
                <Text style={styles.assistantMessage}>
                  Consultando o assistente...
                </Text>
              </View>
            )}

            {error && (
              <View
                accessibilityRole="alert"
                className="mb-4 rounded-2xl border p-4"
                style={styles.errorCard}
              >
                <Text style={styles.errorMessage}>{error}</Text>
                <Pressable
                  accessibilityRole="button"
                  disabled={isSending}
                  onPress={retryLastMessage}
                  className="mt-2 self-start"
                >
                  <Text style={styles.errorAction}>
                    Tentar novamente
                  </Text>
                </Pressable>
              </View>
            )}

            {messages.length === 1 && (
              <View className="mt-1">
                <Text className="mb-2" style={styles.caption}>
                  Sugestões para começar
                </Text>
                {quickQuestions.map((question) => (
                  <Pressable
                    key={question}
                    accessibilityRole="button"
                    disabled={isSending}
                    onPress={() => submitMessage(question)}
                    className="mb-2 self-start rounded-full border px-4 py-2"
                    style={styles.quickQuestion}
                  >
                    <Text style={styles.caption}>{question}</Text>
                  </Pressable>
                ))}
              </View>
            )}
          </ScrollView>

          <View
            className="flex-row items-end border-t px-4 py-3"
            style={styles.composer}
          >
            <TextInput
              accessibilityLabel="Escreva sua pergunta"
              value={draft}
              onChangeText={setDraft}
              onSubmitEditing={() => submitMessage()}
              placeholder="Escreva sua pergunta..."
              editable={!isSending}
              maxLength={1000}
              returnKeyType="send"
              className="mr-3 max-h-24 min-h-11 flex-1 rounded-2xl px-4 py-3"
              placeholderTextColor={theme.colors.textMuted}
              style={styles.input}
            />
            <Pressable
              accessibilityRole="button"
              accessibilityLabel="Enviar pergunta"
              disabled={!draft.trim() || draft.trim().length < 3 || isSending}
              onPress={() => submitMessage()}
              className="h-11 w-11 items-center justify-center rounded-full"
              style={
                draft.trim().length >= 3 && !isSending
                  ? styles.sendButton
                  : styles.sendButtonDisabled
              }
            >
              <Text style={styles.sendIcon}>↑</Text>
            </Pressable>
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: {
    backgroundColor: theme.colors.background,
  },
  suggestionCard: {
    backgroundColor: theme.colors.surface,
    borderColor: theme.colors.borderSubtle,
  },
  suggestionTitle: {
    fontSize: theme.fontSizes.sm,
    fontWeight: "700",
    color: theme.colors.textPrimary,
  },
  caption: {
    ...theme.typography.caption,
  },
  chevron: {
    fontSize: theme.fontSizes.lg,
    fontWeight: "700",
    color: theme.colors.primary,
  },
  userBubble: {
    backgroundColor: theme.colors.primary,
  },
  assistantBubble: {
    backgroundColor: theme.colors.surfaceMuted,
  },
  userMessage: {
    ...theme.typography.body,
    color: theme.colors.onPrimary,
  },
  assistantMessage: {
    ...theme.typography.body,
    color: theme.colors.textPrimary,
  },
  sourceCard: {
    backgroundColor: theme.colors.surface,
    borderColor: theme.colors.borderSubtle,
  },
  sourceHeading: {
    ...theme.typography.caption,
    fontWeight: "700",
    color: theme.colors.textPrimary,
  },
  sourceUrl: {
    ...theme.typography.caption,
    color: theme.colors.primary,
  },
  serviceError: {
    ...theme.typography.caption,
    color: theme.colors.error,
  },
  header: {
    borderBottomColor: theme.colors.border,
  },
  backButton: {
    borderColor: theme.colors.border,
  },
  backIcon: {
    fontSize: theme.fontSizes.xl,
    color: theme.colors.primary,
  },
  headerTitle: {
    fontSize: theme.fontSizes.md,
    fontWeight: "700",
    color: theme.colors.primary,
  },
  headerSparkle: {
    fontSize: theme.fontSizes.xl,
    color: theme.colors.primary,
  },
  errorCard: {
    backgroundColor: theme.colors.errorSurface,
    borderColor: theme.colors.error,
  },
  errorMessage: {
    fontSize: theme.fontSizes.sm,
    color: theme.colors.error,
  },
  errorAction: {
    fontSize: theme.fontSizes.sm,
    fontWeight: "700",
    color: theme.colors.error,
  },
  quickQuestion: {
    backgroundColor: theme.colors.surface,
    borderColor: theme.colors.borderSubtle,
  },
  composer: {
    backgroundColor: theme.colors.surface,
    borderTopColor: theme.colors.borderSubtle,
  },
  input: {
    backgroundColor: theme.colors.surfaceMuted,
    fontSize: theme.fontSizes.sm,
    color: theme.colors.textPrimary,
  },
  sendButton: {
    backgroundColor: theme.colors.primary,
  },
  sendButtonDisabled: {
    backgroundColor: theme.colors.secondary,
  },
  sendIcon: {
    fontSize: theme.fontSizes.lg,
    color: theme.colors.onPrimary,
  },
});