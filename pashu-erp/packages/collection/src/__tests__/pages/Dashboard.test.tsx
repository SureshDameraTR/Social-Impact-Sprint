import { render } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import Dashboard from "../../pages/Dashboard";

vi.mock("../../api/milk", () => ({
  getDailyReport: vi.fn().mockRejectedValue(new Error("no api")),
}));

vi.mock("../../hooks/useCentre", () => ({
  useCentre: () => ({ centreId: "centre-1", centreName: "Test Centre", setCentre: vi.fn() }),
}));

describe("Collection Dashboard", () => {
  it("renders without crashing", () => {
    render(<Dashboard />);
    // While loading, skeleton placeholders are shown
    expect(document.querySelector(".MuiSkeleton-root")).toBeInTheDocument();
  });
});
