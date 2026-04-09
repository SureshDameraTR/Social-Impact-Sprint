"use client";

import { useEffect, useMemo } from "react";
import { useList } from "@refinedev/core";
import dynamic from "next/dynamic";
import { Box, Typography, Paper, Grid, Skeleton, CircularProgress, Alert } from "@mui/material";
import AccountBalanceWalletIcon from "@mui/icons-material/AccountBalanceWallet";
import PersonIcon from "@mui/icons-material/Person";
import RequestQuoteIcon from "@mui/icons-material/RequestQuote";
import StatCard from "@/components/StatCard";
import { fmtCurrency } from "@/utils/format";
import { colors, tooltipStyle, axisTickStyle, gridStroke } from "@/theme/theme";

interface IncomeCategory {
  category: string;
  amount: number;
}

interface MonthlyIncome {
  month: string;
  income: number;
}

const COLORS = [colors.primary, colors.accentGreen, colors.accentAmber, colors.secondary, colors.accentRed, colors.accentBlue];

function IncomeCharts({ incomeByCategory, monthlyIncome }: { incomeByCategory: IncomeCategory[]; monthlyIncome: MonthlyIncome[] }) {
  const {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, PieChart, Pie, Cell, Legend,
  } = require("recharts");

  return (
    <Grid container spacing={2.5}>
      <Grid item xs={12} md={7}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Income by Product Category
          </Typography>
          {incomeByCategory.length === 0 ? (
            <Typography color="text.secondary" sx={{ p: 4, textAlign: 'center' }}>No data available. Ensure the API is running and database is seeded.</Typography>
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={incomeByCategory} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
                <XAxis type="number" tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}K`} tick={axisTickStyle} tickLine={false} />
                <YAxis type="category" dataKey="category" width={120} tick={{ fontSize: 12, fill: colors.textDim }} tickLine={false} />
                <Tooltip formatter={(v: number) => fmtCurrency(v)} contentStyle={tooltipStyle} />
                <Bar dataKey="amount" fill={colors.primary} name="Income" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </Paper>
      </Grid>
      <Grid item xs={12} md={5}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Income Distribution
          </Typography>
          {incomeByCategory.length === 0 ? (
            <Typography color="text.secondary" sx={{ p: 4, textAlign: 'center' }}>No data available.</Typography>
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <PieChart>
                <Pie
                  data={incomeByCategory}
                  dataKey="amount"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={({ category, percent }: { category: string; percent: number }) =>
                    `${category}: ${(percent * 100).toFixed(0)}%`
                  }
                  labelLine
                >
                  {incomeByCategory.map((_: unknown, i: number) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v: number) => fmtCurrency(v)} contentStyle={tooltipStyle} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </Paper>
      </Grid>
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Monthly Income Trend (Last 6 Months)
          </Typography>
          {monthlyIncome.length === 0 ? (
            <Typography color="text.secondary" sx={{ p: 4, textAlign: 'center' }}>No data available.</Typography>
          ) : (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={monthlyIncome}>
                <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
                <XAxis dataKey="month" tick={axisTickStyle} tickLine={false} />
                <YAxis tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}K`} tick={axisTickStyle} tickLine={false} />
                <Tooltip formatter={(v: number) => fmtCurrency(v)} contentStyle={tooltipStyle} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="income" fill={colors.accentGreen} name="Total Income" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </Paper>
      </Grid>
    </Grid>
  );
}

const IncomeChartsLazy = dynamic(() => Promise.resolve(IncomeCharts), {
  ssr: false,
  loading: () => <Skeleton variant="rectangular" height={300} />,
});

export default function IncomePage() {
  useEffect(() => {
    document.title = 'Income Analytics — PashuRaksha ERP';
  }, []);

  const { data: categoryData, isLoading: catLoading, isError: catError } = useList<any>({ resource: "income/by-category" });
  const { data: monthlyData, isLoading: monthLoading, isError: monthError } = useList<MonthlyIncome>({ resource: "income/monthly" });

  const isLoading = catLoading || monthLoading;
  const isError = catError || monthError;

  // income/by-category returns {period, breakdown: {key: amount}} — convert to array
  const rawCat = categoryData?.data ?? [];
  const incomeByCategory: IncomeCategory[] = useMemo(() => {
    const first = rawCat[0];
    if (first?.breakdown && typeof first.breakdown === "object") {
      return Object.entries(first.breakdown)
        .filter(([k]) => !k.startsWith("marketplace_")) // avoid dupes
        .map(([category, amount]) => ({ category, amount: amount as number }));
    }
    if (first?.category) return rawCat as IncomeCategory[];
    return [];
  }, [rawCat]);

  const monthlyIncome: MonthlyIncome[] = monthlyData?.data ?? [];

  const { totalIncome, avgPerFarmer } = useMemo(() => {
    const total = incomeByCategory.reduce((s: number, c: any) => s + c.amount, 0);
    const count = incomeByCategory.length;
    return { totalIncome: total, avgPerFarmer: count > 0 ? Math.round(total / count) : 0 };
  }, [incomeByCategory]);

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 8 }}><CircularProgress /></Box>;
  if (isError) return <Box sx={{ p: 4 }}><Alert severity="error">Failed to load data from server.</Alert></Box>;

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom sx={{ color: colors.text }}>
        Income Analytics
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        Farmer income distribution and trends across Mysuru District
      </Typography>

      {/* Stat Cards */}
      <Grid container spacing={2.5} mb={4}>
        <Grid item xs={12} sm={4}>
          <StatCard
            icon={<AccountBalanceWalletIcon sx={{ fontSize: 28, color: colors.primary }} />}
            title="Total Farmer Income"
            value={fmtCurrency(totalIncome)}
            color={colors.primary}
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <StatCard
            icon={<PersonIcon sx={{ fontSize: 28, color: colors.accentGreen }} />}
            title="Avg Income per Farmer"
            value={fmtCurrency(avgPerFarmer)}
            color={colors.accentGreen}
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <StatCard
            icon={<RequestQuoteIcon sx={{ fontSize: 28, color: colors.accentAmber }} />}
            title="Loan Applications"
            value="--"
            color={colors.accentAmber}
          />
        </Grid>
      </Grid>

      <IncomeChartsLazy incomeByCategory={incomeByCategory} monthlyIncome={monthlyIncome} />
    </Box>
  );
}
