import { Text } from "react-native";
import CardCategory from "@/components/card-category";
import { ScrollView, View } from "react-native";

export default function Categories() {
  return (
    <ScrollView
      style={{ flex: 1 }}
      className="bg-slate-100"
      showsVerticalScrollIndicator={false}>

      <View className="w-full px-8 pb-5">
        <CardCategory />
      </View>
    </ScrollView>
  );
}