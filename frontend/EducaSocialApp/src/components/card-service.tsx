import { useState } from 'react';
import { Modal, Pressable, SafeAreaView, ScrollView, Text, View } from 'react-native';

export default function CardService() {
  const [modalVisible, setModalVisible] = useState(false);

  return (
    <View className="flex-row flex-wrap gap-4 mt-4 justify-center">
      {/* Seu Card Original */}
      <View className="w-full">
        <Pressable
          onPress={() => setModalVisible(true)}
          className="bg-slate-200 h-40 w-full p-3 rounded-3xl border-2 border-slate-300 active:opacity-80"
        >
          <Text className="text-xl font-bold text-slate-800">Service Name</Text>
          <Text className="text-lg text-slate-600">Service Description</Text>
          <Text className="text-base text-slate-600 mt-2">ver mais detalhes</Text>
        </Pressable>
      </View>

      {/* Modal em Tela Cheia */}
      <Modal
        visible={modalVisible}
        animationType="slide"
        transparent={false} // Ocupa a tela inteira
        onRequestClose={() => setModalVisible(false)}
      >
        <SafeAreaView className="flex-1 bg-slate-100">
          <ScrollView 
            className="flex-1 px-5 pt-4"
            contentContainerStyle={{ paddingBottom: 40 }}
            showsVerticalScrollIndicator={false}
          >
            {/* Botão Superior: Voltar a página anterior */}
            <Pressable
              onPress={() => setModalVisible(false)}
              className="flex-row items-center gap-3 mb-5 py-2 active:opacity-70"
            >
              <View className="w-8 h-8 rounded-full border-2 border-slate-700 items-center justify-center">
                <Text className="text-slate-700 font-bold text-base leading-none">←</Text>
              </View>
              <Text className="text-lg font-medium text-slate-800">
                Voltar a página anterior
              </Text>
            </Pressable>


            <View className="bg-slate-50 rounded-3xl p-6 border border-slate-300 shadow-sm">
              <Text className="text-2xl font-bold text-slate-900 mb-5">
                Nome do serviço
              </Text>


              <View className="mb-5">
                <Text className="text-base font-bold text-slate-800 mb-1">
                  Serviço disponível no(s) estado(s):
                </Text>
                <Text className="text-base text-slate-600">
                  XX, XX, XX, XX, XX, XX
                </Text>
              </View>

              <View className="mb-5">
                <Text className="text-base font-bold text-slate-800 mb-1">
                  Elegibilidade{'\n'}
                  <Text className="font-semibold">(quem pode utilizar este serviço):</Text>
                </Text>
                <Text className="text-base text-slate-600 leading-6">
                  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc vulputate libero.
                </Text>
              </View>

              <View className="mb-5">
                <Text className="text-base font-bold text-slate-800 mb-1">
                  Documentos necessários:
                </Text>
                <Text className="text-base text-slate-600 leading-6">
                  Lorem ipsum dolor sit amet, consectetur adipiscing elit, libero et velit interdum, ac aliquet.
                </Text>
              </View>

              <View className="mb-5">
                <Text className="text-base font-bold text-slate-800 mb-1">
                  Etapas da inscrição:
                </Text>
                <View className="pl-2 gap-1">
                  <Text className="text-base text-slate-600">• adipiscing elit</Text>
                  <Text className="text-base text-slate-600">• libero et velit interdum</Text>
                  <Text className="text-base text-slate-600">• ac aliquet</Text>
                </View>
              </View>

              <View className="mb-5">
                <Text className="text-base font-bold text-slate-800 mb-1">
                  Última revisão das informações:
                </Text>
                <Text className="text-base text-slate-600">
                  00-00-0000 às 00h00
                </Text>
              </View>

              <View>
                <Text className="text-base font-bold text-slate-800 mb-1">
                  Status do serviço:
                </Text>
                <Text className="text-base text-slate-600">
                  Ativo
                </Text>
              </View>
            </View>
          </ScrollView>
        </SafeAreaView>
      </Modal>
    </View>
  );
}
