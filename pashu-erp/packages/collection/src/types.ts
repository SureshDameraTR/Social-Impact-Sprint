export type Shift = "morning" | "evening";

export interface Farmer {
  id: string;
  name: string;
  phone: string;
  aadhaar_last4: string | null;
  village_code: string | null;
  district: string | null;
}

export const inrFormatter = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
});

export const inrFormatterRounded = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});
