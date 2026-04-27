"use client";

import { useMemo } from "react";
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
  Chip,
  Card,
  CardContent,
  Grid,
  Stack,
  LinearProgress,
  CircularProgress,
  Alert,
} from "@mui/material";
import { colors, sxCodeCell, sxNameCell } from "@/theme/theme";
import { fmtDate } from "@/utils/format";

/* ---------- stat helpers ---------- */

function coverageColor(pct: number) {
  if (pct >= 85) return colors.accentGreen;
  if (pct >= 60) return colors.accentAmber;
  return colors.accentRed;
}

function statusBadge(pct: number) {
  if (pct >= 85)
    return (
      <Chip
        label="On Track"
        size="small"
        sx={{ fontWeight: 600, bgcolor: colors.successLight, color: colors.accentGreen, border: 'none' }}
      />
    );
  if (pct >= 60)
    return (
      <Chip
        label="Needs Attention"
        size="small"
        sx={{ fontWeight: 600, bgcolor: colors.warningLight, color: colors.accentAmber, border: 'none' }}
      />
    );
  return (
    <Chip
      label="Behind"
      size="small"
      sx={{ fontWeight: 600, bgcolor: colors.errorLight, color: colors.accentRed, border: 'none' }}
    />
  );
}

function urgencyColor(daysUntil: number) {
  if (daysUntil < 0) return colors.accentRed;
  if (daysUntil <= 7) return colors.accentAmber;
  return colors.accentGreen;
}

/* ---------- interfaces ---------- */

/** Raw shape from GET /vaccinations/village-coverage */
interface VillageCoverageRaw {
  village_code?: string;
  code?: string;
  name?: string;
  total_animals?: number;
  totalAnimals?: number;
  coverage_pct?: number;
  vaccinated?: number;
}

/** Raw shape from GET /vaccinations/species-breakdown */
interface SpeciesBreakdownRaw {
  species: string;
  animal_count: number;
  vaccination_count: number;
}

/** Raw shape from GET /vaccinations/schedule */
interface ScheduleEntryRaw {
  species?: string;
  animal?: string;
  owner?: string;
  vaccine?: string;
  vaccine_name?: string;
  due_date?: string;
  dueDate?: string;
  days_until_due?: number;
  daysUntilDue?: number;
}

interface VillageCoverage {
  code: string;
  name: string;
  totalAnimals: number;
  vaccinated: number;
}

interface SpeciesVaccine {
  vaccine: string;
  coverage: number;
}

interface SpeciesBreakdown {
  species: string;
  emoji: string;
  vaccines: SpeciesVaccine[];
}

interface ScheduleEntry {
  animal: string;
  owner: string;
  vaccine: string;
  dueDate: string;
  daysUntilDue: number;
}

/* ---------- component ---------- */

export default function VaccinationsPage() {
  const { data: villageRaw, isLoading: vLoading, isError: vError } = useList<VillageCoverageRaw>({ resource: "vaccinations/village-coverage" });
  const { data: speciesRaw, isLoading: sLoading, isError: sError } = useList<SpeciesBreakdownRaw>({ resource: "vaccinations/species-breakdown" });
  const { data: scheduleRaw, isLoading: schLoading, isError: schError } = useList<ScheduleEntryRaw>({ resource: "vaccinations/schedule" });

  const isLoading = vLoading || sLoading || schLoading;
  const isError = vError || sError || schError;

  // Map API response shapes to expected UI shapes
  const villages: VillageCoverage[] = useMemo(() =>
    (villageRaw?.data ?? []).map((v: VillageCoverageRaw) => ({
      code: v.village_code ?? v.code ?? "",
      name: v.village_code ?? v.name ?? "",
      totalAnimals: v.total_animals ?? v.totalAnimals ?? 0,
      vaccinated: typeof v.coverage_pct === "number"
        ? Math.round((v.coverage_pct / 100) * (v.total_animals ?? 0))
        : (v.vaccinated ?? 0),
    })),
    [villageRaw],
  );

  const speciesList: SpeciesBreakdown[] = useMemo(() =>
    (speciesRaw?.data ?? []).map((s: SpeciesBreakdownRaw) => ({
      species: s.species ?? "",
      emoji: s.species === "Cattle" || s.species === "cattle" ? "\uD83D\uDC04"
        : s.species === "Goat" || s.species === "goat" ? "\uD83D\uDC10"
        : s.species === "Sheep" || s.species === "sheep" ? "\uD83D\uDC11"
        : "\uD83D\uDC14",
      vaccines: [{
        vaccine: "All",
        coverage: s.animal_count > 0 ? Math.round((s.vaccination_count / s.animal_count) * 100) : 0,
      }],
    })),
    [speciesRaw],
  );

  const scheduleList: ScheduleEntry[] = useMemo(() =>
    (scheduleRaw?.data ?? []).map((s: ScheduleEntryRaw) => ({
      animal: s.species ?? s.animal ?? "",
      owner: s.species ?? s.owner ?? "",
      vaccine: s.vaccine ?? s.vaccine_name ?? "",
      dueDate: s.due_date ?? s.dueDate ?? "",
      daysUntilDue: s.days_until_due ?? s.daysUntilDue ?? 0,
    })),
    [scheduleRaw],
  );

  const { totalAnimals, totalVaccinated, overallCoverage, overdueCount, thisMonthCount } = useMemo(() => {
    const ta = villages.reduce((s, v) => s + v.totalAnimals, 0);
    const tv = villages.reduce((s, v) => s + v.vaccinated, 0);
    return {
      totalAnimals: ta,
      totalVaccinated: tv,
      overallCoverage: ta > 0 ? Math.round((tv / ta) * 100) : 0,
      overdueCount: scheduleList.filter((s) => s.daysUntilDue < 0).length,
      thisMonthCount: scheduleList.filter((s) => s.daysUntilDue >= 0 && s.daysUntilDue <= 30).length,
    };
  }, [villages, scheduleList]);

  const sortedSchedule = useMemo(
    () => [...scheduleList].sort((a, b) => a.daysUntilDue - b.daysUntilDue),
    [scheduleList]
  );

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 8 }} role="status" aria-label="Loading vaccination data"><CircularProgress /></Box>;
  if (isError) return <Box sx={{ p: 4 }}><Alert severity="error">Failed to load data from server.</Alert></Box>;

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom sx={{ color: colors.text }}>
        Vaccination Coverage
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        District-wide vaccination tracking for Karnataka livestock
      </Typography>

      {/* ---- Stat cards ---- */}
      <Grid container spacing={2.5} mb={4}>
        <Grid item xs={12} sm={4}>
          <Card sx={{ borderLeft: `3px solid ${coverageColor(overallCoverage)}` }}>
            <CardContent sx={{ textAlign: "center", py: 3 }}>
              <Typography sx={{ fontSize: '12px', color: colors.textDim, mb: 1 }}>
                Overall Coverage
              </Typography>
              <Typography
                sx={{ fontSize: '36px', fontWeight: 700, color: coverageColor(overallCoverage), lineHeight: 1 }}
              >
                {overallCoverage}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={overallCoverage}
                sx={{
                  mt: 1.5,
                  height: 8,
                  borderRadius: 4,
                  bgcolor: 'rgba(0,0,0,0.06)',
                  '& .MuiLinearProgress-bar': { bgcolor: coverageColor(overallCoverage), borderRadius: 4 },
                }}
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card sx={{ borderLeft: `3px solid ${colors.accentRed}` }}>
            <CardContent sx={{ textAlign: "center", py: 3 }}>
              <Typography sx={{ fontSize: '12px', color: colors.textDim, mb: 1 }}>
                Overdue Vaccinations
              </Typography>
              <Typography
                sx={{ fontSize: '36px', fontWeight: 700, color: colors.accentRed, lineHeight: 1 }}
              >
                {overdueCount}
              </Typography>
              <Typography sx={{ fontSize: '12px', color: colors.textDim, mt: 1 }}>
                require immediate attention
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card sx={{ borderLeft: `3px solid ${colors.accentBlue}` }}>
            <CardContent sx={{ textAlign: "center", py: 3 }}>
              <Typography sx={{ fontSize: '12px', color: colors.textDim, mb: 1 }}>
                Vaccinations This Month
              </Typography>
              <Typography
                sx={{ fontSize: '36px', fontWeight: 700, color: colors.accentBlue, lineHeight: 1 }}
              >
                {thisMonthCount}
              </Typography>
              <Typography sx={{ fontSize: '12px', color: colors.textDim, mt: 1 }}>
                scheduled ahead
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* ---- Village coverage table ---- */}
      <Typography variant="h6" gutterBottom>
        Village-Level Coverage
      </Typography>
      <Paper sx={{ mb: 4 }}>
        <TableContainer>
          <Table aria-label="Village vaccination coverage">
            <TableHead>
              <TableRow>
                <TableCell>Village Code</TableCell>
                <TableCell>Village Name</TableCell>
                <TableCell align="right">Total Animals</TableCell>
                <TableCell align="right">Vaccinated</TableCell>
                <TableCell align="right">Coverage %</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {villages.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6}>
                    <Typography color="text.secondary" sx={{ p: 4, textAlign: 'center' }}>No data available. Ensure the API is running and database is seeded.</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                villages.map((v) => {
                  const pct = v.totalAnimals > 0 ? Math.round((v.vaccinated / v.totalAnimals) * 100) : 0;
                  return (
                    <TableRow key={v.code}>
                      <TableCell sx={sxCodeCell}>
                        {v.code}
                      </TableCell>
                      <TableCell sx={sxNameCell}>
                        {v.name}
                      </TableCell>
                      <TableCell align="right">{v.totalAnimals}</TableCell>
                      <TableCell align="right">{v.vaccinated}</TableCell>
                      <TableCell align="right">
                        <Typography fontWeight={600} color={coverageColor(pct)} fontSize="13px">
                          {pct}%
                        </Typography>
                      </TableCell>
                      <TableCell>{statusBadge(pct)}</TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* ---- Species breakdown ---- */}
      <Typography variant="h6" gutterBottom>
        Species Breakdown
      </Typography>
      {speciesList.length === 0 ? (
        <Typography color="text.secondary" sx={{ p: 4, textAlign: 'center', mb: 4 }}>No species data available.</Typography>
      ) : (
        <Grid container spacing={2} mb={4}>
          {speciesList.map((sp) => (
            <Grid item xs={12} sm={6} md={3} key={sp.species}>
              <Card sx={{ height: "100%" }}>
                <CardContent>
                  <Typography sx={{ fontSize: '15px', fontWeight: 700, color: colors.text, mb: 1.5 }}>
                    {sp.emoji} {sp.species}
                  </Typography>
                  <Stack spacing={1.5}>
                    {sp.vaccines.map((vac) => (
                      <Box key={vac.vaccine}>
                        <Box display="flex" justifyContent="space-between" mb={0.5}>
                          <Typography sx={{ fontSize: '12px', color: colors.textDim }}>
                            {vac.vaccine}
                          </Typography>
                          <Typography sx={{ fontSize: '12px', fontWeight: 600, color: coverageColor(vac.coverage) }}>
                            {vac.coverage}%
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={vac.coverage}
                          sx={{
                            height: 6,
                            borderRadius: 3,
                            bgcolor: 'rgba(0,0,0,0.06)',
                            '& .MuiLinearProgress-bar': { bgcolor: coverageColor(vac.coverage), borderRadius: 3 },
                          }}
                        />
                      </Box>
                    ))}
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* ---- Upcoming schedule ---- */}
      <Typography variant="h6" gutterBottom>
        Upcoming Schedule
      </Typography>
      <Paper>
        <TableContainer>
          <Table aria-label="Upcoming vaccination schedule">
            <TableHead>
              <TableRow>
                <TableCell>Animal</TableCell>
                <TableCell>Owner</TableCell>
                <TableCell>Vaccine</TableCell>
                <TableCell>Due Date</TableCell>
                <TableCell align="right">Days Until Due</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sortedSchedule.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5}>
                    <Typography color="text.secondary" sx={{ p: 4, textAlign: 'center' }}>No upcoming vaccinations.</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                sortedSchedule.map((entry) => (
                  <TableRow key={`${entry.animal}-${entry.vaccine}-${entry.dueDate}`}>
                    <TableCell sx={sxNameCell}>
                      {entry.animal}
                    </TableCell>
                    <TableCell>{entry.owner}</TableCell>
                    <TableCell>{entry.vaccine}</TableCell>
                    <TableCell
                      sx={{ ...sxCodeCell, whiteSpace: "nowrap" }}
                    >
                      {fmtDate(entry.dueDate)}
                    </TableCell>
                    <TableCell align="right">
                      <Chip
                        label={
                          entry.daysUntilDue < 0
                            ? `${Math.abs(entry.daysUntilDue)}d overdue`
                            : entry.daysUntilDue === 0
                              ? "Today"
                              : `${entry.daysUntilDue}d`
                        }
                        size="small"
                        sx={{
                          fontWeight: 600,
                          fontSize: '11.5px',
                          color: colors.surface,
                          bgcolor: urgencyColor(entry.daysUntilDue),
                          border: 'none',
                        }}
                      />
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}
