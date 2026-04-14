import { Component, type ErrorInfo, type ReactNode } from "react";
import { Box, Typography, Button } from "@mui/material";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error("ErrorBoundary caught:", error, info.componentStack);
  }

  private handleReload = (): void => {
    window.location.reload();
  };

  render(): ReactNode {
    if (this.state.hasError) {
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
        >
          <Typography variant="h5" gutterBottom>
            Something went wrong
          </Typography>
          <Typography color="text.secondary" sx={{ mb: 3 }}>
            An unexpected error occurred. Please try again.
          </Typography>
          <Button
            variant="contained"
            onClick={this.handleReload}
            sx={{ textTransform: "none", fontWeight: 600 }}
          >
            Reload
          </Button>
        </Box>
      );
    }

    return this.props.children;
  }
}
