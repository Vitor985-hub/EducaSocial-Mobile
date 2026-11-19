import MaterialCommunityIcons from "@expo/vector-icons/MaterialCommunityIcons";
import { Pressable, StyleSheet, TextInput, View } from "react-native";
import { theme } from "@/styles/theme";

type SearchBarProps = {
  value: string;
  onChangeText: (value: string) => void;
  placeholder: string;
};

export default function SearchBar({
  value,
  onChangeText,
  placeholder,
}: SearchBarProps) {
  return (
    <View style={styles.container}>
      <MaterialCommunityIcons
        name="magnify"
        size={21}
        color={theme.colors.primary}
      />
      <TextInput
        accessibilityLabel={placeholder}
        autoCapitalize="none"
        autoCorrect={false}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor={theme.colors.textSecondary}
        returnKeyType="search"
        selectionColor={theme.colors.primary}
        style={styles.input}
        underlineColorAndroid="transparent"
        value={value}
      />
      {value.length > 0 && (
        <Pressable
          accessibilityLabel="Limpar pesquisa"
          accessibilityRole="button"
          hitSlop={8}
          onPress={() => onChangeText("")}
        >
          <MaterialCommunityIcons
            name="close-circle"
            size={18}
            color={theme.colors.textMuted}
          />
        </Pressable>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    height: 40,
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    paddingHorizontal: 12,
    borderRadius: 20,
    backgroundColor: theme.colors.surfaceMuted,
  },
  input: {
    minWidth: 0,
    flex: 1,
    paddingVertical: 0,
    fontSize: theme.fontSizes.sm,
    color: theme.colors.textPrimary,
  },
});
