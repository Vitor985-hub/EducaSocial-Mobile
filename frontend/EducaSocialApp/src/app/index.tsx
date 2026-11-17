import { NavigationContainer } from "@react-navigation/native";
import Routes from "../routes";
import Chat from "./pages/chat/chat";

export default function Index() {
  return (
    <NavigationContainer>
      <Routes/>
      <Chat></Chat>
    </NavigationContainer>
  );
}

