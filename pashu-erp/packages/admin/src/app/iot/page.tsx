"use client";

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
  Alert,
  LinearProgress,
} from "@mui/material";
import NfcIcon from "@mui/icons-material/Nfc";
import ScienceIcon from "@mui/icons-material/Science";
import GpsFixedIcon from "@mui/icons-material/GpsFixed";
import RestaurantIcon from "@mui/icons-material/Restaurant";
import WifiIcon from "@mui/icons-material/Wifi";
import WifiOffIcon from "@mui/icons-material/WifiOff";

interface DeviceType {
  name: string;
  icon: React.ReactNode;
  total: number;
  online: number;
  offline: number;
  lastSync: string;
  color: string;
}

const deviceTypes: DeviceType[] = [
  {
    name: "RFID Scanner",
    icon: <NfcIcon sx={{ fontSize: 40 }} />,
    total: 45,
    online: 42,
    offline: 3,
    lastSync: "2 min ago",
    color: "#1565c0",
  },
  {
    name: "Milk Quality Meter",
    icon: <ScienceIcon sx={{ fontSize: 40 }} />,
    total: 28,
    online: 25,
    offline: 3,
    lastSync: "5 min ago",
    color: "#2e7d32",
  },
  {
    name: "GPS Collar",
    icon: <GpsFixedIcon sx={{ fontSize: 40 }} />,
    total: 120,
    online: 108,
    offline: 12,
    lastSync: "1 min ago",
    color: "#f57c00",
  },
  {
    name: "Smart Feeder",
    icon: <RestaurantIcon sx={{ fontSize: 40 }} />,
    total: 15,
    online: 12,
    offline: 3,
    lastSync: "8 min ago",
    color: "#6a1b9a",
  },
];

const mockSensorReadings = [
  { id: "IOT-001", device: "RFID-MYS-042", type: "RFID Scanner", location: "Hullahalli MC", reading: "Tag: PA-KA-MYS-00001", timestamp: "2026-04-08 09:45:12", status: "online" },
  { id: "IOT-002", device: "MQM-MYS-018", type: "Milk Quality Meter", location: "T. Narasipura MC", reading: "Fat: 4.2%, SNF: 8.6%", timestamp: "2026-04-08 09:42:30", status: "online" },
  { id: "IOT-003", device: "GPS-COL-089", type: "GPS Collar", location: "12.312N, 76.612E", reading: "Temp: 38.6C, Steps: 2400", timestamp: "2026-04-08 09:44:55", status: "online" },
  { id: "IOT-004", device: "SF-MDY-007", type: "Smart Feeder", location: "Pandavapura Farm", reading: "Dispensed: 2.5 kg, Level: 68%", timestamp: "2026-04-08 09:40:00", status: "online" },
  { id: "IOT-005", device: "RFID-HSN-015", type: "RFID Scanner", location: "Arsikere MC", reading: "Tag: PA-KA-HSN-00010", timestamp: "2026-04-08 09:38:45", status: "online" },
  { id: "IOT-006", device: "GPS-COL-034", type: "GPS Collar", location: "12.485N, 75.823E", reading: "Temp: 39.1C, Steps: 890", timestamp: "2026-04-08 08:22:10", status: "offline" },
  { id: "IOT-007", device: "MQM-CHN-009", type: "Milk Quality Meter", location: "Kollegal MC", reading: "Fat: 3.8%, SNF: 8.2%", timestamp: "2026-04-08 09:35:20", status: "online" },
  { id: "IOT-008", device: "SF-KDG-003", type: "Smart Feeder", location: "Virajpet Farm", reading: "Dispensed: 3.0 kg, Level: 45%", timestamp: "2026-04-08 07:15:00", status: "offline" },
];

export default function IotPage() {
  const totalDevices = deviceTypes.reduce((s, d) => s + d.total, 0);
  const totalOnline = deviceTypes.reduce((s, d) => s + d.online, 0);

  return (
    <Box p={3}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        IoT Device Monitoring
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={2}>
        {totalOnline}/{totalDevices} devices online across all centers
      </Typography>

      {/* Phase 2 Banner */}
      <Alert
        severity="info"
        variant="filled"
        sx={{
          mb: 3,
          fontSize: 16,
          fontWeight: 600,
          backgroundColor: "#1565c0",
        }}
      >
        Phase 2 — Coming Soon: Full IoT integration with real-time device management,
        OTA firmware updates, and predictive maintenance alerts.
      </Alert>

      {/* Device Type Cards */}
      <Grid container spacing={3} mb={4}>
        {deviceTypes.map((device) => (
          <Grid item xs={12} sm={6} md={3} key={device.name}>
            <Card
              sx={{
                borderTop: `4px solid ${device.color}`,
                height: "100%",
                transition: "box-shadow 0.2s",
                "&:hover": { boxShadow: 4 },
              }}
            >
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Box sx={{ color: device.color }}>{device.icon}</Box>
                  <Chip
                    label={`${Math.round((device.online / device.total) * 100)}%`}
                    size="small"
                    color="success"
                  />
                </Box>
                <Typography variant="h6" fontWeight={600}>
                  {device.name}
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={1}>
                  {device.total} devices total
                </Typography>
                <Box display="flex" gap={1} mb={1}>
                  <Chip
                    icon={<WifiIcon sx={{ fontSize: 14 }} />}
                    label={`${device.online} online`}
                    size="small"
                    color="success"
                    variant="outlined"
                  />
                  <Chip
                    icon={<WifiOffIcon sx={{ fontSize: 14 }} />}
                    label={`${device.offline} offline`}
                    size="small"
                    color="error"
                    variant="outlined"
                  />
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={(device.online / device.total) * 100}
                  sx={{ borderRadius: 2, height: 6, mt: 1 }}
                />
                <Typography variant="caption" color="text.secondary" mt={0.5} display="block">
                  Last sync: {device.lastSync}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Mock Sensor Readings Table */}
      <Paper sx={{ borderRadius: 2 }}>
        <Box p={2}>
          <Typography variant="h6" fontWeight={600}>
            Recent Sensor Readings
          </Typography>
        </Box>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 700 }}>Device ID</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Type</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Location</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Reading</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Timestamp</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mockSensorReadings.map((row) => (
                <TableRow key={row.id} hover>
                  <TableCell sx={{ fontFamily: "monospace", fontSize: 13 }}>
                    {row.device}
                  </TableCell>
                  <TableCell>
                    <Chip label={row.type} size="small" variant="outlined" />
                  </TableCell>
                  <TableCell>{row.location}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{row.reading}</TableCell>
                  <TableCell sx={{ whiteSpace: "nowrap", fontSize: 13 }}>
                    {row.timestamp}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={row.status}
                      size="small"
                      color={row.status === "online" ? "success" : "error"}
                      variant="filled"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}
