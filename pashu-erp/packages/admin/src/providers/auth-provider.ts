import type { AuthProvider } from "@refinedev/core";

const API_URL = process.env.NEXT_PUBLIC_API_URL;
if (!API_URL) {
  throw new Error("NEXT_PUBLIC_API_URL environment variable is required");
}

let cachedIdentity: { id: string; name: string; role: string } | null = null;

function getCsrfToken(): string {
  if (typeof document === "undefined") return "";
  const match = document.cookie.match(/(?:^|; )csrf_token=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : "";
}

export const authProvider: AuthProvider = {
  login: async ({ phone, otp, rememberMe }) => {
    try {
      const response = await fetch(`${API_URL}/auth/verify-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          phone,
          otp,
          remember_me: rememberMe ?? false,
          client_type: "web",
        }),
      });

      if (!response.ok) {
        const err = await response.json();
        return {
          success: false,
          error: {
            name: err.code || "LoginError",
            message: err.detail || "Authentication failed",
          },
        };
      }

      const data = await response.json();
      cachedIdentity = {
        id: data.user_id,
        name: data.name || "Unknown",
        role: data.role,
      };
      return { success: true, redirectTo: "/" };
    } catch {
      return {
        success: false,
        error: { name: "NetworkError", message: "Could not reach the server" },
      };
    }
  },

  logout: async () => {
    cachedIdentity = null;
    try {
      await fetch(`${API_URL}/auth/logout`, {
        method: "POST",
        credentials: "include",
        headers: { "X-CSRF-Token": getCsrfToken() },
      });
    } catch {
      // best-effort — server may be unreachable
    }
    return { success: true, redirectTo: "/login" };
  },

  check: async () => {
    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        cachedIdentity = { id: data.user_id, name: data.name, role: data.role };
        return { authenticated: true };
      }
    } catch {
      // auth check failed — treat as unauthenticated
    }
    cachedIdentity = null;
    return { authenticated: false, redirectTo: "/login" };
  },

  getIdentity: async () => {
    if (cachedIdentity) {
      return {
        id: cachedIdentity.id,
        name: cachedIdentity.name,
        role: cachedIdentity.role,
      };
    }

    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        cachedIdentity = { id: data.user_id, name: data.name, role: data.role };
        return { id: data.user_id, name: data.name, role: data.role };
      }
    } catch {
      // identity fetch failed
    }
    return null;
  },

  onError: async (error) => {
    if (error?.statusCode === 401) {
      cachedIdentity = null;
      return { logout: true };
    }
    return { error };
  },
};

export { getCsrfToken };
