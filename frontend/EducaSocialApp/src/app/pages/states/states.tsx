import { Host, Icon, List, ListItem } from '@expo/ui';

const CHEVRON = Icon.select({
  ios: 'chevron.right',
  android: import('@expo/material-symbols/chevron_right.xml'),
});

const UF = [
  { id: 1, name: 'Acre' },
  { id: 2, name: 'Alagoas' },
  { id: 3, name: 'Amapá' },
  { id: 4, name: 'Amazonas' },
  { id: 5, name: 'Bahia' },
  { id: 6, name: 'Ceará' },
  { id: 7, name: 'Distrito Federal' },
  { id: 8, name: 'Espírito Santo' },
];

export default function States() {
  return (
    <Host style={{ flex: 1 }}>
      <List>
        {UF.map((uf) => (
          <ListItem key={uf.id} onPress={() => {}} trailing={<Icon name={CHEVRON} size={14} color="gray" />}>
            {uf.name}
          </ListItem>
        ))}
      </List>
    </Host>
  );
}