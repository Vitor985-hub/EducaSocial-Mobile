import Stack from "expo-router/stack";
import { StyleSheet, View } from "react-native";
import ChatLauncher from "../components/chat-launcher";
import { PopularityProvider } from "@/hooks/popularity/PopularityProvider";
import { theme } from "@/styles/theme";
import "../styles/global.css";

export default function RootLayout() {
  return (
    <PopularityProvider>
      <View style={styles.container}>
        <Stack screenOptions={{ headerShown: false }} />
        <ChatLauncher />
      </View>
    </PopularityProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
});
