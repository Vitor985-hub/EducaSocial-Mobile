import { router, useLocalSearchParams } from "expo-router";
import { Pressable, ScrollView, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import CardService from "@/components/card-service";
import { categories } from "@/services/catalog";

export default function CategoryServices() {
  const { categoryId } = useLocalSearchParams<{ categoryId: string }>();
  const selectedCategory = categories.find(
    (category) => category.id === Number(categoryId),
  );

  return (
    <SafeAreaView className="flex-1 bg-slate-100">
      <ScrollView
        className="flex-1"
        contentContainerStyle={{ paddingBottom: 32 }}
        showsVerticalScrollIndicator={false}
      >
        <View className="w-full px-8">
          <Pressable
            accessibilityRole="button"
            onPress={() => router.back()}
            className="mb-4 mt-5 self-start py-2"
          >
            <Text className="text-base font-medium text-slate-700">
              ← Voltar
            </Text>
          </Pressable>

          {selectedCategory ? (
            <>
              <Text className="text-2xl font-bold text-slate-800">
                {selectedCategory.name}
              </Text>
              <Text className="mt-1 text-base text-slate-600">
                Serviços disponíveis nesta categoria
              </Text>
              <CardService categoryId={selectedCategory.id} />
            </>
          ) : (
            <Text className="text-lg text-slate-700">
              Categoria não encontrada.
            </Text>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}