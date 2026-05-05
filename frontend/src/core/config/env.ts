/** SOCsentinel — Environment variable validation. */

interface EnvConfig {
  appName: string;
  apiUrl: string;
  wsUrl: string;
}

function getEnvConfig(): EnvConfig {
  return {
    appName: import.meta.env.VITE_APP_NAME || "SOCsentinel",
    apiUrl: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
    wsUrl: import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws",
  };
}

export const env = getEnvConfig();
