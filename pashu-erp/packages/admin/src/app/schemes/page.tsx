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
  code: string;
  name: string;
  ministry: string;
  max_subsidy: number;
  subsidy_pct: number;
  active: boolean;
  valid_from: string;
  valid_to: string;
}

type SortKey = "code" | "name" | "max_subsidy" | "subsidy_pct";

export default function SchemesPage() {
  useEffect(() => {
    document.title = 'Govt Schemes — PashuRaksha ERP';
  }, []);

  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [sortBy, setSortBy] = useState<SortKey>("code");
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
        s.code.toLowerCase().includes(search.toLowerCase())
    );
    result.sort((a, b) => {
      const aVal = a[sortBy];
      const bVal = b[sortBy];
      const cmp = typeof aVal === "string" ? aVal.localeCompare(bVal as string) : (aVal as number) - (bVal as number);
      return sortDir === "asc" ? cmp : -cmp;
    });
    return result;
  }, [schemes, search, sortBy, sortDir]);

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 8 }}><CircularProgress /></Box>;
  if (isError) return <Box sx={{ p: 4 }}><Alert severity="error">Failed to load data from server.</Alert></Box>;

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom sx={{ color: colors.text }}>
        Government Schemes
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        {schemes.filter((s) => s.active).length} active schemes available for farmers
      </Typography>

      <Paper>
        <Box p={2}>
          <TextField
            size="small"
            placeholder="Search by name or code..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
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
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>
                  <TableSortLabel
                    active={sortBy === "code"}
                    direction={sortBy === "code" ? sortDir : "asc"}
                    onClick={() => handleSort("code")}
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
                    active={sortBy === "max_subsidy"}
                    direction={sortBy === "max_subsidy" ? sortDir : "asc"}
                    onClick={() => handleSort("max_subsidy")}
                  >
                    Max Subsidy
                  </TableSortLabel>
                </TableCell>
                <TableCell align="center">
                  <TableSortLabel
                    active={sortBy === "subsidy_pct"}
                    direction={sortBy === "subsidy_pct" ? sortDir : "asc"}
                    onClick={() => handleSort("subsidy_pct")}
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
                        {scheme.code}
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
                        {fmtCurrency(scheme.max_subsidy)}
                      </TableCell>
                      <TableCell
                        align="center"
                        sx={{ fontFamily: monoFont, fontSize: '12px' }}
                      >
                        {scheme.subsidy_pct}%
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={scheme.active ? "Active" : "Expired"}
                          size="small"
                          sx={{
                            fontWeight: 600,
                            fontSize: '11.5px',
                            bgcolor: scheme.active ? colors.successLight : '#f0f0f0',
                            color: scheme.active ? colors.accentGreen : '#999',
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
