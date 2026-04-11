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

    let body: unknown;
    try {
      body = await res.json();
    } catch {
      throw new Error(`Invalid JSON response from ${url}`);
    }

    if (Array.isArray(body)) {
      return { data: body, total: body.length };
    }

    if (typeof body === "object" && body !== null) {
      const obj = body as Record<string, unknown>;

      if (Array.isArray(obj.data)) {
        return { data: obj.data, total: (obj.total as number) ?? obj.data.length };
      }

      const arrayKey = Object.keys(obj).find((k) => Array.isArray(obj[k]));
      if (arrayKey) {
        const arr = obj[arrayKey] as unknown[];
        return { data: arr, total: (obj.total as number) ?? arr.length };
      }

      return { data: [obj], total: 1 };
    }

    return { data: [], total: 0 };
  },

  getOne: async ({ resource, id }) => {
    const res = await fetchWithAuth(`${API_URL}/${resource}/${id}`);
    if (!res.ok) throw new Error(`API error ${res.status}`);
    try {
      return { data: await res.json() };
    } catch {
      throw new Error(`Invalid JSON from ${resource}/${id}`);
    }
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
