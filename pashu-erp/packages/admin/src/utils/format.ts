const currencyFormatter = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

export const fmtCurrency = (n: number) => currencyFormatter.format(n);

export const fmtDate = (d: string | null | undefined): string => {
  if (!d) return "\u2014";
  const date = new Date(d);
  if (isNaN(date.getTime())) return d;
  return date.toLocaleDateString("en-IN", { timeZone: "Asia/Kolkata" });
};
