import CardCategory from "@/components/card-category";
import CardService from "@/components/card-service";
import { theme } from "@/styles/theme";

import { ScrollView, StyleSheet, Text, View } from "react-native";

export default function Home() {
  return (
    <ScrollView
      style={styles.screen}
      showsVerticalScrollIndicator={false}
    >
      <View className="w-full px-8 mb-3">
        <Text style={styles.title}>
          Categorias mais acessadas
        </Text>
        <CardCategory limit={6} sort="popularity" />
      </View>

      <View className="w-full px-8 mb-3">
        <Text style={styles.title}>Serviços mais acessados</Text>
        <CardService limit={5} />
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  title: {
    fontSize: theme.typography.title.fontSize,
    color: theme.colors.primary,
    fontWeight: theme.typography.title.fontWeight,
    lineHeight: theme.typography.title.lineHeight,
    marginBottom: theme.typography.title.marginBottom,
    marginTop: theme.typography.title.marginTop,
  }
});