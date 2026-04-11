import axios from "axios";

const MUTATING_METHODS = new Set(["post", "put", "delete", "patch"]);

function getCsrfToken(): string {
  if (typeof document === "undefined") return "";
  const match = document.cookie.match(/(?:^|; )csrf_token=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : "";
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/v1",
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});

// Attach CSRF token on mutating requests
api.interceptors.request.use((config) => {
  if (MUTATING_METHODS.has((config.method ?? "").toLowerCase())) {
    const token = getCsrfToken();
    if (token) {
      config.headers.set("X-CSRF-Token", token);
    }
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const isAuthCheck = err.config?.url === "/auth/me";
    if (err.response?.status === 401 && !isAuthCheck) {
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default api;
