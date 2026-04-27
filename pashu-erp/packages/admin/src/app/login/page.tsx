"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  InputAdornment,
  Checkbox,
  FormControlLabel,
  Alert,
  Link,
  CircularProgress,
} from "@mui/material";
import PhoneIcon from "@mui/icons-material/Call";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

const PHONE_REGEX = /^[6-9]\d{9}$/;
const OTP_LENGTH = 6;
const RESEND_COOLDOWN_SECONDS = 60;

interface AuthError {
  detail: string;
  code: string;
}

export default function LoginPage() {
  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState(Array(OTP_LENGTH).fill(""));
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [resendCooldown, setResendCooldown] = useState(0);

  const otpRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    if (resendCooldown <= 0) return;
    const timer = setInterval(() => setResendCooldown((c) => c - 1), 1000);
    return () => clearInterval(timer);
  }, [resendCooldown]);

  const phoneWithPrefix = `+91${phone}`;
  const isPhoneValid = PHONE_REGEX.test(phone);
  const otpString = otp.join("");
  const isOtpComplete = otpString.length === OTP_LENGTH;

  const handleSendOtp = useCallback(async () => {
    if (!isPhoneValid) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_URL}/auth/request-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone: phoneWithPrefix }),
        credentials: "include",
      });
      if (!res.ok) {
        const err: AuthError = await res.json();
        throw new Error(err.detail || "Failed to send OTP");
      }
      setStep("otp");
      setResendCooldown(RESEND_COOLDOWN_SECONDS);
      setTimeout(() => otpRefs.current[0]?.focus(), 100);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Network error");
    } finally {
      setLoading(false);
    }
  }, [isPhoneValid, phoneWithPrefix]);

  const handleVerifyOtp = useCallback(async () => {
    if (!isOtpComplete) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_URL}/auth/verify-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phone: phoneWithPrefix,
          otp: otpString,
          remember_me: rememberMe,
          client_type: "web",
        }),
        credentials: "include",
      });
      if (!res.ok) {
        const err: AuthError = await res.json();
        setError(err.detail || "Verification failed");
        if (err.code === "OTP_MAX_ATTEMPTS" || err.code === "OTP_EXPIRED") {
          setStep("phone");
          setOtp(Array(OTP_LENGTH).fill(""));
        }
        return;
      }
      window.location.href = "/";
    } catch (e) {
      setError(e instanceof Error ? e.message : "Network error");
    } finally {
      setLoading(false);
    }
  }, [isOtpComplete, phoneWithPrefix, otpString, rememberMe]);

  const handleOtpChange = (value: string, index: number) => {
    const cleaned = value.replace(/\D/g, "");
    if (!cleaned) return;

    // Multi-digit paste: distribute digits across boxes starting at index
    if (cleaned.length > 1) {
      const digits = cleaned.slice(0, OTP_LENGTH).split("");
      const newOtp = [...otp];
      digits.forEach((d, i) => {
        if (index + i < OTP_LENGTH) newOtp[index + i] = d;
      });
      setOtp(newOtp);
      const focusIdx = Math.min(index + digits.length, OTP_LENGTH - 1);
      otpRefs.current[focusIdx]?.focus();
      return;
    }

    // Single digit: take the last character to handle MUI controlled-input
    // re-firing onChange with oldChar+newChar when maxLength=1 is bypassed
    const digit = cleaned.slice(-1);
    const newOtp = [...otp];
    newOtp[index] = digit;
    setOtp(newOtp);
    if (digit && index < OTP_LENGTH - 1) {
      otpRefs.current[index + 1]?.focus();
    }
  };

  const handleOtpKeyDown = (e: React.KeyboardEvent, index: number) => {
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      otpRefs.current[index - 1]?.focus();
    }
  };

  const handleResend = () => {
    setOtp(Array(OTP_LENGTH).fill(""));
    setError("");
    handleSendOtp();
  };

  const handleChangePhone = () => {
    setStep("phone");
    setOtp(Array(OTP_LENGTH).fill(""));
    setError("");
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
        {/* Header */}
        <Box
          sx={{
            bgcolor: "primary.dark",
            color: "common.white",
            textAlign: "center",
            py: 4,
            borderRadius: "12px 12px 0 0",
          }}
        >
          <Typography variant="h3" sx={{ mb: 0.5 }}>
            {"\uD83D\uDC04"}
          </Typography>
          <Typography variant="h5" fontWeight={700}>
            PashuRaksha
          </Typography>
          <Typography variant="body2" sx={{ color: "primary.light", mt: 0.5 }}>
            Admin Portal
          </Typography>
        </Box>

        <CardContent sx={{ p: 4 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError("")}>
              {error}
            </Alert>
          )}

          {step === "phone" ? (
            <>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
                Staff Login
              </Typography>
              <TextField
                fullWidth
                label="Mobile Number"
                placeholder="9876543210"
                value={phone}
                onChange={(e) => setPhone(e.target.value.replace(/\D/g, "").slice(0, 10))}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <PhoneIcon sx={{ mr: 0.5 }} />
                      +91
                    </InputAdornment>
                  ),
                }}
                inputProps={{ inputMode: "numeric", maxLength: 10 }}
                error={phone.length === 10 && !isPhoneValid}
                helperText={
                  phone.length === 10 && !isPhoneValid
                    ? "Enter a valid Indian mobile number"
                    : " "
                }
                sx={{ mb: 2 }}
              />
              <Button
                fullWidth
                variant="contained"
                size="large"
                onClick={handleSendOtp}
                disabled={!isPhoneValid || loading}
                sx={{
                  bgcolor: "primary.dark",
                  "&:hover": { bgcolor: "primary.main" },
                  textTransform: "none",
                  fontWeight: 700,
                  fontSize: 16,
                  py: 1.5,
                  borderRadius: 2,
                }}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : "Send OTP"}
              </Button>
            </>
          ) : (
            <>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <Typography variant="body1" sx={{ mr: 1 }}>
                  OTP sent to +91 {phone}
                </Typography>
                <Link
                  component="button"
                  variant="body2"
                  onClick={handleChangePhone}
                  sx={{ color: "primary.dark" }}
                >
                  Change
                </Link>
              </Box>

              {/* OTP boxes */}
              <Box sx={{ display: "flex", gap: 1, mb: 2, justifyContent: "center" }}>
                {otp.map((digit, i) => (
                  <TextField
                    key={i}
                    inputRef={(el) => { otpRefs.current[i] = el; }}
                    value={digit}
                    onChange={(e) => handleOtpChange(e.target.value, i)}
                    onKeyDown={(e) => handleOtpKeyDown(e, i)}
                    inputProps={{
                      maxLength: i === 0 ? OTP_LENGTH : 1,
                      style: { textAlign: "center", fontSize: 24, fontWeight: 700, padding: "12px 0" },
                      inputMode: "numeric",
                      "aria-label": `OTP digit ${i + 1} of ${OTP_LENGTH}`,
                    }}
                    sx={{ width: 52 }}
                  />
                ))}
              </Box>

              <FormControlLabel
                control={
                  <Checkbox
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    sx={{ color: "primary.dark", "&.Mui-checked": { color: "primary.dark" } }}
                  />
                }
                label="Remember this device (7 days)"
                sx={{ mb: 2, display: "block" }}
              />

              <Button
                fullWidth
                variant="contained"
                size="large"
                onClick={handleVerifyOtp}
                disabled={!isOtpComplete || loading}
                sx={{
                  bgcolor: "primary.dark",
                  "&:hover": { bgcolor: "primary.main" },
                  textTransform: "none",
                  fontWeight: 700,
                  fontSize: 16,
                  py: 1.5,
                  borderRadius: 2,
                  mb: 1.5,
                }}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : "Verify & Login"}
              </Button>

              <Box sx={{ textAlign: "center" }}>
                {resendCooldown > 0 ? (
                  <Typography variant="body2" color="text.secondary">
                    Resend OTP in {resendCooldown}s
                  </Typography>
                ) : (
                  <Link
                    component="button"
                    variant="body2"
                    onClick={handleResend}
                    disabled={loading}
                    sx={{ color: "primary.dark" }}
                  >
                    Resend OTP
                  </Link>
                )}
              </Box>
            </>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
