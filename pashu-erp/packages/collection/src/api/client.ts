import axios from "axios";

const api = axios.create({
  baseURL: "/v1",
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
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
