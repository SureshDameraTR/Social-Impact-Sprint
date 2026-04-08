"use client";

import { Box, Typography, Paper } from "@mui/material";
import GISMap, { MapPoint } from "@/components/GISMap";

const allPoints: MapPoint[] = [
  // Disease Alerts
  { id: "a1", lat: 12.3, lng: 76.6, label: "FMD Outbreak", details: "5 animals affected, Mysuru", severity: "critical", type: "alert" },
  { id: "a2", lat: 12.9, lng: 77.5, label: "Mastitis Cluster", details: "3 farms, Bangalore Rural", severity: "high", type: "alert" },
  { id: "a3", lat: 13.0, lng: 76.1, label: "Tick Fever", details: "2 animals, Hassan", severity: "medium", type: "alert" },
  { id: "a4", lat: 14.5, lng: 75.4, label: "PPR Suspected", details: "Goats, Dharwad", severity: "critical", type: "alert" },
  { id: "a5", lat: 15.3, lng: 76.5, label: "Lumpy Skin Disease", details: "4 cattle, Bellary", severity: "high", type: "alert" },
  { id: "a6", lat: 12.5, lng: 75.8, label: "Bloat Cases", details: "1 farm, Kodagu", severity: "medium", type: "alert" },
  { id: "a7", lat: 13.6, lng: 75.1, label: "Brucellosis", details: "Testing pending, Shimoga", severity: "medium", type: "alert" },

  // Milk Centers
  { id: "c1", lat: 12.31, lng: 76.62, label: "Hullahalli MC", details: "Capacity: 500L/day, Active", type: "center" },
  { id: "c2", lat: 12.22, lng: 77.0, label: "T. Narasipura MC", details: "Capacity: 800L/day, Active", type: "center" },
  { id: "c3", lat: 12.58, lng: 76.68, label: "Nanjangud MC", details: "Capacity: 600L/day, Active", type: "center" },
  { id: "c4", lat: 12.26, lng: 76.1, label: "Hunsur MC", details: "Capacity: 450L/day, Active", type: "center" },
  { id: "c5", lat: 12.2, lng: 75.8, label: "Virajpet MC", details: "Capacity: 350L/day, Active", type: "center" },
  { id: "c6", lat: 12.73, lng: 76.95, label: "Mandya MC", details: "Capacity: 1000L/day, Active", type: "center" },
  { id: "c7", lat: 12.65, lng: 76.9, label: "Pandavapura MC", details: "Capacity: 550L/day, Active", type: "center" },
  { id: "c8", lat: 12.08, lng: 77.0, label: "Kollegal MC", details: "Capacity: 400L/day, Active", type: "center" },

  // Farmer Locations
  { id: "f1", lat: 12.32, lng: 76.58, label: "Ramesh Gowda", details: "8 animals, Hullahalli", type: "farmer" },
  { id: "f2", lat: 12.21, lng: 77.02, label: "Lakshmi Devi", details: "5 animals, T. Narasipura", type: "farmer" },
  { id: "f3", lat: 12.72, lng: 76.93, label: "Manjunath K", details: "12 animals, Nagamangala", type: "farmer" },
  { id: "f4", lat: 12.98, lng: 76.08, label: "Savitri Bai", details: "3 animals, Channarayapatna", type: "farmer" },
  { id: "f5", lat: 12.64, lng: 76.88, label: "Krishna Murthy", details: "7 animals, Pandavapura", type: "farmer" },
  { id: "f6", lat: 11.78, lng: 76.68, label: "Parvathi Amma", details: "4 animals, Gundlupet", type: "farmer" },
  { id: "f7", lat: 12.19, lng: 75.81, label: "Suresh Babu", details: "15 animals, Virajpet", type: "farmer" },
  { id: "f8", lat: 12.12, lng: 76.68, label: "Meenakshi H", details: "6 animals, Nanjangud", type: "farmer" },
  { id: "f9", lat: 13.31, lng: 76.28, label: "Basavaraju N", details: "9 animals, Arsikere", type: "farmer" },
  { id: "f10", lat: 12.42, lng: 76.71, label: "Geetha Kumari", details: "2 animals, Srirangapatna", type: "farmer" },
];

export default function MapPage() {
  return (
    <Box p={3}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Map View
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={2}>
        Karnataka livestock monitoring — toggle layers using the control on the top right
      </Typography>

      <Paper sx={{ borderRadius: 2, overflow: "hidden" }}>
        <GISMap
          center={[13.0, 76.5]}
          zoom={7}
          points={allPoints}
          height="calc(100vh - 220px)"
          showLayers
        />
      </Paper>

      {/* Legend */}
      <Paper sx={{ p: 2, mt: 2, borderRadius: 2 }}>
        <Typography variant="subtitle2" fontWeight={600} mb={1}>
          Legend
        </Typography>
        <Box display="flex" gap={3} flexWrap="wrap">
          {[
            { color: "#d32f2f", label: "Critical Alert" },
            { color: "#f57c00", label: "High Alert" },
            { color: "#fbc02d", label: "Medium Alert" },
            { color: "#0288d1", label: "Milk Center" },
            { color: "#388e3c", label: "Farmer Location" },
          ].map((item) => (
            <Box key={item.label} display="flex" alignItems="center" gap={1}>
              <Box
                sx={{
                  width: 14,
                  height: 14,
                  borderRadius: "50%",
                  backgroundColor: item.color,
                }}
              />
              <Typography variant="body2">{item.label}</Typography>
            </Box>
          ))}
        </Box>
      </Paper>
    </Box>
  );
}
