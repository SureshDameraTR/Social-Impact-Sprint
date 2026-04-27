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
  TableSortLabel,
  CircularProgress,
  Alert,
} from "@mui/material";
import dynamic from "next/dynamic";
import { colors, sxCodeCell, sxNameCell, tooltipStyle, axisTickStyle, gridStroke } from "@/theme/theme";
import { fmtDate } from "@/utils/format";
import EmptyState from "@/components/EmptyState";

interface MilkRecord {
  id: string;
  recorded_at: string;
  user_id: string;
  animal_id: string;
  quantity_liters: number;
  session: "morning" | "evening";
  notes: string | null;
}

interface DailySummary {
  date: string;
  total: number;
}

const {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} = require("recharts") as typeof import("recharts");

function MilkChart({ data }: { data: DailySummary[] }) {

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
        <XAxis dataKey="date" tick={axisTickStyle} tickLine={false} />
        <YAxis tick={axisTickStyle} tickLine={false} />
        <Tooltip contentStyle={tooltipStyle} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Bar dataKey="total" fill={colors.primary} name="Total (L)" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

const MilkChartLazy = dynamic(() => Promise.resolve(MilkChart), {
  ssr: false,
  loading: () => (
    <Box sx={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: 'grey.100', borderRadius: 1 }}>
      Loading chart...
    </Box>
  ),
});

type SortKey = "recorded_at" | "quantity_liters" | "session";

export default function MilkPage() {
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [sortBy, setSortBy] = useState<SortKey | "">("");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const { data, isLoading, isError } = useList<MilkRecord>({
    resource: "milk",
    pagination: { current: page + 1, pageSize: rowsPerPage },
    sorters: sortBy ? [{ field: sortBy, order: sortDir }] : [],
  });

  const records = data?.data ?? [];
  const serverTotal = data?.total ?? 0;

  const handleSort = (key: SortKey) => {
    if (sortBy === key) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortBy(key);
      setSortDir("asc");
    }
    setPage(0);
  };

  const filtered = useMemo(() => {
    return records.filter((r) => {
      const d = r.recorded_at?.split("T")[0] ?? "";
      if (dateFrom && d < dateFrom) return false;
      if (dateTo && d > dateTo) return false;
      return true;
    });
  }, [records, dateFrom, dateTo]);

  const todayStr = new Date().toISOString().split('T')[0];
  const todayRecords = records.filter((r) => (r.recorded_at?.split("T")[0] ?? "") === todayStr);
  const totalToday = todayRecords.reduce((sum, r) => sum + (Number(r.quantity_liters) || 0), 0);

  const dailySummary: DailySummary[] = useMemo(() => {
    const map: Record<string, number> = {};
    records.forEach((r) => {
      const d = r.recorded_at?.split("T")[0] ?? "";
      map[d] = (map[d] || 0) + (Number(r.quantity_liters) || 0);
    });
    return Object.entries(map)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([date, total]) => ({ date, total: Math.round(total * 10) / 10 }));
  }, [records]);

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 8 }} role="status" aria-label="Loading milk records"><CircularProgress /></Box>;
  if (isError) return <Box sx={{ p: 4 }}><Alert severity="error">Failed to load data from server.</Alert></Box>;

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom sx={{ color: colors.text }}>
        Milk Collection
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        Today&apos;s total: {Number(totalToday || 0).toFixed(1)} L from{" "}
        {todayRecords.length} entries
      </Typography>

      {/* Daily Summary Chart */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Daily Collection Summary
        </Typography>
        <MilkChartLazy data={dailySummary} />
      </Paper>

      <Paper>
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
          <Table aria-label="Milk collection records">
            <TableHead>
              <TableRow>
                <TableCell>
                  <TableSortLabel active={sortBy === "recorded_at"} direction={sortBy === "recorded_at" ? sortDir : "asc"} onClick={() => handleSort("recorded_at")}>
                    Date
                  </TableSortLabel>
                </TableCell>
                <TableCell>Animal ID</TableCell>
                <TableCell align="right">
                  <TableSortLabel active={sortBy === "quantity_liters"} direction={sortBy === "quantity_liters" ? sortDir : "asc"} onClick={() => handleSort("quantity_liters")}>
                    Quantity (L)
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel active={sortBy === "session"} direction={sortBy === "session" ? sortDir : "asc"} onClick={() => handleSort("session")}>
                    Session
                  </TableSortLabel>
                </TableCell>
                <TableCell>Notes</TableCell>
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
                filtered.map((rec) => (
                    <TableRow key={rec.id}>
                      <TableCell
                        sx={sxCodeCell}
                      >
                        {fmtDate(rec.recorded_at)}
                      </TableCell>
                      <TableCell sx={{ fontSize: '11px', color: colors.textDim }}>{rec.animal_id?.slice(0, 8)}</TableCell>
                      <TableCell
                        align="right"
                        sx={{ ...sxCodeCell, fontWeight: 600, color: colors.text }}
                      >
                        {Number(rec.quantity_liters || 0).toFixed(1)}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={rec.session}
                          size="small"
                          sx={{
                            bgcolor: rec.session === "morning" ? colors.warningLight : colors.infoLight,
                            color: rec.session === "morning" ? colors.accentAmber : colors.accentBlue,
                            border: 'none',
                            fontWeight: 500,
                            fontSize: '11.5px',
                            textTransform: 'capitalize',
                          }}
                        />
                      </TableCell>
                      <TableCell sx={{ fontSize: '12.5px', color: colors.textDim }}>
                        {rec.notes || '\u2014'}
                      </TableCell>
                    </TableRow>
                  ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={dateFrom || dateTo ? filtered.length : serverTotal}
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
