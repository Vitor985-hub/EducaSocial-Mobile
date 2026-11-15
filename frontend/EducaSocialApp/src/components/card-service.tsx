import { Image, Pressable, Text, View } from 'react-native';

export default function CardService() {
  return (
    <View className="flex-row flex-wrap gap-4 mt-4 justify-center ">

        <View className="w-full">
        <Pressable className="bg-slate-200 h-40 w-full p-3 rounded-3xl border-2 border-slate-300">
            <Text className="text-xl font-bold text-slate-800">Service Name</Text>
            <Text className="text-lg text-slate-600">Service Description</Text>
        </Pressable>
        </View>

    </View>
    );
}