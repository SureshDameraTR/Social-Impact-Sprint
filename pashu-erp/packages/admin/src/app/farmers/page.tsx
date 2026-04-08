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
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";

interface Farmer {
  id: string;
  name: string;
  phone: string;
  district: string;
  village: string;
  animals_count: number;
  registered_date: string;
}

const mockFarmers: Farmer[] = [
  { id: "F001", name: "Ramesh Gowda", phone: "+919876543210", district: "Mysuru", village: "Hullahalli", animals_count: 8, registered_date: "2025-11-15" },
  { id: "F002", name: "Lakshmi Devi", phone: "+919876543211", district: "Mysuru", village: "T. Narasipura", animals_count: 5, registered_date: "2025-12-02" },
  { id: "F003", name: "Manjunath K", phone: "+919876543212", district: "Mandya", village: "Nagamangala", animals_count: 12, registered_date: "2025-10-20" },
  { id: "F004", name: "Savitri Bai", phone: "+919876543213", district: "Hassan", village: "Channarayapatna", animals_count: 3, registered_date: "2026-01-10" },
  { id: "F005", name: "Krishna Murthy", phone: "+919876543214", district: "Mandya", village: "Pandavapura", animals_count: 7, registered_date: "2025-09-05" },
  { id: "F006", name: "Parvathi Amma", phone: "+919876543215", district: "Chamarajanagar", village: "Gundlupet", animals_count: 4, registered_date: "2026-02-18" },
  { id: "F007", name: "Suresh Babu", phone: "+919876543216", district: "Kodagu", village: "Virajpet", animals_count: 15, registered_date: "2025-08-22" },
  { id: "F008", name: "Meenakshi H", phone: "+919876543217", district: "Mysuru", village: "Nanjangud", animals_count: 6, registered_date: "2026-03-01" },
  { id: "F009", name: "Basavaraju N", phone: "+919876543218", district: "Hassan", village: "Arsikere", animals_count: 9, registered_date: "2025-11-30" },
  { id: "F010", name: "Geetha Kumari", phone: "+919876543219", district: "Mandya", village: "Srirangapatna", animals_count: 2, registered_date: "2026-01-25" },
  { id: "F011", name: "Nagaraj P", phone: "+919876543220", district: "Mysuru", village: "Hunsur", animals_count: 11, registered_date: "2025-07-14" },
  { id: "F012", name: "Shivamma R", phone: "+919876543221", district: "Chamarajanagar", village: "Kollegal", animals_count: 6, registered_date: "2026-02-05" },
];

export default function FarmersPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // Try API, fallback to mock
  const { data, isLoading } = useList<Farmer>({
    resource: "farmers",
    pagination: { current: page + 1, pageSize: rowsPerPage },
  });

  const farmers = data?.data ?? mockFarmers;

  const filtered = useMemo(
    () =>
      farmers.filter(
        (f) =>
          f.name.toLowerCase().includes(search.toLowerCase()) ||
          f.phone.includes(search)
      ),
    [farmers, search]
  );

  return (
    <Box p={3}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Farmers
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        {filtered.length} registered farmers across all districts
      </Typography>

      <Paper sx={{ borderRadius: 2 }}>
        <Box p={2}>
          <TextField
            size="small"
            placeholder="Search by name or phone..."
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
                <TableCell sx={{ fontWeight: 700 }}>Name</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Phone</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>District</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Village</TableCell>
                <TableCell sx={{ fontWeight: 700 }} align="center">Animals</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Registered</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filtered
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((farmer) => (
                  <TableRow key={farmer.id} hover>
                    <TableCell>{farmer.name}</TableCell>
                    <TableCell>{farmer.phone}</TableCell>
                    <TableCell>
                      <Chip label={farmer.district} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>{farmer.village}</TableCell>
                    <TableCell align="center">
                      <Chip label={farmer.animals_count} size="small" color="primary" />
                    </TableCell>
                    <TableCell>
                      {new Date(farmer.registered_date).toLocaleDateString("en-IN")}
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
