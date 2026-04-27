import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Govt Schemes — PashuRaksha ERP",
  description: "Government livestock subsidy schemes for farmers",
};

export default function SchemesLayout({ children }: { children: React.ReactNode }) {
  return children;
}
