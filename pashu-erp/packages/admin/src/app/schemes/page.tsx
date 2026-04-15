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
  TableSortLabel,
  CircularProgress,
  Alert,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import { colors, sxCodeCell, sxNameCell, monoFont } from "@/theme/theme";
import { fmtCurrency, fmtDate } from "@/utils/format";
import EmptyState from "@/components/EmptyState";

interface GovtScheme {
  id: string;
  scheme_code: string;
  name: string;
  ministry: string;
  max_subsidy_amount: number | null;
  subsidy_percentage: number | null;
  is_active: boolean;
  valid_from: string;
  valid_to: string;
}

type SortKey = "scheme_code" | "name" | "max_subsidy_amount" | "subsidy_percentage";

export default function SchemesPage() {
  useEffect(() => {
    document.title = 'Govt Schemes — PashuRaksha ERP';
  }, []);

  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [sortBy, setSortBy] = useState<SortKey>("scheme_code");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const { data, isLoading, isError } = useList<GovtScheme>({ resource: "schemes" });

  const schemes = data?.data ?? [];

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

  const filtered = useMemo(() => {
    const result = schemes.filter(
      (s) =>
        s.name.toLowerCase().includes(search.toLowerCase()) ||
        s.scheme_code.toLowerCase().includes(search.toLowerCase())
    );
    result.sort((a, b) => {
      const aVal = a[sortBy];
      const bVal = b[sortBy];
      const cmp = typeof aVal === "string" ? aVal.localeCompare(bVal as string) : (aVal as number) - (bVal as number);
      return sortDir === "asc" ? cmp : -cmp;
    });
    return result;
  }, [schemes, search, sortBy, sortDir]);

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 8 }} role="status" aria-label="Loading"><CircularProgress /></Box>;
  if (isError) return <Box sx={{ p: 4 }}><Alert severity="error">Failed to load data from server.</Alert></Box>;

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom sx={{ color: colors.text }}>
        Government Schemes
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        {schemes.filter((s) => s.is_active).length} active schemes available for farmers
      </Typography>

      <Paper>
        <Box p={2}>
          <TextField
            size="small"
            placeholder="Search by name or code..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search schemes"
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
          <Table aria-label="Schemes table">
            <TableHead>
              <TableRow>
                <TableCell>
                  <TableSortLabel
                    active={sortBy === "scheme_code"}
                    direction={sortBy === "scheme_code" ? sortDir : "asc"}
                    onClick={() => handleSort("scheme_code")}
                  >
                    Code
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortBy === "name"}
                    direction={sortBy === "name" ? sortDir : "asc"}
                    onClick={() => handleSort("name")}
                  >
                    Name
                  </TableSortLabel>
                </TableCell>
                <TableCell>Ministry</TableCell>
                <TableCell align="right">
                  <TableSortLabel
                    active={sortBy === "max_subsidy_amount"}
                    direction={sortBy === "max_subsidy_amount" ? sortDir : "asc"}
                    onClick={() => handleSort("max_subsidy_amount")}
                  >
                    Max Subsidy
                  </TableSortLabel>
                </TableCell>
                <TableCell align="center">
                  <TableSortLabel
                    active={sortBy === "subsidy_percentage"}
                    direction={sortBy === "subsidy_percentage" ? sortDir : "asc"}
                    onClick={() => handleSort("subsidy_percentage")}
                  >
                    Subsidy %
                  </TableSortLabel>
                </TableCell>
                <TableCell>Active</TableCell>
                <TableCell>Valid Period</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filtered.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} sx={{ border: 0 }}>
                    <EmptyState />
                  </TableCell>
                </TableRow>
              ) : (
                filtered
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((scheme) => (
                    <TableRow key={scheme.id}>
                      <TableCell
                        sx={{ ...sxCodeCell, fontWeight: 600, color: colors.primary }}
                      >
                        {scheme.scheme_code}
                      </TableCell>
                      <TableCell sx={{ ...sxNameCell, maxWidth: 280 }}>
                        {scheme.name}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={scheme.ministry}
                          size="small"
                          sx={{
                            bgcolor: `${colors.secondary}15`,
                            color: colors.secondary,
                            border: 'none',
                            fontSize: '11.5px',
                          }}
                        />
                      </TableCell>
                      <TableCell
                        align="right"
                        sx={{ ...sxCodeCell, fontWeight: 600 }}
                      >
                        {scheme.max_subsidy_amount != null ? fmtCurrency(scheme.max_subsidy_amount) : "\u2014"}
                      </TableCell>
                      <TableCell
                        align="center"
                        sx={{ fontFamily: monoFont, fontSize: '12px' }}
                      >
                        {scheme.subsidy_percentage != null ? `${scheme.subsidy_percentage}%` : "\u2014"}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={scheme.is_active ? "Active" : "Expired"}
                          size="small"
                          sx={{
                            fontWeight: 600,
                            fontSize: '11.5px',
                            bgcolor: scheme.is_active ? colors.successLight : '#f0f0f0',
                            color: scheme.is_active ? colors.accentGreen : '#999',
                            border: 'none',
                          }}
                        />
                      </TableCell>
                      <TableCell
                        sx={{ ...sxCodeCell, whiteSpace: "nowrap", fontSize: '11.5px' }}
                      >
                        {fmtDate(scheme.valid_from)} -{" "}
                        {fmtDate(scheme.valid_to)}
                      </TableCell>
                    </TableRow>
                  ))
              )}
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
