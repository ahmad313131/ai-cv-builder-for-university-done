import React from "react";
import { Box } from "@mui/material";

import {
  Container,
  Paper,
  Typography,
  Stepper,
  Step,
  StepLabel,
} from "@mui/material";

import useCvForm from "./hooks/useCvForm";
import PersonalInfoStep from "./components/steps/PersonalInfoStep";
import EducationStep from "./components/steps/EducationStep";
import ExperienceStep from "./components/steps/ExperienceStep";
import SkillsLinksStep from "./components/steps/SkillsLinksStep";
import ActionsBar from "./components/ActionsBar";
import AnalysisCard from "./components/AnalysisCard";
import ThemeToggle from "./components/ThemeToggle";

const steps = ["Personal Info", "Education", "Experience", "Skills & Links"];

export default function App() {
  const {
    activeStep,
    next,
    back,
    formData,
    handleChange,
    handlePhotoChange,
    photoUrl,
    uploading,
    uploadError,
    analysis,
    analyzing,
    analyzeError,
    submitCV,
    analyze,
    analyzeFast,
    downloadPdf,
    generating,
  } = useCvForm();

  return (
    <Container maxWidth="sm" sx={{ mt: 6 }}>
      <Paper elevation={4} sx={{ p: 4, borderRadius: 3 }}>
        <Typography variant="h4" align="center" gutterBottom>
          AI CV Builder
        </Typography>
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            mb: 2,
          }}
        >
          <Typography variant="h4">AI CV Builder</Typography>
          <ThemeToggle />
        </Box>
        <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {activeStep === 0 && (
          <PersonalInfoStep
            formData={formData}
            handleChange={handleChange}
            photoUrl={photoUrl}
            handlePhotoChange={handlePhotoChange}
            uploading={uploading}
            uploadError={uploadError}
          />
        )}
        {activeStep === 1 && (
          <EducationStep formData={formData} handleChange={handleChange} />
        )}
        {activeStep === 2 && (
          <ExperienceStep formData={formData} handleChange={handleChange} />
        )}
        {activeStep === 3 && (
          <SkillsLinksStep formData={formData} handleChange={handleChange} />
        )}

        <ActionsBar
          activeStep={activeStep}
          back={back}
          next={next}
          uploading={uploading}
          onSave={submitCV}
          onAnalyze={analyze}
          onAnalyzeFast={analyzeFast}
          onDownload={downloadPdf}
          generating={generating}
          analyzing={analyzing} // <-- جديد
        />
      </Paper>

      <AnalysisCard analysis={analysis} analyzeError={analyzeError} />
    </Container>
  );
}
