"use client";

import { useState, useMemo } from "react";
import { useList } from "@refinedev/core";
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  InputAdornment,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Stack,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import SpeciesChip from "@/components/SpeciesChip";
import RiskBadge from "@/components/RiskBadge";

interface Animal {
  id: string;
  name: string;
  species: string;
  breed: string;
  owner: string;
  pashu_aadhaar: string;
  health_status: string;
}

const mockAnimals: Animal[] = [
  { id: "A001", name: "Lakshmi", species: "Cattle", breed: "Gir", owner: "Ramesh Gowda", pashu_aadhaar: "PA-KA-MYS-00001", health_status: "low" },
  { id: "A002", name: "Nandi", species: "Cattle", breed: "Hallikar", owner: "Ramesh Gowda", pashu_aadhaar: "PA-KA-MYS-00002", health_status: "low" },
  { id: "A003", name: "Gauri", species: "Buffalo", breed: "Murrah", owner: "Lakshmi Devi", pashu_aadhaar: "PA-KA-MYS-00003", health_status: "medium" },
  { id: "A004", name: "Meenu", species: "Goat", breed: "Osmanabadi", owner: "Manjunath K", pashu_aadhaar: "PA-KA-MDY-00004", health_status: "low" },
  { id: "A005", name: "Raja", species: "Cattle", breed: "Amrit Mahal", owner: "Krishna Murthy", pashu_aadhaar: "PA-KA-MDY-00005", health_status: "high" },
  { id: "A006", name: "Kaali", species: "Buffalo", breed: "Surti", owner: "Savitri Bai", pashu_aadhaar: "PA-KA-HSN-00006", health_status: "low" },
  { id: "A007", name: "Sheru", species: "Goat", breed: "Jamunapari", owner: "Parvathi Amma", pashu_aadhaar: "PA-KA-CHN-00007", health_status: "critical" },
  { id: "A008", name: "Sundari", species: "Cattle", breed: "Sahiwal", owner: "Suresh Babu", pashu_aadhaar: "PA-KA-KDG-00008", health_status: "low" },
  { id: "A009", name: "Chinna", species: "Sheep", breed: "Bannur", owner: "Meenakshi H", pashu_aadhaar: "PA-KA-MYS-00009", health_status: "medium" },
  { id: "A010", name: "Kokila", species: "Poultry", breed: "Kadaknath", owner: "Basavaraju N", pashu_aadhaar: "PA-KA-HSN-00010", health_status: "low" },
  { id: "A011", name: "Bhadra", species: "Cattle", breed: "Deoni", owner: "Nagaraj P", pashu_aadhaar: "PA-KA-MYS-00011", health_status: "low" },
  { id: "A012", name: "Kamala", species: "Buffalo", breed: "Pandharpuri", owner: "Shivamma R", pashu_aadhaar: "PA-KA-CHN-00012", health_status: "high" },
];

const speciesList = ["All", "Cattle", "Buffalo", "Goat", "Sheep", "Poultry"];

export default function AnimalsPage() {
  const [search, setSearch] = useState("");
  const [speciesFilter, setSpeciesFilter] = useState("All");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const { data } = useList<Animal>({ resource: "animals" });
  const animals = data?.data ?? mockAnimals;

  const filtered = useMemo(
    () =>
      animals.filter((a) => {
        const matchSearch =
          a.name.toLowerCase().includes(search.toLowerCase()) ||
          a.pashu_aadhaar.toLowerCase().includes(search.toLowerCase());
        const matchSpecies = speciesFilter === "All" || a.species === speciesFilter;
        return matchSearch && matchSpecies;
      }),
    [animals, search, speciesFilter]
  );

  return (
    <Box p={3}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Animals
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        {filtered.length} registered animals with Pashu Aadhaar
      </Typography>

      <Paper sx={{ borderRadius: 2 }}>
        <Box p={2}>
          <Stack direction="row" spacing={2} alignItems="center">
            <TextField
              size="small"
              placeholder="Search by name or Pashu Aadhaar..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              sx={{ minWidth: 300 }}
            />
            <FormControl size="small" sx={{ minWidth: 160 }}>
              <InputLabel>Species</InputLabel>
              <Select
                value={speciesFilter}
                label="Species"
                onChange={(e) => {
                  setSpeciesFilter(e.target.value);
                  setPage(0);
                }}
              >
                {speciesList.map((s) => (
                  <MenuItem key={s} value={s}>
                    {s}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Stack>
        </Box>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 700 }}>Name</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Species</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Breed</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Owner</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Pashu Aadhaar</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Health Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filtered
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((animal) => (
                  <TableRow key={animal.id} hover>
                    <TableCell>{animal.name}</TableCell>
                    <TableCell>
                      <SpeciesChip species={animal.species} />
                    </TableCell>
                    <TableCell>{animal.breed}</TableCell>
                    <TableCell>{animal.owner}</TableCell>
                    <TableCell sx={{ fontFamily: "monospace", fontSize: 13 }}>
                      {animal.pashu_aadhaar}
                    </TableCell>
                    <TableCell>
                      <RiskBadge level={animal.health_status} />
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={filtered.length}
          page={page}
          onPageChange={(_, p) => setPage(p)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </Paper>
    </Box>
  );
}
