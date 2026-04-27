import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Vet Dashboard — PashuRaksha ERP",
  description: "Veterinary case management and district overview",
};

export default function VetLayout({ children }: { children: React.ReactNode }) {
  return children;
}
