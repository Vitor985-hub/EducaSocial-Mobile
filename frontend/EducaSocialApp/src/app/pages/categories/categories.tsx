import { Text } from "react-native";
import CardCategory from "@/components/card-category";
import { ScrollView, StyleSheet, View } from "react-native";
import { theme } from "@/styles/theme";

export default function Categories() {
  return (
    <ScrollView
      style={styles.screen}
      showsVerticalScrollIndicator={false}
    >
      <View className="w-full px-8 pb-5">
        <CardCategory sort="alphabetical" />
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
});