import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("ev_fleet_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (typeof window !== "undefined" && error?.response?.status === 401) {
      localStorage.removeItem("ev_fleet_token");
      localStorage.removeItem("ev_fleet_user");
      if (!window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export function friendlyError(error: unknown): string {
  const anyErr = error as any;
  if (anyErr?.response?.data?.detail) {
    return typeof anyErr.response.data.detail === "string"
      ? anyErr.response.data.detail
      : "Something went wrong. Please try again.";
  }
  if (anyErr?.message === "Network Error") {
    return "Could not reach the server. Is the backend running?";
  }
  return "Something went wrong. Please try again.";
}
