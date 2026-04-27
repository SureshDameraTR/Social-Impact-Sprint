import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Map View — PashuRaksha ERP",
  description: "Karnataka livestock monitoring map with disease alerts and milk centres",
};

export default function MapLayout({ children }: { children: React.ReactNode }) {
  return children;
}
