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
```
##Project layout (simplified):
```bash
ai-cv-builder-for-university-done/
  backend/      # FastAPI app
  src/          # React frontend (Create React App)
  package.json
  README.md
```
## 3. Backend setup (FastAPI)
3.1 Create and activate virtual environment
   ```bash
   cd backend
   python -m venv venv

   # Windows:
   venv\Scripts\activate
   # macOS / Linux:
   # source venv/bin/activate
   ```
 3.2 Install Python dependencies
  ```bash
  pip install -r requirements.txt
 ```
3.3 Environment variables

Create backend/.env:
```bash
# FastAPI
SECRET_KEY=change_me_to_a_random_long_string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# SQLite database
DATABASE_URL=sqlite:///./app.db

# CORS / frontend URL
FRONTEND_ORIGIN=http://localhost:3000

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret



3.4 Initialise / migrate the database

If there is a migrate_db.py file:
```bash
python migrate_db.py
```
Otherwise, the database file will be created automatically on first run.

3.5 Start the backend server
```bash
uvicorn app.main:app --reload --port 8000
```
API base URL: http://localhost:8000
Docs (Swagger UI): http://localhost:8000/docs


## 4. LLM setup (Ollama)

Install Ollama from the official website.

Make sure it is running (default: http://localhost:11434).

Pull the model:
```bash

ollama pull llama3
```

The model name must match OLLAMA_MODEL in .env.

If Ollama is not available, Analyze (AI) will fail with 502 and the app will fall back to the fast, non-LLM analysis.

## 5. Frontend setup (React)

From the project root (not inside backend):
```bash
cd ..
npm install
```
5.1 Frontend environment variables

Create .env in the project root:
```bash
REACT_APP_API_BASE=http://localhost:8000
```
5.2 Run the React dev server
```bash
npm start
```
Open the app in the browser:

http://localhost:3000

You can now:

Fill personal info, education, experience, skills, etc.

(Optionally) sign in with email / Google if configured.

Click Analyze (AI) or Fast Analyze.

Click Download PDF to generate a CV using the selected template.


## 6. Running tests & coverage
Frontend
```bash
npm test
```
Backend

From backend/ with the venv activated:
```bash
pytest
# or
pytest --cov=app
```
GitHub Actions runs tests on each push and sends coverage to Codecov (see badges at the top).


## 7. PDF templates

The backend PDF system is split into:

pdf_logic.py – prepares CV data and communicates with the LLM.

pdf_templates.py – contains several templates (default, modern-blue, LinkedIn style).

pdf_generation.py – FastAPI endpoint (/api/generate_cv) that receives the CV JSON and returns a PDF.

To use another template you just change the template name in pdf_generation.py (for example "default", "modern_blue", "linkedin"). The React app already calls this endpoint.


## 8. Quick summary

To run the project on a new machine:

Install Node, Python, Git, Ollama.

git clone the repo and enter the project.

Set up the backend: cd backend, create venv, pip install -r requirements.txt, create .env, run uvicorn.

Pull the LLM model with ollama pull llama3.

Set up the frontend: npm install, create .env, npm start.

Open http://localhost:3000 and start building CVs.





   



