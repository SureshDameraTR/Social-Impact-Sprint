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
  Chip,
  Avatar,
  TableSortLabel,
  CircularProgress,
  Alert,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import { colors, sxCodeCell, sxNameCell } from "@/theme/theme";
import { fmtDate } from "@/utils/format";
import EmptyState from "@/components/EmptyState";

interface Farmer {
  id: string;
  name: string;
  phone: string;
  district: string;
  village_code: string;
  animals_count: number;
  registered_date: string;
}

const districtColors: Record<string, string> = {
  Mysuru: colors.primary,
  Mandya: colors.accentBlue,
  Hassan: colors.accentAmber,
  Chamarajanagar: colors.accentRed,
  Kodagu: colors.accentGreen,
};

function getInitials(name: string) {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

type SortKey = "name" | "district" | "animals_count" | "registered_date";

export default function FarmersPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [sortBy, setSortBy] = useState<SortKey | "">("");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const { data, isLoading, isError } = useList<Farmer>({
    resource: "farmers",
    pagination: { current: page + 1, pageSize: rowsPerPage },
    sorters: sortBy ? [{ field: sortBy, order: sortDir }] : [],
  });

  const farmers = data?.data ?? [];
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
    setPage(0);
  }, []);

  const filtered = useMemo(
    () =>
      farmers.filter(
        (f) =>
          (f.name || "").toLowerCase().includes(search.toLowerCase()) ||
          (f.phone || "").includes(search)
      ),
    [farmers, search]
  );

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 8 }} role="status" aria-label="Loading"><CircularProgress /></Box>;
  if (isError) return <Box sx={{ p: 4 }}><Alert severity="error">Failed to load data from server.</Alert></Box>;

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom sx={{ color: colors.text }}>
        Farmers
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        {filtered.length} registered farmers across all districts
      </Typography>

      <Paper>
        <Box p={2}>
          <TextField
            size="small"
            placeholder="Search by name or phone..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search farmers"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ color: colors.textLight }} />
                </InputAdornment>
              ),
            }}
            sx={{ minWidth: 320 }}
          />
        </Box>
        <TableContainer>
          <Table aria-label="Farmers table">
            <TableHead>
              <TableRow>
                <TableCell>
                  <TableSortLabel active={sortBy === "name"} direction={sortBy === "name" ? sortDir : "asc"} onClick={() => handleSort("name")}>
                    Name
                  </TableSortLabel>
                </TableCell>
                <TableCell>Phone</TableCell>
                <TableCell>
                  <TableSortLabel active={sortBy === "district"} direction={sortBy === "district" ? sortDir : "asc"} onClick={() => handleSort("district")}>
                    District
                  </TableSortLabel>
                </TableCell>
                <TableCell>Village</TableCell>
                <TableCell align="center">
                  <TableSortLabel active={sortBy === "animals_count"} direction={sortBy === "animals_count" ? sortDir : "asc"} onClick={() => handleSort("animals_count")}>
                    Animals
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel active={sortBy === "registered_date"} direction={sortBy === "registered_date" ? sortDir : "asc"} onClick={() => handleSort("registered_date")}>
                    Registered
                  </TableSortLabel>
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filtered.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} sx={{ border: 0 }}>
                    <EmptyState />
                  </TableCell>
                </TableRow>
              ) : (
                filtered.map((farmer) => (
                    <TableRow key={farmer.id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                          <Avatar
                            sx={{
                              width: 30,
                              height: 30,
                              fontSize: '11px',
                              fontWeight: 600,
                              bgcolor: colors.primaryLight,
                              color: colors.primary,
                            }}
                          >
                            {getInitials(farmer.name)}
                          </Avatar>
                          <Typography sx={{ fontWeight: 500, fontSize: '13px', color: colors.text }}>
                            {farmer.name}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell
                        sx={sxCodeCell}
                      >
                        {farmer.phone}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={farmer.district}
                          size="small"
                          sx={{
                            bgcolor: `${districtColors[farmer.district] || colors.primary}15`,
                            color: districtColors[farmer.district] || colors.primary,
                            border: 'none',
                            fontWeight: 500,
                            fontSize: '12px',
                          }}
                        />
                      </TableCell>
                      <TableCell>{farmer.village_code}</TableCell>
                      <TableCell align="center">
                        <Chip
                          label={farmer.animals_count}
                          size="small"
                          sx={{
                            bgcolor: colors.primaryLight,
                            color: colors.primary,
                            fontWeight: 600,
                            fontSize: '12px',
                            border: 'none',
                          }}
                        />
                      </TableCell>
                      <TableCell
                        sx={{ fontSize: '12px', color: colors.textDim }}
                      >
                        {fmtDate(farmer.registered_date)}
                      </TableCell>
                    </TableRow>
                  ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={search ? filtered.length : serverTotal}
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
