import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Health Alerts — PashuRaksha ERP",
  description: "Active livestock health alerts and AI risk assessments",
};

export default function HealthLayout({ children }: { children: React.ReactNode }) {
  return children;
}
