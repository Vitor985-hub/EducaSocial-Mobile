import CardCategory from "@/components/card-category";
import CardService from "@/components/card-service";
import { Navbar } from "@/components/navbar";
import Constants from 'expo-constants';
import { Text, View, ScrollView} from "react-native";

const statusBarHeight = Constants.statusBarHeight;

export default function Index() {
  return (
    <ScrollView
      style={{ flex: 1 }} 
      className="bg-slate-100" 
      showsVerticalScrollIndicator={false}>
        
        <View className="w-full px-8 pb-5 border-b-2 border-y-slate-400" style={{ marginTop: statusBarHeight + 8 }}>
          <Navbar/>
        </View>

        <View className="w-full px-8 pb-5">
          <Text className="text-2xl font-bold text-slate-800">Categorias mais acessadas</Text>
          <CardCategory/>
        </View>

        <View className="w-full px-8 pb-5">
          <Text className="text-2xl font-bold text-slate-800">Serviços mais acessados</Text>
          <CardService/>
        </View>
    </ScrollView>
  );
}

