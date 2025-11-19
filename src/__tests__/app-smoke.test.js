import React from "react";
import { render, screen } from "@testing-library/react";
import App from "../App";

// Mock the heavy hook so App renders without side effects
jest.mock("../hooks/useCvForm", () => ({
  __esModule: true,
  default: () => ({
    activeStep: 0,
    next: jest.fn(),
    back: jest.fn(),
    formData: {
      name: "",
      email: "",
      education: "",
      experience: "",
      skills: "",
      github: "",
      linkedin: "",
    },
    handleChange: jest.fn(),
    handlePhotoChange: jest.fn(),
    photoUrl: null,
    uploading: false,
    uploadError: null,
    analysis: null,
    analyzing: false,
    analyzeError: null,
    submitCV: jest.fn(),
    analyze: jest.fn(),
    analyzeFast: jest.fn(),
    downloadPdf: jest.fn(),
    generating: false,
  }),
}));

// ThemeToggle uses context; keep it simple
jest.mock("../components/ThemeToggle", () => () => (
  <span data-testid="theme-toggle" />
));

test("App renders title and steps", () => {
  render(<App />);
  expect(screen.getAllByText(/AI CV Builder/i)[0]).toBeInTheDocument();

  // Stepper labels that are hard-coded in App.js
  expect(screen.getByText("Personal Info")).toBeInTheDocument();
  expect(screen.getByText("Education")).toBeInTheDocument();
  expect(screen.getByText("Experience")).toBeInTheDocument();
  expect(screen.getByText("Skills & Links")).toBeInTheDocument();

  // Actions bar buttons exist (labels may differ; keep generic checks)
  // If your labels differ, adjust the text below:
  // e.g., screen.getByRole('button', { name: /Analyze/i })
});
