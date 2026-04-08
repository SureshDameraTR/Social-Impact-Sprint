"use client";

import { Box, Grid, Typography, Paper, Card, CardContent } from "@mui/material";
import PeopleIcon from "@mui/icons-material/People";
import PetsIcon from "@mui/icons-material/Pets";
import LocalDrinkIcon from "@mui/icons-material/LocalDrink";
import WarningIcon from "@mui/icons-material/Warning";
import StoreIcon from "@mui/icons-material/Store";
import StorefrontIcon from "@mui/icons-material/Storefront";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import StatCard from "@/components/StatCard";
import GISMap, { MapPoint } from "@/components/GISMap";

// Mock milk collection data (30 days)
const milkData = Array.from({ length: 30 }, (_, i) => {
  const date = new Date();
  date.setDate(date.getDate() - (29 - i));
  return {
    date: `${date.getDate()}/${date.getMonth() + 1}`,
    morning: Math.round(800 + Math.random() * 400),
    evening: Math.round(600 + Math.random() * 300),
  };
});

// Mock disease alert map points
const alertPoints: MapPoint[] = [
  { id: "a1", lat: 12.3, lng: 76.6, label: "FMD Outbreak", details: "5 animals affected", severity: "critical", type: "alert" },
  { id: "a2", lat: 12.9, lng: 77.5, label: "Mastitis Cluster", details: "3 farms", severity: "high", type: "alert" },
  { id: "a3", lat: 13.0, lng: 76.1, label: "Tick Fever", details: "2 animals", severity: "medium", type: "alert" },
  { id: "a4", lat: 12.5, lng: 75.8, label: "Bloat Cases", details: "1 farm", severity: "medium", type: "alert" },
  { id: "a5", lat: 14.5, lng: 75.4, label: "PPR Suspected", details: "Goats affected", severity: "critical", type: "alert" },
  { id: "a6", lat: 15.3, lng: 76.5, label: "Lumpy Skin", details: "4 cattle", severity: "high", type: "alert" },
  { id: "a7", lat: 13.6, lng: 75.1, label: "Brucellosis", details: "Testing pending", severity: "medium", type: "alert" },
];

export default function DashboardPage() {
  return (
    <Box p={3}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        PashuRaksha ERP overview for Mysuru District
      </Typography>

      {/* Stat Cards - 3x2 grid */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<PeopleIcon sx={{ fontSize: 32, color: "#1565c0" }} />}
            title="Total Farmers"
            value="2,847"
            color="#1565c0"
            trend={{ value: 12, label: "this month" }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<PetsIcon sx={{ fontSize: 32, color: "#2e7d32" }} />}
            title="Registered Animals"
            value="8,432"
            color="#2e7d32"
            trend={{ value: 8, label: "this month" }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<LocalDrinkIcon sx={{ fontSize: 32, color: "#00695c" }} />}
            title="Today's Milk Collection"
            value="12,540 L"
            color="#00695c"
            trend={{ value: 5, label: "vs yesterday" }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<WarningIcon sx={{ fontSize: 32, color: "#c62828" }} />}
            title="Active Health Alerts"
            value="23"
            color="#c62828"
            trend={{ value: -15, label: "this week" }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<StoreIcon sx={{ fontSize: 32, color: "#6a1b9a" }} />}
            title="Marketplace Revenue"
            value="\u20B94.2L"
            color="#6a1b9a"
            trend={{ value: 22, label: "this month" }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<StorefrontIcon sx={{ fontSize: 32, color: "#e65100" }} />}
            title="Active Sellers"
            value="186"
            color="#e65100"
            trend={{ value: 9, label: "this month" }}
          />
        </Grid>
      </Grid>

      {/* Charts and Map Row */}
      <Grid container spacing={3}>
        {/* Milk Collection Chart */}
        <Grid item xs={12} lg={7}>
          <Paper sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Milk Collection (Last 30 Days)
            </Typography>
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={milkData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="morning"
                  stroke="#00695c"
                  strokeWidth={2}
                  name="Morning (L)"
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="evening"
                  stroke="#0288d1"
                  strokeWidth={2}
                  name="Evening (L)"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Disease Alert Map */}
        <Grid item xs={12} lg={5}>
          <Paper sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Disease Alert Map
            </Typography>
            <GISMap
              center={[12.3, 76.6]}
              zoom={7}
              points={alertPoints}
              height={320}
            />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
