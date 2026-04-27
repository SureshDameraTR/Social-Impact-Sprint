import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "District Alerts — PashuRaksha ERP",
  description: "Community alerts and health events across the district",
};

export default function DistrictAlertsLayout({ children }: { children: React.ReactNode }) {
  return children;
}
