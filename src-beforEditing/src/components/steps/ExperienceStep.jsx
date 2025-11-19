import { TextField } from "@mui/material";

export default function ExperienceStep({ formData, handleChange }) {
  return (
    <TextField
      label="Experience"
      name="experience"
      multiline
      minRows={6}
      fullWidth
      value={formData.experience}
      onChange={handleChange}
      placeholder={`Company XYZ — Frontend (2023–Present)
    Project: Banking App
    - Built React SPA with MUI
    - Integrated OAuth2 login
    Tech: React, MUI, FastAPI

    Company ABC — Intern (2022)
    Role: QA Assistant
    - Wrote 50+ test cases`}
      helperText="Hints: lines with 'Title: details' become bold subtitles. Lines starting with '-' become bullets. Separate roles/projects with a blank line."
    />

  );
}
