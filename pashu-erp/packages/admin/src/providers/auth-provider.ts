import type { AuthProvider } from "@refinedev/core";

const API_URL = "http://localhost:8000/v1";

export const authProvider: AuthProvider = {
  login: async ({ phone, otp }) => {
    try {
      const response = await fetch(`${API_URL}/auth/verify-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phone: phone || "+919999900000",
          otp: otp || "123456",
        }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem("token", data.access_token || "demo-jwt-token");
        localStorage.setItem(
          "user",
          JSON.stringify(
            data.user || {
              id: "admin-001",
              name: "Dr. Rajesh Kumar",
              role: "district_admin",
              phone: "+919999900000",
              district: "Mysuru",
            }
          )
        );
        return { success: true, redirectTo: "/" };
      }
    } catch {
      // Fallback for demo: auto-login with mock data
      localStorage.setItem("token", "demo-jwt-token");
      localStorage.setItem(
        "user",
        JSON.stringify({
          id: "admin-001",
          name: "Dr. Rajesh Kumar",
          role: "district_admin",
          phone: "+919999900000",
          district: "Mysuru",
        })
      );
      return { success: true, redirectTo: "/" };
    }

    return {
      success: false,
      error: { name: "LoginError", message: "Invalid credentials" },
    };
  },

  logout: async () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    return { success: true, redirectTo: "/login" };
  },

  check: async () => {
    const token = localStorage.getItem("token");
    if (token) {
      return { authenticated: true };
    }
    return { authenticated: false, redirectTo: "/login" };
  },

  getIdentity: async () => {
    const userStr = localStorage.getItem("user");
    if (userStr) {
      const user = JSON.parse(userStr);
      return {
        id: user.id,
        name: user.name,
        avatar: undefined,
      };
    }
    return null;
  },

  onError: async (error) => {
    if (error?.statusCode === 401) {
      return { logout: true };
    }
    return { error };
  },
};
