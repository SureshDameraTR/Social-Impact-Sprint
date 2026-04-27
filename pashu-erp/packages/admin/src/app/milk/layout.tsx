import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Milk Collection — PashuRaksha ERP",
  description: "Daily milk collection records and trends",
};

export default function MilkLayout({ children }: { children: React.ReactNode }) {
  return children;
}
