import { Host, Icon, List, ListItem } from '@expo/ui';
import { router } from "expo-router";
import { regions } from "@/services/catalog";

const CHEVRON = Icon.select({
  ios: 'chevron.right',
  android: import('@expo/material-symbols/chevron_right.xml'),
});


export default function States() {
  return (
    <Host style={{ flex: 1 }}>
      <List>
        {regions.filter((region) => region.id !== 1).map((region) => (
          <ListItem
            key={region.id}
            onPress={() =>
              router.push({
                pathname: "/pages/states/[stateId]",
                params: { stateId: String(region.id) },
              })
            }
            trailing={<Icon name={CHEVRON} size={14} color="gray" />}
          >
            {region.name}
          </ListItem>
        ))}
      </List>
    </Host>
  );
}