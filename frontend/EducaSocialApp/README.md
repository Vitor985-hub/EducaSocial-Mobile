# Welcome to your Expo app 👋

This is an [Expo](https://expo.dev) project created with [`create-expo-app`](https://www.npmjs.com/package/create-expo-app).

## Get started

1. Install dependencies

   ```bash
   npm install
   ```

2. Start the app

   ```bash
   npx expo start
   ```

In the output, you'll find options to open the app in a

- [development build](https://docs.expo.dev/develop/development-builds/introduction/)
- [Android emulator](https://docs.expo.dev/workflow/android-studio-emulator/)
- [iOS simulator](https://docs.expo.dev/workflow/ios-simulator/)
- [Expo Go](https://expo.dev/go), a limited sandbox for trying out app development with Expo

You can start developing by editing the files inside the **src/app** directory. This project uses [file-based routing](https://docs.expo.dev/router/introduction).

## Conectar o chat à IA

O chat envia perguntas para `POST /api/v1/assistant/query` no backend. Copie o exemplo para `.env` na raiz deste projeto e configure o endereço base do backend:

```powershell
Copy-Item .env.example .env
```

```env
EXPO_PUBLIC_API_URL=http://192.168.1.10:8000
```

Substitua o IP de exemplo pelo endereço que o dispositivo consegue acessar. O Expo carrega `.env`, não `.env.example`; reinicie o servidor Expo após criar ou alterar o arquivo. Em um aparelho físico, `localhost` aponta para o próprio aparelho; use o IP da máquina que executa o backend. No emulador Android, use `http://10.0.2.2:8000`.

As chaves do provedor de IA devem permanecer no backend. Inicie-o com o módulo de IA habilitado e reinicie o Expo após alterar `.env`.

## Catálogo de categorias e serviços

Os cards carregam os programas pela API `GET /api/v1/programs`; os detalhes são consultados por `GET /api/v1/programs/{id}`. As categorias exibidas são derivadas dos programas retornados pela API. O catálogo antigo do frontend foi mantido comentado em `src/services/catalog.ts` apenas como referência para testes.

No backend atual, esses endpoints ainda usam os dados fictícios de `FAKE_PROGRAMS`. Para exibir dados reais, é necessário conectar o repositório do backend à base oficial.

## Ferramentas de desenvolvimento

- To set up ESLint for linting, run `npx expo lint`, or follow our guide on ["Using ESLint and Prettier"](https://docs.expo.dev/guides/using-eslint/)
- If you'd like to set up unit testing, follow our guide on ["Unit Testing with Jest"](https://docs.expo.dev/develop/unit-testing/)
- Learn more about the TypeScript setup in this template in our guide on ["Using TypeScript"](https://docs.expo.dev/guides/typescript/)

## Learn more

To learn more about developing your project with Expo, look at the following resources:

- [Expo documentation](https://docs.expo.dev/): Learn fundamentals, or go into advanced topics with our [guides](https://docs.expo.dev/guides).
- [Learn Expo tutorial](https://docs.expo.dev/tutorial/introduction/): Follow a step-by-step tutorial where you'll create a project that runs on Android, iOS, and the web.

## Join the community

Join our community of developers creating universal apps.

- [Expo on GitHub](https://github.com/expo/expo): View our open source platform and contribute.
- [Discord community](https://chat.expo.dev): Chat with Expo users and ask questions.
