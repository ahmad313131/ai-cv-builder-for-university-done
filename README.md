![CI + Codecov](https://github.com/ahmad313131/ai-cv-builder-for-university-done/actions/workflows/ci-codecov.yml/badge.svg)
[![codecov](https://codecov.io/github/ahmad313131/ai-cv-builder-for-university-done/branch/main/graph/badge.svg)](https://codecov.io/github/ahmad313131/ai-cv-builder-for-university-done)

# AI CV Builder

AI-powered CV builder that helps students and job seekers create a clean, professional CV and export it as a PDF using different templates.  
The app also uses a local LLM (via **Ollama**) to analyse the CV and give feedback / polishing suggestions.

Tech stack:

- **Frontend:** React (Create React App, MUI)
- **Backend:** FastAPI (Python)
- **Database:** SQLite (local file)
- **AI:** Local LLM via Ollama (e.g. `llama3`, `llama3.1`)
- **Auth:** Email + Google OAuth (optional)
- **CI:** GitHub Actions + Codecov

---

## 1. Requirements

Make sure these are installed on the machine:

- **Node.js** ≥ 18 and **npm**
- **Python** ≥ 3.10
- **Git**
- **Ollama** (for the AI features)

You do **not** need to install any external database server; SQLite is used by default.

---

## 2. Clone the repository

```bash
git clone https://github.com/ahmad313131/ai-cv-builder-for-university-done.git
cd ai-cv-builder-for-university-done

