import { useState, useEffect } from "react";
import {
  Box,
  TextField,
  InputAdornment,
  List,
  ListItemButton,
  ListItemText,
  Typography,
  ToggleButtonGroup,
  ToggleButton,
  Button,
  CircularProgress,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import PersonAddIcon from "@mui/icons-material/PersonAdd";
import { useNavigate } from "react-router-dom";
import { searchFarmers } from "../api/milk";
import type { Farmer } from "../types";

interface FarmerSearchProps {
  onSelect: (farmer: Farmer | null) => void;
  selected: Farmer | null;
}

export default function FarmerSearch({ onSelect, selected }: FarmerSearchProps) {
  const navigate = useNavigate();
  const [mode, setMode] = useState<"phone" | "aadhaar">("phone");
  const [phone, setPhone] = useState("");
  const [aadhaarLast4, setAadhaarLast4] = useState("");
  const [name, setName] = useState("");
  const [results, setResults] = useState<Farmer[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  // Debounced phone search
  useEffect(() => {
    if (mode !== "phone" || phone.length < 3) {
      setResults([]);
      setSearched(false);
      return;
    }
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const { data } = await searchFarmers({ phone });
        setResults(data);
        setSearched(true);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [phone, mode]);

  const handleAadhaarSearch = async () => {
    if (!aadhaarLast4 && !name) return;
    setLoading(true);
    try {
      const params: { aadhaar_last4?: string; name?: string } = {};
      if (aadhaarLast4) params.aadhaar_last4 = aadhaarLast4;
      if (name) params.name = name;
      const { data } = await searchFarmers(params);
      setResults(data);
      setSearched(true);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  if (selected) {
    return (
      <Box sx={{ p: 2, bgcolor: "primary.light", borderRadius: 2, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Box>
          <Typography fontWeight={600}>{selected.name}</Typography>
          <Typography variant="body2" color="text.secondary">
            {selected.phone} {selected.aadhaar_last4 ? `· Aadhaar ****${selected.aadhaar_last4}` : ""}
          </Typography>
        </Box>
        <Button size="small" onClick={() => onSelect(null)}>Change</Button>
      </Box>
    );
  }

  return (
    <Box>
      <ToggleButtonGroup
        value={mode}
        exclusive
        onChange={(_, v) => { if (v) setMode(v); }}
        size="small"
        sx={{ mb: 2 }}
      >
        <ToggleButton value="phone">Phone</ToggleButton>
        <ToggleButton value="aadhaar">Aadhaar + Name</ToggleButton>
      </ToggleButtonGroup>

      {mode === "phone" ? (
        <TextField
          fullWidth
          placeholder="Search by phone number..."
          value={phone}
          onChange={(e) => setPhone(e.target.value.replace(/\D/g, ""))}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start"><SearchIcon /></InputAdornment>
            ),
            endAdornment: loading ? <CircularProgress size={20} /> : null,
          }}
          inputProps={{ inputMode: "numeric", maxLength: 10 }}
        />
      ) : (
        <Box sx={{ display: "flex", gap: 1, mb: 1 }}>
          <TextField
            placeholder="Last 4 of Aadhaar"
            value={aadhaarLast4}
            onChange={(e) => setAadhaarLast4(e.target.value.replace(/\D/g, "").slice(0, 4))}
            inputProps={{ inputMode: "numeric", maxLength: 4 }}
            sx={{ width: 160 }}
          />
          <TextField
            placeholder="Farmer name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            sx={{ flexGrow: 1 }}
          />
          <Button variant="contained" onClick={handleAadhaarSearch} disabled={loading || (!aadhaarLast4 && !name)}>
            {loading ? <CircularProgress size={20} /> : "Search"}
          </Button>
        </Box>
      )}

      {results.length > 0 && (
        <List sx={{ mt: 1, border: "1px solid", borderColor: "divider", borderRadius: 2, maxHeight: 200, overflow: "auto" }}>
          {results.map((f) => (
            <ListItemButton key={f.id} onClick={() => { onSelect(f); setResults([]); }}>
              <ListItemText
                primary={f.name}
                secondary={`${f.phone}${f.aadhaar_last4 ? ` · ****${f.aadhaar_last4}` : ""}${f.village_code ? ` · ${f.village_code}` : ""}`}
              />
            </ListItemButton>
          ))}
        </List>
      )}

      {searched && results.length === 0 && !loading && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          No farmers found.
        </Typography>
      )}

      <Button
        startIcon={<PersonAddIcon />}
        size="small"
        sx={{ mt: 1 }}
        onClick={() => navigate("/enroll?returnTo=/intake")}
      >
        New farmer? Enroll here
      </Button>
    </Box>
  );
}
