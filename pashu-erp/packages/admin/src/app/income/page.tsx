"use client";

import { Box, Typography, Paper, Grid } from "@mui/material";
import AccountBalanceWalletIcon from "@mui/icons-material/AccountBalanceWallet";
import PersonIcon from "@mui/icons-material/Person";
import RequestQuoteIcon from "@mui/icons-material/RequestQuote";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import StatCard from "@/components/StatCard";

const incomeByCategory = [
  { category: "Milk Sales", amount: 285000 },
  { category: "Ghee & Butter", amount: 124000 },
  { category: "Livestock Sales", amount: 95000 },
  { category: "Govt Subsidies", amount: 180000 },
  { category: "Eggs & Poultry", amount: 62000 },
  { category: "Organic Manure", amount: 28000 },
];

const monthlyIncome = [
  { month: "Nov", income: 78000 },
  { month: "Dec", income: 92000 },
  { month: "Jan", income: 105000 },
  { month: "Feb", income: 118000 },
  { month: "Mar", income: 142000 },
  { month: "Apr", income: 156000 },
];

const COLORS = ["#1565c0", "#2e7d32", "#f57c00", "#6a1b9a", "#c62828", "#00695c"];

const fmtCurrency = (n: number) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(n);

export default function IncomePage() {
  const totalIncome = incomeByCategory.reduce((s, c) => s + c.amount, 0);
  const avgPerFarmer = Math.round(totalIncome / 2847);

  return (
    <Box p={3}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Income Analytics
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        Farmer income distribution and trends across Mysuru District
      </Typography>

      {/* Stat Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={4}>
          <StatCard
            icon={<AccountBalanceWalletIcon sx={{ fontSize: 28, color: "#1565c0" }} />}
            title="Total Farmer Income"
            value={fmtCurrency(totalIncome)}
            color="#1565c0"
            trend={{ value: 18, label: "vs last quarter" }}
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <StatCard
            icon={<PersonIcon sx={{ fontSize: 28, color: "#2e7d32" }} />}
            title="Avg Income per Farmer"
            value={fmtCurrency(avgPerFarmer)}
            color="#2e7d32"
            trend={{ value: 12, label: "this quarter" }}
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <StatCard
            icon={<RequestQuoteIcon sx={{ fontSize: 28, color: "#f57c00" }} />}
            title="Loan Applications"
            value="142"
            color="#f57c00"
            trend={{ value: 25, label: "this month" }}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Income by Category Bar Chart */}
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Income by Product Category
            </Typography>
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={incomeByCategory} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" tickFormatter={(v) => `${(v / 1000).toFixed(0)}K`} />
                <YAxis type="category" dataKey="category" width={120} tick={{ fontSize: 12 }} />
                <Tooltip formatter={(v: number) => fmtCurrency(v)} />
                <Bar dataKey="amount" fill="#1565c0" name="Income" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Income Distribution Pie */}
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Income Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={320}>
              <PieChart>
                <Pie
                  data={incomeByCategory}
                  dataKey="amount"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={({ category, percent }) =>
                    `${category}: ${(percent * 100).toFixed(0)}%`
                  }
                  labelLine
                >
                  {incomeByCategory.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v: number) => fmtCurrency(v)} />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Monthly Trend */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Monthly Income Trend (Last 6 Months)
            </Typography>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={monthlyIncome}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis tickFormatter={(v) => `${(v / 1000).toFixed(0)}K`} />
                <Tooltip formatter={(v: number) => fmtCurrency(v)} />
                <Legend />
                <Bar dataKey="income" fill="#2e7d32" name="Total Income" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
