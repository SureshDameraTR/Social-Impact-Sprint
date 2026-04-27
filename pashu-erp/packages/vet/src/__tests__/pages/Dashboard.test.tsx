import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import Dashboard from "../../pages/Dashboard";

const mockNavigate = vi.fn();

vi.mock("react-router-dom", () => ({
  useNavigate: () => mockNavigate,
}));

vi.mock("../../api/vet", () => ({
  getDashboardStats: vi.fn().mockRejectedValue(new Error("no api")),
  getPendingCases: vi.fn().mockRejectedValue(new Error("no api")),
}));

vi.mock("../../hooks/useAuth", () => ({
  useAuth: () => ({
    user: { userId: "vet-1", role: "vet", name: "Dr. Sharma", district: "Mysuru" },
    loading: false,
    refresh: vi.fn(),
    logout: vi.fn(),
  }),
}));

describe("Vet Dashboard", () => {
  it("renders without crashing", () => {
    render(<Dashboard />);
    expect(screen.getByText(/welcome/i)).toBeInTheDocument();
  });

  it("shows vet name with Dr. prefix", () => {
    render(<Dashboard />);
    expect(screen.getByText(/Dr\. Sharma/)).toBeInTheDocument();
  });

  it("shows Pending Cases heading", () => {
    render(<Dashboard />);
    expect(screen.getByText("Pending Cases")).toBeInTheDocument();
  });
});
