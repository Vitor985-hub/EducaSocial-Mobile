import { createMaterialTopTabNavigator } from '@react-navigation/material-top-tabs';

import Categories from './app/pages/categories/categories';
import Home from './app/pages/home/home';
import States from './app/pages/states/states';
import { Navbar } from './components/navbar';

const Tab = createMaterialTopTabNavigator();

export default function Routes() {
  return (
    <Tab.Navigator
      tabBar={(props) => <Navbar {...props} />}
    >
      <Tab.Screen name="Início" component={Home} />
      <Tab.Screen name="Categorias" component={Categories} />
      <Tab.Screen name="Estados" component={States} />
      {/* <Tab.Screen name="Chat" component={Chat} /> */}
    </Tab.Navigator>
  );
}