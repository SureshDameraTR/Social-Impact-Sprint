"use client";

import { useState, useMemo, useEffect, useCallback } from "react";
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
  Grid,
  Chip,
  TextField,
  InputAdornment,
  CircularProgress,
  Alert,
} from "@mui/material";
import ShoppingCartIcon from "@mui/icons-material/ShoppingCart";
import CurrencyRupeeIcon from "@mui/icons-material/CurrencyRupee";
import StorefrontIcon from "@mui/icons-material/Storefront";
import SearchIcon from "@mui/icons-material/Search";
import dynamic from "next/dynamic";
import StatCard from "@/components/StatCard";
import { fmtCurrency } from "@/utils/format";
import { colors, sxCodeCell, sxNameCell, tooltipStyle, axisTickStyle, gridStroke } from "@/theme/theme";
import EmptyState from "@/components/EmptyState";

interface MarketTx {
  id: string;
  sold_at: string;
  user_id: string;
  product_type: string;
  quantity: number;
  unit: string;
  price_per_unit: number;
  total_amount: number;
  buyer_name: string | null;
}

interface RevenueByProduct {
  product: string;
  revenue: number;
}

function MarketplaceChart({ data }: { data: RevenueByProduct[] }) {
  const {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  } = require("recharts");

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
        <XAxis dataKey="product" tick={axisTickStyle} tickLine={false} />
        <YAxis tick={axisTickStyle} tickLine={false} />
        <Tooltip
          formatter={(v: number) => fmtCurrency(v)}
          contentStyle={tooltipStyle}
        />
        <Bar dataKey="revenue" fill={colors.secondary} name="Revenue" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

const MarketplaceChartLazy = dynamic(() => Promise.resolve(MarketplaceChart), {
  ssr: false,
  loading: () => (
    <Box sx={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: '#f5f5f5', borderRadius: 1 }}>
      Loading chart...
    </Box>
  ),
});

export default function MarketplacePage() {
  useEffect(() => {
    document.title = 'Marketplace — PashuRaksha ERP';
  }, []);

  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const { data, isLoading, isError } = useList<MarketTx>({ resource: "marketplace" });

  const txs = data?.data ?? [];

  const totalVolume = useMemo(() => txs.reduce((s, t) => s + t.total_amount, 0), [txs]);
  const uniqueSellers = useMemo(() => new Set(txs.map((t) => t.user_id)).size, [txs]);

  const revenueByProduct = useMemo(() => {
    const map: Record<string, number> = {};
    txs.forEach((t) => { map[t.product_type] = (map[t.product_type] || 0) + t.total_amount; });
    return Object.entries(map).map(([product, revenue]) => ({ product, revenue }));
  }, [txs]);

  const filtered = useMemo(
    () =>
      txs.filter(
        (t) =>
          (t.user_id || "").toLowerCase().includes(search.toLowerCase()) ||
          t.product_type.toLowerCase().includes(search.toLowerCase()) ||
          (t.buyer_name || "").toLowerCase().includes(search.toLowerCase())
      ),
    [txs, search]
  );

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 8 }}><CircularProgress /></Box>;
  if (isError) return <Box sx={{ p: 4 }}><Alert severity="error">Failed to load data from server.</Alert></Box>;

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom sx={{ color: colors.text }}>
        Marketplace
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        Farmer-to-buyer transactions and revenue analytics
      </Typography>

      {/* Stat Cards */}
      <Grid container spacing={2.5} mb={3}>
        <Grid item xs={12} sm={4}>
          <StatCard
            icon={<ShoppingCartIcon sx={{ fontSize: 28, color: colors.primary }} />}
            title="Total Sales Volume"
            value={fmtCurrency(totalVolume)}
            color={colors.primary}
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <StatCard
            icon={<CurrencyRupeeIcon sx={{ fontSize: 28, color: colors.secondary }} />}
            title="Average Tx Value"
            value={fmtCurrency(txs.length > 0 ? Math.round(totalVolume / txs.length) : 0)}
            color={colors.secondary}
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <StatCard
            icon={<StorefrontIcon sx={{ fontSize: 28, color: colors.accentAmber }} />}
            title="Active Sellers"
            value={uniqueSellers}
            color={colors.accentAmber}
          />
        </Grid>
      </Grid>

      {/* Revenue by Product Chart */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Revenue by Product
        </Typography>
        <MarketplaceChartLazy data={revenueByProduct} />
      </Paper>

      {/* Transaction Table */}
      <Paper>
        <Box p={2}>
          <TextField
            size="small"
            placeholder="Search by farmer, product, or buyer..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(0); }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ color: colors.textLight }} />
                </InputAdornment>
              ),
            }}
            sx={{ minWidth: 320 }}
          />
        </Box>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Farmer</TableCell>
                <TableCell>Product</TableCell>
                <TableCell align="right">Qty</TableCell>
                <TableCell align="right">Price/Unit</TableCell>
                <TableCell align="right">Total</TableCell>
                <TableCell>Buyer</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filtered.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} sx={{ border: 0 }}>
                    <EmptyState />
                  </TableCell>
                </TableRow>
              ) : (
                filtered
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((tx) => (
                    <TableRow key={tx.id}>
                      <TableCell
                        sx={{ ...sxCodeCell, whiteSpace: "nowrap" }}
                      >
                        {new Date(tx.sold_at).toLocaleDateString("en-IN", { timeZone: "Asia/Kolkata" })}
                      </TableCell>
                      <TableCell sx={{ fontSize: '11px', color: colors.textDim }}>
                        {tx.user_id?.slice(0, 8)}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={tx.product_type}
                          size="small"
                          sx={{
                            bgcolor: colors.primaryLight,
                            color: colors.primary,
                            border: 'none',
                            fontSize: '11.5px',
                          }}
                        />
                      </TableCell>
                      <TableCell
                        align="right"
                        sx={{ fontFamily: sxCodeCell.fontFamily, fontSize: sxCodeCell.fontSize }}
                      >
                        {tx.quantity} {tx.unit}
                      </TableCell>
                      <TableCell
                        align="right"
                        sx={{ fontFamily: sxCodeCell.fontFamily, fontSize: sxCodeCell.fontSize }}
                      >
                        {fmtCurrency(tx.price_per_unit)}
                      </TableCell>
                      <TableCell
                        align="right"
                        sx={{ ...sxCodeCell, fontWeight: 600, color: colors.text }}
                      >
                        {fmtCurrency(tx.total_amount)}
                      </TableCell>
                      <TableCell sx={{ fontSize: '12.5px', color: colors.textDim }}>
                        {tx.buyer_name || '\u2014'}
                      </TableCell>
                    </TableRow>
                  ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={filtered.length}
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
