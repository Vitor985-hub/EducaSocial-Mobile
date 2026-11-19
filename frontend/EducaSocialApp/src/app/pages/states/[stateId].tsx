import { useState } from "react";
import MaterialCommunityIcons from "@expo/vector-icons/MaterialCommunityIcons";
import { router, useLocalSearchParams } from "expo-router";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import CardService from "@/components/card-service";
import SearchBar from "@/components/search-bar";
import { regions } from "@/services/catalog";
import { theme } from "@/styles/theme";

export default function StateServices() {
  const { stateId } = useLocalSearchParams<{ stateId: string }>();
  const [searchQuery, setSearchQuery] = useState("");
  const selectedRegion = regions.find(
    (region) => region.id === Number(stateId),
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

          {selectedRegion ? (
            <>
              <Text style={styles.title}>
                Serviços em {selectedRegion.name}
              </Text>
              <Text className="mt-1" style={styles.body}>
                (Os serviços nacionais serão exibidos em todos os estados)
              </Text>
              {selectedRegion.stateCode ? (
                <CardService
                  stateCode={selectedRegion.stateCode}
                  searchQuery={searchQuery}
                />
              ) : (
                <CardService searchQuery={searchQuery} />
              )}
            </>
          ) : (
            <Text style={styles.body}>
              Estado não encontrado.
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
  title: {
    fontSize: theme.typography.title.fontSize,
    lineHeight: theme.typography.title.lineHeight,
    fontWeight: theme.typography.title.fontWeight,
    color: theme.colors.primary,
  },
  body: {
    ...theme.typography.body,
    color: theme.colors.textSecondary,
  },
});