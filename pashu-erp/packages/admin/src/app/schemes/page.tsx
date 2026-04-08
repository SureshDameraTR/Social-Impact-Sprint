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
  Chip,
  TableSortLabel,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";

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

const mockSchemes: GovtScheme[] = [
  { id: "S001", code: "NADCP", name: "National Animal Disease Control Programme", ministry: "MoAHD", max_subsidy: 500000, subsidy_pct: 100, active: true, valid_from: "2024-01-01", valid_to: "2027-03-31" },
  { id: "S002", code: "DEDS", name: "Dairy Entrepreneurship Development Scheme", ministry: "MoAHD", max_subsidy: 700000, subsidy_pct: 33, active: true, valid_from: "2024-04-01", valid_to: "2027-03-31" },
  { id: "S003", code: "RGM", name: "Rashtriya Gokul Mission", ministry: "MoAHD", max_subsidy: 250000, subsidy_pct: 50, active: true, valid_from: "2023-04-01", valid_to: "2026-03-31" },
  { id: "S004", code: "NLM-EDS", name: "NLM - Entrepreneurship Development & Employment Generation", ministry: "MoAHD", max_subsidy: 1000000, subsidy_pct: 50, active: true, valid_from: "2024-04-01", valid_to: "2026-12-31" },
  { id: "S005", code: "AHIDF", name: "Animal Husbandry Infrastructure Dev Fund", ministry: "MoAHD", max_subsidy: 3000000, subsidy_pct: 3, active: true, valid_from: "2024-01-01", valid_to: "2026-12-31" },
  { id: "S006", code: "KMF-BNS", name: "KMF Bonus Scheme (State)", ministry: "Karnataka AHD", max_subsidy: 50000, subsidy_pct: 100, active: true, valid_from: "2025-04-01", valid_to: "2026-03-31" },
  { id: "S007", code: "PMFBY-L", name: "PM Fasal Bima - Livestock Component", ministry: "MoA&FW", max_subsidy: 200000, subsidy_pct: 50, active: true, valid_from: "2024-06-01", valid_to: "2026-05-31" },
  { id: "S008", code: "KVIC-HD", name: "KVIC Honey & Dairy Mission", ministry: "MSME", max_subsidy: 150000, subsidy_pct: 60, active: false, valid_from: "2023-01-01", valid_to: "2025-12-31" },
];

type SortKey = "code" | "name" | "max_subsidy" | "subsidy_pct";

export default function SchemesPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [sortBy, setSortBy] = useState<SortKey>("code");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const { data } = useList<GovtScheme>({ resource: "schemes" });
  const schemes = data?.data ?? mockSchemes;

  const handleSort = (key: SortKey) => {
    if (sortBy === key) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortBy(key);
      setSortDir("asc");
    }
  };

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

  const fmtCurrency = (n: number) =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(n);

  return (
    <Box p={3}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Government Schemes
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        {schemes.filter((s) => s.active).length} active schemes available for farmers
      </Typography>

      <Paper sx={{ borderRadius: 2 }}>
        <Box p={2}>
          <TextField
            size="small"
            placeholder="Search by name or code..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
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
                <TableCell sx={{ fontWeight: 700 }}>
                  <TableSortLabel
                    active={sortBy === "code"}
                    direction={sortBy === "code" ? sortDir : "asc"}
                    onClick={() => handleSort("code")}
                  >
                    Code
                  </TableSortLabel>
                </TableCell>
                <TableCell sx={{ fontWeight: 700 }}>
                  <TableSortLabel
                    active={sortBy === "name"}
                    direction={sortBy === "name" ? sortDir : "asc"}
                    onClick={() => handleSort("name")}
                  >
                    Name
                  </TableSortLabel>
                </TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Ministry</TableCell>
                <TableCell sx={{ fontWeight: 700 }} align="right">
                  <TableSortLabel
                    active={sortBy === "max_subsidy"}
                    direction={sortBy === "max_subsidy" ? sortDir : "asc"}
                    onClick={() => handleSort("max_subsidy")}
                  >
                    Max Subsidy
                  </TableSortLabel>
                </TableCell>
                <TableCell sx={{ fontWeight: 700 }} align="center">
                  <TableSortLabel
                    active={sortBy === "subsidy_pct"}
                    direction={sortBy === "subsidy_pct" ? sortDir : "asc"}
                    onClick={() => handleSort("subsidy_pct")}
                  >
                    Subsidy %
                  </TableSortLabel>
                </TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Active</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Valid Period</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filtered
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((scheme) => (
                  <TableRow key={scheme.id} hover>
                    <TableCell sx={{ fontFamily: "monospace", fontWeight: 600 }}>
                      {scheme.code}
                    </TableCell>
                    <TableCell sx={{ maxWidth: 280 }}>{scheme.name}</TableCell>
                    <TableCell>
                      <Chip label={scheme.ministry} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell align="right" sx={{ fontWeight: 600 }}>
                      {fmtCurrency(scheme.max_subsidy)}
                    </TableCell>
                    <TableCell align="center">{scheme.subsidy_pct}%</TableCell>
                    <TableCell>
                      <Chip
                        label={scheme.active ? "Active" : "Expired"}
                        size="small"
                        color={scheme.active ? "success" : "default"}
                      />
                    </TableCell>
                    <TableCell sx={{ whiteSpace: "nowrap", fontSize: 13 }}>
                      {new Date(scheme.valid_from).toLocaleDateString("en-IN")} -{" "}
                      {new Date(scheme.valid_to).toLocaleDateString("en-IN")}
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
