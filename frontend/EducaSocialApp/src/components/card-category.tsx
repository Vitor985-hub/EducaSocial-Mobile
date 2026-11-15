import { Image, Pressable, Text, View } from 'react-native';

export default function CardCategory() {
  return (
    <View className="flex-row flex-wrap gap-4 mt-4 justify-center">
        <View className="justify-center items-center">
        <Pressable className="bg-slate-300 h-28 w-28 items-center justify-center rounded-3xl">
            <Image className="h-14 w-14" source={require('../assets/logofigma.png')}/>
        </Pressable>
        <Text>Category Name</Text>
        </View>

        <View className="justify-center items-center" >
        <Pressable className="bg-slate-300 h-28 w-28 items-center justify-center rounded-3xl">
            <Image className="h-14 w-14" source={require('../assets/logofigma.png')}/>
        </Pressable>
        <Text>Category Name</Text>
        </View>
        
        <View className="justify-center items-center">
        <Pressable className="bg-slate-300 h-28 w-28 items-center justify-center rounded-3xl">
            <Image className="h-14 w-14" source={require('../assets/logofigma.png')}/>
        </Pressable>
        <Text>Category Name</Text>
        </View>

        <View className="justify-center items-center">
        <Pressable className="bg-slate-300 h-28 w-28 items-center justify-center rounded-3xl">
            <Image className="h-14 w-14" source={require('../assets/logofigma.png')}/>
        </Pressable>
        <Text>Category Name</Text>
        </View>
    </View>
  );
}