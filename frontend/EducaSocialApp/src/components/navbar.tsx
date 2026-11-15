import { View, Pressable, Text } from 'react-native';

export function Navbar() {
 return (
    <View className= "w-full flex flex-row items-center justify-between">
        <View>
            <Pressable className=" bg-neutral-500 px-4 py-2 rounded-full">
                <Text className="text-xl text-white">Inicio</Text>
            </Pressable>
        </View>

        <View>
            <Pressable className="0 px-4 py-2 rounded-full border-2 border-slate-600">
                <Text className="text-xl text-slate-500">Categorias</Text>
            </Pressable>
        </View>

        <View>
            <Pressable className=" px-4 py-2 rounded-full border-2 border-slate-600">
                <Text className="text-xl text-slate-500">Estado</Text>
            </Pressable>
        </View> 
    </View>
 );
}