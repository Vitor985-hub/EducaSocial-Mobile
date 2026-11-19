import { useState } from "react";
import MaterialCommunityIcons from "@expo/vector-icons/MaterialCommunityIcons";
import { router, useLocalSearchParams } from "expo-router";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import CardService from "@/components/card-service";
import SearchBar from "@/components/search-bar";
import { useCatalog } from "@/hooks/catalog/useCatalog";
import { theme } from "@/styles/theme";

export default function CategoryServices() {
  const { categoryId, serviceId } = useLocalSearchParams<{
    categoryId: string;
    serviceId?: string;
  }>();
  const [searchQuery, setSearchQuery] = useState("");
  const { categories, loading, error, retry } = useCatalog();
  const selectedCategory = categories.find(
    (category) => category.id === categoryId,
  );

  return (
    <SafeAreaView className="flex-1" style={styles.screen}>
      <ScrollView
        className="flex-1"
        contentContainerStyle={{ paddingBottom: 32 }}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        <View className="w-full px-8">
          <View className="mb-4 mt-5 flex-row items-center gap-3">
            <Pressable
              accessibilityLabel="Voltar"
              accessibilityRole="button"
              onPress={() => router.back()}
              style={styles.backButton}
            >
              <MaterialCommunityIcons
                name="arrow-left"
                size={20}
                color={theme.colors.primary}
              />
            </Pressable>
            <SearchBar
              value={searchQuery}
              onChangeText={setSearchQuery}
              placeholder="Pesquisar serviço"
            />
          </View>

          {loading ? (
            <Text style={styles.body}>
              Carregando categoria...
            </Text>
          ) : error ? (
            <View>
              <Text style={styles.error}>{error}</Text>
              <Pressable
                accessibilityRole="button"
                onPress={retry}
                className="mt-2 self-start rounded-full px-4 py-2"
                style={styles.primaryButton}
              >
                <Text style={styles.primaryButtonLabel}>
                  Tentar novamente
                </Text>
              </Pressable>
            </View>
          ) : selectedCategory ? (
            <>
              <Text style={styles.title}>
                {selectedCategory.name}
              </Text>
              <Text className="mt-1" style={styles.body}>
                Serviços disponíveis nesta categoria
              </Text>
              <CardService
                categoryId={selectedCategory.id}
                searchQuery={searchQuery}
                initialServiceId={
                  serviceId ? Number(serviceId) : undefined
                }
              />
            </>
          ) : (
            <Text style={styles.body}>
              Categoria não encontrada.
            </Text>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: {
    backgroundColor: theme.colors.background,
  },
  backButton: {
    width: 34,
    height: 34,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: theme.colors.primary,
    borderRadius: 17,
  },
  body: {
    ...theme.typography.body,
    color: theme.colors.textSecondary,
  },
  title: {
    fontSize: theme.typography.title.fontSize,
    lineHeight: theme.typography.title.lineHeight,
    fontWeight: theme.typography.title.fontWeight,
    color: theme.colors.primary,
  },
  error: {
    fontSize: theme.fontSizes.md,
    color: theme.colors.error,
  },
  primaryButton: {
    backgroundColor: theme.colors.primary,
  },
  primaryButtonLabel: {
    ...theme.typography.button,
  },
});