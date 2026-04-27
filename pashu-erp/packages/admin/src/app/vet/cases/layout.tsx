import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Vet Cases — PashuRaksha ERP",
  description: "Review, diagnose, and manage veterinary consultations",
};

export default function VetCasesLayout({ children }: { children: React.ReactNode }) {
  return children;
}
