"use client";

import { useState, useMemo } from "react";
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
  Chip,
  Card,
  CardContent,
  Grid,
  Stack,
  LinearProgress,
} from "@mui/material";

/* ---------- stat helpers ---------- */

function coverageColor(pct: number) {
  if (pct >= 85) return "#2E7D32";
  if (pct >= 60) return "#FF8F00";
  return "#D32F2F";
}

function statusBadge(pct: number) {
  if (pct >= 85) return <Chip label="On Track" color="success" size="small" variant="filled" sx={{ fontWeight: 600 }} />;
  if (pct >= 60) return <Chip label="Needs Attention" color="warning" size="small" variant="filled" sx={{ fontWeight: 600 }} />;
  return <Chip label="Behind" color="error" size="small" variant="filled" sx={{ fontWeight: 600 }} />;
}

function urgencyColor(daysUntil: number) {
  if (daysUntil < 0) return "#D32F2F";
  if (daysUntil <= 7) return "#FF8F00";
  return "#2E7D32";
}

/* ---------- mock data ---------- */

interface VillageCoverage {
  code: string;
  name: string;
  totalAnimals: number;
  vaccinated: number;
}

const VILLAGE_DATA: VillageCoverage[] = [
  { code: "KA-571-001", name: "Hoskote", totalAnimals: 320, vaccinated: 296 },
  { code: "KA-571-002", name: "Devanahalli", totalAnimals: 185, vaccinated: 148 },
  { code: "KA-571-003", name: "Doddaballapura", totalAnimals: 240, vaccinated: 226 },
  { code: "KA-571-004", name: "Nelamangala", totalAnimals: 160, vaccinated: 112 },
  { code: "KA-571-005", name: "Ramanagara", totalAnimals: 275, vaccinated: 244 },
];

interface SpeciesVaccine {
  vaccine: string;
  coverage: number;
}

interface SpeciesBreakdown {
  species: string;
  emoji: string;
  vaccines: SpeciesVaccine[];
}

const SPECIES_DATA: SpeciesBreakdown[] = [
  { species: "Cattle", emoji: "\uD83D\uDC04", vaccines: [{ vaccine: "FMD", coverage: 92 }, { vaccine: "Brucella", coverage: 78 }, { vaccine: "HS", coverage: 85 }] },
  { species: "Goats", emoji: "\uD83D\uDC10", vaccines: [{ vaccine: "PPR", coverage: 76 }, { vaccine: "Enterotoxemia", coverage: 65 }] },
  { species: "Sheep", emoji: "\uD83D\uDC11", vaccines: [{ vaccine: "Enterotoxemia", coverage: 70 }, { vaccine: "Sheep Pox", coverage: 82 }] },
  { species: "Poultry", emoji: "\uD83D\uDC14", vaccines: [{ vaccine: "Newcastle", coverage: 88 }, { vaccine: "Marek's", coverage: 75 }] },
];

interface ScheduleEntry {
  animal: string;
  owner: string;
  vaccine: string;
  dueDate: string;
  daysUntilDue: number;
}

const SCHEDULE_DATA: ScheduleEntry[] = [
  { animal: "Sheru (Goat)", owner: "Parvathi Amma", vaccine: "PPR Booster", dueDate: "2026-04-02", daysUntilDue: -6 },
  { animal: "Kamala (Buffalo)", owner: "Shivamma R", vaccine: "HS/BQ", dueDate: "2026-04-05", daysUntilDue: -3 },
  { animal: "Raja (Cattle)", owner: "Krishna Murthy", vaccine: "FMD", dueDate: "2026-04-10", daysUntilDue: 2 },
  { animal: "Lakshmi (Cattle)", owner: "Ramesh Gowda", vaccine: "Brucella", dueDate: "2026-04-12", daysUntilDue: 4 },
  { animal: "Meenu (Goat)", owner: "Manjunath K", vaccine: "Enterotoxemia", dueDate: "2026-04-15", daysUntilDue: 7 },
  { animal: "Sundari (Cattle)", owner: "Suresh Babu", vaccine: "FMD Booster", dueDate: "2026-04-22", daysUntilDue: 14 },
  { animal: "Kokila (Poultry)", owner: "Basavaraju N", vaccine: "Newcastle", dueDate: "2026-04-28", daysUntilDue: 20 },
  { animal: "Bhadra (Cattle)", owner: "Nagaraj P", vaccine: "HS/BQ", dueDate: "2026-05-05", daysUntilDue: 27 },
];

/* ---------- component ---------- */

export default function VaccinationsPage() {
  const totalAnimals = VILLAGE_DATA.reduce((s, v) => s + v.totalAnimals, 0);
  const totalVaccinated = VILLAGE_DATA.reduce((s, v) => s + v.vaccinated, 0);
  const overallCoverage = Math.round((totalVaccinated / totalAnimals) * 100);
  const overdueCount = SCHEDULE_DATA.filter((s) => s.daysUntilDue < 0).length;
  const thisMonthCount = SCHEDULE_DATA.filter((s) => s.daysUntilDue >= 0 && s.daysUntilDue <= 30).length;

  const sortedSchedule = useMemo(
    () => [...SCHEDULE_DATA].sort((a, b) => a.daysUntilDue - b.daysUntilDue),
    []
  );

  return (
    <Box p={3}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Vaccination Coverage
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        District-wide vaccination tracking for Karnataka livestock
      </Typography>

      {/* ---- Stat cards ---- */}
      <Grid container spacing={2} mb={4}>
        <Grid item xs={12} sm={4}>
          <Paper sx={{ p: 3, borderRadius: 2, textAlign: "center" }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Overall Coverage
            </Typography>
            <Typography variant="h3" fontWeight={700} color={coverageColor(overallCoverage)}>
              {overallCoverage}%
            </Typography>
            <LinearProgress
              variant="determinate"
              value={overallCoverage}
              sx={{ mt: 1, height: 8, borderRadius: 4, bgcolor: "#E0E0E0", "& .MuiLinearProgress-bar": { bgcolor: coverageColor(overallCoverage) } }}
            />
          </Paper>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Paper sx={{ p: 3, borderRadius: 2, textAlign: "center" }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Overdue Vaccinations
            </Typography>
            <Typography variant="h3" fontWeight={700} color="#D32F2F">
              {"\u26A0\uFE0F"} {overdueCount}
            </Typography>
            <Typography variant="body2" color="text.secondary" mt={1}>
              require immediate attention
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Paper sx={{ p: 3, borderRadius: 2, textAlign: "center" }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Vaccinations This Month
            </Typography>
            <Typography variant="h3" fontWeight={700} color="#1565C0">
              {"\uD83D\uDCC8"} {thisMonthCount}
            </Typography>
            <Typography variant="body2" color="text.secondary" mt={1}>
              scheduled ahead
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* ---- Village coverage table ---- */}
      <Typography variant="h6" fontWeight={700} mb={2}>
        Village-Level Coverage
      </Typography>
      <Paper sx={{ borderRadius: 2, mb: 4 }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 700 }}>Village Code</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Village Name</TableCell>
                <TableCell sx={{ fontWeight: 700 }} align="right">Total Animals</TableCell>
                <TableCell sx={{ fontWeight: 700 }} align="right">Vaccinated</TableCell>
                <TableCell sx={{ fontWeight: 700 }} align="right">Coverage %</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {VILLAGE_DATA.map((v) => {
                const pct = Math.round((v.vaccinated / v.totalAnimals) * 100);
                return (
                  <TableRow key={v.code} hover>
                    <TableCell sx={{ fontFamily: "monospace" }}>{v.code}</TableCell>
                    <TableCell>{v.name}</TableCell>
                    <TableCell align="right">{v.totalAnimals}</TableCell>
                    <TableCell align="right">{v.vaccinated}</TableCell>
                    <TableCell align="right">
                      <Typography fontWeight={600} color={coverageColor(pct)}>
                        {pct}%
                      </Typography>
                    </TableCell>
                    <TableCell>{statusBadge(pct)}</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* ---- Species breakdown ---- */}
      <Typography variant="h6" fontWeight={700} mb={2}>
        Species Breakdown
      </Typography>
      <Grid container spacing={2} mb={4}>
        {SPECIES_DATA.map((sp) => (
          <Grid item xs={12} sm={6} md={3} key={sp.species}>
            <Card sx={{ borderRadius: 2, height: "100%" }}>
              <CardContent>
                <Typography variant="h6" fontWeight={700} gutterBottom>
                  {sp.emoji} {sp.species}
                </Typography>
                <Stack spacing={1.5}>
                  {sp.vaccines.map((vac) => (
                    <Box key={vac.vaccine}>
                      <Box display="flex" justifyContent="space-between" mb={0.5}>
                        <Typography variant="body2">{vac.vaccine}</Typography>
                        <Typography variant="body2" fontWeight={600} color={coverageColor(vac.coverage)}>
                          {vac.coverage}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={vac.coverage}
                        sx={{ height: 6, borderRadius: 3, bgcolor: "#E0E0E0", "& .MuiLinearProgress-bar": { bgcolor: coverageColor(vac.coverage) } }}
                      />
                    </Box>
                  ))}
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* ---- Upcoming schedule ---- */}
      <Typography variant="h6" fontWeight={700} mb={2}>
        Upcoming Schedule
      </Typography>
      <Paper sx={{ borderRadius: 2 }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 700 }}>Animal</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Owner</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Vaccine</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Due Date</TableCell>
                <TableCell sx={{ fontWeight: 700 }} align="right">Days Until Due</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sortedSchedule.map((entry, idx) => (
                <TableRow key={idx} hover>
                  <TableCell>{entry.animal}</TableCell>
                  <TableCell>{entry.owner}</TableCell>
                  <TableCell>{entry.vaccine}</TableCell>
                  <TableCell sx={{ whiteSpace: "nowrap" }}>
                    {new Date(entry.dueDate).toLocaleDateString("en-IN")}
                  </TableCell>
                  <TableCell align="right">
                    <Chip
                      label={entry.daysUntilDue < 0 ? `${Math.abs(entry.daysUntilDue)}d overdue` : entry.daysUntilDue === 0 ? "Today" : `${entry.daysUntilDue}d`}
                      size="small"
                      variant="filled"
                      sx={{
                        fontWeight: 600,
                        color: "#FFFFFF",
                        bgcolor: urgencyColor(entry.daysUntilDue),
                      }}
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
