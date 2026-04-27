import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Income Analytics — PashuRaksha ERP",
  description: "Farmer income distribution and trends across Mysuru District",
};

export default function IncomeLayout({ children }: { children: React.ReactNode }) {
  return children;
}
