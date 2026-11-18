import { Image, Pressable, Text, View } from 'react-native';

const categories = [
    { id: 1, name: 'Assistência Social', image: require('../assets/logofigma.png') },
    { id: 2, name: 'Atendimento ao Cidadão', image: require('../assets/logofigma.png') },
    { id: 3, name: 'Educação', image: require('../assets/logofigma.png') },
    { id: 4, name: 'Mobilidade', image: require('../assets/logofigma.png') },
    { id: 5, name: 'Moradia', image: require('../assets/logofigma.png') },
    { id: 6, name: 'Renda', image: require('../assets/logofigma.png') },
    { id: 7, name: 'Trabalho', image: require('../assets/logofigma.png') },
];

export default function CardCategory() {
    return (
        <View className="mt-5 flex-row flex-wrap justify-center">
            {categories.map((category) => (
                <View key={category.id} className="w-1/2 items-center mb-10">
                    <Pressable className="bg-slate-300 h-28 w-28 items-center justify-center rounded-3xl">
                        <Image className="h-14 w-14" source={category.image} />
                    </Pressable>
                    <Text className="w-28 text-center mt-2">{category.name}</Text>
                </View>
            ))}
        </View>
    );
}
