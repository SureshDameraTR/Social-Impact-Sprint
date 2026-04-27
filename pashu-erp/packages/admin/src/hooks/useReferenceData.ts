import { useList } from "@refinedev/core";

interface SpeciesRecord {
  code: string;
  name_en: string;
  name_kn?: string;
}

interface BreedRecord {
  id: string;
  name: string;
  name_local?: string;
  species_code: string;
  origin?: string;
  nbagr_code?: string;
  is_indigenous: boolean;
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
  const resource = speciesCode
    ? `reference/breeds?species_code=${encodeURIComponent(speciesCode)}`
    : "reference/breeds";
  const { data, isLoading } = useList<BreedRecord>({
    resource,
    pagination: { mode: "off" },
  });
  return { breeds: data?.data ?? [], isLoading };
}

export function useDistricts(stateLgdCode: number = 29) {
  const { data, isLoading } = useList<DistrictRecord>({
    resource: `reference/districts?state_lgd_code=${stateLgdCode}`,
    pagination: { mode: "off" },
  });
  return { districts: data?.data ?? [], isLoading };
}
