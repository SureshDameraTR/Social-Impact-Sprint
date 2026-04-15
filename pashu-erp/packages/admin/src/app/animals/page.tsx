"use client";

import { useState, useMemo, useEffect, useCallback } from "react";
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
  Chip,
  TableSortLabel,
  CircularProgress,
  Alert,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import SpeciesChip from "@/components/SpeciesChip";
import { colors, sxCodeCell, sxNameCell } from "@/theme/theme";
import EmptyState from "@/components/EmptyState";

interface Animal {
  id: string;
  name: string;
  species: string;
  breed: string;
  user_id: string;
  pashu_aadhaar_id: string;
  sex: string;
}

const speciesList = ["All", "Cattle", "Buffalo", "Goat", "Sheep", "Poultry"];

type SortKey = "name" | "species" | "user_id" | "sex";

export default function AnimalsPage() {
  useEffect(() => {
    document.title = 'Animals — PashuRaksha ERP';
  }, []);

  const [search, setSearch] = useState("");
  const [speciesFilter, setSpeciesFilter] = useState("All");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [sortBy, setSortBy] = useState<SortKey | "">("");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const { data, isLoading, isError } = useList<Animal>({
    resource: "animals",
    pagination: {
      current: page + 1,
      pageSize: rowsPerPage,
    },
  });

  const animals = data?.data ?? [];
  const serverTotal = data?.total ?? 0;

  const handleSort = useCallback((key: SortKey) => {
    setSortBy((prev) => {
      if (prev === key) {
        setSortDir((d) => (d === "asc" ? "desc" : "asc"));
        return prev;
      }
      setSortDir("asc");
      return key;
    });
  }, []);

  const filtered = useMemo(
    () =>
      animals.filter((a) => {
        const matchSearch =
          (a.name || "").toLowerCase().includes(search.toLowerCase()) ||
          (a.pashu_aadhaar_id || "").toLowerCase().includes(search.toLowerCase());
        const matchSpecies = speciesFilter === "All" || (a.species || "").toLowerCase() === speciesFilter.toLowerCase();
        return matchSearch && matchSpecies;
      }),
    [animals, search, speciesFilter]
  );

  const sortedRows = useMemo(() => {
    if (!sortBy) return filtered;
    const sorted = [...filtered];
    sorted.sort((a, b) => {
      const cmp = a[sortBy].localeCompare(b[sortBy]);
      return sortDir === "asc" ? cmp : -cmp;
    });
    return sorted;
  }, [filtered, sortBy, sortDir]);

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 8 }} role="status" aria-label="Loading"><CircularProgress /></Box>;
  if (isError) return <Box sx={{ p: 4 }}><Alert severity="error">Failed to load data from server.</Alert></Box>;

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom sx={{ color: colors.text }}>
        Animals
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        {filtered.length} registered animals with Pashu Aadhaar
      </Typography>

      <Paper>
        <Box p={2}>
          <Stack direction="row" spacing={2} alignItems="center">
            <TextField
              size="small"
              placeholder="Search by name or Pashu Aadhaar..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              aria-label="Search animals"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon sx={{ color: colors.textLight }} />
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
          <Table aria-label="Animals table">
            <TableHead>
              <TableRow>
                <TableCell>
                  <TableSortLabel active={sortBy === "name"} direction={sortBy === "name" ? sortDir : "asc"} onClick={() => handleSort("name")}>
                    Name
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel active={sortBy === "species"} direction={sortBy === "species" ? sortDir : "asc"} onClick={() => handleSort("species")}>
                    Species
                  </TableSortLabel>
                </TableCell>
                <TableCell>Breed</TableCell>
                <TableCell>Owner ID</TableCell>
                <TableCell>Pashu Aadhaar</TableCell>
                <TableCell>
                  <TableSortLabel active={sortBy === "sex"} direction={sortBy === "sex" ? sortDir : "asc"} onClick={() => handleSort("sex")}>
                    Sex
                  </TableSortLabel>
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sortedRows.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} sx={{ border: 0 }}>
                    <EmptyState />
                  </TableCell>
                </TableRow>
              ) : (
                sortedRows
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((animal) => (
                    <TableRow key={animal.id}>
                      <TableCell sx={sxNameCell}>
                        {animal.name}
                      </TableCell>
                      <TableCell>
                        <SpeciesChip species={animal.species} />
                      </TableCell>
                      <TableCell>{animal.breed}</TableCell>
                      <TableCell sx={{ fontSize: '11px', color: colors.textDim }}>{animal.user_id?.slice(0, 8)}</TableCell>
                      <TableCell
                        sx={sxCodeCell}
                      >
                        {animal.pashu_aadhaar_id}
                      </TableCell>
                      <TableCell>
                        <Chip label={animal.sex} size="small" sx={{ textTransform: 'capitalize', bgcolor: colors.primaryLight, color: colors.primary, border: 'none', fontSize: '11.5px' }} />
                      </TableCell>
                    </TableRow>
                  ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={search || speciesFilter !== "All" ? sortedRows.length : serverTotal}
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
