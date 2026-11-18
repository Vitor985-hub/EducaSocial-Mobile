import { useState } from 'react';
import { Modal, Pressable, SafeAreaView, ScrollView, Text, View } from 'react-native';

const SERVICE  = [
  {id: 1, name: 'CadÚnico — Cadastro Único (Prefeitura de São Paulo)', description: 'O CadÚnico reúne as famílias de baixa renda do país e permite participar de programas sociais federais, estaduais e municipais, como o Programa Bolsa Família, o BPC e a Tarifa Social de Energia Elétrica e Água.'},
  {id: 2, name: 'Bolsa Família', description: 'O Programa Bolsa Família é um programa de transferência de renda do Governo Federal que tem como objetivo garantir a segurança alimentar e nutricional das famílias em situação de pobreza e extrema pobreza.'},
  {id: 3, name: 'BPC — Benefício de Prestação Continuada', description: 'O Benefício de Prestação Continuada (BPC) é um benefício assistencial pago pelo Governo Federal a pessoas com deficiência e idosos com 65 anos ou mais que não têm condições de se sustentar.'},
  {id: 4, name: 'Tarifa Social de Energia Elétrica', description: 'A Tarifa Social de Energia Elétrica é um benefício do Governo Federal que concede descontos na conta de energia elétrica para famílias de baixa renda.'},
  {id: 5, name: 'Tarifa Social de Água', description: 'A Tarifa Social de Água é um benefício do Governo Federal que concede descontos na conta de água para famílias de baixa renda.'},
]


export default function CardService() {
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedService, setSelectedService] = useState<(typeof SERVICE)[number] | null>(null);

  return (
    <View className="flex-row flex-wrap gap-4 mt-5 justify-center">
      {SERVICE.map((service) => (
        <View key={service.id} className="w-full">
          <Pressable
            onPress={() => {
              setSelectedService(service);
              setModalVisible(true);
            }}
            className="bg-slate-200 h-auto w-full p-3 rounded-3xl border-2 border-slate-300 active:opacity-80"
          >
          <Text className="text-xl font-bold text-slate-800 mb-2">{service.name}</Text>
          <Text className="text-lg text-slate-600" numberOfLines={3}>{service.description}</Text>
        </Pressable>
      </View>
      ))}

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
                {selectedService?.name}
              </Text>
              <Text className="text-base font-bold text-slate-800 mb-1">
                Descrição
              </Text>
              <Text className="text-base text-slate-600 leading-6">
                {selectedService?.description}
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
