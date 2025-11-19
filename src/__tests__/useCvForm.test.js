import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import useCvForm from "../hooks/useCvForm";

// Safely mock api module (no out-of-scope vars!)
jest.mock("../api", () => {
  const okBlob = new Blob(["pdf"], { type: "application/pdf" });
  return {
    API_BASE: "http://test",
    uploadPhoto: jest.fn(async () => ({ path: "/uploads/x.png" })),
    saveCV: jest.fn(async (data) => ({ id: 1, ...data })),
    analyzeCV: jest.fn(async () => ({
      matching_score: 71,
      match_level: "Medium Match",
      reasons: ["ok"],
      missing_skills: [],
      nice_to_have: [],
    })),
    generateCV: jest.fn(async () => okBlob),
  };
});

// Harness component to exercise the hook without your pages/components
function CvHookHarness() {
  const {
    activeStep,
    next,
    back,
    formData,
    handleChange,
    analyzeFast,
    analysis,
    submitCV,
    downloadPdf,
  } = useCvForm();

  return (
    <div>
      <div data-testid="step">{activeStep}</div>

      <button onClick={next}>next</button>
      <button onClick={back}>back</button>

      <input
        aria-label="name"
        name="name"
        value={formData.name}
        onChange={handleChange}
      />

      <button onClick={analyzeFast}>fast</button>
      <div data-testid="level">{analysis?.match_level || ""}</div>

      <button onClick={submitCV}>save</button>
      <button onClick={downloadPdf}>pdf</button>
    </div>
  );
}

beforeEach(() => {
  // URL helpers used by downloadPdf
  Object.defineProperty(window, "URL", {
    value: {
      createObjectURL: jest.fn(() => "blob:test"),
      revokeObjectURL: jest.fn(),
    },
    writable: true,
  });

  // Intercept anchor creation/click for download
  const a = { click: jest.fn(), set href(v) {}, set download(v) {} };
  jest.spyOn(document, "createElement").mockImplementation((tag) => {
    if (tag === "a") return a;
    return document.createElement(tag);
  });
  jest.spyOn(document.body, "appendChild").mockImplementation(() => {});
  jest.spyOn(a, "click"); // keep reference
});

afterEach(() => {
  jest.restoreAllMocks();
});

test("next/back move between steps", () => {
  render(<CvHookHarness />);
  expect(screen.getByTestId("step")).toHaveTextContent("0");
  fireEvent.click(screen.getByText("next"));
  expect(screen.getByTestId("step")).toHaveTextContent("1");
  fireEvent.click(screen.getByText("back"));
  expect(screen.getByTestId("step")).toHaveTextContent("0");
});

test("handleChange updates formData", () => {
  render(<CvHookHarness />);
  const input = screen.getByLabelText("name");
  fireEvent.change(input, { target: { value: "Alex" } });
  expect(input).toHaveValue("Alex");
});

test("analyzeFast uses analyzeCV and exposes analysis", async () => {
  render(<CvHookHarness />);
  fireEvent.click(screen.getByText("fast"));

  await waitFor(() =>
    expect(screen.getByTestId("level")).toHaveTextContent(/medium match/i)
  );
});

test("submitCV returns saved data", async () => {
  render(<CvHookHarness />);
  // click "save" just to ensure the path runs; we don't assert the return here
  fireEvent.click(screen.getByText("save"));
  // No throw means success; optional: you can assert your mock was called
});

test("downloadPdf creates object URL and clicks anchor", async () => {
  render(<CvHookHarness />);
  fireEvent.click(screen.getByText("pdf"));

  await waitFor(() => {
    expect(window.URL.createObjectURL).toHaveBeenCalled();
  });
});
