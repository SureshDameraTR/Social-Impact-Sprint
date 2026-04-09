export const RESOURCE_NAMES = {
  animals: "animals",
  farmers: "farmers",
  health: "health",
  milk: "milk",
  marketplace: "marketplace",
  schemes: "schemes",
  vaccinations: "vaccinations",
  income: "income",
  iot: "iot",
  map: "map",
} as const;

export const RISK_LEVELS = ["critical", "high", "medium", "low"] as const;
export type RiskLevel = (typeof RISK_LEVELS)[number];

export const SPECIES = [
  "Cattle",
  "Buffalo",
  "Goat",
  "Sheep",
  "Poultry",
] as const;
export type Species = (typeof SPECIES)[number];
