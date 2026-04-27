import { useList } from "@refinedev/core";

interface SpeciesRecord {
  code: string;
  name_en: string;
  name_kn?: string;
}

interface BreedRecord {
  code: string;
  name_en: string;
  species_code: string;
}

interface DistrictRecord {
  lgd_code: number;
  name: string;
  state_lgd_code: number;
}

export function useSpecies() {
  const { data, isLoading } = useList<SpeciesRecord>({
    resource: "reference/species",
    pagination: { mode: "off" },
  });
  return {
    species: data?.data ?? [],
    speciesNames: (data?.data ?? []).map((s) => s.name_en),
    isLoading,
  };
}

export function useBreeds(speciesCode?: string) {
  const { data, isLoading } = useList<BreedRecord>({
    resource: "reference/breeds",
    filters: speciesCode
      ? [{ field: "species_code", operator: "eq" as const, value: speciesCode }]
      : [],
    pagination: { mode: "off" },
  });
  return { breeds: data?.data ?? [], isLoading };
}

export function useDistricts(stateLgdCode: number = 29) {
  const { data, isLoading } = useList<DistrictRecord>({
    resource: "reference/districts",
    filters: [
      { field: "state_lgd_code", operator: "eq" as const, value: stateLgdCode },
    ],
    pagination: { mode: "off" },
  });
  return { districts: data?.data ?? [], isLoading };
}
