"use client";

import { useEffect } from "react";
import { Box, Typography, Button } from "@mui/material";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    if (process.env.NODE_ENV === "development") {
      console.error("Page error:", error.message, error.digest);
    }
    // In production, send to structured error reporting service when configured
  }, [error]);

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "60vh",
        p: 4,
        textAlign: "center",
      }}
      role="alert"
    >
      <Typography variant="h5" gutterBottom>
        Something went wrong
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        An unexpected error occurred. Please try again.
      </Typography>
      <Button
        variant="contained"
        onClick={() => reset()}
        sx={{ textTransform: "none", fontWeight: 600 }}
      >
        Reload
      </Button>
    </Box>
  );
}
