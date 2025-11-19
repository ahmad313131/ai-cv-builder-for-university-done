import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import PersonalInfoStep from "../components/steps/PersonalInfoStep";

function setup(extra = {}) {
  const props = {
    formData: { name: "Alex", email: "a@a.com", photo_path: "/uploads/p.png" },
    handleChange: jest.fn(),
    photoUrl: "/uploads/p.png",
    handlePhotoChange: jest.fn(),
    uploading: false,
    uploadError: "",
    ...extra,
  };
  render(<PersonalInfoStep {...props} />);
  return props;
}

test("shows Upload Photo button and stored path", () => {
  setup();
  expect(screen.getByText(/Upload Photo/i)).toBeInTheDocument();
  expect(screen.getByText(/Stored at:/i)).toBeInTheDocument();
});

test("disables upload button while uploading and shows spinner text", () => {
  setup({ uploading: true });
  // When uploading: text becomes "Uploading..."
  expect(screen.getByText(/Uploading/i)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /Uploading/i })).toBeDisabled();
});

test("renders error text when uploadError provided", () => {
  setup({ uploadError: "Bad file type" });
  expect(screen.getByText(/Bad file type/i)).toBeInTheDocument();
});

test("calls handleChange when typing in Name and Email", () => {
  const props = setup();
  const name = screen.getByLabelText(/Name/i);
  const email = screen.getByLabelText(/Email/i);

  fireEvent.change(name, { target: { value: "Alexa" } });
  fireEvent.change(email, { target: { value: "x@x.com" } });

  expect(props.handleChange).toHaveBeenCalledTimes(2);
});
