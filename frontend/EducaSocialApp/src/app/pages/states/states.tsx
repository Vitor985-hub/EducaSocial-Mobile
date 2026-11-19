import { useMemo, useState } from "react";
import { regions } from "@/services/catalog";
import { theme } from "@/styles/theme";
import { Host, Icon, List, ListItem } from '@expo/ui';
import { router } from "expo-router";
import { StyleSheet, Text, View } from "react-native";
import SearchBar from "@/components/search-bar";
import { normalizeSearchText } from "@/utils/search";

const CHEVRON = Icon.select({
  ios: 'chevron.right',
  android: import('@expo/material-symbols/chevron_right.xml'),
});


export default function States() {
  const [searchQuery, setSearchQuery] = useState("");
  const filteredRegions = useMemo(() => {
    const query = normalizeSearchText(searchQuery);
    return regions
      .filter((region) => region.id !== 1)
      .filter((region) => normalizeSearchText(region.name).includes(query));
  }, [searchQuery]);

  return (
    <View style={styles.screen}>
      <View style={styles.searchContainer}>
        <SearchBar
          value={searchQuery}
          onChangeText={setSearchQuery}
          placeholder="Pesquisar Estado"
        />
      </View>
      {filteredRegions.length === 0 ? (
        <Text style={styles.emptyMessage}>Nenhum estado encontrado.</Text>
      ) : (
        <Host style={styles.listHost}>
          <List>
            {filteredRegions.map((region) => (
              <ListItem
                key={region.id}
                onPress={() =>
                  router.push({
                    pathname: "/pages/states/[stateId]",
                    params: { stateId: String(region.id) },
                  })
                }
                colors={{
                  containerColor: theme.colors.background,
                  contentColor: theme.colors.textPrimary,
                  trailingContentColor: theme.colors.primary,
                }}
                trailing={
                  <Icon name={CHEVRON} size={24} color={theme.colors.primary} />
                }
              >
                <Text style={styles.stateName}>{region.name}</Text>
                {region.name}
              </ListItem>
            ))}
          </List>
        </Host>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  searchContainer: {
    paddingHorizontal: 24,
    paddingTop: 12,
    paddingBottom: 8,
  },
  listHost: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  stateName: {
    fontSize: theme.fontSizes.md,
    color: theme.colors.textPrimary,
  },
  emptyMessage: {
    marginTop: 24,
    textAlign: "center",
    fontSize: theme.fontSizes.md,
    color: theme.colors.textSecondary,
  },
});