import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Marketplace — PashuRaksha ERP",
  description: "Farmer-to-buyer transactions and revenue analytics",
};

export default function MarketplaceLayout({ children }: { children: React.ReactNode }) {
  return children;
}
