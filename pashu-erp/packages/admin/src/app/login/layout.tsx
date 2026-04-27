import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Login — PashuRaksha ERP",
  description: "Admin portal login",
};

export default function LoginLayout({ children }: { children: React.ReactNode }) {
  return children;
}
