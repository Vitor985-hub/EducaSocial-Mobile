import CardCategory from "@/components/card-category";
import CardService from "@/components/card-service";

import { Text, View, ScrollView } from "react-native";

export default function Home() {
    return (
    <ScrollView
      style={{ flex: 1 }} 
      className="bg-slate-100" 
      showsVerticalScrollIndicator={false}>
        
        <View className="w-full px-8 pb-5">
          <Text className="text-2xl font-bold text-slate-800 mt-5">Categorias mais acessadas</Text>
          <CardCategory/>
        </View>

        <View className="w-full px-8 pb-5">
          <Text className="text-2xl font-bold text-slate-800">Serviços mais acessados</Text>
          <CardService/>
        </View>
    </ScrollView>
    );

}