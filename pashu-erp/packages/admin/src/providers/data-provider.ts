import dataProvider from "@refinedev/simple-rest";

const API_URL = "http://localhost:8000/v1";

const fetchWrapper = (url: string, options: RequestInit = {}) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  return fetch(url, { ...options, headers });
};

export const restDataProvider = dataProvider(API_URL, fetchWrapper);
