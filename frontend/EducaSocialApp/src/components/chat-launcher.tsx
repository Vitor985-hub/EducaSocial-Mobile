import { router, usePathname } from "expo-router";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { theme } from "@/styles/theme";

export default function ChatLauncher() {
  const pathname = usePathname();

  if (pathname === "/pages/chat/chat") {
    return null;
  }

  return (
    <SafeAreaView
      edges={["bottom"]}
      className="px-5 pt-2"
      style={styles.screen}
    >
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Abrir conversa com o assistente"
        onPress={() => router.push("/pages/chat/chat")}
        className="min-h-12 flex-row items-center rounded-full border px-4"
        style={styles.launcher}
      >
        <Text className="mr-3" style={styles.icon}>
          ✦
        </Text>
        <Text className="flex-1" style={styles.label}>
          Clique aqui para perguntar
        </Text>
        <View
          className="h-8 w-8 items-center justify-center rounded-full"
          style={styles.sendButton}
        >
          <Text style={styles.sendIcon}>↑</Text>
        </View>
      </Pressable>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: {
    backgroundColor: theme.colors.background,
  },
  launcher: {
    backgroundColor: theme.colors.surface,
    borderColor: theme.colors.border,
  },
  icon: {
    fontSize: theme.fontSizes.xl,
    color: theme.colors.primary,
  },
  label: {
    fontSize: theme.fontSizes.md,
    color: theme.colors.textSecondary,
  },
  sendButton: {
    backgroundColor: theme.colors.primary,
  },
  sendIcon: {
    fontSize: theme.fontSizes.md,
    color: theme.colors.onPrimary,
  },
});
