import { useState, useEffect, useCallback } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Alert,
  Skeleton,
  Grid,
} from "@mui/material";
import { getDailyReport } from "../api/milk";
import { useCentre } from "../hooks/useCentre";
import { inrFormatterRounded } from "../types";

interface ShiftData {
  liters: number;
  farmers: number;
}

interface DailyReport {
  center_id: string;
  date: string;
  summary: {
    total_liters: number;
    total_amount_inr: number;
    farmer_count: number;
    record_count: number;
    avg_fat_pct: number;
    avg_snf_pct: number;
  };
  morning: ShiftData;
  evening: ShiftData;
}

const REFRESH_INTERVAL_MS = 60_000;


function StatCard({
  value,
  label,
  sublabel,
}: {
  value: string;
  label: string;
  sublabel?: string;
}) {
  return (
    <Card sx={{ height: "100%" }}>
      <CardContent>
        <Typography variant="h4" fontWeight={700}>
          {value}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {label}
        </Typography>
        {sublabel && (
          <Typography variant="body2" color="text.secondary">
            {sublabel}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}

function ShiftCard({
  title,
  shift,
}: {
  title: string;
  shift: ShiftData;
}) {
  return (
    <Card sx={{ height: "100%" }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Typography variant="h5" fontWeight={700}>
          {shift.liters} L
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {shift.farmers} farmers
        </Typography>
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const { centreId } = useCentre();
  const [report, setReport] = useState<DailyReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchReport = useCallback(async () => {
    if (!centreId) return;
    try {
      const res = await getDailyReport(centreId);
      setReport(res.data);
      setError(null);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Failed to load daily report";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [centreId]);

  useEffect(() => {
    setLoading(true);
    setReport(null);
    fetchReport();

    const id = setInterval(fetchReport, REFRESH_INTERVAL_MS);
    return () => clearInterval(id);
  }, [fetchReport]);

  if (loading) {
    return (
      <Box p={3}>
        <Grid container spacing={2}>
          {[0, 1, 2, 3].map((i) => (
            <Grid item xs={6} md={3} key={i}>
              <Skeleton variant="rounded" height={120} />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (!report) return null;

  const { summary, morning, evening } = report;

  return (
    <Box p={3}>
      <Typography variant="h5" fontWeight={700} gutterBottom>
        Daily Collection &mdash; {report.date}
      </Typography>

      <Grid container spacing={2} mb={3}>
        <Grid item xs={6} md={3}>
          <StatCard
            value={`${summary.total_liters} L`}
            label="Today's Milk"
          />
        </Grid>
        <Grid item xs={6} md={3}>
          <StatCard
            value={inrFormatterRounded.format(summary.total_amount_inr)}
            label="Today's Revenue"
          />
        </Grid>
        <Grid item xs={6} md={3}>
          <StatCard
            value={String(summary.farmer_count)}
            label="Farmers Today"
          />
        </Grid>
        <Grid item xs={6} md={3}>
          <StatCard
            value={`${summary.avg_fat_pct}% Fat`}
            label="Avg Quality"
            sublabel={`${summary.avg_snf_pct}% SNF`}
          />
        </Grid>
      </Grid>

      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <ShiftCard title="Morning Shift" shift={morning} />
        </Grid>
        <Grid item xs={12} md={6}>
          <ShiftCard title="Evening Shift" shift={evening} />
        </Grid>
      </Grid>
    </Box>
  );
}
