import api from "./client";

export interface DashboardStats {
  pending_cases: number;
  diagnosed_today: number;
  district_animals: number;
  active_alerts: number;
}

export interface VetCase {
  id: string;
  animal_id: string;
  farmer_id: string;
  vet_id: string | null;
  status: string;
  priority: string;
  channel: string;
  farmer_notes: string | null;
  photo_urls: string[] | null;
  diagnosis: string | null;
  prescription: string | null;
  follow_up_date: string | null;
  video_call_url: string | null;
  district: string;
  created_at: string;
  updated_at: string;
  animal?: {
    id: string;
    species: string;
    name: string | null;
    breed: string;
    owner?: { id: string; name: string; phone: string; village_code: string; location_district: string };
  };
  farmer?: { id: string; name: string };
}

export interface HealthEvent {
  id: string;
  animal_id: string;
  event_type: string;
  symptoms: string | null;
  ai_risk_score: number | null;
  created_at: string;
}

export interface AlertItem {
  id: string;
  disease_name: string;
  severity: string;
  alert_type: string;
  latitude: number | null;
  longitude: number | null;
  location_name: string | null;
  status: string;
  created_at: string;
}

export interface AlertsResponse {
  community_alerts: AlertItem[];
  health_events: HealthEvent[];
}

export function getDashboardStats() {
  return api.get<DashboardStats>("/vet/dashboard/stats");
}

export function getCases(status?: string, skip = 0, limit = 50) {
  const params = new URLSearchParams();
  if (status) params.set("status", status);
  params.set("skip", String(skip));
  params.set("limit", String(limit));
  return api.get<{ data: VetCase[]; skip: number; limit: number }>(`/vet/cases?${params}`);
}

export function getCaseDetail(id: string) {
  return api.get<VetCase>(`/vet/cases/${id}`);
}

export function claimCase(id: string) {
  return api.patch(`/vet/cases/${id}/claim`);
}

export function diagnoseCase(id: string, body: { diagnosis: string; prescription: string; follow_up_date?: string }) {
  return api.patch(`/vet/cases/${id}/diagnose`, body);
}

export function setVideoLink(id: string, video_call_url: string) {
  return api.patch(`/vet/cases/${id}/video-link`, { video_call_url });
}

export function closeCase(id: string) {
  return api.patch(`/vet/cases/${id}/close`);
}

export function getDashboardAlerts() {
  return api.get<AlertsResponse>("/vet/dashboard/alerts");
}

export function verifyAlert(id: string) {
  return api.patch(`/alerts/${id}/verify`);
}

export function getPendingCases(limit = 10) {
  return api.get<{ data: VetCase[] }>(`/vet/cases?status=pending&limit=${limit}`);
}
