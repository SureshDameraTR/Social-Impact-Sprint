import type { DataProvider } from "@refinedev/core";
import { getCsrfToken } from "@/providers/auth-provider";

const API_URL = process.env.NEXT_PUBLIC_API_URL;
if (!API_URL) {
  throw new Error("NEXT_PUBLIC_API_URL environment variable is required");
}

const MUTATING_METHODS = new Set(["POST", "PUT", "DELETE", "PATCH"]);

async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const method = (options.method || "GET").toUpperCase();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(MUTATING_METHODS.has(method) ? { "X-CSRF-Token": getCsrfToken() } : {}),
    ...(options.headers || {}),
  };
  return fetch(url, { ...options, headers, credentials: "include" });
}

export const restDataProvider: DataProvider = {
  getList: async ({ resource, pagination, filters, sorters, meta }) => {
    const params = new URLSearchParams();

    if (pagination?.current && pagination?.pageSize) {
      params.set("offset", String((pagination.current - 1) * pagination.pageSize));
      params.set("limit", String(pagination.pageSize));
    }

    if (meta?.params) {
      for (const [k, v] of Object.entries(meta.params)) {
        if (v !== undefined && v !== null) params.set(k, String(v));
      }
    }

    const qs = params.toString();
    const url = `${API_URL}/${resource}${qs ? `?${qs}` : ""}`;
    const res = await fetchWithAuth(url);

    if (!res.ok) {
      throw new Error(`API error ${res.status}: ${await res.text()}`);
    }

    const body = await res.json();

    if (Array.isArray(body)) {
      return { data: body, total: body.length };
    }

    if (body.data && Array.isArray(body.data)) {
      return { data: body.data, total: body.total ?? body.data.length };
    }

    const arrayKey = Object.keys(body).find((k) => Array.isArray(body[k]));
    if (arrayKey) {
      return { data: body[arrayKey], total: body.total ?? body[arrayKey].length };
    }

    return { data: [body], total: 1 };
  },

  getOne: async ({ resource, id }) => {
    const res = await fetchWithAuth(`${API_URL}/${resource}/${id}`);
    if (!res.ok) throw new Error(`API error ${res.status}`);
    return { data: await res.json() };
  },

  create: async ({ resource, variables }) => {
    const res = await fetchWithAuth(`${API_URL}/${resource}`, {
      method: "POST",
      body: JSON.stringify(variables),
    });
    if (!res.ok) throw new Error(`API error ${res.status}`);
    return { data: await res.json() };
  },

  update: async ({ resource, id, variables }) => {
    const res = await fetchWithAuth(`${API_URL}/${resource}/${id}`, {
      method: "PATCH",
      body: JSON.stringify(variables),
    });
    if (!res.ok) throw new Error(`API error ${res.status}`);
    return { data: await res.json() };
  },

  // @ts-expect-error -- Refine's deleteOne is generic over TData which cannot
  // be satisfied by a concrete data-provider; this is a known Refine limitation.
  deleteOne: async ({ resource, id }) => {
    const res = await fetchWithAuth(`${API_URL}/${resource}/${id}`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error(`API error ${res.status}`);
    return { data: { id } };
  },

  getApiUrl: () => API_URL!,
};
