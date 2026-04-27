import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Vaccinations — PashuRaksha ERP",
  description: "District-wide vaccination coverage tracking for Karnataka livestock",
};

export default function VaccinationsLayout({ children }: { children: React.ReactNode }) {
  return children;
}
