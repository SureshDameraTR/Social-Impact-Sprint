import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import Login from "../../pages/Login";

vi.mock("react-router-dom", () => ({
  useNavigate: () => vi.fn(),
}));

vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { language: "en", changeLanguage: vi.fn() },
  }),
}));

vi.mock("../../api/auth", () => ({
  requestOtp: vi.fn(),
  verifyOtp: vi.fn(),
}));

vi.mock("../../hooks/useAuth", () => ({
  useAuth: () => ({ user: null, loading: false, refresh: vi.fn(), logout: vi.fn() }),
}));

describe("Vet Login", () => {
  it("renders without crashing", () => {
    render(<Login />);
    expect(screen.getByText("login.title")).toBeInTheDocument();
  });

  it("shows subtitle", () => {
    render(<Login />);
    expect(screen.getByText("login.subtitle")).toBeInTheDocument();
  });

  it("shows vet login heading", () => {
    render(<Login />);
    expect(screen.getByText("login.vetLogin")).toBeInTheDocument();
  });

  it("shows mobile number input", () => {
    render(<Login />);
    expect(screen.getByLabelText("login.mobileNumber")).toBeInTheDocument();
  });

  it("shows send OTP button", () => {
    render(<Login />);
    expect(screen.getByRole("button", { name: "login.sendOtp" })).toBeInTheDocument();
  });

  it("send OTP button is disabled when phone is empty", () => {
    render(<Login />);
    expect(screen.getByRole("button", { name: "login.sendOtp" })).toBeDisabled();
  });
});
