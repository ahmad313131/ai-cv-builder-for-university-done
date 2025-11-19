import { TextField } from "@mui/material";

export default function EducationStep({ formData, handleChange }) {
  return (
    <TextField
      fullWidth
      multiline
      minRows={4}
      margin="normal"
      label="Education"
      name="education"
      value={formData.education}
      onChange={handleChange}
      placeholder="e.g., B.Sc. in CS — XYZ University (2019–2023)"
    />
  );
}
