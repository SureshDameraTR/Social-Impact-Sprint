import { useQuery } from "@tanstack/react-query";
import { api } from "../config/api";

interface SpeciesRecord {
  code: string;
  name_en: string;
  name_kn: string | null;
  name_hi: string | null;
  emoji: string | null;
  is_active: boolean;
}

interface BreedRecord {
  id: string;
  name: string;
  species_code: string;
  origin: string | null;
  is_indigenous: boolean;
}

interface DistrictRecord {
  lgd_code: number;
  name: string;
  name_local: string | null;
  latitude: number | null;
  longitude: number | null;
}

interface ListResponse<T> {
  data: T[];
  total: number;
}

export function useSpecies() {
  return useQuery({
    queryKey: ["reference", "species"],
    queryFn: () =>
      api.get<ListResponse<SpeciesRecord>>("/v1/reference/species"),
    staleTime: 24 * 60 * 60 * 1000,
  });
}

export function useBreeds(speciesCode?: string) {
  return useQuery({
    queryKey: ["reference", "breeds", speciesCode],
    queryFn: () =>
      api.get<ListResponse<BreedRecord>>(
        `/v1/reference/breeds${speciesCode ? `?species_code=${speciesCode}` : ""}`
      ),
    staleTime: 24 * 60 * 60 * 1000,
    enabled: !!speciesCode,
  });
}

export function useDistricts(stateLgdCode: number = 29) {
  return useQuery({
    queryKey: ["reference", "districts", stateLgdCode],
    queryFn: () =>
      api.get<ListResponse<DistrictRecord>>(
        `/v1/reference/districts?state_lgd_code=${stateLgdCode}`
      ),
    staleTime: 7 * 24 * 60 * 60 * 1000,
  });
}
