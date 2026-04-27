import React, { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import axios from "axios";
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  InputAdornment,
  CircularProgress,
  Link,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { enrollFarmer } from "../api/milk";

const PHONE_REGEX = /^[6-9]\d{9}$/;
const AADHAAR_REGEX = /^\d{12}$/;

function maskAadhaar(raw: string): string {
  if (raw.length <= 4) return raw;
  if (raw.length <= 8) return "X".repeat(4) + "-" + raw.slice(4);
  return "XXXX-XXXX-" + raw.slice(8);
}

export default function Enroll() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const returnTo = searchParams.get("returnTo");

  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [aadhaar, setAadhaar] = useState("");
  const [village, setVillage] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const isPhoneValid = PHONE_REGEX.test(phone);
  const isAadhaarValid = AADHAAR_REGEX.test(aadhaar);
  const canSubmit = name.trim() !== "" && isPhoneValid && isAadhaarValid && !loading;

  const resetForm = () => {
    setName("");
    setPhone("");
    setAadhaar("");
    setVillage("");
    setError("");
    setSuccess(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;
    setLoading(true);
    setError("");
    try {
      const res = await enrollFarmer({
        name: name.trim(),
        phone: "+91" + phone,
        aadhaar,
        village_code: village.trim() || undefined,
      });
      if (returnTo) {
        navigate(returnTo, { state: { enrolledFarmer: res.data } });
      } else {
        setSuccess(true);
      }
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response?.status === 409) {
        setError(err.response.data?.detail || "A farmer with this phone or Aadhaar already exists.");
      } else if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || "Something went wrong. Please try again.");
      } else {
        setError("Something went wrong. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        bgcolor: "background.default",
        p: 2,
      }}
    >
      <Card sx={{ maxWidth: 440, width: "100%", borderRadius: 3, boxShadow: 3 }}>
        <CardContent sx={{ p: 4 }}>
          {returnTo && (
            <Link
              component="button"
              variant="body2"
              onClick={() => navigate(returnTo)}
              sx={{ display: "flex", alignItems: "center", mb: 2, color: "primary.main" }}
            >
              <ArrowBackIcon sx={{ fontSize: 18, mr: 0.5 }} />
              Back
            </Link>
          )}

          <Typography variant="h5" fontWeight={700} sx={{ mb: 3 }}>
            Enroll New Farmer
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError("")}>
              {error}
            </Alert>
          )}

          {success ? (
            <>
              <Alert severity="success" sx={{ mb: 2 }}>
                Farmer enrolled successfully!
              </Alert>
              <Button
                fullWidth
                variant="contained"
                size="large"
                onClick={resetForm}
                sx={{
                  bgcolor: "primary.main",
                  "&:hover": { bgcolor: "primary.dark" },
                  textTransform: "none",
                  fontWeight: 700,
                  fontSize: 16,
                  py: 1.5,
                  borderRadius: 2,
                }}
              >
                Enroll Another
              </Button>
            </>
          ) : (
            <Box component="form" onSubmit={handleSubmit} noValidate>
              <TextField
                fullWidth
                label="Full Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                label="Phone Number"
                placeholder="9876543210"
                value={phone}
                onChange={(e) => setPhone(e.target.value.replace(/\D/g, "").slice(0, 10))}
                required
                InputProps={{
                  startAdornment: <InputAdornment position="start">+91</InputAdornment>,
                }}
                inputProps={{ inputMode: "numeric", maxLength: 10 }}
                error={phone.length === 10 && !isPhoneValid}
                helperText={
                  phone.length === 10 && !isPhoneValid
                    ? "Enter a valid Indian mobile number"
                    : " "
                }
                sx={{ mb: 1 }}
              />

              <TextField
                fullWidth
                label="Aadhaar Number"
                value={maskAadhaar(aadhaar)}
                onChange={(e) => {
                  const inputDigits = e.target.value.replace(/[^0-9]/g, "");
                  if (inputDigits.length < aadhaar.length) {
                    // backspace — remove last digit from raw
                    setAadhaar(aadhaar.slice(0, -1));
                  } else if (inputDigits.length > aadhaar.length) {
                    // new digit(s) typed — figure out what was added
                    const newChars = inputDigits.slice(aadhaar.length);
                    setAadhaar((aadhaar + newChars).slice(0, 12));
                  }
                }}
                onKeyDown={(e) => {
                  if (e.key === "Backspace") {
                    e.preventDefault();
                    setAadhaar(aadhaar.slice(0, -1));
                  }
                }}
                required
                inputProps={{ inputMode: "numeric", maxLength: 14 }}
                error={aadhaar.length === 12 && !isAadhaarValid}
                helperText={
                  aadhaar.length > 0 && aadhaar.length < 12
                    ? `${12 - aadhaar.length} digits remaining`
                    : " "
                }
                sx={{ mb: 1 }}
              />

              <TextField
                fullWidth
                label="Village (optional)"
                value={village}
                onChange={(e) => setVillage(e.target.value)}
                sx={{ mb: 3 }}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={!canSubmit}
                sx={{
                  bgcolor: "primary.main",
                  "&:hover": { bgcolor: "primary.dark" },
                  textTransform: "none",
                  fontWeight: 700,
                  fontSize: 16,
                  py: 1.5,
                  borderRadius: 2,
                }}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : "Enroll Farmer"}
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
