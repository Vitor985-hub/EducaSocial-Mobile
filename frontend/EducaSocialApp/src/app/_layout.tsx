import { Slot, useRouter } from 'expo-router';
import '../styles/global.css';

  
export default function RootLayout() {
  return (
    // Renders the active child route component in the layout
    <Slot />
  );
}
