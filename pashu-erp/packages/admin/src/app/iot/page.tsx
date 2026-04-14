"use client";

import { useState, useMemo, useEffect } from "react";
import { useList } from "@refinedev/core";
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Alert,
  LinearProgress,
  TextField,
  InputAdornment,
  CircularProgress,
} from "@mui/material";
import WifiIcon from "@mui/icons-material/Wifi";
import WifiOffIcon from "@mui/icons-material/WifiOff";
import SearchIcon from "@mui/icons-material/Search";
import { colors, sxCodeCell } from "@/theme/theme";
import EmptyState from "@/components/EmptyState";

/* ---------- Types matching the real API response ---------- */

interface DeviceTypeSummary {
  name: string;
  total: number;
  online: number;
  offline: number;
}

interface TelemetryMetric {
  type: string;
  value: number | { lat: number; lng: number };
  unit: string;
}

interface TelemetryReading {
  device_id: string;
  animal_id: string;
  timestamp: string;
  metrics: TelemetryMetric[];
  battery_pct: number;
  rssi: number;
}

/* ---------- Helpers ---------- */

const TYPE_COLORS: Record<string, string> = {
  smart_collar: "#43a047",
  ear_tag_sensor: "#1e88e5",
  bolus_sensor: "#e53935",
  milk_meter: "#fb8c00",
  weather_station: "#8e24aa",
};

const TYPE_LABELS: Record<string, string> = {
  smart_collar: "Smart Collars",
  ear_tag_sensor: "Ear Tag Sensors",
  bolus_sensor: "Bolus Sensors",
  milk_meter: "Milk Meters",
  pedometer: "Pedometers",
  weather_station: "Weather Stations",
};

function formatMetrics(metrics: TelemetryMetric[]): string {
  return metrics
    .filter((m) => m.type !== "gps")
    .map((m) => `${m.value} ${m.unit}`)
    .join("  ·  ");
}

function formatTimestamp(iso: string): string {
  try {
    return new Date(iso).toLocaleString("en-IN", {
      day: "numeric",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

/* ---------- Page ---------- */

export default function IotPage() {
  useEffect(() => {
    document.title = "IoT Devices — PashuRaksha ERP";
  }, []);

  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const {
    data: deviceData,
    isLoading: devLoading,
    isError: devError,
  } = useList<DeviceTypeSummary>({ resource: "iot/device-types" });

  const {
    data: readingsData,
    isLoading: readLoading,
    isError: readError,
  } = useList<TelemetryReading>({ resource: "iot/readings" });

  const isLoading = devLoading || readLoading;

  const deviceTypes = deviceData?.data ?? [];
  const rawReadings = readingsData?.data ?? [];

  const totalDevices = deviceTypes.reduce((s, d) => s + d.total, 0);
  const totalOnline = deviceTypes.reduce((s, d) => s + d.online, 0);

  const filteredReadings = useMemo(
    () =>
      rawReadings.filter(
        (r) =>
          r.device_id?.toLowerCase().includes(search.toLowerCase()) ||
          r.animal_id?.toLowerCase().includes(search.toLowerCase())
      ),
    [rawReadings, search]
  );

  if (isLoading)
    return (
      <Box sx={{ display: "flex", justifyContent: "center", p: 8 }}>
        <CircularProgress />
      </Box>
    );

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom sx={{ color: colors.text }}>
        IoT Device Monitoring
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={2}>
        {totalOnline}/{totalDevices} devices online across all centers
      </Typography>

      {/* Phase 2 Banner */}
      <Alert
        severity="info"
        sx={{
          mb: 3,
          fontSize: "13px",
          fontWeight: 600,
          backgroundColor: colors.primaryLight,
          color: colors.primary,
          border: `1px solid ${colors.primary}30`,
          "& .MuiAlert-icon": { color: colors.primary },
        }}
      >
        Phase 2 -- Coming Soon: Full IoT integration with real-time device
        management, OTA firmware updates, and predictive maintenance alerts.
      </Alert>

      {devError ? (
        <Alert severity="error" sx={{ mb: 3 }}>
          Failed to load device summary from IoT gateway.
        </Alert>
      ) : deviceTypes.length === 0 ? (
        <Typography color="text.secondary" sx={{ p: 4, textAlign: "center" }}>
          No device data available. Ensure the IoT gateway is running.
        </Typography>
      ) : (
        <Grid container spacing={2.5} mb={4}>
          {deviceTypes.map((device) => {
            const pct =
              device.total > 0
                ? Math.round((device.online / device.total) * 100)
                : 0;
            const color = TYPE_COLORS[device.name] || colors.primary;
            return (
              <Grid item xs={12} sm={6} md={3} key={device.name}>
                <Card sx={{ borderLeft: `3px solid ${color}`, height: "100%" }}>
                  <CardContent sx={{ p: 2.5 }}>
                    <Box
                      display="flex"
                      justifyContent="space-between"
                      alignItems="flex-start"
                      mb={2}
                    >
                      <Chip
                        label={`${pct}%`}
                        size="small"
                        sx={{
                          bgcolor: colors.successLight,
                          color: colors.accentGreen,
                          fontWeight: 600,
                          border: "none",
                        }}
                      />
                    </Box>
                    <Typography
                      sx={{
                        fontSize: "14px",
                        fontWeight: 600,
                        color: colors.text,
                      }}
                    >
                      {TYPE_LABELS[device.name] || device.name}
                    </Typography>
                    <Typography
                      sx={{ fontSize: "12px", color: colors.textDim, mb: 1 }}
                    >
                      {device.total} devices total
                    </Typography>
                    <Box display="flex" gap={1} mb={1}>
                      <Chip
                        icon={
                          <WifiIcon sx={{ fontSize: "13px !important" }} />
                        }
                        label={`${device.online} online`}
                        size="small"
                        sx={{
                          bgcolor: colors.successLight,
                          color: colors.accentGreen,
                          border: "none",
                          fontSize: "11px",
                          "& .MuiChip-icon": { color: colors.accentGreen },
                        }}
                      />
                      <Chip
                        icon={
                          <WifiOffIcon sx={{ fontSize: "13px !important" }} />
                        }
                        label={`${device.offline} offline`}
                        size="small"
                        sx={{
                          bgcolor: colors.errorLight,
                          color: colors.accentRed,
                          border: "none",
                          fontSize: "11px",
                          "& .MuiChip-icon": { color: colors.accentRed },
                        }}
                      />
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={pct}
                      sx={{
                        mt: 1,
                        height: 6,
                        borderRadius: 3,
                        bgcolor: "rgba(0,0,0,0.06)",
                        "& .MuiLinearProgress-bar": {
                          bgcolor: color,
                          borderRadius: 3,
                        },
                      }}
                    />
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}

      {/* Telemetry Readings Table */}
      <Paper>
        <Box
          p={2}
          display="flex"
          justifyContent="space-between"
          alignItems="center"
        >
          <Typography
            sx={{ fontSize: "14px", fontWeight: 600, color: colors.text }}
          >
            Recent Telemetry Readings
          </Typography>
          <TextField
            size="small"
            placeholder="Search by device or animal ID..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(0);
            }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ color: colors.textLight }} />
                </InputAdornment>
              ),
            }}
            sx={{ minWidth: 300 }}
          />
        </Box>
        {readError ? (
          <Alert severity="error" sx={{ mx: 2, mb: 2 }}>
            Failed to load telemetry from IoT gateway.
          </Alert>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Device ID</TableCell>
                  <TableCell>Animal ID</TableCell>
                  <TableCell>Metrics</TableCell>
                  <TableCell align="center">Battery</TableCell>
                  <TableCell align="center">RSSI</TableCell>
                  <TableCell>Timestamp</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredReadings.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} sx={{ border: 0 }}>
                      <EmptyState />
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredReadings
                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                    .map((row, idx) => (
                      <TableRow key={`${row.device_id}-${idx}`}>
                        <TableCell sx={sxCodeCell}>{row.device_id}</TableCell>
                        <TableCell
                          sx={{ fontSize: "11px", color: colors.textDim }}
                        >
                          {row.animal_id}
                        </TableCell>
                        <TableCell
                          sx={{ fontSize: "12px", color: colors.textDim }}
                        >
                          {formatMetrics(row.metrics ?? [])}
                        </TableCell>
                        <TableCell align="center">
                          <Chip
                            label={`${row.battery_pct}%`}
                            size="small"
                            sx={{
                              fontWeight: 600,
                              fontSize: "11.5px",
                              bgcolor:
                                row.battery_pct > 50
                                  ? colors.successLight
                                  : row.battery_pct > 20
                                    ? "#fff3e0"
                                    : colors.errorLight,
                              color:
                                row.battery_pct > 50
                                  ? colors.accentGreen
                                  : row.battery_pct > 20
                                    ? "#e65100"
                                    : colors.accentRed,
                              border: "none",
                            }}
                          />
                        </TableCell>
                        <TableCell
                          align="center"
                          sx={{ ...sxCodeCell, fontSize: "11px" }}
                        >
                          {row.rssi} dBm
                        </TableCell>
                        <TableCell
                          sx={{ ...sxCodeCell, whiteSpace: "nowrap" }}
                        >
                          {formatTimestamp(row.timestamp)}
                        </TableCell>
                      </TableRow>
                    ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
        <TablePagination
          component="div"
          count={filteredReadings.length}
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
