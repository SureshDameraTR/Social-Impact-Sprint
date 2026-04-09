/**
 * Reference data: Medicine withdrawal periods.
 * These are regulatory constants from FSSAI/DAHD guidelines.
 * TODO: Fetch from API /medicines/reference in future.
 */

export interface Medicine {
  key: string;
  name: string;
  withdrawalDays: { milk: number; meat: number };
}

export const MEDICINES: Medicine[] = [
  { key: 'oxytetracycline', name: 'Oxytetracycline', withdrawalDays: { milk: 7, meat: 28 } },
  { key: 'ivermectin', name: 'Ivermectin', withdrawalDays: { milk: 5, meat: 35 } },
  { key: 'penicillin', name: 'Penicillin', withdrawalDays: { milk: 4, meat: 14 } },
  { key: 'enrofloxacin', name: 'Enrofloxacin', withdrawalDays: { milk: 7, meat: 14 } },
  { key: 'albendazole', name: 'Albendazole', withdrawalDays: { milk: 5, meat: 14 } },
  { key: 'meloxicam', name: 'Meloxicam', withdrawalDays: { milk: 5, meat: 15 } },
  { key: 'amoxicillin', name: 'Amoxicillin', withdrawalDays: { milk: 3, meat: 21 } },
];
