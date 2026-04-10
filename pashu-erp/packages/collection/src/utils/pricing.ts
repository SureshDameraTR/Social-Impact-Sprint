const FAT_SLABS = [
  { min: 3.0, max: 3.5, rate: 7.50 },
  { min: 3.5, max: 4.0, rate: 8.00 },
  { min: 4.0, max: 4.5, rate: 8.50 },
  { min: 4.5, max: 5.0, rate: 9.00 },
  { min: 5.0, max: 5.5, rate: 9.50 },
  { min: 5.5, max: 6.0, rate: 10.00 },
  { min: 6.0, max: 7.0, rate: 10.50 },
  { min: 7.0, max: 10.0, rate: 11.00 },
];

const SNF_SLABS = [
  { min: 8.0, max: 8.3, rate: 5.00 },
  { min: 8.3, max: 8.5, rate: 5.50 },
  { min: 8.5, max: 8.8, rate: 6.00 },
  { min: 8.8, max: 9.0, rate: 6.50 },
  { min: 9.0, max: 10.0, rate: 7.00 },
];

function getSlabRate(value: number, slabs: { min: number; max: number; rate: number }[]): number {
  for (const slab of slabs) {
    if (value >= slab.min && value < slab.max) return slab.rate;
  }
  if (value >= slabs[slabs.length - 1].max) return slabs[slabs.length - 1].rate;
  return slabs[0].rate;
}

export function calculateRate(fatPct: number, snfPct: number): number {
  const fatRate = getSlabRate(fatPct, FAT_SLABS);
  const snfRate = getSlabRate(snfPct, SNF_SLABS);
  return Math.round(((fatPct * fatRate + snfPct * snfRate) / 2) * 100) / 100;
}
