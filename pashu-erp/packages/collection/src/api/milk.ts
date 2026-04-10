import api from "./client";
import type { Shift } from "../types";

export async function receiveMilk(data: {
  center_id: string;
  farmer_user_id: string;
  quantity_liters: number;
  fat_pct: number;
  snf_pct: number;
  shift: Shift;
}) {
  return api.post("/milk-center/receive", data);
}

export async function getDailyReport(centerId: string) {
  return api.get(`/milk-center/${centerId}/daily-report`);
}

export async function getFarmerSettlements(centerId: string, days: number = 15) {
  return api.get(`/milk-center/${centerId}/farmer-settlements`, { params: { days } });
}

export async function searchFarmers(params: { phone?: string; aadhaar_last4?: string; name?: string }) {
  return api.get("/milk-center/farmers/search", { params });
}

export async function enrollFarmer(data: {
  name: string;
  phone: string;
  aadhaar: string;
  village_code?: string;
}) {
  return api.post("/milk-center/farmers/enroll", data);
}
