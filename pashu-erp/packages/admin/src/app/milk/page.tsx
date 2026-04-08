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
  Stack,
  Chip,
} from "@mui/material";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

interface MilkRecord {
  id: string;
  date: string;
  farmer: string;
  animal: string;
  quantity: number;
  session: "Morning" | "Evening";
  center: string;
}

const mockMilk: MilkRecord[] = [
  { id: "M001", date: "2026-04-08", farmer: "Ramesh Gowda", animal: "Lakshmi", quantity: 8.5, session: "Morning", center: "Hullahalli MC" },
  { id: "M002", date: "2026-04-08", farmer: "Ramesh Gowda", animal: "Nandi", quantity: 6.2, session: "Morning", center: "Hullahalli MC" },
  { id: "M003", date: "2026-04-08", farmer: "Lakshmi Devi", animal: "Gauri", quantity: 12.0, session: "Morning", center: "T. Narasipura MC" },
  { id: "M004", date: "2026-04-08", farmer: "Suresh Babu", animal: "Sundari", quantity: 9.8, session: "Morning", center: "Virajpet MC" },
  { id: "M005", date: "2026-04-07", farmer: "Ramesh Gowda", animal: "Lakshmi", quantity: 7.2, session: "Evening", center: "Hullahalli MC" },
  { id: "M006", date: "2026-04-07", farmer: "Krishna Murthy", animal: "Raja", quantity: 5.5, session: "Evening", center: "Pandavapura MC" },
  { id: "M007", date: "2026-04-07", farmer: "Lakshmi Devi", animal: "Gauri", quantity: 11.0, session: "Morning", center: "T. Narasipura MC" },
  { id: "M008", date: "2026-04-07", farmer: "Nagaraj P", animal: "Bhadra", quantity: 7.8, session: "Morning", center: "Hunsur MC" },
  { id: "M009", date: "2026-04-06", farmer: "Suresh Babu", animal: "Sundari", quantity: 10.2, session: "Morning", center: "Virajpet MC" },
  { id: "M010", date: "2026-04-06", farmer: "Meenakshi H", animal: "Chinna", quantity: 3.5, session: "Evening", center: "Nanjangud MC" },
  { id: "M011", date: "2026-04-06", farmer: "Ramesh Gowda", animal: "Nandi", quantity: 6.8, session: "Morning", center: "Hullahalli MC" },
  { id: "M012", date: "2026-04-05", farmer: "Shivamma R", animal: "Kamala", quantity: 9.0, session: "Morning", center: "Kollegal MC" },
];

// Daily summary for chart
const dailySummary = [
  { date: "Apr 3", morning: 920, evening: 680 },
  { date: "Apr 4", morning: 1050, evening: 740 },
  { date: "Apr 5", morning: 980, evening: 710 },
  { date: "Apr 6", morning: 1120, evening: 790 },
  { date: "Apr 7", morning: 1080, evening: 750 },
  { date: "Apr 8", morning: 1200, evening: 0 },
];

export default function MilkPage() {
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const { data } = useList<MilkRecord>({ resource: "milk" });
  const records = data?.data ?? mockMilk;

  const filtered = useMemo(() => {
    return records.filter((r) => {
      if (dateFrom && r.date < dateFrom) return false;
      if (dateTo && r.date > dateTo) return false;
      return true;
    });
  }, [records, dateFrom, dateTo]);

  const totalToday = mockMilk
    .filter((r) => r.date === "2026-04-08")
    .reduce((sum, r) => sum + r.quantity, 0);

  return (
    <Box p={3}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Milk Collection
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        Today&apos;s total: {totalToday.toFixed(1)} L from{" "}
        {mockMilk.filter((r) => r.date === "2026-04-08").length} entries
      </Typography>

      {/* Daily Summary Chart */}
      <Paper sx={{ p: 3, borderRadius: 2, mb: 3 }}>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          Daily Collection Summary
        </Typography>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={dailySummary}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="morning" fill="#00695c" name="Morning (L)" />
            <Bar dataKey="evening" fill="#0288d1" name="Evening (L)" />
          </BarChart>
        </ResponsiveContainer>
      </Paper>

      <Paper sx={{ borderRadius: 2 }}>
        <Box p={2}>
          <Stack direction="row" spacing={2} alignItems="center">
            <TextField
              size="small"
              type="date"
              label="From"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              size="small"
              type="date"
              label="To"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Stack>
        </Box>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 700 }}>Date</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Farmer</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Animal</TableCell>
                <TableCell sx={{ fontWeight: 700 }} align="right">Quantity (L)</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Session</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Center</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filtered
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((rec) => (
                  <TableRow key={rec.id} hover>
                    <TableCell>{new Date(rec.date).toLocaleDateString("en-IN")}</TableCell>
                    <TableCell>{rec.farmer}</TableCell>
                    <TableCell>{rec.animal}</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 600 }}>
                      {rec.quantity.toFixed(1)}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={rec.session}
                        size="small"
                        color={rec.session === "Morning" ? "warning" : "info"}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>{rec.center}</TableCell>
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
