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

// Request interceptor — add request ID
apiClient.interceptors.request.use((config) => {
  config.headers["x-request-id"] = crypto.randomUUID();
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
