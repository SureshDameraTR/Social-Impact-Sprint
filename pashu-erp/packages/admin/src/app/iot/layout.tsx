import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "IoT Devices — PashuRaksha ERP",
  description: "IoT device monitoring and telemetry readings",
};

export default function IotLayout({ children }: { children: React.ReactNode }) {
  return children;
}
