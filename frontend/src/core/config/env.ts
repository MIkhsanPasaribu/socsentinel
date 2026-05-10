/** SOCsentinel — Environment variable validation. */

interface EnvConfig {
  appName: string;
  apiUrl: string;
  wsUrl: string;
}

function getEnvConfig(): EnvConfig {
  const defaultApiUrl =
    import.meta.env.MODE === "development"
      ? "http://localhost:8000/api/v1"
      : "/api/v1";
  const defaultWsUrl =
    import.meta.env.MODE === "development"
      ? "ws://localhost:8000/ws"
      : `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/ws`;

  return {
    appName: import.meta.env.VITE_APP_NAME || "SOCsentinel",
    apiUrl: import.meta.env.VITE_API_URL || defaultApiUrl,
    wsUrl: import.meta.env.VITE_WS_URL || defaultWsUrl,
  };
}

export const env = getEnvConfig();
