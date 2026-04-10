import api from "./client";

export async function requestOtp(phone: string) {
  return api.post("/auth/request-otp", { phone });
}

export async function verifyOtp(phone: string, otp: string, rememberMe: boolean) {
  return api.post("/auth/verify-otp", {
    phone,
    otp,
    remember_me: rememberMe,
    client_type: "web",
  });
}

export async function getMe() {
  return api.get<{ user_id: string; role: string; name: string }>("/auth/me");
}

export async function logout() {
  return api.post("/auth/logout");
}
