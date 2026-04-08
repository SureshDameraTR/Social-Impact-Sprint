"use client";

import { useState, useMemo } from "react";
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
} from "@mui/material";
import ShoppingCartIcon from "@mui/icons-material/ShoppingCart";
import CurrencyRupeeIcon from "@mui/icons-material/CurrencyRupee";
import StorefrontIcon from "@mui/icons-material/Storefront";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import StatCard from "@/components/StatCard";

interface MarketTx {
  id: string;
  date: string;
  farmer: string;
  product_type: string;
  quantity: number;
  unit: string;
  price_per_unit: number;
  total_amount: number;
  buyer: string;
}

const mockTx: MarketTx[] = [
  { id: "TX001", date: "2026-04-08", farmer: "Ramesh Gowda", product_type: "Milk", quantity: 50, unit: "L", price_per_unit: 42, total_amount: 2100, buyer: "Nandini Dairy" },
  { id: "TX002", date: "2026-04-08", farmer: "Lakshmi Devi", product_type: "Ghee", quantity: 5, unit: "kg", price_per_unit: 650, total_amount: 3250, buyer: "Local Market" },
  { id: "TX003", date: "2026-04-07", farmer: "Manjunath K", product_type: "Goat Milk", quantity: 10, unit: "L", price_per_unit: 80, total_amount: 800, buyer: "Direct Consumer" },
  { id: "TX004", date: "2026-04-07", farmer: "Krishna Murthy", product_type: "Curd", quantity: 20, unit: "kg", price_per_unit: 55, total_amount: 1100, buyer: "KMF Outlet" },
  { id: "TX005", date: "2026-04-07", farmer: "Suresh Babu", product_type: "Milk", quantity: 80, unit: "L", price_per_unit: 44, total_amount: 3520, buyer: "Nandini Dairy" },
  { id: "TX006", date: "2026-04-06", farmer: "Nagaraj P", product_type: "Butter", quantity: 3, unit: "kg", price_per_unit: 520, total_amount: 1560, buyer: "Direct Consumer" },
  { id: "TX007", date: "2026-04-06", farmer: "Parvathi Amma", product_type: "Goat Milk", quantity: 8, unit: "L", price_per_unit: 85, total_amount: 680, buyer: "Health Store" },
  { id: "TX008", date: "2026-04-05", farmer: "Basavaraju N", product_type: "Eggs", quantity: 200, unit: "nos", price_per_unit: 6, total_amount: 1200, buyer: "Wholesale Market" },
  { id: "TX009", date: "2026-04-05", farmer: "Ramesh Gowda", product_type: "Paneer", quantity: 8, unit: "kg", price_per_unit: 380, total_amount: 3040, buyer: "Restaurant" },
  { id: "TX010", date: "2026-04-04", farmer: "Shivamma R", product_type: "Milk", quantity: 60, unit: "L", price_per_unit: 43, total_amount: 2580, buyer: "Nandini Dairy" },
];

const revenueByProduct = [
  { product: "Milk", revenue: 8200 },
  { product: "Ghee", revenue: 3250 },
  { product: "Paneer", revenue: 3040 },
  { product: "Curd", revenue: 1100 },
  { product: "Butter", revenue: 1560 },
  { product: "Eggs", revenue: 1200 },
  { product: "Goat Milk", revenue: 1480 },
];

export default function MarketplacePage() {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const { data } = useList<MarketTx>({ resource: "marketplace" });
  const txs = data?.data ?? mockTx;

  const totalVolume = txs.reduce((s, t) => s + t.total_amount, 0);
  const uniqueSellers = new Set(txs.map((t) => t.farmer)).size;

  const fmtCurrency = (n: number) =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(n);

  return (
    <Box p={3}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Marketplace
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        Farmer-to-buyer transactions and revenue analytics
      </Typography>

      {/* Stat Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={4}>
          <StatCard
            icon={<ShoppingCartIcon sx={{ fontSize: 28, color: "#1565c0" }} />}
            title="Total Sales Volume"
            value={fmtCurrency(totalVolume)}
            color="#1565c0"
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <StatCard
            icon={<CurrencyRupeeIcon sx={{ fontSize: 28, color: "#6a1b9a" }} />}
            title="Average Tx Value"
            value={fmtCurrency(Math.round(totalVolume / txs.length))}
            color="#6a1b9a"
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <StatCard
            icon={<StorefrontIcon sx={{ fontSize: 28, color: "#e65100" }} />}
            title="Active Sellers"
            value={uniqueSellers}
            color="#e65100"
          />
        </Grid>
      </Grid>

      {/* Revenue by Product Chart */}
      <Paper sx={{ p: 3, borderRadius: 2, mb: 3 }}>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          Revenue by Product
        </Typography>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={revenueByProduct}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="product" />
            <YAxis />
            <Tooltip formatter={(v: number) => fmtCurrency(v)} />
            <Bar dataKey="revenue" fill="#6a1b9a" name="Revenue" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </Paper>

      {/* Transaction Table */}
      <Paper sx={{ borderRadius: 2 }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 700 }}>Date</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Farmer</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Product</TableCell>
                <TableCell sx={{ fontWeight: 700 }} align="right">Qty</TableCell>
                <TableCell sx={{ fontWeight: 700 }} align="right">Price/Unit</TableCell>
                <TableCell sx={{ fontWeight: 700 }} align="right">Total</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Buyer</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {txs
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((tx) => (
                  <TableRow key={tx.id} hover>
                    <TableCell sx={{ whiteSpace: "nowrap" }}>
                      {new Date(tx.date).toLocaleDateString("en-IN")}
                    </TableCell>
                    <TableCell>{tx.farmer}</TableCell>
                    <TableCell>
                      <Chip label={tx.product_type} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell align="right">
                      {tx.quantity} {tx.unit}
                    </TableCell>
                    <TableCell align="right">{fmtCurrency(tx.price_per_unit)}</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 600 }}>
                      {fmtCurrency(tx.total_amount)}
                    </TableCell>
                    <TableCell>{tx.buyer}</TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={txs.length}
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
