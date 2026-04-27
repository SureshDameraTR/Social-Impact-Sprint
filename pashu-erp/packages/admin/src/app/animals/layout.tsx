import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Animals — PashuRaksha ERP",
  description: "Registered animals with Pashu Aadhaar across all districts",
};

export default function AnimalsLayout({ children }: { children: React.ReactNode }) {
  return children;
}
