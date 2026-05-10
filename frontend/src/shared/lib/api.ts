/** SOCsentinel — Axios HTTP client setup. */

import axios from "axios";
import { env } from "../../core/config/env";

export const apiClient = axios.create({
  baseURL: env.apiUrl,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Polyfill for crypto.randomUUID (older browsers or Node.js without Web Crypto)
function generateUUID(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  // Fallback: simple UUID v4 implementation
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

// Request interceptor — add request ID
apiClient.interceptors.request.use((config) => {
  config.headers["x-request-id"] = generateUUID();
  return config;
});

// Response interceptor — handle errors globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      const message =
        error.response.data?.message || "An unexpected error occurred";
      console.error(`[API Error] ${error.response.status}: ${message}`);
    } else if (error.request) {
      // No response received
      console.error("[API Error] No response received from server");
    }
    return Promise.reject(error);
  }
);
