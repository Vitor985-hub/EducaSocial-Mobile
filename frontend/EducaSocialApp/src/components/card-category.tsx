import { router } from "expo-router";
import { Image, Pressable, Text, View } from "react-native";
import { categories } from "@/services/catalog";

export default function CardCategory() {
  return (
    <View className="mt-5 flex-row flex-wrap justify-center">
      {categories.map((category) => (
        <View key={category.id} className="mb-10 w-1/2 items-center">
          <Pressable
            accessibilityRole="button"
            accessibilityLabel={`Ver serviços de ${category.name}`}
            onPress={() =>
              router.push({
                pathname: "/pages/categories/[categoryId]",
                params: { categoryId: String(category.id) },
              })
            }
            className="h-28 w-28 items-center justify-center rounded-3xl bg-slate-300"
          >
            <Image className="h-14 w-14" source={category.image} />
          </Pressable>
          <Text className="mt-2 w-28 text-center">{category.name}</Text>
        </View>
      ))}
    </View>
  );
}
