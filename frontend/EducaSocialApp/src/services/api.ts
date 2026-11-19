function getApiBaseUrl() {
  const baseUrl = process.env.EXPO_PUBLIC_API_URL?.trim().replace(/\/+$/, "");
  if (!baseUrl) {
    throw new Error(
      "EXPO_PUBLIC_API_URL não foi carregada. Configure-a em .env e reinicie o Expo.",
    );
  }

  return baseUrl;
}

function getErrorMessage(payload: unknown): string | undefined {
  if (typeof payload !== "object" || payload === null || Array.isArray(payload)) {
    return undefined;
  }

  const error = (payload as Record<string, unknown>).error;
  if (typeof error !== "object" || error === null || Array.isArray(error)) {
    return undefined;
  }

  const message = (error as Record<string, unknown>).message;
  return typeof message === "string" ? message : undefined;
}

export async function requestApi(
  path: string,
  init?: RequestInit,
): Promise<unknown> {
  let response: Response;
  try {
    response = await fetch(`${getApiBaseUrl()}${path}`, init);
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error(
        "Não foi possível conectar ao backend. Verifique o endereço e a conexão de rede.",
      );
    }
    throw error;
  }

  const responseText = await response.text();
  let payload: unknown;
  try {
    payload = JSON.parse(responseText) as unknown;
  } catch {
    if (!response.ok) {
      throw new Error(`O backend retornou um erro (${response.status}).`);
    }
    throw new Error("O backend retornou uma resposta inválida.");
  }

  if (!response.ok) {
    throw new Error(
      getErrorMessage(payload) ?? `O backend retornou um erro (${response.status}).`,
    );
  }

  return payload;
}
