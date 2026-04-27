import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Farmers — PashuRaksha ERP",
  description: "Registered farmers across all districts",
};

export default function FarmersLayout({ children }: { children: React.ReactNode }) {
  return children;
}
