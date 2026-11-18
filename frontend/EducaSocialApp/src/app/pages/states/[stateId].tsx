import { router, useLocalSearchParams } from "expo-router";
import { Pressable, ScrollView, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import CardService from "@/components/card-service";
import { regions } from "@/services/catalog";

export default function StateServices() {
  const { stateId } = useLocalSearchParams<{ stateId: string }>();
  const selectedRegion = regions.find(
    (region) => region.id === Number(stateId),
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

          {selectedRegion ? (
            <>
              <Text className="text-2xl font-bold text-slate-800">
                Serviços em {selectedRegion.name}
              </Text>
              <Text className="mt-1 text-base text-slate-600">
                (Os serviços nacionais serão exibidos em todos os estados)
              </Text>
              <CardService regionId={selectedRegion.id} />
            </>
          ) : (
            <Text className="text-lg text-slate-700">
              Estado não encontrado.
            </Text>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}