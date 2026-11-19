import { useMemo } from "react";
import { router } from "expo-router";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { theme } from "@/styles/theme";
import { useCatalog } from "@/hooks/catalog/useCatalog";
import CategoryIcon from "@/components/category-icon";
import {
  rankByPopularity,
  usePopularity,
} from "@/hooks/popularity/PopularityProvider";

export default function CardCategory({
  limit,
  sort = "catalog",
}: {
  limit?: number;
  sort?: "catalog" | "alphabetical" | "popularity";
}) {
  const { categories, loading, error, retry } = useCatalog();
  const { categoryCounts, recordCategoryAccess } = usePopularity();
  const visibleCategories = useMemo(
    () => {
      if (sort === "popularity") {
        return rankByPopularity(categories, categoryCounts, limit);
      }

      const orderedCategories =
        sort === "alphabetical"
          ? [...categories].sort((left, right) =>
              left.name.localeCompare(right.name, "pt-BR", {
                sensitivity: "base",
              }),
            )
          : categories;

      return limit === undefined
        ? orderedCategories
        : orderedCategories.slice(0, limit);
    },
    [categories, categoryCounts, limit, sort],
  );

  if (loading) {
    return (
      <Text className="mt-5 text-center" style={styles.body}>
        Carregando categorias...
      </Text>
    );
  }

  if (error) {
    return (
      <View className="mt-5 items-center">
        <Text className="text-center" style={styles.error}>
          {error}
        </Text>
        <Pressable
          accessibilityRole="button"
          onPress={retry}
          className="mt-2 rounded-full px-4 py-2"
          style={styles.primaryButton}
        >
          <Text style={styles.primaryButtonLabel}>Tentar novamente</Text>
        </Pressable>
      </View>
    );
  }

  if (categories.length === 0) {
    return (
      <Text className="mt-5 text-center" style={styles.body}>
        Nenhuma categoria disponível.
      </Text>
    );
  }

  return (
    <View className="mt-4 flex-row flex-wrap">
      {visibleCategories.map((category) => (
        <View key={category.id} className="mb-6 w-1/3 items-center px-1">
          <Pressable
            accessibilityRole="button"
            accessibilityLabel={`Ver serviços de ${category.name}`}
            onPress={() => {
              recordCategoryAccess(category.id);
              router.push({
                pathname: "/pages/categories/[categoryId]",
                params: { categoryId: String(category.id) },
              });
            }}
            className="h-24 w-24 items-center justify-center rounded-3xl"
            style={styles.colors}
          >
            <CategoryIcon category={category.id} />
          </Pressable>
          <Text
            className="mt-2 w-full text-center"
            numberOfLines={1}
            ellipsizeMode="tail"
            style={styles.font}
          >
            {category.name}
          </Text>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  colors: {
    backgroundColor: theme.colors.secondary,
  },
  font: {
    fontSize: theme.fontSizes.md,
    color: theme.colors.textPrimary,
  },
  body: {
    fontSize: theme.fontSizes.md,
    color: theme.colors.textSecondary,
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